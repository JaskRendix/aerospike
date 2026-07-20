from __future__ import annotations

import matplotlib

matplotlib.use("QtAgg")  # ensure Qt backend

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from aerospike.plotting import plot_results_gui
from aerospike_gui.controller import Controller


class PlotPanel(QWidget):
    """
    Embedded Matplotlib plot panel for aerospike results.
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        # Group box for visual clarity
        group = QGroupBox("Aerospike Plot")
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(group)

        layout = QVBoxLayout(group)

        # Create a Matplotlib figure and canvas
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def refresh(self) -> None:
        """
        Clear the figure and redraw using the solver result.
        """
        result = self.controller.result
        if result is None:
            return

        # Clear previous plot
        self.figure.clear()

        # Let your existing plotting function draw into this figure
        ax = self.figure.add_subplot(111)
        plot_results_gui(result, ax=ax)

        # Redraw canvas
        self.canvas.draw()
