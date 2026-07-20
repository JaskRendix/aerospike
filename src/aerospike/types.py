from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class EngineParameters:
    Tc: float
    Pc: float
    molar_m: float
    gamma: float
    Re: float
    er: float


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
