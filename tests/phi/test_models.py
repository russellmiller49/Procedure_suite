"""Unit tests for PHI ORM models using an in-memory SQLite database.

All test data is synthetic and avoids real PHI.
"""

from __future__ import annotations

import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from modules.phi.db import Base
from modules.phi import models


@pytest.fixture()
def session():
    """Create a fresh in-memory database for each test."""

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


def test_phi_vault_and_procedure_data_relationship(session):
    """PHIVault stores encrypted data; ProcedureData stores scrubbed text only."""

    vault = models.PHIVault(
        encrypted_data=b"encrypted-synthetic-phi",
        data_hash="0" * 64,
        encryption_algorithm="FERNET",
        key_version=1,
    )

    proc = models.ProcedureData(
        phi_vault=vault,
        scrubbed_text="Patient X underwent bronchoscopy <PERSON_0>.",
        original_text_hash="f" * 64,
        entity_map=[{"placeholder": "<PERSON_0>", "entity_type": "PERSON", "original_start": 10, "original_end": 18}],
        status=models.ProcessingStatus.PENDING_REVIEW,
        submitted_by="clinician_demo",
    )

    session.add(proc)
    session.commit()

    stored_proc = session.query(models.ProcedureData).one()
    assert stored_proc.phi_vault_id == vault.id
    assert stored_proc.scrubbed_text.startswith("Patient X")
    assert stored_proc.phi_vault.encrypted_data.startswith(b"encrypted-")


def test_scrubbing_feedback_persists_metrics(session):
    """ScrubbingFeedback captures physician corrections for synthetic text."""

    vault = models.PHIVault(
        encrypted_data=b"encrypted-phi",
        data_hash="1" * 64,
    )
    proc = models.ProcedureData(
        phi_vault=vault,
        scrubbed_text="Patient Y with placeholder <DATE_0>.",
        original_text_hash="2" * 64,
        entity_map=[{"placeholder": "<DATE_0>", "entity_type": "DATE", "original_start": 12, "original_end": 22}],
        status=models.ProcessingStatus.PHI_CONFIRMED,
        submitted_by="reviewer_demo",
    )

    feedback = models.ScrubbingFeedback(
        procedure_data=proc,
        presidio_entities=[{"text": "Patient Y", "start": 0, "end": 9, "entity_type": "PERSON"}],
        confirmed_entities=[{"text": "<DATE_0>", "start": 21, "end": 27, "entity_type": "DATE"}],
        false_positives=[{"text": "Patient Y", "entity_type": "PERSON"}],
        false_negatives=[],
        true_positives=0,
        precision=0.0,
        recall=0.0,
        f1_score=0.0,
        document_type="procedure_note",
        specialty="pulmonary",
    )

    session.add(feedback)
    session.commit()

    stored = session.query(models.ScrubbingFeedback).one()
    assert stored.procedure_data_id == proc.id
    assert stored.false_positives[0]["text"] == "Patient Y"
    assert stored.precision == pytest.approx(0.0)


def test_audit_log_links_entities(session):
    """AuditLog links vault/procedure records without exposing raw PHI."""

    vault = models.PHIVault(
        encrypted_data=b"vault-bytes",
        data_hash="3" * 64,
    )
    proc = models.ProcedureData(
        phi_vault=vault,
        scrubbed_text="Patient Z placeholder <PHONE_0>.",
        original_text_hash="4" * 64,
        entity_map=[{"placeholder": "<PHONE_0>", "entity_type": "PHONE", "original_start": 20, "original_end": 32}],
        submitted_by="clinician_demo",
    )

    audit = models.AuditLog(
        phi_vault=vault,
        procedure_data=proc,
        user_id="auditor_demo",
        user_email="auditor@example.com",
        action=models.AuditAction.PHI_ACCESSED,
        action_detail="Viewed scrubbed text for status check",
        ip_address="127.0.0.1",
        metadata_json={"request_id": str(uuid.uuid4())},
    )

    session.add_all([audit, proc])
    session.commit()

    stored_audit = session.query(models.AuditLog).one()
    assert stored_audit.phi_vault_id == vault.id
    assert stored_audit.procedure_data_id == proc.id
    assert stored_audit.action == models.AuditAction.PHI_ACCESSED
    assert "request_id" in stored_audit.metadata_json

