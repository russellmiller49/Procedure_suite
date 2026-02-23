from __future__ import annotations

import base64
import uuid

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.fastapi_app import app
from app.phi.db import Base
from app.registry_store.dependencies import get_registry_store_engine
from app.registry_store.models import RegistryAppendedDocument

TEST_JWT_SECRET = "unit-test-supabase-secret"


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _settings_payload() -> dict[str, object]:
    return {
        "wrapped_vmk_b64": _b64(b"wrapped-key-material"),
        "wrap_iv_b64": _b64(b"123456789012"),
        "kdf_salt_b64": _b64(b"salt-salt-salt-1234"),
        "kdf_iterations": 210_000,
        "kdf_hash": "PBKDF2-SHA256",
        "crypto_version": 1,
    }


def _record_payload(registry_uuid: str, *, text: bytes = b"encrypted-patient-json") -> dict[str, object]:
    return {
        "registry_uuid": registry_uuid,
        "ciphertext_b64": _b64(text),
        "iv_b64": _b64(b"abcdef123456"),
        "crypto_version": 1,
    }


def _bearer(user_id: str) -> dict[str, str]:
    token = jwt.encode({"sub": user_id}, TEST_JWT_SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def bearer_db(tmp_path, monkeypatch):
    db_path = tmp_path / "vault_bearer_e2e.db"
    monkeypatch.setenv("REGISTRY_STORE_DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", TEST_JWT_SECRET)
    monkeypatch.setenv("PROCSUITE_ENV", "production")
    monkeypatch.setenv("VAULT_AUTH_ALLOW_X_USER_ID", "0")

    engine = get_registry_store_engine()
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(bearer_db):
    return TestClient(app)


def test_x_user_id_rejected_when_disabled(client: TestClient) -> None:
    resp = client.get("/api/v1/vault/settings", headers={"X-User-Id": "user_a"})
    assert resp.status_code == 401
    assert "X-User-Id" in str(resp.json().get("detail", ""))


def test_invalid_bearer_token_rejected(client: TestClient) -> None:
    bad_token = jwt.encode({"sub": "user_a"}, "wrong-secret", algorithm="HS256")
    resp = client.get(
        "/api/v1/vault/settings",
        headers={"Authorization": f"Bearer {bad_token}"},
    )
    assert resp.status_code == 401


def test_bearer_unlock_view_append_pathology_flow(client: TestClient, bearer_db) -> None:
    user_a_headers = _bearer("user_a")
    user_b_headers = _bearer("user_b")

    put_settings = client.put(
        "/api/v1/vault/settings",
        json=_settings_payload(),
        headers=user_a_headers,
    )
    assert put_settings.status_code == 200
    assert put_settings.json()["user_id"] == "user_a"

    registry_uuid = str(uuid.uuid4())
    put_record = client.put(
        "/api/v1/vault/record",
        json=_record_payload(registry_uuid, text=b"ciphertext-v1"),
        headers=user_a_headers,
    )
    assert put_record.status_code == 201

    user_a_records = client.get("/api/v1/vault/records", headers=user_a_headers)
    assert user_a_records.status_code == 200
    user_a_rows = user_a_records.json()
    assert len(user_a_rows) == 1
    assert user_a_rows[0]["registry_uuid"] == registry_uuid

    user_b_records = client.get("/api/v1/vault/records", headers=user_b_headers)
    assert user_b_records.status_code == 200
    assert user_b_records.json() == []

    append_payload = {
        "note": "Pathology follow-up note (scrubbed)",
        "already_scrubbed": True,
        "event_type": "pathology",
        "document_kind": "pathology",
        "source_type": "camera_ocr",
        "relative_day_offset": 10,
        "ocr_correction_applied": True,
        "metadata": {"synced_from": "vault_e2e_test"},
    }
    append_resp = client.post(
        f"/api/v1/registry/{registry_uuid}/append",
        headers=user_a_headers,
        json=append_payload,
    )
    assert append_resp.status_code == 200
    append_body = append_resp.json()
    assert append_body["registry_uuid"] == registry_uuid
    assert append_body["user_id"] == "user_a"

    append_row = (
        bearer_db.query(RegistryAppendedDocument)
        .filter_by(id=uuid.UUID(append_body["append_id"]))
        .one()
    )
    assert str(append_row.registry_uuid) == registry_uuid
    assert append_row.user_id == "user_a"
    assert append_row.event_type == "pathology"
    assert append_row.relative_day_offset == 10
    assert append_row.document_kind == "pathology"

    user_b_append = client.post(
        f"/api/v1/registry/{registry_uuid}/append",
        headers=user_b_headers,
        json={"note": "Other user attempt", "already_scrubbed": True},
    )
    assert user_b_append.status_code == 404
