"""Unit tests for PHIService using in-memory SQLite and demo adapters."""

from __future__ import annotations

import hashlib
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from app.phi import models
from app.phi.adapters.audit_logger_db import DatabaseAuditLogger
from app.phi.adapters.encryption_insecure_demo import InsecureDemoEncryptionAdapter
from app.phi.adapters.scrubber_stub import StubScrubber
from app.phi.db import Base
from app.phi.ports import ScrubResult
from app.phi.service import PHIService


@pytest.fixture()
def session():
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def encryption():
    return InsecureDemoEncryptionAdapter()


@pytest.fixture()
def scrubber():
    return StubScrubber()


@pytest.fixture()
def audit_logger(session):
    return DatabaseAuditLogger(session)


@pytest.fixture()
def service(session, encryption, scrubber, audit_logger):
    return PHIService(session=session, encryption=encryption, scrubber=scrubber, audit_logger=audit_logger)


def test_preview_does_not_persist_to_db(service, session):
    result = service.preview(text="Patient X synthetic note.")

    assert result.scrubbed_text.startswith("[[REDACTED]]")
    assert result.entities[0]["entity_type"] == "PERSON"
    assert session.query(models.PHIVault).count() == 0
    assert session.query(models.ProcedureData).count() == 0


def test_vault_phi_persists_encrypted_and_scrubbed_data(service, session, scrubber):
    raw_text = "Patient X synthetic note with token."
    scrub_result = scrubber.scrub(raw_text, document_type="demo_note")

    proc = service.vault_phi(
        raw_text=raw_text,
        scrub_result=scrub_result,
        submitted_by="clinician_demo",
        document_type="demo_note",
        specialty="demo_specialty",
    )

    vault_rows = session.query(models.PHIVault).all()
    proc_rows = session.query(models.ProcedureData).all()
    audit_rows = session.query(models.AuditLog).all()

    assert len(vault_rows) == 1
    assert len(proc_rows) == 1
    assert vault_rows[0].encrypted_data.startswith(b"demo-")
    assert proc.phi_vault_id == vault_rows[0].id
    assert proc.scrubbed_text == scrub_result.scrubbed_text
    assert proc.entity_map[0]["placeholder"] == scrub_result.entities[0]["placeholder"]

    expected_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    assert proc.original_text_hash == expected_hash

    assert len(audit_rows) == 1
    assert audit_rows[0].action == models.AuditAction.PHI_CREATED
    assert audit_rows[0].phi_vault_id == vault_rows[0].id
    assert "document_type" in audit_rows[0].metadata_json
    assert raw_text not in str(audit_rows[0].metadata_json)


def test_reidentify_decrypts_and_audits(service, session, scrubber):
    raw_text = "Patient X synthetic follow-up."
    scrub_result = scrubber.scrub(raw_text)

    proc = service.vault_phi(
        raw_text=raw_text,
        scrub_result=scrub_result,
        submitted_by="clinician_demo",
        document_type="demo_note",
    )

    returned_text = service.reidentify(
        procedure_data_id=proc.id,
        user_id="auditor_demo",
        user_email="auditor@example.com",
        user_role="reviewer",
        ip_address="127.0.0.1",
        user_agent="pytest",
        request_id=str(uuid.uuid4()),
    )

    assert returned_text == raw_text
    audit_events = session.query(models.AuditLog).order_by(models.AuditLog.timestamp).all()
    assert audit_events[-1].action == models.AuditAction.REIDENTIFIED
    assert audit_events[-1].procedure_data_id == proc.id


def test_get_procedure_for_review_returns_scrubbed_text_only(service, session, scrubber):
    raw_text = "Patient X synthetic note."
    scrub_result = scrubber.scrub(raw_text)
    proc = service.vault_phi(raw_text=raw_text, scrub_result=scrub_result, submitted_by="clinician_demo")

    fetched = service.get_procedure_for_review(procedure_data_id=proc.id)

    assert fetched.id == proc.id
    assert fetched.scrubbed_text == scrub_result.scrubbed_text
    assert fetched.entity_map == scrub_result.entities
    # Ensure ciphertext remains unchanged (no decryption performed)
    vault = session.query(models.PHIVault).filter_by(id=proc.phi_vault_id).one()
    assert vault.encrypted_data.startswith(b"demo-")


def test_apply_scrubbing_feedback_updates_procedure_and_logs(service, session, scrubber):
    raw_text = "Patient X synthetic note."
    scrub_result = scrubber.scrub(raw_text)
    proc = service.vault_phi(raw_text=raw_text, scrub_result=scrub_result, submitted_by="clinician_demo")

    updated_entities = [
        {"placeholder": "[[REDACTED]]", "entity_type": "PERSON", "original_start": 0, "original_end": 7},
        {"placeholder": "<DATE_0>", "entity_type": "DATE", "original_start": 15, "original_end": 25},
    ]
    updated_text = scrub_result.scrubbed_text + " on <DATE_0>"

    updated_proc = service.apply_scrubbing_feedback(
        procedure_data_id=proc.id,
        scrubbed_text=updated_text,
        entities=updated_entities,
        reviewer_id="reviewer_demo",
        reviewer_email="reviewer@example.com",
        reviewer_role="physician",
        comment="Reviewed synthetic note",
    )

    session.refresh(updated_proc)

    assert updated_proc.status == models.ProcessingStatus.PHI_REVIEWED
    assert updated_proc.scrubbed_text == updated_text
    assert updated_proc.entity_map[1]["placeholder"] == "<DATE_0>"
    assert updated_proc.reviewed_by == "reviewer_demo"
    assert updated_proc.reviewed_at is not None

    feedback = session.query(models.ScrubbingFeedback).filter_by(procedure_data_id=proc.id).one()
    assert feedback.reviewer_id == "reviewer_demo"
    assert feedback.updated_scrubbed_text == updated_text
    assert feedback.updated_entity_map[1]["placeholder"] == "<DATE_0>"

    audit_events = session.query(models.AuditLog).filter_by(procedure_data_id=proc.id).all()
    assert any(event.action == models.AuditAction.SCRUBBING_FEEDBACK_APPLIED for event in audit_events)
    # Ensure no raw text is accidentally stored in audit metadata
    for event in audit_events:
        assert raw_text not in str(event.metadata_json)
