import matplotlib

matplotlib.use("Agg")  # headless backend for CI

import matplotlib.pyplot as plt
import numpy as np
import pytest

# IMPORTANT:
# We now import the standalone plotting function
# not the GUI version.
from aerospike.plotting import plot_results
from aerospike.types import SolverResult


@pytest.fixture
def fake_result() -> SolverResult:
    N = 20
    return SolverResult(
        M=np.linspace(1, 2, N),
        Rx_over_Re=np.linspace(1.0, 0.2, N),
        X_over_Re=np.linspace(0.0, 1.0, N),
        P=np.linspace(5e6, 1e5, N),
        T=np.linspace(1900, 500, N),
        Isp=np.linspace(0, 300, N),
        F=1000.0,
        Cf=1.5,
        m_dot=0.2,
        At=0.0005,
        ht=0.005,
        delta=0.3,
        Pa=101e3,
    )


def test_plot_results_creates_figure(fake_result: SolverResult):
    plt.close("all")

    plot_results(fake_result)

    figs = list(map(plt.figure, plt.get_fignums()))
    assert len(figs) == 1

    fig = figs[0]
    assert len(fig.axes) == 6


@pytest.mark.parametrize("N", [5, 10, 50])
def test_plot_results_various_sizes(N: int):
    result = SolverResult(
        M=np.linspace(1, 2, N),
        Rx_over_Re=np.linspace(1.0, 0.2, N),
        X_over_Re=np.linspace(0.0, 1.0, N),
        P=np.linspace(5e6, 1e5, N),
        T=np.linspace(1900, 500, N),
        Isp=np.linspace(0, 300, N),
        F=500.0,
        Cf=1.2,
        m_dot=0.1,
        At=0.0003,
        ht=0.004,
        delta=0.25,
        Pa=50e3,
    )

    plt.close("all")
    plot_results(result)

    fig = plt.gcf()
    assert len(fig.axes) == 6

    for ax in fig.axes:
        assert len(ax.lines) + len(ax.texts) > 0


def test_plot_results_no_crash_on_zero_arrays():
    N = 10
    result = SolverResult(
        M=np.zeros(N),
        Rx_over_Re=np.zeros(N),
        X_over_Re=np.zeros(N),
        P=np.zeros(N),
        T=np.zeros(N),
        Isp=np.zeros(N),
        F=0.0,
        Cf=0.0,
        m_dot=0.0,
        At=0.0,
        ht=0.0,
        delta=0.0,
        Pa=0.0,
    )

    plt.close("all")
    plot_results(result)

    fig = plt.gcf()
    assert len(fig.axes) == 6


def test_plot_results_multiple_calls(fake_result: SolverResult):
    plt.close("all")

    plot_results(fake_result)
    plot_results(fake_result)  # ensure no accumulation

    fig = plt.gcf()
    for ax in fig.axes:
        assert len(ax.lines) <= 2
