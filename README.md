# TFIM — Transverse-Field Ising Model with PennyLane

Course project (Quantum Computing) exploring the 1D/2D transverse-field Ising
model — exact diagonalization, entanglement/central-charge scaling, an
independent Jordan-Wigner cross-check, classical-shadow reconstruction, and
two VQE ansätze (hardware-efficient vs. a Hamiltonian Variational Ansatz) —
grounded in the official PennyLane [`qspin`](https://pennylane.ai/datasets/transverse-field-ising-model)
dataset.

## Hamiltonian

    H = J Σ_<i,j> σ_i^z σ_j^z + h Σ_i σ_i^x      (J = -1, ferromagnetic)

`<i,j>` runs over nearest-neighbour lattice bonds; `h` is the transverse
field. The order parameter is the longitudinal magnetization ⟨|M_z|⟩. The 1D
infinite chain has a quantum critical point at `h/|J| = 1`.

## Setup

```bash
python3.12 -m venv .venv
uv pip install -r <(echo "pennylane==0.45.0 aiohttp fsspec h5py")
.venv/bin/python -m pytest tests/ -q
```

The `qspin` dataset is downloaded on first use and cached under `data/`
(git-ignored).

## Layout

- `src/` — reusable modules: dataset loader, VQE/QAOA ansätze, entanglement
  and central-charge analysis, finite-size scaling, classical shadows,
  Jordan-Wigner cross-check, barren-plateau trainability study
- `tests/` — pytest suite mirroring `src/` (one test module per source module)
- `plots/` — generated figures (PNG), referenced by both the report and the
  slides
- `report/report.md` — full written report
- `presentation/` — slides (Typst) + speaker notes

See `CLAUDE.md` for full project history, physics background, and detailed
status notes.
