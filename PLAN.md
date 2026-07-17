# Project Plan — TFIM with PennyLane

## Objective
Explore the transverse-field Ising model with PennyLane, using the official
`qspin` dataset as ground truth, and reproduce its physics both from exact data
and via a variational quantum eigensolver (VQE).

## Milestones
1. **Setup** ✅ — venv, PennyLane, dataset access, schema confirmed.
2. **Data layer** — `src/loader.py` wrapping `qml.data.load`; tests.
3. **Exact analysis** — order parameter $\langle|M_z|\rangle$ vs $h$, energy gap,
   correlations, directly from `ground_states`/`order_params`. Plots.
4. **VQE** — variational ansatz (e.g. hardware-efficient) to approximate ground
   states across the $h$ sweep; compare energies & order parameter to exact.
5. **Criticality** — finite-size analysis across `1x4/1x8/1x16` to locate the
   transition near $h/|J| = 1$.
6. **Report & slides** — write up in `report.md`, slides in `presentation/`.

## Open questions
- Which ansatz best captures the ordered–disordered transition at fixed depth?
- How do open vs closed boundary conditions shift finite-size critical estimates?

## Visualization & robustness pass (2026-06-22)

### Done
- **`src/plotting.py`** — shared style (`setup_style`), stable `N → color` map
  (`color_for_n`) so a given system size reads the same across every figure,
  and a `save_fig` helper (kills the scattered inline matplotlib config).
  `analysis.py` and `entanglement.py` now route through it.
- **Bug fix: entropy crossover.** `plot_entropy_vs_field` reported "N=16
  crossover h≈0.00": `argmin(np.gradient(S))` latched onto the h→0 cliff (at
  exactly h=0 the dataset returns a symmetry-broken product state, S=0, then S
  jumps to ln2). New `analysis.steepest_field(...)` windows the search to
  h ≥ 0.2; N=16 now reads h≈0.95. `estimate_critical_field` uses it too.
- **Binder cumulant** (`binder_cumulant`, `binder_crossing`, `plot_binder`):
  U₄ = 1 − ⟨M⁴⟩/3⟨M²⟩² from the exact ground-state moments. Curves cross at
  h≈0.84 (N=8/16) — a cleaner h_c estimate than the magnetization inflection.
- **Finite-size data collapse** (`plot_data_collapse`): N^{β/ν}⟨|M_z|⟩/N vs
  (h−h_c)N^{1/ν} with the exact 2D-Ising exponents (β/ν=1/8, ν=1) — curves
  collapse onto the universal scaling function.
- Tests for all of the above (`tests/test_analysis.py`); suite now 41 passing.

### Done (2026-07-16 deeper-analysis pass)
- **Central charge bias fixed.** Refit on the *closed* (periodic) chain, where
  the Calabrese-Cardy boundary-operator correction (arXiv:1002.4353) is
  absent: c≈0.513 (N=8), c≈0.506 (N=16) vs the open chain's 0.61/0.62 —
  confirms the bias was the boundary artifact, not the fit code.
  `entanglement.fit_central_charge(..., periodicity=...)`.
- **Classical-shadow reconstruction landed** (`src/classical_shadow.py`):
  √⟨M_z²⟩ from `shadow_basis`/`shadow_meas` via `qml.ClassicalShadow`, overlaid
  on the exact curve for N=4,8. ⟨|M_z|⟩ itself is nonlinear so not directly a
  shadow observable; √⟨M_z²⟩ coincides with it when |M_z| is two-valued.
- **`gradient_variance` now averages over every gradient component** (was: one
  fixed mid-circuit angle) — same qualitative conclusion (HEA decays with N,
  HVA/QAOA grow), now robust to which angle happens to sit at the probed index.
- **VQE optimizer-trajectory plot** (`src/optimizer_trajectory.py`,
  `optimizer_trajectories.png`): energy error vs Adam step, HEA vs HVA vs
  QAOA at one field — shows HEA plateauing early, not just where it ends up.
- **Jordan-Wigner cross-check** (`src/jordan_wigner.py`): closed-form
  free-fermion ground energy on the periodic chain, agreeing with the
  dataset's ED to 1e-13–1e-15 for N=4,8,16 — an analytic, not just numerical,
  confirmation.
- **Open vs closed boundary comparison** (`src/boundary_comparison.py`):
  closed-chain h_c estimate (0.93, 1.01, 1.01 for N=4,8,16) converges to the
  exact h_c=1 far faster than open (0.61, 0.78, 0.91) — periodic BC removes
  the two-end finite-size correction.
- **2D (rectangular) lattices** (`src/lattice_2d.py`): h_c grows with
  connectivity — 0.93 (2x2) → 1.31 (2x4) → 1.61 (2x8) → 1.88 (4x4) — trending
  toward the known square-lattice value h_c≈3.044. No central-charge fit
  attempted here (2D entanglement is an area law, not the 1D CFT log law).
- **Report Secs. 5–7 and Abstract filled in**, incorporating all of the above.

### Done (2026-07-16 code-quality pass)
- **Routed `vqe.py` / `benchmark.py` / `trainability.py` plots through
  `src/plotting.py`** (`setup_style`/`save_fig`/`color_for_n`, no more
  ad-hoc inline styling or manual `fig.savefig`/`plt.close`).
- **Fixed the HEA h=0 outlier** in `benchmark.compare_ansatze`: the dataset's
  h=0 point is a trivial symmetry-broken product state every ansatz gets for
  free (same artifact as `analysis.steepest_field`'s h→0 cliff), so it was
  excluded from the sweep. **This changed the headline number**: mean|ΔE|
  4.5e-1 (SEL) → 2.0e-2 (HVA), ~23× — not the old ~38× (which included the
  artificially-good h=0 point in the SEL average) — updated everywhere
  (report, slides, CLAUDE.md).
- **`vqe_error_profile.gradient_variance_vs_field`** was a stale duplicate of
  the *pre-fix* single-fixed-component gradient probe from `trainability.py`;
  refactored to call the already-fixed `trainability.gradient_variance`
  instead of re-implementing it, so both trainability results now agree.
- Removed 5 dead imports (`PLOTS_DIR` in analysis/entanglement/finite_size_scaling,
  `run_vqe_hva` in benchmark, `abs_mz_from_state` in vqe_hva) found via an
  AST-based unused-import scan.

### Still missing
- **Combined order-parameter + entropy figure** sharing the h-axis (M_z collapse
  and S peak at the same h is the whole story; currently two separate PNGs).
- **Closed-chain critical-field fit is a 3-point interpolation, not a
  statistically meaningful regression** — same caveat as the original
  open-chain fit; more system sizes would be needed for real error bars on ν.
- Reference baseline for more ideas: `../M4P/project/tfim_baseline`
  (Binder/collapse, free-fermion ED cross-check, DMRG, annealing dynamics).
