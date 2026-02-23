from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.fastapi_app import app
from app.phi.db import Base
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument, RegistryCaseRecord
from app.vault.models import UserPatientVault


@pytest.fixture
def case_db(tmp_path, monkeypatch):
    db_path = tmp_path / "registry_case.db"
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
def client(case_db):
    return TestClient(app)


def _auth(user_id: str) -> dict[str, str]:
    return {"X-User-Id": user_id}


def _seed_user_case(db, *, user_id: str, registry_uuid: uuid.UUID) -> None:
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
    db.add(
        RegistryCaseRecord(
            registry_uuid=registry_uuid,
            registry_json={"clinical_context": {"lesion_location": "RUL"}},
            schema_version="v3",
            version=1,
            source_run_id=None,
            created_at=now,
            updated_at=now,
        )
    )
    db.add(
        RegistryAppendedDocument(
            id=uuid.uuid4(),
            user_id=user_id,
            registry_uuid=registry_uuid,
            note_text="pathology follow-up",
            note_sha256="x" * 64,
            event_type="pathology",
            document_kind="pathology",
            source_type="manual_entry",
            relative_day_offset=2,
            ocr_correction_applied=False,
            metadata_json={"structured_data": {"hospital_admission": False}},
            created_at=now,
        )
    )
    db.commit()


def test_registry_case_requires_user_header(client: TestClient) -> None:
    case_id = uuid.uuid4()
    resp = client.get(f"/api/v1/registry/{case_id}")
    assert resp.status_code == 401


def test_registry_case_get_is_user_scoped(client: TestClient, case_db) -> None:
    case_id = uuid.uuid4()
    _seed_user_case(case_db, user_id="user_a", registry_uuid=case_id)

    res = client.get(f"/api/v1/registry/{case_id}", headers=_auth("user_a"))
    assert res.status_code == 200
    body = res.json()
    assert body["registry_uuid"] == str(case_id)
    assert body["version"] == 1
    assert body["registry"]["clinical_context"]["lesion_location"] == "RUL"
    assert len(body["events"]) == 1
    assert body["events"][0]["event_type"] == "pathology"
    assert body["events"][0]["relative_day_offset"] == 2

    res_other = client.get(f"/api/v1/registry/{case_id}", headers=_auth("user_b"))
    assert res_other.status_code == 404


def test_registry_case_patch_updates_registry_and_version(client: TestClient, case_db) -> None:
    case_id = uuid.uuid4()
    _seed_user_case(case_db, user_id="user_a", registry_uuid=case_id)

    patch_res = client.patch(
        f"/api/v1/registry/{case_id}",
        headers=_auth("user_a"),
        json={
            "expected_version": 1,
            "registry_patch": {
                "clinical_context": {"lesion_location": "RML"},
            },
        },
    )
    assert patch_res.status_code == 200
    payload = patch_res.json()
    assert payload["version"] == 2
    assert payload["registry"]["clinical_context"]["lesion_location"] == "RML"

    db_row = case_db.get(RegistryCaseRecord, case_id)
    assert db_row is not None
    assert db_row.version == 2
    assert db_row.registry_json["clinical_context"]["lesion_location"] == "RML"


def test_registry_case_patch_rejects_version_conflict(client: TestClient, case_db) -> None:
    case_id = uuid.uuid4()
    _seed_user_case(case_db, user_id="user_a", registry_uuid=case_id)

    res = client.patch(
        f"/api/v1/registry/{case_id}",
        headers=_auth("user_a"),
        json={
            "expected_version": 99,
            "registry_patch": {"clinical_context": {"lesion_location": "LLL"}},
        },
    )
    assert res.status_code == 409


def test_registry_case_patch_rejects_invalid_schema_payload(client: TestClient, case_db) -> None:
    case_id = uuid.uuid4()
    _seed_user_case(case_db, user_id="user_a", registry_uuid=case_id)

    res = client.patch(
        f"/api/v1/registry/{case_id}",
        headers=_auth("user_a"),
        json={
            "registry_patch": {
                "clinical_context": "invalid-should-be-object",
            },
        },
    )
    assert res.status_code == 422
