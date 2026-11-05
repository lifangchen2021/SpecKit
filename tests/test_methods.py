import numpy as np
import pytest

from neutron_spectrum_solver import METHODS, call_solver, NeuralSolverApp


@pytest.fixture
def synthetic_system():
    rng = np.random.default_rng(42)
    n_groups = 8
    n_react = 4
    A = rng.random((n_react, n_groups)) * 1e-2 + 1e-4
    x_true = rng.random(n_groups) * 1e3
    b = A @ x_true
    x0 = np.ones(n_groups, dtype=float) * 100.0
    return A, b, x0, n_groups


def test_all_methods_import():
    assert len(METHODS) >= 15
    for name, fn in METHODS.items():
        if fn is not None:
            assert callable(fn), f"{name} is not callable"


def test_call_solver_runs_all_methods(synthetic_system):
    A, b, x0, n = synthetic_system
    for name, fn in METHODS.items():
        if fn is None:
            continue
        try:
            x = call_solver(fn, A, b, x0, 200, 1e-6)
        except Exception as e:
            pytest.fail(f"{name} raised: {type(e).__name__}: {e}")
        arr = np.asarray(x).flatten()
        assert arr.shape == (n,), f"{name}: bad shape {arr.shape}"
        assert np.all(np.isfinite(arr)), f"{name}: non-finite values"
        assert not np.any(np.isnan(arr)), f"{name}: NaN values"


def test_builtin_gradient(synthetic_system):
    A, b, x0, n = synthetic_system
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    app = NeuralSolverApp(root)
    app.A = A.astype(np.float32)
    app.b = b.reshape(-1, 1).astype(np.float32)
    app.b_error = np.abs(b).reshape(-1, 1).astype(np.float32) * 0.05
    app.A_header = np.arange(n, dtype=np.float32)
    app.x_dummy = x0.reshape(1, -1).astype(np.float32)
    app.original_x_dummy = app.x_dummy.copy()
    app.check_ready()
    app.selected_method.set("SpecKit (gradient + log-smoothness)")
    xv, lh = app.run_one_training(1e3, app.b)
    arr = np.asarray(xv).flatten()
    assert arr.shape == (n,)
    assert np.all(arr >= 0)
    root.destroy()


def test_gui_instantiation():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    app = NeuralSolverApp(root)
    assert app is not None
    root.destroy()
