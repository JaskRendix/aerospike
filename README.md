# **Aerospike Nozzle Design**

This project provides a modern, fully tested implementation of the aerospike nozzle solver based on the plug‑nozzle contour algorithm developed by **C.C. Lee (NASA MSFC, 1963)**.

It includes:

- a modular **solver library** (`src/aerospike`)
- a modern **PySide6 GUI** (`src/aerospike_gui`)
- a complete **pytest suite** (`tests/`)

The original Tkinter GUI by Matthew Vernacchia (MIT Rocket Team, 2014) is available at:  
[https://github.com/mvernacc/aerospike-nozzle-design-gui](https://github.com/mvernacc/aerospike-nozzle-design-gui)

This repository replaces that interface with a new PySide6 application and a rewritten solver, geometry, plotting, and export modules.

---

## **Installation**

Requires **Python 3.12**, **NumPy**, and **Matplotlib**.

Install the core solver:

```
pip install aerospike
```

Install the optional GUI:

```
pip install aerospike[gui]
```

The PySide6 GUI is tested on Linux (X11/Wayland).  
Headless CI uses Matplotlib’s `Agg` backend.

---

## **Running the GUI**

After installing the GUI extras:

```
aerospike-gui
```

The interface provides panels for:

- chamber conditions  
- gas properties  
- propellant presets (LOX/LH₂, LOX/CH₄, RP‑1, hybrids)  
- ambient pressure or altitude  
- atmosphere presets (sea level, 5 km, 10 km, vacuum)  
- expansion ratio or exit radius  
- solver results  
- embedded Matplotlib plot  
- save/load (JSON)  
- export (XYZ, STL, SVG)  
- altitude performance sweep with bell‑nozzle comparison

Press **Solve** to run the solver and update all panels.

Press **Run Altitude Sweep** to generate a dual‑axis plot showing:

- aerospike thrust vs altitude  
- bell‑nozzle thrust vs altitude  
- aerospike thrust coefficient \(C_f\)

---

## **Saving and Loading**

Design parameters can be saved to and loaded from JSON files.  
The GUI includes a dedicated panel for this.

---

## **Exporting Geometry**

The GUI supports exporting spike geometry in three formats:

- **XYZ point cloud** — for CAD lofting or point‑curve workflows  
- **ASCII STL mesh** — for 3D printing or CFD meshing  
- **SVG 2D line art** — for laser cutting, DXF conversion, or vector CAD

The SVG export produces a clean mirrored 2D contour suitable for manufacturing templates.

---

## **Solver**

The solver implements the C.C. Lee plug‑nozzle contour algorithm with modernized flow physics:

- Newton–Raphson inversion of the area–Mach relation  
- multi‑layer atmospheric model  
- direct analytical inversion of Pe → er  
- stable behavior for large expansion ratios  
- improved geometry scaling  
- altitude sweep helper for off‑design analysis  
- bell‑nozzle comparison model

Reference documents are included in the `references/` directory.

---

## **Testing**

Run the full test suite:

```
pytest
```

Tests cover:

- flow relations (Mach, Pe, er(Pe), atmosphere)  
- geometry generation (XYZ, STL, **SVG**)  
- solver behavior  
- plotting (standalone and GUI‑embedded)  
- type definitions  
- SVG scaling, mirroring, and empty‑profile fallback

The plotting module provides two APIs:

- `plot_results(result)` — standalone 2×3 subplot version  
- `plot_results_gui(result, ax)` — embedded version for PySide6

---

## **Repository Structure**

```
src/aerospike/
    flow.py
    solver.py
    geometry.py        # XYZ, STL, SVG export
    plotting.py
    types.py

src/aerospike_gui/
    controller.py      # solver orchestration, export helpers
    window.py          # main GUI window
    widgets/           # panels (inputs, results, export, save/load)

tests/
    test_flow.py
    test_solver.py
    test_geometry.py   # includes SVG tests
    test_plotting.py

references/
    C.C. Lee algorithm documents
```
