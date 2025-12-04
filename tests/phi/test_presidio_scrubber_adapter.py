"""Smoke test for PresidioScrubberAdapter stub."""

from __future__ import annotations

from modules.phi.adapters.presidio_scrubber import PresidioScrubberAdapter


def test_presidio_scrubber_stub_behaves_like_stub_scrubber():
    adapter = PresidioScrubberAdapter(model_name="fake_model")
    result = adapter.scrub("Patient X synthetic note.")

    assert result.scrubbed_text.startswith("[[REDACTED]]")
    assert result.entities
