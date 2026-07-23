import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox
from aerospike_gui.window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    """Ensure a single QApplication instance exists for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def main_window(qapp):
    """Instantiate MainWindow and ensure cleanup."""
    window = MainWindow()
    yield window
    window.close()


def test_main_window_initialization(main_window):
    """Verify MainWindow sets up layouts, controller, panels, and initial solve."""
    assert main_window is not None
    assert main_window.controller is not None
    assert main_window.controller.result is not None
    assert main_window.windowTitle().startswith("Aerospike Nozzle Design")


def test_refresh_all(main_window):
    """Verify _refresh_all runs safely without exceptions."""
    main_window._refresh_all()


def test_run_solver_success(main_window, monkeypatch):
    """Verify solver execution updates the UI and controller state successfully."""
    # Mock panel refresh methods to isolate window logic
    monkeypatch.setattr(main_window.results_panel, "refresh", lambda: None)
    monkeypatch.setattr(main_window.plot_panel, "refresh", lambda: None)

    main_window.run_solver()
    assert main_window.controller.result is not None


def test_run_solver_exception_handling(main_window, monkeypatch):
    """Verify that solver exceptions trigger a critical message box instead of crashing."""
    def mock_fail():
        raise RuntimeError("Simulated solver failure")

    monkeypatch.setattr(main_window.controller, "run_solver", mock_fail)
    
    # Capture/mock QMessageBox.critical to prevent blocking modal dialogs during tests
    error_triggered = []
    monkeypatch.setattr(
        QMessageBox, 
        "critical", 
        lambda parent, title, text: error_triggered.append((title, text))
    )

    main_window.run_solver()
    assert len(error_triggered) == 1
    assert "Solver Error" in error_triggered[0][0]


def test_on_config_loaded(main_window, monkeypatch):
    """Verify configuration load signal handler triggers panel refreshing and re-solving."""
    refreshed_widgets = []
    
    for widget in (
        main_window.engine_inputs,
        main_window.ambient_inputs,
        main_window.expansion_inputs,
        main_window.sizing_inputs,
    ):
        if hasattr(widget, "refresh_from_controller"):
            monkeypatch.setattr(widget, "refresh_from_controller", lambda w=widget: refreshed_widgets.append(w))

    solve_called = []
    monkeypatch.setattr(main_window, "run_solver", lambda: solve_called.append(True))

    main_window._on_config_loaded()
    assert len(solve_called) == 1
    assert len(refreshed_widgets) >= 4


def test_altitude_sweep_plot_execution(main_window, monkeypatch):
    """Verify altitude sweep popup plot runs successfully and handles execution flow."""
    # Prevent matplotlib from opening blocking GUI windows during test runs
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)
    
    # Run sweep plot method
    try:
        main_window.run_altitude_sweep_plot()
    except Exception as e:
        pytest.fail(f"run_altitude_sweep_plot raised an unexpected exception: {e}")


def test_altitude_sweep_plot_error_handling(main_window, monkeypatch):
    """Verify altitude sweep plot catches errors gracefully via message box."""
    def mock_sweep_fail():
        raise RuntimeError("Sweep calculation failed")

    monkeypatch.setattr(main_window.controller, "run_altitude_sweep", mock_sweep_fail)

    error_triggered = []
    monkeypatch.setattr(
        QMessageBox, 
        "critical", 
        lambda parent, title, text: error_triggered.append((title, text))
    )

    main_window.run_altitude_sweep_plot()
    assert len(error_triggered) == 1
    assert "Sweep Error" in error_triggered[0][0]
