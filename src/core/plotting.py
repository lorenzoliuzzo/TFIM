from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

PLOTS_DIR = Path(__file__).resolve().parent.parent.parent / "plots"

# Fixed N -> color map so a given system size reads the same across every figure.
N_COLORS: dict[int, str] = {
    4: "#1f77b4",
    8: "#d62728",
    16: "#2ca02c",
}

# Colorblind-safe cycle (Wong) for everything not keyed by N.
_CYCLE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000"]


def setup_style() -> None:
    """Apply the project-wide matplotlib style. Call once before building a figure."""
    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "font.size": 12,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "axes.prop_cycle": mpl.cycler(color=_CYCLE),
        "lines.linewidth": 1.6,
    })


def color_for_n(num_spins: int) -> str:
    """Color assigned to a given system size N (stable across all figures)."""
    return N_COLORS.get(num_spins, "#444444")


def save_fig(fig: plt.Figure, name: str, *, out_path: Path | None = None) -> Path:
    """Save a figure into PLOTS_DIR/<name>.png (or out_path) and close it."""
    out_path = out_path or PLOTS_DIR / f"{name}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    plt.close(fig)
    return out_path
