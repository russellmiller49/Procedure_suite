"""Structured report engine tests for NL → structured conversion."""

import json

from modules.reporter.engine import ReportEngine


class StubLLM:
    def __init__(self, payload: dict):
        self.payload = payload

    def generate(self, prompt: str) -> str:
        return json.dumps(self.payload)


def test_engine_autofixes_missing_fields_and_sampling():
    payload = {
        "indication": "",
        "anesthesia": "",
        "survey": [],
        "localization": "",
        "sampling": [],
        "therapeutics": ["Bronchial stent placed"],
        "complications": [],
        "disposition": "",
    }
    engine = ReportEngine(llm=StubLLM(payload))
    report = engine.from_free_text("Sample note")
    assert report.indication == "Unknown"
    assert report.anesthesia == "Unknown"
    assert report.localization == "Unknown"
    assert report.disposition == "Unknown"
    assert report.sampling, "Sampling should receive autofill when therapeutics include stent"


def test_engine_fallback_on_invalid_json():
    class BadLLM:
        def generate(self, prompt: str) -> str:
            return "not json"

    engine = ReportEngine(llm=BadLLM())
    report = engine.from_free_text("note")
    assert report.indication == "Unknown"
    assert report.therapeutics == []

