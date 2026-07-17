"""Single entry point: reproduce every figure and tabular result.

Run from the project root with:

    .venv/bin/python run_all.py

Writes figures to plots/ and CSVs to data/. Each stage prints what it wrote.
"""
from __future__ import annotations

import time
from pathlib import Path

from src.analysis import (
    binder_crossing,
    estimate_critical_field,
    plot_binder,
    plot_data_collapse,
    plot_order_parameter,
)
from src.benchmark import (
    compare_ansatze,
    plot_convergence,
    run_benchmark,
    summarize,
)
from src.entanglement import fit_central_charge, plot_central_charge, plot_entropy_vs_field
from src.loader import load_ising
from src.trainability import plot_barren_plateaus
from src.vqe import plot_sweep, sweep_vqe

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CHAIN_LAYOUTS = ("1x4", "1x8", "1x16")


def _banner(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def exact_analysis() -> None:
    _banner("1. Exact analysis — order parameter, Binder cumulant, data collapse")
    print(f"wrote {plot_order_parameter(CHAIN_LAYOUTS)}")
    print(f"wrote {plot_binder(CHAIN_LAYOUTS)}")
    print(f"wrote {plot_data_collapse(CHAIN_LAYOUTS)}")
    datasets = [load_ising(ly) for ly in CHAIN_LAYOUTS]
    for d in datasets:
        print(f"  N={d.num_spins:2d}  inflection h_c = {estimate_critical_field(d):.3f}")
    print(f"  Binder crossing N=8/16: h_c = {binder_crossing(datasets[1], datasets[2]):.3f}")


def entanglement_analysis() -> None:
    _banner("2. Entanglement — half-chain entropy, central charge")
    print(f"wrote {plot_entropy_vs_field(CHAIN_LAYOUTS)}")
    data = load_ising("1x16")
    fit = fit_central_charge(data)
    print(f"wrote {plot_central_charge(fit, data.num_spins)}")
    print("  central charge vs N (Ising CFT c=0.5):")
    for layout in ("1x8", "1x16"):
        f = fit_central_charge(load_ising(layout))
        print(f"    N={f.ls[-1] + 1:2d}  h={f.field:.3f}  c={f.central_charge:.4f}")


def vqe_demo() -> None:
    _banner("3. VQE vs exact (N=4, every 5th field)")
    data = load_ising("1x4")
    idx = list(range(0, data.n_fields, 5))
    sweep = sweep_vqe(data, indices=idx, n_layers=3, steps=200)
    print(f"wrote {plot_sweep(sweep, data.num_spins)}")
    mae = float(abs(sweep.vqe_energies - sweep.exact_energies).mean())
    print(f"  mean |E_VQE - E_exact| = {mae:.4e}")


# Runs are distributed across processes; cap the pool so the N=16 workers (each
# holds a 2**16 statevector) fit in RAM. Raise on a larger-memory machine.
N_JOBS = 8


def benchmark_and_ansatze() -> None:
    _banner("4. VQE benchmark + ansatz comparison (multi-restart, median +/- IQR)")
    df = run_benchmark(layouts=("1x4", "1x8", "1x16"), layers_list=(1, 2, 4, 6),
                       n_fields=8, n_jobs=N_JOBS)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_DIR / "vqe_benchmark.csv", index=False)
    summary = summarize(df)
    print(f"wrote {plot_convergence(summary)}")
    print(summary.to_string(index=False))

    for layout in ("1x8", "1x16"):
        data = load_ising(layout)
        cmp_path, cmp_df = compare_ansatze(data, n_layers=10, n_fields=12, n_jobs=N_JOBS)
        cmp_df.to_csv(DATA_DIR / f"ansatz_comparison_{layout}.csv", index=False)
        print(f"wrote {cmp_path}")
        med = cmp_df.groupby(["ansatz", "h"])["abs_E_error"].median().groupby("ansatz").mean()
        print(med.to_string())


def trainability() -> None:
    _banner("5. Barren plateaus — gradient variance vs system size")
    print(f"wrote {plot_barren_plateaus(n_layers=4, n_samples=50)}")


def main() -> None:
    t0 = time.time()
    exact_analysis()
    entanglement_analysis()
    vqe_demo()
    benchmark_and_ansatze()
    trainability()
    _banner(f"DONE in {time.time() - t0:.0f}s — figures in plots/, tables in data/")


if __name__ == "__main__":
    main()
