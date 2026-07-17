from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pennylane as qml
from pennylane import numpy as pnp

from src.core.loader import IsingData, load_ising
from src.core.plotting import save_fig, setup_style


def abs_mz_from_state(state: pnp.ndarray, num_spins: int) -> float:
    """Order parameter <|M_z|> = sum_x |sum_i s_i(x)| * |amp_x|^2 from a statevector.

    s_i = +1 for |0> and -1 for |1> on each wire, matching the dataset's
    longitudinal magnetization definition.
    """
    probs = pnp.abs(pnp.asarray(state)) ** 2
    dim = 1 << num_spins
    idx = pnp.arange(dim)
    # bit b of basis state -> spin +1 (bit 0) or -1 (bit 1)
    bits = ((idx[:, None] >> pnp.arange(num_spins)[::-1]) & 1)
    mz = (1 - 2 * bits).sum(axis=1)
    return float((pnp.abs(mz) * probs).sum())


@dataclass(frozen=True)
class VQEResult:
    energy: float
    params: pnp.ndarray
    state: pnp.ndarray
    history: list[float]


def run_adam(
    energy,
    params: pnp.ndarray,
    *,
    stepsize: float,
    max_steps: int,
    tol: float = 1e-7,
    patience: int = 30,
) -> tuple[pnp.ndarray, list[float]]:
    """Adam descent with energy-plateau early stopping.

    Steps until the energy stops improving by more than `tol` for `patience`
    consecutive steps, or `max_steps` is reached. Returns the final parameters
    and the per-step energy history (energy is recorded before each update, as
    `AdamOptimizer.step_and_cost` returns the cost at the pre-step parameters).
    A convergence criterion (rather than a fixed step count) is what keeps a
    deeper ansatz from looking *worse* than a shallow one purely because it was
    under-trained at a fixed budget.
    """
    opt = qml.AdamOptimizer(stepsize=stepsize)
    history: list[float] = []
    best = float("inf")
    stall = 0
    for _ in range(max_steps):
        params, prev = opt.step_and_cost(energy, params)
        e = float(prev)
        history.append(e)
        if e < best - tol:
            best = e
            stall = 0
        else:
            stall += 1
            if stall >= patience:
                break
    return params, history


def run_vqe(
    hamiltonian: qml.Hamiltonian,
    num_spins: int,
    *,
    n_layers: int = 3,
    steps: int = 500,
    stepsize: float = 0.1,
    tol: float = 1e-7,
    patience: int = 30,
    seed: int = 0,
    device: str = "lightning.qubit",
    diff_method: str = "adjoint",
    c_dtype=pnp.complex128,
) -> VQEResult:
    """Minimize <H> with a hardware-efficient StronglyEntanglingLayers ansatz.

    `steps` is the maximum step budget; optimization stops early once the energy
    plateaus (see `run_adam`). `c_dtype` sets the statevector precision:
    `complex64` roughly halves the per-step cost at the ~1e-5 accuracy floor of
    single precision — safe for the energy-*error* sweeps, which run at
    tolerances far above that (the default stays `complex128` so the tight
    variational-bound checks are unaffected).
    """
    dev = qml.device(device, wires=num_spins, c_dtype=c_dtype)
    shape = qml.StronglyEntanglingLayers.shape(n_layers=n_layers, n_wires=num_spins)

    @qml.qnode(dev, interface="autograd", diff_method=diff_method)
    def energy(params: pnp.ndarray) -> float:
        qml.StronglyEntanglingLayers(params, wires=range(num_spins))
        return qml.expval(hamiltonian)

    @qml.qnode(dev, interface="autograd")
    def statevector(params: pnp.ndarray) -> pnp.ndarray:
        qml.StronglyEntanglingLayers(params, wires=range(num_spins))
        return qml.state()

    rng = pnp.random.default_rng(seed)
    params = pnp.array(rng.normal(scale=0.1, size=shape), requires_grad=True)
    params, history = run_adam(energy, params, stepsize=stepsize, max_steps=steps,
                               tol=tol, patience=patience)

    return VQEResult(
        energy=float(energy(params)),
        params=params,
        state=statevector(params),
        history=history,
    )


@dataclass(frozen=True)
class VQESweep:
    fields: pnp.ndarray
    vqe_energies: pnp.ndarray
    exact_energies: pnp.ndarray
    vqe_order_params: pnp.ndarray
    exact_order_params: pnp.ndarray


def sweep_vqe(
    data: IsingData,
    *,
    indices: list[int] | None = None,
    n_layers: int = 3,
    steps: int = 200,
    seed: int = 0,
) -> VQESweep:
    """Run VQE at selected field indices and collect results vs the exact data."""
    indices = list(range(data.n_fields)) if indices is None else indices
    fields, ve, ee, vo, eo = [], [], [], [], []
    for i in indices:
        res = run_vqe(data.hamiltonians[i], data.num_spins,
                      n_layers=n_layers, steps=steps, seed=seed)
        fields.append(data.fields[i])
        ve.append(res.energy)
        ee.append(data.ground_energies[i])
        vo.append(abs_mz_from_state(res.state, data.num_spins))
        eo.append(data.order_params[i])
    return VQESweep(
        fields=pnp.array(fields),
        vqe_energies=pnp.array(ve),
        exact_energies=pnp.array(ee),
        vqe_order_params=pnp.array(vo),
        exact_order_params=pnp.array(eo),
    )


def plot_sweep(sweep: VQESweep, num_spins: int, *, out_path: Path | None = None) -> Path:
    """Two-panel comparison of VQE vs exact: energy and order parameter vs h."""
    setup_style()
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.plot(sweep.fields, sweep.exact_energies, "-", lw=1.5, label="exact")
    ax1.plot(sweep.fields, sweep.vqe_energies, "o", ms=5, mfc="none", label="VQE")
    ax1.set_xlabel("$h$"); ax1.set_ylabel("ground energy"); ax1.legend()
    ax1.set_title("Energy")

    ax2.plot(sweep.fields, sweep.exact_order_params / num_spins, "-", lw=1.5, label="exact")
    ax2.plot(sweep.fields, sweep.vqe_order_params / num_spins, "o", ms=5, mfc="none", label="VQE")
    ax2.axvline(1.0, color="k", ls="--", lw=1, alpha=0.6)
    ax2.set_xlabel("$h$"); ax2.set_ylabel(r"$\langle|M_z|\rangle/N$"); ax2.legend()
    ax2.set_title("Order parameter")

    fig.suptitle(f"VQE vs exact — TFIM chain, N={num_spins}")
    return save_fig(fig, f"vqe_vs_exact_1x{num_spins}", out_path=out_path)


if __name__ == "__main__":
    data = load_ising("1x4")
    idx = list(range(0, data.n_fields, 5))  # every 5th field for speed
    sweep = sweep_vqe(data, indices=idx, n_layers=3, steps=200)
    path = plot_sweep(sweep, data.num_spins)
    mae = float(pnp.abs(sweep.vqe_energies - sweep.exact_energies).mean())
    print(f"wrote {path}")
    print(f"mean |E_VQE - E_exact| over sweep = {mae:.4e}")
