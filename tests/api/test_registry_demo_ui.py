"""Routing for the robotic/EBUS demo page: home switch, dashboard route, shared placeholder."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.fastapi_app import app
from app.registry_demo.settings import PLACEHOLDER

os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")

STATIC = Path(__file__).resolve().parents[2] / "ui" / "static" / "phi_redactor"
DEMO_TITLE = "Robotic bronchoscopy + EBUS registry demo"
DASHBOARD_MARK = 'href="./reporter_builder.html"'


@pytest.fixture
def client():
    return TestClient(app)


def _isolated(resp) -> None:
    assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert resp.headers.get("Cross-Origin-Embedder-Policy") == "require-corp"


def test_dashboard_stays_the_home_page_by_default(client, monkeypatch):
    monkeypatch.delenv("PROCSUITE_UI_HOME", raising=False)
    monkeypatch.setenv("PROCSUITE_ROBOTIC_EBUS_DEMO", "1")
    for path in ("/ui/", "/ui/index.html"):
        resp = client.get(path)
        assert resp.status_code == 200
        assert DASHBOARD_MARK in resp.text
        assert DEMO_TITLE not in resp.text


def test_home_switch_serves_the_demo_page_with_isolation_headers(client, monkeypatch):
    monkeypatch.setenv("PROCSUITE_UI_HOME", "robotic_ebus_demo")
    monkeypatch.setenv("PROCSUITE_ROBOTIC_EBUS_DEMO", "1")
    for path in ("/ui/", "/ui/index.html"):
        resp = client.get(path)
        assert resp.status_code == 200
        assert DEMO_TITLE in resp.text
        assert "/ui/registry_demo/registry_demo.js" in resp.text
        _isolated(resp)
        assert resp.headers.get("Cache-Control") == "no-store"


def test_home_switch_needs_the_demo_flag_and_the_atlas_ui(client, monkeypatch):
    monkeypatch.setenv("PROCSUITE_UI_HOME", "robotic_ebus_demo")
    monkeypatch.delenv("PROCSUITE_ROBOTIC_EBUS_DEMO", raising=False)
    assert DASHBOARD_MARK in client.get("/ui/").text
    monkeypatch.setenv("PROCSUITE_ROBOTIC_EBUS_DEMO", "1")
    monkeypatch.setenv("PROCSUITE_UI_VARIANT", "classic")
    assert DEMO_TITLE not in client.get("/ui/").text


@pytest.mark.parametrize("home", ["dashboard", "robotic_ebus_demo"])
def test_dashboard_route_always_serves_the_dashboard(client, monkeypatch, home):
    monkeypatch.setenv("PROCSUITE_UI_HOME", home)
    monkeypatch.setenv("PROCSUITE_ROBOTIC_EBUS_DEMO", "1")
    resp = client.get("/ui/dashboard.html")
    assert resp.status_code == 200
    assert DASHBOARD_MARK in resp.text
    assert "window.__PROCSUITE_UI_VARIANT__" in resp.text
    _isolated(resp)


def test_demo_page_and_assets_are_served_under_ui(client):
    for path in (
        "/ui/registry_demo/",
        "/ui/registry_demo/registry_demo.js",
        "/ui/registry_demo/registry_demo.css",
    ):
        resp = client.get(path)
        assert resp.status_code == 200, path
        _isolated(resp)
    page = client.get("/ui/registry_demo/").text
    # COEP: the page must not pull anything from another origin.
    assert "http://" not in page and "https://" not in page


def test_pages_that_link_to_the_dashboard_name_it():
    assert 'href="./dashboard.html">Dashboard</a>' in (STATIC / "reporter_builder.html").read_text()
    assert (
        'window.location.href = "./dashboard.html";' in (STATIC / "reporter_builder.js").read_text()
    )
    assert 'href="./dashboard.html">Back to Dashboard</a>' in (STATIC / "workflow.html").read_text()
    assert (
        'href="./dashboard.html">Dashboard</a>' in (STATIC / "pdf_local_redaction.html").read_text()
    )
    assert '"../dashboard.html?smart=1"' in (STATIC / "smart" / "callback.js").read_text()


def test_redaction_placeholder_is_the_same_everywhere():
    assert PLACEHOLDER == "[REDACTED]"
    assert "[REDACTED]" in (STATIC / "reporter_builder.js").read_text()
    assert "[REDACTED]" in (STATIC / "registry_demo" / "registry_demo.js").read_text()
    demo_dir = Path(__file__).resolve().parents[2] / "data/knowledge/robotic_ebus_v1/demo"
    import json

    assert json.loads((demo_dir / "samples.json").read_text())["placeholder"] == PLACEHOLDER


def test_every_shipped_sample_has_a_reviewed_redaction_that_is_a_real_redaction():
    import hashlib
    import json

    demo_dir = Path(__file__).resolve().parents[2] / "data/knowledge/robotic_ebus_v1/demo"
    samples = {s["id"]: s for s in json.loads((demo_dir / "samples.json").read_text())["samples"]}
    redactions = json.loads((demo_dir / "redactions.json").read_text())["redactions"]
    assert set(redactions) == set(samples)
    for sample_id, variants in redactions.items():
        assert variants, sample_id
        for variant in variants:
            assert hashlib.sha256(variant["text"].encode()).hexdigest() == variant["sha256"]
            # Every fragment between placeholders appears, in order, in the sample text.
            position, source = 0, samples[sample_id]["text"]
            for fragment in variant["text"].split(PLACEHOLDER):
                found = source.find(fragment, position)
                assert found >= 0, sample_id
                position = found + len(fragment)
            assert PLACEHOLDER in variant["text"], f"{sample_id}: nothing was redacted"


def test_every_reviewed_redaction_has_a_stored_model_result_whose_quotes_match():
    import json

    demo_dir = Path(__file__).resolve().parents[2] / "data/knowledge/robotic_ebus_v1/demo"
    redactions = json.loads((demo_dir / "redactions.json").read_text())["redactions"]
    entries = json.loads((demo_dir / "results.json").read_text())["entries"]
    for sample_id, variants in redactions.items():
        for variant in variants:
            entry = entries.get(variant["sha256"])
            assert entry is not None, f"{sample_id}: no stored result"
            assert entry["sample_id"] == sample_id
            llm = entry["llm"]
            observations = llm["observations"]
            # A public result comes from a real model run, never the development stand-in.
            assert observations["inference"]["provider"] in {"claude", "openai"}, sample_id
            assert llm["status"] == "proposed", sample_id
            assert not observations["inference"]["fallback_used"], sample_id
            for item in observations["proposal"]["field_provenance"]:
                if "source_start" in item:
                    excerpt = variant["text"][item["source_start"] : item["source_end"]]
                    assert excerpt == item["source_excerpt"], (sample_id, item["field_path"])
            assert entry["rules"]["observations"].get("proposal") is not None, sample_id


def test_stored_results_keep_the_four_public_sample_checks():
    """Surveyed stays unsampled, planned stays unperformed, a radial view gives no TIL."""
    import json

    demo_dir = Path(__file__).resolve().parents[2] / "data/knowledge/robotic_ebus_v1/demo"
    samples = {s["id"]: s for s in json.loads((demo_dir / "samples.json").read_text())["samples"]}
    redactions = json.loads((demo_dir / "redactions.json").read_text())["redactions"]
    entries = json.loads((demo_dir / "results.json").read_text())["entries"]
    for sample_id, variants in redactions.items():
        proposal = entries[variants[0]["sha256"]]["llm"]["observations"]["proposal"]
        sample = samples[sample_id]
        gold = (sample.get("gold") or {}).get("revision")
        sampled = {
            s["iaslc_station"] for s in proposal["station_surveys"] if s.get("station_sampled")
        }
        if gold:
            allowed = {
                s["iaslc_station"] for s in gold["station_surveys"] if s.get("station_sampled")
            }
            started = lambda p: {  # noqa: E731
                x["category"]
                for x in p["procedures"]
                if x["performance"] in {"performed", "attempted"}
            }
            assert started(proposal) <= started(gold), sample_id
        else:
            allowed = set(sample["expected"]["stations_sampled"])
        assert sampled <= allowed, sample_id
        for event in proposal["localization_events"]:
            if event.get("tool_lesion_relationship") == "TIL":
                assert event["localization_modality"] != "radial_EBUS", sample_id
