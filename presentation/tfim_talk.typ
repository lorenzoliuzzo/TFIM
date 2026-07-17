#import "presentation_conf.typ": *
#import "@preview/touying:0.6.1": touying-set-config

#show: bamboo-theme.with(
  title: "Quantum Phase Transitions of the Transverse-Field Ising Model",
  author: "Lorenzo Liuzzo",
  date: datetime.today(),
)

// Provenance tag: names the src/ module that produced a slide's numbers/figures.
#let src-tag(..names) = {
  v(0.4em)
  align(right)[#text(size: 0.62em, fill: muted)[
    #names.pos().map(n => raw(n)).join([ · ])
  ]]
}

#title-slide()

== Phase transitions and the classical Ising model
#speaker-note[Let's start with the classical picture everyone already knows, because the quantum story is going to be the same question asked a different way. A phase transition is formally a non-analyticity of a thermodynamic potential -- Ehrenfest's classification just asks which derivative of the free energy first jumps or diverges: a discontinuity in the first derivative is first-order, like ice melting; a divergence in the second derivative is continuous, like the Curie point. For a symmetry-breaking transition specifically, we track an order parameter that's identically zero in the disordered phase and becomes nonzero -- and non-unique -- once the symmetry breaks.

Grounding this in a concrete model: the classical Ising Hamiltonian is H = -(1/2) sum over nearest-neighbor pairs of J sigma_i sigma_j, each spin sigma_i = ±1. It's invariant under flipping every spin at once -- a global Z_2 symmetry -- and the order parameter is the magnetization m, which the system spontaneously breaks below T_C by picking one of the two symmetry-related ground states.

The reason for this table is the 1D versus 2D contrast, the classical precursor to the quantum story. In 1D, a domain wall costs a fixed energy 2J but the entropy of where to place it grows like k_B T ln N, so Delta F = 2J - k_B T ln N is negative for any T>0 as N grows -- thermal fluctuations always win, no finite-temperature transition. In 2D, Onsager showed in 1944 the transition survives, because the domain wall's boundary is itself extensive, enough room to pay the entropy cost. Mean-field theory gets the 1D chain qualitatively wrong -- it predicts a transition where there isn't one -- which sets up the question of what quantum fluctuations, instead of thermal ones, can do that mean-field also can't capture.]
#grid(
  columns: (1.5fr, 1fr),
  gutter: 14pt,
  align(horizon)[
    - Phase transition = non-analyticity of a thermodynamic potential; symmetry-breaking $arrow$ an *order parameter* zero in the disordered phase, nonzero (and non-unique) in the ordered one
    #text(size: 0.9em)[$ H=-1/2 sum_(chevron.l i,j chevron.r) J sigma_i sigma_j, quad sigma_i=plus.minus 1 $]
    - $bb(Z)_2$ symmetry: invariant under the global flip $sigma_i arrow -sigma_i$; order parameter = magnetization $m$
  ],
  align(horizon + center)[#figure(image("assets/phase_transition_states.png", width: 100%), caption: [First-order: ice $arrow$ water $arrow$ vapor])],
)
#table(
  columns: (auto, auto, 1.8fr),
  table.header([dim.], [transition?], [why]),
  [1D], [*no*], [$Delta F_"wall" = 2J - k_B T ln N < 0$ for any $T>0$],
  [2D], [yes (Onsager '44)], [wall boundary is extensive — entropy cost is payable],
)

== The transverse-field Ising model
#speaker-note[Here's the conceptual jump, and the model we'll actually work with. A quantum phase transition happens at exactly T=0, driven not by thermal fluctuations but by quantum ones, and the signature is the same kind of non-analyticity as before, except now it's the ground-state energy that's non-analytic in some coupling g, not the free energy in temperature. We get quantum fluctuations in by promoting the classical spins to Pauli operators and adding a transverse field term proportional to sigma^x; since sigma^x doesn't commute with sigma^z, this genuinely drives quantum dynamics -- tunnelling between the classical spin configurations -- not just a relabeling. That gives the actual model on the slide: H = J times the sum of ZZ couplings over nearest-neighbor bonds, plus h times the sum of X on every site, J=-1 by convention. I've defined the order parameter here too, the expectation of |M_z|, which we track throughout. The reason to write down the two solvable limits in the table before doing anything numerical is that they're qualitatively different, and that alone forces a transition somewhere in between. When g = h/|J| is much greater than 1 the field term dominates and the ground state is the uncorrelated product state with every spin along +x -- a trivial paramagnet. When g is much less than 1 the coupling term dominates and you get the two classical ferromagnetic ground states back, all up or all down along z. You can't smoothly deform an uncorrelated product state into a two-fold-degenerate symmetry-broken one without something singular happening in between. One subtlety on the last bullet: on any finite lattice, what would be a level crossing is smoothed into an avoided crossing, so the ground-state energy is perfectly smooth at finite N; it only sharpens into a true non-analyticity in the thermodynamic limit, N to infinity -- which is exactly why finite-size scaling later matters. For the 1D infinite chain that critical point sits at exactly g_c=1, and the rest of the talk pins that number down three independent ways and then reproduces it on a quantum computer.]
- QPT: transition at $T=0$ driven by quantum (not thermal) fluctuations — the *ground-state energy* becomes non-analytic in a coupling $g$
- Promote the Ising spins to Pauli operators and add a transverse field $sigma^x$ that does *not* commute with $sigma^z$ $arrow$ quantum dynamics (tunnelling between classical configurations)
#text(size: 0.82em)[$ H = J sum_(chevron.l i,j chevron.r) sigma_i^z sigma_j^z + h sum_i sigma_i^x, quad J=-1, quad chevron.l |M_z| chevron.r = chevron.l |sum_i sigma_i^z| chevron.r $]
#align(center)[#table(
  columns: (auto, auto, auto),
  table.header([regime], [ground state], [phase]),
  [$g=h\/|J| gt.double 1$], [$product_i |arrow.r chevron.r_i$], [paramagnetic],
  [$g lt.double 1$], [$product_i |arrow.t chevron.r_i$ or $product_i |arrow.b chevron.r_i$], [ferromagnetic],
)]
- Finite $N$: avoided crossing (smooth); true non-analyticity only at $N arrow infinity$ — exact 1D critical point $g_c=1$

== Two exact routes to $g_c=1$
#speaker-note[g_c=1 isn't a numerical fit, it's derived exactly -- and by two independent routes, which is why I'm putting them side by side.

Route one, Suzuki-Trotter: slice the partition function Z = Tr(e^{-beta H}) into M imaginary-time steps, and each slice becomes an extra classical Ising layer, so you end up with the partition function of a classical 2D anisotropic Ising model on an N-sites-by-M-time-slices lattice -- imaginary time literally becomes the second spatial dimension. Onsager already solved that model's exact critical point in 1944; substitute the mapped anisotropy back in, take M to infinity -- same as T to zero on the quantum side -- and you get g_c = 1, for every value of J. No series expansion, no fit.

Route two, Jordan-Wigner: map spin up/down onto an occupied or empty fermionic orbital. The naive site-local version is broken, because spins on different sites commute but fermions anticommute -- fixed by attaching a nonlocal string operator. After the transform the Hamiltonian is quadratic -- hopping and pairing only -- so a Fourier transform plus a Bogoliubov rotation diagonalizes it with no exponential cost. The gap is the minimum over k of the dispersion, and it vanishes exactly at k=0, g=1.

