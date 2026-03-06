from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.fastapi_app import app
from app.phi.db import Base
from app.registry_store.dependencies import get_registry_store_engine
from app.vault.models import UserPatientVault


@pytest.fixture
def strict_db(tmp_path, monkeypatch):
    db_path = tmp_path / "append_guardrails.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
    engine = get_registry_store_engine()
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(strict_db):
    return TestClient(app)


def _auth(user_id: str) -> dict[str, str]:
    return {"X-User-Id": user_id}


def _seed_case(db, *, user_id: str, registry_uuid: uuid.UUID) -> None:
    now = datetime.now(UTC)
    db.add(
        UserPatientVault(
            user_id=user_id,
            registry_uuid=registry_uuid,
            ciphertext_b64="ZHVtbXktY2lwaGVydGV4dA==",
            iv_b64="YWJjZGVmMTIzNDU2",
            crypto_version=1,
            created_at=now,
            updated_at=now,
        )
    )
    db.commit()


def test_append_rejects_server_side_scrub_in_strict_mode(
    client: TestClient, strict_db, monkeypatch
) -> None:
    monkeypatch.setenv("PROCSUITE_STRICT_ZK", "1")
    case_id = uuid.uuid4()
    _seed_case(strict_db, user_id="user_a", registry_uuid=case_id)

    res = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_a"),
        json={
            "text": "clinical update",
            "already_scrubbed": False,
            "event_type": "clinical_update",
        },
    )
    assert res.status_code == 400
    assert "already_scrubbed=true" in str(res.json())


def test_append_rejects_absolute_dates_in_text_and_title(client: TestClient, strict_db) -> None:
    case_id = uuid.uuid4()
    _seed_case(strict_db, user_id="user_a", registry_uuid=case_id)

    res = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_a"),
        json={
            "text": "Follow-up completed on 01/02/2026.",
            "event_title": "Visit Jan 2, 2026",
            "already_scrubbed": True,
            "event_type": "clinical_update",
        },
    )
    assert res.status_code == 400
    assert "absolute date-like strings" in str(res.json())


def test_append_rejects_dd_mm_dates_and_structured_dates(client: TestClient, strict_db) -> None:
    case_id = uuid.uuid4()
    _seed_case(strict_db, user_id="user_a", registry_uuid=case_id)

    res = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_a"),
        json={
            "text": "Symptoms worsened on 24/01/2026.",
            "already_scrubbed": True,
            "event_type": "clinical_update",
            "structured_data": {"planned_followup": "2026-02-10"},
        },
    )
    assert res.status_code == 400
    assert "absolute date-like strings" in str(res.json())


def test_append_absolute_dates_override_blocked_without_env_flag(
    client: TestClient, strict_db
) -> None:
    case_id = uuid.uuid4()
    _seed_case(strict_db, user_id="user_a", registry_uuid=case_id)

    res = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_a"),
        json={
            "text": "Follow-up completed on 2026-01-02.",
            "already_scrubbed": True,
            "event_type": "clinical_update",
            "allow_absolute_dates": True,
        },
    )
    assert res.status_code == 400
    assert "PROCSUITE_ALLOW_ABSOLUTE_DATES" in str(res.json())
