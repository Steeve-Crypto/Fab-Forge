"""Tests for the Python simulation core (and native if available)."""
import sys
import os
import pytest

# Make package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fabforge.cli import _python_simulate, _try_native_simulate


def test_python_simulate_basic():
    res = _python_simulate(5, 3)
    assert res["num_wafers"] == 5
    assert res["steps"] == 3
    assert 0.90 < res["avg_yield"] < 1.0
    assert len(res["wafers"]) == 5
    for w in res["wafers"]:
        assert 0.0 < w["yield"] <= 1.0
        assert isinstance(w["history"], list)
        assert len(w["history"]) == 3


def test_python_simulate_yield_degrades():
    res1 = _python_simulate(3, 2)
    res2 = _python_simulate(3, 5)  # more steps -> generally lower or equal yield
    assert res2["avg_yield"] <= res1["avg_yield"] + 0.02


def test_native_or_fallback():
    # Should never crash; either native or raises cleanly
    try:
        res = _try_native_simulate(4, 2)
        assert res["mode"] in ("native-cpp-pybind11", "native-cpp-exe")
    except RuntimeError as e:
        assert "No usable native" in str(e) or "not available" in str(e).lower()


def test_simulate_mode_field():
    res = _python_simulate(2, 2)
    assert "mode" in res
    assert res["mode"] == "python-fallback"