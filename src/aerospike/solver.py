from __future__ import annotations

from math import atan, pi, sin
import numpy as np

from .flow import R_MOLAR, get_Mach
from .types import EngineParameters, SolverResult

G0 = 9.80665  # Standard gravity


def solve(params: EngineParameters, Pa: float) -> SolverResult:
    y = params.gamma
    R = R_MOLAR / params.molar_m * 1000.0

    Me = get_Mach(params)

    Pe = params.Pc * (1 + (y - 1) / 2 * Me * Me) ** (-y / (y - 1))

    nu_e = ((y + 1) / (y - 1)) ** 0.5 * atan(
        ((y - 1) / (y + 1) * (Me * Me - 1)) ** 0.5
    ) - atan((Me * Me - 1) ** 0.5)

    delta = pi / 2 - nu_e

    htRe = (params.er - (params.er * (params.er - sin(delta))) ** 0.5) / (
        params.er * sin(delta)
    )

    Tt = params.Tc / (1 + (y - 1) / 2)
    Pt = params.Pc * (1 + (y - 1) / 2) ** (-y / (y - 1))
    vt = (y * R * Tt) ** 0.5

    N = 10000
    M = np.linspace(1.0, Me, N)

    mu = np.arcsin(1.0 / M)
    nu = ((y + 1) / (y - 1)) ** 0.5 * np.arctan(
        ((y - 1) / (y + 1) * (M * M - 1)) ** 0.5
    ) - np.arctan((M * M - 1) ** 0.5)

    phi = nu_e - nu + mu

    term = (2 / (y + 1) * (1 + (y - 1) / 2 * M * M)) ** ((y + 1) / (2 * y - 2))
    Rx_over_Re = np.sqrt(np.maximum(0.0, 1.0 - term * np.sin(phi) / params.er))

    with np.errstate(divide="ignore", invalid="ignore"):
        X_over_Re = np.where(
            np.isclose(np.tan(phi), 0.0), 0.0, (1.0 - Rx_over_Re) / np.tan(phi)
        )

    P = params.Pc * (1 + (y - 1) / 2 * M * M) ** (-y / (y - 1))

    d_Isp = (
        vt
        / y
        * ((y + 1) / 2) ** (y / (y - 1))
        * params.er
        / 2
        * ((P[:-1] - Pa) / params.Pc + (P[1:] - Pa) / params.Pc)
        * (Rx_over_Re[:-1] ** 2 - Rx_over_Re[1:] ** 2)
    ) / G0

    Isp0 = (
        vt
        * sin(delta)
        * (1 + 1 / y * (1 - ((y + 1) / 2) ** (y / (y - 1)) * Pa / params.Pc))
        / G0
    )

    Isp = np.empty_like(M)
    Isp[0] = Isp0
    Isp[1:] = Isp0 + np.cumsum(d_Isp)

    ht = htRe * params.Re
    At = pi * ht * (2 * params.Re - ht * sin(delta))

    rho_t = Pt / (R * Tt)
    m_dot = rho_t * At * vt

    F = Isp[-1] * m_dot * G0
    Cf = F / (params.Pc * At)

    res = SolverResult(
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
        params=params,
    )

    # --- Truncation base drag correction ---
    if params.truncation < 1.0:
        x_full = res.X_over_Re
        idx = np.searchsorted(x_full, x_full[-1] * params.truncation)
        idx = min(max(idx, 0), len(x_full) - 1)

        Re = params.Re
        r_base = res.Rx_over_Re[idx] * Re
        A_base = np.pi * (r_base ** 2)

        delta_p = max(0.0, params.Pc - Pa)
        base_drag = 0.5 * delta_p * A_base

        F_corr = max(0.0, res.F - base_drag)
        Cf_corr = F_corr / (res.m_dot * (res.F / res.Cf) / res.m_dot) if res.Cf > 0 else res.Cf

        object.__setattr__(res, "F", F_corr)
        object.__setattr__(res, "Cf", Cf_corr)

    return res
