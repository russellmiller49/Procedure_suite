"""Integration-style tests to ensure peripheral candidates enter the pipeline."""

from __future__ import annotations

from modules.autocode.coder import EnhancedCPTCoder
from modules.coder.types import PeripheralLesionEvidence


class StubPeripheralExtractor:
    def __init__(self, evidence: list[PeripheralLesionEvidence]):
        self._evidence = evidence

    def extract(self, scrubbed_text: str):
        return list(self._evidence)


def test_enhanced_cptcoder_merges_peripheral_candidates(monkeypatch):
    monkeypatch.setenv("CODING_PERIPHERAL_TUPLE_MODE", "true")
    monkeypatch.delenv("CODING_EBUS_TUPLE_MODE", raising=False)

    evidence = [
        PeripheralLesionEvidence(
            lobe="LLL",
            segment="LB10",
            actions=["Cryobiopsy", "Fiducial", "BAL"],
            navigation=True,
            radial_ebus=True,
        )
    ]
    extractor = StubPeripheralExtractor(evidence)
    coder = EnhancedCPTCoder(peripheral_extractor=extractor, use_llm_advisor=False)

    # Avoid relying on the legacy KB for these tests.
    monkeypatch.setattr(
        coder,
        "_collect_initial_candidates",
        lambda *args, **kwargs: [],
        raising=False,
    )
    monkeypatch.setattr(
        coder,
        "_collect_ebus_candidates",
        lambda *args, **kwargs: [],
        raising=False,
    )

    suggestions = coder._generate_codes({"note_text": "Peripheral lesion case"}, term_hits={})
    codes = {suggestion.cpt for suggestion in suggestions}

    assert {"31628", "31626", "31624", "31627", "31654"}.issubset(codes)
