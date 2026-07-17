from __future__ import annotations

from pathlib import Path

from src.loader import IsingData, load_ising
from src.plotting import save_fig, setup_style
from src.vqe import run_vqe
from src.vqe_hva import run_qaoa, run_vqe_hva


def energy_error_trajectories(
    data: IsingData,
    *,
    field_index: int,
    n_layers: int = 4,
    steps: int = 200,
    seed: int = 0,
) -> dict[str, list[float]]:
    """Per-step |E - E_exact| for HEA, HVA (random init), and QAOA (anneal init)
    at a single field, so the optimization trajectories can be compared directly
    rather than just their endpoints.
    """
    hamiltonian = data.hamiltonians[field_index]
    exact = float(data.ground_energies[field_index])

    hea = run_vqe(hamiltonian, data.num_spins, n_layers=n_layers, steps=steps, seed=seed)
    hva = run_vqe_hva(hamiltonian, data.num_spins, n_layers=n_layers, steps=steps,
                      init_strategy="random", seed=seed)
    qaoa = run_qaoa(hamiltonian, data.num_spins, n_layers=n_layers, steps=steps, seed=seed)

    return {
        "HEA": [abs(e - exact) for e in hea.history],
        "HVA": [abs(e - exact) for e in hva.history],
        "QAOA": [abs(e - exact) for e in qaoa.history],
    }


def plot_optimizer_trajectories(
    layout: str = "1x8",
    *,
    n_layers: int = 4,
    steps: int = 200,
    field_frac: float = 0.3,
    out_path: Path | None = None,
) -> Path:
    """Energy error vs Adam step, one curve per ansatz, at a field inside the
    ordered phase (the hard region where HEA struggles most).
    """
    setup_style()
    data = load_ising(layout)
    field_index = int(field_frac * (data.n_fields - 1))
    trajectories = energy_error_trajectories(data, field_index=field_index,
                                             n_layers=n_layers, steps=steps)

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    for label, errors in trajectories.items():
        ax.semilogy(range(1, len(errors) + 1), errors, label=label)
    ax.set_xlabel("Adam step")
    ax.set_ylabel(r"$|E_{\mathrm{VQE}} - E_0|$")
    ax.set_title(f"Optimizer trajectories, N={data.num_spins}, h={data.fields[field_index]:.2f}")
    ax.legend()
    return save_fig(fig, "optimizer_trajectories", out_path=out_path)


if __name__ == "__main__":
    path = plot_optimizer_trajectories()
    print(f"wrote {path}")