Why both: these are complementary, not redundant. Suzuki-Trotter gives the actual non-analyticity of the free energy -- sufficient for a QPT; Jordan-Wigner gives a vanishing gap -- a necessary condition. Zero shared machinery, same answer. And the JW closed form is what src/physics/jordan_wigner.py evaluates numerically later, as a cross-check against the dataset. Full derivations for both are in backup if anyone wants them.]
#table(
  columns: (auto, 1.5fr, 1fr),
  table.header([route], [mechanism], [gives]),
  [Suzuki-Trotter], [$Z="Tr"(e^(-beta H))$ sliced into $M$ imaginary-time steps $arrow$ *classical* 2D anisotropic Ising ($N times.o M$); Onsager's exact $sinh(2beta J_x^c)sinh(2beta J_y^c)=1$, then $M arrow infinity$], [non-analytic free energy — *sufficient*],
  [Jordan-Wigner], [spin $arrow$ fermion ($sigma_j^z=2hat(n)_j-1$) + nonlocal string $arrow$ $H$ *quadratic* $arrow$ Fourier + Bogoliubov; $epsilon(k)=2sqrt(1+g^2-2g cos k)$], [vanishing gap at $k=0$ — *necessary*],
)
- Both are exact and non-perturbative — no fit, no series expansion; *zero shared machinery, same $g_c=1$* (derivations in backup)
- JW also gives $E_0 = -sum_(k>0) epsilon(k)$ in closed form — evaluated by `src/physics/jordan_wigner.py` as a numerical cross-check later

== Entanglement entropy and the area law
#speaker-note[This sets up the central-charge results, so let me define things carefully. For a bipartite pure state, the Schmidt decomposition gives a reduced density matrix rho_A on one half, and the entanglement entropy is its von Neumann entropy, S = -Tr(rho_A ln rho_A). Away from criticality, gapped ground states obey an area law: S scales with the size of the boundary between the two regions, not the volume of either, because only correlations within one correlation length xi of the cut actually contribute. Right at criticality, xi diverges, the area law breaks down, and S grows logarithmically with block size instead -- the coefficient fixed by the central charge c of the underlying CFT, via Calabrese-Cardy. For the Ising universality class, c = 1/2 exactly. One more closed-form check: exactly at g=0, the TFIM entropy formula predicts S goes to ln 2 -- that's the cat-state degeneracy from the classical Ising slide, made explicit as an entanglement statement: the two symmetry-broken branches are equally weighted, giving exactly one bit of entanglement entropy.]
- A correlation-based probe, *independent of any order parameter* — and it fixes the *universality class* (via $c$), not just the transition's location
- Bipartite pure state $arrow$ Schmidt decomposition; entanglement entropy $S=-"Tr"(rho_A ln rho_A)$ of the reduced density matrix
- Gapped ground states obey an *area law*: $S$ scales with a region's boundary, not its volume — only correlations within a correlation length $xi$ of the cut matter
- At criticality $xi arrow infinity$: the area law breaks, $S$ grows *logarithmically* with block size, coefficient fixed by the central charge $c$ (Calabrese-Cardy) — Ising CFT: $c=1\/2$
- Exactly at $g arrow 0$ the closed-form TFIM entropy predicts $S arrow ln 2$ — the cat-state degeneracy of Sec. "classical Ising model" made explicit

== The dataset: qspin / Ising
#speaker-note[Before the results, I want to be upfront about where the ground truth comes from. Everything is loaded from PennyLane's qspin dataset via a single call: qml.data.load with sysname Ising, plus periodicity, lattice, and layout -- a system is fully determined by those four discrete choices. Periodicity is open, two free ends, or closed, a ring. Lattice is chain, 1D, or rectangular, 2D. Layout is the size, rows by columns -- chains use 1x4, 1x8, 1x16; rectangular goes from 2x2 up through 4x4. N, the total spin count, is rows times columns, over 4, 8, 16 -- fourteen distinct systems in all.

Each system isn't one Hamiltonian, it's a sweep of 100 field values over a range that always straddles h=1, and every attribute in the table is an array of length 100 indexed by that sweep. hamiltonians is 100 full PennyLane Hamiltonian objects -- our code reads these directly, term by term, rather than hard-coding the lattice geometry; src/ansatz/vqe_hva.py literally extracts the ZZ bonds and X field sites from whatever Hamiltonian object it's handed. ground_energies and ground_states are the exact diagonalization ground truth at each field. order_params is the expectation of |M_z|, precomputed. shadow_basis and shadow_meas are classical-shadow data: 1000 randomized single-qubit Pauli measurement bases and outcomes per field -- exactly what a real NISQ device would hand you, no statevector involved, used in backup.]
- `qml.data.load("qspin", sysname="Ising", periodicity=.., lattice=.., layout=..)` — fully specified by four discrete choices: `periodicity` `"open"`/`"closed"`, `lattice` `"chain"` (1D)/`"rectangular"` (2D), `layout` = `rows x cols` (chain: `1x4,1x8,1x16`; rect.: `2x2 … 4x4`)
- $N = "rows"times"cols" in {4,8,16}$; each system sweeps 100 values of $h$, always straddling $h=1$
#table(
  columns: (auto, auto, 1fr),
  table.header([attribute], [shape], [meaning]),
  [`hamiltonians`], [$100 times$ `qml.Hamiltonian`], [$H(h)$, one per field — read directly by our code, not hard-coded],
  [`ground_energies` / `ground_states`], [$(100,)$ / $100 times 2^N$], [exact $E_0(h)$ and $|psi_0(h) chevron.r$],
  [`order_params`], [$(100,)$], [$chevron.l |M_z| chevron.r (h)$],
  [`shadow_basis` / `shadow_meas`], [$(100,1000,N)$], [classical-shadow bases / outcomes],
)

== The code: one module per physics question
#speaker-note[Every number in this talk comes out of this pipeline, so it's worth thirty seconds. The cached qspin HDF5 goes through loader.load_ising, which returns a typed IsingData dataclass -- one per lattice, periodicity, layout combination. Each physics question is then exactly one module in src/: it takes IsingData in and writes one PNG to plots/ out, through shared plotting helpers so every figure has the same style and the same N-to-colour map. Both report.md and these slides embed those same PNGs by relative path. That's the important part: no number in either output is re-typed by hand -- everything is re-read from the code's own printed output, so a stale number can't silently survive a code change.

The scale: sixteen modules, about twenty-one hundred lines, backed by six hundred lines of tests -- 63 of them, all passing, one test module per physics module. pytest gates every module before its plot is trusted.

The design point I'd most defend is the second bullet: extract_structure inspects the dataset's own qml.Hamiltonian object term by term -- PauliZ-tensor-PauliZ factors become bonds, lone PauliX factors become field wires. There is no hardcoded lattice geometry anywhere. That's why the identical VQE code is correct on the open chain, the closed ring, and the 2D rectangular lattices, without a single branch on system type -- the circuit is built from whatever bonds are actually present in the Hamiltonian it's handed.

If asked what this bought us concretely: the pipeline is exactly what caught a stale duplicate and five dead imports, and excluding a trivial h=0 point moved a headline number from about 38x to 23x -- which then held up under a later multi-restart rerun as a proper median rather than a single-seed fluke. Backup has the full module map.]
- Pipeline: cached `qspin` HDF5 $arrow$ `loader.load_ising()` $arrow$ typed `IsingData` $arrow$ *one `src/*.py` per physics question* $arrow$ one PNG in `plots/` $arrow$ embedded by relative path into *both* `report.md` and these slides — *no number in either output is typed by hand*
#grid(
  columns: (1.45fr, 1fr),
  gutter: 12pt,
  align(horizon)[
    #text(size: 0.88em)[
    - `extract_structure` reads the dataset's own `qml.Hamiltonian` term-by-term (`PauliZ@PauliZ` $arrow$ bonds, `PauliX` $arrow$ field wires): *no hardcoded lattice* — the same VQE code is correct for open/closed, 1D/2D
    - Shared `plotting.py` (one style, one $N arrow$ colour map); `parallel.py` process pool for the multi-restart VQE grids
    ]
  ],
  align(horizon + center)[
    #text(size: 0.82em)[#table(
      columns: (auto, auto),
      table.header([artefact], [size]),
      [`src/` modules], [16 (2 151 lines)],
      [`tests/`], [621 lines, *63 passing*],
      [coverage], [1 test module / physics module],
      [figures], [every PNG script-generated],
    )]
  ],
)

