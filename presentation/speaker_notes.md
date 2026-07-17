# Speaker Notes — Quantum Phase Transitions of the Transverse-Field Ising Model

*Lorenzo Liuzzo*

---

## Phase transitions and the classical Ising model

Let's start with the classical picture everyone already knows, because the quantum story is going to be the same question asked a different way. A phase transition is formally a non-analyticity of a thermodynamic potential — Ehrenfest's classification just asks which derivative of the free energy first jumps or diverges: a discontinuity in the first derivative is first-order, like ice melting; a divergence in the second derivative is continuous, like the Curie point. For a symmetry-breaking transition specifically, we track an order parameter that's identically zero in the disordered phase and becomes nonzero — and non-unique — once the symmetry breaks.

Grounding this in a concrete model: the classical Ising Hamiltonian is H = -J times the sum over nearest-neighbor pairs of σ_i σ_j, each spin σ_i = ±1. It's invariant under flipping every spin at once — a global Z₂ symmetry — and the order parameter is the magnetization m, which the system spontaneously breaks below T_C by picking one of the two symmetry-related ground states.

The reason for this table is the 1D versus 2D contrast, the classical precursor to the quantum story. In 1D, a domain wall costs a fixed energy 2J but the entropy of where to place it grows like k_B T ln N, so ΔF = 2J - k_B T ln N is negative for any T>0 as N grows — thermal fluctuations always win, no finite-temperature transition, no matter how you tune the coupling. In 2D, Onsager showed in 1944 the transition survives, because the domain wall's boundary is itself extensive, enough room to pay the entropy cost. Mean-field theory gets the 1D chain qualitatively wrong — it predicts a transition where there isn't one — which sets up the question of what quantum fluctuations, instead of thermal ones, can do that mean-field also can't capture.

---

## The transverse-field Ising model

Here's the conceptual jump, and the model we'll actually work with. A quantum phase transition happens at exactly T=0, driven not by thermal fluctuations but by quantum ones, and the signature is the same kind of non-analyticity as before, except now it's the ground-state energy that's non-analytic in some coupling g, not the free energy in temperature. We get quantum fluctuations in by promoting the classical spins to Pauli operators and adding a transverse field term proportional to σˣ; since σˣ doesn't commute with σᶻ, this genuinely drives quantum dynamics — tunnelling between the classical spin configurations — not just a relabeling.

That gives the actual model on the slide: H = J times the sum of ZZ couplings over nearest-neighbor bonds, plus h times the sum of X on every site, J=-1 by convention. I've defined the order parameter here too, the expectation of |M_z|, which we track throughout. The reason to write down the two solvable limits in the table before doing anything numerical is that they're qualitatively different, and that alone forces a transition somewhere in between. When g = h/|J| ≫ 1 the field term dominates and the ground state is the uncorrelated product state |−⟩ on every site — the σˣ = −1 eigenstate, since the field term enters with a plus sign in this convention; the same minus state the HVA uses later as its reference — a trivial paramagnet. When g ≪ 1 the coupling term dominates and you get the two classical ferromagnetic ground states back, all up or all down along z. You can't smoothly deform an uncorrelated product state into a two-fold-degenerate symmetry-broken one without something singular happening in between.

One subtlety on the last bullet: on any finite lattice, what would be a level crossing is smoothed into an avoided crossing, so the ground-state energy is perfectly smooth at finite N; it only sharpens into a true non-analyticity in the thermodynamic limit, N→∞ — which is exactly why finite-size scaling later matters. For the 1D infinite chain that critical point sits at exactly g_c=1, and the rest of the talk pins that number down three independent ways and then reproduces it on a quantum computer.

---

## Two exact routes to g_c = 1

*g_c=1 isn't a numerical fit — it's derived exactly, by two independent routes with zero shared machinery. Suzuki-Trotter gives the non-analyticity of the free energy (**sufficient** for a QPT); Jordan-Wigner gives a vanishing gap (**necessary**). Same answer. Full derivations are in backup.*

**Route one — Suzuki-Trotter.** Slice the partition function Z = Tr(e^{-βH}) into M imaginary-time steps; each slice becomes an extra classical Ising layer, so you land on the partition function of a classical 2D anisotropic Ising model, N sites by M time-slices — imaginary time literally becomes the second spatial dimension. Onsager already solved that model's exact critical point in 1944; substitute the mapped anisotropy back in, take M to infinity — same as T to zero on the quantum side — and you get g_c = 1, for every value of J. No series expansion, no fit. *(Full mapping: backup.)*

**Route two — Jordan-Wigner.** Map spin up/down onto an occupied or empty fermionic orbital, σ_j^z = 2n_j - 1. The naive site-local version is broken, because spins on different sites commute but fermions anticommute — fixed by attaching a nonlocal string operator to each site, the Jordan-Wigner string.

