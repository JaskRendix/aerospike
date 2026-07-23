from __future__ import annotations

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from aerospike_gui.controller import Controller


class ExportPanel(QWidget):
    """Widget for exporting spike geometry to CAD-friendly XYZ files and 3D STL meshes."""

    def __init__(self, controller: Controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        group = QGroupBox("Export Geometry")
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(group)

        layout = QVBoxLayout(group)

        # Resolution dropdown
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Radial Resolution:"))
        self.res_combo = QComboBox()
        self.res_combo.addItems(["36 points (Fast)", "72 points (Standard)", "180 points (Detailed)", "360 points (High Res)"])
        self.res_combo.setCurrentIndex(1) # Default: 72 points
        res_layout.addWidget(self.res_combo)
        layout.addLayout(res_layout)

        # Export Buttons
        self.export_xyz_button = QPushButton("Export CAD Points (.XYZ)")
        self.export_xyz_button.clicked.connect(self.on_export_xyz_clicked)

        self.export_stl_button = QPushButton("Export 3D Mesh (.STL)")
        self.export_stl_button.clicked.connect(self.on_export_stl_clicked)

        self.export_svg_button = QPushButton("Export 2D Line Art (.SVG)")
        self.export_svg_button.clicked.connect(self.on_export_svg_clicked)

        layout.addWidget(self.export_xyz_button)
        layout.addWidget(self.export_stl_button)
        layout.addWidget(self.export_svg_button)

    def _get_samples(self) -> int:
        mapping = {0: 36, 1: 72, 2: 180, 3: 360}
        return mapping.get(self.res_combo.currentIndex(), 72)

    @Slot()
    def on_export_xyz_clicked(self) -> None:
        """Export point cloud for SolidWorks/Fusion 360 curve import."""
        self._handle_export(
            title="Export Spike Geometry (XYZ)",
            file_filter="XYZ Point Cloud (*.xyz);;Text Files (*.txt)",
            default_ext=".xyz",
            is_stl=False,
        )

    @Slot()
    def on_export_stl_clicked(self) -> None:
        """Export 3D printable ASCII STL solid mesh."""
        self._handle_export(
            title="Export Spike 3D Mesh (STL)",
            file_filter="STL 3D Mesh (*.stl)",
            default_ext=".stl",
            is_stl=True,
        )

    @Slot()
    def on_export_svg_clicked(self) -> None:
        """Export 2D contour vector graphic for laser cutting / CAD."""
        if self.controller.result is None:
            QMessageBox.warning(
                self,
                "No Solver Result",
                "Please run the solver before exporting geometry.",
            )
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Export 2D Line Art (SVG)", "", "Scalable Vector Graphics (*.svg)"
        )

        if not filename:
            return

        try:
            if not filename.lower().endswith(".svg"):
                filename += ".svg"

            if hasattr(self.controller, "export_svg"):
                self.controller.export_svg(filename)
            else:
                from aerospike.geometry import export_spike_svg
                content = export_spike_svg(self.controller.result)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)

            QMessageBox.information(
                self,
                "Export Successful",
                f"2D vector line art successfully exported to:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting:\n{e}",
            )

    def _handle_export(
        self, title: str, file_filter: str, default_ext: str, is_stl: bool
    ) -> None:
        if self.controller.result is None:
            QMessageBox.warning(
                self,
                "No Solver Result",
                "Please run the solver before exporting geometry.",
            )
            return

        filename, selected_filter = QFileDialog.getSaveFileName(
            self, title, "", file_filter
        )

        if not filename:
            return

        try:
            if not filename.lower().endswith((default_ext, ".txt")):
                filename += default_ext

            samples = self._get_samples()

            # Call controller helper (or geometry module directly)
            if is_stl:
                if hasattr(self.controller, "export_stl"):
                    self.controller.export_stl(filename, samples=samples)
                else:
                    # Direct geometry fallback if controller method isn't wrapped yet
                    from aerospike.geometry import export_spike_stl
                    content = export_spike_stl(self.controller.result, radial_samples=samples)
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)
            else:
                if hasattr(self.controller, "export_xyz"):
                    self.controller.export_xyz(filename, samples=samples)
                else:
                    from aerospike.geometry import export_spike_xyz
                    content = export_spike_xyz(self.controller.result, samples=samples)
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(content)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Geometry successfully exported to:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred while exporting:\n{e}",
            )
