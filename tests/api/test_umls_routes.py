import pytest


@pytest.mark.asyncio
async def test_umls_suggest_uses_local_fixture(api_client, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.umls.ip_umls_store import get_ip_umls_store

    get_ip_umls_store.cache_clear()
    monkeypatch.setenv("UMLS_ENABLE_LINKER", "true")
    monkeypatch.setenv("ENABLE_UMLS_LINKER", "true")
    monkeypatch.setenv("UMLS_LINKER_BACKEND", "distilled")
    monkeypatch.setenv("UMLS_IP_UMLS_MAP_LOCAL_PATH", "tests/fixtures/ip_umls_map.small.json")
    monkeypatch.setenv("UMLS_IP_UMLS_MAP_S3_URI", "")

    resp = await api_client.get("/api/v1/umls/suggest", params={"q": "rb", "category": "anatomy", "limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data
    assert data[0]["term"].startswith("rb")


@pytest.mark.asyncio
async def test_umls_concept_looks_up_cui(api_client, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.umls.ip_umls_store import get_ip_umls_store

    get_ip_umls_store.cache_clear()
    monkeypatch.setenv("UMLS_ENABLE_LINKER", "true")
    monkeypatch.setenv("ENABLE_UMLS_LINKER", "true")
    monkeypatch.setenv("UMLS_LINKER_BACKEND", "distilled")
    monkeypatch.setenv("UMLS_IP_UMLS_MAP_LOCAL_PATH", "tests/fixtures/ip_umls_map.small.json")
    monkeypatch.setenv("UMLS_IP_UMLS_MAP_S3_URI", "")

    resp = await api_client.get("/api/v1/umls/concept/C0001")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["cui"] == "C0001"
    assert payload["preferred_name"] == "Right upper lobe"