After the transform, the Hamiltonian is quadratic in these fermions — hopping and pairing terms only, no quartic interactions — diagonalizable by a Fourier transform followed by a Bogoliubov rotation, no exponential cost at all. The gap is the dispersion's minimum over k, and it vanishes exactly at k=0, g=1 — the same critical point, zero shared machinery with the Suzuki-Trotter argument. This closed form is literally what src/physics/jordan_wigner.py evaluates, and we'll see it match exact diagonalization to floating-point precision in the results section.

---

## Entanglement entropy and the area law

Everything so far has found the transition from the *symmetry-breaking* side — an order parameter that switches on. Entanglement entropy is a deliberately different lens, and it earns its place for two reasons. First, it locates the transition using no order parameter at all, purely from how correlations are structured, so it's genuinely independent evidence for the same point. Second, and this is the real payoff, it does something the order parameter simply can't: it tells us *which universality class* the transition belongs to, not just where it sits. That's the upgrade from "there's a critical point at g=1" to "it's an Ising-CFT critical point."

Mechanically: for a bipartite pure state, the Schmidt decomposition gives a reduced density matrix ρ_A on one half, and the entanglement entropy is its von Neumann entropy, S = -Tr(ρ_A ln ρ_A) — literally a measure of how entangled the two halves are. What matters is how S *scales* with block size, because that scaling is a fingerprint of the correlation structure. Away from criticality the ground state is gapped, correlations decay over a finite length ξ, and only the region within ξ of the cut contributes — so S saturates and scales with the *boundary* of the region, not its volume. That's the area law.

Right at criticality ξ diverges, correlations become scale-free, and the area law breaks: S instead grows logarithmically with block size. This is the quantum analog of the diverging susceptibility at a classical critical point. And the coefficient of that logarithm isn't arbitrary — Calabrese-Cardy tie it to a single number, the central charge c of the underlying conformal field theory. For the Ising universality class, c = 1/2 exactly. So the *slope* of S versus log-block-size is the universality-class fingerprint we extract two slides from now.

One more closed-form anchor, and it ties entropy back to the symmetry-breaking picture: exactly at g=0, the TFIM entropy predicts S goes to ln 2 — the cat-state degeneracy from the classical Ising slide, now restated as an entanglement statement. The ordered ground state is an equal superposition of the two symmetry-broken branches, so tracing out half the system leaves exactly one bit. Entropy sees the ordered phase too — from the entanglement side rather than the magnetization side.

---

## The dataset: qspin / Ising

Before the results, I want to be upfront about where the ground truth comes from. Everything is loaded from PennyLane's qspin dataset via a single call: qml.data.load with sysname Ising, plus periodicity, lattice, and layout as the specifying arguments — a system is fully determined by those four discrete choices. Periodicity is open, two free ends, or closed, a ring. Lattice is chain, 1D, or rectangular, 2D. Layout is the actual size, rows by columns — chains use 1x4, 1x8, 1x16; rectangular goes from 2x2 up through 4x4.

N, the total spin count, is rows times columns, ranging over 4, 8, 16, and every combination of periodicity, lattice and layout gives 2 times (3+4), fourteen distinct systems total. For every one, the dataset sweeps 100 values of h over a range that always straddles h=1, giving dense coverage right where the physics happens.

Worth being precise that each system isn't one Hamiltonian, it's a sweep of 100 field values, and every attribute in this table is an array of length 100, indexed by that sweep. hamiltonians is 100 full PennyLane Hamiltonian objects, H(h) for each field — our code reads these directly, term by term, rather than hard-coding the lattice geometry; src/ansatz/vqe_hva.py literally extracts the ZZ bonds and X field sites from whatever Hamiltonian object it's handed.

ground_energies is the exact ground energy E_0(h) at each field, from exact diagonalization. ground_states is the full 2^N-dimensional statevector at each field. order_params is the expectation of |M_z| at each field, precomputed for us. shadow_basis and shadow_meas are the classical-shadow data: 1000 randomized single-qubit Pauli measurement bases and outcomes per field — exactly what a real NISQ device would hand you, no statevector involved, used in the backup section.

---

## The code: one module per physics question

Every number in this talk comes out of this pipeline, so it's worth thirty seconds. The cached qspin HDF5 goes through `loader.load_ising`, which returns a typed `IsingData` dataclass — one per (lattice, periodicity, layout). Each physics question is then exactly one module in `src/`: it takes `IsingData` in and writes one PNG to `plots/` out, through shared plotting helpers so every figure has the same style and the same N→colour map. Both `report.md` and these slides embed those same PNGs by relative path. That's the important part: **no number in either output is re-typed by hand** — everything is re-read from the code's own printed output, so a stale number can't silently survive a code change.

The scale: sixteen modules, ~2 151 lines, backed by 621 lines of tests — 63 of them, all passing, one test module per physics module. `pytest` gates every module before its plot is trusted.

