"""2D (rectangular) lattices: 2x2, 2x4, 2x8, 4x4 — untouched by every other
analysis module, which is chain-only. Each site has more nearest neighbours
than in 1D, so the transverse field needed to disorder the system is larger;
the known square-lattice (N->infinity) TFIM critical point is h_c/|J| ~ 3.044
(quantum Monte Carlo), well above the 1D value of 1. Of these four systems
only 4x4 is a genuine (small) square lattice — 2x2/2x4/2x8 are two-leg
ladders, geometrically closer to 1D than to the thermodynamic 2D lattice.

The entanglement entropy here is not compared against the 1D Calabrese-Cardy
formula: in 2D the ground-state entanglement of a region obeys an area law
set by the boundary perimeter, not a 1D conformal log law, so extracting a
"central charge" from these lattices the same way as the chain would be
physically meaningless.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from src.physics.analysis import magnetization_per_spin, steepest_field
from src.physics.entanglement import entropy_vs_field, quasi_degenerate_cutoff
from src.core.loader import load_ising
from src.core.plotting import save_fig, setup_style

LATTICE_2D_COLORS: dict[str, str] = {
    "2x2": "#1f77b4",
    "2x4": "#d62728",
    "2x8": "#2ca02c",
    "4x4": "#9467bd",
}

H_C_2D_SQUARE = 3.044  # thermodynamic-limit square-lattice TFIM (QMC), for reference


def collect_2d_critical_fields(
    layouts: tuple[str, ...] = ("2x2", "2x4", "2x8", "4x4"),
) -> dict[str, float]:
    """Steepest-descent h_c estimate for each rectangular layout."""
    hcs = {}
    for layout in layouts:
        data = load_ising(layout, lattice="rectangular", periodicity="open")
        m = magnetization_per_spin(data)
        hcs[layout] = steepest_field(m, data.fields)
    return hcs


def plot_2d_order_parameter(
    layouts: tuple[str, ...] = ("2x2", "2x4", "2x8", "4x4"),
    *,
    out_path: Path | None = None,
) -> Path:
    """Order parameter vs h for the rectangular lattices, vs the 1D chains and
    the known 2D thermodynamic-limit critical field.
    """
    setup_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    for layout in layouts:
        data = load_ising(layout, lattice="rectangular", periodicity="open")
        m = magnetization_per_spin(data)
        hc = steepest_field(m, data.fields)
        color = LATTICE_2D_COLORS[layout]
        ax.plot(data.fields, m, marker=".", ms=4, color=color,
                label=f"{layout} (N={data.num_spins}, $h_c\\approx{hc:.2f}$)")
        ax.axvline(hc, color=color, ls=":", lw=1, alpha=0.5)

    ax.axvline(1.0, color="k", ls="--", lw=1, alpha=0.5, label="1D chain, $N\\to\\infty$: $h_c=1$")
    ax.axvline(H_C_2D_SQUARE, color="k", ls="-.", lw=1.2, alpha=0.7,
               label=f"2D square lattice, $N\\to\\infty$: $h_c\\approx{H_C_2D_SQUARE}$")
    ax.set_xlabel("transverse field $h$")
    ax.set_ylabel(r"$\langle|M_z|\rangle/N$")
    ax.set_title("TFIM order parameter — rectangular lattices")
    ax.legend(fontsize=9)
    return save_fig(fig, "order_parameter_rectangular_open", out_path=out_path)


def plot_2d_entropy(
    layouts: tuple[str, ...] = ("2x2", "2x4", "2x8", "4x4"),
    *,
    out_path: Path | None = None,
) -> Path:
    """Half-system entanglement entropy vs h for the rectangular lattices."""
    setup_style()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    max_cutoff = 0.0
    for layout in layouts:
        data = load_ising(layout, lattice="rectangular", periodicity="open")
        s = entropy_vs_field(data)
        hc = steepest_field(s, data.fields)
        max_cutoff = max(max_cutoff, quasi_degenerate_cutoff(data.fields, s))
        color = LATTICE_2D_COLORS[layout]
        ax.plot(data.fields, s, "-", color=color,
                label=f"{layout} (N={data.num_spins}, crossover $h\\approx{hc:.2f}$)")
    if max_cutoff > 0:
        ax.axvspan(0, max_cutoff, color="gray", alpha=0.12, zorder=0)
        ax.annotate("quasi-degenerate GS\n(solver picks a branch)",
                    xy=(max_cutoff, 0.15), xytext=(6, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=8, color="dimgray")
    ax.axhline(np.log(2), color="gray", ls=":", lw=1, alpha=0.7, label=r"$\ln 2$ (cat / SSB plateau)")
    ax.set_xlabel("transverse field $h$")
    ax.set_ylabel("half-system entanglement entropy $S$")
    ax.set_title("Entanglement across the transition — rectangular lattices")
    ax.legend(fontsize=9)
    return save_fig(fig, "entropy_rectangular_open", out_path=out_path)


if __name__ == "__main__":
    hcs = collect_2d_critical_fields()
    for layout, hc in hcs.items():
        print(f"{layout}: h_c (steepest descent) = {hc:.3f}")
    p1 = plot_2d_order_parameter()
    print(f"wrote {p1}")
    p2 = plot_2d_entropy()
    print(f"wrote {p2}")
