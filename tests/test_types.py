import numpy as np
import pytest

from aerospike.types import EngineParameters, SolverResult


def test_engine_parameters_basic():
    p = EngineParameters(
        Tc=1900,
        Pc=5e6,
        molar_m=20.18,
        gamma=1.27,
        Re=0.015,
        er=12,
    )

    assert p.Tc == 1900
    assert p.Pc == 5e6
    assert p.molar_m == 20.18
    assert p.gamma == 1.27
    assert p.Re == 0.015
    assert p.er == 12


def test_engine_parameters_slots():
    p = EngineParameters(1900, 5e6, 20.18, 1.27, 0.015, 12)

    # slots → no __dict__
    assert not hasattr(p, "__dict__")

    # slots → no dynamic attributes
    with pytest.raises(AttributeError):
        p.new_field = 123


@pytest.mark.parametrize(
    "Tc,Pc,molar_m,gamma,Re,er",
    [
        (1500, 3e6, 18.0, 1.20, 0.010, 8),
        (2500, 8e6, 22.0, 1.35, 0.020, 20),
    ],
)
def test_engine_parameters_parametrized(Tc, Pc, molar_m, gamma, Re, er):
    p = EngineParameters(Tc, Pc, molar_m, gamma, Re, er)
    assert p.Tc == Tc
    assert p.Pc == Pc
    assert p.molar_m == molar_m
    assert p.gamma == gamma
    assert p.Re == Re
    assert p.er == er


def test_solver_result_basic():
    N = 10
    r = SolverResult(
        M=np.zeros(N),
        Rx_over_Re=np.zeros(N),
        X_over_Re=np.zeros(N),
        P=np.zeros(N),
        T=np.zeros(N),
        Isp=np.zeros(N),
        F=100.0,
        Cf=1.5,
        m_dot=0.2,
        At=0.0005,
        ht=0.005,
        delta=0.3,
        Pa=101e3,
    )

    assert isinstance(r.M, np.ndarray)
    assert isinstance(r.P, np.ndarray)
    assert r.F == 100.0
    assert r.Cf == 1.5
    assert r.Pa == 101e3


def test_solver_result_shapes():
    N = 20
    r = SolverResult(
        M=np.zeros(N),
        Rx_over_Re=np.zeros(N),
        X_over_Re=np.zeros(N),
        P=np.zeros(N),
        T=np.zeros(N),
        Isp=np.zeros(N),
        F=100.0,
        Cf=1.5,
        m_dot=0.2,
        At=0.0005,
        ht=0.005,
        delta=0.3,
        Pa=101e3,
    )

    assert len(r.M) == N
    assert len(r.Rx_over_Re) == N
    assert len(r.X_over_Re) == N
    assert len(r.P) == N
    assert len(r.T) == N
    assert len(r.Isp) == N


def test_solver_result_slots():
    N = 5
    r = SolverResult(
        M=np.zeros(N),
        Rx_over_Re=np.zeros(N),
        X_over_Re=np.zeros(N),
        P=np.zeros(N),
        T=np.zeros(N),
        Isp=np.zeros(N),
        F=10.0,
        Cf=1.0,
        m_dot=0.1,
        At=0.0001,
        ht=0.001,
        delta=0.2,
        Pa=50000,
    )

    assert not hasattr(r, "__dict__")

    with pytest.raises(AttributeError):
        r.extra_field = 123


def test_solver_result_allows_mismatched_shapes():
    r = SolverResult(
        M=np.zeros(10),
        Rx_over_Re=np.zeros(10),
        X_over_Re=np.zeros(10),
        P=np.zeros(5),  # mismatched
        T=np.zeros(10),
        Isp=np.zeros(10),
        F=10.0,
        Cf=1.0,
        m_dot=0.1,
        At=0.0001,
        ht=0.001,
        delta=0.2,
        Pa=50000,
    )
    assert isinstance(r, SolverResult)