The design point I'd most defend is the second bullet: `extract_structure` inspects the dataset's own `qml.Hamiltonian` object term by term — `PauliZ⊗PauliZ` factors become bonds, lone `PauliX` factors become field wires. There is **no hardcoded lattice geometry anywhere**. That's why the identical VQE code is correct on the open chain, the closed ring, and the 2D rectangular lattices, without a single branch on system type — the circuit is built from whatever bonds are actually present in the Hamiltonian it's handed.

If asked what this bought us concretely: the pipeline is exactly what caught a stale duplicate and five dead imports, and excluding a trivial h=0 point moved a headline number from ~38× to ~23× — which then held up under a later multi-restart rerun as a proper median rather than a single-seed fluke. Backup has the full module map.

---

# Exact results

---

## Order parameter and the Binder cumulant

On the left is the headline picture: the order parameter, |M_z| over N, against h, for a few sizes — collapsing from near 1 in the ordered phase down toward 0 in the paramagnetic phase, sharpening as N grows, exactly the finite-size behavior expected approaching a true non-analyticity.

On the right is the Binder cumulant, U_4, defined below — a specific combination of moments engineered so finite-size shape effects cancel out, which is why curves for different N cross almost exactly at a single point instead of gradually sliding past each other. That crossing gives h_c ≈ 0.84 in the cumulant's own units.

Flag if it comes up: 0.84 isn't directly comparable to the textbook universal Binder ratio for isotropic 2D classical Ising, about 0.61, because the quantum-classical mapping produces an anisotropic classical system — N spatial sites by M imaginary-time slices, not a square lattice — and the universal ratio depends on that aspect ratio and boundary conditions. What's universal, and what we actually use, is that the curves cross at all, at a single h — that crossing location, not its height, is our h_c estimate, and it's cleaner than reading the inflection point by eye.

---

## Entanglement entropy and the central charge

This is the previous theory slide's prediction turned into an observation, and reading the curve left-to-right in the field h gives all three regimes at once. Deep in the paramagnetic phase, away from the transition, S is modest and stays roughly flat with N — the area law, correlations short-ranged. As h approaches the transition, S rises and *peaks*: this is ξ diverging, correlations going long-range — and the peak location is itself an independent estimate of g_c, the same "entropy crossover" I use as a cross-check against the order-parameter inflection a couple of slides on. Deep in the ordered phase it plateaus at ln 2: the cat-state degeneracy again — the exact ground state there is a symmetric superposition of the two ferromagnetic branches, and tracing out half the system leaves exactly one bit of entanglement.

So the takeaway is that this single curve carries three things: the area law, a third independent locator of the critical point, and the signature of the ordered phase's cat-state structure.

I want to flag proactively: there's a shaded band near h=0 where entropy wobbles noticeably. That's not noise in the pipeline — the two symmetry-broken branches near h=0 have an exponentially-small-in-N tunnelling splitting between them, so the exact-diagonalization solver has no principled reason to return the same near-degenerate eigenvector at adjacent field values; it can flip between the symmetric and antisymmetric combination essentially at random. The order parameter doesn't care which combination comes back, since |M_z| is the same either way, which is why that curve stays smooth even though entropy wobbles. We flagged this automatically in the pipeline rather than smoothing it away.

Central charge is the universal fingerprint of the critical point's underlying field theory — for the Ising universality class, CFT predicts c = 1/2 exactly. We extract it by fitting the block-entropy scaling to the Calabrese-Cardy formula below, the two-parameter fit used throughout.

On the open chain at N=16, we get c ≈ 0.62, visibly off from 1/2. That's not a bug: it's a known finite-size boundary-operator artifact, documented in Calabrese and Cardy's follow-up work, arXiv 1002.4353 — irrelevant operators localized at the two open ends add subleading corrections the naive two-parameter fit doesn't account for, biasing the extracted c.

Refit the identical procedure, same formula, same code, on the periodic chain instead — no boundary at all — and the bias goes away: c ≈ 0.51, right on the Ising value. That agreement, appearing only once we remove the boundary, is itself evidence we correctly diagnosed the bias rather than curve-fitting our way to a number we wanted.

---

## Locating g_c: finite size and boundaries

Here's the finite-size h_c estimate from the steepest-descent point of the order parameter, at three sizes, for both boundary conditions. Open chain: 0.61, 0.78, 0.91 at N=4, 8, 16 — drifting toward the thermodynamic value of 1 as N grows, exactly as expected, since finite systems round off the transition and pull the apparent critical point inward. As a cross-check, the steepest-descent of the order parameter and the crossover point of the entanglement entropy agree at each N — reassuring, since they come from completely different quantities.

Now the boundary comparison, in the same table. Periodic boundaries have no chain ends at all, so there's no boundary-driven finite-size correction to fight, and the closed chain converges to 1 much faster — already 1.01 by N=8, where the open chain is still at 0.78. Quantitatively that's the finite-size scaling ansatz on the slide: the open chain simply has a much larger prefactor a, because of the extra boundary operators. Note this is the same boundary physics that biased the central charge two slides ago — one cause, two symptoms.

