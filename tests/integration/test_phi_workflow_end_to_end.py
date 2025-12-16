"""End-to-end PHI workflow integration tests."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")
os.environ.setdefault("PHI_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("PHI_ENCRYPTION_MODE", "demo")
os.environ.setdefault("PHI_SCRUBBER_MODE", "stub")

from modules.api.fastapi_app import app  # noqa: E402
from modules.api.dependencies import get_coding_service  # noqa: E402
from modules.api.phi_dependencies import engine  # noqa: E402
from modules.phi.db import Base  # noqa: E402
from modules.phi import models  # noqa: E402
from modules.coder.phi_gating import is_phi_review_required  # noqa: E402
from proc_schemas.coding import CodingResult  # noqa: E402
from tests.helpers.phi_asserts import assert_no_raw_phi_in_text  # noqa: E402


class FakeCodingService:
    def __init__(self):
        class _KB:
            version = "fake"

            def get_procedure_info(self_inner, code):
                return None

            def get_all_codes(self_inner):
                return []

        self.kb_repo = _KB()
        self.last_report_text = None

    def generate_result(self, procedure_id: str, report_text: str, use_llm: bool = True, procedure_type: str | None = None):
        self.last_report_text = report_text
        return CodingResult(
            procedure_id=procedure_id,
            suggestions=[],
            final_codes=[],
            procedure_type=procedure_type or "unknown",
            processing_time_ms=0.0,
            llm_latency_ms=0.0,
        )


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def override_coding_service():
    fake = FakeCodingService()
    app.dependency_overrides[get_coding_service] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_coding_service, None)


@pytest.fixture(autouse=True)
def require_phi_review(monkeypatch):
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")


def test_phi_to_coding_end_to_end(client, override_coding_service, monkeypatch):
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    raw_text = "Patient X synthetic note for EBUS."

    # Preview
    preview_resp = client.post("/v1/phi/scrub/preview", json={"text": raw_text})
    assert preview_resp.status_code == 200
    preview = preview_resp.json()

    # Submit
    submit_resp = client.post(
        "/v1/phi/submit",
        json={"text": raw_text, "submitted_by": "clinician_demo"},
    )
    assert submit_resp.status_code == 200
    procedure_id = submit_resp.json()["procedure_id"]

    # Feedback to mark reviewed
    feedback_resp = client.post(
        f"/v1/phi/procedure/{procedure_id}/feedback",
        json={
            "scrubbed_text": preview["scrubbed_text"],
            "entities": preview["entities"],
            "reviewer_id": "reviewer_demo",
        },
    )
    assert feedback_resp.status_code == 200
    assert feedback_resp.json()["status"] == models.ProcessingStatus.PHI_REVIEWED.value

    # Coding via primary entrypoint
    coding_resp = client.post(
        f"/api/v1/procedures/{procedure_id}/codes/suggest",
        json={"report_text": "ignored in PHI path", "use_llm": False, "procedure_type": "demo_note"},
    )
    assert coding_resp.status_code == 200
    assert coding_resp.json()["procedure_id"] == procedure_id
    assert override_coding_service.last_report_text == preview["scrubbed_text"]

    # Status check
    status_resp = client.get(f"/v1/phi/status/{procedure_id}")
    assert status_resp.status_code == 200
    status_payload = status_resp.json()
    assert status_payload["status"] in (
        models.ProcessingStatus.PHI_REVIEWED.value,
        models.ProcessingStatus.COMPLETED.value,
    )

    # Reidentify
    reid_resp = client.post("/v1/phi/reidentify", json={"procedure_id": procedure_id, "user_id": "reviewer_demo"})
    assert reid_resp.status_code == 200
    assert reid_resp.json()["raw_text"] == raw_text


def test_cannot_code_without_review_end_to_end(client, monkeypatch):
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    raw_text = "Patient X synthetic pending review"
    submit_resp = client.post(
        "/v1/phi/submit",
        json={"text": raw_text, "submitted_by": "clinician_demo"},
    )
    proc_id = submit_resp.json()["procedure_id"]

    coding_resp = client.post(
        f"/api/v1/procedures/{proc_id}/codes/suggest",
        json={"report_text": "ignored", "use_llm": False, "procedure_type": "demo"},
    )
    assert coding_resp.status_code == 403


def test_no_raw_phi_in_non_reidentify_responses(client, monkeypatch):
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    raw_text = "Patient X synthetic note 01/02/2099 at Fake Hospital"
    preview = client.post("/v1/phi/scrub/preview", json={"text": raw_text}).json()
    submit = client.post("/v1/phi/submit", json={"text": raw_text, "submitted_by": "clinician_demo"}).json()
    proc_id = submit["procedure_id"]

    status_resp = client.get(f"/v1/phi/status/{proc_id}")
    procedure_resp = client.get(f"/v1/phi/procedure/{proc_id}")
    coding_resp = client.post(
        f"/api/v1/procedures/{proc_id}/codes/suggest",
        json={"report_text": "ignored", "use_llm": False, "procedure_type": "demo"},
    )

    fragments = ["Patient X"]
    assert_no_raw_phi_in_text(str(submit), fragments)
    assert_no_raw_phi_in_text(status_resp.text, fragments)
    assert_no_raw_phi_in_text(procedure_resp.text, fragments)
    assert_no_raw_phi_in_text(coding_resp.text, fragments)
    assert "raw_text" not in procedure_resp.text


def test_logs_do_not_contain_raw_phi(client, caplog):
    raw_text = "Patient X synthetic secret"
    with caplog.at_level("INFO"):
        client.post("/v1/phi/scrub/preview", json={"text": raw_text})
    for record in caplog.records:
        msg = record.getMessage()
        assert "Patient X" not in msg
        assert "synthetic secret" not in msg
