"""Process-level parallelism for the embarrassingly-parallel VQE grids.

The benchmark / ansatz-comparison / trainability sweeps are independent over
(system size, depth, field, random restart), so they map cleanly onto a process
pool. State-vector simulation of these small circuits is effectively
single-threaded, so one worker per core gives close to a linear speedup; each
worker is pinned to a single BLAS/OpenMP thread to avoid oversubscription.
"""
from __future__ import annotations

import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, Sequence, TypeVar

T = TypeVar("T")
R = TypeVar("R")

_THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS")


def _limit_threads() -> None:
    for var in _THREAD_VARS:
        os.environ[var] = "1"


def parallel_map(func: Callable[[T], R], items: Sequence[T], *,
                 n_jobs: int | None = None) -> list[R]:
    """Map `func` over `items` across processes, preserving order.

    Falls back to a serial map for a single item or `n_jobs <= 1`. `n_jobs`
    defaults to the CPU count. Uses the *spawn* start method: the state-vector
    simulator activates OpenMP threads in the parent, and forking a process that
    already has live OpenMP threads deadlocks — spawn starts clean children
    instead. Each worker is pinned to one BLAS/OpenMP thread so `n_jobs`
    processes do not oversubscribe the cores.
    """
    items = list(items)
    if n_jobs is None:
        n_jobs = os.cpu_count() or 1
    n_jobs = min(n_jobs, len(items)) if items else 1
    if n_jobs <= 1 or len(items) <= 1:
        return [func(x) for x in items]
    # Ensure spawned children inherit single-thread limits from the start.
    _limit_threads()
    ctx = mp.get_context("spawn")
    with ProcessPoolExecutor(max_workers=n_jobs, mp_context=ctx,
                             initializer=_limit_threads) as ex:
        return list(ex.map(func, items))
