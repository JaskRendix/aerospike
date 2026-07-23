from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QSpinBox, QWidget

from aerospike_gui.controller import Controller

PROPELLANT_PRESETS = {
    "Custom": {"gamma": 1.27, "tc": 1900.0, "molar_m": 20.18},
    "LOX / Methane": {"gamma": 1.20, "tc": 3500.0, "molar_m": 20.5},
    "LOX / RP-1": {"gamma": 1.24, "tc": 3600.0, "molar_m": 22.0},
    "LOX / LH2": {"gamma": 1.26, "tc": 3200.0, "molar_m": 10.0},
    "N2O / HTPB (Hybrid)": {"gamma": 1.25, "tc": 3100.0, "molar_m": 25.0},
}


class EngineInputsWidget(QWidget):
    """
    Widget containing all engine parameter inputs:
    Tc, Pc, molar mass, gamma, er, Re, truncation, flange, and bolt configuration,
    plus propellant presets.
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        form = QFormLayout(self)

        # --- Propellant Presets Dropdown ---
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PROPELLANT_PRESETS.keys()))
        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)
        form.addRow("Propellant Preset", self.preset_combo)

        # --- Chamber Temperature Tc [K] ---
        self.tc_box = QDoubleSpinBox()
        self.tc_box.setRange(0.0, 10000.0)
        self.tc_box.setValue(controller.params.Tc)
        self.tc_box.valueChanged.connect(self.on_tc_changed)
        form.addRow("Chamber Temperature Tc [K]", self.tc_box)

        # --- Chamber Pressure Pc [MPa] ---
        self.pc_box = QDoubleSpinBox()
        self.pc_box.setRange(0.0, 100.0)
        self.pc_box.setDecimals(2)
        self.pc_box.setSingleStep(0.1)
        self.pc_box.setValue(controller.params.Pc / 1e6)
        self.pc_box.valueChanged.connect(self.on_pc_changed)
        form.addRow("Chamber Pressure Pc [MPa]", self.pc_box)

        # --- Molar Mass [g/mol] ---
        self.mm_box = QDoubleSpinBox()
        self.mm_box.setRange(0.0, 1000.0)
        self.mm_box.setDecimals(1)
        self.mm_box.setValue(controller.params.molar_m)
        self.mm_box.valueChanged.connect(self.on_mm_changed)
        form.addRow("Molar Mass [g/mol]", self.mm_box)

        # --- Gamma [-] ---
        self.gamma_box = QDoubleSpinBox()
        self.gamma_box.setRange(1.0, 2.0)
        self.gamma_box.setDecimals(2)
        self.gamma_box.setSingleStep(0.01)
        self.gamma_box.setValue(controller.params.gamma)
        self.gamma_box.valueChanged.connect(self.on_gamma_changed)
        form.addRow("Gamma [-]", self.gamma_box)

        # --- Expansion Ratio er [-] ---
        self.er_box = QDoubleSpinBox()
        self.er_box.setRange(1.0, 100.0)
        self.er_box.setDecimals(1)
        self.er_box.setSingleStep(1.0)
        self.er_box.setValue(controller.params.er)
        self.er_box.valueChanged.connect(self.on_er_changed)
        form.addRow("Expansion Ratio er [-]", self.er_box)

        # --- Exit Radius Re [mm] ---
        self.re_box = QDoubleSpinBox()
        self.re_box.setRange(0.0, 500.0)
        self.re_box.setDecimals(3)
        self.re_box.setValue(controller.params.Re * 1e3)
        self.re_box.valueChanged.connect(self.on_re_changed)
        form.addRow("Exit Radius Re [mm]", self.re_box)

        # --- Spike Length Ratio (Truncation) ---
        self.trunc_box = QDoubleSpinBox()
        self.trunc_box.setRange(0.4, 1.0)
        self.trunc_box.setSingleStep(0.05)
        self.trunc_box.setDecimals(2)
        self.trunc_box.setValue(getattr(controller.params, "truncation", 1.0))
        self.trunc_box.valueChanged.connect(self.on_truncation_changed)
        form.addRow("Spike Length Ratio", self.trunc_box)

        # --- Flange Thickness [mm] ---
        self.flange_thick_box = QDoubleSpinBox()
        self.flange_thick_box.setRange(0.0, 20.0)
        self.flange_thick_box.setSingleStep(1.0)
        self.flange_thick_box.setDecimals(2)
        self.flange_thick_box.setValue(getattr(controller.params, "flange_thickness", 0.005) * 1e3)
        self.flange_thick_box.valueChanged.connect(self.on_flange_thick_changed)
        form.addRow("Flange Thickness [mm]", self.flange_thick_box)

        # --- Flange Radius [mm] ---
        self.flange_rad_box = QDoubleSpinBox()
        self.flange_rad_box.setRange(1.0, 100.0)
        self.flange_rad_box.setSingleStep(1.0)
        self.flange_rad_box.setDecimals(2)
        self.flange_rad_box.setValue(getattr(controller.params, "flange_radius", 0.025) * 1e3)
        self.flange_rad_box.valueChanged.connect(self.on_flange_rad_changed)
        form.addRow("Flange Radius [mm]", self.flange_rad_box)

        # --- Bolt Circle Radius [mm] ---
        self.bolt_circle_box = QDoubleSpinBox()
        self.bolt_circle_box.setRange(1.0, 80.0)
        self.bolt_circle_box.setSingleStep(1.0)
        self.bolt_circle_box.setDecimals(2)
        self.bolt_circle_box.setValue(getattr(controller.params, "bolt_circle_radius", 0.020) * 1e3)
        self.bolt_circle_box.valueChanged.connect(self.on_bolt_circle_changed)
        form.addRow("Bolt Circle Radius [mm]", self.bolt_circle_box)

        # --- Bolt Count ---
        self.bolt_count_box = QSpinBox()
        self.bolt_count_box.setRange(0, 24)
        self.bolt_count_box.setValue(getattr(controller.params, "bolt_count", 6))
        self.bolt_count_box.valueChanged.connect(self.on_bolt_count_changed)
        form.addRow("Bolt Count", self.bolt_count_box)

        # --- Bolt Hole Radius [mm] ---
        self.bolt_hole_box = QDoubleSpinBox()
        self.bolt_hole_box.setRange(0.0, 5.0)
        self.bolt_hole_box.setSingleStep(0.5)
        self.bolt_hole_box.setDecimals(2)
        self.bolt_hole_box.setValue(getattr(controller.params, "bolt_hole_radius", 0.002) * 1e3)
        self.bolt_hole_box.valueChanged.connect(self.on_bolt_hole_changed)
        form.addRow("Bolt Hole Radius [mm]", self.bolt_hole_box)

    @Slot(int)
    def on_preset_selected(self, index: int) -> None:
        name = self.preset_combo.currentText()
        if name not in PROPELLANT_PRESETS or name == "Custom":
            return
        props = PROPELLANT_PRESETS[name]
        
        self.tc_box.blockSignals(True)
        self.gamma_box.blockSignals(True)
        self.mm_box.blockSignals(True)

        self.tc_box.setValue(props["tc"])
        self.gamma_box.setValue(props["gamma"])
        self.mm_box.setValue(props["molar_m"])

        self.tc_box.blockSignals(False)
        self.gamma_box.blockSignals(False)
        self.mm_box.blockSignals(False)

        self.controller.update_param(
            Tc=props["tc"], gamma=props["gamma"], molar_m=props["molar_m"]
        )

    @Slot(float)
    def on_tc_changed(self, value: float) -> None:
        self.preset_combo.setCurrentText("Custom")
        self.controller.update_param(Tc=value)

    @Slot(float)
    def on_pc_changed(self, value: float) -> None:
        self.controller.update_param(Pc=value * 1e6)

    @Slot(float)
    def on_mm_changed(self, value: float) -> None:
        self.preset_combo.setCurrentText("Custom")
        self.controller.update_param(molar_m=value)

    @Slot(float)
    def on_gamma_changed(self, value: float) -> None:
        self.preset_combo.setCurrentText("Custom")
        self.controller.update_param(gamma=value)

    @Slot(float)
    def on_er_changed(self, value: float) -> None:
        self.controller.update_param(er=value)

    @Slot(float)
    def on_re_changed(self, value: float) -> None:
        self.controller.update_param(Re=value * 1e-3)

    @Slot(float)
    def on_truncation_changed(self, value: float) -> None:
        self.controller.update_param(truncation=value)

    @Slot(float)
    def on_flange_thick_changed(self, value: float) -> None:
        self.controller.update_param(flange_thickness=value * 1e-3)

    @Slot(float)
    def on_flange_rad_changed(self, value: float) -> None:
        self.controller.update_param(flange_radius=value * 1e-3)

    @Slot(float)
    def on_bolt_circle_changed(self, value: float) -> None:
        self.controller.update_param(bolt_circle_radius=value * 1e-3)

    @Slot(int)
    def on_bolt_count_changed(self, value: int) -> None:
        self.controller.update_param(bolt_count=value)

    @Slot(float)
    def on_bolt_hole_changed(self, value: float) -> None:
        self.controller.update_param(bolt_hole_radius=value * 1e-3)
