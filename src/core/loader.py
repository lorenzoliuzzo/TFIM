from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pennylane as qml

Periodicity = Literal["open", "closed"]
Lattice = Literal["chain", "rectangular"]

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

# Valid (lattice, layout) combinations in the qspin Ising dataset.
VALID_LAYOUTS: dict[Lattice, tuple[str, ...]] = {
    "chain": ("1x4", "1x8", "1x16"),
    "rectangular": ("2x2", "2x4", "2x8", "4x4"),
}


@dataclass(frozen=True)
class IsingData:
    """A single qspin Ising datapoint with the transverse field swept over `h`."""

    periodicity: Periodicity
    lattice: Lattice
    layout: str
    num_spins: int
    fields: np.ndarray  # transverse field values h, shape (n_fields,)
    hamiltonians: list[qml.Hamiltonian]
    ground_energies: np.ndarray  # shape (n_fields,)
    ground_states: list[np.ndarray]  # each shape (2**num_spins,)
    order_params: np.ndarray  # <|M_z|>, shape (n_fields,)
    shadow_basis: np.ndarray  # int8, shape (n_fields, n_shots, num_spins); 0/1/2 = X/Y/Z
    shadow_meas: np.ndarray  # int8, shape (n_fields, n_shots, num_spins); +-1 measurement outcome bit

    @property
    def n_fields(self) -> int:
        return len(self.fields)


def _num_spins(layout: str) -> int:
    rows, cols = (int(x) for x in layout.split("x"))
    return rows * cols


def load_ising(
    layout: str = "1x4",
    *,
    lattice: Lattice = "chain",
    periodicity: Periodicity = "open",
    folder_path: Path | str = DATA_DIR,
) -> IsingData:
    """Load one transverse-field Ising datapoint from PennyLane's qspin dataset.

    Downloads to `folder_path` (cached) on first use.
    """
    if lattice not in VALID_LAYOUTS:
        raise ValueError(f"lattice must be one of {tuple(VALID_LAYOUTS)}, got {lattice!r}")
    if layout not in VALID_LAYOUTS[lattice]:
        raise ValueError(
            f"layout {layout!r} invalid for lattice {lattice!r}; "
            f"valid: {VALID_LAYOUTS[lattice]}"
        )

    ds = qml.data.load(
        "qspin",
        sysname="Ising",
        periodicity=periodicity,
        lattice=lattice,
        layout=layout,
        folder_path=str(folder_path),
    )[0]

    fields = np.asarray(ds.parameters["h"], dtype=float)
    return IsingData(
        periodicity=periodicity,
        lattice=lattice,
        layout=layout,
        num_spins=_num_spins(layout),
        fields=fields,
        hamiltonians=list(ds.hamiltonians),
        ground_energies=np.asarray(ds.ground_energies).real.astype(float),
        ground_states=[np.asarray(s) for s in ds.ground_states],
        order_params=np.asarray(ds.order_params).real,
        shadow_basis=np.asarray(ds.shadow_basis),
        shadow_meas=np.asarray(ds.shadow_meas),
    )
