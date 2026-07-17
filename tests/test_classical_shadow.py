from __future__ import annotations

import pytest

from src.classical_shadow import shadow_mz_squared, shadow_order_parameter_sweep
from src.loader import load_ising


@pytest.fixture(scope="module")
def data():
    return load_ising("1x4", lattice="chain", periodicity="open")


def test_shadow_mz_squared_matches_exact_in_ordered_phase(data) -> None:
    # Deep in the ordered phase the order parameter is large and the shadow
    # estimate should track sqrt(<M_z^2>) closely despite shot noise.
    i = 5
    import numpy as np

    est = shadow_mz_squared(data, i, k=10)
    exact_abs_mz = data.order_params[i]
    assert np.sqrt(est) == pytest.approx(exact_abs_mz, rel=0.2)


def test_shadow_sweep_shape_and_positivity(data) -> None:
    sweep = shadow_order_parameter_sweep(data, k=5)
    assert sweep.shape == (data.n_fields,)
    assert (sweep >= 0).all()
