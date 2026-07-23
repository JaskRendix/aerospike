from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class EngineParameters:
    Tc: float        # Chamber temperature [K]
    Pc: float        # Chamber pressure [Pa]
    molar_m: float   # Molar mass [kg/mol]
    gamma: float     # Specific heat ratio
    Re: float        # Throat radius [m]
    er: float        # Expansion ratio (Ae/At)

    truncation: float = 1.0             # Fraction of spike length kept [0.4–1.0]
    flange_thickness: float = 0.005     # Flange extrusion thickness [m]
    flange_radius: float = 0.025        # Outer radius of mounting flange [m]
    bolt_circle_radius: float = 0.020   # Bolt-hole circle radius [m]
    bolt_count: int = 6                 # Number of bolts on the circle
    bolt_hole_radius: float = 0.002     # Radius of each bolt hole [m]

@dataclass(slots=True)
class SolverResult:
    M: np.ndarray
    Rx_over_Re: np.ndarray
    X_over_Re: np.ndarray
    P: np.ndarray
    T: np.ndarray
    Isp: np.ndarray

    F: float
    Cf: float
    m_dot: float
    At: float
    ht: float
    delta: float
    Pa: float

    params: EngineParameters | None = None
