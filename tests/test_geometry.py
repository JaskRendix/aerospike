import numpy as np
import pytest

from aerospike.geometry import (
    Point3D,
    export_spike_xyz,
    export_xyz,
    spike_profile,
    spike_profile_xyz,
)
from aerospike.types import SolverResult


@pytest.fixture
def fake_result() -> SolverResult:
    """
    Minimal synthetic SolverResult for geometry testing.
    Uses a simple linear spike shape.
    """
    N = 10
    M = np.linspace(1, 2, N)
    Rx = np.linspace(1.0, 0.2, N)  # radius shrinks
    Xx = np.linspace(0.0, 1.0, N)  # axial coordinate grows
    P = np.linspace(5e6, 1e5, N)
    T = np.linspace(1900, 500, N)
    Isp = np.linspace(0, 300, N)

    return SolverResult(
        M=M,
        Rx_over_Re=Rx,
        X_over_Re=Xx,
        P=P,
        T=T,
        Isp=Isp,
        F=1000.0,
        Cf=1.5,
        m_dot=0.2,
        At=0.0005,
        ht=0.005,
        delta=0.3,
        Pa=101e3,
    )


def test_spike_profile_basic(fake_result: SolverResult):
    profile = spike_profile(fake_result)

    assert isinstance(profile, list)
    assert len(profile) == len(fake_result.M)

    # x must increase, r must decrease
    xs = [p[0] for p in profile]
    rs = [p[1] for p in profile]

    assert xs[0] < xs[-1]
    assert rs[0] > rs[-1]


@pytest.mark.parametrize("scale", [1.0, 2.0, 5.0])
def test_spike_profile_scaling(fake_result: SolverResult, scale: float):
    # artificially scale geometry
    fake_result.At *= scale
    fake_result.ht *= scale

    profile = spike_profile(fake_result)
    xs = [p[0] for p in profile]
    rs = [p[1] for p in profile]

    assert all(x >= 0 for x in xs)
    assert all(r >= 0 for r in rs)


def test_spike_profile_xyz_basic(fake_result: SolverResult):
    pts = spike_profile_xyz(fake_result, samples=36)

    assert isinstance(pts, list)
    assert all(isinstance(p, Point3D) for p in pts)

    # correct number of points
    assert len(pts) == len(fake_result.M) * 36

    # radius consistency: y^2 + z^2 ≈ r^2
    profile = spike_profile(fake_result)
    for i, (x, r) in enumerate(profile):
        for j in range(36):
            p = pts[i * 36 + j]
            assert p.x == pytest.approx(x)
            assert (p.y**2 + p.z**2) ** 0.5 == pytest.approx(r, rel=1e-3)


@pytest.mark.parametrize("samples", [1, 5, 10])
def test_spike_profile_xyz_samples(fake_result: SolverResult, samples: int):
    pts = spike_profile_xyz(fake_result, samples=samples)
    assert len(pts) == len(fake_result.M) * samples


def test_export_xyz_basic(fake_result: SolverResult):
    pts = spike_profile_xyz(fake_result, samples=5)
    text = export_xyz(pts)

    lines = text.splitlines()
    assert len(lines) == len(pts)

    # format check
    first = lines[0]
    parts = first.split(",")
    assert len(parts) == 3


def test_export_xyz_roundtrip(fake_result: SolverResult):
    pts = spike_profile_xyz(fake_result, samples=3)
    text = export_xyz(pts)

    parsed = []
    for line in text.splitlines():
        x, y, z = map(float, line.split(","))
        parsed.append((x, y, z))

    assert len(parsed) == len(pts)

    for (x, y, z), p in zip(parsed, pts):
        assert x == pytest.approx(round(p.x, 6))
        assert y == pytest.approx(round(p.y, 6))
        assert z == pytest.approx(round(p.z, 6))


def test_export_spike_xyz(fake_result: SolverResult):
    text = export_spike_xyz(fake_result, samples=4)
    lines = text.splitlines()

    # correct number of lines
    assert len(lines) == len(fake_result.M) * 4

    # format check
    assert "," in lines[0]
