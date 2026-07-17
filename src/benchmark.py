from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.loader import IsingData, Lattice, Periodicity, load_ising
from src.parallel import parallel_map
from src.plotting import color_for_n, save_fig, setup_style
from src.vqe import abs_mz_from_state, run_vqe
from src.vqe_hva import warm_start_core

ROOT = Path(__file__).resolve().parent.parent
RESULTS_CSV = ROOT / "data" / "vqe_benchmark.csv"

# Independent random restarts per point. A single seed is an anecdote: VQE
# outcomes depend strongly on the initialization, so every reported point is a
# median over these restarts with an inter-quartile band, plus a
# best-of-restarts curve (the accuracy actually achievable).
DEFAULT_SEEDS: tuple[int, ...] = (0, 1, 2, 3)

# Single precision for the energy-error sweeps: ~1.4x faster per step, and the
# ~1e-5 float32 floor is far below the errors these plots report. (Sparse
# Hamiltonians were tried and dropped — lightning's native Pauli-sum expval is
# faster than a general sparse mat-vec for this model.)
_BENCH_DTYPE = np.complex64


def _bench_task(task: tuple) -> dict:
    """One VQE run for the (size, depth, field, restart) grid — the process-pool
    worker for `run_benchmark`."""
    layout, ham, num_spins, n_layers, seed, h, e_exact, order_param, steps = task
    res = run_vqe(ham, num_spins, n_layers=n_layers, steps=steps, seed=seed,
                  c_dtype=_BENCH_DTYPE)
    m_vqe = abs_mz_from_state(res.state, num_spins)
    return {
        "layout": layout,
        "num_spins": num_spins,
        "n_layers": n_layers,
        "seed": seed,
        "h": float(h),
        "e_vqe": res.energy,
        "e_exact": float(e_exact),
        "abs_energy_error": abs(res.energy - e_exact),
        "rel_energy_error": abs(res.energy - e_exact) / abs(e_exact),
        "mz_vqe": m_vqe,
        "mz_exact": float(order_param),
        "mz_error": abs(m_vqe - order_param),
    }


