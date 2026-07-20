from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from aerospike_gui.controller import Controller


class ExportPanel(QWidget):
    """
    Widget for exporting spike geometry to CAD-friendly XYZ files.
    """

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        group = QGroupBox("Export")
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(group)

        layout = QVBoxLayout(group)

        self.export_button = QPushButton("Export Spike Geometry (XYZ)")
        self.export_button.clicked.connect(self.on_export_clicked)

        layout.addWidget(self.export_button)

    @Slot()
    def on_export_clicked(self) -> None:
        """
        Open a save dialog and export spike geometry.
        """
        if self.controller.result is None:
            QMessageBox.warning(
                self,
                "No Solver Result",
                "Please run the solver before exporting geometry.",
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Spike Geometry",
            "",
            "XYZ Files (*.xyz);;Text Files (*.txt);;All Files (*)",
        )

        if not filename:
            return

        try:
            # Ensure .xyz extension if user didn't specify one
            if "." not in filename:
                filename += ".xyz"

            self.controller.export_xyz(filename)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Spike geometry exported to:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting:\n{e}",
            )
