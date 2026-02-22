from __future__ import annotations

import base64
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.fastapi_app import app
from app.phi.db import Base
from app.registry_store.dependencies import get_registry_store_engine
from app.vault import models as vault_models  # noqa: F401


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


@pytest.fixture
def vault_db(tmp_path, monkeypatch):
    db_path = tmp_path / "vault_store.db"
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
def client(vault_db):
    return TestClient(app)


def _auth(user_id: str) -> dict[str, str]:
    return {"X-User-Id": user_id}


def test_vault_requires_user_header(client: TestClient) -> None:
    resp = client.get("/api/v1/vault/settings")
    assert resp.status_code == 401


def test_vault_settings_invalid_base64_rejected(client: TestClient) -> None:
    payload = _settings_payload()
    payload["wrapped_vmk_b64"] = "%%not-base64%%"
    resp = client.put("/api/v1/vault/settings", json=payload, headers=_auth("user_a"))
    assert resp.status_code == 422


def test_vault_settings_wrong_iv_length_rejected(client: TestClient) -> None:
    payload = _settings_payload()
    payload["wrap_iv_b64"] = _b64(b"short-iv")
    resp = client.put("/api/v1/vault/settings", json=payload, headers=_auth("user_a"))
    assert resp.status_code == 422


def test_vault_user_scoping_and_record_lifecycle(client: TestClient) -> None:
    create_settings = client.put(
        "/api/v1/vault/settings",
        json=_settings_payload(),
        headers=_auth("user_a"),
    )
    assert create_settings.status_code == 200
    assert create_settings.json()["user_id"] == "user_a"

    user_b_settings = client.get("/api/v1/vault/settings", headers=_auth("user_b"))
    assert user_b_settings.status_code == 404

    registry_uuid = str(uuid.uuid4())
    create_record = client.put(
        "/api/v1/vault/record",
        json=_record_payload(registry_uuid, text=b"ciphertext-v1"),
        headers=_auth("user_a"),
    )
    assert create_record.status_code == 201
    assert create_record.json()["registry_uuid"] == registry_uuid

    user_a_records = client.get("/api/v1/vault/records", headers=_auth("user_a"))
    assert user_a_records.status_code == 200
    assert len(user_a_records.json()) == 1

    user_b_records = client.get("/api/v1/vault/records", headers=_auth("user_b"))
    assert user_b_records.status_code == 200
    assert user_b_records.json() == []

    user_b_delete = client.delete(f"/api/v1/vault/records/{registry_uuid}", headers=_auth("user_b"))
    assert user_b_delete.status_code == 404

    update_record = client.put(
        "/api/v1/vault/record",
        json=_record_payload(registry_uuid, text=b"ciphertext-v2-updated"),
        headers=_auth("user_a"),
    )
    assert update_record.status_code == 200
    assert update_record.json()["ciphertext_b64"] == _b64(b"ciphertext-v2-updated")

    delete_record = client.delete(f"/api/v1/vault/records/{registry_uuid}", headers=_auth("user_a"))
    assert delete_record.status_code == 200
    assert delete_record.json()["ok"] is True

    user_a_after_delete = client.get("/api/v1/vault/records", headers=_auth("user_a"))
    assert user_a_after_delete.status_code == 200
    assert user_a_after_delete.json() == []


def test_vault_record_oversize_rejected(client: TestClient) -> None:
    payload = _record_payload(str(uuid.uuid4()), text=b"x" * 13_000)
    resp = client.put("/api/v1/vault/record", json=payload, headers=_auth("user_a"))
    assert resp.status_code == 413
