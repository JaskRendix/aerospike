### Aerospike Nozzle Design

This project provides a modern, fully tested implementation of the aerospike nozzle solver based on the plug‑nozzle contour algorithm developed by **C.C. Lee (NASA MSFC, 1963)**.  
It includes:

- a modular **solver library** (`src/aerospike`)
- a modern **PySide6 GUI** (`src/aerospike_gui`)
- a complete **pytest suite** (`tests/`)

The original Tkinter GUI by Matthew Vernacchia (MIT Rocket Team, 2014) is available at:  
[https://github.com/mvernacc/aerospike-nozzle-design-gui](https://github.com/mvernacc/aerospike-nozzle-design-gui)

This repository replaces that interface with a new PySide6 application and a rewritten solver, geometry, and plotting module.

---

### Installation

The solver library requires **Python 3.12**, **NumPy**, and **Matplotlib**.

Install the core package:

```
pip install aerospike
```

Install the optional GUI:

```
pip install aerospike[gui]
```

The PySide6 GUI is fully functional and tested on Linux (X11/Wayland).  
Headless CI uses Matplotlib’s `Agg` backend.

---

### Running the GUI

After installing the GUI extras:

```
aerospike-gui
```

The interface provides panels for:

- chamber conditions  
- gas properties  
- ambient pressure or altitude  
- expansion ratio or exit pressure  
- thrust or exit radius  
- solver results  
- embedded Matplotlib plot  
- save/load (JSON)  
- export (XYZ point cloud or STL mesh)

Press **Solve** to run the solver and update all panels.

---

### Saving and Loading

Design parameters can be saved to and loaded from JSON files.  
The GUI includes a dedicated panel for this.

---

### Exporting Geometry

The GUI supports exporting spike geometry in two formats:

- **XYZ point cloud** — suitable for CAD tools that support point‑curve or loft-from-points workflows.
- **ASCII STL mesh** — suitable for 3D printing, meshing, or direct import into CAD/CFD tools.

A radial resolution selector (36–360 points) allows controlling mesh density.

---

### Solver

The solver implements the C.C. Lee plug‑nozzle contour algorithm with modernized flow physics:

- Newton–Raphson inversion of the area–Mach relation  
- multi‑layer atmospheric model  
- direct analytical inversion of Pe → er  
- stable behavior for large expansion ratios  
- improved geometry scaling

Reference documents are included in the `references/` directory.

---

### Testing

Run the full test suite:

```
pytest
```

Tests cover:

- flow relations (Mach, Pe, er(Pe), atmosphere)  
- geometry generation (XYZ, STL)  
- solver behavior  
- plotting (standalone and GUI‑embedded)  
- type definitions  

The plotting module provides two APIs:

- `plot_results(result)` — standalone 2×3 subplot version (used in tests)  
- `plot_results_gui(result, ax)` — embedded version for PySide6

---

### Repository Structure

```
src/aerospike/        solver, flow relations, geometry, STL/XYZ export, plotting, types
src/aerospike_gui/    PySide6 GUI (widgets, controller, main window)
tests/                pytest suite (flow, solver, geometry, plotting)
references/           original algorithm documents
```
