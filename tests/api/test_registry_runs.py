from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from modules.api.dependencies import get_coding_service, get_registry_service
from modules.api.fastapi_app import app
from modules.phi.db import Base
from modules.registry_store.dependencies import get_registry_store_engine
from modules.registry_store.models import RegistryRun


@pytest.fixture
def registry_store_db(tmp_path, monkeypatch):
    db_path = tmp_path / "registry_store.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("REGISTRY_RUNS_PERSIST_ENABLED", "1")
    monkeypatch.delenv("REGISTRY_RUNS_ALLOW_PHI_RISK_PERSIST", raising=False)

    engine = get_registry_store_engine()
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(registry_store_db):
    # registry_store_db fixture sets env + creates tables
    return TestClient(app)


@pytest.fixture
def mock_registry_service():
    service_mock = MagicMock()
    app.dependency_overrides[get_registry_service] = lambda: service_mock
    yield service_mock
    app.dependency_overrides.pop(get_registry_service, None)


@pytest.fixture
def stub_coding_service():
    class StubKBRepo:
        version = "test_kb"

        def get_procedure_info(self, _code: str):
            return None

    class StubCodingService:
        kb_repo = StubKBRepo()

    app.dependency_overrides[get_coding_service] = lambda: StubCodingService()
    yield
    app.dependency_overrides.pop(get_coding_service, None)


def _stub_registry_extraction_result(*, note_text: str):
    record = SimpleNamespace(model_dump=lambda **_: {})
    return SimpleNamespace(
        record=record,
        cpt_codes=["31622"],
        coder_difficulty="HIGH_CONF",
        coder_source="stub",
        mapped_fields={},
        code_rationales={"31622": "stub"},
        derivation_warnings=[],
        warnings=[],
        needs_manual_review=False,
        validation_errors=[],
        audit_warnings=[],
    )


def test_create_registry_run_persists_row(
    client: TestClient,
    registry_store_db,
    mock_registry_service,
    stub_coding_service,
):
    mock_registry_service.extract_fields.side_effect = lambda note_text: _stub_registry_extraction_result(
        note_text=note_text
    )

    resp = client.post(
        "/api/v1/registry/runs",
        json={
            "note": "Scrubbed note text",
            "already_scrubbed": True,
            "include_financials": False,
            "submitter_name": "Alice",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["run_id"]
    assert body["result"]["cpt_codes"] == ["31622"]

    run_id = body["run_id"]
    row = registry_store_db.get(RegistryRun, run_id)
    assert row is not None
    assert row.submitter_name == "Alice"
    assert row.note_text == "Scrubbed note text"
    assert row.raw_response_json.get("cpt_codes") == ["31622"]


def test_feedback_once_enforced(
    client: TestClient,
    registry_store_db,
    mock_registry_service,
    stub_coding_service,
):
    mock_registry_service.extract_fields.side_effect = lambda note_text: _stub_registry_extraction_result(
        note_text=note_text
    )

    create = client.post(
        "/api/v1/registry/runs",
        json={"note": "Scrubbed note text", "already_scrubbed": True, "include_financials": False},
    )
    assert create.status_code == 200
    run_id = create.json()["run_id"]

    first = client.post(
        f"/api/v1/registry/runs/{run_id}/feedback",
        json={"reviewer_name": "Bob", "rating": 9, "comment": "Looks good"},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/registry/runs/{run_id}/feedback",
        json={"reviewer_name": "Bob", "rating": 9, "comment": "Second attempt"},
    )
    assert second.status_code == 409

    row = registry_store_db.get(RegistryRun, run_id)
    assert row is not None
    assert row.feedback_reviewer_name == "Bob"
    assert row.feedback_rating == 9
    assert row.feedback_submitted_at is not None


def test_correction_upsert(
    client: TestClient,
    registry_store_db,
    mock_registry_service,
    stub_coding_service,
):
    mock_registry_service.extract_fields.side_effect = lambda note_text: _stub_registry_extraction_result(
        note_text=note_text
    )

    create = client.post(
        "/api/v1/registry/runs",
        json={"note": "Scrubbed note text", "already_scrubbed": True, "include_financials": False},
    )
    assert create.status_code == 200
    run_id = create.json()["run_id"]

    first = client.put(
        f"/api/v1/registry/runs/{run_id}/correction",
        json={
            "corrected_response_json": {"edited_for_training": True, "cpt_codes": ["12345"]},
            "edited_tables_json": [{"id": "coding_selected", "rows": [{"code": "12345"}]}],
            "editor_name": "Carol",
        },
    )
    assert first.status_code == 200

    second = client.put(
        f"/api/v1/registry/runs/{run_id}/correction",
        json={
            "corrected_response_json": {"edited_for_training": True, "cpt_codes": ["99999"]},
            "edited_tables_json": [{"id": "coding_selected", "rows": [{"code": "99999"}]}],
            "editor_name": "Carol",
        },
    )
    assert second.status_code == 200

    row = registry_store_db.get(RegistryRun, run_id)
    assert row is not None
    assert row.correction_editor_name == "Carol"
    assert row.corrected_at is not None
    assert row.corrected_response_json.get("cpt_codes") == ["99999"]


def test_persistence_phi_gate_rejects_obvious_phi_like_strings(
    client: TestClient,
    registry_store_db,
    mock_registry_service,
    stub_coding_service,
):
    mock_registry_service.extract_fields.side_effect = lambda note_text: _stub_registry_extraction_result(
        note_text=note_text
    )

    resp = client.post(
        "/api/v1/registry/runs",
        json={
            "note": "DOB: 01/02/1980\\nMRN: 1234567",
            "already_scrubbed": True,
            "include_financials": False,
        },
    )
    assert resp.status_code == 400

    rows = registry_store_db.query(RegistryRun).all()
    assert rows == []


def test_persistence_phi_gate_can_allow_persist_with_flag(
    client: TestClient,
    registry_store_db,
    mock_registry_service,
    stub_coding_service,
    monkeypatch,
):
    monkeypatch.setenv("REGISTRY_RUNS_ALLOW_PHI_RISK_PERSIST", "true")
    mock_registry_service.extract_fields.side_effect = lambda note_text: _stub_registry_extraction_result(
        note_text=note_text
    )

    resp = client.post(
        "/api/v1/registry/runs",
        json={
            "note": "DOB: 01/02/1980\\nMRN: 1234567",
            "already_scrubbed": True,
            "include_financials": False,
        },
    )
    assert resp.status_code == 200
    run_id = resp.json()["run_id"]

    row = registry_store_db.get(RegistryRun, run_id)
    assert row is not None
    assert row.review_status == "phi_risk"
    assert row.needs_manual_review is True

