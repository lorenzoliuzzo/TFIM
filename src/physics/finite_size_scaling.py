"""Finite-size scaling analysis for the 1D TFIM.

Collects h_c(N) estimates from multiple methods, fits the power-law correction
h_c(N) = h_c(∞) − a·N^{−1/ν} to extract ν and extrapolate to N→∞, and tracks
the central-charge overshoot c(N) from the Calabrese–Cardy fit.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

from src.physics.analysis import binder_crossing, estimate_critical_field
from src.physics.entanglement import fit_central_charge
from src.core.loader import load_ising
from src.core.plotting import color_for_n, save_fig, setup_style


# ---------------------------------------------------------------------------
# h_c estimation
# ---------------------------------------------------------------------------

def collect_hc_estimates(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (ns, hc_inflection, hc_binder) arrays.

    Binder crossings are between each adjacent pair; the smallest-N entry uses
    the (N=4, N=8) crossing so every size has a value for comparison.
    """
    datasets = [load_ising(ly, lattice=lattice, periodicity=periodicity) for ly in layouts]  # type: ignore[arg-type]
    ns = np.array([d.num_spins for d in datasets])
    hc_infl = np.array([estimate_critical_field(d) for d in datasets])

    # Binder: pair each dataset with the next larger one; smallest gets (0,1) pair
    hc_bind = np.empty(len(datasets))
    for k in range(len(datasets)):
        a, b = datasets[max(0, k - 1)], datasets[min(k + 1, len(datasets) - 1)]
        hc_bind[k] = binder_crossing(a, b)

    return ns, hc_infl, hc_bind


# ---------------------------------------------------------------------------
# Power-law fit  h_c(N) = h_c_inf - a * N^{-1/nu}
# ---------------------------------------------------------------------------

def _hc_model(n: np.ndarray, h_inf: float, a: float, inv_nu: float) -> np.ndarray:
    return h_inf - a * n ** (-inv_nu)


def fit_hc_power_law(
    ns: np.ndarray,
    hcs: np.ndarray,
    *,
    nu_fixed: float | None = None,
) -> dict[str, float]:
    """Fit h_c(N) = h_c(∞) − a·N^{−1/ν}.

    If `nu_fixed` is given (e.g. 1.0 for the exact 1D result) the exponent is
    held fixed and only h_c(∞) and a are fitted.  Otherwise all three are free.
    Returns a dict with keys 'h_inf', 'a', 'nu'.
    """
    if nu_fixed is not None:
        def model(n, h_inf, a):
            return h_inf - a * n ** (-1.0 / nu_fixed)
        p0 = [1.0, 0.5]
        popt, _ = curve_fit(model, ns, hcs, p0=p0)
        return {"h_inf": float(popt[0]), "a": float(popt[1]), "nu": float(nu_fixed)}

    p0 = [1.0, 0.5, 1.0]
    bounds = ([0.5, 0.0, 0.1], [2.0, 5.0, 5.0])
    popt, _ = curve_fit(_hc_model, ns, hcs, p0=p0, bounds=bounds)
    return {"h_inf": float(popt[0]), "a": float(popt[1]), "nu": float(1.0 / popt[2])}


# ---------------------------------------------------------------------------
# Central charge vs N
# ---------------------------------------------------------------------------

def collect_central_charges(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
) -> tuple[np.ndarray, np.ndarray]:
    """Return (ns, cs) from the Calabrese–Cardy fit at the nearest-critical field."""
    ns, cs = [], []
    for ly in layouts:
        data = load_ising(ly, lattice=lattice, periodicity=periodicity)  # type: ignore[arg-type]
        cf = fit_central_charge(data, periodicity=periodicity)
        ns.append(data.num_spins)
        cs.append(cf.central_charge)
    return np.array(ns), np.array(cs)


# ---------------------------------------------------------------------------
# Plots
# ---------------------------------------------------------------------------

