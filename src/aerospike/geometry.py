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
