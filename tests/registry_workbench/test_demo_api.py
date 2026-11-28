"""Public robotic/EBUS demo API: stored results for exact reviewed texts only (offline)."""

import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.registry_demo import service, store
from app.registry_demo.routes import router
from app.registry_demo.settings import DEFAULT_DATA_DIR, PLACEHOLDER
from app.registry_workbench.contract_coding import provenance_from_evidence_map

SAMPLES = json.loads((DEFAULT_DATA_DIR / "samples.json").read_text())["samples"]
BY_ID = {s["id"]: s for s in SAMPLES}
COMBINED = BY_ID["ion-ebus-prior-procedure-in-history"]


def _stored(sample, text):
    """A stored entry whose "LLM" side is the generator gold, re-anchored to ``text``."""
    proposal = dict(sample["gold"]["revision"])
    proposal.pop("event_date", None)
    proposal["field_provenance"] = [
        p
        for p in provenance_from_evidence_map(sample["gold"]["evidence"], sample["text"])
        if p["source_excerpt"] in text
    ]
    for p in proposal["field_provenance"]:
        p["source_start"] = text.index(p["source_excerpt"])
        p["source_end"] = p["source_start"] + len(p["source_excerpt"])
    return {
        "sample_id": sample["id"],
        "generated_at": "2026-11-25T00:00:00+00:00",
        "llm": {
            "status": "proposed",
            "warnings": ["requires_clinical_review"],
            "observations": {
                "proposal": proposal,
                "unresolved_mentions": [
                    {"kind": "historical", "note": "prior EBUS", "start": 0, "end": 5}
                ],
                "inference": {
                    "provider": "anthropic",
                    "model": "claude-opus-5-5",
                    "effort": "medium",
                    "cost_usd": 0.07,
                    "request_ids": ["req_secret"],
                    "usage": [{"input_tokens": 1}],
                },
            },
        },
        "rules": {
            "status": "degraded",
            "warnings": ["model_unavailable"],
            "observations": {
                "proposal": {
                    "procedures": proposal["procedures"],
                    "station_surveys": proposal["station_surveys"][:1],
                    "field_provenance": [],
                },
                "inference": {"deterministic_version": "0.2.0", "ner_available": False},
            },
        },
    }


@pytest.fixture
def client(tmp_path, monkeypatch):
    redacted = COMBINED["text"].replace("87-year-old", PLACEHOLDER)
    (tmp_path / "samples.json").write_text(json.dumps({"samples": SAMPLES}))
    (tmp_path / "redactions.json").write_text(
        json.dumps(
            {
                "redactions": {
                    COMBINED["id"]: [
                        {"worker": "module", "text": redacted, "sha256": store.text_key(redacted)}
                    ]
                }
            }
        )
    )
    (tmp_path / "results.json").write_text(
        json.dumps({"entries": {store.text_key(redacted): _stored(COMBINED, redacted)}})
    )
    monkeypatch.setenv("PROCSUITE_DEMO_DATA_DIR", str(tmp_path))
    app = FastAPI()
    app.include_router(router, prefix="/api/v1/demo/robotic-ebus")
    test_client = TestClient(app)
    test_client.redacted = redacted
    return test_client


def test_config_lists_samples_profile_and_no_live_extraction(client):
    config = client.get("/api/v1/demo/robotic-ebus/config").json()
    assert [s["id"] for s in config["samples"]] == [s["id"] for s in SAMPLES]
    assert config["samples"][0]["id"] == "lead-combined-4r-7-11l"
    assert config["placeholder"] == PLACEHOLDER
    assert config["live_extraction"] == {"enabled": False, "reason": "reviewed_samples_only"}
    assert {"schema", "sections", "help"} <= set(config["profile"])
    with_result = {s["id"] for s in config["samples"] if s["has_result"]}
    assert with_result == {COMBINED["id"]}
    assert "text" not in config["samples"][0]


def test_sample_detail_returns_text_and_reviewed_redaction(client):
    detail = client.get(f"/api/v1/demo/robotic-ebus/samples/{COMBINED['id']}").json()
    assert detail["text"] == COMBINED["text"]
    assert detail["reviewed_redactions"] == [{"worker": "module", "text": client.redacted}]
    assert client.get("/api/v1/demo/robotic-ebus/samples/nope").status_code == 404


