"""Tests for predictive maintenance (with fallback when sklearn missing)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fabforge.predictive_maintenance import PredictiveMaintenance


def test_predictive_train_and_predict():
    pm = PredictiveMaintenance()
    pm.train()  # should be safe even if no sklearn (it uses its own generator)
    out = pm.predict({"temp": 210, "vibration": 0.65, "pressure": 0.012, "runtime": 4500})
    assert "failure_prob" in out
    assert "alert" in out
    assert isinstance(out["alert"], bool)
    assert 0.0 <= out["failure_prob"] <= 1.0


def test_predictive_alert_threshold():
    pm = PredictiveMaintenance()
    # Force a high-risk input
    out = pm.predict({"temp": 280, "vibration": 0.95, "pressure": 0.03, "runtime": 9800})
    # Heuristic or model should be willing to flag high
    assert out["failure_prob"] > 0.5 or out["alert"] is True  # tolerant of pure heuristic mode