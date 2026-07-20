from __future__ import annotations

import json
from dataclasses import asdict

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from aerospike.types import EngineParameters
from aerospike_gui.controller import Controller


class SaveLoadPanel(QWidget):
    """
    Widget for saving/loading engine parameters using JSON.
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        group = QGroupBox("Save / Load")
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(group)

        layout = QVBoxLayout(group)

        # Save button
        self.save_button = QPushButton("Save Engine Parameters")
        self.save_button.clicked.connect(self.on_save_clicked)
        layout.addWidget(self.save_button)

        # Load button
        self.load_button = QPushButton("Load Engine Parameters")
        self.load_button.clicked.connect(self.on_load_clicked)
        layout.addWidget(self.load_button)

    @Slot()
    def on_save_clicked(self) -> None:
        """
        Save current engine parameters to a JSON file.
        """
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Engine Parameters",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if not filename:
            return

        try:
            params_dict = asdict(self.controller.params)

            # Ensure .json extension
            if "." not in filename:
                filename += ".json"

            with open(filename, "w") as f:
                json.dump(params_dict, f, indent=4)

            QMessageBox.information(
                self,
                "Save Successful",
                f"Parameters saved to:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"An error occurred while saving:\n{e}",
            )

    @Slot()
    def on_load_clicked(self) -> None:
        """
        Load engine parameters from a JSON file.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Engine Parameters",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if not filename:
            return

        try:
            with open(filename, "r") as f:
                data = json.load(f)

            # Validate required fields
            required = {"Tc", "Pc", "molar_m", "gamma", "Re", "er"}
            if not required.issubset(data.keys()):
                raise ValueError("JSON file missing required fields.")

            # Construct new EngineParameters
            new_params = EngineParameters(
                Tc=float(data["Tc"]),
                Pc=float(data["Pc"]),
                molar_m=float(data["molar_m"]),
                gamma=float(data["gamma"]),
                Re=float(data["Re"]),
                er=float(data["er"]),
            )

            # Update controller
            self.controller.params = new_params

            QMessageBox.information(
                self,
                "Load Successful",
                f"Parameters loaded from:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"An error occurred while loading:\n{e}",
            )
