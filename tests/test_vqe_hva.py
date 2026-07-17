from __future__ import annotations

import numpy as np
import pytest

from src.loader import load_ising
from src.vqe_hva import extract_structure, run_vqe_hva, warm_start_sweep


@pytest.fixture(scope="module")
def data():
    return load_ising("1x4", lattice="chain", periodicity="open")


def test_extract_structure_open_chain(data) -> None:
    bonds, field_wires = extract_structure(data.hamiltonians[50])
    assert bonds == [(0, 1), (1, 2), (2, 3)]  # open chain of 4 sites
    assert sorted(field_wires) == [0, 1, 2, 3]


def test_extract_structure_closed_chain() -> None:
    d = load_ising("1x4", lattice="chain", periodicity="closed")
    bonds, _ = extract_structure(d.hamiltonians[50])
    assert (3, 0) in bonds or (0, 3) in bonds  # periodic bond present
    assert len(bonds) == 4


def test_hva_accurate_in_paramagnet(data) -> None:
    # Large field: |->^N start makes this nearly exact even at shallow depth.
    i = data.n_fields - 1
    res = run_vqe_hva(data.hamiltonians[i], data.num_spins, n_layers=4, steps=200)
    assert res.energy == pytest.approx(data.ground_energies[i], abs=1e-2)


def test_hva_respects_variational_bound(data) -> None:
    i = 60
    res = run_vqe_hva(data.hamiltonians[i], data.num_spins, n_layers=4, steps=150)
    assert res.energy >= data.ground_energies[i] - 1e-6


def test_warm_start_sweep_runs(data) -> None:
    sw = warm_start_sweep(data, n_layers=4, steps=60, indices=[0, 50, 99])
    assert sw.fields.shape == (3,)
    assert np.all(np.diff(sw.fields) > 0)  # returned in ascending field order
    assert np.all(sw.abs_errors >= 0)
