from __future__ import annotations

from dataclasses import replace
from typing import Final

import numpy as np

from .types import EngineParameters

R_MOLAR: Final = 8.314510  # Standard molar gas constant (J/(mol*K))


def get_Mach(params: EngineParameters) -> float:
    """Compute exit Mach number Me from expansion ratio er."""
    er = params.er
    if er <= 1.0:
        return 1.0

    y = params.gamma
    k = (y - 1) / 2
    exponent = (y + 1) / (2 * (y - 1))
    c = (2 / (y + 1)) ** exponent

    Me = np.sqrt(2 / (y - 1) * ((er / c) ** ((y - 1) / exponent) - 1))
    Me = max(1.1, float(Me))

    for _ in range(20):
        term = 1 + k * Me * Me
        f = (1 / Me) * ((c * term) ** exponent) - er
        df = ((c * term) ** exponent) * ((y + 1) * k * Me * Me / term - 1) / (Me * Me)

        dM = f / df
        Me -= dM

        if abs(dM) < 1e-7:
            break

    return float(Me)


def get_Pe(params: EngineParameters) -> float:
    """Compute nozzle exit static pressure Pe."""
    Me = get_Mach(params)
    y = params.gamma
    return params.Pc * (1 + (y - 1) / 2 * Me * Me) ** (-y / (y - 1))


def get_Pa_from_alt(alt: float) -> float:
    """Return ambient pressure Pa for given altitude."""
    alt = max(0.0, alt)
    if alt <= 11000:
        return 101325.0 * (1.0 - 2.25577e-5 * alt) ** 5.25588
    elif alt <= 25000:
        return 22632.1 * np.exp(-1.57688e-4 * (alt - 11000))
    elif alt <= 44331:
        return 2488.0 * (1.0 - 1.25e-5 * (alt - 25000)) ** -34.163
    else:
        return 0.0


def get_alt_from_Pa(Pa: float) -> float:
    """Return altitude estimate from ambient pressure Pa."""
    if Pa >= 101325.0:
        return 0.0
    elif Pa >= 22632.1:
        return (1.0 - (Pa / 101325.0) ** (1 / 5.25588)) / 2.25577e-5
    elif Pa >= 2488.0:
        return 11000.0 - np.log(Pa / 22632.1) / 1.57688e-4
    elif Pa > 0.0:
        return 25000.0 + (1.0 - (Pa / 2488.0) ** (-1 / 34.163)) / 1.25e-5
    else:
        return 80000.0


def get_thrust(params: EngineParameters) -> float:
    """Compute ideal thrust from chamber pressure and geometry."""
    y = params.gamma
    Pe = get_Pe(params)

    C_F = np.sqrt(
        (2 * y * y)
        / (y - 1)
        * (2 / (y + 1)) ** ((y + 1) / (y - 1))
        * (1 - (Pe / params.Pc) ** ((y - 1) / y))
    )

    Ae = np.pi * params.Re * params.Re
    At = Ae / params.er
    return C_F * At * params.Pc


def get_Re_from_mass_flow(params: EngineParameters, m_dot: float) -> float:
    """Compute shroud radius Re from target mass flow."""
    y = params.gamma
    R = R_MOLAR / params.molar_m * 1000.0

    At = m_dot / (
        params.Pc
        * y
        * (2 / (y + 1)) ** ((y + 1) / (2 * y - 2))
        / np.sqrt(y * R * params.Tc)
    )

    Ae = At * params.er
    return float(np.sqrt(Ae / np.pi))


def get_Re_from_thrust(params: EngineParameters, F: float) -> float:
    """Compute shroud radius Re from target thrust."""
    y = params.gamma
    Pe = get_Pe(params)

    C_F = np.sqrt(
        (2 * y * y)
        / (y - 1)
        * (2 / (y + 1)) ** ((y + 1) / (y - 1))
        * (1 - (Pe / params.Pc) ** ((y - 1) / y))
    )

    At = F / (C_F * params.Pc)
    Ae = At * params.er
    return float(np.sqrt(Ae / np.pi))


def get_er_from_Pe(
    params: EngineParameters, Pe_target: float, tol: float = 1e-3, max_iter: int = 50
) -> float:
    """Compute expansion ratio er from target exit pressure Pe."""
    if Pe_target >= params.Pc:
        return 1.0

    y = params.gamma

    Me = np.sqrt(2 / (y - 1) * ((params.Pc / Pe_target) ** ((y - 1) / y) - 1))

    exponent = (y + 1) / (2 * (y - 1))
    er = (1 / Me) * ((2 / (y + 1) * (1 + (y - 1) / 2 * Me * Me)) ** exponent)

    return float(er)
