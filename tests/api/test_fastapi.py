"""Integration tests for the FastAPI surface."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from modules.api.fastapi_app import app

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_knowledge_endpoint() -> None:
    response = client.get("/knowledge")
    assert response.status_code == 200
    payload = response.json()
    assert payload["version"], "Knowledge version should not be empty"
    assert payload["sha256"], "Knowledge hash should not be empty"


def test_coder_run_fixture_response() -> None:
    note = _read_fixture("ppl_nav_radial_tblb.txt")
    response = client.post("/v1/coder/run", json={"note": note})
    assert response.status_code == 200
    payload = response.json()
    codes = {entry["cpt"]: entry for entry in payload["codes"]}
    expected = {"31627", "+31654", "31629", "31628", "31624"}
    assert expected.issubset(codes.keys())
    assert "navigation_initiated" in codes["31627"].get("rule_trace", [])
    assert "radial_peripheral_localization" in codes["+31654"].get("rule_trace", [])

    mer_summary = payload.get("mer_summary") or {}
    adjustments = mer_summary.get("adjustments", [])
    assert adjustments, "MER summary should include adjustments"
    assert all(adj.get("role") for adj in adjustments)


def test_registry_run_normalizes_stations() -> None:
    note = _read_fixture("ebus_staging_4R_7_11R.txt")
    response = client.post("/v1/registry/run", json={"note": note, "explain": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["linear_ebus_stations"] == ["4R", "7", "11R"]
    evidence = payload.get("evidence", {})
    assert "linear_ebus_stations" in evidence
    assert evidence["linear_ebus_stations"], "Evidence for stations should be captured"
