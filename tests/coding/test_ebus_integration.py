"""Integration-style tests ensuring EBUS candidates flow through the coder."""

from __future__ import annotations

import os

from modules.autocode.coder import EnhancedCPTCoder
from modules.coder.types import CodeCandidate, EBUSNodeEvidence


class StubEBUSExtractor:
    def __init__(self, evidence: list[EBUSNodeEvidence]):
        self._evidence = evidence

    def extract(self, scrubbed_text: str):
        return list(self._evidence)


def test_enhanced_cptcoder_merges_ebus_candidates(monkeypatch):
    monkeypatch.setenv("CODING_EBUS_TUPLE_MODE", "true")
    evidence = [EBUSNodeEvidence(station="7", action="Sampling")]
    extractor = StubEBUSExtractor(evidence)
    coder = EnhancedCPTCoder(ebus_extractor=extractor, use_llm_advisor=False)

    monkeypatch.setattr(
        coder,
        "_collect_initial_candidates",
        lambda *args, **kwargs: [],
        raising=False,
    )

    suggestions = coder._generate_codes({"note_text": "EBUS staging performed"}, term_hits={})
    codes = {s.cpt for s in suggestions}
    assert "31652" in codes
