"""Lightweight API contract tests (requires fastapi + httpx / starlette test client)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from fastapi.testclient import TestClient
    from dashboard.fastapi_backend import app
    HAS_TESTCLIENT = True
except Exception:
    HAS_TESTCLIENT = False
    TestClient = None
    app = None

import pytest


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="FastAPI TestClient not available (pip install httpx)")
def test_status_endpoint():
    client = TestClient(app)
    r = client.get("/api/status")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "fab" in data
    assert "tools" in data["fab"]


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="FastAPI TestClient not available")
def test_simulate_endpoint():
    client = TestClient(app)
    r = client.post("/api/simulate", json={"num_wafers": 4, "steps": 2})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "result" in data or "avg_yield" in str(data)


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="FastAPI TestClient not available")
def test_secsgem_and_control():
    client = TestClient(app)
    r1 = client.post("/api/secsgem", json={"command": "START", "wafer_id": 7})
    assert r1.status_code == 200

    r2 = client.post("/api/control", json={"tool": "Etch", "action": "START"})
    assert r2.status_code == 200
    assert "new_state" in r2.json() or r2.json().get("status") == "ok"

    log = client.get("/api/secsgem/log")
    assert log.status_code == 200
    assert "log" in log.json()