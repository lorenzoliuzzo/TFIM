"""Energy-error profile and trainability as a function of the transverse field h.

Connects the variational accuracy (ΔE(h) = |E_VQE − E_exact|) to the
trainability landscape (gradient variance vs h) for both the hardware-efficient
ansatz (HEA / StronglyEntanglingLayers) and the structure-aware HVA.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from src.core.loader import IsingData, load_ising
from src.core.plotting import save_fig, setup_style
from src.ansatz.trainability import gradient_variance
from src.ansatz.vqe import run_vqe
from src.ansatz.vqe_hva import warm_start_sweep


# ---------------------------------------------------------------------------
# HEA sweep: independent VQE per field (no warm start — fair comparison)
# ---------------------------------------------------------------------------

def hea_error_sweep(
    data: IsingData,
    *,
    indices: list[int] | None = None,
    n_layers: int = 3,
    steps: int = 120,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Run HEA VQE at each selected field and return (fields, abs_errors)."""
    indices = list(range(data.n_fields)) if indices is None else indices
    fields, errors = [], []
    for i in indices:
        res = run_vqe(data.hamiltonians[i], data.num_spins,
                      n_layers=n_layers, steps=steps, seed=seed)
        fields.append(data.fields[i])
        errors.append(abs(res.energy - float(data.ground_energies[i])))
    return np.array(fields), np.array(errors)


# ---------------------------------------------------------------------------
# Gradient variance as a function of h (at fixed N)
# ---------------------------------------------------------------------------

def gradient_variance_vs_field(
    ansatz: str,
    data: IsingData,
    *,
    field_indices: list[int] | None = None,
    n_layers: int = 4,
    n_samples: int = 30,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    """Var[∂_θ ⟨H⟩] at each field value, for a fixed N, averaged over every
    gradient component (see trainability.gradient_variance).

    Returns (fields, variances).
    """
    if field_indices is None:
        field_indices = list(range(0, data.n_fields, 5))

    fields, variances = [], []
    for i in field_indices:
        v = gradient_variance(ansatz, data.num_spins, data.hamiltonians[i],  # type: ignore[arg-type]
                              n_layers=n_layers, n_samples=n_samples, seed=seed)
        fields.append(data.fields[i])
        variances.append(v)
    return np.array(fields), np.array(variances)


# ---------------------------------------------------------------------------
# Combined plot
# ---------------------------------------------------------------------------

def plot_error_and_trainability(
    layout: str = "1x8",
    *,
    lattice: str = "chain",
    periodicity: str = "open",
    sweep_indices: list[int] | None = None,
    var_indices: list[int] | None = None,
    hva_layers: int = 6,
    hea_layers: int = 3,
    steps: int = 120,
    n_samples: int = 30,
    seed: int = 0,
    out_path: Path | None = None,
) -> Path:
    """Two-panel figure: energy error vs h (top) and gradient variance vs h (bottom).

    Top panel reveals where each ansatz fails to approximate the ground state.
    Bottom panel connects that failure to the trainability landscape: a flat
    gradient (low variance) in the ordered phase explains why the optimizer
    stalls there.
    """
    data = load_ising(layout, lattice=lattice, periodicity=periodicity)  # type: ignore[arg-type]
    n = data.num_spins

    if sweep_indices is None:
        sweep_indices = list(range(0, data.n_fields, 5))
    if var_indices is None:
        var_indices = list(range(0, data.n_fields, 10))

    print(f"Running HEA sweep (N={n}, {len(sweep_indices)} fields)...")
    hea_fields, hea_errors = hea_error_sweep(
        data, indices=sweep_indices, n_layers=hea_layers, steps=steps, seed=seed
    )

    print(f"Running HVA warm-start sweep (N={n}, {len(sweep_indices)} fields)...")
    sw = warm_start_sweep(data, n_layers=hva_layers, steps=steps, indices=sweep_indices, seed=seed)
    hva_fields = np.array(sw.fields)
    hva_errors = np.array(sw.abs_errors)

    print(f"Computing gradient variance vs h for HEA and HVA ({n_samples} samples/field)...")
    gv_hea_f, gv_hea = gradient_variance_vs_field(
        "hea", data, field_indices=var_indices, n_layers=hea_layers, n_samples=n_samples, seed=seed
    )
    gv_hva_f, gv_hva = gradient_variance_vs_field(
        "hva", data, field_indices=var_indices, n_layers=hva_layers, n_samples=n_samples, seed=seed
    )

    setup_style()
    import matplotlib.pyplot as plt

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    ax_top.semilogy(hea_fields, hea_errors, "o-", color="#d62728", ms=5, lw=1.4,
                    label=f"HEA (SEL, L={hea_layers})")
    ax_top.semilogy(hva_fields, hva_errors, "s-", color="#1f77b4", ms=5, lw=1.4,
                    label=f"HVA warm-start (L={hva_layers})")
    ax_top.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6, label="$h_c=1$")
    ax_top.set_ylabel(r"$|E_\mathrm{VQE} - E_\mathrm{exact}|$")
    ax_top.set_title(f"VQE energy error vs transverse field — N={n}")
    ax_top.legend()

    ax_bot.semilogy(gv_hea_f, gv_hea, "o-", color="#d62728", ms=5, lw=1.4, label="HEA")
    ax_bot.semilogy(gv_hva_f, gv_hva, "s-", color="#1f77b4", ms=5, lw=1.4, label="HVA")
    ax_bot.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6)
    ax_bot.set_xlabel("transverse field $h$")
    ax_bot.set_ylabel(r"$\mathrm{Var}[\partial_\theta \langle H \rangle]$")
    ax_bot.set_title("Gradient variance vs transverse field (trainability)")
    ax_bot.legend()

    fig.tight_layout()
    return save_fig(fig, f"vqe_error_trainability_{layout}", out_path=out_path)


if __name__ == "__main__":
    path = plot_error_and_trainability("1x8", sweep_indices=list(range(0, 100, 5)),
                                       var_indices=list(range(0, 100, 10)),
                                       hva_layers=6, hea_layers=3, steps=120, n_samples=30)
    print(f"wrote {path}")