Honest caveat: only three system sizes, so what I'm calling an extrapolation is really an exact interpolation through three points, not an error-barred fit — I wouldn't overstate the precision of that h_c(infinity) intercept.

If asked about data collapse: it's in backup — rescaling the order parameter by N^(β/ν) collapses curves for different N onto one universal curve, which fixes location and universality class at once, without needing the central charge.

---

## Independent check: Jordan-Wigner

This is the payoff of the free-fermion derivation from the theory section. The closed-form Jordan-Wigner ground energy, E_0 = -sum over positive-k modes of ε(k), filling every negative-energy mode of the Bogoliubov spectrum, is evaluated directly and compared against the dataset's exact diagonalization energies: they agree to somewhere between 1e-13 and 1e-15 for N=4, 8, and 16.

That's floating-point precision, not numerical-method precision — there's no exact diagonalization anywhere in this calculation, just a closed-form expression evaluated directly. Since this derivation shares zero code with the exact-diagonalization pipeline the rest of the results rely on, this agreement is about as strong a cross-check as we could ask for.

---

# Variational quantum eigensolver

---

## VQE: the variational principle and two ansätze

Switching to the quantum-computing side. The variational theorem is the whole justification for VQE: for any trial state, E(θ), the expectation of H in that state, is guaranteed greater than or equal to the true ground energy E_0. So minimizing E(θ) over θ can only approach E_0 from above, never overshoot below, for any parametrized family of trial states.

Concretely, U(θ) is a parametrized quantum circuit acting on a fixed reference state. The hybrid loop: a quantum device, or simulator here, evaluates E(θ) and its gradient — we use the adjoint method, exact and efficient in simulation — and a classical optimizer, Adam, updates θ.

One thing to flag before the next slide: convergence of Adam only certifies a local optimum of whatever ansatz you chose — not E_0 itself. There's an irreducible expressibility floor, E at the optimal θ minus E_0, unless the true ground state lies exactly within the reachable manifold of your circuit. That's the real design question, and exactly what the next two slides' comparison measures: expressive enough to reach the ground state, structured enough to stay trainable.

Two circuits sitting at opposite ends of the expressiveness-trainability trade-off. HEA is PennyLane's built-in StronglyEntanglingLayers: generic single-qubit rotations plus a fixed pattern of entangling CNOTs, knows nothing about the Hamiltonian it's preparing a ground state for. HVA, the Hamiltonian variational ansatz, goes the other way: p layers, each alternating a product of e^{-i γ Z_i Z_j} over every bond and e^{-i β X_i} over every site — two parameters per layer, regardless of system size.

This is motivated by Trotterizing real-time evolution under H itself, or equivalently digitizing an adiabatic path in g — alternating the two non-commuting pieces of H as unitaries. The reference state, the all-minus product state, is exact at g to infinity, since the field term is +h sum of X, minimized by the -1 eigenstate of X on every site — so HVA starts exactly at the easy end of the sweep, where the exact answer is already known in closed form.

On top of that, a warm start: sweep h from high to low, initializing each field's optimization from the previous field's optimized parameters, transporting the easy solution progressively into the harder, more entangled regime instead of starting randomly at every field.

---

## QAOA as digitized quantum annealing

QAOA reuses the literal same HVA circuit, but reinterprets it and initializes it differently. The physical picture is an adiabatic path from an easy Hamiltonian H_B to the target H_C: H(s) = (1-s)H_B + s H_C, sweeping s from 0 to 1 slowly — the adiabatic theorem guarantees the ground state is tracked throughout, provided s varies slowly relative to the instantaneous gap.

One Trotter step of that sweep is exactly one HVA layer: H_B is the sum of X, the mixer, H_C is the ZZ coupling — same (γ,β) circuit, reinterpreted as digitized annealing rather than a generic variational ansatz. The annealing-inspired init seeds layer l at s_l=(l+1/2)/p, with γ_l = s_l·δt and β_l=(1-s_l)·δt — placing the optimizer directly in the basin a slow physical anneal would follow, instead of random angles.

As p goes to infinity with a slow enough schedule, this reproduces exact adiabatic evolution; at finite p, the residual energy error directly measures the cost of digitizing that continuous sweep into discrete Trotter steps.

Worth flagging forward: because QAOA is the *same circuit* as HVA, it inherits HVA's trainability wholesale — which is why the barren-plateau table two slides on reports a single shared HVA/QAOA column rather than three separate ansätze.

*(src/ansatz/vqe_hva.py)*

---

## VQE: hardware-efficient vs physics-informed — results

