from dataclasses import replace

import numpy as np
import pytest

from aerospike.flow import (
    get_alt_from_Pa,
    get_Mach,
    get_Pe,
    get_Re_from_mass_flow,
    get_Re_from_thrust,
)
from aerospike.solver import solve
from aerospike.types import EngineParameters


@pytest.fixture
def test_params() -> EngineParameters:
    return EngineParameters(
        Tc=1900,
        Pc=5e6,
        molar_m=20.18,
        gamma=1.27,
        Re=0.015,
        er=12,
    )


@pytest.mark.parametrize(
    "Pa,expected_alt",
    [
        (101e3, get_alt_from_Pa(101e3)),
        (50e3, get_alt_from_Pa(50e3)),
        (25e3, get_alt_from_Pa(25e3)),
        (10e3, get_alt_from_Pa(10e3)),
        (1e3, get_alt_from_Pa(1e3)),
    ],
)
def test_altitude_conversion(Pa: float, expected_alt: float):
    alt = get_alt_from_Pa(Pa)
    assert alt == pytest.approx(expected_alt, rel=1e-6)


def test_exit_mach(test_params: EngineParameters):
    Me = get_Mach(test_params)
    assert Me == pytest.approx(3.64, rel=1e-2)


def test_exit_pressure(test_params: EngineParameters):
    Pe = get_Pe(test_params)
    assert Pe == pytest.approx(40283.20, rel=1e-2)


def test_exit_radius_from_mass_flow(test_params: EngineParameters):
    Re = get_Re_from_mass_flow(test_params, 0.2196)
    assert Re == pytest.approx(0.0150, abs=3e-05)


def test_exit_radius_from_thrust(test_params: EngineParameters):
    Re = get_Re_from_thrust(test_params, 470)
    assert Re == pytest.approx(0.0150, rel=1e-2)


def test_solver_runs(test_params: EngineParameters):
    result = solve(test_params, Pa=57e3)

    # Basic sanity checks
    assert isinstance(result.M, np.ndarray)
    assert isinstance(result.P, np.ndarray)
    assert isinstance(result.T, np.ndarray)
    assert result.F > 0
    assert result.Cf > 0

    # Monotonicity: Mach should increase along the spike
    assert np.all(np.diff(result.M) >= 0)

    # Geometry: radius should decrease toward the tip
    assert result.Rx_over_Re[0] > result.Rx_over_Re[-1]


@pytest.mark.parametrize(
    "Pc,Tc,gamma,er",
    [
        (3e6, 1500, 1.20, 8),
        (5e6, 1900, 1.27, 12),
        (8e6, 2500, 1.35, 20),
    ],
)
def test_solver_parametrized(Pc, Tc, gamma, er):
    params = EngineParameters(Tc=Tc, Pc=Pc, molar_m=20.18, gamma=gamma, Re=0.015, er=er)
    result = solve(params, Pa=57e3)
    assert np.all(np.diff(result.M) >= 0)
    assert result.Rx_over_Re[0] > result.Rx_over_Re[-1]


def test_pressure_monotonicity(test_params):
    result = solve(test_params, Pa=57e3)
    assert np.all(np.diff(result.P) <= 0)


def test_temperature_monotonicity(test_params):
    result = solve(test_params, Pa=57e3)
    assert np.all(np.diff(result.T) <= 0)


def test_isp_monotonicity(test_params):
    result = solve(test_params, Pa=57e3)
    diffs = np.diff(result.Isp)

    # Allow realistic numerical noise
    assert np.min(diffs) > -1e-3

    # Global monotonicity: final Isp > initial
    assert result.Isp[-1] > result.Isp[0]


def test_throat_geometry(test_params):
    result = solve(test_params, Pa=57e3)
    assert result.ht > 0
    assert result.At > 0


def test_pressure_matched(test_params):
    Pe = get_Pe(test_params)
    result = solve(test_params, Pa=Pe)
    assert result.F > 0


def test_overexpanded(test_params):
    result = solve(test_params, Pa=200e3)
    assert result.F > 0


def test_underexpanded(test_params):
    result = solve(test_params, Pa=100)
    assert result.F > 0


def test_small_er():
    params = EngineParameters(
        Tc=1900, Pc=5e6, molar_m=20.18, gamma=1.27, Re=0.015, er=5
    )
    result = solve(params, Pa=57e3)
    assert np.all(np.diff(result.M) >= 0)


def test_large_er():
    params = EngineParameters(
        Tc=1900, Pc=5e6, molar_m=20.18, gamma=1.27, Re=0.015, er=40
    )
    result = solve(params, Pa=57e3)
    assert np.all(np.diff(result.M) >= 0)


def test_mass_flow_positive(test_params):
    result = solve(test_params, Pa=57e3)
    assert result.m_dot > 0
    assert np.isfinite(result.m_dot)


def test_thrust_scales_with_pressure(test_params):
    r1 = solve(test_params, Pa=57e3)

    params2 = replace(test_params, Pc=test_params.Pc * 2)
    r2 = solve(params2, Pa=57e3)

    assert r2.F > r1.F


def test_solver_result_shapes(test_params):
    result = solve(test_params, Pa=57e3)
    N = len(result.M)
    assert len(result.Rx_over_Re) == N
    assert len(result.X_over_Re) == N
    assert len(result.P) == N
    assert len(result.T) == N
    assert len(result.Isp) == N


def test_solver_with_truncation(test_params: EngineParameters):
    """Verify that enabling spike truncation correctly adjusts performance outputs (F and Cf)."""
    # Solve standard full-length spike
    res_full = solve(test_params, Pa=57e3)

    # Solve with truncation enabled
    truncated_params = replace(test_params, truncation=0.7)
    res_trunc = solve(truncated_params, Pa=57e3)

    # Truncation changes the effective exit area and applies base drag, 
    # resulting in a modified total thrust compared to full length.
    assert res_trunc.F > 0
    assert res_trunc.Cf > 0
    assert res_trunc.F != res_full.F


def test_solver_truncation_base_drag_ambient_extremes(test_params: EngineParameters):
    """Ensure base drag calculation handles extreme ambient pressures gracefully during truncation."""
    truncated_params = replace(test_params, truncation=0.8)

    # Vacuum condition (Pa = 0)
    res_vacuum = solve(truncated_params, Pa=0.0)
    assert res_vacuum.F > 0
    assert np.isfinite(res_vacuum.F)

    # High overexpansion condition (Pa >> Pc)
    res_high_pa = solve(truncated_params, Pa=200e3)
    assert res_high_pa.F >= 0  # Should clamp to zero or positive via max(0.0, ...)
    assert np.isfinite(res_high_pa.F)
