from __future__ import annotations

import pandas as pd

from src.ansatz.benchmark import plot_convergence, run_benchmark, summarize


def test_benchmark_runs_and_tabulates() -> None:
    df = run_benchmark(layouts=("1x4",), layers_list=(1, 2), n_fields=3, steps=40,
                       seeds=(0, 1), n_jobs=1)
    assert len(df) == 1 * 2 * 3 * 2  # layouts * layers * fields * seeds
    assert {"num_spins", "n_layers", "seed", "h", "abs_energy_error", "mz_error"} <= set(df.columns)
    assert (df["abs_energy_error"] >= 0).all()


def test_summary_shape_bands_and_depth_helps() -> None:
    df = run_benchmark(layouts=("1x4",), layers_list=(1, 2), n_fields=3, steps=120,
                       seeds=(0, 1), n_jobs=1)
    s = summarize(df)
    assert len(s) == 2  # one row per (N, n_layers)
    assert {"mean_abs_E", "lo_abs_E", "hi_abs_E", "best_abs_E"} <= set(s.columns)
    # best-of-restarts never worse than the median restart; band brackets the median
    assert (s["best_abs_E"] <= s["mean_abs_E"] + 1e-12).all()
    assert (s["lo_abs_E"] <= s["mean_abs_E"] + 1e-12).all()
    by_depth = s.set_index("n_layers")["mean_abs_E"]
    assert by_depth[2] < by_depth[1]  # deeper ansatz fits better


def test_plot_written(tmp_path) -> None:
    df = run_benchmark(layouts=("1x4",), layers_list=(1, 2), n_fields=2, steps=20,
                       seeds=(0, 1), n_jobs=1)
    out = plot_convergence(summarize(df), out_path=tmp_path / "b.png")
    assert out.exists() and out.stat().st_size > 0
