"""Classical-shadow reconstruction of the order parameter from `shadow_basis` /
`shadow_meas` — the one NISQ-realistic result in the dataset, since it uses
1000 single-shot randomized-Pauli measurements per field instead of the exact
statevector.

<|M_z|> itself is not a linear functional of the state (the absolute value is
nonlinear), so it cannot be estimated directly from classical shadows. Instead
we estimate the quadratic <M_z^2> = sum_i <Z_i^2> + sum_{i != j} <Z_i Z_j>
= N + sum_{i != j} <Z_i Z_j> (a genuine shadow observable), and report
sqrt(<M_z^2>) as the order-parameter proxy. In the ordered phase the ground
state has a sharply peaked |M_z| distribution (or is a two-branch cat state),
so sqrt(<M_z^2>) ~ <|M_z|> to good approximation; the two coincide exactly
whenever M_z takes only the values +-m.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pennylane as qml

from src.core.loader import IsingData
from src.core.plotting import color_for_n, save_fig, setup_style


def shadow_mz_squared(data: IsingData, field_index: int, *, k: int = 1) -> float:
    """Classical-shadow estimate of <M_z^2> at one field, from that field's
    1000-shot randomized-Pauli shadow.
    """
    n = data.num_spins
    shadow = qml.ClassicalShadow(data.shadow_meas[field_index], data.shadow_basis[field_index])
    ops = [qml.Z(a) @ qml.Z(b) for a in range(n) for b in range(n) if a != b]
    hamiltonian = qml.Hamiltonian([1.0] * len(ops), ops)
    offdiag = float(shadow.expval(hamiltonian, k=k))
    return n + offdiag  # <Z_i^2> = 1 for every i


def shadow_order_parameter_sweep(data: IsingData, *, k: int = 1) -> np.ndarray:
    """sqrt(<M_z^2>) from shadows at every field in the sweep."""
    mz2 = np.array([shadow_mz_squared(data, i, k=k) for i in range(data.n_fields)])
    return np.sqrt(np.clip(mz2, 0.0, None))


def plot_shadow_reconstruction(
    data: IsingData,
    *,
    k: int = 10,
    out_path: Path | None = None,
) -> Path:
    """Shadow-reconstructed order parameter (with shot noise) vs the exact
    dataset value, both normalized by N.
    """
    setup_style()
    import matplotlib.pyplot as plt

    n = data.num_spins
    shadow_est = shadow_order_parameter_sweep(data, k=k)
    exact = data.order_params

    fig, ax = plt.subplots(figsize=(7, 5))
    color = color_for_n(n)
    ax.plot(data.fields, exact / n, "-", lw=1.8, color="k", label="exact (statevector)")
    ax.plot(data.fields, shadow_est / n, "o", ms=4, mfc="none", color=color,
            label=f"classical shadow, 1000 shots ($N={n}$)")
    ax.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6, label="$h/|J|=1$")
    ax.set_xlabel("transverse field $h$")
    ax.set_ylabel(r"$\sqrt{\langle M_z^2\rangle}\,/\,N$  (shadow)  vs.  $\langle|M_z|\rangle/N$ (exact)")
    ax.set_title(f"Classical-shadow reconstruction of the order parameter, N={n}")
    ax.legend()
    return save_fig(fig, f"shadow_reconstruction_N{n}", out_path=out_path)


if __name__ == "__main__":
    from src.core.loader import load_ising

    for layout in ("1x4", "1x8"):
        data = load_ising(layout)
        shadow_est = shadow_order_parameter_sweep(data, k=10)
        mae = float(np.abs(shadow_est - data.order_params).mean())
        print(f"{layout}: mean |shadow - exact| (order param, not /N) = {mae:.4f}")
        path = plot_shadow_reconstruction(data)
        print(f"  wrote {path}")