Here's the head-to-head, and every curve is a median over four independent random restarts with the shaded inter-quartile band showing the restart-to-restart spread — a single seed is an anecdote, VQE outcomes swing with the initialization. At N=8, median absolute error over the field sweep is 2.8e-1 for HEA and 1.2e-2 for HVA — about 23 times better, or 1.8e-3 if you take the best of the four restarts.

The right panel is the same comparison at N=16, and the gap widens to about 85 times: HEA has essentially stopped learning — its error is order ten — while HVA is still near 0.2. That widening is the whole point: it's not that HEA is a constant factor worse, it degrades as the system grows.

Reproducibility note if asked: these numbers come from convergence-based training rather than a fixed step budget, and the whole grid runs in parallel across cores in single precision — an earlier fixed-budget, single-seed version reported this as a fragile ~23x that has now firmed up with proper restart statistics.

---

## Trainability: barren plateaus and depth

Accuracy alone doesn't tell you whether an ansatz is trainable at scale, so here's the other half of the VQE story. The diagnostic is defined below: the variance, over random parameter initializations, of the energy gradient with respect to each parameter component, averaged over components, at fixed circuit depth. If that variance shrinks exponentially with N, almost every random starting point sits on a flat plain with essentially no gradient signal to descend — a barren plateau, and no optimizer, however good, can climb out.

The table shows exactly this divergence: HEA's variance drops from 0.298 at N=4 to 6.9e-4 at N=16 — collapsing fast. HVA and QAOA's variance instead grows, from 5.0 up to 147.3 over the same range. So HVA isn't just more accurate, it stays trainable as the system gets bigger, while HEA is heading toward untrainability.

If pushed on whether this is a proof or an empirical trend: with only N up to 16, this alone can't distinguish "provably plateau-free" from "plateaus onset later than HEA's" — but there's theoretical backing, the dynamical-Lie-algebra argument from Larocca and collaborators: HVA's generators, the Z₂-symmetric ZZ bonds and X field terms, span only a polynomially-sized dynamical Lie algebra under the Hamiltonian's own symmetry, unlike HEA's unstructured generators, which span the full exponentially-large unitary algebra. A polynomial-dimension DLA is what guarantees polynomially, rather than exponentially, vanishing gradients at any N — the real reason the Z₂-respecting, physically-motivated structure of HVA keeps it trainable.

This is the hardware-efficient ansatz on its own, swept over circuit depth at each system size, with restart bands — deliberately HEA-only, because the point is what happens to the generic ansatz as you give it more layers. Two things to read off. First, the naive intuition — more layers, more expressibility, lower error — only holds at the smallest size: N=4 keeps improving through depth 4. Second, and this is the striking part, at N=16 the error actually grows with depth, from about 4 up to 14 — adding parameters makes it strictly worse.

That's the operational face of the barren plateau: a deeper generic circuit has an exponentially flatter landscape, so with a fixed optimizer it trains worse, not better. Crucially this is now a fair test — convergence-based stopping means depth isn't being confounded with an under-spent step budget, and the bands are over four random restarts — so the upward trend is real, not an artifact. It's the mirror image of the previous slides: the structured HVA got better with size, the generic HEA gets worse.

---

## Summary and next steps

To pull it together: we reproduced the TFIM phase transition three independent ways — from the exact ground states via order parameter and Binder cumulant, from the completely independent analytic Jordan-Wigner solution, and from VQE — and all three agree on g_c=1. The physics-informed ansatz, HVA, beats generic HEA on both accuracy and trainability, and that advantage traces directly back to respecting the model's own Z₂ symmetry.

Periodic boundaries resolved two separate open-chain artifacts at once — the central-charge bias and the slow convergence of the finite-size h_c estimate — a nice unification, since a priori those looked like two unrelated issues.

Beyond the original scope, covered in backup if there's time, we extended to 2D lattices, where h_c grows with lattice connectivity, and to classical-shadow reconstruction, the one genuinely NISQ-realistic result in the project. What's still open: a combined order-parameter-plus-entropy figure we haven't built yet, and proper error bars on the finite-size fits, since we only have three system sizes to work with.

---

# Backup slides

---

## Backup: Suzuki-Trotter, the mapping in full

*Route one of the main deck, carried through explicitly.*

This is the strongest statement in the whole talk, so let me walk through it carefully: g_c=1 isn't a numerical fit, it's derived exactly. The trick is Suzuki-Trotter: slice the partition function Z = Tr(e^{-βH}) into M imaginary-time steps, and each slice becomes an extra classical Ising layer, so you end up with the partition function of a classical 2D anisotropic Ising model on an N-sites-by-M-time-slices lattice. The quantum coupling g maps onto a classical anisotropy γ via this tanh formula and imaginary time literally becomes the second spatial dimension of that classical model.

Onsager already solved the exact critical point of the anisotropic 2D classical Ising model in 1944: sinh(2β J_x^c) sinh(2β J_y^c) = 1. Substitute the mapped anisotropy back in, take M to infinity — same as T to zero on the quantum side — and you get g^c = 1, for every value of J. No series expansion, no fit: this is genuinely where h_c=1 comes from.

