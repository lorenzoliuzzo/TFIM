from __future__ import annotations

from src.boundary_comparison import compare_boundary_conditions


def test_closed_chain_converges_faster_than_open() -> None:
    results = compare_boundary_conditions()
    assert set(results) == {"open", "closed"}
    for res in results.values():
        assert res["hc_infl"].shape == (3,)

    # Periodic (closed) boundaries have no edge effects, so the finite-size
    # h_c estimate should sit closer to the exact h_c=1 already at N=4.
    assert abs(results["closed"]["hc_infl"][0] - 1.0) < abs(results["open"]["hc_infl"][0] - 1.0)
