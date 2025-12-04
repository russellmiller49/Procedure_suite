"""API tests for coding PHI gating."""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

# Ensure PHI config is test-friendly
os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")
os.environ.setdefault("PHI_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("PHI_ENCRYPTION_MODE", "demo")
os.environ.setdefault("CODER_REQUIRE_PHI_REVIEW", "true")

from modules.api.fastapi_app import app  # noqa: E402
from modules.api.phi_dependencies import SessionLocal, engine  # noqa: E402
from modules.api.dependencies import get_coding_service  # noqa: E402
from modules.phi import models  # noqa: E402
from modules.phi.db import Base  # noqa: E402
from proc_schemas.coding import CodingResult  # noqa: E402


class FakeCodingService:
    def __init__(self):
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
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def override_coding_service():
    fake = FakeCodingService()
    app.dependency_overrides[get_coding_service] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_coding_service, None)


@pytest.fixture()
def client():
    return TestClient(app)


def test_coding_rejected_when_not_reviewed(client):
    submit_resp = client.post(
        "/v1/phi/submit",
        json={"text": "Patient X synthetic note.", "submitted_by": "clinician_demo"},
    )
    proc_id = submit_resp.json()["procedure_id"]

    resp = client.post(
        f"/api/v1/procedures/{proc_id}/codes/suggest",
        json={"report_text": "legacy text", "use_llm": False, "procedure_type": "unknown"},
    )
    assert resp.status_code == 403


def test_coding_allowed_after_review_uses_scrubbed_text(client, override_coding_service):
    submit_resp = client.post(
        "/v1/phi/submit",
        json={"text": "Patient X synthetic note.", "submitted_by": "clinician_demo"},
    )
    proc_id = submit_resp.json()["procedure_id"]
    scrubbed_text = submit_resp.json()["scrubbed_text"]

    feedback_resp = client.post(
        f"/v1/phi/procedure/{proc_id}/feedback",
        json={
            "scrubbed_text": scrubbed_text,
            "entities": [
                {"placeholder": "[[REDACTED]]", "entity_type": "PERSON", "original_start": 0, "original_end": 7}
            ],
            "reviewer_id": "reviewer_demo",
        },
    )
    assert feedback_resp.status_code == 200
    assert feedback_resp.json()["status"] == models.ProcessingStatus.PHI_REVIEWED.value

    resp = client.post(
        f"/api/v1/procedures/{proc_id}/codes/suggest",
        json={"report_text": "legacy text", "use_llm": False, "procedure_type": "unknown"},
    )
    assert resp.status_code == 200
    assert override_coding_service.last_report_text == scrubbed_text


def test_coder_run_blocked_when_review_required(client):
    resp = client.post(
        "/v1/coder/run",
        json={"note": "Patient X synthetic note.", "allow_weak_sedation_docs": False},
    )
    assert resp.status_code == 400
