# TFIM — Transverse-Field Ising Model with PennyLane

Course project (Quantum Computing). Explore the 1D/2D transverse-field Ising
model using PennyLane, grounded in the official PennyLane `qspin` dataset.
**This file is the living source of truth — keep it updated as the project evolves.**

## Environment
- Python 3.12, virtualenv at `.venv/` (already created).
- **Install packages with `uv pip install ...`** (not plain `pip`).
- Run code with `.venv/bin/python`.
- Installed: `pennylane==0.45.0`, `aiohttp`, `fsspec`, `h5py`.

## The physics
Hamiltonian (dataset convention, ferromagnetic):

    H = J Σ_<i,j> σ_i^z σ_j^z + h Σ_i σ_i^x      with J = -1

- `<i,j>` runs over nearest-neighbour bonds on the lattice.
- `h` = external transverse field in the X direction (the tuning parameter).
- Order parameter: longitudinal magnetization  ⟨M_z⟩ = ⟨|Σ_i σ_i^z|⟩.
- Physics: at small `h` the ground state is ferromagnetically ordered
  (⟨M_z⟩ large); at large `h` it is paramagnetic (spins align with X, ⟨M_z⟩→0).
  The 1D infinite chain has a quantum critical point at h/|J| = 1.

## The dataset (`qspin` / Ising)
Load via:

```python
import pennylane as qml
ds = qml.data.load(
    "qspin",
    sysname="Ising",
    periodicity="open",      # or "closed"
    lattice="chain",         # or "rectangular"
    layout="1x4",            # see grid below
    folder_path="data",      # cache .h5 files under data/
)[0]
```

Available `(lattice, layout)` combos (both `open` and `closed` periodicity):
- `chain`: `1x4`, `1x8`, `1x16`
- `rectangular`: `2x2`, `2x4`, `2x8`, `4x4`

Each datapoint holds **100 values of `h` swept over [0.0, 3.0]**, with these attributes:
| attribute | meaning |
|---|---|
| `parameters` | dict, `parameters["h"]` = 100 field values in [0,3] |
| `hamiltonians` | list of 100 `qml.Hamiltonian`, one per `h` |
| `ground_energies` | ground-state energy per `h` |
| `ground_states` | exact ground statevector per `h` (dim 2^N) |
| `order_params` | ⟨|M_z|⟩ per `h` (the magnetization order parameter) |
| `num_phases` | number of phases in this system |
| `shadow_basis`, `shadow_meas` | classical-shadow measurement data |
| `spin_system` | metadata dict (name, ham_eq, order_params description) |

## Repo layout
- `data/`          — cached dataset `.h5` files (git-ignored; large)
- `src/`           — reusable Python modules, split by role: `core/` (loader,
  plotting, process-pool), `physics/` (order parameter, entanglement,
  finite-size scaling, boundary/lattice studies, Jordan-Wigner, classical
  shadows), `ansatz/` (VQE/QAOA ansätze, trainability, benchmarks)
- `notebooks/`     — exploratory Jupyter notebooks
- `tests/`         — pytest tests mirroring `src/`'s `core/`/`physics/`/`ansatz/`
- `plots/`         — generated figures
- `report.md`      — the written report (living document)
- `presentation/`  — slides
- `PLAN.md`, `TODO.md`, `CHANGELOG.md` — project tracking

## Conventions
- Type hints on all signatures; `pathlib` over `os.path`; `ruff` for lint/format.
- Tests alongside new code (`pytest`); mock only at system boundaries.
- Figures saved to `plots/` as PNG; reference them from `report.md`.

