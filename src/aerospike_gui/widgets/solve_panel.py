from __future__ import annotations

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class SolvePanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window

        layout = QVBoxLayout()

        # --- Main Solve Button ---
        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.main_window.run_solver)
        layout.addWidget(self.solve_button)

        # --- Altitude Performance Sweep Button ---
        self.sweep_button = QPushButton("Run Altitude Sweep (0–40 km)")
        self.sweep_button.clicked.connect(self.main_window.run_altitude_sweep_plot)
        layout.addWidget(self.sweep_button)

        self.setLayout(layout)
