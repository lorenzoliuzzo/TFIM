"""Open vs closed (periodic) boundary conditions: does the finite-size h_c
estimate drift faster/slower, or land closer to h/|J|=1, on a ring than on a
chain with two open ends?
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from src.physics.finite_size_scaling import collect_hc_estimates, fit_hc_power_law
from src.core.plotting import save_fig, setup_style


def compare_boundary_conditions(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
) -> dict[str, dict[str, float]]:
    """Power-law h_c(infinity) extrapolation (inflection method) for both BCs."""
    results = {}
    for periodicity in ("open", "closed"):
        ns, hc_infl, _ = collect_hc_estimates(layouts, periodicity=periodicity)
        fit = fit_hc_power_law(ns, hc_infl)
        results[periodicity] = {"ns": ns, "hc_infl": hc_infl, **fit}
    return results


def plot_boundary_comparison(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    out_path: Path | None = None,
) -> Path:
    """h_c(N) vs 1/N for open and closed chains side by side, with each fit."""
    setup_style()
    import matplotlib.pyplot as plt

    results = compare_boundary_conditions(layouts)
    styles = {"open": ("o", "-", "#1f77b4"), "closed": ("s", "--", "#d62728")}

    fig, ax = plt.subplots(figsize=(7, 5))
    x_ext = np.linspace(0, 1.0 / results["open"]["ns"].min(), 300)
    for periodicity, res in results.items():
        marker, ls, color = styles[periodicity]
        ns = res["ns"]
        x = 1.0 / ns
        ax.plot(x, res["hc_infl"], marker, color=color, ms=8,
                label=f"{periodicity} (data)")
        n_ext = np.where(x_ext > 0, 1.0 / x_ext, np.inf)
        h_ext = res["h_inf"] - res["a"] * n_ext ** (-1.0 / res["nu"])
        ax.plot(x_ext, h_ext, ls, color=color, lw=1.4,
                label=f"{periodicity} fit: $h_c^\\infty={res['h_inf']:.3f}$, $\\nu={res['nu']:.2f}$")

    ax.axhline(1.0, color="k", ls=":", lw=1, alpha=0.6, label="exact $h_c=1$")
    ax.set_xlabel(r"$1/N$")
    ax.set_ylabel(r"$h_c(N)$ (steepest-descent)")
    ax.set_title("Finite-size critical field: open vs closed chain")
    ax.legend(fontsize=9)
    return save_fig(fig, "boundary_comparison_hc", out_path=out_path)


if __name__ == "__main__":
    results = compare_boundary_conditions()
    for periodicity, res in results.items():
        print(f"{periodicity:6s}: h_c(N) = {list(np.round(res['hc_infl'], 3))}"
              f"  ->  h_c(inf) = {res['h_inf']:.4f}, nu = {res['nu']:.3f}")
    path = plot_boundary_comparison()
    print(f"wrote {path}")