#focus-slide[Exact results]

== Order parameter and the Binder cumulant
#speaker-note[On the left is the headline picture: the order parameter, |M_z| over N, against h, for a few sizes -- collapsing from near 1 in the ordered phase down toward 0 in the paramagnetic phase, sharpening as N grows, exactly the finite-size behavior expected approaching a true non-analyticity. On the right is the Binder cumulant, U_4, defined below -- a specific combination of moments engineered so finite-size shape effects cancel out, which is why curves for different N cross almost exactly at a single point instead of gradually sliding past each other. That crossing gives h_c ≈ 0.84 in the cumulant's own units. Flag if it comes up: 0.84 isn't directly comparable to the textbook universal Binder ratio for isotropic 2D classical Ising, about 0.61, because the quantum-classical mapping produces an anisotropic classical system -- N spatial sites by M imaginary-time slices, not a square lattice -- and the universal ratio depends on that aspect ratio and boundary conditions. What's universal, and what we actually use, is that the curves cross at all, at a single h -- that crossing location, not its height, is our h_c estimate, and it's cleaner than reading the inflection point by eye.]
- Binder cumulant $U_4 = 1 - chevron.l M_z^4 chevron.r \/ (3 chevron.l M_z^2 chevron.r^2)$ — cancels finite-size shape effects
#grid(
  columns: 2,
  gutter: 8pt,
  figure(image("../plots/order_parameter_chain_open.png", width: 92%), caption: [$chevron.l |M_z| chevron.r \/ N$ vs $h$]),
  figure(image("../plots/binder_cumulant_chain_open.png", width: 92%), caption: [$U_4$ crossing $approx 0.84$]),
)
#src-tag("src/physics/analysis.py")

== Entanglement entropy and the central charge
#speaker-note[Two results on one slide. On the left, entanglement entropy S against h for several N: away from the transition S stays roughly flat with N -- the area law -- then peaks near the transition, where correlations become long-ranged, and deep in the ordered phase it plateaus at ln 2. That plateau is the cat-state degeneracy: the exact ground state there is a symmetric superposition of the two ferromagnetic branches, and tracing out half the system leaves exactly one bit. The peak location is a third independent g_c estimate.

Flag proactively: there's a shaded band near h=0 where entropy wobbles. That's not noise in the pipeline -- the two symmetry-broken branches have an exponentially-small-in-N tunnelling splitting, so the ED solver has no principled reason to return the same near-degenerate eigenvector at adjacent fields; it can flip between the symmetric and antisymmetric combination at random. The order parameter doesn't care which one comes back, since |M_z| is the same either way, which is why that curve stays smooth. We flagged this in the pipeline rather than smoothing it away.