I'll flag this isn't redundant with the free-fermion derivation next: this one gives the actual non-analyticity of the free energy, the sufficient condition for a phase transition; Jordan-Wigner gives a vanishing gap, a necessary condition. Two different pieces of evidence for the same point.

---

## Backup: data collapse

Rescale the order parameter by N^(β/ν) and the field axis by N^(1/ν): if curves for different N fall onto a single universal curve, that independently confirms both the critical point location and the universality class — with no central charge needed. It collapses *only* for the correct h_c **and** the correct exponents simultaneously, which is what makes it a sharp test rather than a fit. The exponents β=1/8, ν=1 are the 2D classical Ising exponents — 2D because of the imaginary-time dimension of the Suzuki-Trotter mapping.

---

## Backup: why we don't quote an h_c(∞)

This anticipates the obvious question after the finite-size slide: you have h_c at three sizes drifting toward 1 — why not just fit the scaling ansatz, extrapolate to N=∞, and quote that number? Because we tried, and it doesn't work, and I'd rather show you that than quietly omit it.

**Left panel.** Fit h_c(N) = h_c(∞) − a·N^(−1/ν) to the three open-chain points with h_c(∞) and ν both free. The inflection-point data extrapolates to **1.34**; the Binder-crossing data extrapolates to **2.00** — which is its fit bound, so the optimizer ran to the edge of the allowed range. The fitted exponents come out at ν = 2.58 and 8.57, against the exact ν = 1. So a free three-parameter fit through three points recovers neither the right critical field nor the right exponent — and scipy's `curve_fit` can't even estimate a covariance, which is the fit telling you it has zero degrees of freedom left. Three points, three parameters. That's not a measurement, it's interpolation wearing a lab coat.

This is exactly why the main deck states the finite-size scaling ansatz with ν fixed at 1 and quotes only the measured h_c(N) values, never an extrapolated intercept. The honest claim is the one we make: h_c(N) drifts toward 1, and periodic boundaries get there faster. The dishonest version — "we extrapolate h_c(∞) = 1.00 ± 0.02" — would need more system sizes than the dataset ships, which is the N=16 ceiling from the other backup slide.

**Right panel.** Same story for the central charge: c drifts 0.588, 0.608, 0.622 across N=4,8,16 — moving *away* from the CFT value of 1/2, not toward it, because of the open-chain boundary bias. That divergence-with-N is what made us suspect a boundary artifact rather than a numerical error in the first place, and refitting on the closed chain confirmed it.

*(src/physics/finite_size_scaling.py)*

---

## Backup: where HVA's advantage actually lives

This anticipates the sharpest challenge to the headline number. The main deck says HVA beats HEA by ~23× at N=8 as a *median* over the field sweep. A median hides structure, so here is the error resolved field by field — and the structure is the opposite of uniform.

**Top panel.** At h=0, HEA is not merely competitive, it is *better* by orders of magnitude — error around 1e-6, essentially exact — while HVA sits near 0.9, its worst point anywhere. The two cross around h≈0.4, and past that HVA wins by one to four orders of magnitude for the rest of the sweep. So the 23× is real, but it is an average over a regime where HVA dominates plus a corner where it loses.

Both facts have the same explanation, and it's the reference state. At h=0 the exact ground state is a classical product state, which a generic circuit nails trivially — and this is precisely why we exclude h=0 from the reported sweep, since it's a trivial symmetry-broken product state rather than a meaningful test. HVA is worst there because its warm start comes from the opposite end: |−⟩^⊗N is exact at h→∞, so the sweep transports that solution downward and accumulates the most error at the far end, deep in the ordered phase, where preparing a GHZ-like cat state needs circuit depth ~N/2 that a fixed p simply doesn't have. HVA's advantage is real and it grows with N, but it lives *at and above* criticality — not at h=0.

**Bottom panel.** Gradient variance against field for both, at N=8. HVA's is two to three orders of magnitude above HEA's at *every single field*, and both rise with h. So the trainability gap isn't a critical-point phenomenon — it holds across the whole sweep. Cross-check worth noting: at mid-sweep these read ~0.03 for HEA and ~25 for HVA, which is exactly the N=8 row of the main-deck barren-plateau table, computed by a *different* module. Two independent code paths, same numbers.

*(src/ansatz/vqe_error_profile.py)*

---

## Backup: why HVA wins — optimizer trajectories

The endpoint comparison on the previous slide understates the gap, so here's the full trajectory: ΔE plotted against Adam step number, one curve per ansatz, at a single representative field deep in the ordered phase. HEA plateaus early, at an error orders of magnitude above where HVA and QAOA end up — and both keep descending well past where HEA has stalled out.

