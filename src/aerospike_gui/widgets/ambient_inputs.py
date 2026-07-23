from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QRadioButton,
    QWidget,
)

from aerospike.flow import get_alt_from_Pa, get_Pa_from_alt
from aerospike_gui.controller import Controller

ALTITUDE_PRESETS = {
    "Custom / Manual": None,
    "Sea Level (0 m)": 0.0,
    "5,000 m": 5000.0,
    "10,000 m": 10000.0,
    "Vacuum / Orbit": 40000.0,
}


class AmbientInputsWidget(QWidget):
    """
    Widget for ambient conditions:
    - Ambient pressure Pa [kPa]
    - Altitude AMSL [m]
    - Altitude/Pressure presets selector
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QFormLayout(self)

        # --- Altitude / Flight Presets ---
        self.alt_preset_combo = QComboBox()
        self.alt_preset_combo.addItems(list(ALTITUDE_PRESETS.keys()))
        self.alt_preset_combo.currentIndexChanged.connect(self.on_preset_selected)
        layout.addRow("Flight Regime Preset", self.alt_preset_combo)

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
        self.pa_box.setDecimals(3)
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

    @Slot(int)
    def on_preset_selected(self, index: int) -> None:
        name = self.alt_preset_combo.currentText()
        alt = ALTITUDE_PRESETS.get(name)
        if alt is None:
            return  # Custom selected

        # Switch to altitude mode automatically when choosing an altitude preset
        self.alt_mode.setChecked(True)
        self.alt_box.setValue(alt)

    @Slot()
    def on_mode_changed(self) -> None:
        if self.pa_mode.isChecked():
            self.pa_box.setEnabled(True)
            self.alt_box.setEnabled(False)
        else:
            self.pa_box.setEnabled(False)
            self.alt_box.setEnabled(True)

    @Slot(float)
    def on_pa_changed(self, value: float) -> None:
        self.alt_preset_combo.setCurrentText("Custom / Manual")
        self.controller.update_ambient_pressure(value)
        self.alt_box.blockSignals(True)
        self.alt_box.setValue(get_alt_from_Pa(self.controller.Pa))
        self.alt_box.blockSignals(False)

    @Slot(float)
    def on_alt_changed(self, value: float) -> None:
        Pa = get_Pa_from_alt(value)
        self.controller.update_ambient_pressure(Pa / 1e3)
        self.pa_box.blockSignals(True)
        self.pa_box.setValue(Pa / 1e3)
        self.pa_box.blockSignals(False)
