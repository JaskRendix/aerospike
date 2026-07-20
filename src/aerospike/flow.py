from __future__ import annotations

from dataclasses import replace
from typing import Final

import numpy as np

from .types import EngineParameters

R_MOLAR: Final = 8.314


def get_Mach(params: EngineParameters) -> float:
    """Explicit inversion of Stodola’s Area–Mach equation."""
    n = 5
    X = np.zeros(n)
    M = np.zeros(n)

    e = 1.0 / params.er
    y = params.gamma
    B = (y + 1) / (y - 1)
    k = (0.5 * (y - 1)) ** 0.5
    u = e ** (1 / B) / (1 + k * k) ** 0.5

    X[0] = (u * k) ** (B / (1 - B))
    M[0] = X[0]

    for i in range(1, n):
        lamb = 1 / (
            2 * M[i - 1] ** (2 / B) * (B - 2) + M[i - 1] ** 2 * B * B * k * k * u * u
        )

        X[i] = (
            lamb
            * M[i - 1]
            * B
            * (
                M[i - 1] ** (2 / B)
                - M[i - 1] ** 2 * B * k * k * u * u
                + (
                    M[i - 1] ** (2 + 2 / B) * k * k * u * u * (B * B - 4 * B + 4)
                    - M[i - 1] ** 2 * B * B * k * k * u**4
                    + M[i - 1] ** (4 / B) * (2 * B - 3)
                    + 2 * M[i - 1] ** (2 / B) * u * u * (2 - B)
                )
                ** 0.5
            )
        )

        M[i] = M[i - 1] + X[i]

    return float(np.real(M[-1]))


def get_Pe(params: EngineParameters) -> float:
    Me = get_Mach(params)
    y = params.gamma
    return params.Pc * (1 + (y - 1) / 2 * Me * Me) ** (-y / (y - 1))


def get_Pa_from_alt(alt: float) -> float:
    if alt < 44331:
        return 100 * ((44331.514 - alt) / 11880.516) ** (1 / 0.1902632)
    return 0.0


def get_alt_from_Pa(Pa: float) -> float:
    if Pa > 0:
        return 44331.5 - 4946.62 * Pa**0.190263
    return 0.0


def get_thrust(params: EngineParameters) -> float:
    y = params.gamma
    Pe = get_Pe(params)

    C_F = (
        (2 * y * y)
        / (y - 1)
        * (2 / (y + 1)) ** ((y + 1) / (y - 1))
        * (1 - (Pe / params.Pc) ** ((y - 1) / y))
    ) ** 0.5

    Ae = np.pi * params.Re * params.Re
    At = Ae / params.er
    return C_F * At * params.Pc


def get_Re_from_mass_flow(params: EngineParameters, m_dot: float) -> float:
    """
    Compute shroud radius from desired mass flow.
    Based on Rocket Propulsion Elements Eq. 3-24.
    """
    y = params.gamma
    R = R_MOLAR / params.molar_m * 1000.0

    At = m_dot / (
        params.Pc
        * y
        * (2 / (y + 1)) ** ((y + 1) / (2 * y - 2))
        / (y * R * params.Tc) ** 0.5
    )

    Ae = At * params.er
    Re = (Ae / np.pi) ** 0.5
    return float(Re)


def get_Re_from_thrust(params: EngineParameters, F: float) -> float:
    """
    Compute shroud radius from desired thrust.
    Based on Rocket Propulsion Elements Eq. 3-30.
    """
    y = params.gamma
    Pe = get_Pe(params)

    C_F = (
        (2 * y * y)
        / (y - 1)
        * (2 / (y + 1)) ** ((y + 1) / (y - 1))
        * (1 - (Pe / params.Pc) ** ((y - 1) / y))
    ) ** 0.5

    At = F / (C_F * params.Pc)
    Ae = At * params.er
    Re = (Ae / np.pi) ** 0.5
    return float(Re)


def get_er_from_Pe(
    params: EngineParameters, Pe_target: float, tol: float = 1e-3, max_iter: int = 50
) -> float:
    """
    Compute expansion ratio er such that exit pressure Pe matches Pe_target.
    Uses monotonic bisection because Pe(er) is strictly decreasing.

    Parameters
    ----------
    params : EngineParameters
        Current engine parameters (er will be replaced during iteration).
    Pe_target : float
        Desired exit pressure [Pa].
    tol : float
        Absolute tolerance on Pe.
    max_iter : int
        Maximum number of bisection iterations.

    Returns
    -------
    float
        Expansion ratio er that yields Pe ≈ Pe_target.
    """
    # Reasonable bounds for typical aerospike designs
    er_low = 1.0
    er_high = 200.0

    for _ in range(max_iter):
        er_mid = 0.5 * (er_low + er_high)
        params_mid = replace(params, er=er_mid)
        Pe_mid = get_Pe(params_mid)

        if abs(Pe_mid - Pe_target) < tol:
            return er_mid

        # Pe decreases as er increases
        if Pe_mid > Pe_target:
            er_low = er_mid
        else:
            er_high = er_mid

    return er_mid