This data was actually sitting in VQEResult.history the whole time, collected during every optimization run but previously discarded once the final energy was logged — plotting it directly is what makes the trainability gap visible rather than just inferring it from the endpoint numbers.

---

## Backup: 2D lattices

Everything in the main talk was chain-only; these rectangular layouts — 2x2, 2x4, 2x8 ladders, and a 4x4 small square — were part of the dataset but unused in the original project scope, so I extended the analysis to them. The clear trend is h_c growing with the number of nearest neighbors per site: 0.93, 1.31, 1.61, 1.88 going from the 1D chain toward the more connected 2D lattices, trending toward the known square-lattice value of about 3.044 from quantum Monte Carlo — though still far from that at these small N.

I didn't attempt a central-charge fit here, because 2D entanglement entropy follows a boundary-area law, not the 1D CFT logarithmic law from the theory section, so the Calabrese-Cardy formula simply doesn't apply. The same near-h=0 shading artifact from the 1D entropy slide shows up here too, and it's actually worse: the two N=16 rectangular lattices have the smallest finite-size tunnelling gap in the whole report, so the near-degeneracy issue is more pronounced.

---

## Backup: classical-shadow reconstruction

This is the one genuinely NISQ-realistic result in the project — no statevector anywhere in this calculation, only the 1000 randomized single-qubit measurement outcomes per field that the dataset ships, exactly what a real device would hand back. The estimator, defined below: for each snapshot, invert the randomized measurement to build a single-shot state estimate, and average the resulting linear-functional estimates — via median-of-means for robustness — across all 1000 snapshots.

What we reconstruct specifically, and why it's the square root of M_z squared rather than |M_z| directly, is the next backup slide.

---

## Backup: why √⟨M_z²⟩?

This anticipates why we don't just estimate the order parameter directly from the shadow data. Classical shadows only give unbiased estimators for functionals of ρ that are linear — expectation of O equals trace of ρ O, for some operator O — a hard requirement, not a technical inconvenience. The expectation of |M_z| is not linear in ρ, because of the absolute value, so no shadow protocol, however clever, can estimate it directly.

But the expectation of M_z squared is a linear functional — expand the operator and its expectation is N plus the sum over i not equal j of the expectation of Z_i Z_j, a genuine two-body Pauli observable, perfectly estimable from shadows. So what we actually reconstruct is the square root of the shadow estimate of M_z squared. In the deep ordered phase, where M_z only ever takes the two values plus or minus m, this coincides exactly with the true |M_z|. Away from that limit, particularly near criticality where M_z has a broader distribution, it's only an approximation, and that's where the reconstruction in the figures deviates a bit from the exact order parameter.

---

## Backup: fixing the central-charge bias

This anticipates how we know the open-chain bias isn't just a bug in our fitting code. The formula used throughout, the Calabrese-Cardy two-parameter fit, is the leading-order prediction and doesn't include boundary effects. The real correction, documented in Calabrese and Cardy's follow-up paper, arXiv 1002.4353, is that boundary-localized irrelevant operators contribute subleading terms scaling as a power of N, largest right at the two open ends of an open chain.

On the open chain we get c ≈ 0.62; refit the identical code, same formula, no changes, on periodic data instead, which has no boundary by construction, and the bias disappears — c comes out at about 0.51, right at the Ising value of 1/2. I trust this diagnosis rather than suspecting a code bug because the culprit, boundary operators, was named in the literature well before we ever fit anything — the lesson I'd draw is that a persistent, structured bias against known theory is itself data worth chasing physically before hunting through the code.

---

## Backup: building the HVA circuit

This anticipates whether the ansatz is hardcoded per system size or lattice. It's not: extract_structure inspects the dataset's own qml.Hamiltonian object term by term, so PauliZ tensor PauliZ factors become bonds in the circuit, and lone PauliX factors become field-rotation wires. There's no hardcoded lattice geometry anywhere — the exact same ansatz-construction code is correct for open or closed chains, 1D or 2D, purely because it's built from whatever bonds happen to be present in the Hamiltonian object it's handed.

The circuit: prepare the all-minus product state, then p layers, each applying e^{-i γ Z_i Z_j} across every bond followed by e^{-i β X_i} on every site — two parameters per layer, not O(N). Because that structure only ever applies ZZ and X rotations, it respects the model's own Z₂ symmetry by construction, which, as discussed on the trainability slide, is a large part of why it avoids barren plateaus in the first place.

---

## Backup: gradient variance, precisely

This anticipates exactly what's being measured for the barren-plateau claim. We sample n random parameter initializations, and at each one compute the exact gradient of the energy expectation with respect to every parameter, using adjoint differentiation — exact, not a finite-difference or parameter-shift estimate. For each gradient component separately, we take its variance across those n random samples, then average that variance over components — not just look at one fixed angle, which was an earlier, buggy version of this exact plot that gave a misleading picture.