On the right, the central charge -- the universal fingerprint of the critical point's field theory; Ising CFT predicts exactly 1/2. We fit block-entropy scaling to Calabrese-Cardy. On the open chain we get 0.62, visibly off. That's not a bug: it's a known boundary-operator artifact, arXiv 1002.4353 -- irrelevant operators at the two open ends add subleading corrections the naive two-parameter fit ignores. Refit the identical code on the periodic chain -- no boundary at all -- and the bias vanishes: c ≈ 0.51. That agreement appearing only once we remove the boundary is itself evidence we diagnosed the bias correctly rather than curve-fitting to a number we wanted. Details in backup.]
#text(size: 0.88em)[
- Three regimes: area-law plateau $arrow$ critical peak ($xi arrow infinity$, a third independent $g_c$ estimate) $arrow$ $ln 2$ plateau (ordered cat state)
- Calabrese-Cardy fit $S(l) = (c\/6) ln[(2N\/pi) sin(pi l\/N)] + c_1'$: open chain $c approx 0.62$ (boundary bias, arXiv:1002.4353) $arrow$ *closed chain $c approx 0.51$*, the Ising value — same code, boundary removed (backup)
]
#grid(
  columns: 2,
  gutter: 8pt,
  figure(image("../plots/entropy_vs_field_chain_open.png", width: 92%), caption: [#text(size: 0.8em)[$S$ vs $h$: area law $arrow$ peak $arrow$ $ln 2$]]),
  figure(image("../plots/central_charge_closed_N16.png", width: 92%), caption: [#text(size: 0.8em)[Closed chain: $c approx 0.51$ (Ising: $1\/2$)]]),
)
#src-tag("src/physics/entanglement.py")

== Locating $g_c$: finite size and boundaries
#speaker-note[Here's the finite-size h_c estimate from the steepest-descent point of the order parameter, at three sizes, for both boundary conditions. Open chain: 0.61, 0.78, 0.91 at N=4, 8, 16 -- drifting toward the thermodynamic value of 1 as N grows, exactly as expected, since finite systems round off the transition and pull the apparent critical point inward. As a cross-check, the steepest-descent of the order parameter and the crossover point of the entanglement entropy agree at each N -- reassuring, since they come from completely different quantities.

Now the boundary comparison, in the same table. Periodic boundaries have no chain ends at all, so there's no boundary-driven finite-size correction to fight, and the closed chain converges to 1 much faster -- already 1.01 by N=8, where the open chain is still at 0.78. Quantitatively that's the finite-size scaling ansatz on the slide: the open chain simply has a much larger prefactor a, because of the extra boundary operators. Note this is the same boundary physics that biased the central charge two slides ago -- one cause, two symptoms.

Honest caveat: only three system sizes, so what I'm calling an extrapolation is really an exact interpolation through three points, not an error-barred fit -- I wouldn't overstate the precision of that h_c(infinity) intercept.

If asked about data collapse: it's in backup -- rescaling the order parameter by N^{beta/nu} collapses curves for different N onto one universal curve, which fixes location and universality class at once, without needing the central charge.]
#grid(
  columns: (1.1fr, 1fr),
  gutter: 14pt,
  align(horizon)[
    #table(
      columns: (auto, auto, auto),
      table.header([$N$], [$h_c$ open], [$h_c$ closed]),
      [4], [0.61], [0.93],
      [8], [0.78], [1.01],
      [16], [0.91], [1.01],
    )
    - Both drift toward $h\/|J|=1$ (*thermodynamic limit*); steepest-descent of $chevron.l |M_z| chevron.r$ and the entropy crossover agree at each $N$
    - Finite-size scaling $h_c (N) = h_c (infinity) - a N^(-1\/nu)$, $nu=1$ — the closed chain's $a$ is far smaller: *no ends, no boundary correction*
    - Same boundary physics that biased $c$ — one cause, two symptoms
  ],
  align(horizon + center)[#figure(image("../plots/boundary_comparison_hc.png", width: 100%))],
)
#src-tag("src/physics/finite_size_scaling.py", "src/physics/boundary_comparison.py")

== Independent check: Jordan-Wigner
#speaker-note[This is the payoff of the free-fermion derivation from the theory section. The closed-form Jordan-Wigner ground energy, E_0 = -sum over positive-k modes of epsilon(k), filling every negative-energy mode of the Bogoliubov spectrum, is evaluated directly and compared against the dataset's exact diagonalization energies: they agree to somewhere between 1e-13 and 1e-15 for N=4, 8, and 16. That's floating-point precision, not numerical-method precision -- there's no exact diagonalization anywhere in this calculation, just a closed-form expression evaluated directly. Since this derivation shares zero code with the exact-diagonalization pipeline the rest of the results rely on, this agreement is about as strong a cross-check as we could ask for.]
- The closed-form free-fermion energy (previous section) matches the dataset's exact diagonalization to floating-point precision, with no ED involved
#figure(image("../plots/jordan_wigner_cross_check.png", width: 88%))
#src-tag("src/physics/jordan_wigner.py")

#focus-slide[Variational quantum eigensolver]

== VQE: the variational principle and two ansätze
#speaker-note[Switching to the quantum-computing side. The variational theorem is the whole justification for VQE: for any trial state, E(theta) is guaranteed greater than or equal to the true ground energy E_0. So minimizing over theta can only approach E_0 from above, never overshoot, for any parametrized family. U(theta) is a parametrized circuit on a fixed reference state; the hybrid loop has a quantum device -- simulator here -- evaluate E(theta) and its gradient via the adjoint method, exact and efficient in simulation, while a classical optimizer, Adam, updates theta.

Key caveat: convergence of Adam only certifies a local optimum of whatever ansatz you chose -- not E_0 itself. There's an irreducible expressibility floor unless the true ground state lies in the reachable manifold of your circuit. That's the real design question, and it's exactly what the ansatz comparison measures: expressive enough to reach the ground state, structured enough to stay trainable.

The two circuits sit at opposite ends of that trade-off. HEA is PennyLane's StronglyEntanglingLayers: generic rotations plus a fixed CNOT pattern, knows nothing about the Hamiltonian. HVA goes the other way: p layers alternating e^{-i gamma Z_i Z_j} over every bond and e^{-i beta X_i} over every site -- two parameters per layer regardless of size -- motivated by Trotterizing real-time evolution under H itself, or equivalently digitizing an adiabatic path in g.

The reference state, all-minus, is exact at g to infinity, since the field term is +h sum of X, minimized by the -1 eigenstate of X on every site -- so HVA starts exactly at the easy end of the sweep. On top of that, a warm start: sweep h from high to low, initializing each field from the previous field's optimum, transporting the easy solution into the harder, more entangled regime.

QAOA, on the next slide, is this same HVA circuit again -- reinterpreted and initialized differently.]
#text(size: 0.9em)[$ E(theta) = chevron.l psi(theta)|H|psi(theta) chevron.r gt.eq E_0, quad |psi(theta) chevron.r = U(theta)|psi_0 chevron.r $]
- Hybrid loop: a quantum device evaluates $E(theta)$ and its gradient (adjoint), a classical optimizer (Adam) updates $theta$. Caveat: convergence certifies a *local* optimum of a *bounded* ansatz — $E(theta^*)-E_0$ has an expressibility floor unless $|psi_0 chevron.r$ lies in $U(theta)$'s reachable manifold
#table(
  columns: (auto, 2.1fr, 1fr),
  table.header([ansatz], [circuit], [knows about $H$?]),
  [*HEA*], [generic single-qubit rotations + entangling gates], [no — expressive],
  [*HVA*], [$p$ layers of $product_(chevron.l i,j chevron.r) e^(-i gamma_l Z_i Z_j) product_i e^(-i beta_l X_i)$ — 2 params/layer], [yes — reads $H$'s bonds],
)
- HVA reference state $|- chevron.r^(times.o N)$ = the *exact* ground state at $g arrow infinity$; *warm-start* sweeps $h$ high$arrow$low, each field initialized from the previous optimum — transporting the easy solution into the entangled regime

== QAOA as digitized quantum annealing
#speaker-note[QAOA reuses the literal same HVA circuit, but reinterprets and initializes it differently. The physical picture is an adiabatic path from an easy Hamiltonian H_B to the target H_C: H(s) = (1-s)H_B + s H_C, sweeping s from 0 to 1 slowly -- the adiabatic theorem guarantees the ground state is tracked, provided s varies slowly relative to the instantaneous gap. One Trotter step of that sweep is exactly one HVA layer: H_B is the sum of X, the mixer; H_C is the ZZ coupling -- same (gamma,beta) circuit, reinterpreted as digitized annealing rather than a generic variational ansatz. The annealing-inspired init seeds layer l at s_l=(l+1/2)/p, with gamma_l = s_l·delta t and beta_l=(1-s_l)·delta t -- placing the optimizer directly in the basin a slow physical anneal would follow, instead of random angles. As p goes to infinity with a slow enough schedule this reproduces exact adiabatic evolution; at finite p the residual energy error measures the cost of digitizing that continuous sweep into discrete Trotter steps. Worth flagging forward: because QAOA is the same circuit as HVA, it inherits HVA's trainability wholesale -- which is why the barren-plateau table two slides on reports a single shared HVA/QAOA column rather than three separate ansätze.]
- Adiabatic path from an easy Hamiltonian to $H$ itself: $H(s) = (1-s)H_B + s H_C$, $s:0 arrow 1$ slowly — the adiabatic theorem guarantees the ground state is tracked if $s$ varies slowly enough relative to the gap
- One Trotter step of this sweep *is* one HVA layer: $H_B=sum_i X_i$ (mixer), $H_C$ = the ZZ coupling — the same $(gamma,beta)$ circuit, reinterpreted
- *Annealing-inspired init*: layer $l$ seeded at $s_l=(l+1\/2)\/p$ with $gamma_l = s_l dot.c delta t$, $beta_l=(1-s_l) dot.c delta t$ — places the optimizer in the basin a slow anneal would follow, instead of starting at random
- As $p arrow infinity$ with a slow schedule, QAOA reproduces exact adiabatic evolution; at finite $p$ the residual energy error measures the cost of digitization
- Same circuit as HVA $arrow$ *same trainability*: the barren-plateau table reports one shared HVA/QAOA column
#src-tag("src/ansatz/vqe_hva.py")

== VQE: hardware-efficient vs physics-informed — results
#speaker-note[Here's the head-to-head, and every curve is a median over four independent random restarts with the shaded inter-quartile band showing the restart-to-restart spread -- a single seed is an anecdote, VQE outcomes swing with the initialization. At N=8, median absolute error over the field sweep is 2.8e-1 for HEA and 1.2e-2 for HVA -- about 23 times better, or 1.8e-3 if you take the best of the four restarts. The right panel is the same comparison at N=16, and the gap widens to about 85 times: HEA has essentially stopped learning -- its error is order ten -- while HVA is still near 0.2. That widening is the whole point: it's not that HEA is a constant factor worse, it degrades as the system grows. Reproducibility note if asked: these numbers come from convergence-based training rather than a fixed step budget, and the whole grid runs in parallel across cores in single precision -- an earlier fixed-budget, single-seed version reported this as a fragile ~23x that has now firmed up with proper restart statistics.]
- Error metric: $Delta E(theta) = E(theta) - E_0 gt.eq 0$; each curve is the *median over 4 restarts*, band = IQR
- The HEA$arrow$HVA gap *widens* with size: $approx 23 times$ at $N=8$ $arrow$ $approx 85 times$ at $N=16$, where HEA hits its barren plateau
#grid(
  columns: 2,
  gutter: 8pt,
  figure(image("../plots/ansatz_comparison_N8.png", width: 100%), caption: [$N=8$: median $|Delta E|$ $2.8 times 10^(-1)$ (HEA) $arrow$ $1.2 times 10^(-2)$ (HVA), $approx 23 times$]),
  figure(image("../plots/ansatz_comparison_N16.png", width: 100%), caption: [$N=16$: $1.8 times 10^1$ (HEA) $arrow$ $2.1 times 10^(-1)$ (HVA), $approx 85 times$]),
)
#src-tag("src/ansatz/vqe.py", "src/ansatz/vqe_hva.py", "src/ansatz/benchmark.py")

== Trainability: barren plateaus and depth
#speaker-note[Accuracy alone doesn't tell you whether an ansatz is trainable at scale, so here's the other half of the VQE story. The diagnostic: the variance, over random parameter initializations, of the energy gradient with respect to each parameter component, averaged over components, at fixed depth. If that variance shrinks exponentially with N, almost every random starting point sits on a flat plain with essentially no gradient signal -- a barren plateau, and no optimizer, however good, can climb out.

The left panel and the table show exactly this divergence: HEA's variance drops from 0.298 at N=4 to 6.9e-4 at N=16 -- collapsing fast. HVA and QAOA's variance instead grows, from 5.0 to 147.3 over the same range. So HVA isn't just more accurate, it stays trainable as the system grows.

