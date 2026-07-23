from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np

from .types import SolverResult


def plot_results_gui(result: SolverResult, ax: Axes) -> None:
    """Render 2D aerospike geometry and pressure profile in GUI axis."""
    ax.clear()

    # Exact outer radius from throat geometry
    Re = (result.At + np.pi * result.ht**2 * np.sin(result.delta)) / (
        2.0 * np.pi * result.ht
    )

    x_mm = result.X_over_Re * Re * 1000.0
    r_mm = result.Rx_over_Re * Re * 1000.0
    Re_mm = Re * 1000.0

    # Geometry: spike contour + symmetric lower half
    (line1,) = ax.plot(x_mm, r_mm, "b-", linewidth=2, label="Spike Contour")
    ax.plot(x_mm, -r_mm, "b-", linewidth=2)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5, label="Centerline")

    # Cowl / shroud throat gap
    ax.plot([0, 0], [Re_mm, r_mm[0]], "k-", linewidth=3, label="Cowl / Throat Gap")
    ax.plot([0, 0], [-Re_mm, -r_mm[0]], "k-", linewidth=3)

    ax.set_xlabel("Axial Position X [mm]")
    ax.set_ylabel("Radial Radius R [mm]", color="b")
    ax.tick_params(axis="y", labelcolor="b")
    ax.set_title("Aerospike Nozzle Geometry & Pressure Profile")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_aspect("equal", adjustable="datalim")

    # Pressure on second axis
    ax2 = ax.twinx()
    (line2,) = ax2.plot(x_mm, result.P / 1e6, "r--", linewidth=1.5, label="Pressure [MPa]")
    ax2.set_ylabel("Static Pressure P [MPa]", color="r")
    ax2.tick_params(axis="y", labelcolor="r")

    ax.legend([line1, line2], ["Spike Contour", "Pressure [MPa]"], loc="upper right")


def plot_results(result: SolverResult) -> None:
    """Render full 2×3 analysis plot with performance summary."""
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    ax_r, ax_p, ax_i, ax_m, ax_t, ax_txt = axes.flatten()

    ax_r.plot(result.X_over_Re, result.Rx_over_Re, "b-")
    ax_r.set_ylabel("R_x / R_e")
    ax_r.set_xlabel("X / R_e")
    ax_r.grid(True)

    ax_p.plot(result.X_over_Re, result.P / 1e6, "r-")
    ax_p.set_ylabel("Pressure [MPa]")
    ax_p.set_xlabel("X / R_e")
    ax_p.grid(True)

    ax_i.plot(result.X_over_Re, result.Isp, "g-")
    ax_i.set_ylabel("Isp [s]")
    ax_i.set_xlabel("X / R_e")
    ax_i.grid(True)

    ax_m.plot(result.X_over_Re, result.M, "m-")
    ax_m.set_ylabel("Mach Number")
    ax_m.set_xlabel("X / R_e")
    ax_m.grid(True)

    ax_t.plot(result.X_over_Re, result.T, "c-")
    ax_t.set_ylabel("Temperature [K]")
    ax_t.set_xlabel("X / R_e")
    ax_t.grid(True)

    # Summary card
    ax_txt.axis("off")
    summary = (
        f"--- Performance Summary ---\n"
        f"Thrust (F): {result.F/1000:.2f} kN\n"
        f"Vacuum Isp: {result.Isp[-1]:.1f} s\n"
        f"Mass Flow (ṁ): {result.m_dot:.3f} kg/s\n"
        f"Thrust Coeff C_f: {result.Cf:.3f}\n"
        f"Throat Gap (h_t): {result.ht*1000:.2f} mm\n"
        f"Throat Area (A_t): {result.At*1e4:.2f} cm²\n"
        f"Exit Angle (δ): {np.degrees(result.delta):.2f}°"
    )
    ax_txt.text(0.05, 0.5, summary, fontsize=10, family="monospace", va="center")

    fig.tight_layout()
    plt.show()
