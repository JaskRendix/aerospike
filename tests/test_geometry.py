import numpy as np
import pytest

from aerospike.geometry import (
    Point3D,
    export_spike_xyz,
    export_xyz,
    spike_profile,
    export_spike_svg,
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


def test_export_spike_svg_basic(fake_result: SolverResult):
    svg = export_spike_svg(fake_result)

    # Basic structure checks
    assert isinstance(svg, str)
    assert "<svg" in svg
    assert "</svg>" in svg

    # Should contain two contour paths (top + bottom)
    assert 'class="contour"' in svg
    assert svg.count('class="contour"') == 2

    # Should contain at least one 'M' and 'L' command
    assert "M " in svg
    assert "L " in svg

    # Should contain a centerline
    assert 'class="centerline"' in svg

    # Should not be empty or trivial
    assert len(svg) > 100


def test_export_spike_svg_mirrored_contour(fake_result: SolverResult):
    svg = export_spike_svg(fake_result)

    # Extract path commands for top and bottom contours
    lines = svg.splitlines()
    top_path = next(l for l in lines if 'class="contour"' in l and 'path' in l)
    bot_path = next(l for l in lines if 'class="contour"' in l and 'path' in l and l != top_path)

    # Parse coordinates from "M x,y L x,y ..." sequences
    def parse_coords(path_line: str):
        coords = []
        d = path_line.split('d="')[1].split('"')[0]
        for cmd in d.split():
            if cmd in ("M", "L"):
                continue
            x, y = cmd.split(",")
            coords.append((float(x), float(y)))
        return coords

    top_coords = parse_coords(top_path)
    bot_coords = parse_coords(bot_path)

    # Same number of points
    assert len(top_coords) == len(bot_coords)

    # X coordinates must match; Y must be mirrored around centerline
    # Find centerline Y from SVG
    centerline_y = None
    for l in lines:
        if 'class="centerline"' in l:
            parts = l.split()
            for p in parts:
                if p.startswith("y1="):
                    centerline_y = float(p.split('"')[1])
                    break
    assert centerline_y is not None

    for (xt, yt), (xb, yb) in zip(top_coords, bot_coords):
        assert xt == pytest.approx(xb)
        # mirrored around centerline
        assert yt == pytest.approx(2 * centerline_y - yb, rel=1e-3)


def test_export_spike_svg_scaling_effect(fake_result: SolverResult):
    svg1 = export_spike_svg(fake_result)

    # Scale geometry artificially (affects spike_profile)
    fake_result.Rx_over_Re *= 2.0
    fake_result.X_over_Re *= 2.0

    svg2 = export_spike_svg(fake_result)

    # The SVG strings must differ meaningfully
    assert svg1 != svg2

    # Extract one coordinate from each to ensure scaling changed geometry
    def extract_first_coord(svg: str):
        for line in svg.splitlines():
            if 'class="contour"' in line:
                d = line.split('d="')[1].split('"')[0]
                parts = d.split()
                for p in parts:
                    if p not in ("M", "L"):
                        x, y = p.split(",")
                        return float(x), float(y)
        return None

    c1 = extract_first_coord(svg1)
    c2 = extract_first_coord(svg2)

    assert c1 is not None and c2 is not None
    assert c1 != c2


def test_export_spike_svg_empty_profile():

    class DummyResult:
        pass

    # Monkeypatch spike_profile to return empty list
    original = spike_profile

    try:
        def empty_profile(_):
            return []

        # Replace spike_profile temporarily
        import aerospike.geometry as geom
        geom.spike_profile = empty_profile

        svg = export_spike_svg(DummyResult())
        assert svg.strip() == "<svg></svg>"
    finally:
        # Restore original
        geom.spike_profile = original