def plot_hc_scaling(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
    out_path: Path | None = None,
) -> Path:
    """h_c(N) from inflection and Binder crossing + power-law extrapolation."""
    import matplotlib.pyplot as plt

    ns, hc_infl, hc_bind = collect_hc_estimates(layouts, lattice=lattice, periodicity=periodicity)

    fit_infl = fit_hc_power_law(ns, hc_infl)
    fit_bind = fit_hc_power_law(ns, hc_bind)

    colors = {"inflection": "#1f77b4", "binder": "#d62728"}

    setup_style()
    fig, ax = plt.subplots(figsize=(7, 5))

    x = 1.0 / ns
    ax.plot(x, hc_infl, "o", color=colors["inflection"], ms=8, label="inflection (magnetisation)")
    ax.plot(x, hc_bind, "s", color=colors["binder"], ms=8, label="Binder crossing")

    x_ext = np.linspace(0, 1.0 / ns.min(), 300)
    for key, fit, ls in [
        ("inflection", fit_infl, "-"),
        ("binder", fit_bind, "--"),
    ]:
        # parametric: h_c(N) = h_inf - a * N^{-1/nu} with N = 1/x
        ax.plot(
            x_ext,
            fit["h_inf"] - fit["a"] * (1.0 / np.where(x_ext > 0, x_ext, np.inf)) ** (-1.0 / fit["nu"]),
            ls, color=colors[key], lw=1.4,
            label=f"fit ({key}): $h_c^\\infty={fit['h_inf']:.3f}$, $\\nu={fit['nu']:.2f}$",
        )

    ax.axhline(1.0, color="k", ls=":", lw=1, alpha=0.6, label="exact $h_c=1$")
    ax.axvline(0.0, color="gray", ls=":", lw=0.8, alpha=0.4)

    for n_val, hc_i in zip(ns, hc_infl):
        ax.annotate(f"N={n_val}", (1.0 / n_val, hc_i),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)

    ax.set_xlabel(r"$1/N$")
    ax.set_ylabel(r"$h_c(N)$")
    ax.set_title("Finite-size extrapolation of the critical field")
    ax.legend(fontsize=9)
    return save_fig(fig, f"finite_size_hc_{lattice}_{periodicity}", out_path=out_path)


def plot_central_charge_scaling(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
    out_path: Path | None = None,
) -> Path:
    """Central charge c(N) vs 1/N, approaching the CFT value c=1/2."""
    import matplotlib.pyplot as plt

    ns, cs = collect_central_charges(layouts, lattice=lattice, periodicity=periodicity)

    # Linear fit in 1/N: c(N) = c_inf + b/N
    x = 1.0 / ns
    slope, intercept = np.polyfit(x, cs, 1)
    x_plot = np.linspace(0, x.max() * 1.1, 200)

    setup_style()
    fig, ax = plt.subplots(figsize=(7, 5))
    for n_val, c_val in zip(ns, cs):
        ax.plot(1.0 / n_val, c_val, "o", color=color_for_n(n_val), ms=9, label=f"N={n_val}")
    ax.plot(x_plot, intercept + slope * x_plot, "k--", lw=1.4,
            label=f"linear fit → $c_\\infty={intercept:.3f}$")
    ax.axhline(0.5, color="gray", ls=":", lw=1.2, label="CFT value $c=1/2$")
    ax.axvline(0.0, color="gray", ls=":", lw=0.8, alpha=0.4)
    ax.set_xlabel(r"$1/N$")
    ax.set_ylabel("central charge $c$")
    ax.set_title("Calabrese–Cardy central charge: finite-size convergence")
    ax.legend()
    return save_fig(fig, f"central_charge_scaling_{lattice}_{periodicity}", out_path=out_path)


if __name__ == "__main__":
    ns, hc_infl, hc_bind = collect_hc_estimates()
    for n, hi, hb in zip(ns, hc_infl, hc_bind):
        print(f"N={n:2d}  inflection={hi:.3f}  binder={hb:.3f}")

    fit = fit_hc_power_law(ns, hc_infl)
    print(f"\nPower-law fit (inflection):  h_c(∞)={fit['h_inf']:.4f}  ν={fit['nu']:.3f}")
    fit_b = fit_hc_power_law(ns, hc_bind)
    print(f"Power-law fit (binder):      h_c(∞)={fit_b['h_inf']:.4f}  ν={fit_b['nu']:.3f}")

    ns_c, cs = collect_central_charges()
    print("\nCentral charge vs N (CFT c = 0.5):")
    for n, c in zip(ns_c, cs):
        print(f"  N={n:2d}  c={c:.4f}")

    p1 = plot_hc_scaling()
    print(f"\nwrote {p1}")
    p2 = plot_central_charge_scaling()
    print(f"wrote {p2}")
