from __future__ import annotations

from dataclasses import replace
from typing import Optional

from aerospike.geometry import export_spike_stl, export_spike_svg, export_spike_xyz
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

        # Ambient pressure [Pa]
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

    def run_altitude_sweep(self, alt_min: float = 0.0, alt_max: float = 40000.0, steps: int = 41):
        """
        Run the solver across a range of altitudes to generate off-design performance curves
        for both the aerospike and a comparable standard bell nozzle.
        Returns altitudes [km], aerospike thrusts [N], bell thrusts [N], and aerospike Cfs.
        """
        import numpy as np
        from aerospike.flow import get_Pa_from_alt
        from aerospike.solver import solve

        altitudes = np.linspace(alt_min, alt_max, steps)
        spike_thrusts = []
        bell_thrusts = []
        cfs = []

        # Run first point to get baseline exit characteristics for the bell estimation
        baseline_res = solve(self.params, Pa=get_Pa_from_alt(alt_min))
        mdot = baseline_res.m_dot
        ve = baseline_res.Ve
        pe = baseline_res.Pe
        ae = baseline_res.Ae

        for alt in altitudes:
            Pa_pa = get_Pa_from_alt(alt)
            
            # 1. Aerospike solve (handles altitude compensation natively)
            res = solve(self.params, Pa=Pa_pa)
            spike_thrusts.append(res.F)
            cfs.append(res.Cf)

            # 2. Equivalent Bell Nozzle performance at this altitude
            # F_bell = mdot * Ve + (Pe - Pa) * Ae
            f_bell = mdot * ve + (pe - Pa_pa) * ae
            bell_thrusts.append(max(0.0, f_bell)) # Thrust cannot go negative physically in this simple model

        return altitudes / 1e3, np.array(spike_thrusts), np.array(bell_thrusts), np.array(cfs)

    def plot(self) -> None:
        """
        Plot the current solver result using matplotlib.
        """
        if self.result is None:
            return
        plot_results(self.result)

    def export_xyz(self, filename: str, samples: int = 72) -> None:
        """
        Export spike geometry to an XYZ point cloud file.
        """
        if self.result is None:
            raise RuntimeError("No solver result available for export.")

        text = export_spike_xyz(self.result, samples=samples)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

    def export_stl(self, filename: str, samples: int = 72) -> None:
        """
        Export spike geometry to a 3D ASCII STL mesh file for CAD & 3D printing.
        """
        if self.result is None:
            raise RuntimeError("No solver result available for export.")

        text = export_spike_stl(self.result, radial_samples=samples)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

    def export_svg(self, filename: str) -> None:
        """
        Export 2D spike contour to an SVG vector graphic file for laser cutting / CAD.
        """
        if self.result is None:
            raise RuntimeError("No solver result available for export.")

        text = export_spike_svg(self.result)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

    def get_thrust(self) -> float:
        return self.result.F if self.result else 0.0

    def get_cf(self) -> float:
        return self.result.Cf if self.result else 0.0

    def get_mdot(self) -> float:
        return self.result.m_dot if self.result else 0.0
