# TFIM — Transverse-Field Ising Model with PennyLane

Course project (Quantum Computing) exploring the 1D/2D transverse-field Ising
model — exact diagonalization, entanglement/central-charge scaling, an
independent Jordan-Wigner cross-check, classical-shadow reconstruction, and
two VQE ansätze (hardware-efficient vs. a Hamiltonian Variational Ansatz) —
grounded in the official PennyLane [`qspin`](https://pennylane.ai/datasets/transverse-field-ising-model)
dataset.

Full write-up: [`report.md`](report.md). Slides + speaker notes:
[`presentation/`](presentation/).

## Hamiltonian

    H = J Σ_<i,j> σ_i^z σ_j^z + h Σ_i σ_i^x      (J = -1, ferromagnetic)

`<i,j>` runs over nearest-neighbour lattice bonds; `h` is the transverse
field. The order parameter is the longitudinal magnetization ⟨|M_z|⟩. The 1D
infinite chain has a quantum critical point at `h/|J| = 1`.

## Key results

- **Critical point, two independent exact routes** (Suzuki-Trotter mapping to
  the classical 2D Ising model; Jordan-Wigner free-fermion gap) agree on
  `g_c = 1`; the Jordan-Wigner closed form matches the dataset's exact
  diagonalization to 1e-13–1e-15 (`src/physics/jordan_wigner.py`).
- **Finite-size `h_c(N)`** from the order parameter/Binder cumulant converges
  toward `h_c=1` as `N` grows, faster on the closed (periodic) chain than the
  open one — an explicit finite-size boundary effect
  (`src/physics/boundary_comparison.py`, `src/physics/finite_size_scaling.py`).
- **Entanglement entropy** shows the area law away from criticality and the
  expected CFT log-scaling at the critical point; the naive Calabrese-Cardy
  central-charge fit is biased on the open chain (`c≈0.62`) by boundary
  operators, confirmed by refitting on the closed chain (`c≈0.51`, matching
  the Ising CFT value `1/2`) (`src/physics/entanglement.py`).
- **VQE ansatz comparison**: a physics-informed Hamiltonian Variational Ansatz
  with warm-starting beats a generic hardware-efficient ansatz by roughly
  23× median energy error at `N=8`, widening to ~85× at `N=16`
  (`src/ansatz/vqe_hva.py`, `src/ansatz/benchmark.py`).
- **Barren plateaus**: gradient variance for the hardware-efficient ansatz
  decays exponentially with `N`; the symmetry-respecting HVA/QAOA ansatz
  instead grows (`src/ansatz/trainability.py`).
- **Classical-shadow reconstruction** of `√⟨M_z²⟩` from the dataset's
  pre-simulated randomized measurements — the one NISQ-realistic,
  shot-noise-limited result in the project (`src/physics/classical_shadow.py`).

<p align="center">
  <img src="plots/order_parameter_chain_open.png" width="49%" alt="Order parameter vs field, three chain sizes">
  <img src="plots/vqe_benchmark.png" width="49%" alt="VQE ansatz benchmark: HEA vs HVA">
</p>

## Setup

```bash
python3.12 -m venv .venv
uv pip install -r <(echo "pennylane==0.45.0 aiohttp fsspec h5py")
.venv/bin/python -m pytest tests/ -q
```

The `qspin` dataset is downloaded on first use and cached under `data/`
(git-ignored). To regenerate every figure and CSV from scratch:

```bash
.venv/bin/python run_all.py
```

## Layout

- `src/` — reusable Python modules, split by role:
  - `core/` — dataset loader, shared plotting style, process-pool helper
  - `physics/` — order parameter, entanglement/central charge, finite-size
    scaling, boundary comparison, 2D lattices, Jordan-Wigner, classical shadows
  - `ansatz/` — VQE/QAOA ansätze, optimizer trajectories, trainability,
    benchmarks
- `tests/` — pytest suite mirroring `src/` (`core/`, `physics/`, `ansatz/`)
- `plots/` — generated figures (PNG), referenced by both the report and the
  slides
- `report.md` — full written report
- `presentation/` — slides (Typst) + speaker notes
- `run_all.py` — single entry point that reproduces every figure/CSV

See `CLAUDE.md` for full project history, physics background, and detailed
status notes.
