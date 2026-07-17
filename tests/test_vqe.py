from __future__ import annotations

import numpy as np
import pytest

from src.loader import load_ising
from src.vqe import abs_mz_from_state, run_adam, run_vqe, sweep_vqe


@pytest.fixture(scope="module")
def data():
    return load_ising("1x4", lattice="chain", periodicity="open")


def test_abs_mz_matches_dataset_on_exact_states(data) -> None:
    # The statevector-based order parameter must reproduce the dataset values.
    for i in (0, 30, 60, 99):
        m = abs_mz_from_state(np.asarray(data.ground_states[i]), data.num_spins)
        assert m == pytest.approx(data.order_params[i], abs=1e-6)


def test_abs_mz_extremes() -> None:
    # |0000> -> all spins +1 -> |M_z| = 4
    s = np.zeros(16); s[0] = 1.0
    assert abs_mz_from_state(s, 4) == pytest.approx(4.0)


def test_vqe_recovers_ground_energy(data) -> None:
    # Deep in the paramagnetic phase the ansatz should reach the ground energy.
    i = 99
    res = run_vqe(data.hamiltonians[i], data.num_spins, n_layers=3, steps=300)
    assert res.energy == pytest.approx(data.ground_energies[i], abs=1e-2)
    assert res.history[0] > res.history[-1]  # energy decreased


def test_early_stopping_halts_before_budget(data) -> None:
    # On a converging landscape the optimizer should stop well before a large
    # step ceiling, yet still reach the ground energy.
    i = 99
    res = run_vqe(data.hamiltonians[i], data.num_spins, n_layers=3,
                  steps=5000, patience=15)
    assert len(res.history) < 5000  # early-stopped
    assert res.energy == pytest.approx(data.ground_energies[i], abs=1e-2)


def test_run_adam_stops_on_plateau() -> None:
    # A trivial constant objective plateaus immediately: stop after ~patience.
    import pennylane.numpy as pnp

    calls = {"n": 0}

    def const_energy(params):
        calls["n"] += 1
        return pnp.sum(0.0 * params)

    params = pnp.array([0.1, 0.2], requires_grad=True)
    _, history = run_adam(const_energy, params, stepsize=0.1, max_steps=1000, patience=10)
    assert len(history) <= 12  # stalls almost immediately, far below max_steps


def test_sweep_shapes(data) -> None:
    sw = sweep_vqe(data, indices=[0, 99], steps=50)
    assert sw.fields.shape == (2,)
    assert sw.vqe_energies.shape == sw.exact_energies.shape == (2,)
    assert np.all(sw.vqe_energies >= sw.exact_energies - 1e-6)  # variational bound
