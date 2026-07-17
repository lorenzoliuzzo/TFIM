from __future__ import annotations

import numpy as np
import pytest

from src.analysis import (
    binder_crossing,
    binder_cumulant,
    estimate_critical_field,
    magnetization_moments,
    magnetization_per_spin,
    plot_binder,
    plot_data_collapse,
    plot_order_parameter,
)
from src.loader import load_ising


@pytest.fixture(scope="module")
def data():
    return load_ising("1x4", lattice="chain", periodicity="open")


def test_magnetization_per_spin_in_unit_range(data) -> None:
    m = magnetization_per_spin(data)
    assert m.shape == data.fields.shape
    assert np.all(m >= 0) and np.all(m <= 1 + 1e-9)
    assert m[0] == pytest.approx(1.0, abs=1e-6)  # fully ordered at h=0


def test_critical_field_near_one(data) -> None:
    # Finite-size estimate should be in the ordered->disordered crossover region.
    hc = estimate_critical_field(data)
    assert 0.5 < hc < 1.6


def test_plot_written(tmp_path) -> None:
    out = tmp_path / "op.png"
    result = plot_order_parameter(layouts=("1x4",), out_path=out)
    assert result == out
    assert out.exists() and out.stat().st_size > 0


def test_binder_cumulant_limits(data) -> None:
    u = binder_cumulant(data)
    assert u.shape == data.fields.shape
    # At h=0 the dataset stores a single symmetry-broken product state (M_z=+/-N
    # with no fluctuation), so <M^4>/<M^2>^2 = 1 and U_4 = 1 - 1/3 = 2/3; the
    # ordered plateau, dropping in the disordered phase.
    assert u[0] == pytest.approx(2 / 3, abs=1e-6)
    assert u[-1] < u[0]
    assert np.all(u <= 2 / 3 + 1e-9)


def test_magnetization_moments_consistency(data) -> None:
    m2, m4 = magnetization_moments(data)
    # Jensen / moment ordering: <M^4> >= <M^2>^2 >= 0.
    assert np.all(m2 >= -1e-9)
    assert np.all(m4 + 1e-9 >= m2**2)


def test_binder_crossing_near_critical() -> None:
    d8 = load_ising("1x8")
    d16 = load_ising("1x16")
    hc = binder_crossing(d8, d16)
    assert 0.6 < hc < 1.2


def test_collapse_and_binder_plots_written(tmp_path) -> None:
    b = plot_binder(layouts=("1x4", "1x8"), out_path=tmp_path / "b.png")
    c = plot_data_collapse(layouts=("1x4", "1x8"), out_path=tmp_path / "c.png")
    assert b.exists() and b.stat().st_size > 0
    assert c.exists() and c.stat().st_size > 0