If pushed on whether that's a proof or an empirical trend: with only N up to 16, this alone can't distinguish "provably plateau-free" from "plateaus onset later than HEA's" -- but there's theoretical backing, the dynamical-Lie-algebra argument from Larocca and collaborators. HVA's generators, the Z2-symmetric ZZ bonds and X field terms, span only a polynomially-sized dynamical Lie algebra under the Hamiltonian's own symmetry, unlike HEA's unstructured generators, which span the full exponentially-large unitary algebra. A polynomial-dimension DLA is what guarantees polynomially, rather than exponentially, vanishing gradients at any N.

The right panel is the operational face of that: HEA alone, swept over circuit depth at each size, with restart bands. The naive intuition -- more layers, more expressibility, lower error -- only holds at N=4. At N=16 the error actually grows with depth, from about 4 up to 14: adding parameters makes it strictly worse, because a deeper generic circuit has an exponentially flatter landscape. This is a fair test -- convergence-based stopping means depth isn't confounded with an under-spent step budget, and bands are over four restarts. Mirror image of the HVA story: structured gets better with size, generic gets worse.]
#text(size: 0.86em)[- Diagnostic: $"Var"_theta [partial_(theta_i) chevron.l H chevron.r]$, averaged over components $i$ across $n$ random $theta$ draws (protocol in backup). HEA collapses with $N$; HVA/QAOA *grows* — a polynomial-dimension dynamical Lie algebra (Larocca et al.), enforced by $bb(Z)_2$ symmetry]
#grid(
  columns: (0.5fr, 1fr, 1fr),
  gutter: 8pt,
  align(horizon)[
    #text(size: 0.8em)[#table(
      columns: (auto, auto, auto),
      table.header([$N$], [HEA], [HVA]),
      [4], [0.298], [5.0],
      [8], [0.034], [24.8],
      [16], [$6.9 dot 10^(-4)$], [147.3],
    )]
    #v(6pt)
    #align(left)[#text(size: 0.62em, fill: rgb("#5E8B65"))[#raw("src/ansatz/trainability.py")\ #raw("src/ansatz/benchmark.py")]]
  ],
  align(horizon + center)[#figure(image("../plots/barren_plateaus.png", width: 100%), caption: [#text(size: 0.65em)[Gradient variance vs $N$]])],
  align(horizon + center)[#figure(image("../plots/vqe_benchmark.png", width: 100%), caption: [#text(size: 0.65em)[HEA depth scan: deeper = *worse* at $N=16$]])],
)

== Summary and next steps
#speaker-note[To pull it together: we reproduced the TFIM phase transition three independent ways -- from the exact ground states via order parameter and Binder cumulant, from the completely independent analytic Jordan-Wigner solution, and from VQE -- and all three agree on g_c=1. The physics-informed ansatz, HVA, beats generic HEA on both accuracy and trainability, and that advantage traces directly back to respecting the model's own Z2 symmetry. Periodic boundaries resolved two separate open-chain artifacts at once -- the central-charge bias and the slow convergence of the finite-size h_c estimate -- a nice unification, since a priori those looked like two unrelated issues. Beyond the original scope, covered in backup if there's time, we extended to 2D lattices, where h_c grows with lattice connectivity, and to classical-shadow reconstruction, the one genuinely NISQ-realistic result in the project. What's still open: a combined order-parameter-plus-entropy figure we haven't built yet, and proper error bars on the finite-size fits, since we only have three system sizes to work with.]
- Reproduced the TFIM phase transition from exact data, an independent analytic (Jordan-Wigner) solution, and VQE — all agree
- Physics-informed ansatz (HVA) beats generic HEA on accuracy and trainability
- Periodic boundaries resolve two open-chain artifacts at once: the central-charge bias and the slow $h_c$ convergence
- Extended scope (backup): 2D lattices (h_c grows with connectivity) and classical-shadow reconstruction (the NISQ-realistic result)
- Open: combined order-parameter + entropy figure; error bars on the finite-size fits (only 3 system sizes)

#focus-slide[Thank you]

#show: touying-set-config.with((appendix: true, freeze-slide-counter: true))

#focus-slide[Backup slides]

== Backup: Suzuki-Trotter, the mapping in full
#speaker-note[This is the main-deck "route one" carried through. Slice Z = Tr(e^{-beta H}) into M imaginary-time steps; each slice becomes an extra classical Ising layer, so you land on the partition function of a classical 2D anisotropic Ising model, N sites by M time-slices -- imaginary time literally is the second spatial dimension. The quantum coupling g maps onto the classical anisotropy gamma via this tanh formula. Onsager solved the anisotropic 2D classical Ising critical point exactly in 1944: sinh(2 beta J_x^c) sinh(2 beta J_y^c) = 1. Substitute the mapped anisotropy back in, take M to infinity -- same as T to zero on the quantum side -- and you get g_c = 1 for every value of J. Exact and non-perturbative: no series expansion, no fit. This is genuinely where h_c=1 comes from, and it's the sufficient condition -- an actual non-analyticity of the free energy -- as opposed to Jordan-Wigner's necessary vanishing gap.]
- Suzuki-Trotter: slice $Z="Tr"(e^(-beta H))$ into $M$ imaginary-time steps $arrow$ partition function of a *classical* 2D anisotropic Ising model, $N$ sites $times.o$ $M$ time-slices — imaginary time *is* the second spatial dimension
- Quantum coupling $g$ becomes a classical anisotropy $beta^*J_y=gamma=-1/2 ln[tanh(beta J g\/M)]$
- Onsager's exact 2D critical point, $sinh(2beta J_x^c)sinh(2beta J_y^c)=1$, substituted back with $M arrow infinity$ (i.e. $T arrow 0$) gives $g^c=1$ for *every* $J$
- Exact and non-perturbative: no series expansion, no fit — and it gives the non-analyticity of the free energy itself (*sufficient* for a QPT), where JW's vanishing gap is only *necessary*

== Backup: data collapse
#speaker-note[This is the finite-size scaling result I skipped in the main deck. Rescale the order parameter by N^{beta/nu} and the field axis by N^{1/nu}: if curves for different N fall onto a single universal curve under that rescaling, that's strong independent confirmation of both the critical point location and the universality class -- and crucially it needs no central charge at all. It collapses only for the correct h_c and the correct exponents simultaneously, which is what makes it a sharp test rather than a fit. The exponents used, beta=1/8 and nu=1, are the 2D classical Ising exponents -- 2D because of the imaginary-time dimension from the Suzuki-Trotter mapping, which is the same correspondence as the theory section.]
- Data collapse: $(chevron.l |M_z| chevron.r \/ N) N^(beta\/nu) = f[(h-h_c) N^(1\/nu)]$ — collapses *only* for the correct $h_c$ *and* exponents, so it fixes location + universality class at once (no central charge needed)
- $beta=1\/8$, $nu=1$ are the 2D-Ising exponents (the imaginary-time dimension of the Suzuki-Trotter mapping)
#figure(image("../plots/data_collapse_chain_open.png", width: 74%))

== Backup: why we don't quote an $h_c (infinity)$
#speaker-note[This anticipates the obvious question after the finite-size slide: you have h_c at three sizes drifting toward 1 -- why not just fit the scaling ansatz and extrapolate to N=infinity, and quote that number? Because we tried, and it doesn't work, and I'd rather show you that than quietly omit it.

Left panel: fit h_c(N) = h_c(infinity) - a N^{-1/nu} to the three open-chain points with h_c(infinity) and nu both free. The inflection-point data extrapolates to 1.34; the Binder-crossing data extrapolates to 2.00 -- which is its fit bound, so the optimizer ran to the edge of the allowed range. The fitted exponents come out at nu = 2.58 and 8.57, against the exact nu = 1. So a free three-parameter fit through three points recovers neither the right critical field nor the right exponent -- and scipy's curve_fit can't even estimate a covariance, which is the fit telling you it has zero degrees of freedom left. Three points, three parameters. That's not a measurement, it's interpolation wearing a lab coat.

This is exactly why the main deck states the finite-size scaling ansatz with nu fixed at 1 and quotes only the measured h_c(N) values, never an extrapolated intercept. The honest claim is the one we make: h_c(N) drifts toward 1, and periodic boundaries get there faster. The dishonest version -- "we extrapolate h_c(infinity) = 1.00 +/- 0.02" -- would need more system sizes than the dataset ships, which is the N=16 ceiling from the other backup slide.

Right panel is the same story for the central charge: c drifts 0.588, 0.608, 0.622 across N=4,8,16 -- moving away from the CFT value of 1/2, not toward it, because of the open-chain boundary bias. That divergence-with-N is what made us suspect a boundary artifact rather than a numerical error in the first place, and refitting on the closed chain confirmed it.]
#text(size: 0.84em)[
- We *measure* $h_c (N)$ and deliberately do *not* quote an extrapolated $h_c (infinity)$ — this slide is why
- Free fit of $h_c (N) = h_c (infinity) - a N^(-1\/nu)$ to 3 points: $h_c (infinity)=1.34$ (inflection) / $2.00$ (Binder — *its fit bound*), $nu=2.58\/8.57$ vs exact $nu=1$; `curve_fit` cannot even estimate a covariance — 3 points, 3 free parameters
- Main deck therefore fixes $nu=1$ and quotes only measured $h_c (N)$; more sizes would need $N>16$
]
#grid(
  columns: 2,
  gutter: 8pt,
  figure(image("../plots/finite_size_hc_chain_open.png", width: 92%), caption: [#text(size: 0.75em)[Free 3-point fit overshoots $h_c=1$]]),
  figure(image("../plots/central_charge_scaling_chain_open.png", width: 92%), caption: [#text(size: 0.75em)[$c$ drifts *away* from $1\/2$ — boundary bias]]),
)
#src-tag("src/physics/finite_size_scaling.py")

== Backup: where HVA's advantage actually lives
#speaker-note[This anticipates the sharpest challenge to the headline number. The main deck says HVA beats HEA by 23x at N=8 as a median over the field sweep. A median hides structure, so here is the error resolved field by field, and the structure is the opposite of uniform.

Top panel: at h=0, HEA is not merely competitive, it is better by orders of magnitude -- error around 1e-6, essentially exact -- while HVA sits near 0.9, its worst point anywhere. The two cross around h≈0.4, and past that HVA wins by one to four orders of magnitude for the rest of the sweep. So the 23x is real but it is an average over a regime where HVA dominates, plus a corner where it loses.

Both facts have the same explanation, and it's the reference state. At h=0 the exact ground state is a classical product state, which a generic circuit nails trivially -- and this is precisely why we exclude h=0 from the reported sweep, since it's a trivial symmetry-broken product state rather than a meaningful test. HVA is worst there because its warm start comes from the opposite end: the all-minus state is exact at h to infinity, so the sweep transports that solution downward, and it accumulates the most error at the far end, deep in the ordered phase, where preparing a GHZ-like cat state needs circuit depth of order N/2 that a fixed p simply doesn't have. HVA's advantage is real and it grows with N, but it lives at and above criticality -- not at h=0.

Bottom panel: gradient variance against field for both, at N=8. HVA's is two to three orders of magnitude above HEA's at every single field, and both rise with h. So the trainability gap isn't a critical-point phenomenon -- it holds across the whole sweep. Cross-check worth noting: at mid-sweep these read about 0.03 for HEA and about 25 for HVA, which is exactly the N=8 row of the main-deck barren-plateau table, computed by a different module. Two independent code paths, same numbers.]
#grid(
  columns: (1.25fr, 1fr),
  gutter: 12pt,
  align(horizon)[
    #text(size: 0.8em)[
    - The headline "$approx 23 times$ at $N=8$" is a *median over the sweep* — resolved by field, the advantage is *not* uniform
    - $h=0$: HEA is *better* by orders of magnitude (exact product state — why we exclude $h=0$); crossover at $h approx 0.4$; HVA then wins by up to $10^4$
    - HVA's worst point is the deep ordered phase: its warm start is exact at $h arrow infinity$, and a GHZ cat state needs depth $tilde N\/2$
    - Gradient variance (bottom): HVA above HEA at *every* field — the trainability gap is *not* a critical-point artifact; mid-sweep values reproduce the main-deck $N=8$ row from a *different* module
    ]
  ],
  align(horizon + center)[#figure(image("../plots/vqe_error_trainability_1x8.png", width: 95%))],
)
#src-tag("src/ansatz/vqe_error_profile.py")

== Backup: why HVA wins — optimizer trajectories
#speaker-note[The endpoint comparison in the main deck understates the gap, so here's the full trajectory: Delta E against Adam step number, one curve per ansatz, at a single representative field deep in the ordered phase. HEA plateaus early, at an error orders of magnitude above where HVA and QAOA end up -- and both keep descending well past where HEA has stalled. This data was sitting in VQEResult.history the whole time, collected during every optimization run but discarded once the final energy was logged; plotting it directly is what makes the trainability gap visible rather than merely inferred from endpoint numbers.]
- $Delta E$ vs Adam step at one field: HEA plateaus early, orders of magnitude above where HVA/QAOA end up — the endpoint comparison alone *understates* the gap
#figure(image("../plots/optimizer_trajectories.png", width: 52%))

#focus-slide[Beyond the original scope]

== Backup: 2D lattices
#speaker-note[Everything in the main talk was chain-only; these rectangular layouts -- 2x2, 2x4, 2x8 ladders, and a 4x4 small square -- were part of the dataset but unused in the original project scope, so I extended the analysis to them. The clear trend is h_c growing with the number of nearest neighbors per site: 0.93, 1.31, 1.61, 1.88 going from the 1D chain toward the more connected 2D lattices, trending toward the known square-lattice value of about 3.044 from quantum Monte Carlo -- though still far from that at these small N. I didn't attempt a central-charge fit here, because 2D entanglement entropy follows a boundary-area law, not the 1D CFT logarithmic law from the theory section, so the Calabrese-Cardy formula simply doesn't apply. The same near-h=0 shading artifact from the 1D entropy slide shows up here too, and it's actually worse: the two N=16 rectangular lattices have the smallest finite-size tunnelling gap in the whole report, so the near-degeneracy issue is more pronounced.]
#grid(
  columns: 2,
  gutter: 8pt,
  figure(image("../plots/order_parameter_rectangular_open.png", width: 100%), caption: [#text(size: 0.75em)[Order parameter, 2x2/2x4/2x8/4x4]]),
  figure(image("../plots/entropy_rectangular_open.png", width: 100%), caption: [#text(size: 0.75em)[Entanglement entropy, 2x2/2x4/2x8/4x4]]),
)

== Backup: classical-shadow reconstruction
#speaker-note[This is the one genuinely NISQ-realistic result in the project -- no statevector anywhere in this calculation, only the 1000 randomized single-qubit measurement outcomes per field that the dataset ships, exactly what a real device would hand back. The estimator, defined below: for each snapshot, invert the randomized measurement to build a single-shot state estimate, and average the resulting linear-functional estimates -- via median-of-means for robustness -- across all 1000 snapshots. What we reconstruct specifically, and why it's the square root of M_z squared rather than |M_z| directly, is the next backup slide.]
- Shadow estimator: $hat(rho) = times.o_i (3|b_i chevron.r chevron.l b_i| - II)$ per snapshot, averaged (median-of-means) over 1000 shots
#grid(
  columns: 2,
  gutter: 8pt,
  figure(image("../plots/shadow_reconstruction_N4.png", width: 100%), caption: [#text(size: 0.75em)[$N=4$]]),
  figure(image("../plots/shadow_reconstruction_N8.png", width: 100%), caption: [#text(size: 0.75em)[$N=8$]]),
)

== Backup: why $sqrt(chevron.l M_z^2 chevron.r)$?
#speaker-note[This anticipates why we don't just estimate the order parameter directly from the shadow data. Classical shadows only give unbiased estimators for functionals of rho that are linear -- expectation of O equals trace of rho O, for some operator O -- a hard requirement, not a technical inconvenience. The expectation of |M_z| is not linear in rho, because of the absolute value, so no shadow protocol, however clever, can estimate it directly. But M_z squared is linear -- expand it out and it's N plus the sum over i not equal j of the expectation of Z_i Z_j, a genuine two-body Pauli observable, perfectly estimable from shadows. So what we actually reconstruct is the square root of the shadow estimate of M_z squared. In the deep ordered phase, where M_z only ever takes the two values plus or minus m, this coincides exactly with the true |M_z|. Away from that limit, particularly near criticality where M_z has a broader distribution, it's only an approximation, and that's where the reconstruction in the figures deviates a bit from the exact order parameter.]
- Classical shadows give unbiased estimators of *linear* functionals of $rho$ only: $chevron.l O chevron.r = "Tr"(rho O)$ for an operator $O$
- $chevron.l |M_z| chevron.r$ is *not* linear in $rho$ (absolute value), so it cannot be estimated this way — no shadow protocol gets around this
- $M_z^2 = sum_i Z_i^2 + sum_(i eq.not j) Z_i Z_j = N + sum_(i eq.not j) chevron.l Z_i Z_j chevron.r$ *is* linear — a genuine two-body Pauli observable
- If $M_z$ only ever takes values $plus.minus m$ (deep ordered phase), $chevron.l |M_z| chevron.r = m = sqrt(chevron.l M_z^2 chevron.r)$ exactly; elsewhere it is an approximation, worst near criticality

== Backup: fixing the central-charge bias
#speaker-note[This anticipates how we know the open-chain bias isn't just a bug in our fitting code. The formula used throughout, the Calabrese-Cardy two-parameter fit, is the leading-order prediction and doesn't include boundary effects. The real correction, documented in Calabrese and Cardy's follow-up paper, arXiv 1002.4353, is that boundary-localized irrelevant operators contribute subleading terms scaling as a power of N, largest right at the two open ends of an open chain. On the open chain we get c ≈ 0.62; refit the identical code, same formula, no changes, on periodic data instead, which has no boundary by construction, and the bias disappears -- c comes out at about 0.51, right at the Ising value of 1/2. I trust this diagnosis rather than suspecting a code bug because the culprit, boundary operators, was named in the literature well before we ever fit anything -- the lesson I'd draw is that a persistent, structured bias against known theory is itself data worth chasing physically before hunting through the code.]
#text(size: 0.85em)[
- Calabrese-Cardy (open chain): $S(l) = (c\/6) ln[(2N\/pi) sin(pi l\/N)] + c_1'$ — the naive 2-parameter fit used throughout the report
- Real correction (arXiv:1002.4353): boundary-localized *irrelevant operators* add subleading terms scaling as a power of $N$, biggest at the two open ends. Lesson: a persistent bias against known theory is itself data — chase the physics before suspecting the code
]
#grid(
  columns: 2,
  gutter: 8pt,
  figure(image("../plots/central_charge_open_N16.png", width: 92%), caption: [#text(size: 0.75em)[Open: $c approx 0.62$ — boundary present]]),
  figure(image("../plots/central_charge_closed_N16.png", width: 92%), caption: [#text(size: 0.75em)[Closed: $c approx 0.51$ — bias gone]]),
)

== Backup: building the HVA circuit
#speaker-note[This anticipates whether the ansatz is hardcoded per system size or lattice. It's not: extract_structure inspects the dataset's own qml.Hamiltonian object term by term, so PauliZ tensor PauliZ factors become bonds in the circuit, and lone PauliX factors become field-rotation wires. There's no hardcoded lattice geometry anywhere -- the exact same ansatz-construction code is correct for open or closed chains, 1D or 2D, purely because it's built from whatever bonds happen to be present in the Hamiltonian object it's handed. The circuit: prepare the all-minus product state, then p layers, each applying e^{-i gamma Z_i Z_j} across every bond followed by e^{-i beta X_i} on every site -- two parameters per layer, not O(N). Because that structure only ever applies ZZ and X rotations, it respects the model's own Z2 symmetry by construction, which, as discussed on the trainability slide, is a large part of why it avoids barren plateaus in the first place.]
- `extract_structure(hamiltonian)` inspects the dataset's own `qml.Hamiltonian` term-by-term: `PauliZ@PauliZ` factors $arrow$ bonds, lone `PauliX` factors $arrow$ field wires
- No hardcoded lattice geometry: the *same* ansatz code is correct for open or closed chains, 1D or 2D, because it is built from whatever bonds are actually present
- Circuit: prepare $|- chevron.r^(times.o N)$, then $p$ layers of $product_(chevron.l i,j chevron.r) e^(-i gamma Z_i Z_j)$ followed by $product_i e^(-i beta X_i)$ — 2 parameters per layer, not $O(N)$
- Respects the model's own $bb(Z)_2$ symmetry by construction, which is a large part of why it avoids barren plateaus

== Backup: gradient variance, precisely
#speaker-note[This anticipates exactly what's being measured for the barren-plateau claim. We sample n random parameter initializations, and at each one compute the exact gradient of the energy expectation with respect to every parameter, using adjoint differentiation -- exact, not a finite-difference or parameter-shift estimate. For each gradient component separately, we take its variance across those n random samples, then average that variance over components -- not just look at one fixed angle, which was an earlier, buggy version of this exact plot that gave a misleading picture. For the HEA specifically we exclude its very first angle from that average, because it's a leading R_z rotation acting on |0⟩ before any entanglement has been introduced -- an unobservable global phase with an identically zero gradient by construction, not a genuine trainability signal, and including it would have deflated the apparent variance. The HVA has no such leading-phase angle -- its first parameter is a genuine ZZ rotation, in fact its largest gradient component -- so for the HVA every component is kept. Bottom line again: a variance that shrinks exponentially with N means almost every random starting point sits on a flat plain with no local signal to climb down.]
- Sample $n$ random parameter initializations; compute $partial_theta chevron.l H chevron.r$ (exact, adjoint differentiation) at each
- Take the variance of each gradient *component* across the samples, then average over components (not one fixed angle — that was the pre-fix version of this exact plot)
- HEA only: exclude its leading angle — a leading $R_z$ acting on $|0 chevron.r$, an unobservable global phase with identically zero gradient by construction, not a trainability signal. HVA's first angle is a genuine $Z Z$ rotation (its *largest* gradient component) and is kept
- A variance that shrinks exponentially with $N$ means: almost every random starting point sits on a flat plain — no local signal to climb down

== Backup: why stop at N=16?
#speaker-note[This anticipates why we didn't push to larger systems. It's both a dataset limit and a genuine computational one. Exact ground truth needs the full statevector, 2^N complex amplitudes -- already 65,536 entries at N=16 -- and computing entanglement entropy needs an SVD of that state reshaped into a 2^(N/2)-by-2^(N/2) matrix, at every field value, every layout -- that SVD, not the VQE circuits themselves, is the actual computational bottleneck in this whole project. The qspin dataset itself only ships chain sizes 1x4, 1x8, 1x16, and rectangular sizes up through 4x4 -- there simply is no larger exact ground truth available to compare against even if we wanted to push further. VQE and QAOA circuits alone would happily scale to larger N; it's specifically the exact cross-checks -- exact diagonalization, entanglement entropy, Jordan-Wigner -- that anchor N at 16 for this project.]
- Exact ground truth needs the full statevector: $2^N$ complex amplitudes — already 65,536 entries at $N=16$
- Entanglement entropy needs an SVD of that state reshaped into a $2^(N\/2) times 2^(N\/2)$ matrix at every field, every layout — the actual bottleneck, not the VQE circuits themselves
- The `qspin` dataset itself only ships `1x4`/`1x8`/`1x16` (chain) and up to `4x4` (rectangular) — there is no larger *exact* ground truth to compare against even if we wanted one
- VQE/QAOA circuits alone would happily scale further; it is the exact cross-checks (ED, entanglement, JW) that anchor $N$ at 16

== Backup: Jordan-Wigner, the diagonalization in full
#speaker-note[This goes one level deeper than the main-deck derivation, carrying the Fourier-plus-Bogoliubov claim all the way to the explicit matrix. After Jordan-Wigner and a Fourier transform, the Hamiltonian block-diagonalizes into 2-by-2 sectors, each coupling mode q to mode minus q, shown here explicitly. Diagonalizing that 2-by-2 kernel gives the two bands below. Notational note if anyone compares this against the main-deck dispersion slide: that one was written as epsilon(k) = 2 sqrt(1 + g^2 - 2g cos k) -- the sign in front of the cosine differs, and that's a momentum-origin convention difference: q here is shifted by pi relative to k there, since cos(k+pi) = -cos(k) -- same physics, same spectrum, different labeling of where q=0 sits. The ground state fills every negative-energy mode, the lambda-minus band; the gap is lambda_+ minus lambda_-, minimized at q=pi -- since this q's origin is shifted by pi relative to the main-deck k, that's the same point as k=0 there -- vanishing there exactly at g=1 -- the same physics as the main-deck slide, carried through to the explicit diagonalization.]
- After Jordan-Wigner + Fourier transform ($hat(a)_j = N^(-1\/2)sum_q hat(a)_q e^(i q j)$), the Hamiltonian block-diagonalizes into $2 times 2$ sectors $(hat(a)_q, hat(a)_(-q)^dagger)$: $hat(H) = sum_(q>0) mat(hat(a)_q^dagger, hat(a)_(-q);)mat(-J cos q - g J, -i J sin q; i J sin q, J cos q + g J;) mat(hat(a)_q; hat(a)_(-q)^dagger;)$
- Diagonalizing this $2 times 2$ kernel gives two bands $lambda_plus.minus (q) = plus.minus J sqrt((cos q + g)^2 + sin^2 q) = plus.minus J sqrt(1+g^2+2g cos q)$
- Ground state fills every negative-energy mode ($lambda_-$ band); the gap is $Delta(q)=lambda_+(q)-lambda_-(q)$, minimized at $q=pi$ (this $q$'s origin is shifted by $pi$ relative to the main-deck $k$), vanishing there exactly at $g=1$
- This is the same physics as the main-deck dispersion slide, carried through to the explicit matrix diagonalization

== Backup: codebase layout
#speaker-note[For anyone curious how this is organized: `src/` is split into three subpackages by role. `core/` holds the loader module wrapping qml.data.load into a typed IsingData dataclass, the shared plotting module for consistent style and an N-to-color mapping, and the process-pool helper for the multi-restart VQE grids. `physics/` holds one source file per physics question -- order parameter and Binder cumulant, entanglement and central charge, finite-size scaling, boundary comparison, the 2D lattice analysis, Jordan-Wigner, classical shadows. `ansatz/` holds the two VQE ansätze, optimizer trajectories, the trainability benchmark, and the N x depth sweep. Every source module is mirrored by its own test module in the matching tests/ subpackage, 63 tests total. Nothing here is a monolith -- each physics question lives in its own file, gets its own tests, produces its own plot.]
#text(size: 13pt)[
```
data/               cached qspin .h5 files (git-ignored)
src/
  core/
    loader.py             qml.data.load -> typed IsingData dataclass
    plotting.py           shared style / N->color map / save_fig
    parallel.py           process-pool map for multi-restart VQE grids
  physics/
    analysis.py           order parameter, Binder cumulant, data collapse
    entanglement.py       entropy, central charge (open + closed)
    finite_size_scaling.py   h_c(N) extrapolation, central charge vs N
    boundary_comparison.py   open vs closed h_c
    lattice_2d.py         rectangular-lattice analysis
    jordan_wigner.py      analytic free-fermion cross-check
    classical_shadow.py   shadow-based order-parameter reconstruction
  ansatz/
    vqe.py / vqe_hva.py           HEA / HVA+QAOA ansätze + sweeps
    optimizer_trajectory.py       per-step energy-error trajectories
    vqe_error_profile.py          dE(h) + gradient variance vs field
    trainability.py / benchmark.py   gradient variance, N x depth sweep
                          16 modules, 2151 lines
tests/              mirrors src/ (core/physics/ansatz), 63 tests, pytest
                    621 lines; plotting/parallel exercised indirectly
plots/              generated figures (PNG), referenced by both outputs below
report.md         written report — embeds plots/*.png
presentation/            these slides — embed the *same* plots/*.png
```
]

== Backup: how a result becomes a slide
#speaker-note[This anticipates whether the numbers in this talk are trustworthy or just hand-typed into the slides. The pipeline: the cached qspin HDF5 data goes through loader.load_ising, producing one typed IsingData object per lattice-periodicity-layout combination; each physics question's source module takes that IsingData in and writes exactly one PNG to plots/, using the shared plotting helpers; report.md and this presentation both embed those same PNG files directly, by relative path -- no number in either document is re-typed by hand, everything is re-read from the code's own printed output. Pytest, 63 tests, gates every module before its plot is trusted. A code-quality pass caught a stale duplicate and five dead imports, and one specific fix -- excluding a trivial h=0 point from an average -- moved a headline number from roughly 38x to 23x; a later performance-and-robustness pass then reran the whole VQE grid with convergence-based training and four random restarts per point, and the ~23x held up as a proper median rather than a single-seed fluke. I mention this deliberately: it's exactly the kind of thing this direct pipeline is designed to catch and to firm up, precisely because there's no hand-typing step where a stale number could silently survive a code change.]
- `qspin` dataset (cached HDF5) $arrow$ `loader.load_ising()` $arrow$ one typed `IsingData` per (lattice, periodicity, layout)
- Each physics question is one `src/*.py` module: takes `IsingData` in, writes one PNG to `plots/` out, via the shared `plotting.py` helpers
- `report.md` and `presentation/tfim_talk.typ` both embed those same PNGs directly by relative path — no numbers are re-typed by hand, only re-read from the code's own printed output
- `pytest` (63 tests) gates every module before its plot is trusted; a code-quality pass fixed a stale duplicate and 5 dead imports, and excluding a trivial h=0 point moved the headline from ~38x to ~23x — which then *held* under a later multi-restart (median $plus.minus$ IQR) rerun, all caught/confirmed precisely *because* the pipeline is this direct

== Backup: dataset provenance
#speaker-note[Last question this anticipates: is the underlying data itself trustworthy, and who produced it. It's PennyLane's own hosted qspin dataset collection, generated by Xanadu via exact diagonalization, downloaded once and cached locally as HDF5 -- deliberately not our own exact-diagonalization code, so it can genuinely serve as ground truth rather than being a second copy of whatever bugs we might have. shadow_basis and shadow_meas are pre-simulated randomized single-qubit Pauli measurements of those same exact ground states -- so the shot noise in that data is real sampling noise, it's only the physical device itself that's simulated rather than actually run on hardware. The dataset's documentation page is linked below if anyone wants to look at it directly.]
- PennyLane's `qspin` collection: exact-diagonalization ground truth hosted by Xanadu, downloaded once and cached locally as HDF5
- Not our own ED code — deliberately independent of everything we compute, so it can act as ground truth rather than a second copy of our own bugs
- `shadow_basis`/`shadow_meas` are pre-simulated randomized single-qubit Pauli measurements of the *same* exact ground states — the shot noise is real, only the "device" is simulated
- https://pennylane.ai/datasets/transverse-field-ising-model
