"""Exact free-fermion (Jordan-Wigner) solution of the 1D TFIM, periodic chain.

An independent, purely analytic cross-check on the dataset's `ground_energies`
(exact diagonalization), rather than a second numerical method agreeing with
the first by construction.

The Jordan-Wigner transform maps H = -|J| sum_i sigma^z_i sigma^z_{i+1}
+ h sum_i sigma^x_i (our convention, |J|=1, periodic chain) onto free
fermions with single-particle dispersion

    eps(k) = 2 sqrt(1 + h^2 - 2 h cos k).

The physical (even-fermion-parity) ground state of a finite ring uses the
anti-periodic momenta k_m = pi(2m+1)/N, m=0..N-1, and fills every negative-
energy mode:

    E0 = -(1/2) sum_m eps(k_m).

This momentum set is invariant under k -> pi-k, so the same E0 results
whether h enters the dispersion as +h or -h — i.e. the formula is agnostic to
the sign convention on the field term, and needs no adjustment for the
dataset's H = J*ZZ + h*X with J=-1.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from src.core.loader import load_ising
from src.core.plotting import color_for_n, save_fig, setup_style


def dispersion(k: np.ndarray | float, h: float) -> np.ndarray | float:
    """Single-particle excitation energy eps(k), |J|=1. Gap closes at h=1, k=0."""
    return 2.0 * np.sqrt(1.0 + h**2 - 2.0 * h * np.cos(k))


def _allowed_momenta(n: int) -> np.ndarray:
    """Anti-periodic momenta for the even-fermion-parity (physical) sector."""
    m = np.arange(n)
    return np.pi * (2 * m + 1) / n


def ground_energy_analytic(n: int, h: float) -> float:
    """Exact ground-state energy (not per-site) of the periodic TFIM ring."""
    k = _allowed_momenta(n)
    return -0.5 * np.sum(dispersion(k, h))


def gap_analytic(n: int, h: float) -> float:
    """Smallest single-particle excitation energy of the periodic ring."""
    k = _allowed_momenta(n)
    return float(np.min(dispersion(k, h)))


def plot_jw_cross_check(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    out_path: Path | None = None,
) -> Path:
    """Two-panel figure: analytic-vs-ED energy residual, and the finite-size
    excitation gap vs h closing near h=1 as N grows — the independent
    Jordan-Wigner evidence for the critical point, with no ED involved.
    """
    setup_style()
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    for layout in layouts:
        data = load_ising(layout, lattice="chain", periodicity="closed")
        n = data.num_spins
        color = color_for_n(n)
        analytic = np.array([ground_energy_analytic(n, h) for h in data.fields])
        residual = np.abs(analytic - data.ground_energies)
        ax1.semilogy(data.fields, residual + 1e-18, color=color, label=f"N={n}")

        gaps = np.array([gap_analytic(n, h) for h in data.fields])
        ax2.plot(data.fields, gaps, color=color, label=f"N={n}")

    ax1.set_xlabel("$h$"); ax1.set_ylabel(r"$|E_{JW} - E_{ED}|$")
    ax1.set_title("Jordan-Wigner vs exact diagonalization (closed chain)")
    ax1.legend()

    ax2.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6)
    ax2.set_xlabel("$h$"); ax2.set_ylabel("excitation gap")
    ax2.set_title("Finite-size gap closing near $h=1$")
    ax2.legend()

    fig.tight_layout()
    return save_fig(fig, "jordan_wigner_cross_check", out_path=out_path)


if __name__ == "__main__":
    path = plot_jw_cross_check()
    print(f"wrote {path}")
    for layout in ("1x4", "1x8", "1x16"):
        data = load_ising(layout, lattice="chain", periodicity="closed")
        n = data.num_spins
        errs = [abs(ground_energy_analytic(n, h) - e)
                for h, e in zip(data.fields, data.ground_energies)]
        print(f"N={n:2d}: max |E_JW - E_ED| = {max(errs):.2e}")
