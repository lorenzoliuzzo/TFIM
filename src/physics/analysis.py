from __future__ import annotations

from pathlib import Path

import numpy as np

from src.core.loader import IsingData, load_ising
from src.core.plotting import color_for_n, save_fig, setup_style


def magnetization_per_spin(data: IsingData) -> np.ndarray:
    """Order parameter <|M_z|> normalized by system size, in [0, 1]."""
    return data.order_params / data.num_spins


def steepest_field(
    y: np.ndarray, fields: np.ndarray, *, h_min: float = 0.2, sign: str = "negative"
) -> float:
    """The h of steepest change of `y(h)`, restricted to h >= `h_min`.

    The h_min window excludes the h->0 boundary artifact (at exactly h=0 the
    dataset returns a symmetry-broken product state, creating a spurious cliff
    in both magnetization and entropy that otherwise hijacks the argmax).
    `sign` picks the steepest descent ("negative") or steepest slope ("abs").
    """
    mask = fields >= h_min
    dydh = np.gradient(y, fields)
    score = -dydh if sign == "negative" else np.abs(dydh)
    score = np.where(mask, score, -np.inf)
    return float(fields[np.argmax(score)])


def estimate_critical_field(data: IsingData) -> float:
    """Finite-size critical-field estimate: the h of steepest drop of <m>(h)."""
    return steepest_field(magnetization_per_spin(data), data.fields)


def plot_order_parameter(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
    out_path: Path | None = None,
) -> Path:
    """Plot normalized magnetization <|M_z|>/N vs transverse field h for several
    system sizes, marking the steepest-descent estimate of the critical field."""
    import matplotlib.pyplot as plt

    setup_style()
    fig, ax = plt.subplots(figsize=(7, 5))
    for layout in layouts:
        data = load_ising(layout, lattice=lattice, periodicity=periodicity)  # type: ignore[arg-type]
        m = magnetization_per_spin(data)
        hc = estimate_critical_field(data)
        c = color_for_n(data.num_spins)
        ax.plot(data.fields, m, marker=".", ms=4, color=c,
                label=f"N={data.num_spins} ($h_c\\approx{hc:.2f}$)")
        ax.axvline(hc, color=c, ls=":", lw=1, alpha=0.5)

    ax.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6, label="$h/|J|=1$ (exact, $N\\to\\infty$)")
    ax.set_xlabel("transverse field $h$")
    ax.set_ylabel(r"$\langle |M_z| \rangle / N$")
    ax.set_title(f"TFIM order parameter — {lattice}, {periodicity} BC")
    ax.legend()
    return save_fig(fig, f"order_parameter_{lattice}_{periodicity}", out_path=out_path)


def magnetization_moments(data: IsingData) -> tuple[np.ndarray, np.ndarray]:
    """<M_z^2>(h) and <M_z^4>(h) from the exact ground states, M_z = sum_i sigma_i^z.

    Computed directly from Born probabilities |<b|psi>|^2 of each computational
    basis state b, whose magnetization is m(b) = sum_i (1 - 2 b_i).
    """
    n = data.num_spins
    idx = np.arange(1 << n)
    bits = (idx[:, None] >> np.arange(n)[::-1]) & 1
    mz = (1 - 2 * bits).sum(axis=1).astype(float)  # per basis state
    m2, m4 = [], []
    for psi in data.ground_states:
        p = np.abs(np.asarray(psi)) ** 2
        m2.append(float((p * mz**2).sum()))
        m4.append(float((p * mz**4).sum()))
    return np.array(m2), np.array(m4)


def binder_cumulant(data: IsingData) -> np.ndarray:
    """Binder cumulant U_4(h) = 1 - <M_z^4> / (3 <M_z^2>^2).

    Dimensionless: -> 2/3 in the ordered phase (M_z sharply two-valued at +-M0,
    so <M_z^4> = <M_z^2>^2) and -> 0 in the disordered phase (Gaussian M_z, so
    <M_z^4> = 3<M_z^2>^2). Curves for different N cross near the critical field
    with weak finite-size drift, giving a cleaner h_c estimate than the
    magnetization inflection.
    """
    m2, m4 = magnetization_moments(data)
    return 1.0 - m4 / (3.0 * m2**2)


