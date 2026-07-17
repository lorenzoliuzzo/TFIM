from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pennylane as qml
from pennylane import numpy as pnp

from src.core.loader import IsingData
from src.ansatz.vqe import VQEResult, run_adam

PLOTS_DIR = Path(__file__).resolve().parent.parent / "plots"


def extract_structure(hamiltonian: qml.Hamiltonian) -> tuple[list[tuple[int, int]], list[int]]:
    """Read the ZZ bonds and the transverse-field wires straight off the
    dataset Hamiltonian, so the ansatz matches the actual lattice/BC.
    """
    bonds: list[tuple[int, int]] = []
    field_wires: list[int] = []
    coeffs, ops = hamiltonian.terms()
    for op in ops:
        factors = op.operands if isinstance(op, qml.ops.op_math.Prod) else [op]
        names = [type(f).__name__ for f in factors]
        wires = [w for f in factors for w in f.wires]
        if names == ["PauliZ", "PauliZ"]:
            bonds.append((wires[0], wires[1]))
        elif names == ["PauliX"]:
            field_wires.append(wires[0])
    return bonds, field_wires


def _hva_circuit(params: pnp.ndarray, bonds, field_wires, num_spins: int) -> None:
    # Start in |->^N: the exact ground state at h -> infinity, since the field
    # term +h*sum(X) is minimized by the X = -1 eigenstate on every site.
    for w in range(num_spins):
        qml.PauliX(wires=w)
        qml.Hadamard(wires=w)
    for gamma, beta in params:
        for i, j in bonds:
            qml.IsingZZ(gamma, wires=[i, j])
        for w in field_wires:
            qml.RX(beta, wires=w)


def anneal_init(n_layers: int, dt: float = 0.3) -> pnp.ndarray:
    """Annealing-inspired initial angles for QAOA / HVA.

    One Trotter step of the adiabatic sweep H(s) = (1-s) H_B + s H_C is a single
    (ZZ, X) layer; setting layer k to s_k = (k+0.5)/p gives gamma_k = s_k*dt and
    beta_k = (1-s_k)*dt, seeding the optimizer in the basin a slow anneal follows.
    """
    s = (pnp.arange(n_layers) + 0.5) / n_layers
    return pnp.stack([s * dt, (1.0 - s) * dt], axis=1)


def run_vqe_hva(
    hamiltonian: qml.Hamiltonian,
    num_spins: int,
    *,
    n_layers: int = 4,
    steps: int = 500,
    stepsize: float = 0.05,
    tol: float = 1e-7,
    patience: int = 30,
    init_params: pnp.ndarray | None = None,
    init_strategy: str = "random",
    seed: int = 0,
    device: str = "lightning.qubit",
    diff_method: str = "adjoint",
    c_dtype=pnp.complex128,
) -> VQEResult:
    """VQE with the Hamiltonian Variational Ansatz (HVA / QAOA-style) for the TFIM.

    Two parameters per layer (a ZZ angle and a transverse-field angle); the
    initial state is the exact h->infinity ground state |->^N.

    Initialization precedence: explicit `init_params` (e.g. a warm start) wins;
    otherwise `init_strategy` selects "random" (small uniform angles) or
    "anneal" (the adiabatic schedule of `anneal_init`).
    """
    bonds, field_wires = extract_structure(hamiltonian)
    dev = qml.device(device, wires=num_spins, c_dtype=c_dtype)

    @qml.qnode(dev, interface="autograd", diff_method=diff_method)
    def energy(params: pnp.ndarray) -> float:
        _hva_circuit(params, bonds, field_wires, num_spins)
        return qml.expval(hamiltonian)

    @qml.qnode(dev, interface="autograd")
    def statevector(params: pnp.ndarray) -> pnp.ndarray:
        _hva_circuit(params, bonds, field_wires, num_spins)
        return qml.state()

    if init_params is not None:
        params = pnp.array(init_params, requires_grad=True)
    elif init_strategy == "anneal":
        params = pnp.array(anneal_init(n_layers), requires_grad=True)
    elif init_strategy == "random":
        rng = pnp.random.default_rng(seed)
        params = pnp.array(rng.uniform(0.0, 0.1, size=(n_layers, 2)), requires_grad=True)
    else:
        raise ValueError(f"unknown init_strategy {init_strategy!r}")

    params, history = run_adam(energy, params, stepsize=stepsize, max_steps=steps,
                               tol=tol, patience=patience)

    return VQEResult(
        energy=float(energy(params)),
        params=params,
        state=statevector(params),
        history=history,
    )


