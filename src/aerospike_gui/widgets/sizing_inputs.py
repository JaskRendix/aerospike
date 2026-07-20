from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QRadioButton,
    QWidget,
)

from aerospike.flow import get_Re_from_thrust, get_thrust
from aerospike_gui.controller import Controller


class SizingInputsWidget(QWidget):
    """
    Widget for nozzle sizing:
    - Desired thrust F [N]
    - Exit radius Re [mm]
    Allows switching between thrust mode and exit-radius mode.
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QFormLayout(self)

        # --- Mode selection: thrust or exit radius ---
        mode_layout = QHBoxLayout()
        self.f_mode = QRadioButton("Desired Thrust F [N]")
        self.re_mode = QRadioButton("Exit Radius Re [mm]")

        self.f_mode.setChecked(True)

        self.f_mode.toggled.connect(self.on_mode_changed)
        self.re_mode.toggled.connect(self.on_mode_changed)

        mode_layout.addWidget(self.f_mode)
        mode_layout.addWidget(self.re_mode)
        layout.addRow("Sizing Mode", mode_layout)

        # --- Thrust F [N] ---
        F_default = get_thrust(controller.params)

        self.f_box = QDoubleSpinBox()
        self.f_box.setRange(0.0, 1e6)
        self.f_box.setDecimals(0)
        self.f_box.setSingleStep(100.0)
        self.f_box.setValue(F_default)
        self.f_box.valueChanged.connect(self.on_f_changed)
        layout.addRow("Thrust F [N]", self.f_box)

        # --- Exit Radius Re [mm] ---
        self.re_box = QDoubleSpinBox()
        self.re_box.setRange(0.0, 500.0)
        self.re_box.setDecimals(3)
        self.re_box.setSingleStep(1.0)
        self.re_box.setValue(controller.params.Re * 1e3)
        self.re_box.valueChanged.connect(self.on_re_changed)
        self.re_box.setEnabled(False)
        layout.addRow("Exit Radius Re [mm]", self.re_box)

    @Slot()
    def on_mode_changed(self) -> None:
        """
        Enable/disable input boxes depending on selected mode.
        """
        if self.f_mode.isChecked():
            self.f_box.setEnabled(True)
            self.re_box.setEnabled(False)
        else:
            self.f_box.setEnabled(False)
            self.re_box.setEnabled(True)

    @Slot(float)
    def on_f_changed(self, value: float) -> None:
        """
        Thrust changed in GUI.
        Convert F → Re and update controller.
        """
        Re_new = get_Re_from_thrust(self.controller.params, value)
        self.controller.update_param(Re=Re_new)
        self.re_box.setValue(Re_new * 1e3)

    @Slot(float)
    def on_re_changed(self, value: float) -> None:
        """
        Exit radius changed in GUI (mm → m).
        Convert Re → F and update controller.
        """
        Re_m = value * 1e-3
        self.controller.update_param(Re=Re_m)
        F_new = get_thrust(self.controller.params)
        self.f_box.setValue(F_new)