def binder_crossing(data_a: IsingData, data_b: IsingData) -> float:
    """Field where the Binder cumulants of two sizes cross (linear interpolation
    of their difference on the shared field grid)."""
    fields = data_a.fields
    diff = binder_cumulant(data_a) - binder_cumulant(data_b)
    sign_change = np.where(np.diff(np.sign(diff)) != 0)[0]
    if len(sign_change) == 0:
        return float(fields[np.argmin(np.abs(diff))])
    i = sign_change[len(sign_change) // 2]
    # linear interpolation between i and i+1 where diff crosses zero
    h0, h1, d0, d1 = fields[i], fields[i + 1], diff[i], diff[i + 1]
    return float(h0 - d0 * (h1 - h0) / (d1 - d0))


def plot_binder(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
    out_path: Path | None = None,
) -> Path:
    """Binder cumulant U_4 vs h for several sizes; the crossing locates h_c."""
    import matplotlib.pyplot as plt

    setup_style()
    fig, ax = plt.subplots(figsize=(7, 5))
    datasets = [load_ising(ly, lattice=lattice, periodicity=periodicity) for ly in layouts]  # type: ignore[arg-type]
    for data in datasets:
        ax.plot(data.fields, binder_cumulant(data), "-", color=color_for_n(data.num_spins),
                label=f"N={data.num_spins}")
    if len(datasets) >= 2:
        hc = binder_crossing(datasets[-2], datasets[-1])
        ax.axvline(hc, color="k", ls=":", lw=1.2, alpha=0.7,
                   label=f"crossing $h\\approx{hc:.2f}$")
    ax.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6, label="$h/|J|=1$")
    ax.axhline(2 / 3, color="gray", ls=":", lw=1, alpha=0.6, label=r"ordered: $U_4=2/3$")
    ax.set_xlabel("transverse field $h$")
    ax.set_ylabel(r"Binder cumulant $U_4 = 1 - \langle M_z^4\rangle/3\langle M_z^2\rangle^2$")
    ax.set_title(f"Binder-cumulant crossing — {lattice}, {periodicity} BC")
    ax.legend()
    return save_fig(fig, f"binder_cumulant_{lattice}_{periodicity}", out_path=out_path)


def plot_data_collapse(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
    h_c: float = 1.0,
    beta_over_nu: float = 0.125,
    nu: float = 1.0,
    out_path: Path | None = None,
) -> Path:
    """Finite-size data collapse of the order parameter onto the universal curve.

    With the exact 2D-Ising-universality exponents (beta/nu = 1/8, nu = 1), the
    rescaled magnetization N^{beta/nu} <|M_z|>/N plotted against the scaling
    variable (h - h_c) N^{1/nu} collapses all system sizes onto one curve.
    """
    import matplotlib.pyplot as plt

    setup_style()
    fig, (ax_raw, ax) = plt.subplots(1, 2, figsize=(12, 5))
    for layout in layouts:
        data = load_ising(layout, lattice=lattice, periodicity=periodicity)  # type: ignore[arg-type]
        n = data.num_spins
        m = magnetization_per_spin(data)
        c = color_for_n(n)
        ax_raw.plot(data.fields, m, "-", color=c, label=f"N={n}")
        x = (data.fields - h_c) * n ** (1.0 / nu)
        y = n**beta_over_nu * m
        ax.plot(x, y, "-", color=c, label=f"N={n}")

    ax_raw.axvline(h_c, color="k", ls="--", lw=1, alpha=0.6)
    ax_raw.set_xlabel("transverse field $h$")
    ax_raw.set_ylabel(r"$\langle|M_z|\rangle/N$")
    ax_raw.set_title("Raw order parameter")
    ax_raw.legend()

    ax.axvline(0.0, color="k", ls="--", lw=1, alpha=0.6)
    ax.set_xlabel(r"$(h - h_c)\,N^{1/\nu}$")
    ax.set_ylabel(r"$N^{\beta/\nu}\,\langle|M_z|\rangle/N$")
    ax.set_title(rf"Data collapse ($h_c={h_c}$, $\beta/\nu={beta_over_nu}$, $\nu={nu}$)")
    ax.set_xlim(-6, 6)
    ax.legend()
    return save_fig(fig, f"data_collapse_{lattice}_{periodicity}", out_path=out_path)


if __name__ == "__main__":
    path = plot_order_parameter()
    print(f"wrote {path}")
    bpath = plot_binder()
    print(f"wrote {bpath}")
    cpath = plot_data_collapse()
    print(f"wrote {cpath}")
    datasets = [load_ising(ly) for ly in ("1x4", "1x8", "1x16")]
    for d in datasets:
        print(f"N={d.num_spins:2d}  inflection h_c = {estimate_critical_field(d):.3f}")
    print(f"Binder crossing N=8/16: h_c = {binder_crossing(datasets[1], datasets[2]):.3f}")