For the HEA specifically we exclude its very first angle from that average, because it's a leading R_z rotation acting on |0⟩ before any entanglement has been introduced — an unobservable global phase with an identically zero gradient by construction, not a genuine trainability signal, and including it would have deflated the apparent variance. The HVA has no such leading-phase angle — its first parameter is a genuine ZZ rotation, in fact its largest gradient component — so for the HVA every component is kept.

Bottom line again: a variance that shrinks exponentially with N means almost every random starting point sits on a flat plain with no local signal to climb down.

---

## Backup: why stop at N=16?

This anticipates why we didn't push to larger systems. It's both a dataset limit and a genuine computational one. Exact ground truth needs the full statevector, 2^N complex amplitudes — already 65,536 entries at N=16 — and computing entanglement entropy needs an SVD of that state reshaped into a 2^(N/2)-by-2^(N/2) matrix, at every field value, every layout — that SVD, not the VQE circuits themselves, is the actual computational bottleneck in this whole project.

The qspin dataset itself only ships chain sizes 1x4, 1x8, 1x16, and rectangular sizes up through 4x4 — there simply is no larger exact ground truth available to compare against even if we wanted to push further. VQE and QAOA circuits alone would happily scale to larger N; it's specifically the exact cross-checks — exact diagonalization, entanglement entropy, Jordan-Wigner — that anchor N at 16 for this project.

---

## Backup: Jordan-Wigner, the diagonalization in full

This goes one level deeper than the main-deck derivation, carrying the Fourier-plus-Bogoliubov claim all the way to the explicit matrix. After Jordan-Wigner and a Fourier transform, the Hamiltonian block-diagonalizes into 2-by-2 sectors, each coupling mode q to mode minus q, shown here explicitly. Diagonalizing that 2-by-2 kernel gives the two bands below.

Notational note if anyone compares this against the main-deck dispersion slide: that one was written as ε(k) = 2 sqrt(1 + g² - 2g cos k) — the sign in front of the cosine differs, and that's a momentum-origin convention difference: q here is shifted by π relative to k there, since cos(k+π) = -cos(k) — same physics, same spectrum, different labeling of where q=0 sits.

The ground state fills every negative-energy mode, the lambda-minus band; the gap is λ_+ minus λ_-, minimized at q=π — since this q's origin is shifted by π relative to the main-deck k, that's the same point as k=0 there — vanishing there exactly at g=1 — the same physics as the main-deck slide, carried through to the explicit diagonalization.

---

## Backup: codebase layout

For anyone curious how this is organized: `src/` is split into three subpackages by role. `core/` holds the loader module wrapping qml.data.load into a typed IsingData dataclass, the shared plotting module for consistent style and an N-to-color mapping, and the process-pool helper for the multi-restart VQE grids. `physics/` holds one source file per physics question — order parameter and Binder cumulant, entanglement and central charge, finite-size scaling, boundary comparison, the 2D lattice analysis, Jordan-Wigner, classical shadows. `ansatz/` holds the two VQE ansätze, optimizer trajectories, the trainability benchmark, and the N x depth sweep. Every source module is mirrored by its own test module in the matching tests/ subpackage, 63 tests total. Nothing here is a monolith — each physics question lives in its own file, gets its own tests, produces its own plot.

---

## Backup: how a result becomes a slide

This anticipates whether the numbers in this talk are trustworthy or just hand-typed into the slides. The pipeline: the cached qspin HDF5 data goes through loader.load_ising, producing one typed IsingData object per lattice-periodicity-layout combination; each physics question's source module takes that IsingData in and writes exactly one PNG to plots/, using the shared plotting helpers; report.md and this presentation both embed those same PNG files directly, by relative path — no number in either document is re-typed by hand, everything is re-read from the code's own printed output.

Pytest, 63 tests, gates every module before its plot is trusted. A code-quality pass caught a stale duplicate and five dead imports, and one specific fix — excluding a trivial h=0 point from an average — moved a headline number from roughly 38x to 23x; a later performance-and-robustness pass then reran the whole VQE grid with convergence-based training and four random restarts per point, and the ~23x held up as a proper median rather than a single-seed fluke. I mention this deliberately: it's exactly the kind of thing this direct pipeline is designed to catch and to firm up, precisely because there's no hand-typing step where a stale number could silently survive a code change.

---

## Backup: dataset provenance

Last question this anticipates: is the underlying data itself trustworthy, and who produced it. It's PennyLane's own hosted qspin dataset collection, generated by Xanadu via exact diagonalization, downloaded once and cached locally as HDF5 — deliberately not our own exact-diagonalization code, so it can genuinely serve as ground truth rather than being a second copy of whatever bugs we might have.

shadow_basis and shadow_meas are pre-simulated randomized single-qubit Pauli measurements of those same exact ground states — so the shot noise in that data is real sampling noise, it's only the physical device itself that's simulated rather than actually run on hardware. The dataset's documentation page is linked below if anyone wants to look at it directly.

---
