from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class SolvePanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)

        self.main_window = main_window

        layout = QVBoxLayout()

        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.main_window.run_solver)

        layout.addWidget(self.solve_button)
        self.setLayout(layout)
