"""Presidio-based scrubber adapter (synthetic PHI demo ready).

Implements PHIScrubberPort using Presidio AnalyzerEngine. Avoids logging raw
PHI and preserves IP anatomical terms via allowlist filtering.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Iterable

from modules.phi.ports import PHIScrubberPort, ScrubResult

logger = logging.getLogger(__name__)


ANATOMICAL_ALLOW_LIST = {
    # Lung lobes and shorthand
    "upper lobe",
    "lower lobe",
    "middle lobe",
    "right upper lobe",
    "rul",
    "right middle lobe",
    "rml",
    "right lower lobe",
    "rll",
    "left upper lobe",
    "lul",
    "left lower lobe",
    "lll",
    "lingula",
    # Airway structures
    "carina",
    "trachea",
    "bronchus",
    "bronchi",
    "mainstem",
    "segmental",
    "subsegmental",
    # Stations
    "station 4r",
    "station 4l",
    "station 7",
    "station 2r",
    "station 2l",
    "station 10",
    "station 11",
    "station 12",
    # Mediastinal/lymphatic terms
    "mediastinum",
    "hilum",
    "hilar",
    "paratracheal",
    # Procedures/techniques
    "ebus",
    "eus",
    "tbna",
    "bal",
    "bronchoscopy",
    # Laterality descriptors
    "left",
    "right",
    "bilateral",
    "unilateral",
}


def _build_analyzer(model_name: str):
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider

    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": model_name}],
        }
    )
    nlp_engine = provider.create_engine()
    return AnalyzerEngine(nlp_engine=nlp_engine)


@lru_cache()
def _get_analyzer(model_name: str):
    try:
        analyzer = _build_analyzer(model_name)
        logger.info("PresidioScrubber initialized", extra={"model": model_name})
        return analyzer
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "PresidioScrubber initialization failed; ensure presidio-analyzer and spaCy model are installed."
        ) from exc


class PresidioScrubber(PHIScrubberPort):
    """Presidio-powered scrubber with IP allowlist filtering."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("PRESIDIO_NLP_MODEL", "en_core_web_lg")
        self._analyzer = _get_analyzer(self.model_name)

    def _is_allowlisted(self, text: str) -> bool:
        lower = text.lower()
        if lower in ANATOMICAL_ALLOW_LIST:
            return True
        # Simple substring heuristic for composite phrases
        for term in ANATOMICAL_ALLOW_LIST:
            if term in lower:
                return True
        return False

    def _placeholder(self, entity_type: str, index: int) -> str:
        return f"<{entity_type.upper()}_{index}>"

    def scrub(self, text: str, document_type: str | None = None, specialty: str | None = None) -> ScrubResult:
        if not text:
            return ScrubResult(scrubbed_text="", entities=[])

        # Analyze
        results = self._analyzer.analyze(
            text=text,
            language="en",
            entities=[
                "PERSON",
                "EMAIL_ADDRESS",
                "PHONE_NUMBER",
                "US_SSN",
                "LOCATION",
                "DATE_TIME",
                "US_DRIVER_LICENSE",
                "MEDICAL_LICENSE",
            ],
        )

        # Filter and build entity list
        filtered = []
        for res in results:
            detected_text = text[res.start : res.end]
            if self._is_allowlisted(detected_text):
                continue
            filtered.append(res)

        # Replace from end to start to preserve offsets
        scrubbed_text = text
        entities = []
        for idx, res in enumerate(sorted(filtered, key=lambda r: r.start, reverse=True)):
            placeholder = self._placeholder(res.entity_type, idx)
            scrubbed_text = (
                scrubbed_text[: res.start] + placeholder + scrubbed_text[res.end :]
            )
            entities.append(
                {
                    "placeholder": placeholder,
                    "entity_type": res.entity_type,
                    "original_start": res.start,
                    "original_end": res.end,
                }
            )

        # Preserve ordering from original text (ascending) for entity map
        entities = list(reversed(entities))
        return ScrubResult(scrubbed_text=scrubbed_text, entities=entities)


__all__ = ["PresidioScrubber"]
