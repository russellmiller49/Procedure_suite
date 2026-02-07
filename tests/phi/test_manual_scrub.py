"""Unit tests for manual scrubbing logic in PHIService."""

from __future__ import annotations

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from app.phi.adapters.audit_logger_db import DatabaseAuditLogger
from app.phi.adapters.encryption_insecure_demo import InsecureDemoEncryptionAdapter
from app.phi.adapters.scrubber_stub import StubScrubber
from app.phi.db import Base
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


def test_scrub_with_manual_entities(service):
    raw_text = "Dr. Smith visited Paris on May 1st."
    # We want to scrub "Dr. Smith" and "Paris" but leave "May 1st" alone (manual override).
    
    manual_entities = [
        {
            "entity_type": "PERSON",
            "original_start": 0,
            "original_end": 9,
            "placeholder": "<PERSON_1>"
        },
        {
            "entity_type": "LOCATION",
            "original_start": 18,
            "original_end": 23,
            # No placeholder provided, let it generate one
        }
    ]

    result = service.scrub_with_manual_entities(text=raw_text, entities=manual_entities)

    # Expected behavior:
    # "Dr. Smith" (0-9) -> "<PERSON_1>"
    # " visited " (9-18) -> kept as is
    # "Paris" (18-23) -> "<LOCATION_0>" (index 0 because it's the 2nd one processed in reverse order, or based on implementation)
    # " on May 1st." (23-end) -> kept as is

    # Wait, let's check the implementation of placeholder generation:
    # placeholder = f"<{entity_type}_{len(sorted_entities) - idx}>"
    # sorted_entities is reversed by start position.
    # 1. "Paris" (start 18). idx=0. len=2. Placeholder = <LOCATION_2> ? No, len - idx = 2. <LOCATION_2>
    # 2. "Dr. Smith" (start 0). idx=1. len=2. Placeholder = <PERSON_1>. But we provided <PERSON_1>.

    # Let's re-verify the implementation logic:
    # sorted_entities = sorted(entities, key=lambda x: x["original_start"], reverse=True)
    # Paris is first (idx 0). Placeholder generated: <LOCATION_2>
    # Dr. Smith is second (idx 1). Placeholder provided: <PERSON_1>

    assert "<PERSON_1>" in result.scrubbed_text
    assert "visited" in result.scrubbed_text
    assert "Paris" not in result.scrubbed_text
    assert "Dr. Smith" not in result.scrubbed_text
    
    # Check generated placeholder format
    # We expect something like <LOCATION_2> or similar based on the logic.
    # The logic is: f"<{entity_type}_{len(sorted_entities) - idx}>"
    # Paris is first in loop (idx 0). len=2. 2-0=2. -> <LOCATION_2>
    assert "<LOCATION_2>" in result.scrubbed_text
    
    expected_text = "<PERSON_1> visited <LOCATION_2> on May 1st."
    assert result.scrubbed_text == expected_text

    assert len(result.entities) == 2
    
    # Entities in result should be sorted by start (ascending)
    assert result.entities[0]["original_start"] == 0
    assert result.entities[0]["placeholder"] == "<PERSON_1>"
    
    assert result.entities[1]["original_start"] == 18
    assert result.entities[1]["placeholder"] == "<LOCATION_2>"


def test_scrub_with_manual_entities_out_of_bounds(service):
    raw_text = "Hello"
    manual_entities = [
        {
            "entity_type": "PERSON",
            "original_start": 10,
            "original_end": 15,
            "placeholder": "<FAIL>"
        }
    ]
    
    result = service.scrub_with_manual_entities(text=raw_text, entities=manual_entities)
    
    # Should ignore out of bounds
    assert result.scrubbed_text == "Hello"
    assert len(result.entities) == 0


def test_scrub_with_manual_entities_empty(service):
    raw_text = "Hello World"
    result = service.scrub_with_manual_entities(text=raw_text, entities=[])
    
    assert result.scrubbed_text == "Hello World"
    assert len(result.entities) == 0
