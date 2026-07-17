from __future__ import annotations

import numpy as np
import pytest

from src.loader import load_ising
from src.vqe_hva import anneal_init, run_qaoa, run_vqe_hva


@pytest.fixture(scope="module")
def data():
    return load_ising("1x4", lattice="chain", periodicity="open")


def test_anneal_init_shape_and_schedule() -> None:
    p = np.asarray(anneal_init(4, dt=0.3))
    assert p.shape == (4, 2)
    # gamma (col 0) increases, beta (col 1) decreases across layers
    assert np.all(np.diff(p[:, 0]) > 0)
    assert np.all(np.diff(p[:, 1]) < 0)
    # gamma_k + beta_k = dt for every layer
    assert np.allclose(p.sum(axis=1), 0.3)


def test_qaoa_accurate_in_paramagnet(data) -> None:
    i = data.n_fields - 1
    res = run_qaoa(data.hamiltonians[i], data.num_spins, n_layers=4, steps=200)
    assert res.energy == pytest.approx(data.ground_energies[i], abs=1e-2)


def test_qaoa_respects_variational_bound(data) -> None:
    i = 60
    res = run_qaoa(data.hamiltonians[i], data.num_spins, n_layers=4, steps=150)
    assert res.energy >= data.ground_energies[i] - 1e-6


def test_unknown_init_strategy_raises(data) -> None:
    with pytest.raises(ValueError):
        run_vqe_hva(data.hamiltonians[0], data.num_spins, n_layers=2, steps=1,
                    init_strategy="bogus")
