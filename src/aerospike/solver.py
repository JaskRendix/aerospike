from __future__ import annotations

from math import atan, pi, sin

import numpy as np

from .flow import R_MOLAR, get_Mach
from .types import EngineParameters, SolverResult


def solve(params: EngineParameters, Pa: float) -> SolverResult:
    """Modernized aerospike nozzle solver (pure function)."""

    y = params.gamma
    R = R_MOLAR / params.molar_m * 1000.0

    # Exit Mach
    Me = get_Mach(params)

    # Exit pressure
    Pe = params.Pc * (1 + (y - 1) / 2 * Me * Me) ** (-y / (y - 1))

    # Total turning angle
    nu_e = ((y + 1) / (y - 1)) ** 0.5 * atan(
        ((y - 1) / (y + 1) * (Me * Me - 1)) ** 0.5
    ) - atan((Me * Me - 1) ** 0.5)

    delta = pi / 2 - nu_e

    # Throat gap ratio
    htRe = (params.er - (params.er * (params.er - sin(delta))) ** 0.5) / (
        params.er * sin(delta)
    )

    # Throat conditions (M=1)
    Tt = params.Tc / (1 + (y - 1) / 2)
    Pt = params.Pc * (1 + (y - 1) / 2) ** (-y / (y - 1))
    vt = (y * R * Tt) ** 0.5

    # Mach distribution
    N = 10000
    M = np.linspace(1.0, Me, N)

    mu = np.arcsin(1.0 / M)

    nu = ((y + 1) / (y - 1)) ** 0.5 * np.arctan(
        ((y - 1) / (y + 1) * (M * M - 1)) ** 0.5
    ) - np.arctan((M * M - 1) ** 0.5)

    phi = nu_e - nu + mu

    term = (2 / (y + 1) * (1 + (y - 1) / 2 * M * M)) ** ((y + 1) / (2 * y - 2))

    Rx_over_Re = np.sqrt(np.maximum(0.0, 1.0 - term * np.sin(phi) / params.er))

    X_over_Re = (1.0 - Rx_over_Re) / np.tan(phi)

    P = params.Pc * (1 + (y - 1) / 2 * M * M) ** (-y / (y - 1))

    # Cumulative Isp
    Isp = np.zeros_like(M)
    Isp[0] = (
        vt
        * sin(delta)
        * (1 + 1 / y * (1 - ((y + 1) / 2) ** (y / (y - 1)) * Pa / params.Pc))
        / 9.81
    )

    for i in range(1, N):
        Isp[i] = (
            Isp[i - 1]
            + (
                vt
                / y
                * ((y + 1) / 2) ** (y / (y - 1))
                * params.er
                / 2
                * ((P[i - 1] - Pa) / params.Pc + (P[i] - Pa) / params.Pc)
                * (Rx_over_Re[i - 1] ** 2 - Rx_over_Re[i] ** 2)
            )
            / 9.81
        )

    # Throat geometry
    ht = htRe * params.Re
    At = pi * ht * (2 * params.Re - ht * sin(delta))

    rho_t = Pt / (R * Tt)
    m_dot = rho_t * At * vt

    F = Isp[-1] * m_dot * 9.81
    Cf = F / (params.Pc * At)

    return SolverResult(
        M=M,
        Rx_over_Re=Rx_over_Re,
        X_over_Re=X_over_Re,
        P=P,
        T=params.Tc / (1 + (y - 1) / 2 * M * M),
        Isp=Isp,
        F=F,
        Cf=Cf,
        m_dot=m_dot,
        At=At,
        ht=ht,
        delta=delta,
        Pa=Pa,
    )
