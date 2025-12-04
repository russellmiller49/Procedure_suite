"""API tests for /v1/phi endpoints using FastAPI TestClient.

All data is synthetic; raw PHI is only returned by the reidentify endpoint.
"""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

# Ensure warmup is skipped for tests and DB uses in-memory SQLite
os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")
os.environ.setdefault("PHI_DATABASE_URL", "sqlite:///:memory:")

from modules.api.fastapi_app import app  # noqa: E402
from modules.api.phi_dependencies import SessionLocal, engine  # noqa: E402
from modules.phi import models  # noqa: E402
from modules.phi.db import Base  # noqa: E402


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


def test_preview_endpoint_does_not_persist(client):
    resp = client.post(
        "/v1/phi/scrub/preview",
        json={"text": "Patient X synthetic note."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scrubbed_text"].startswith("[[REDACTED]]")
    assert data["entities"][0]["entity_type"] == "PERSON"

    db = SessionLocal()
    try:
        assert db.query(models.PHIVault).count() == 0
        assert db.query(models.ProcedureData).count() == 0
    finally:
        db.close()


def test_submit_creates_vault_and_procedure(client):
    resp = client.post(
        "/v1/phi/submit",
        json={
            "text": "Patient X synthetic note with token.",
            "submitted_by": "clinician_demo",
            "document_type": "demo_note",
            "specialty": "demo_specialty",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "procedure_id" in data
    assert data["status"] == models.ProcessingStatus.PENDING_REVIEW.value
    assert "Patient" not in data["scrubbed_text"]
    assert "text" not in data  # no raw text field

    db = SessionLocal()
    try:
        vaults = db.query(models.PHIVault).all()
        procs = db.query(models.ProcedureData).all()
        audits = db.query(models.AuditLog).all()
        assert len(vaults) == 1
        assert len(procs) == 1
        assert procs[0].phi_vault_id == vaults[0].id
        assert len(audits) == 1
        assert audits[0].action == models.AuditAction.PHI_CREATED
        assert "Patient" not in str(audits[0].metadata_json)
    finally:
        db.close()


def test_status_returns_current_state(client):
    submit_resp = client.post(
        "/v1/phi/submit",
        json={
            "text": "Patient X synthetic note.",
            "submitted_by": "clinician_demo",
        },
    )
    proc_id = submit_resp.json()["procedure_id"]

    status_resp = client.get(f"/v1/phi/status/{proc_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["procedure_id"] == proc_id
    assert status_data["status"] == models.ProcessingStatus.PENDING_REVIEW.value
    assert "raw_text" not in status_data


def test_get_procedure_for_review_returns_scrubbed_text_and_entities(client):
    submit_resp = client.post(
        "/v1/phi/submit",
        json={
            "text": "Patient X synthetic note.",
            "submitted_by": "clinician_demo",
        },
    )
    proc_id = submit_resp.json()["procedure_id"]

    review_resp = client.get(f"/v1/phi/procedure/{proc_id}")
    assert review_resp.status_code == 200
    data = review_resp.json()
    assert data["procedure_id"] == proc_id
    assert data["status"] == models.ProcessingStatus.PENDING_REVIEW.value
    assert "Patient" not in data["scrubbed_text"]
    assert data["entities"][0]["entity_type"] == "PERSON"
    assert "raw_text" not in data


def test_feedback_endpoint_updates_procedure_status_and_logs(client):
    submit_resp = client.post(
        "/v1/phi/submit",
        json={
            "text": "Patient X synthetic note.",
            "submitted_by": "clinician_demo",
            "document_type": "demo_note",
        },
    )
    proc_id = submit_resp.json()["procedure_id"]

    feedback_resp = client.post(
        f"/v1/phi/procedure/{proc_id}/feedback",
        json={
            "scrubbed_text": "[[REDACTED]] synthetic note on <DATE_0>",
            "entities": [
                {"placeholder": "[[REDACTED]]", "entity_type": "PERSON", "original_start": 0, "original_end": 7},
                {"placeholder": "<DATE_0>", "entity_type": "DATE", "original_start": 22, "original_end": 30},
            ],
            "reviewer_id": "reviewer_demo",
            "reviewer_email": "reviewer@example.com",
            "reviewer_role": "physician",
            "comment": "Reviewed synthetic note",
        },
    )
    assert feedback_resp.status_code == 200
    data = feedback_resp.json()
    assert data["status"] == models.ProcessingStatus.PHI_REVIEWED.value
    assert data["scrubbed_text"].endswith("<DATE_0>")

    db = SessionLocal()
    try:
        proc = db.get(models.ProcedureData, uuid.UUID(proc_id))
        assert proc.status == models.ProcessingStatus.PHI_REVIEWED
        assert proc.scrubbed_text.endswith("<DATE_0>")

        feedback = db.query(models.ScrubbingFeedback).filter_by(procedure_data_id=proc.id).one()
        assert feedback.reviewer_id == "reviewer_demo"
        assert feedback.updated_entity_map[1]["entity_type"] == "DATE"

        audit = db.query(models.AuditLog).filter_by(procedure_data_id=proc.id).order_by(models.AuditLog.timestamp).all()
        assert any(a.action == models.AuditAction.SCRUBBING_FEEDBACK_APPLIED for a in audit)
        assert "Patient" not in str(audit[-1].metadata_json)
    finally:
        db.close()


def test_reidentify_returns_raw_text_and_audits(client):
    raw_text = "Patient X synthetic follow-up."
    submit_resp = client.post(
        "/v1/phi/submit",
        json={
            "text": raw_text,
            "submitted_by": "clinician_demo",
            "document_type": "demo_note",
        },
    )
    proc_id = submit_resp.json()["procedure_id"]

    reid_resp = client.post(
        "/v1/phi/reidentify",
        json={
            "procedure_id": proc_id,
            "user_id": "auditor_demo",
            "user_email": "auditor@example.com",
            "user_role": "reviewer",
        },
    )
    assert reid_resp.status_code == 200
    assert reid_resp.json()["raw_text"] == raw_text

    db = SessionLocal()
    try:
        audits = db.query(models.AuditLog).order_by(models.AuditLog.timestamp).all()
        assert audits[-1].action == models.AuditAction.REIDENTIFIED
        assert audits[-1].procedure_data_id == uuid.UUID(proc_id)
        assert raw_text not in str(audits[-1].metadata_json)
    finally:
        db.close()


def test_reidentify_missing_record_returns_404(client):
    missing_id = str(uuid.uuid4())
    resp = client.post(
        "/v1/phi/reidentify",
        json={"procedure_id": missing_id, "user_id": "auditor_demo"},
    )
    assert resp.status_code == 404
