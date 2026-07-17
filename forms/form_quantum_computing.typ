#let check(on) = if on [(X)] else [( )]

#set page(paper: "a4", margin: (x: 2.1cm, top: 1.5cm, bottom: 1.2cm))
#set text(font: "Libertinus Serif", size: 10.5pt)
#set par(justify: true, leading: 0.55em)

#let course = "Foundations of Quantum Computing 2025/26"
#let professors = (
  (name: "Enrico Prati", mail: "enrico.prati@unimi.it"),
  (name: "Daniele Bajoni", mail: "daniele.bajoni@unipv.it"),
)
#let title = [Quantum Phase Transition of the Transverse-Field Ising Model: a VQE and QAOA Study]
#let method = [VQE and QAOA with a Hamiltonian Variational Ansatz (HVA); gradient-variance
  analysis to study trainability (barren plateaus).]
#let objective = [Probing the QPT of the 1D TFIM using VQE and QAOA,
  benchmarked against exact ground states from the PennyLane `qspin` dataset. The critical
  field $h_c$ is estimated via finite-size scaling of the magnetisation and entanglement
  entropy. Energy error and gradient variance vs $h$ reveal where the variational ansatz
  fails and connect this to barren plateaus.]
#let repos = (
  [*PennyLane* — statevector simulation and optimisation of the VQE and QAOA circuits.],
  [*NumPy / SciPy / Matplotlib* — base numerical and plotting stack.],
)
#let references = (
  (text: [Kadowaki & Nishimori — Quantum annealing in the transverse Ising model, Phys. Rev. E 58 (1998)],
    url: "https://arxiv.org/abs/cond-mat/9804280"),
  (text: [Peruzzo et al. — A variational eigenvalue solver on a photonic quantum processor, Nat. Commun. 5, 4213 (2014)],
    url: "https://arxiv.org/abs/1304.3061"),
  (text: [Farhi et al. — A Quantum Approximate Optimization Algorithm (2014)],
    url: "https://arxiv.org/abs/1411.4028"),
  (text: [Calabrese & Cardy — Entanglement entropy and quantum field theory, J. Stat. Mech. P06002 (2004)],
    url: "https://arxiv.org/abs/hep-th/0405152"),
  (text: [McClean et al. — Barren plateaus in quantum neural network training landscapes, Nat. Commun. 9, 4812 (2018)],
    url: "https://arxiv.org/abs/1803.11173"),
  (text: [Wiersema et al. — Exploring entanglement and optimization within the Hamiltonian Variational Ansatz, PRX Quantum (2020)],
    url: "https://arxiv.org/abs/2008.02941"),
  (text: [Preskill — Quantum Computing in the NISQ Era and Beyond, Quantum 2, 79 (2018)],
    url: "https://arxiv.org/abs/1801.00862"),
)

// --- layout ---

#grid(
  columns: (1fr, 1fr, 1fr),
  [Name: *Lorenzo*],
  [Last name: *Liuzzo*],
  [Date: *30 / 06 / 2026*],
)

#v(0.6em)
Send to #professors.map(p => link("mailto:" + p.mail)[#p.mail]).join([ and ]) and wait for
approval. We recommend to ask approval with sufficient advance (at least 3 weeks)
before the examination day you plan, so you may start to work on the project once
you received approval.

#v(0.7em)
#align(center)[#text(size: 12pt)[#course]]
#v(0.25em)
#align(center)[PROPOSAL OF EXAMINATION PROJECT]
#v(0.7em)

*Title:* #title

#v(0.55em)
*Learning method/algorithm used:* #method

#v(0.55em)
*Objective* (max 3 lines):
#par(justify: true)[#objective]

#v(0.55em)
*Based on a previously existing project:*
#pad(left: 2.4em)[
  #check(false) No, it is totally new not based on code of others \
  #check(true) Yes, I have partly used code from the following repositories
  (Qiskit, Mitiq, Github….): \
  #pad(left: 1.2em, top: 0.2em)[
    #for r in repos [#sym.dash.en #r \ ]
  ]
]

#v(0.45em)
*Reference used:*
#pad(left: 2.4em)[
  #for r in references [#link(r.url)[#r.text] \ ]
]

#v(0.45em)
*Needed dataset:*
#pad(left: 2.4em)[
  #check(false) Not needed \
  #check(false) Yes: I have original data from… \
  #check(true) Yes: Published here url: #link("https://pennylane.ai/datasets/transverse-field-ising-model") \
]
