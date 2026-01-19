import pytest
from fastapi.testclient import TestClient

from modules.api.dependencies import get_coding_service, get_registry_service
from modules.api.fastapi_app import app
from modules.api.readiness import require_ready
from modules.common.spans import Span
from modules.registry.application.registry_service import RegistryExtractionResult
from modules.registry.schema import RegistryRecord


@pytest.fixture(autouse=True)
def production_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_SCHEMA_VERSION", "v3")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("PROCSUITE_ALLOW_LEGACY_ENDPOINTS", "0")
    monkeypatch.setenv("PROCSUITE_ALLOW_REQUEST_MODE_OVERRIDE", "0")
    monkeypatch.setenv("PROCSUITE_SKIP_DOTENV", "1")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    yield


class _DummyKB:
    version = "test_kb"

    def get_procedure_info(self, code):
        class _Info:
            description = f"Desc {code}"
            work_rvu = 1.0
            total_facility_rvu = 2.0

        return _Info()


class _DummyCodingService:
    kb_repo = _DummyKB()


class _DummyRegistryService:
    def extract_fields(self, note_text, mode: str = "default"):
        record = RegistryRecord()
        record.evidence = {
            "ner_spans": [Span(text="cryoprobe", start=10, end=19, confidence=1.0)]
        }
        return RegistryExtractionResult(
            record=record,
            cpt_codes=["31654"],
            coder_difficulty="HIGH_CONF",
            coder_source="parallel_ner",
            mapped_fields={},
        )


@pytest.fixture
def client():
    app.dependency_overrides[get_registry_service] = lambda: _DummyRegistryService()
    app.dependency_overrides[get_coding_service] = lambda: _DummyCodingService()
    app.dependency_overrides[require_ready] = lambda: None
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_process_route_header_and_review_status(client):
    resp = client.post(
        "/api/v1/process",
        json={
            "note": "Scrubbed note text",
            "already_scrubbed": True,
            "include_financials": False,
            "explain": True,
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("X-Process-Route") == "router"
    data = resp.json()
    assert data["review_status"] == "pending_phi_review"
    assert data["needs_manual_review"] is True


def test_legacy_lockout_registry_extract(client):
    resp = client.post(
        "/api/registry/extract",
        json={"note_text": "Scrubbed note text"},
    )
    assert resp.status_code == 410


def test_legacy_lockout_procedure_extract(client):
    resp = client.post(
        "/api/v1/procedures/00000000-0000-0000-0000-000000000000/extract",
        json={"include_financials": False},
    )
    assert resp.status_code == 410


def test_parallel_ner_evidence_payload(client):
    resp = client.post(
        "/api/v1/process",
        json={
            "note": "Scrubbed note text",
            "already_scrubbed": True,
            "include_financials": False,
            "explain": True,
        },
    )
    assert resp.status_code == 200
    evidence = resp.json().get("evidence") or {}
    assert "ner_spans" in evidence
    assert evidence["ner_spans"][0]["source"] == "ner_span"
    assert evidence["ner_spans"][0]["text"] == "cryoprobe"
    assert evidence["ner_spans"][0]["span"] == [10, 19]


def test_config_crash_on_parallel_ner_mode(monkeypatch):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "parallel_ner")
    with pytest.raises(RuntimeError):
        with TestClient(app):
            pass