def test_exact_reviewed_text_returns_the_stored_result(client):
    body = client.post(
        "/api/v1/demo/robotic-ebus/extract",
        json={"text": client.redacted.replace("\n", "\r\n") + "\n", "sample_id": COMBINED["id"]},
    ).json()
    assert body["source"] == "precomputed_sample"
    assert body["source_label"] == "Precomputed sample"
    assert body["sample_id"] == COMBINED["id"]
    llm = body["llm"]
    assert llm["inference"] == {
        "provider": "anthropic",
        "model": "claude-opus-5-5",
        "effort": "medium",
        "cost_usd": 0.07,
    }
    assert llm["unresolved_mentions"][0]["kind"] == "historical"
    for entry in llm["proposal"]["field_provenance"]:
        assert (
            client.redacted[entry["source_start"] : entry["source_end"]]
            == (entry["source_excerpt"])
        )
    summary = body["comparison"]["summary"]
    assert body["comparison"]["sources"] == ["LLM", "Rules engine"]
    assert summary["llm_total"] > summary["rules_total"] > 0
    assert summary["llm_only"] > 0
    # Rules-engine marks: one per model value the rules engine has too, at a real path.
    marks = body["rules_agreement"]
    states = [m["state"] for m in marks.values()]
    assert states.count("agree") == summary["agree"] > 0
    assert states.count("differ") == summary["differ"]
    for path in marks:
        value = llm["proposal"]
        for part in path.strip("/").split("/"):
            value = value[int(part)] if part.isdigit() else value[part]
        assert value is not None, path
    codes = {c["code"]: c for c in body["codes"]["codes"]}
    assert {"31653", "31627", "31654", "31628", "31629", "31623"} == set(codes)
    assert codes["31629"]["modifiers"] == ["59"]
    assert body["codes"]["title"] == "Suggested codes for review"
    for code in codes.values():
        for item in code["evidence"]:
            assert client.redacted[item["start"] : item["end"]] == item["quote"]


@pytest.mark.parametrize(
    "text",
    [
        COMBINED["text"],  # the unredacted sample is not a reviewed text here
        "Station 4R was sampled.",
        "x" + COMBINED["text"].replace("87-year-old", PLACEHOLDER),
    ],
)
def test_anything_but_an_exact_reviewed_text_is_refused(client, text):
    response = client.post("/api/v1/demo/robotic-ebus/extract", json={"text": text})
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "reviewed_samples_only"


def test_empty_and_oversized_text_are_rejected(client):
    assert client.post("/api/v1/demo/robotic-ebus/extract", json={"text": "  "}).status_code == 422
    huge = "a" * 20_001
    assert client.post("/api/v1/demo/robotic-ebus/extract", json={"text": huge}).status_code == 413


def test_the_demo_makes_no_provider_call_and_needs_no_key(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def explode(*args, **kwargs):
        raise AssertionError("the demo must not call a provider")

    monkeypatch.setattr("app.common.anthropic_client.ClaudeClient.complete_json", explode)
    response = client.post("/api/v1/demo/robotic-ebus/extract", json={"text": client.redacted})
    assert response.status_code == 200


def test_the_demo_does_not_load_the_workbench_database():
    assert service.config()["enabled"] is True
    import importlib

    for name in (
        "app.registry_demo.service",
        "app.registry_demo.routes",
        "app.registry_demo.store",
    ):
        source = importlib.import_module(name).__file__
        text = open(source).read()
        assert "registry_workbench.db" not in text and "registry_workbench.service" not in text
        assert "registry_workbench import jobs" not in text


def test_shipped_samples_are_synthetic_safe_for_browser_offsets():
    assert len(SAMPLES) == 8
    for sample in SAMPLES:
        assert PLACEHOLDER not in sample["text"]
        assert "\r" not in sample["text"]
        assert all(ord(ch) <= 0xFFFF for ch in sample["text"])
        assert store.text_key(sample["text"]) == store.text_key(sample["text"] + "\n")


def test_a_reviewed_text_without_a_stored_result_says_so(client, tmp_path):
    other = BY_ID["ion-plain-peripheral"]
    redacted = other["text"].replace("2026-09-01", PLACEHOLDER)
    data = json.loads((tmp_path / "redactions.json").read_text())
    data["redactions"][other["id"]] = [
        {"worker": "module", "text": redacted, "sha256": store.text_key(redacted)}
    ]
    (tmp_path / "redactions.json").write_text(json.dumps(data))
    response = client.post("/api/v1/demo/robotic-ebus/extract", json={"text": redacted})
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "result_not_generated"
