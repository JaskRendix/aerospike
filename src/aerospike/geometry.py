from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from .types import SolverResult


@dataclass(slots=True)
class Point3D:
    """Simple 3D point representation."""

    x: float
    y: float
    z: float


def spike_profile(result: SolverResult) -> list[tuple[float, float]]:
    """
    Returns the 2D spike contour as (x, r) pairs in meters.
    X_over_Re and Rx_over_Re are dimensionless, so multiply by Re.
    """
    Re = result.ht + (result.At / (np.pi * result.ht))  # approximate outer radius

    x = result.X_over_Re * Re
    r = result.Rx_over_Re * Re

    return list(zip(x.tolist(), r.tolist()))


def spike_profile_xyz(result: SolverResult, samples: int = 360) -> list[Point3D]:
    """
    Revolves the spike contour around the axis to produce a 3D point cloud.
    Useful for CAD import (XYZ point cloud).
    """
    profile = spike_profile(result)
    points: list[Point3D] = []

    theta = np.linspace(0.0, 2.0 * np.pi, samples)

    for x, r in profile:
        for t in theta:
            y = r * np.cos(t)
            z = r * np.sin(t)
            points.append(Point3D(x=x, y=y, z=z))

    return points


def export_xyz(points: Iterable[Point3D]) -> str:
    """
    Export a list of 3D points to a simple XYZ text format.
    This matches SolidWorks “Curve Through XYZ Points”.
    """
    lines = []
    for p in points:
        lines.append(f"{p.x:.6f}, {p.y:.6f}, {p.z:.6f}")
    return "\n".join(lines)


def export_spike_xyz(result: SolverResult, samples: int = 360) -> str:
    """
    Convenience wrapper: generate full 3D spike geometry and export as XYZ text.
    """
    pts = spike_profile_xyz(result, samples=samples)
    return export_xyz(pts)
