from __future__ import annotations

import os
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from modules.api.fastapi_app import app
from modules.api.dependencies import get_coding_service, get_registry_service
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


def test_unified_process_already_scrubbed_bypasses_server_scrubber(monkeypatch, client: TestClient) -> None:
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
    from modules.api import fastapi_app as fastapi_app_module

    def _fail_apply(*_args, **_kwargs):
        raise AssertionError("apply_phi_redaction should not be called when already_scrubbed=true")

    monkeypatch.setattr(fastapi_app_module, "apply_phi_redaction", _fail_apply)

    async def _run_cpu_direct(_app, fn, *args):  # noqa: ANN001
        return fn(*args)

    monkeypatch.setattr(fastapi_app_module, "run_cpu", _run_cpu_direct)

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

