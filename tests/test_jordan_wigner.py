from __future__ import annotations

import numpy as np
import pytest

from src.jordan_wigner import ground_energy_analytic
from src.loader import load_ising


@pytest.mark.parametrize("layout", ["1x4", "1x8", "1x16"])
def test_jw_matches_dataset_closed_chain(layout: str) -> None:
    data = load_ising(layout, lattice="chain", periodicity="closed")
    for i in (0, 25, 50, 75, 99):
        h = float(data.fields[i])
        analytic = ground_energy_analytic(data.num_spins, h)
        assert analytic == pytest.approx(float(data.ground_energies[i]), abs=1e-6)


def test_gap_closes_near_criticality() -> None:
    from src.jordan_wigner import gap_analytic

    n = 200  # large N: gap should be small at h=1, much larger away from it
    assert gap_analytic(n, 1.0) < gap_analytic(n, 0.3)
    assert gap_analytic(n, 1.0) < gap_analytic(n, 3.0)
    assert np.isclose(gap_analytic(n, 1.0), 0.0, atol=0.1)
