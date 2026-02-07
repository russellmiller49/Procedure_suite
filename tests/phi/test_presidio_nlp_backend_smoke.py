"""Smoke tests for PresidioScrubber NLP backend wiring.

Skipped unless presidio_analyzer and the requested spaCy/SciSpaCy model are installed.
"""

from __future__ import annotations

import pytest

pytest.importorskip("presidio_analyzer")
spacy = pytest.importorskip("spacy")

from app.phi.adapters.presidio_scrubber import PresidioScrubber


def _first_loadable_model(candidates: list[str]) -> str | None:
    for name in candidates:
        try:
            spacy.load(name)
            return name
        except Exception:  # noqa: BLE001
            continue
    return None


@pytest.mark.parametrize(
    ("backend", "model_candidates"),
    [
        ("spacy", ["en_core_web_lg", "en_core_web_sm"]),
        ("scispacy", ["en_core_sci_sm", "en_core_sci_md", "en_core_sci_lg"]),
    ],
)
def test_presidio_scrubber_initializes_with_backend(monkeypatch, backend: str, model_candidates: list[str]):
    model_name = _first_loadable_model(model_candidates)
    if model_name is None:
        pytest.skip(f"No installed model found for backend={backend}: {model_candidates}")

    monkeypatch.setenv("NLP_BACKEND", backend)
    monkeypatch.setenv("PRESIDIO_NLP_MODEL", model_name)

    scrubber = PresidioScrubber()
    result, audit = scrubber.scrub_with_audit("Patient: Fisher, Sarah")

    assert isinstance(result.scrubbed_text, str)
    assert isinstance(audit, dict)
