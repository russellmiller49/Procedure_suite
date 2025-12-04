"""Presidio scrubber adapter scaffold.

Placeholder for future Presidio integration. Currently falls back to the stub
scrubber behavior to keep tests passing without Presidio installed.
"""

from __future__ import annotations

import os

from modules.phi.adapters.scrubber_stub import StubScrubber
from modules.phi.ports import PHIScrubberPort, ScrubResult


class PresidioScrubberAdapter(PHIScrubberPort):
    """Stub Presidio adapter; replace with real Presidio wiring later."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("PRESIDIO_NLP_MODEL", "en_core_web_lg")
        # For now, reuse the stub behavior to keep tests fast
        self._fallback = StubScrubber()

    def scrub(self, text: str, document_type: str | None = None, specialty: str | None = None) -> ScrubResult:
        # TODO: integrate Presidio AnalyzerEngine when available
        return self._fallback.scrub(text, document_type=document_type, specialty=specialty)


__all__ = ["PresidioScrubberAdapter"]
