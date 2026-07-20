from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from .types import SolverResult


def plot_results_gui(result: SolverResult, ax: Axes) -> None:
    """
    Plot aerospike flow + geometry into the provided Matplotlib axis.
    Designed for PySide6 embedding (no plt.show(), no new figure).
    """

    ax.clear()

    ax.plot(result.X_over_Re, result.Rx_over_Re, label="R_x / R_e")
    ax.plot(result.X_over_Re, result.P / 1e6, label="Pressure [MPa]")
    ax.plot(result.X_over_Re, result.Isp, label="Isp [s]")
    ax.plot(result.X_over_Re, result.M, label="Mach")
    ax.plot(result.X_over_Re, result.T, label="Temperature [K]")

    ax.set_xlabel("X / R_e")
    ax.set_ylabel("Value")
    ax.set_title("Aerospike Flow & Geometry")
    ax.grid(True)
    ax.legend()


def plot_results(result: SolverResult) -> None:
    """
    Standalone plotting version used by tests.
    Creates a 2x3 grid of subplots and calls plt.show().
    """

    fig, axes = plt.subplots(2, 3, figsize=(10, 6))
    ax_r, ax_p, ax_i, ax_m, ax_t, ax_txt = axes.flatten()

    ax_r.plot(result.X_over_Re, result.Rx_over_Re)
    ax_r.set_ylabel("R_x / R_e")

    ax_p.plot(result.X_over_Re, result.P / 1e6)
    ax_p.set_ylabel("Pressure [MPa]")

    ax_i.plot(result.X_over_Re, result.Isp)
    ax_i.set_ylabel("Isp [s]")

    ax_m.plot(result.X_over_Re, result.M)
    ax_m.set_ylabel("Mach")

    ax_t.plot(result.X_over_Re, result.T)
    ax_t.set_ylabel("Temperature [K]")

    ax_txt.text(0.1, 0.8, f"er = {result.At:.2f}")

    fig.tight_layout()
    plt.show()
