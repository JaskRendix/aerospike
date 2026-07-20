from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from aerospike_gui.controller import Controller
from aerospike_gui.widgets.ambient_inputs import AmbientInputsWidget

# Widgets
from aerospike_gui.widgets.engine_inputs import EngineInputsWidget
from aerospike_gui.widgets.expansion_inputs import ExpansionInputsWidget
from aerospike_gui.widgets.export_panel import ExportPanel
from aerospike_gui.widgets.plot_panel import PlotPanel
from aerospike_gui.widgets.results_panel import ResultsPanel
from aerospike_gui.widgets.save_load_panel import SaveLoadPanel
from aerospike_gui.widgets.sizing_inputs import SizingInputsWidget
from aerospike_gui.widgets.solve_panel import SolvePanel


class MainWindow(QMainWindow):
    """
    Full PySide6 GUI for Aerospike Nozzle Design.
    Assembles all modular widgets and coordinates layout + solver refresh.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Aerospike Nozzle Design (PySide6)")
        self.resize(1400, 900)

        # Controller (central logic)
        self.controller = Controller()

        # Central widget
        central = QWidget(self)
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # Add input widgets
        self.engine_inputs = EngineInputsWidget(self.controller)
        self.ambient_inputs = AmbientInputsWidget(self.controller)
        self.expansion_inputs = ExpansionInputsWidget(self.controller)
        self.sizing_inputs = SizingInputsWidget(self.controller)
        self.save_load_panel = SaveLoadPanel(self.controller)
        self.export_panel = ExportPanel(self.controller)
        self.solve_panel = SolvePanel(self)

        left_layout.addWidget(self.engine_inputs)
        left_layout.addWidget(self.ambient_inputs)
        left_layout.addWidget(self.expansion_inputs)
        left_layout.addWidget(self.sizing_inputs)
        left_layout.addWidget(self.save_load_panel)
        left_layout.addWidget(self.export_panel)
        left_layout.addWidget(self.solve_panel)
        left_layout.addStretch()

        left_scroll.setWidget(left_container)
        root_layout.addWidget(left_scroll, stretch=1)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        self.results_panel = ResultsPanel(self.controller)
        self.plot_panel = PlotPanel(self.controller)

        right_layout.addWidget(self.results_panel)
        right_layout.addWidget(self.plot_panel)

        root_layout.addWidget(right_container, stretch=2)

        # Initial empty refresh
        self._refresh_all()

    def _refresh_all(self) -> None:
        """
        Refresh results + plot panel.
        Called after each solve.
        """
        self.results_panel.refresh()
        self.plot_panel.refresh()

    def run_solver(self) -> None:
        """
        Run solver and refresh UI.
        """
        self.controller.run_solver()
        self._refresh_all()
