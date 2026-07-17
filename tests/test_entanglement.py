from __future__ import annotations

import numpy as np
import pytest

from src.entanglement import (
    entanglement_entropy,
    entropy_vs_field,
    fit_central_charge,
    plot_central_charge,
    plot_entropy_vs_field,
    quasi_degenerate_cutoff,
)
from src.loader import load_ising


@pytest.fixture(scope="module")
def data():
    return load_ising("1x8", lattice="chain", periodicity="open")


def test_product_state_has_zero_entropy() -> None:
    psi = np.zeros(2**4)
    psi[0] = 1.0  # |0000>, a product state
    assert entanglement_entropy(psi, 4) == pytest.approx(0.0, abs=1e-12)


def test_bell_pair_has_ln2_entropy() -> None:
    psi = np.zeros(4)
    psi[0] = psi[3] = 1 / np.sqrt(2)  # (|00>+|11>)/sqrt2
    assert entanglement_entropy(psi, 2, cut=1) == pytest.approx(np.log(2), abs=1e-10)


def test_entropy_nonnegative_and_bounded(data) -> None:
    s = entropy_vs_field(data)
    assert s.shape == data.fields.shape
    assert np.all(s >= -1e-9)
    # half-chain entropy is bounded by cut * ln2
    assert np.all(s <= (data.num_spins // 2) * np.log(2) + 1e-9)


def test_paramagnet_less_entangled_than_critical(data) -> None:
    s = entropy_vs_field(data)
    i_crit = int(np.argmin(np.abs(data.fields - 1.0)))
    assert s[-1] < s[i_crit]  # deep paramagnet (large h) is nearly a product state


def test_central_charge_close_to_half(data) -> None:
    fit = fit_central_charge(data)
    assert fit.field == pytest.approx(1.0, abs=0.05)
    # Finite-size + open BC: expect within a reasonable band of the CFT value 1/2.
    assert 0.3 < fit.central_charge < 0.9


def test_quasi_degenerate_cutoff_flags_known_wobble() -> None:
    fields = np.array([0.0, 0.04, 0.08, 0.11, 0.15, 0.19])
    s = np.array([0.06, 0.0, 0.27, 0.67, 0.69, 0.69])  # mimics N=16 h->0 wobble
    cutoff = quasi_degenerate_cutoff(fields, s)
    assert cutoff == pytest.approx(0.11)


def test_quasi_degenerate_cutoff_zero_when_smooth() -> None:
    fields = np.array([0.0, 0.04, 0.08, 0.11])
    s = np.array([0.69, 0.69, 0.69, 0.68])
    assert quasi_degenerate_cutoff(fields, s) == 0.0


def test_plots_written(tmp_path, data) -> None:
    p1 = plot_entropy_vs_field(("1x8",), out_path=tmp_path / "e.png")
    fit = fit_central_charge(data)
    p2 = plot_central_charge(fit, data.num_spins, out_path=tmp_path / "c.png")
    assert p1.exists() and p1.stat().st_size > 0
    assert p2.exists() and p2.stat().st_size > 0
