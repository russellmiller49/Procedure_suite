"""Tester path of the robotic/EBUS demo: password, live reading, spend cap, egress switch.

Offline: the model provider is replaced by a stand-in, so no test calls a provider.
"""

import json
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_demo_api import COMBINED, SAMPLES, _stored

from app.common.exceptions import LLMError
from app.registry_demo import budget, live, routes, store
from app.registry_demo.routes import router
from app.registry_demo.settings import PLACEHOLDER

BASE = "/api/v1/demo/robotic-ebus"
CODES = "alpha-code-1, beta-code-2"
MARKER = "zebrafinch"
OWN_NOTE = (
    f"Patient {PLACEHOLDER}. Robotic bronchoscopy with the Ion platform to a right upper lobe "
    f"nodule ({MARKER}). Linear EBUS: station 7 was sampled with three passes of a 22-gauge "
    "needle. Station 4R was sampled with two passes. No complications."
)


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def model_dump(self, mode="json"):
        return self.payload


@pytest.fixture
def tester(tmp_path, monkeypatch):
    redacted = COMBINED["text"].replace("87-year-old", PLACEHOLDER)
    data = tmp_path / "data"
    data.mkdir()
    (data / "samples.json").write_text(json.dumps({"samples": SAMPLES}))
    (data / "redactions.json").write_text(
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
    (data / "results.json").write_text(
        json.dumps({"entries": {store.text_key(redacted): _stored(COMBINED, redacted)}})
    )
    monkeypatch.setenv("PROCSUITE_DEMO_DATA_DIR", str(data))
    monkeypatch.setenv("PROCSUITE_DEMO_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("PROCSUITE_DEMO_ACCESS_CODE", CODES)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-real")
    for name in (
        "PROCSUITE_LLM_EGRESS_APPROVED",
        "PROCSUITE_LLM_EGRESS_PROVIDERS",
        "PROCSUITE_TRUST_CLIENT_SCRUB",
        "PROCSUITE_DEMO_DAILY_USD_CAP",
        "PROCSUITE_DEMO_RESERVE_USD",
    ):
        monkeypatch.delenv(name, raising=False)
    for limiter in (live.FAILED_CODES, live.LIVE_REQUESTS, routes.RECODE_REQUESTS):
        limiter.clear()

    calls = []
    model = _stored(COMBINED, redacted)["llm"]

    def fake_extract(self, request):
        calls.append(request.text)
        return _Response(json.loads(json.dumps(model)))

    monkeypatch.setattr(
        "app.registry_workbench.extraction.claude_provider.ClaudeRegistryProvider.extract",
        fake_extract,
    )
    app = FastAPI()
    app.include_router(router, prefix=BASE)
    client = TestClient(app)
    client.redacted = redacted
    client.model_calls = calls
    client.data_dir = data
    return client


def _own(client, **overrides):
    body = {
        "text": OWN_NOTE,
        "access_code": "alpha-code-1",
        "note_kind": "synthetic",
        "attested": True,
        **overrides,
    }
    return client.post(f"{BASE}/extract", json=body)


def test_config_turns_tester_access_on_only_when_a_password_is_set(tester, monkeypatch):
    config = tester.get(f"{BASE}/config").json()
    assert config["live_extraction"] == {"enabled": True, "reason": None}
    assert "nothing is stored" in config["notice"]
    monkeypatch.delenv("PROCSUITE_DEMO_ACCESS_CODE")
    config = tester.get(f"{BASE}/config").json()
    assert config["live_extraction"] == {"enabled": False, "reason": "reviewed_samples_only"}
    assert tester.post(f"{BASE}/unlock", json={"access_code": "alpha-code-1"}).status_code == 403
    assert _own(tester).status_code == 403


def test_unlock_accepts_each_password_and_refuses_others(tester):
    for code in ("alpha-code-1", "beta-code-2", "  beta-code-2 "):
        answer = tester.post(f"{BASE}/unlock", json={"access_code": code})
        assert answer.status_code == 200
    body = answer.json()
    assert body["ok"] is True and body["model_configured"] is True
    assert body["real_notes_to_model"] is False
    assert body["model"].startswith("claude-")
    for code in ("alpha-code", "alpha-code-1, beta-code-2", "x"):
        refused = tester.post(f"{BASE}/unlock", json={"access_code": code})
        assert refused.status_code == 401
        assert refused.json()["detail"]["code"] == "bad_access_code"


def test_repeated_wrong_passwords_are_locked_out(tester):
    for _ in range(8):
        assert tester.post(f"{BASE}/unlock", json={"access_code": "nope"}).status_code == 401
    locked = tester.post(f"{BASE}/unlock", json={"access_code": "alpha-code-1"})
    assert locked.status_code == 429


def test_own_note_needs_password_kind_and_confirmation(tester):
    assert tester.post(f"{BASE}/extract", json={"text": OWN_NOTE}).status_code == 403
    assert _own(tester, access_code="wrong").status_code == 401
    assert _own(tester, note_kind="other").json()["detail"]["code"] == "note_kind_required"
    assert _own(tester, attested=False).json()["detail"]["code"] == "attestation_required"
    assert tester.model_calls == []


def test_synthetic_note_is_read_by_the_model_and_nothing_is_stored(tester):
    before = sorted(p.name for p in tester.data_dir.iterdir())
    stamp = (tester.data_dir / "results.json").read_text()
    answer = _own(tester)
    assert answer.status_code == 200
    body = answer.json()
    assert body["source"] == "live" and body["primary"] == "llm"
    assert body["sample_id"] is None and body["text_sha256"] is None
    assert body["reader"] == {
        "model_used": True,
        "sent_to_provider": True,
        "reason": None,
        "message": None,
    }
    assert body["llm"]["proposal"] and body["rules"]["proposal"]
    assert body["codes"]["codes"]
    assert tester.model_calls == [store.normalise(OWN_NOTE)]
    assert sorted(p.name for p in tester.data_dir.iterdir()) == before
    assert (tester.data_dir / "results.json").read_text() == stamp
    assert budget.spent_today() == pytest.approx(0.07)


def test_without_a_key_the_rules_engine_reads_the_note(tester, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    body = _own(tester).json()
    assert body["primary"] == "rules" and body["llm"] is None
    assert body["reader"]["reason"] == "model_not_configured"
    assert body["reader"]["sent_to_provider"] is False
    assert body["rules"]["proposal"]["procedures"]
    assert body["codes"] is not None
    assert tester.model_calls == [] and budget.spent_today() == 0


def test_real_redacted_note_stays_on_the_server_until_all_three_switches_are_set(
    tester, monkeypatch
):
    body = _own(tester, note_kind="real_redacted").json()
    assert body["reader"]["reason"] == "real_notes_not_approved"
    assert body["reader"]["sent_to_provider"] is False and body["primary"] == "rules"
    monkeypatch.setenv("PROCSUITE_LLM_EGRESS_APPROVED", "1")
    monkeypatch.setenv("PROCSUITE_LLM_EGRESS_PROVIDERS", "anthropic")
    assert _own(tester, note_kind="real_redacted").json()["reader"]["reason"] == (
        "real_notes_not_approved"
    )
    assert tester.model_calls == []

    monkeypatch.setenv("PROCSUITE_TRUST_CLIENT_SCRUB", "1")
    unlocked = tester.post(f"{BASE}/unlock", json={"access_code": "alpha-code-1"}).json()
    assert unlocked["real_notes_to_model"] is True
    body = _own(tester, note_kind="real_redacted").json()
    assert body["reader"]["model_used"] is True and body["primary"] == "llm"
    assert len(tester.model_calls) == 1


def test_the_daily_cap_stops_model_calls(tester, monkeypatch):
    monkeypatch.setenv("PROCSUITE_DEMO_DAILY_USD_CAP", "0.10")
    monkeypatch.setenv("PROCSUITE_DEMO_RESERVE_USD", "0.08")
    assert _own(tester).json()["reader"]["model_used"] is True  # spends 0.07
    body = _own(tester).json()
    assert body["reader"]["reason"] == "daily_cap_reached" and body["primary"] == "rules"
    assert len(tester.model_calls) == 1
    assert budget.spent_today() == pytest.approx(0.07)


@pytest.mark.parametrize(
    ("error", "charged"),
    [("APITimeoutError", 0.75), ("AuthenticationError", 0.0)],
)
def test_a_failed_model_call_falls_back_to_the_rules_engine(tester, monkeypatch, error, charged):
    def broken(self, request):
        raise LLMError(f"Claude request failed: {error}: provider said no")

    monkeypatch.setattr(
        "app.registry_workbench.extraction.claude_provider.ClaudeRegistryProvider.extract",
        broken,
    )
    body = _own(tester).json()
    assert body["reader"]["reason"] == "model_call_failed" and body["primary"] == "rules"
    assert body["rules"]["proposal"]
    assert budget.spent_today() == pytest.approx(charged)


def test_a_bundled_sample_is_still_answered_from_the_stored_result(tester):
    answer = _own(tester, text=tester.redacted)
    assert answer.status_code == 200
    assert answer.json()["source"] == "precomputed_sample"
    assert tester.model_calls == []


def test_logs_carry_no_note_text(tester, caplog):
    with caplog.at_level(logging.DEBUG):
        assert _own(tester).status_code == 200
        assert _own(tester, note_kind="real_redacted").status_code == 200
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "source=live" in logged
    assert MARKER not in logged and "Ion platform" not in logged


def test_codes_follow_a_reviewer_correction(tester):
    stored = tester.post(f"{BASE}/extract", json={"text": tester.redacted}).json()
    proposal = stored["llm"]["proposal"]
    same = tester.post(f"{BASE}/codes", json={"proposal": proposal}).json()
    assert [c["code"] for c in same["codes"]] == [c["code"] for c in stored["codes"]["codes"]]
    assert "31653" in [c["code"] for c in same["codes"]]

    corrected = json.loads(json.dumps(proposal))
    kept = corrected["station_surveys"][0]["station_survey_id"]
    for row in corrected["station_surveys"]:
        if row["station_survey_id"] != kept:
            row["station_sampled"] = False
    after = tester.post(f"{BASE}/codes", json={"proposal": corrected}).json()
    codes = [c["code"] for c in after["codes"]]
    assert "31653" not in codes


def test_codes_endpoint_refuses_what_it_cannot_read(tester):
    broken = tester.post(f"{BASE}/codes", json={"proposal": {"procedures": "not a list"}})
    assert broken.status_code in (200, 422)
    huge = {"procedures": [], "padding": "x" * 700_000}
    assert tester.post(f"{BASE}/codes", json={"proposal": huge}).status_code == 413
