from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QRadioButton,
    QWidget,
)

from aerospike.flow import get_alt_from_Pa, get_Pa_from_alt
from aerospike_gui.controller import Controller


class AmbientInputsWidget(QWidget):
    """
    Widget for ambient conditions:
    - Ambient pressure Pa [kPa]
    - Altitude AMSL [m]
    Allows switching between pressure input and altitude input.
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QFormLayout(self)

        # --- Mode selection: Pa or altitude ---
        mode_layout = QHBoxLayout()
        self.pa_mode = QRadioButton("Ambient Pressure [kPa]")
        self.alt_mode = QRadioButton("Altitude AMSL [m]")

        self.pa_mode.setChecked(True)

        self.pa_mode.toggled.connect(self.on_mode_changed)
        self.alt_mode.toggled.connect(self.on_mode_changed)

        mode_layout.addWidget(self.pa_mode)
        mode_layout.addWidget(self.alt_mode)
        layout.addRow("Ambient Mode", mode_layout)

        # --- Ambient Pressure Pa [kPa] ---
        self.pa_box = QDoubleSpinBox()
        self.pa_box.setRange(0.0, 110.0)
        self.pa_box.setDecimals(1)
        self.pa_box.setSingleStep(1.0)
        self.pa_box.setValue(controller.Pa / 1e3)
        self.pa_box.valueChanged.connect(self.on_pa_changed)
        layout.addRow("Pa [kPa]", self.pa_box)

        # --- Altitude AMSL [m] ---
        self.alt_box = QDoubleSpinBox()
        self.alt_box.setRange(0.0, 44000.0)
        self.alt_box.setDecimals(0)
        self.alt_box.setSingleStep(100.0)
        self.alt_box.setValue(get_alt_from_Pa(controller.Pa))
        self.alt_box.valueChanged.connect(self.on_alt_changed)
        self.alt_box.setEnabled(False)
        layout.addRow("Altitude [m]", self.alt_box)

    @Slot()
    def on_mode_changed(self) -> None:
        """
        Enable/disable input boxes depending on selected mode.
        """
        if self.pa_mode.isChecked():
            self.pa_box.setEnabled(True)
            self.alt_box.setEnabled(False)
        else:
            self.pa_box.setEnabled(False)
            self.alt_box.setEnabled(True)

    @Slot(float)
    def on_pa_changed(self, value: float) -> None:
        """
        Pa changed in GUI (kPa → Pa).
        Update controller and altitude box.
        """
        self.controller.update_ambient_pressure(value)
        self.alt_box.setValue(get_alt_from_Pa(self.controller.Pa))

    @Slot(float)
    def on_alt_changed(self, value: float) -> None:
        """
        Altitude changed in GUI (m → Pa).
        Update controller and pressure box.
        """
        Pa = get_Pa_from_alt(value)
        self.controller.update_ambient_pressure(Pa / 1e3)
        self.pa_box.setValue(Pa / 1e3)
