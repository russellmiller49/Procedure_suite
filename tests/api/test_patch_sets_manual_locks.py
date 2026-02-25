from __future__ import annotations

from datetime import datetime, timezone
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.fastapi_app import app
from app.phi.db import Base
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryCaseRecord
from app.vault.models import UserPatientVault


@pytest.fixture
def patch_locks_db(tmp_path, monkeypatch):
    db_path = tmp_path / "patch_locks.db"
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
def client(patch_locks_db):
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
    db.add(
        RegistryCaseRecord(
            registry_uuid=registry_uuid,
            registry_json={"clinical_context": {"lesion_location": "RUL"}},
            schema_version="v3",
            version=1,
            source_run_id=None,
            manual_overrides={},
            created_at=now,
            updated_at=now,
        )
    )
    db.commit()


def test_patch_sets_manual_leaf_locks(client: TestClient, patch_locks_db) -> None:
    case_id = uuid.uuid4()
    _seed_case(patch_locks_db, user_id="user_a", registry_uuid=case_id)

    res = client.patch(
        f"/api/v1/registry/{case_id}",
        headers=_auth("user_a"),
        json={"expected_version": 1, "registry_patch": {"clinical_context": {"lesion_location": "RML"}}},
    )
    assert res.status_code == 200
    body = res.json()

    locks = body.get("manual_overrides") or {}
    assert "/clinical_context/lesion_location" in locks
    assert locks["/clinical_context/lesion_location"]["locked"] is True

    row = patch_locks_db.get(RegistryCaseRecord, case_id)
    assert row is not None
    assert row.manual_overrides["/clinical_context/lesion_location"]["source"] == "manual"
