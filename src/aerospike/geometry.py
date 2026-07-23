from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from .types import SolverResult


@dataclass(slots=True)
class Point3D:
    """3D point container."""
    x: float
    y: float
    z: float


def spike_profile(result: SolverResult) -> list[tuple[float, float]]:
    """Return 2D spike contour (x, r) in meters."""
    Re = (result.At + np.pi * result.ht**2 * np.sin(result.delta)) / (
        2.0 * np.pi * result.ht
    )

    x = result.X_over_Re * Re
    r = result.Rx_over_Re * Re

    return list(zip(x.tolist(), r.tolist()))


def spike_profile_xyz(result: SolverResult, samples: int = 72) -> list[Point3D]:
    """Generate 3D point cloud by revolving spike contour."""
    Re = (result.At + np.pi * result.ht**2 * np.sin(result.delta)) / (
        2.0 * np.pi * result.ht
    )

    x_2d = result.X_over_Re * Re
    r_2d = result.Rx_over_Re * Re

    theta = np.linspace(0.0, 2.0 * np.pi, samples)

    X, T = np.meshgrid(x_2d, theta, indexing="ij")
    R, _ = np.meshgrid(r_2d, theta, indexing="ij")

    Y = R * np.cos(T)
    Z = R * np.sin(T)

    x_flat = X.ravel()
    y_flat = Y.ravel()
    z_flat = Z.ravel()

    return [
        Point3D(float(x), float(y), float(z))
        for x, y, z in zip(x_flat, y_flat, z_flat)
    ]


def export_xyz(points: Iterable[Point3D]) -> str:
    """Export 3D points in XYZ text format."""
    return "\n".join(f"{p.x:.6f}, {p.y:.6f}, {p.z:.6f}" for p in points)


def export_spike_xyz(result: SolverResult, samples: int = 72) -> str:
    """Generate and export spike geometry as XYZ text."""
    pts = spike_profile_xyz(result, samples=samples)
    return export_xyz(pts)


def export_spike_stl(
    result: SolverResult, radial_samples: int = 64, header: str = "Aerospike"
) -> str:
    """Export spike geometry as ASCII STL mesh."""
    Re = (result.At + np.pi * result.ht**2 * np.sin(result.delta)) / (
        2.0 * np.pi * result.ht
    )

    x_2d = result.X_over_Re * Re
    r_2d = result.Rx_over_Re * Re

    step = max(1, len(x_2d) // 100)
    x_2d = x_2d[::step]
    r_2d = r_2d[::step]

    theta = np.linspace(0.0, 2.0 * np.pi, radial_samples, endpoint=False)
    n_x, n_t = len(x_2d), len(theta)

    grid = np.zeros((n_x, n_t, 3))
    for i in range(n_x):
        for j in range(n_t):
            grid[i, j] = [
                x_2d[i],
                r_2d[i] * np.cos(theta[j]),
                r_2d[i] * np.sin(theta[j]),
            ]

    stl = [f"solid {header}"]

    for i in range(n_x - 1):
        for j in range(n_t):
            jn = (j + 1) % n_t

            p1 = grid[i, j]
            p2 = grid[i + 1, j]
            p3 = grid[i + 1, jn]
            p4 = grid[i, jn]

            stl.append(" facet normal 0 0 0\n  outer loop")
            stl.append(f"   vertex {p1[0]:.6f} {p1[1]:.6f} {p1[2]:.6f}")
            stl.append(f"   vertex {p2[0]:.6f} {p2[1]:.6f} {p2[2]:.6f}")
            stl.append(f"   vertex {p3[0]:.6f} {p3[1]:.6f} {p3[2]:.6f}")
            stl.append("  endloop\n endfacet")

            stl.append(" facet normal 0 0 0\n  outer loop")
            stl.append(f"   vertex {p1[0]:.6f} {p1[1]:.6f} {p1[2]:.6f}")
            stl.append(f"   vertex {p3[0]:.6f} {p3[1]:.6f} {p3[2]:.6f}")
            stl.append(f"   vertex {p4[0]:.6f} {p4[1]:.6f} {p4[2]:.6f}")
            stl.append("  endloop\n endfacet")

    stl.append(f"endsolid {header}")
    return "\n".join(stl)


def export_spike_svg(result: SolverResult) -> str:
    """Export 2D spike contour as an SVG vector graphic."""
    profile = spike_profile(result)
    if not profile:
        return "<svg></svg>"

    xs = [p[0] for p in profile]
    rs = [p[1] for p in profile]

    min_x, max_x = min(xs), max(xs)
    min_r, max_r = min(rs), max(rs)

    width_m = max_x - min_x if max_x > min_x else 1.0
    height_m = max_r - min_r if max_r > min_r else 1.0

    # Scale to a clean pixel viewbox (e.g., 800x400 base)
    svg_w, svg_h = 800, 400
    margin = 50

    plot_w = svg_w - 2 * margin
    plot_h = svg_h - 2 * margin

    scale_x = plot_w / width_m
    scale_y = plot_h / height_m
    scale = min(scale_x, scale_y)

    def trans_x(x: float) -> float:
        return margin + (x - min_x) * scale

    def trans_y(r: float) -> float:
        # Flip Y for screen coordinates (SVG origin is top-left)
        return svg_h - margin - (r - min_r) * scale

    # Build path commands for top contour and mirrored bottom contour
    top_pts = [(trans_x(x), trans_y(r)) for x, r in profile]
    bot_pts = [(trans_x(x), trans_y(-r)) for x, r in profile]

    path_top = " ".join(f"{'M' if i == 0 else 'L'} {p[0]:.2f},{p[1]:.2f}" for i, p in enumerate(top_pts))
    path_bot = " ".join(f"{'M' if i == 0 else 'L'} {p[0]:.2f},{p[1]:.2f}" for i, p in enumerate(bot_pts))

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="100%">',
        '  <style>',
        '    .contour { fill: none; stroke: #2563eb; stroke-width: 2px; }',
        '    .centerline { stroke: #94a3b8; stroke-dasharray: 4; stroke-width: 1px; }',
        '    .grid { stroke: #e2e8f0; stroke-width: 0.5px; }',
        '  </style>',
        f'  <rect width="{svg_w}" height="{svg_h}" fill="#ffffff"/>',
        f'  <line x1="{margin}" y1="{trans_y(0.0)}" x2="{svg_w - margin}" y2="{trans_y(0.0)}" class="centerline" />',
        f'  <path d="{path_top}" class="contour" />',
        f'  <path d="{path_bot}" class="contour" />',
        '</svg>'
    ]

    return "\n".join(svg_lines)
