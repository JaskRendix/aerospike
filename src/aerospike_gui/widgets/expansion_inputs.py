from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QRadioButton,
    QWidget,
)

from aerospike.flow import get_er_from_Pe, get_Pe
from aerospike_gui.controller import Controller


class ExpansionInputsWidget(QWidget):
    """
    Widget for nozzle expansion settings:
    - Expansion ratio er = Ae/At
    - Exit pressure Pe [kPa]
    Allows switching between er mode and Pe mode.
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QFormLayout(self)

        # --- Mode selection: er or Pe ---
        mode_layout = QHBoxLayout()
        self.er_mode = QRadioButton("Expansion Ratio er [-]")
        self.pe_mode = QRadioButton("Exit Pressure Pe [kPa]")

        self.er_mode.setChecked(True)

        self.er_mode.toggled.connect(self.on_mode_changed)
        self.pe_mode.toggled.connect(self.on_mode_changed)

        mode_layout.addWidget(self.er_mode)
        mode_layout.addWidget(self.pe_mode)
        layout.addRow("Expansion Mode", mode_layout)

        # --- Expansion Ratio er ---
        self.er_box = QDoubleSpinBox()
        self.er_box.setRange(1.0, 100.0)
        self.er_box.setDecimals(1)
        self.er_box.setSingleStep(1.0)
        self.er_box.setValue(controller.params.er)
        self.er_box.valueChanged.connect(self.on_er_changed)
        layout.addRow("er [-]", self.er_box)

        # --- Exit Pressure Pe [kPa] ---
        Pe_kPa = get_Pe(controller.params) / 1e3

        self.pe_box = QDoubleSpinBox()
        self.pe_box.setRange(0.0, 500.0)
        self.pe_box.setDecimals(1)
        self.pe_box.setSingleStep(1.0)
        self.pe_box.setValue(Pe_kPa)
        self.pe_box.valueChanged.connect(self.on_pe_changed)
        self.pe_box.setEnabled(False)
        layout.addRow("Pe [kPa]", self.pe_box)

    @Slot()
    def on_mode_changed(self) -> None:
        """
        Enable/disable input boxes depending on selected mode.
        """
        if self.er_mode.isChecked():
            self.er_box.setEnabled(True)
            self.pe_box.setEnabled(False)
        else:
            self.er_box.setEnabled(False)
            self.pe_box.setEnabled(True)

    @Slot(float)
    def on_er_changed(self, value: float) -> None:
        """
        er changed in GUI.
        Update controller and Pe box.
        """
        self.controller.update_param(er=value)
        Pe = get_Pe(self.controller.params)
        self.pe_box.setValue(Pe / 1e3)

    @Slot(float)
    def on_pe_changed(self, value: float) -> None:
        """
        Pe changed in GUI (kPa → Pa).
        Convert Pe → er and update controller.
        """
        Pe_Pa = value * 1e3
        er_new = get_er_from_Pe(self.controller.params, Pe_Pa)
        self.controller.update_param(er=er_new)
        self.er_box.setValue(er_new)
