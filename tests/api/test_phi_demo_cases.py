"""Tests for non-PHI PHI demo cases endpoints."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")
os.environ.setdefault("PHI_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("PHI_ENCRYPTION_MODE", "demo")

from modules.api.fastapi_app import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_store(monkeypatch):
    # Replace the store with a fresh in-memory instance for tests
    from modules.api import phi_demo_store

    phi_demo_store._store = phi_demo_store.InMemoryPhiDemoStore()  # type: ignore
    yield


@pytest.fixture()
def client():
    return TestClient(app)


def test_create_and_list_cases(client):
    resp = client.post(
        "/api/v1/phi-demo/cases",
        json={
            "synthetic_patient_label": "Patient X",
            "procedure_date": "2024-01-01",
            "operator_name": "Dr. Jane Test",
            "scenario_label": "Synthetic bronchoscopy",
        },
    )
    assert resp.status_code == 201
    case_id = resp.json()["id"]

    list_resp = client.get("/api/v1/phi-demo/cases")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert len(data) == 1
    assert data[0]["id"] == case_id
    assert data[0]["procedure_id"] is None


def test_attach_procedure(client):
    create_resp = client.post(
        "/api/v1/phi-demo/cases",
        json={
            "synthetic_patient_label": "Patient X",
            "procedure_date": "2024-01-02",
            "operator_name": "Dr. Jane Test",
            "scenario_label": "Demo case",
        },
    )
    case_id = create_resp.json()["id"]
    proc_id = str(uuid.uuid4())

    attach_resp = client.put(
        f"/api/v1/phi-demo/cases/{case_id}/procedure",
        json={"procedure_id": proc_id},
    )
    assert attach_resp.status_code == 200
    assert attach_resp.json()["procedure_id"] == proc_id
