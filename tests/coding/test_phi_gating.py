"""Tests for PHI gating helper used before coding."""

from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from app.phi.db import Base
from app.phi import models
from app.phi.adapters.encryption_insecure_demo import InsecureDemoEncryptionAdapter
from app.phi.adapters.scrubber_stub import StubScrubber
from app.phi.adapters.audit_logger_db import DatabaseAuditLogger
from app.phi.service import PHIService
from app.coder.phi_gating import load_procedure_for_coding


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
def phi_service(session):
    encryption = InsecureDemoEncryptionAdapter()
    scrubber = StubScrubber()
    audit_logger = DatabaseAuditLogger(session)
    return PHIService(session=session, encryption=encryption, scrubber=scrubber, audit_logger=audit_logger)


def test_gating_requires_review_when_enabled(monkeypatch, session, phi_service):
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    proc = phi_service.vault_phi(
        raw_text="Patient X synthetic note.",
        scrub_result=phi_service.preview(text="Patient X synthetic note."),
        submitted_by="clinician_demo",
    )
    # Status is pending_review by default
    with pytest.raises(PermissionError):
        load_procedure_for_coding(session, proc.id, require_review=None)


def test_gating_allows_reviewed(monkeypatch, session, phi_service):
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    proc = phi_service.vault_phi(
        raw_text="Patient X synthetic note.",
        scrub_result=phi_service.preview(text="Patient X synthetic note."),
        submitted_by="clinician_demo",
    )
    # Mark reviewed
    phi_service.apply_scrubbing_feedback(
        procedure_data_id=proc.id,
        scrubbed_text="[[REDACTED]] synthetic note.",
        entities=[{"placeholder": "[[REDACTED]]", "entity_type": "PERSON", "original_start": 0, "original_end": 7}],
        reviewer_id="reviewer_demo",
    )

    loaded = load_procedure_for_coding(session, proc.id, require_review=None)
    assert loaded.id == proc.id
    assert loaded.status == models.ProcessingStatus.PHI_REVIEWED
    assert loaded.scrubbed_text.startswith("[[REDACTED]]")


def test_gating_allows_legacy_when_disabled(monkeypatch, session, phi_service):
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "false")
    missing_id = uuid.uuid4()
    proc = load_procedure_for_coding(session, missing_id, require_review=None)
    assert proc is None
