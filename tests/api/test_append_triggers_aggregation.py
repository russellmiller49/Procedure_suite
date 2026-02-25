from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.fastapi_app import app
from app.phi.db import Base
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryCaseRecord
from app.vault.models import UserPatientVault


_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "case_events"


@pytest.fixture
def append_aggregate_db(tmp_path, monkeypatch):
    db_path = tmp_path / "append_aggregate.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("REGISTRY_AGGREGATE_ON_APPEND", "1")
    engine = get_registry_store_engine()
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(append_aggregate_db):
    return TestClient(app)


def _auth(user_id: str) -> dict[str, str]:
    return {"X-User-Id": user_id}


def _seed_case(db, *, user_id: str, registry_uuid: uuid.UUID) -> None:
    now = datetime.now(timezone.utc)
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


def test_append_imaging_triggers_case_aggregation(client: TestClient, append_aggregate_db) -> None:
    case_id = uuid.uuid4()
    _seed_case(append_aggregate_db, user_id="user_a", registry_uuid=case_id)

    text = (_FIXTURE_DIR / "ct_preop_nodule_growth.txt").read_text()
    res = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_a"),
        json={
            "text": text,
            "already_scrubbed": True,
            "event_type": "imaging",
            "source_modality": "ct",
            "event_subtype": "preop",
            "event_title": "Preop CT",
            "relative_day_offset": -7,
        },
    )
    assert res.status_code == 200
    body = res.json()

    assert body["append_id"]
    assert body["version"] >= 2
    assert body["registry_uuid"] == str(case_id)
    assert isinstance(body.get("recent_events"), list)
    assert body["recent_events"][0]["event_type"] == "imaging"

    case_row = append_aggregate_db.get(RegistryCaseRecord, case_id)
    assert case_row is not None

    imaging_summary = case_row.registry_json.get("imaging_summary") or {}
    baseline = imaging_summary.get("baseline") or {}
    assert baseline.get("modality") == "ct"
    assert baseline.get("relative_day_offset") == -7

    targets = (case_row.registry_json.get("targets") or {}).get("peripheral_targets") or []
    assert targets
    assert targets[0].get("size_mm_long") == 22
