from __future__ import annotations

from src.benchmark import compare_ansatze
from src.loader import load_ising


def test_compare_ansatze_outputs(tmp_path) -> None:
    data = load_ising("1x4", lattice="chain", periodicity="open")
    out = tmp_path / "cmp.png"
    path, df = compare_ansatze(data, n_layers=3, steps=40, n_fields=3, seeds=(0, 1),
                               n_jobs=1, out_path=out)
    assert path.exists() and path.stat().st_size > 0
    assert set(df["ansatz"].unique()) == {
        "StronglyEntangling (random)", "HVA + warm-start", "QAOA (anneal) + warm-start"}
    assert len(df) == 3 * 3 * 2  # n_fields * 3 ansatze * seeds
    assert "seed" in df.columns
    assert (df["abs_E_error"] >= 0).all()
