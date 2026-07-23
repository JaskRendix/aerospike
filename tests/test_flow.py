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
        (12, 3.6383),
        (8, 3.3036),
        (20, 4.0656),
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
    assert Pe == pytest.approx(40283.20, rel=1e-2)


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
    er = get_er_from_Pe(params, Pe_target)
    assert er > 0
    assert np.isfinite(er)


def test_get_er_from_Pe_monotonicity(params: EngineParameters):
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
from aerospike.types import EngineParameters, SolverResult


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

    # Scale geometry artificially
    fake_result.Rx_over_Re *= 2.0
    fake_result.X_over_Re *= 2.0

    svg2 = export_spike_svg(fake_result)

    # SVG is normalized to the same viewBox, so scaling should NOT change the output
    assert svg1 == svg2


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


def test_spike_profile_truncation(fake_result: SolverResult):
    """Verify spike profile length is reduced when truncation is enabled."""
    # Full length profile
    full_profile = spike_profile(fake_result)
    
    # Attach parameters with truncation
    fake_result.params = EngineParameters(
        Tc=1900, Pc=5e6, molar_m=20.18, gamma=1.27, Re=0.015, er=12, truncation=0.7
    )
    
    trunc_profile = spike_profile(fake_result)
    
    assert len(trunc_profile) < len(full_profile)
    assert trunc_profile[-1][0] < full_profile[-1][0]


def test_export_spike_stl_structure(fake_result: SolverResult):
    """Verify STL output has correct header, solid blocks, and face definitions."""
    from aerospike.geometry import export_spike_stl
    
    stl_str = export_spike_stl(fake_result, radial_samples=16)
    
    assert isinstance(stl_str, str)
    assert stl_str.startswith("solid Aerospike")
    assert stl_str.endswith("endsolid Aerospike")
    assert "facet normal" in stl_str
    assert "outer loop" in stl_str
    assert "vertex" in stl_str


def test_export_spike_stl_with_flange_and_bolts(fake_result: SolverResult):
    """Verify STL generator successfully incorporates flange and bolt holes without crashing."""
    from aerospike.geometry import export_spike_stl
    
    fake_result.params = EngineParameters(
        Tc=1900, 
        Pc=5e6, 
        molar_m=20.18, 
        gamma=1.27, 
        Re=0.015, 
        er=12,
        flange_thickness=0.005,
        flange_radius=0.030,
        bolt_circle_radius=0.022,
        bolt_count=6,
        bolt_hole_radius=0.002
    )
    
    stl_str = export_spike_stl(fake_result, radial_samples=16)
    
    # Should contain valid ASCII mesh data including the extra geometry blocks
    assert len(stl_str) > 500
    assert "solid Aerospike" in stl_str


def test_get_alt_from_Pa_zero():
    """Verify vacuum condition returns maximum sensible altitude limit or does not crash."""
    alt = get_alt_from_Pa(0.0)
    assert alt > 0.0 or alt == 0.0  # Handles vacuum cleanly


def test_get_Pa_from_alt_stratosphere():
    """Verify pressure calculation at boundary conditions (e.g., 20 km and 44.3 km)."""
    Pa_20k = get_Pa_from_alt(20000)
    assert 0 < Pa_20k < 10000  # Should be ~5500 Pa

    Pa_boundary = get_Pa_from_alt(44331.514)
    assert Pa_boundary == pytest.approx(0.0, abs=1e-1)


def test_get_er_from_Pe_high_expansion(params: EngineParameters):
    """Test solver handling near lower bound pressure targets."""
    Pe_very_low = 500.0  # High expansion ratio required
    er = get_er_from_Pe(params, Pe_very_low)
    assert er > 0
    assert np.isfinite(er)


@pytest.mark.parametrize("er", [1.01, 1.1, 50.0, 100.0])
def test_get_Mach_boundary_er(er: float, params: EngineParameters):
    """Ensure Mach calculation does not output NaN or imaginary numbers at boundary expansion ratios."""
    p = replace(params, er=er)
    M = get_Mach(p)
    assert np.isfinite(M)
    assert np.isreal(M)
    assert M >= 1.0


def test_get_Re_from_mass_flow_zero(params: EngineParameters):
    """Ensure zero mass flow gives zero radius without zero-division crash."""
    Re = get_Re_from_mass_flow(params, 0.0)
    assert Re == 0.0


def test_get_Re_from_thrust_zero(params: EngineParameters):
    """Ensure zero thrust gives zero radius cleanly."""
    Re = get_Re_from_thrust(params, 0.0)
    assert Re == 0.0
