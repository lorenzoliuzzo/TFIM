from __future__ import annotations

from src.lattice_2d import collect_2d_critical_fields


def test_2d_critical_field_grows_with_more_neighbours() -> None:
    hcs = collect_2d_critical_fields()
    assert set(hcs) == {"2x2", "2x4", "2x8", "4x4"}
    # More nearest neighbours per site (closer to the square-lattice limit)
    # should push the finite-size h_c further above the 1D value of 1.
    assert hcs["2x2"] < hcs["2x4"] < hcs["2x8"] < hcs["4x4"]