def run_benchmark(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    layers_list: tuple[int, ...] = (1, 2, 4, 6),
    *,
    lattice: Lattice = "chain",
    periodicity: Periodicity = "open",
    n_fields: int = 8,
    steps: int = 500,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    n_jobs: int | None = None,
) -> pd.DataFrame:
    """Sweep (system size, ansatz depth, random restart), running VQE at
    `n_fields` field values evenly sampled across the h range, and tabulate
    accuracy vs the exact data.

    `steps` is the per-run maximum budget; each run early-stops on convergence,
    so a deeper ansatz is not penalised by a fixed budget. The independent runs
    are distributed across processes (`n_jobs`, default all cores). Returns a
    long-format DataFrame, one row per (layout, n_layers, field, seed).
    """
    tasks: list[tuple] = []
    for layout in layouts:
        data = load_ising(layout, lattice=lattice, periodicity=periodicity)
        idx = np.linspace(0, data.n_fields - 1, n_fields, dtype=int)
        for n_layers in layers_list:
            for i in idx:
                for seed in seeds:
                    tasks.append((layout, data.hamiltonians[i], data.num_spins,
                                  n_layers, seed, float(data.fields[i]),
                                  float(data.ground_energies[i]),
                                  float(data.order_params[i]), steps))
    rows = parallel_map(_bench_task, tasks, n_jobs=n_jobs)
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per (num_spins, n_layers) across fields and random restarts.

    `mean_abs_E` is the median (over restarts) of each restart's mean error over
    the field sweep; `lo_abs_E`/`hi_abs_E` are the 25th/75th percentiles of the
    same, giving the restart-to-restart band. `best_abs_E` is the
    best-of-restarts accuracy: the min over restarts at each field, averaged
    over the sweep.
    """
    per_seed = (df.groupby(["num_spins", "n_layers", "seed"])["abs_energy_error"]
                .mean().rename("seed_mean").reset_index())
    agg = (per_seed.groupby(["num_spins", "n_layers"])["seed_mean"]
           .agg(mean_abs_E="median",
                lo_abs_E=lambda x: x.quantile(0.25),
                hi_abs_E=lambda x: x.quantile(0.75)).reset_index())
    per_field_best = (df.groupby(["num_spins", "n_layers", "h"])["abs_energy_error"]
                      .min().rename("field_best").reset_index())
    best = (per_field_best.groupby(["num_spins", "n_layers"])["field_best"]
            .mean().rename("best_abs_E").reset_index())
    return agg.merge(best, on=["num_spins", "n_layers"])


def plot_convergence(summary: pd.DataFrame, *, out_path: Path | None = None) -> Path:
    """Median energy error vs ansatz depth with a restart-to-restart IQR band and
    a best-of-restarts curve (dashed), one colour per system size."""
    setup_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    for n, sub in summary.groupby("num_spins"):
        sub = sub.sort_values("n_layers")
        c = color_for_n(n)
        ax.plot(sub["n_layers"], sub["mean_abs_E"], "o-", color=c, label=f"N={n} (median)")
        ax.fill_between(sub["n_layers"], sub["lo_abs_E"], sub["hi_abs_E"], color=c, alpha=0.18)
        ax.plot(sub["n_layers"], sub["best_abs_E"], "--", color=c, lw=1.1, alpha=0.7)
    ax.plot([], [], "k--", lw=1.1, alpha=0.7, label="best of restarts")
    ax.set_yscale("log")
    ax.set_xlabel("ansatz depth (n_layers)")
    ax.set_ylabel(r"mean $|E_{VQE}-E_{exact}|$ over field sweep")
    ax.set_title("VQE convergence vs depth and system size (HEA, restart bands)")
    ax.legend()
    return save_fig(fig, "vqe_benchmark", out_path=out_path)


_ANSATZ_STYLE = {
    "StronglyEntangling (random)": ("tab:red", "s"),
    "HVA + warm-start": ("tab:blue", "o"),
    "QAOA (anneal) + warm-start": ("tab:green", "^"),
}


def _cmp_hea_task(task: tuple) -> dict:
    ham, num_spins, n_layers, steps, seed, h, e_exact = task
    res = run_vqe(ham, num_spins, n_layers=n_layers, steps=steps, seed=seed,
                  c_dtype=_BENCH_DTYPE)
    return {"h": float(h), "ansatz": "StronglyEntangling (random)",
            "seed": seed, "abs_E_error": abs(res.energy - e_exact)}


def _cmp_sweep_task(task: tuple) -> list[dict]:
    hams, num_spins, fields, ees, n_layers, steps, seed, strategy, name = task
    sw = warm_start_core(hams, num_spins, fields, ees, n_layers=n_layers,
                         steps=steps, init_strategy=strategy, seed=seed,
                         c_dtype=_BENCH_DTYPE)
    return [{"h": float(h), "ansatz": name, "seed": seed, "abs_E_error": float(e)}
            for h, e in zip(np.asarray(sw.fields), np.asarray(sw.abs_errors))]


def compare_ansatze(
    data: IsingData,
    *,
    n_layers: int = 10,
    steps: int = 500,
    n_fields: int = 12,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    n_jobs: int | None = None,
    out_path: Path | None = None,
) -> tuple[Path, pd.DataFrame]:
    """Per-field |E_VQE - E_exact| for three ansätze over several random restarts:
    the generic StronglyEntanglingLayers (random init, independent fields), the
    Hamiltonian Variational Ansatz with warm-start, and QAOA (annealing init +
    warm-start). Returns the figure path and a tidy DataFrame with a `seed`
    column; the plot shows the per-restart median and inter-quartile band. The
    independent HEA runs and the (per-restart) warm-start sweeps run across
    processes.
    """
    # Exclude h=0: the dataset returns a symmetry-broken product state there
    # (same h->0 boundary artifact documented in analysis.steepest_field), which
    # every ansatz reproduces trivially and which would stretch the log-y axis
    # over several decades for a result that says nothing about ansatz quality.
    candidates = np.arange(data.n_fields)[data.fields > 0]
    idx = list(np.linspace(candidates[0], candidates[-1], n_fields, dtype=int))
    hams = [data.hamiltonians[i] for i in idx]
    fields = [float(data.fields[i]) for i in idx]
    ees = [float(data.ground_energies[i]) for i in idx]
    n = data.num_spins

    hea_tasks = [(hams[k], n, n_layers, steps, seed, fields[k], ees[k])
                 for seed in seeds for k in range(len(idx))]
    sweep_tasks = [(hams, n, fields, ees, n_layers, steps, seed, strat, name)
                   for seed in seeds
                   for strat, name in (("random", "HVA + warm-start"),
                                       ("anneal", "QAOA (anneal) + warm-start"))]

    hea_rows = parallel_map(_cmp_hea_task, hea_tasks, n_jobs=n_jobs)
    sweep_rows = parallel_map(_cmp_sweep_task, sweep_tasks, n_jobs=n_jobs)
    rows = list(hea_rows) + [r for sub in sweep_rows for r in sub]
    df = pd.DataFrame(rows)

    agg = (df.groupby(["ansatz", "h"])["abs_E_error"]
           .agg(med="median", lo=lambda x: x.quantile(0.25), hi=lambda x: x.quantile(0.75))
           .reset_index())

    setup_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.5, 5))
    for ansatz, (color, marker) in _ANSATZ_STYLE.items():
        sub = agg[agg["ansatz"] == ansatz].sort_values("h")
        ax.fill_between(sub["h"], sub["lo"], sub["hi"], color=color, alpha=0.18)
        ax.semilogy(sub["h"], sub["med"], marker=marker, ls="-", ms=6, color=color, label=ansatz)
    ax.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6, label="$h/|J|=1$")
    ax.set_xlabel("transverse field $h$")
    ax.set_ylabel(r"energy error $|E_{VQE}-E_{exact}|$")
    ax.set_title(f"Ansatz comparison — TFIM chain, N={data.num_spins}, "
                 f"{n_layers} layers, {len(seeds)} restarts (median $\\pm$ IQR)")
    ax.legend()
    path = save_fig(fig, f"ansatz_comparison_N{data.num_spins}", out_path=out_path)
    return path, df


if __name__ == "__main__":
    df = run_benchmark(layouts=("1x4", "1x8", "1x16"), layers_list=(1, 2, 4, 6),
                       n_fields=8)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RESULTS_CSV, index=False)
    summary = summarize(df)
    path = plot_convergence(summary)
    print(f"raw rows: {len(df)}  ->  {RESULTS_CSV}")
    print(f"plot: {path}\n")
    print(summary.to_string(index=False))

    for layout in ("1x8", "1x16"):
        print(f"\nbuilding ansatz comparison ({layout})...")
        data = load_ising(layout)
        cmp_path, cmp_df = compare_ansatze(data, n_layers=10, n_fields=12)
        cmp_df.to_csv(ROOT / "data" / f"ansatz_comparison_{layout}.csv", index=False)
        print(f"plot: {cmp_path}")
        # median over restarts, then mean/best-of-restarts over the field sweep
        med = cmp_df.groupby(["ansatz", "h"])["abs_E_error"].median().groupby("ansatz").mean()
        best = cmp_df.groupby(["ansatz", "h"])["abs_E_error"].min().groupby("ansatz").mean()
        print("mean over sweep of median|dE| (typical) and min|dE| (best of restarts):")
        for ansatz in _ANSATZ_STYLE:
            print(f"  {ansatz:32s} median={med[ansatz]:.3e}  best={best[ansatz]:.3e}")
