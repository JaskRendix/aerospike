from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from aerospike_gui.controller import Controller


class ResultsPanel(QWidget):
    """
    Widget showing solver results:
    - Thrust F
    - Thrust coefficient Cf
    - Mass flow m_dot
    - Optional extra fields
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        # Group box for visual clarity
        group = QGroupBox("Solver Results")
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(group)

        layout = QVBoxLayout(group)

        # --- Labels ---
        self.thrust_label = QLabel("Thrust F: –")
        self.cf_label = QLabel("Cf: –")
        self.mdot_label = QLabel("Mass Flow ṁ: –")

        # Optional extended info
        self.mach_label = QLabel("Exit Mach: –")
        self.pe_label = QLabel("Exit Pressure Pe: –")

        layout.addWidget(self.thrust_label)
        layout.addWidget(self.cf_label)
        layout.addWidget(self.mdot_label)
        layout.addSpacing(10)
        layout.addWidget(self.mach_label)
        layout.addWidget(self.pe_label)

    def refresh(self) -> None:
        """
        Refresh displayed values from controller.result.
        Called after each solve.
        """
        result = self.controller.result
        if result is None:
            return

        # Main values
        self.thrust_label.setText(f"Thrust F: {result.F:.2f} N")
        self.cf_label.setText(f"Cf: {result.Cf:.4f}")
        self.mdot_label.setText(f"Mass Flow ṁ: {result.m_dot:.6f} kg/s")

        # Extended values
        Me = result.M[-1]
        Pe = result.P[-1]

        self.mach_label.setText(f"Exit Mach: {Me:.3f}")
        self.pe_label.setText(f"Exit Pressure Pe: {Pe:.2f} Pa")
