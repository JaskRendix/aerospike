from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
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
    Assembles modular widgets and coordinates layout + solver refresh.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Aerospike Nozzle Design & CAD Generator (PySide6)")
        self.resize(1400, 900)

        # Controller (central logic)
        self.controller = Controller()

        # Central widget
        central = QWidget(self)
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)

        # Left scrollable area for inputs and action buttons
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

        # Right container for results and Matplotlib plotting panel
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)

        self.results_panel = ResultsPanel(self.controller)
        self.plot_panel = PlotPanel(self.controller)

        right_layout.addWidget(self.results_panel, stretch=1)
        right_layout.addWidget(self.plot_panel, stretch=3)

        root_layout.addWidget(right_container, stretch=2)

        # Wire Signals
        self._connect_signals()

        # Run initial solve on launch
        self.run_solver()

    def _connect_signals(self) -> None:
        """Connect button events and signals across panels."""
        # Connect Solve button
        if hasattr(self.solve_panel, "solve_requested"):
            self.solve_panel.solve_requested.connect(self.run_solver)
        elif hasattr(self.solve_panel, "solve_button"):
            self.solve_panel.solve_button.clicked.connect(self.run_solver)

        # Connect JSON Load signal (if available) to reload fields and re-solve
        if hasattr(self.save_load_panel, "loaded"):
            self.save_load_panel.loaded.connect(self._on_config_loaded)

    def _on_config_loaded(self) -> None:
        """Triggered when a user loads a JSON configuration file."""
        # Refresh field values across input panels
        for widget in (
            self.engine_inputs,
            self.ambient_inputs,
            self.expansion_inputs,
            self.sizing_inputs,
        ):
            if hasattr(widget, "refresh_from_controller"):
                widget.refresh_from_controller()

        self.run_solver()

    def _refresh_all(self) -> None:
        """Refresh results + plot panel. Called after each solve."""
        if hasattr(self.results_panel, "refresh"):
            self.results_panel.refresh()
        if hasattr(self.plot_panel, "refresh"):
            self.plot_panel.refresh()

    def run_solver(self) -> None:
        """Run aerospike solver and refresh UI components."""
        try:
            self.controller.run_solver()
            self._refresh_all()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Solver Error",
                f"An error occurred during calculation:\n{e}",
            )

    def run_altitude_sweep_plot(self) -> None:
        """Run altitude performance sweep and display in a popup plot window."""
        try:
            import matplotlib.pyplot as plt
            alt_km, thrusts, cfs = self.controller.run_altitude_sweep()

            fig, ax1 = plt.subplots(figsize=(8, 5))

            color = 'tab:red'
            ax1.set_xlabel('Altitude AMSL [km]')
            ax1.set_ylabel('Thrust F [N]', color=color)
            ax1.plot(alt_km, thrusts, color=color, linewidth=2, label='Thrust [N]')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.grid(True, linestyle='--', alpha=0.5)

            ax2 = ax1.twinx()  
            color = 'tab:blue'
            ax2.set_ylabel('Thrust Coefficient $C_f$', color=color)
            ax2.plot(alt_km, cfs, color=color, linewidth=2, linestyle='-.', label='Cf [-]')
            ax2.tick_params(axis='y', labelcolor=color)

            plt.title('Aerospike Off-Design Altitude Performance Sweep')
            fig.tight_layout()
            plt.show()

        except Exception as e:
            QMessageBox.critical(self, "Sweep Error", f"Failed to run altitude sweep:\n{e}")
