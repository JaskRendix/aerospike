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
- export (XYZ geometry)  
- save/load (JSON)

Press **Solve** to run the solver and update the results and plot.

---

### Saving and Loading

Design parameters can be saved to and loaded from JSON files.  
The GUI includes a dedicated panel for this.

---

### Exporting Geometry

Spike geometry can be exported as an **XYZ point file** suitable for import into CAD tools that support point‑curve import.

---

### Solver

The solver implements the **C.C. Lee plug‑nozzle contour algorithm**.

Reference documents are included in the `references/` directory:

- *Spike Contour Algorithm.docx*  
- *Spike Contour Algorithm.pdf*  
- *Fortran Programs for Plug Nozzle Design – C.C. Lee (1963)*

---

### Testing

Run the full test suite:

```
pytest
```

Tests cover:

- flow relations  
- geometry generation  
- solver behavior  
- plotting (standalone mode)  
- type definitions  

The plotting module provides two APIs:

- `plot_results(result)` — standalone 2×3 subplot version (used in tests)  
- `plot_results_gui(result, ax)` — embedded version for PySide6

---

### Repository Structure

```
src/aerospike/        solver, flow relations, geometry, plotting, types
src/aerospike_gui/    PySide6 GUI (widgets + controller + main window)
tests/                pytest suite
references/           original algorithm documents
```
