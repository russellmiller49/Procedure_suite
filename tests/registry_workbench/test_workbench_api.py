"""Workbench API: cases, extraction runs, revisions, approval, analysis (offline)."""

import json
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.registry_workbench import jobs
from app.registry_workbench.db import Event, session_factory
from app.registry_workbench.routes import router

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/registry_workbench"
TEXT = (FIXTURES / "rebus_demo_procedure.txt").read_text()
FACTS = json.loads((FIXTURES / "rebus_demo_facts.json").read_text())


class _Stream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class _FakeSDK:
    def __init__(self, payload):
        self.payload = payload
        self.messages = self
        self.beta = self

    def stream(self, **params):
        return _Stream(
            {
                "id": "msg_wb",
                "model": params["model"],
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": json.dumps(self.payload)}],
                "usage": {
                    "input_tokens": 1000,
                    "output_tokens": 3000,
                    "cache_read_input_tokens": 7000,
                },
            }
        )


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("REGISTRY_WORKBENCH_DATABASE_URL", f"sqlite:///{tmp_path / 'wb.db'}")
    monkeypatch.setenv("PROCSUITE_WORKBENCH_INLINE_JOBS", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-used")
    monkeypatch.setattr(jobs, "SDK_FACTORY", lambda: _FakeSDK(FACTS))
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/workbench")
    return TestClient(app)


def _case(client, label="demo"):
    case = client.post(
        "/api/v1/workbench/cases",
        json={"label": label, "synthetic_attestation": True, "event_date": "2018-12-21"},
    ).json()
    document = client.post(
        f"/api/v1/workbench/cases/{case['id']}/documents",
        json={"kind": "procedure", "text": TEXT, "synthetic_attestation": True},
    ).json()
    return case, document


def _extract(client, document_id, provider):
    run = client.post(
        f"/api/v1/workbench/documents/{document_id}/extractions", json={"provider": provider}
    ).json()
    return client.get(f"/api/v1/workbench/extractions/{run['id']}").json()


def test_profile_carries_schema_and_dictionary_help(client):
    profile = client.get("/api/v1/workbench/profile").json()
    assert profile["schema_version"] == "0.2.0"
    assert (
        "Bronchus visibly leading" in profile["help"]["targets.bronchus_sign_present"]["definition"]
    )
    assert profile["sections"]["station_surveys"] == "Stations surveyed and sampled"


def test_manual_entries_require_a_synthetic_attestation(client):
    response = client.post("/api/v1/workbench/cases", json={"label": "x"})
    assert response.status_code == 422


def test_deterministic_and_claude_runs_produce_comparable_proposals(client):
    case, document = _case(client)
    deterministic = _extract(client, document["id"], "deterministic")
    claude = _extract(client, document["id"], "claude")
    assert deterministic["status"] == "succeeded" and claude["status"] == "succeeded"
    assert claude["proposal_status"] == "proposed" and claude["model"] == "claude-opus-5-5"
    assert claude["cost_usd"] and claude["cost_usd"] > 0
    proposal = claude["response"]["observations"]["proposal"]
    assert proposal["field_provenance"][0]["source_document_id"] == document["id"]
    compared = client.get(
        f"/api/v1/workbench/cases/{case['id']}/compare",
        params={"runs": f"{deterministic['id']},{claude['id']}"},
    ).json()
    lobe = next(r for r in compared["rows"] if r["row"] == "lung RUL" and r["field"] == "lobe")
    assert lobe["agree"] is True


def test_claude_requires_configuration(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    _, document = _case(client)
    response = client.post(
        f"/api/v1/workbench/documents/{document['id']}/extractions", json={"provider": "claude"}
    )
    assert response.status_code == 409


def test_assisted_revision_approval_analysis_and_gold_export(client):
    case, document = _case(client)
    run = _extract(client, document["id"], "claude")
    values = {**run["response"]["observations"]["proposal"], "event_date": "2018-12-21"}
    saved = client.post(
        f"/api/v1/workbench/cases/{case['id']}/revisions",
        json={
            "expected_version": 1,
            "values": values,
            "mode": "assisted",
            "source_run_ids": [run["id"]],
        },
    )
    assert saved.status_code == 201
    stale = client.post(
        f"/api/v1/workbench/cases/{case['id']}/revisions",
        json={"expected_version": 1, "values": values, "mode": "assisted"},
    )
    assert stale.status_code == 409
    detail = client.get(f"/api/v1/workbench/cases/{case['id']}").json()
    assert detail["status"] == "draft" and detail["version"] == 2
    approved = client.post(
        f"/api/v1/workbench/cases/{case['id']}/approve",
        json={"expected_version": 2, "revision_id": saved.json()["revision_id"]},
    )
    assert approved.status_code == 200
    analysis = client.get("/api/v1/workbench/analysis").json()
    assert len(analysis["tables"]["cases"]) == 1
    assert analysis["measures"]["counts"]["cases_received"] == 1
    gold = [
        json.loads(line)
        for line in client.get("/api/v1/workbench/export/gold.jsonl").text.splitlines()
    ]
    assert gold[0]["review_mode"] == "assisted" and gold[0]["qualification_eligible"] is False
    worklist = client.get("/api/v1/workbench/cases").json()
    assert worklist[0]["status"] == "approved" and "pathology" in worklist[0]["missing"]


def test_tampered_evidence_is_rejected(client):
    case, document = _case(client)
    run = _extract(client, document["id"], "claude")
    values = {**run["response"]["observations"]["proposal"], "event_date": "2018-12-21"}
    entry = next(p for p in values["field_provenance"] if p.get("source_excerpt"))
    entry["source_excerpt"] = "X" * len(entry["source_excerpt"])
    response = client.post(
        f"/api/v1/workbench/cases/{case['id']}/revisions",
        json={"expected_version": 1, "values": values, "mode": "assisted"},
    )
    assert (
        response.status_code == 422
        and response.json()["detail"]["code"] == "evidence_span_mismatch"
    )


def test_unresolved_conflicts_block_approval(client):
    case, document = _case(client)
    run = _extract(client, document["id"], "claude")
    values = {**run["response"]["observations"]["proposal"], "event_date": "2018-12-21"}
    values["field_provenance"][0]["conflict_status"] = "unresolved"
    saved = client.post(
        f"/api/v1/workbench/cases/{case['id']}/revisions",
        json={"expected_version": 1, "values": values, "mode": "blinded"},
    ).json()
    response = client.post(
        f"/api/v1/workbench/cases/{case['id']}/approve",
        json={"expected_version": 2, "revision_id": saved["revision_id"]},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["errors"] == ["unresolved_field_conflict"]


def test_viewing_an_exposed_document_is_recorded(client):
    from app.registry_workbench import service

    with session_factory()() as db:
        case = service.create_case(db, label="exposed", source="corpus:test", split="test")
        document = service.add_document(
            db, case, kind="procedure", text=TEXT, exposure="exposed_test"
        )
        db.commit()
        document_id = document.id
    assert client.get(f"/api/v1/workbench/documents/{document_id}").json()["text"] == TEXT
    with session_factory()() as db:
        kinds = [e.kind for e in db.query(Event).filter(Event.document_id == document_id)]
    assert "exposed_document_viewed" in kinds


def test_unknown_case_is_not_found(client):
    assert client.get(f"/api/v1/workbench/cases/{uuid.uuid4()}").status_code == 404


def test_compare_treats_not_documented_as_absent():
    from app.registry_workbench.compare import compare

    rows = compare(
        {
            "a": {"procedures": [{"category": "linear_ebus", "performance": "performed"}]},
            "b": {
                "procedures": [
                    {"category": "linear_ebus", "performance": "performed", "planned": None}
                ],
                "complication_assessment": "not_documented",
            },
        }
    )
    assert [r["field"] for r in rows] == ["category", "performance"] and all(
        r["agree"] for r in rows
    )


def test_main_app_does_not_expose_the_workbench_by_default():
    from app.api.fastapi_app import app as main_app

    assert not [
        r
        for r in main_app.routes
        if getattr(r, "path", "").startswith(("/api/v1/workbench", "/workbench"))
    ]
