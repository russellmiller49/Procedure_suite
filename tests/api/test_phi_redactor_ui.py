from __future__ import annotations

import os
import re
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from modules.api.dependencies import get_coding_service, get_registry_service
from modules.api.fastapi_app import app
from modules.api.phi_dependencies import get_phi_scrubber
from modules.api.readiness import require_ready

os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")


@pytest.fixture
def client():
    return TestClient(app)


def test_phi_redactor_index_has_coop_coep_headers(client: TestClient) -> None:
    resp = client.get("/ui/phi_redactor/")
    assert resp.status_code == 200
    assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert resp.headers.get("Cross-Origin-Embedder-Policy") == "require-corp"

def test_phi_redactor_redirects_trailing_slash(client: TestClient) -> None:
    resp = client.get("/ui/phi_redactor", follow_redirects=False)
    assert resp.status_code in (301, 302, 303, 307, 308)
    assert resp.headers.get("location") == "/ui/phi_redactor/"
    # Even the redirect response should carry headers for debugging/consistency.
    assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert resp.headers.get("Cross-Origin-Embedder-Policy") == "require-corp"


def test_phi_redactor_assets_have_coop_coep_headers(client: TestClient) -> None:
    """Test that all PHI redactor static assets have COOP/COEP headers."""
    for path in (
        "/ui/phi_redactor/index.html",
        "/ui/phi_redactor/app.js",
        "/ui/phi_redactor/redactor.worker.js",
        "/ui/phi_redactor/styles.css",
        "/ui/phi_redactor/allowlist_trie.json",
        "/ui/phi_redactor/sw.js",
    ):
        resp = client.get(path)
        assert resp.status_code == 200, path
        assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin", (
            f"Missing COOP header for {path}"
        )
        assert resp.headers.get("Cross-Origin-Embedder-Policy") == "require-corp", (
            f"Missing COEP header for {path}"
        )

def test_phi_redactor_index_has_formatted_report_sections(client: TestClient) -> None:
    resp = client.get("/ui/phi_redactor/index.html")
    assert resp.status_code == 200
    assert 'id="billingSelectedBody"' in resp.text
    assert 'id="evidenceTraceabilityHost"' in resp.text

def test_phi_redactor_worker_stoplist_includes_lymph_nodes(client: TestClient) -> None:
    """Regression: don't treat "Lymph Nodes" headings as patient names."""
    resp = client.get("/ui/phi_redactor/redactor.worker.js")
    assert resp.status_code == 200
    body = resp.text
    assert re.search(
        r"const\s+NAME_REGEX_CLINICAL_STOPLIST\s*=\s*new\s+Set\(\[[\s\S]*?\"lymph\"[\s\S]*?\"node\"[\s\S]*?\"nodes\"",
        body,
        re.MULTILINE,
    ), "Expected lymph/node/nodes in NAME_REGEX_CLINICAL_STOPLIST"


def test_phi_redactor_worker_gates_procedure_for_clinical_phrases(client: TestClient) -> None:
    """Regression: don't flag 'EBUS for peripheral lesion' as a patient name."""
    resp = client.get("/ui/phi_redactor/redactor.worker.js")
    assert resp.status_code == 200
    body = resp.text
    assert re.search(
        r"for\s*\(const\s+match\s+of\s+text\.matchAll\(PROCEDURE_FOR_NAME_RE\)\)\s*\{[\s\S]*?isInClinicalStoplist\(firstName\)[\s\S]*?continue;",
        body,
        re.MULTILINE,
    ), "Expected clinical stoplist gating inside PROCEDURE_FOR_NAME_RE loop"


def test_phi_redactor_legacy_worker_has_same_regression_fixes(client: TestClient) -> None:
    resp = client.get("/ui/redactor.worker.legacy.js")
    assert resp.status_code == 200
    body = resp.text
    assert re.search(
        r"const\s+NAME_REGEX_CLINICAL_STOPLIST\s*=\s*new\s+Set\(\[[\s\S]*?\"lymph\"[\s\S]*?\"node\"[\s\S]*?\"nodes\"",
        body,
        re.MULTILINE,
    ), "Expected lymph/node/nodes in legacy NAME_REGEX_CLINICAL_STOPLIST"
    assert re.search(
        r"for\s*\(const\s+match\s+of\s+text\.matchAll\(PROCEDURE_FOR_NAME_RE\)\)\s*\{[\s\S]*?isInClinicalStoplist\(firstName\)[\s\S]*?continue;",
        body,
        re.MULTILINE,
    ), "Expected clinical stoplist gating inside legacy PROCEDURE_FOR_NAME_RE loop"


def test_unified_process_already_scrubbed_bypasses_server_scrubber(
    monkeypatch, client: TestClient
) -> None:
    class StubRegistryService:
        def __init__(self) -> None:
            self.seen_note: str | None = None

        def extract_fields(self, note_text: str):
            self.seen_note = note_text
            record = SimpleNamespace(model_dump=lambda **_: {})
            return SimpleNamespace(
                record=record,
                cpt_codes=[],
                coder_difficulty="HIGH_CONF",
                coder_source="stub",
                mapped_fields={},
                derivation_warnings=[],
                warnings=[],
                needs_manual_review=False,
                validation_errors=[],
                audit_warnings=[],
            )

    class StubKBRepo:
        version = "test_kb"

        def get_procedure_info(self, _code: str):
            return None

    class StubCodingService:
        kb_repo = StubKBRepo()

    stub_registry = StubRegistryService()

    # Hard-fail if the server-side scrubbing helper is invoked.
    from modules.api.services import unified_pipeline as unified_pipeline_module

    def _fail_apply(*_args, **_kwargs):
        raise AssertionError("apply_phi_redaction should not be called when already_scrubbed=true")

    monkeypatch.setattr(unified_pipeline_module, "apply_phi_redaction", _fail_apply)

    async def _run_cpu_direct(_app, fn, *args):  # noqa: ANN001
        return fn(*args)

    monkeypatch.setattr(unified_pipeline_module, "run_cpu", _run_cpu_direct)

    # Avoid unrelated readiness dependencies
    app.dependency_overrides[require_ready] = lambda: None
    app.dependency_overrides[get_registry_service] = lambda: stub_registry
    app.dependency_overrides[get_coding_service] = lambda: StubCodingService()
    app.dependency_overrides[get_phi_scrubber] = lambda: (lambda text: text)

    try:
        note = "RAW_TEXT_SHOULD_PASS_THROUGH_UNCHANGED"
        resp = client.post(
            "/api/v1/process",
            json={"note": note, "already_scrubbed": True, "include_financials": False},
        )
        assert resp.status_code == 200
        assert stub_registry.seen_note == note
    finally:
        app.dependency_overrides.clear()
