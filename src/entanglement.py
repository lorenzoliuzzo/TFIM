from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.loader import IsingData
from src.plotting import color_for_n, save_fig, setup_style


def entanglement_entropy(state: np.ndarray, num_spins: int, cut: int | None = None) -> float:
    """Von Neumann entropy S = -Tr[ρ_A ln ρ_A] of the contiguous block [0, cut).

    Reshape the statevector into a (2^cut × 2^(N-cut)) matrix; its squared
    singular values are the Schmidt (eigenvalue) probabilities of ρ_A.
    PennyLane orders wire 0 as the most significant bit, so the first `cut`
    wires form block A under this reshape.
    """
    if cut is None:
        cut = num_spins // 2
    psi = np.asarray(state).reshape(2**cut, 2 ** (num_spins - cut))
    svals = np.linalg.svd(psi, compute_uv=False)
    probs = svals**2
    probs = probs[probs > 1e-12]
    return float(-np.sum(probs * np.log(probs)))


def entropy_vs_field(data: IsingData, cut: int | None = None) -> np.ndarray:
    """Half-chain entanglement entropy at every field value in the sweep."""
    return np.array([entanglement_entropy(s, data.num_spins, cut) for s in data.ground_states])


def quasi_degenerate_cutoff(
    fields: np.ndarray, s: np.ndarray, *, search_window: float = 0.3, thresh: float = 0.55
) -> float:
    """Field below which S(h) is likely an artifact of near-degenerate ground states.

    Deep in the ordered phase the two symmetry-broken branches are split by an
    exponentially small (in N) finite-size gap; an eigensolver has no reason to
    return the same member of that near-degenerate pair from one field to the
    next, so S(h) — unlike the order parameter, which stays smooth — can swing
    between ~0 (a classical product-like branch) and ~ln2 (the symmetric cat
    combination) within the same plateau region. Returns the field just past
    the last such swing seen in `h <= search_window`, or 0.0 if none.
    """
    mask = fields <= search_window
    unstable = np.where(mask & (s < thresh))[0]
    if len(unstable) == 0:
        return 0.0
    last = unstable[-1]
    return float(fields[min(last + 1, len(fields) - 1)])


def entropy_vs_subsystem(data: IsingData, field_index: int) -> tuple[np.ndarray, np.ndarray]:
    """At a fixed field, S(l) for every block size l = 1 .. N-1."""
    psi = data.ground_states[field_index]
    ls = np.arange(1, data.num_spins)
    s = np.array([entanglement_entropy(psi, data.num_spins, int(l)) for l in ls])
    return ls, s


@dataclass(frozen=True)
class CentralChargeFit:
    central_charge: float
    intercept: float
    field: float
    ls: np.ndarray
    entropies: np.ndarray
    x: np.ndarray  # the Calabrese-Cardy conformal coordinate
    coefficient: float = 6.0  # c/6 (open chain, one boundary pair) or c/3 (ring)

    @property
    def fit_entropies(self) -> np.ndarray:
        return (self.central_charge / self.coefficient) * self.x + self.intercept


def fit_central_charge(
    data: IsingData, field_index: int | None = None, *, periodicity: str = "open"
) -> CentralChargeFit:
    """Extract the central charge from the Calabrese-Cardy law.

    Open chain (two boundaries): S(l) = (c/6) ln[ (2N/π) sin(π l/N) ] + const.
    Closed/periodic ring (translation-invariant, no boundary): the coefficient
    halves to c/3, and the subleading corrections from boundary-localized
    irrelevant operators (the source of the open-chain bias, arXiv:1002.4353)
    are absent — so the ring fit is expected to land closer to the Ising CFT
    value c = 1/2 at the same finite N.

    Linear regression of S(l) against x = ln[(N/π) sin(π l/N)] (ring) or
    ln[(2N/π) sin(π l/N)] (chain). If `field_index` is None, use the field
    closest to the critical point h=1.
    """
    if periodicity not in ("open", "closed"):
        raise ValueError(f"periodicity must be 'open' or 'closed', got {periodicity!r}")
    if field_index is None:
        field_index = int(np.argmin(np.abs(data.fields - 1.0)))
    n = data.num_spins
    ls, s = entropy_vs_subsystem(data, field_index)
    prefactor = (2 * n / np.pi) if periodicity == "open" else (n / np.pi)
    coefficient = 6.0 if periodicity == "open" else 3.0
    x = np.log(prefactor * np.sin(np.pi * ls / n))
    slope, intercept = np.polyfit(x, s, 1)
    return CentralChargeFit(
        central_charge=float(coefficient * slope),
        intercept=float(intercept),
        field=float(data.fields[field_index]),
        ls=ls,
        entropies=s,
        x=x,
        coefficient=coefficient,
    )


