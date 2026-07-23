import numpy as np
import pytest
from aerospike.flow import (
    get_alt_from_Pa,
    get_er_from_Pe,
    get_Mach,
    get_Pa_from_alt,
    get_Pe,
    get_Re_from_mass_flow,
    get_Re_from_thrust,
    get_thrust,
)
from aerospike.types import EngineParameters


@pytest.fixture
def params() -> EngineParameters:
    return EngineParameters(
        Tc=1900,
        Pc=5e6,
        molar_m=20.18,
        gamma=1.27,
        Re=0.015,
        er=12,
    )


@pytest.mark.parametrize(
    "er,expected",
    [
        (12, 4.4611),
        (8, 4.1082),
        (20, 4.8812),
    ],
)
def test_get_Mach_parametrized(er: float, expected: float, params: EngineParameters):
    p = EngineParameters(
        Tc=params.Tc,
        Pc=params.Pc,
        molar_m=params.molar_m,
        gamma=params.gamma,
        Re=params.Re,
        er=er,
    )
    Me = get_Mach(p)
    assert Me == pytest.approx(expected, rel=1e-3)


def test_get_Pe_basic(params: EngineParameters):
    Pe = get_Pe(params)
    assert Pe == pytest.approx(10806.39, rel=1e-2)


@pytest.mark.parametrize(
    "Pc,er",
    [
        (3e6, 12),
        (5e6, 20),
        (1e6, 8),
    ],
)
def test_get_Pe_parametrized(Pc: float, er: float, params: EngineParameters):
    p = EngineParameters(
        Tc=params.Tc,
        Pc=Pc,
        molar_m=params.molar_m,
        gamma=params.gamma,
        Re=params.Re,
        er=er,
    )
    Pe = get_Pe(p)
    assert Pe > 0
    assert np.isfinite(Pe)


@pytest.mark.parametrize("Pa", [101e3, 50e3, 25e3, 10e3, 1e3])
def test_altitude_roundtrip(Pa: float):
    alt = get_alt_from_Pa(Pa)
    Pa2 = get_Pa_from_alt(alt)
    assert Pa2 == pytest.approx(Pa, rel=1e-2)


def test_altitude_negative():
    assert get_alt_from_Pa(-100) == 0.0


def test_pressure_high_alt():
    assert get_Pa_from_alt(50000) == 0.0


def test_get_thrust_basic(params: EngineParameters):
    F = get_thrust(params)
    assert F > 0
    assert np.isfinite(F)


@pytest.mark.parametrize("Pc", [1e6, 3e6, 5e6, 8e6])
def test_get_thrust_parametrized(Pc: float, params: EngineParameters):
    p = EngineParameters(
        Tc=params.Tc,
        Pc=Pc,
        molar_m=params.molar_m,
        gamma=params.gamma,
        Re=params.Re,
        er=params.er,
    )
    F = get_thrust(p)
    assert F > 0


def test_get_Re_from_mass_flow(params: EngineParameters):
    Re = get_Re_from_mass_flow(params, 0.2196)
    assert Re == pytest.approx(0.0150, abs=3e-05)


@pytest.mark.parametrize("m_dot", [0.05, 0.1, 0.2, 0.5])
def test_get_Re_from_mass_flow_parametrized(m_dot: float, params: EngineParameters):
    Re = get_Re_from_mass_flow(params, m_dot)
    assert Re > 0
    assert np.isfinite(Re)


def test_get_Re_from_thrust(params: EngineParameters):
    Re = get_Re_from_thrust(params, 470)
    assert Re == pytest.approx(0.0150, rel=5e-2)


@pytest.mark.parametrize("F", [100, 300, 500, 800])
def test_get_Re_from_thrust_parametrized(F: float, params: EngineParameters):
    Re = get_Re_from_thrust(params, F)
    assert Re > 0
    assert np.isfinite(Re)


@pytest.mark.parametrize(
    "er",
    [5, 8, 12, 20, 30],
)
def test_get_er_from_Pe_roundtrip(er: float, params: EngineParameters):
    """
    For a given expansion ratio er, compute Pe, then invert it using
    get_er_from_Pe(). The result should match the original er within tolerance.
    """
    p = EngineParameters(
        Tc=params.Tc,
        Pc=params.Pc,
        molar_m=params.molar_m,
        gamma=params.gamma,
        Re=params.Re,
        er=er,
    )

    Pe = get_Pe(p)
    er2 = get_er_from_Pe(params, Pe)

    assert er2 == pytest.approx(er, rel=1e-2)


@pytest.mark.parametrize(
    "Pe_target",
    [5e4, 3e4, 2e4, 1e4],
)
def test_get_er_from_Pe_basic(Pe_target: float, params: EngineParameters):
    """
    Basic sanity check: returned er must be positive and finite.
    """
    er = get_er_from_Pe(params, Pe_target)
    assert er > 0
    assert np.isfinite(er)


def test_get_er_from_Pe_monotonicity(params: EngineParameters):
    """
    Larger er should produce lower Pe. Verify monotonic behavior.
    """
    er_small = 5
    er_large = 20

    p_small = EngineParameters(
        Tc=params.Tc,
        Pc=params.Pc,
        molar_m=params.molar_m,
        gamma=params.gamma,
        Re=params.Re,
        er=er_small,
    )
    p_large = EngineParameters(
        Tc=params.Tc,
        Pc=params.Pc,
        molar_m=params.molar_m,
        gamma=params.gamma,
        Re=params.Re,
        er=er_large,
    )

    Pe_small = get_Pe(p_small)
    Pe_large = get_Pe(p_large)

    assert Pe_large < Pe_small
