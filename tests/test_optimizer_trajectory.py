from __future__ import annotations

import pytest

from src.loader import load_ising
from src.optimizer_trajectory import energy_error_trajectories


@pytest.fixture(scope="module")
def data():
    return load_ising("1x4", lattice="chain", periodicity="open")


def test_trajectories_have_one_curve_per_ansatz(data) -> None:
    trajectories = energy_error_trajectories(data, field_index=30, n_layers=3, steps=20)
    assert set(trajectories) == {"HEA", "HVA", "QAOA"}
    for errors in trajectories.values():
        assert len(errors) == 20
        assert all(e >= 0 for e in errors)


def test_trajectories_generally_decrease(data) -> None:
    trajectories = energy_error_trajectories(data, field_index=30, n_layers=3, steps=40)
    for errors in trajectories.values():
        assert errors[-1] <= errors[0]
