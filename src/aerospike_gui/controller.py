from __future__ import annotations

from dataclasses import replace
from typing import Optional

from aerospike.geometry import export_spike_xyz
from aerospike.plotting import plot_results
from aerospike.solver import solve
from aerospike.types import EngineParameters, SolverResult


class Controller:
    """
    Central application logic for the PySide6 GUI.
    Keeps state, runs the solver, updates results, and handles exports.
    """

    def __init__(self) -> None:
        # Default engine parameters
        self.params = EngineParameters(
            Tc=1900.0,
            Pc=5e6,
            molar_m=20.18,
            gamma=1.27,
            Re=0.015,
            er=12.0,
        )

        # Ambient pressure
        self.Pa: float = 57e3

        # Last solver result
        self.result: Optional[SolverResult] = None

    def update_param(self, **kwargs) -> None:
        """
        Update EngineParameters using dataclasses.replace().
        Example: controller.update_param(Tc=2100)
        """
        self.params = replace(self.params, **kwargs)

    def update_ambient_pressure(self, Pa_kPa: float) -> None:
        """
        Update ambient pressure from GUI (kPa → Pa).
        """
        self.Pa = Pa_kPa * 1e3

    def run_solver(self) -> SolverResult:
        """
        Run the aerospike solver with current parameters.
        Stores and returns the SolverResult.
        """
        self.result = solve(self.params, Pa=self.Pa)
        return self.result

    def plot(self) -> None:
        """
        Plot the current solver result using matplotlib.
        """
        if self.result is None:
            return
        plot_results(self.result)

    def export_xyz(self, filename: str, samples: int = 360) -> None:
        """
        Export spike geometry to an XYZ file.
        """
        if self.result is None:
            raise RuntimeError("No solver result available for export.")

        text = export_spike_xyz(self.result, samples=samples)

        with open(filename, "w") as f:
            f.write(text)

    def get_thrust(self) -> float:
        return self.result.F if self.result else 0.0

    def get_cf(self) -> float:
        return self.result.Cf if self.result else 0.0

    def get_mdot(self) -> float:
        return self.result.m_dot if self.result else 0.0
