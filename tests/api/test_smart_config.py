"""Tests for GET /api/v1/smart/config (SMART on FHIR issuer allowlist)."""

import json

import pytest

_SMART_ENV_VARS = (
    "SMART_ENABLED",
    "SMART_ON_FHIR_ENABLED",
    "SMART_ISSUERS",
    "SMART_ISSUERS_FILE",
    "SMART_DEFAULT_SCOPES",
)


def _clear_smart_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _SMART_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.mark.asyncio
async def test_smart_config_disabled_by_default(api_client, monkeypatch: pytest.MonkeyPatch):
    _clear_smart_env(monkeypatch)
    resp = await api_client.get("/api/v1/smart/config")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["enabled"] is False
    assert payload["issuers"] == []
    assert payload["config_errors"] == []


@pytest.mark.asyncio
async def test_smart_config_returns_allowlisted_issuers(
    api_client, monkeypatch: pytest.MonkeyPatch
):
    _clear_smart_env(monkeypatch)
    monkeypatch.setenv("SMART_ENABLED", "1")
    monkeypatch.setenv(
        "SMART_ISSUERS",
        json.dumps(
            [
                {
                    "name": "Epic Sandbox",
                    # trailing slash must be normalized away for exact iss matching
                    "iss": "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/",
                    "client_id": "epic-public-client",
                    "vendor": "epic",
                },
                {
                    "name": "Cerner Sandbox",
                    "iss": "https://fhir-ehr-code.cerner.com/r4/tenant-id",
                    "client_id": "cerner-public-client",
                    "vendor": "cerner",
                },
            ]
        ),
    )

    resp = await api_client.get("/api/v1/smart/config")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["enabled"] is True
    assert payload["config_errors"] == []
    assert len(payload["issuers"]) == 2

    epic = payload["issuers"][0]
    assert epic["iss"] == "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
    assert "user/DocumentReference.read" in epic["scopes"]
    assert "online_access" not in epic["scopes"].split()
    # the launch-context scope is added by the browser at authorize time, never here
    assert "launch" not in epic["scopes"].split()
    # public endpoint: exactly the public client config, nothing more
    assert set(epic.keys()) == {"name", "iss", "client_id", "vendor", "scopes"}

    cerner = payload["issuers"][1]
    # short-lived Cerner tokens -> online_access appended for in-session refresh
    assert cerner["scopes"].split()[-1] == "online_access"


@pytest.mark.asyncio
async def test_smart_config_scope_override_is_verbatim(
    api_client, monkeypatch: pytest.MonkeyPatch
):
    _clear_smart_env(monkeypatch)
    monkeypatch.setenv("SMART_ENABLED", "1")
    monkeypatch.setenv(
        "SMART_ISSUERS",
        json.dumps(
            [
                {
                    "name": "Cerner Custom",
                    "iss": "https://fhir.example.org/r4",
                    "client_id": "abc",
                    "vendor": "cerner",
                    "scopes": "openid user/DocumentReference.read online_access",
                }
            ]
        ),
    )
    resp = await api_client.get("/api/v1/smart/config")
    payload = resp.json()
    # online_access already present -> not duplicated
    assert payload["issuers"][0]["scopes"] == "openid user/DocumentReference.read online_access"


@pytest.mark.asyncio
async def test_smart_config_rejects_bad_entries_fail_soft(
    api_client, monkeypatch: pytest.MonkeyPatch
):
    _clear_smart_env(monkeypatch)
    monkeypatch.setenv("SMART_ENABLED", "true")
    monkeypatch.setenv(
        "SMART_ISSUERS",
        json.dumps(
            [
                {"name": "Good", "iss": "https://ehr.example.org/fhir", "client_id": "abc"},
                {"name": "Insecure", "iss": "http://ehr.example.org/fhir", "client_id": "abc"},
                {"name": "Typo", "iss": "https://x.example.org/fhir", "clientid": "abc"},
                {"name": "Duplicate", "iss": "https://ehr.example.org/fhir/", "client_id": "dup"},
            ]
        ),
    )
    resp = await api_client.get("/api/v1/smart/config")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["enabled"] is True
    assert [issuer["name"] for issuer in payload["issuers"]] == ["Good"]
    assert len(payload["config_errors"]) == 3


@pytest.mark.asyncio
async def test_smart_config_issuers_file_and_localhost_http(
    api_client, monkeypatch: pytest.MonkeyPatch, tmp_path
):
    _clear_smart_env(monkeypatch)
    monkeypatch.setenv("SMART_ENABLED", "1")
    issuers_file = tmp_path / "issuers.json"
    issuers_file.write_text(
        json.dumps(
            [
                {
                    "name": "Local HAPI",
                    # plain http is allowed for localhost dev servers only
                    "iss": "http://localhost:8080/fhir",
                    "client_id": "dev-client",
                    "scopes": "openid user/DocumentReference.read",
                }
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("SMART_ISSUERS_FILE", str(issuers_file))

    resp = await api_client.get("/api/v1/smart/config")
    payload = resp.json()
    assert payload["enabled"] is True
    assert payload["config_errors"] == []
    assert payload["issuers"][0]["iss"] == "http://localhost:8080/fhir"
    assert payload["issuers"][0]["scopes"] == "openid user/DocumentReference.read"


@pytest.mark.asyncio
async def test_smart_config_enabled_without_issuers_reports_hint(
    api_client, monkeypatch: pytest.MonkeyPatch
):
    _clear_smart_env(monkeypatch)
    monkeypatch.setenv("SMART_ENABLED", "1")
    resp = await api_client.get("/api/v1/smart/config")
    payload = resp.json()
    assert payload["enabled"] is True
    assert payload["issuers"] == []
    assert any("SMART_ISSUERS" in error for error in payload["config_errors"])


@pytest.mark.asyncio
async def test_smart_config_malformed_json_fails_soft(
    api_client, monkeypatch: pytest.MonkeyPatch
):
    _clear_smart_env(monkeypatch)
    monkeypatch.setenv("SMART_ENABLED", "1")
    monkeypatch.setenv("SMART_ISSUERS", "{this is not json")
    resp = await api_client.get("/api/v1/smart/config")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["enabled"] is True
    assert payload["issuers"] == []
    assert any("not valid JSON" in error for error in payload["config_errors"])
