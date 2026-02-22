from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.fastapi_app import app
from app.phi.db import Base
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument
from app.vault.models import UserPatientVault


@pytest.fixture
def append_db(tmp_path, monkeypatch):
    db_path = tmp_path / "registry_append.db"
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
def client(append_db):
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


def test_append_requires_user_header(client: TestClient) -> None:
    case_id = uuid.uuid4()
    resp = client.post(f"/api/v1/registry/{case_id}/append", json={"note": "pathology", "already_scrubbed": True})
    assert resp.status_code == 401


def test_append_rejects_unknown_case_for_user(client: TestClient) -> None:
    case_id = uuid.uuid4()
    resp = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_a"),
        json={"note": "pathology text", "already_scrubbed": True},
    )
    assert resp.status_code == 404


def test_append_succeeds_and_is_user_scoped(client: TestClient, append_db) -> None:
    case_id = uuid.uuid4()
    _seed_case(append_db, user_id="user_a", registry_uuid=case_id)

    res = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_a"),
        json={
            "note": "Pathology follow-up note (scrubbed).",
            "already_scrubbed": True,
            "source_type": "camera_ocr",
            "ocr_correction_applied": True,
            "document_kind": "pathology",
            "metadata": {"specimen_count": 2},
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["registry_uuid"] == str(case_id)
    assert body["user_id"] == "user_a"
    assert body["document_kind"] == "pathology"

    row = append_db.query(RegistryAppendedDocument).filter_by(id=uuid.UUID(body["append_id"])).one()
    assert row.user_id == "user_a"
    assert str(row.registry_uuid) == str(case_id)
    assert row.note_text == "Pathology follow-up note (scrubbed)."
    assert row.source_type == "camera_ocr"
    assert row.ocr_correction_applied is True
    assert isinstance(row.metadata_json, dict)
    assert row.metadata_json.get("specimen_count") == 2

    # Different user cannot append to user_a case.
    res_other = client.post(
        f"/api/v1/registry/{case_id}/append",
        headers=_auth("user_b"),
        json={"note": "Other user attempt", "already_scrubbed": True},
    )
    assert res_other.status_code == 404

