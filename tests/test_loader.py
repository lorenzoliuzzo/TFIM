from __future__ import annotations

import numpy as np
import pennylane as qml
import pytest

from src.loader import VALID_LAYOUTS, IsingData, load_ising


@pytest.fixture(scope="module")
def data() -> IsingData:
    # Smallest system keeps the download/test fast.
    return load_ising("1x4", lattice="chain", periodicity="open")


def test_shapes_consistent(data: IsingData) -> None:
    n = data.n_fields
    assert n == 100
    assert data.num_spins == 4
    assert data.fields.shape == (n,)
    assert data.ground_energies.shape == (n,)
    assert data.order_params.shape == (n,)
    assert len(data.hamiltonians) == n
    assert len(data.ground_states) == n
    assert data.ground_states[0].shape == (2**data.num_spins,)


def test_fields_sweep_zero_to_three(data: IsingData) -> None:
    assert data.fields.min() == pytest.approx(0.0)
    assert data.fields.max() == pytest.approx(3.0)
    assert np.all(np.diff(data.fields) > 0)  # monotonically increasing


def test_ground_state_solves_hamiltonian(data: IsingData) -> None:
    # The stored ground state must be an eigenvector of the stored Hamiltonian
    # at the stored ground energy. Check a mid-sweep field.
    i = 50
    h_mat = qml.matrix(data.hamiltonians[i], wire_order=range(data.num_spins))
    psi = data.ground_states[i]
    energy = (psi.conj() @ h_mat @ psi).real
    assert energy == pytest.approx(data.ground_energies[i], abs=1e-6)


def test_order_param_decreases_with_field(data: IsingData) -> None:
    # Ordered (large <|M_z|>) at h=0, paramagnetic (small) at large h.
    assert data.order_params[0] > data.order_params[-1]
    assert data.order_params[0] == pytest.approx(data.num_spins, abs=1e-6)


@pytest.mark.parametrize(
    "lattice,layout",
    [("chain", "bogus"), ("rectangular", "1x4"), ("sphere", "1x4")],
)
def test_invalid_arguments_raise(lattice: str, layout: str) -> None:
    with pytest.raises(ValueError):
        load_ising(layout, lattice=lattice)  # type: ignore[arg-type]


def test_valid_layouts_table() -> None:
    assert VALID_LAYOUTS["chain"] == ("1x4", "1x8", "1x16")
