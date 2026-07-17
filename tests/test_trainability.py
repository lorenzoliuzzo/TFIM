from __future__ import annotations

from src.loader import load_ising
from src.trainability import gradient_variance, plot_barren_plateaus


def test_gradient_variance_positive_finite() -> None:
    d = load_ising("1x4")
    for ansatz in ("hea", "hva"):
        v = gradient_variance(ansatz, d.num_spins, d.hamiltonians[50],
                              n_layers=3, n_samples=15)
        assert v > 0 and v < 1e6


def test_hea_gradient_variance_decays_with_N() -> None:
    # Barren-plateau signature: HEA gradient variance shrinks as N grows.
    d4, d8 = load_ising("1x4"), load_ising("1x8")
    v4 = gradient_variance("hea", d4.num_spins, d4.hamiltonians[50], n_layers=4, n_samples=40)
    v8 = gradient_variance("hea", d8.num_spins, d8.hamiltonians[50], n_layers=4, n_samples=40)
    assert v8 < v4


def test_plot_written(tmp_path) -> None:
    out = plot_barren_plateaus(("1x4", "1x8"), ("hea", "hva"),
                               n_layers=3, n_samples=15, out_path=tmp_path / "bp.png")
    assert out.exists() and out.stat().st_size > 0