def plot_entropy_vs_field(
    layouts: tuple[str, ...] = ("1x8", "1x16"),
    *,
    lattice: str = "chain",
    periodicity: str = "open",
    out_path: Path | None = None,
) -> Path:
    """Half-chain entropy vs h for several sizes — the peak marks criticality."""
    from src.analysis import steepest_field
    from src.loader import load_ising

    import matplotlib.pyplot as plt

    setup_style()
    fig, ax = plt.subplots(figsize=(7, 5))
    max_cutoff = 0.0
    for layout in layouts:
        data = load_ising(layout, lattice=lattice, periodicity=periodicity)  # type: ignore[arg-type]
        s = entropy_vs_field(data)
        # Critical crossover = steepest descent of S(h), windowed away from the
        # h->0 product-state cliff (the cat-state ln2 plateau masks a literal peak).
        h_cross = steepest_field(s, data.fields)
        max_cutoff = max(max_cutoff, quasi_degenerate_cutoff(data.fields, s))
        c = color_for_n(data.num_spins)
        ax.plot(data.fields, s, "-", color=c,
                label=f"N={data.num_spins} (crossover $h\\approx{h_cross:.2f}$)")
        ax.axvline(h_cross, color=c, ls=":", lw=1, alpha=0.5)
    if max_cutoff > 0:
        ax.axvspan(0, max_cutoff, color="gray", alpha=0.12, zorder=0)
        ax.annotate("quasi-degenerate GS\n(solver picks a branch)",
                    xy=(max_cutoff, 0.5), xytext=(6, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=8, color="dimgray")
    ax.axhline(np.log(2), color="gray", ls=":", lw=1, alpha=0.7, label=r"$\ln 2$ (cat / SSB plateau)")
    ax.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6, label="$h/|J|=1$")
    ax.set_xlabel("transverse field $h$")
    ax.set_ylabel("half-chain entanglement entropy $S$")
    ax.set_title("Entanglement across the quantum phase transition")
    ax.legend()
    return save_fig(fig, f"entropy_vs_field_{lattice}_{periodicity}", out_path=out_path)


def plot_central_charge(
    fit: CentralChargeFit, num_spins: int, *, periodicity: str = "open", out_path: Path | None = None
) -> Path:
    """S(l) vs the conformal coordinate, with the fitted Calabrese-Cardy line."""
    import matplotlib.pyplot as plt

    setup_style()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(fit.x, fit.entropies, "o", ms=7, color=color_for_n(num_spins),
            label="data (exact ground state)")
    order = np.argsort(fit.x)
    ax.plot(fit.x[order], fit.fit_entropies[order], "-", color="k",
            label=f"fit: $c={fit.central_charge:.3f}$  (Ising: $c=1/2$)")
    prefactor = r"\frac{2N}{\pi}" if periodicity == "open" else r"\frac{N}{\pi}"
    ax.set_xlabel(rf"$\ln\left[{prefactor}\sin\frac{{\pi l}}{{N}}\right]$")
    ax.set_ylabel("entanglement entropy $S(l)$")
    ax.set_title(f"Central charge, {periodicity} BC (N={num_spins}, h={fit.field:.2f})")
    ax.legend()
    return save_fig(fig, f"central_charge_{periodicity}_N{num_spins}", out_path=out_path)


if __name__ == "__main__":
    from src.loader import load_ising

    p1 = plot_entropy_vs_field(("1x4", "1x8", "1x16"))
    print(f"wrote {p1}")

    data = load_ising("1x16")
    fit = fit_central_charge(data, periodicity="open")
    p2 = plot_central_charge(fit, data.num_spins, periodicity="open")
    print(f"wrote {p2}")

    data_c = load_ising("1x16", periodicity="closed")
    fit_c = fit_central_charge(data_c, periodicity="closed")
    p3 = plot_central_charge(fit_c, data_c.num_spins, periodicity="closed")
    print(f"wrote {p3}")

    print("\ncentral charge vs system size (Ising CFT value c = 0.5):")
    for layout in ("1x8", "1x16"):
        d_open = load_ising(layout, periodicity="open")
        f_open = fit_central_charge(d_open, periodicity="open")
        d_closed = load_ising(layout, periodicity="closed")
        f_closed = fit_central_charge(d_closed, periodicity="closed")
        print(f"  N={d_open.num_spins:2d}  open:   h={f_open.field:.3f}  c = {f_open.central_charge:.4f}")
        print(f"  N={d_closed.num_spins:2d}  closed: h={f_closed.field:.3f}  c = {f_closed.central_charge:.4f}")