## Status / next steps
- [x] Environment + dataset access working.
- [x] Confirmed dataset schema (above).
- [x] `src/loader.py`: `load_ising(...)` → `IsingData` dataclass; tested (`tests/test_loader.py`, 8 passing).
- [x] `src/analysis.py`: order-parameter ⟨|M_z|⟩/N vs `h`, `estimate_critical_field`, plot → `plots/`; tested. Finite-size h_c: N=4→0.61, N=8→0.78, N=16→0.91 (→1 as expected).
- [x] `src/vqe.py`: StronglyEntanglingLayers ansatz + Adam; `run_vqe`, `sweep_vqe`, `plot_sweep`, and `abs_mz_from_state` (statevector order param, verified vs dataset). N=4 sweep mean |ΔE|≈4.6e-2 (3 layers, 200 steps). Tested.
- [x] Locate/estimate the critical point from finite-size data (order param + entropy crossover → h→1).
- [x] `src/entanglement.py`: half-chain von Neumann entropy via Schmidt/SVD, `entropy_vs_field` (shows area-law → criticality → product-state, with ln2 cat/SSB plateau in ordered phase), and `fit_central_charge` via Calabrese-Cardy, now parametrized by `periodicity`. **Open chain: c≈0.61-0.62 (N=8,16) vs CFT c=1/2 — a boundary-operator artifact (arXiv:1002.4353); refit on the closed chain gives c≈0.51 (N=8,16), confirming the fix.** Tested.
- [x] `src/vqe_hva.py`: improved VQE — Hamiltonian Variational Ansatz (auto-extracts ZZ bonds + field wires from the dataset Hamiltonian), correct `|->^N` reference state (h→∞ ground state), and `warm_start_sweep`/`warm_start_core` (carry params high-h→low-h). **Multi-restart medians (2026-07-17): N=8 median|ΔE| 2.8e-1 (SEL) → 1.2e-2 (HVA L=10 warm-start), ~23× (best-of-restarts HVA 1.8e-3); gap widens to ~85× at N=16 (HEA median 1.8e1 vs HVA 2.1e-1).** h=0 excluded from the sweep (trivial symmetry-broken product state). Residual error sits in deep ordered phase (h→0 needs GHZ depth ~N/2). Tested.
  - Perf (2026-07-17): `run_adam` shared loop with convergence-based early stopping (tol/patience, replaces fixed step count); `c_dtype` param → drivers use complex64 (~1.4× at N=16; sparse-H tried and dropped, slower than lightning's Pauli-sum expval); `src/parallel.py` process-pool (spawn, one BLAS thread/worker) parallelizes the benchmark/ansatz grids. No lightning.gpu: at N≤16 the statevector is too small for GPU to beat CPU.
  - Gotcha: ground state at h→∞ is `|->^N` not `|+>^N` (field term is +hΣX). Bond/field extraction matches on class names `PauliZ`/`PauliX`.
  - QAOA: `run_qaoa` / `anneal_init` add annealing-inspired init (γ_k=s_k·dt, β_k=(1-s_k)·dt, s_k=(k+0.5)/p) to the same HVA circuit — digitized quantum annealing. `init_strategy` ("random"|"anneal") threads through `run_vqe_hva` and `warm_start_sweep`.
- [x] `src/trainability.py`: barren-plateau study — `gradient_variance` (Var averaged over every non-trivial gradient component, over random inits) + `plot_barren_plateaus`. HEA decays with N (0.298→0.034→6.9e-4 for N=4,8,16); HVA/QAOA *grow* (5.0→24.8→147.3). Gotcha: exclude index 0 **only for HEA** (its leading RZ on |0> = global phase, gradient ≡ 0); the HVA's index-0 is a real ZZ angle (its *largest* gradient component) and must be kept — masking it for HVA was a bug (fixed 2026-07-16).
- [x] `src/optimizer_trajectory.py`: energy-error-vs-Adam-step for HEA/HVA/QAOA at one field, `plots/optimizer_trajectories.png` — shows HEA plateauing early, the endpoint comparison alone understates this.
- [x] `src/vqe_error_profile.py`: ΔE(h) + gradient-variance-vs-h for HEA/HVA at N=8, `plots/vqe_error_trainability_1x8.png`. **Nuances the headline median: at h=0 HEA is better by orders of magnitude (~1e-6 vs HVA's ~0.9 — exact product state); the curves cross at h≈0.4 and HVA then wins by up to 1e4.** HVA's worst point is the deep ordered phase (warm start is exact at h→∞; GHZ cat needs depth ~N/2). Gradient variance: HVA above HEA at *every* field, and mid-sweep values reproduce `trainability.py`'s N=8 row from a different code path.
- [x] `src/finite_size_scaling.py`: h_c(N) extrapolation + central-charge-vs-N, `plots/finite_size_hc_chain_open.png`, `plots/central_charge_scaling_chain_open.png`. **Negative result, deliberately kept:** a *free* 3-point fit of h_c(N)=h_c(∞)−a·N^(−1/ν) gives h_c(∞)=1.34 (inflection) / 2.00 (Binder — hits its fit bound), ν=2.58/8.57 vs exact ν=1, and `curve_fit` can't estimate a covariance (3 points, 3 params). This is *why* the report/deck fix ν=1 and never quote an extrapolated h_c(∞). Central charge drifts 0.588→0.608→0.622 with N (*away* from ½) — the open-chain boundary bias, which is what flagged it as physics not a bug.
- [x] `src/jordan_wigner.py`: closed-form free-fermion ground energy on the periodic chain, `ground_energy_analytic`/`gap_analytic`. Matches the dataset's ED to 1e-13–1e-15 for N=4,8,16 (`plots/jordan_wigner_cross_check.png`) — an independent analytic check, not a second numerical method.
- [x] `src/boundary_comparison.py`: closed-chain h_c (0.93, 1.01, 1.01 for N=4,8,16) converges to the exact h_c=1 far faster than open (0.61, 0.78, 0.91) — periodic BC removes the open chain's two-end finite-size correction (`plots/boundary_comparison_hc.png`).
- [x] `src/lattice_2d.py`: rectangular layouts (2x2/2x4/2x8/4x4), previously untouched. h_c grows with connectivity: 0.93→1.31→1.61→1.88, trending toward the known square-lattice h_c≈3.044. No central-charge fit here (2D entanglement follows a boundary-area law, not the 1D CFT log law).
- [x] `src/classical_shadow.py`: reconstructs √⟨M_z²⟩ from `shadow_basis`/`shadow_meas` via `qml.ClassicalShadow.expval` — the one NISQ-realistic (shot-noise) result in the report; ⟨|M_z|⟩ itself is nonlinear so not a direct shadow observable, but √⟨M_z²⟩ coincides with it when the ground state's magnetization is sharply two-valued.
- [x] `report.md` Secs. 5–7 and Abstract filled in, incorporating all of the above.
- Field range is layout-dependent: 1x4→[0,3], 1x8→[0,3.5], 1x16→[0,3.75]; always 100 points, always straddles h=1.
- Reference project for more ideas: `../../M4P/project/tfim_baseline` (exact ED/Jordan-Wigner/Onsager, QAOA, annealing, DMRG, Hopfield, barren plateaus) — Jordan-Wigner cross-check now landed; DMRG/Hopfield/annealing-dynamics still untouched.
