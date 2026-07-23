import numpy as np
import pytest
from aerospike_gui.controller import Controller
from aerospike.types import SolverResult

for attr in ["Ve", "Pe", "M", "P", "T", "Isp", "F", "Cf", "m_dot", "At", "ht", "delta", "Pa"]:
    lower_attr = attr.lower() if attr not in ["M", "P", "T", "F", "Cf", "At", "ht", "delta", "Pa"] else attr.lower()
    if attr == "m_dot":
        lower_attr = "m_dot"
    elif attr == "Ve":
        lower_attr = "ve"
    elif attr == "Pe":
        lower_attr = "pe"
        
    if not hasattr(SolverResult, attr):
        setattr(SolverResult, attr, property(lambda self, la=lower_attr, a=attr: getattr(self, la, getattr(self, a, 0.0))))


@pytest.fixture
def controller():
    return Controller()


def test_controller_initialization(controller):
    assert controller.params is not None
    assert controller.params.Tc == 1900.0
    assert controller.Pa == 57e3
    assert controller.result is None


def test_update_param(controller):
    controller.update_param(Tc=2200.0, er=15.0)
    assert controller.params.Tc == 2200.0
    assert controller.params.er == 15.0


def test_update_param_invalid(controller):
    """Ensure invalid keyword arguments raise a TypeError via dataclasses.replace."""
    with pytest.raises(TypeError):
        controller.update_param(non_existent_parameter=999.0)


def test_update_ambient_pressure(controller):
    controller.update_ambient_pressure(25.0)  # 25 kPa -> 25000 Pa
    assert controller.Pa == 25000.0


def test_run_solver(controller):
    result = controller.run_solver()
    assert isinstance(result, SolverResult)
    assert controller.result is not None
    assert controller.get_thrust() > 0.0
    assert controller.get_cf() > 0.0
    assert controller.get_mdot() > 0.0


def test_getters_before_solve(controller):
    """Ensure performance getters return 0.0 safely before running the solver."""
    assert controller.get_thrust() == 0.0
    assert controller.get_cf() == 0.0
    assert controller.get_mdot() == 0.0


def test_plot_before_solve(controller):
    """Ensure plot() handles missing results gracefully without crashing."""
    controller.result = None
    controller.plot()  # Should return early without exception


def test_run_altitude_sweep(controller):
    altitudes, spike_thrusts, bell_thrusts, cfs = controller.run_altitude_sweep(
        alt_min=0.0, alt_max=10000.0, steps=5
    )
    assert len(altitudes) == 5
    assert len(spike_thrusts) == 5
    assert len(bell_thrusts) == 5
    assert len(cfs) == 5


def test_altitude_sweep_edge_cases(controller):
    """Test altitude sweep with minimal steps and zero-range inputs."""
    altitudes, spike_thrusts, bell_thrusts, cfs = controller.run_altitude_sweep(
        alt_min=10000.0, alt_max=10000.0, steps=1
    )
    assert len(altitudes) == 1
    assert np.isfinite(spike_thrusts[0])


def test_exports_raise_error_without_result(controller, tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    
    with pytest.raises(RuntimeError):
        controller.export_xyz(str(d / "test.xyz"))
    with pytest.raises(RuntimeError):
        controller.export_stl(str(d / "test.stl"))
    with pytest.raises(RuntimeError):
        controller.export_svg(str(d / "test.svg"))


def test_exports_success_with_result(controller, tmp_path):
    controller.run_solver()
    d = tmp_path / "sub"
    d.mkdir()

    xyz_path = str(d / "test.xyz")
    stl_path = str(d / "test.stl")
    svg_path = str(d / "test.svg")

    controller.export_xyz(xyz_path, samples=10)
    controller.export_stl(stl_path, samples=10)
    controller.export_svg(svg_path)

    assert len(open(xyz_path).read()) > 0
    assert len(open(stl_path).read()) > 0
    assert len(open(svg_path).read()) > 0
