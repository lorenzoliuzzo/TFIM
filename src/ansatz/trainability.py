from __future__ import annotations

from pathlib import Path
from typing import Literal

import pennylane as qml
from pennylane import numpy as pnp

from src.core.loader import load_ising
from src.core.plotting import save_fig, setup_style
from src.ansatz.vqe_hva import _hva_circuit, extract_structure

Ansatz = Literal["hea", "hva"]


def _energy_qnode(ansatz: Ansatz, hamiltonian: qml.Hamiltonian, num_spins: int,
                  c_dtype=pnp.complex128):
    """Energy QNode for the chosen ansatz, differentiable in the parameters."""
    dev = qml.device("lightning.qubit", wires=num_spins, c_dtype=c_dtype)

    if ansatz == "hea":
        @qml.qnode(dev, interface="autograd", diff_method="adjoint")
        def energy(params: pnp.ndarray) -> float:
            qml.StronglyEntanglingLayers(params, wires=range(num_spins))
            return qml.expval(hamiltonian)
        return energy

    if ansatz == "hva":
        bonds, field_wires = extract_structure(hamiltonian)

        @qml.qnode(dev, interface="autograd", diff_method="adjoint")
        def energy(params: pnp.ndarray) -> float:
            _hva_circuit(params, bonds, field_wires, num_spins)
            return qml.expval(hamiltonian)
        return energy

    raise ValueError(f"unknown ansatz {ansatz!r}")


def _random_params(ansatz: Ansatz, num_spins: int, n_layers: int, rng) -> pnp.ndarray:
    if ansatz == "hea":
        shape = qml.StronglyEntanglingLayers.shape(n_layers=n_layers, n_wires=num_spins)
    else:
        shape = (n_layers, 2)
    return pnp.array(rng.uniform(0.0, 2 * pnp.pi, size=shape), requires_grad=True)


def gradient_variance(
    ansatz: Ansatz,
    num_spins: int,
    hamiltonian: qml.Hamiltonian,
    *,
    n_layers: int = 4,
    n_samples: int = 40,
    seed: int = 0,
    c_dtype=pnp.complex128,
) -> float:
    """Variance of the energy gradient, averaged over components, over random inits.

    The barren-plateau diagnostic: if this variance shrinks (exponentially) with
    `num_spins`, the landscape is flat and the ansatz is hard to train. Averaging
    over components (rather than probing one fixed angle) makes the diagnostic
    robust to which parameter happens to sit at a given index.
    """
    energy = _energy_qnode(ansatz, hamiltonian, num_spins, c_dtype=c_dtype)
    grad_fn = qml.grad(energy)
    rng = pnp.random.default_rng(seed)

    grads: list[pnp.ndarray] = []
    for _ in range(n_samples):
        params = _random_params(ansatz, num_spins, n_layers, rng)
        grads.append(pnp.asarray(grad_fn(params)).flatten())
    grads_arr = pnp.array(grads)
    variances = pnp.var(grads_arr, axis=0)
    if ansatz == "hea":
        # HEA's first angle is a leading RZ on |0>, an unobservable global phase
        # whose gradient is identically zero; exclude it from the average. The
        # HVA's first angle is a genuine ZZ rotation with a nonzero (in fact the
        # largest) gradient component, so it must be kept.
        variances = variances[pnp.arange(variances.shape[0]) != 0]
    return float(pnp.mean(variances))


def plot_barren_plateaus(
    layouts: tuple[str, ...] = ("1x4", "1x8", "1x16"),
    ansatze: tuple[Ansatz, ...] = ("hea", "hva"),
    *,
    n_layers: int = 4,
    n_samples: int = 40,
    field_index: int = 50,
    out_path: Path | None = None,
) -> Path:
    """Gradient variance vs system size, one line per ansatz (log scale)."""
    setup_style()
    import matplotlib.pyplot as plt

    labels = {"hea": "StronglyEntangling (HEA)", "hva": "HVA / QAOA"}
    fig, ax = plt.subplots(figsize=(7, 5))
    for ansatz in ansatze:
        ns, vs = [], []
        for layout in layouts:
            data = load_ising(layout)
            v = gradient_variance(ansatz, data.num_spins, data.hamiltonians[field_index],
                                  n_layers=n_layers, n_samples=n_samples)
            ns.append(data.num_spins)
            vs.append(v)
        ax.semilogy(ns, vs, "o-", label=labels[ansatz])
    ax.set_xlabel("number of spins $N$")
    ax.set_ylabel("Var$[\\partial_\\theta \\langle H \\rangle]$")
    ax.set_title("Barren plateaus: gradient variance vs system size")
    ax.legend()
    return save_fig(fig, "barren_plateaus", out_path=out_path)


if __name__ == "__main__":
    path = plot_barren_plateaus(n_layers=4, n_samples=50)
    print(f"wrote {path}")
    for ansatz in ("hea", "hva"):
        print(f"\n{ansatz}: gradient variance vs N")
        for layout in ("1x4", "1x8", "1x16"):
            d = load_ising(layout)
            v = gradient_variance(ansatz, d.num_spins, d.hamiltonians[50], n_layers=4, n_samples=50)
            print(f"  N={d.num_spins:2d}: Var = {v:.4e}")