@dataclass(frozen=True)
class WarmStartSweep:
    fields: pnp.ndarray
    vqe_energies: pnp.ndarray
    exact_energies: pnp.ndarray
    abs_errors: pnp.ndarray


def run_qaoa(
    hamiltonian: qml.Hamiltonian,
    num_spins: int,
    *,
    n_layers: int = 4,
    steps: int = 200,
    stepsize: float = 0.05,
    seed: int = 0,
) -> VQEResult:
    """QAOA for the TFIM: the HVA circuit seeded from an adiabatic schedule.

    Identical gate family to `run_vqe_hva`, but the annealing-inspired
    initialization (`init_strategy="anneal"`) makes this digitized quantum
    annealing rather than a generic variational search.
    """
    return run_vqe_hva(hamiltonian, num_spins, n_layers=n_layers, steps=steps,
                       stepsize=stepsize, init_strategy="anneal", seed=seed)


def warm_start_core(
    hamiltonians: list,
    num_spins: int,
    fields,
    ground_energies,
    *,
    n_layers: int = 4,
    steps: int = 400,
    init_strategy: str = "random",
    seed: int = 0,
    c_dtype=pnp.complex128,
) -> WarmStartSweep:
    """Warm-start sweep over a pre-selected list of (Hamiltonian, field, exact
    energy) triples, in ascending-field output order.

    Takes plain lists rather than a full `IsingData` so a single sweep is cheap
    to ship to a worker process (no bulky ground-state statevectors are pickled).
    """
    import numpy as _np

    fields = _np.asarray(fields, dtype=float)
    ee = _np.asarray(ground_energies, dtype=float)
    order = _np.argsort(fields)          # ascending, for the returned arrays
    ve = _np.empty(len(fields))
    prev_params = None
    for j in order[::-1]:                # sweep high field -> low field
        res = run_vqe_hva(hamiltonians[j], num_spins, n_layers=n_layers,
                          steps=steps, init_params=prev_params,
                          init_strategy=init_strategy, seed=seed, c_dtype=c_dtype)
        prev_params = res.params
        ve[j] = res.energy

    return WarmStartSweep(pnp.array(fields[order]), pnp.array(ve[order]),
                          pnp.array(ee[order]), pnp.array(_np.abs(ve - ee)[order]))


def warm_start_sweep(
    data: IsingData,
    *,
    n_layers: int = 4,
    steps: int = 400,
    indices: list[int] | None = None,
    init_strategy: str = "random",
    seed: int = 0,
    c_dtype=pnp.complex128,
) -> WarmStartSweep:
    """Sweep fields from high h (where |->^N is exact) down to low h, carrying
    the optimized parameters forward as the warm start for the next field.

    The first (highest-h) field uses `init_strategy` (e.g. "anneal" for QAOA);
    every subsequent field warm-starts from the previous optimum. `steps` is the
    per-field maximum budget; early stopping (see `run_adam`) usually converges
    well before it, so the warm-started fields are cheap.
    """
    indices = list(range(data.n_fields)) if indices is None else indices
    hams = [data.hamiltonians[i] for i in indices]
    fields = [float(data.fields[i]) for i in indices]
    ee = [float(data.ground_energies[i]) for i in indices]
    return warm_start_core(hams, data.num_spins, fields, ee, n_layers=n_layers,
                           steps=steps, init_strategy=init_strategy, seed=seed,
                           c_dtype=c_dtype)


if __name__ == "__main__":
    from src.core.loader import load_ising

    data = load_ising("1x8")
    idx = list(range(0, data.n_fields, 5))

    print("HVA + warm start vs the old StronglyEntanglingLayers benchmark (N=8):")
    sw = warm_start_sweep(data, n_layers=4, steps=120, indices=idx)
    print(f"  mean |dE| = {float(sw.abs_errors.mean()):.4e}")
    print(f"  max  |dE| = {float(sw.abs_errors.max()):.4e}")
    print("  (old StronglyEntanglingLayers N=8, 4 layers: mean |dE| ~ 6e-1)")
