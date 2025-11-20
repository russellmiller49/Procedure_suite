"""Registry extraction orchestrator."""

from __future__ import annotations

import re
from typing import Any, Dict

from modules.common.sectionizer import SectionizerService
from modules.common.spans import Span
from modules.registry.extractors.llm_detailed import LLMDetailedExtractor

from .schema import RegistryRecord


class RegistryEngine:
    """Coordinates sectionization, LLM extraction, and record assembly."""

    def __init__(
        self,
        sectionizer: SectionizerService | None = None,
        llm_extractor: LLMDetailedExtractor | None = None,
    ) -> None:
        self.sectionizer = sectionizer or SectionizerService()
        self.llm_extractor = llm_extractor or LLMDetailedExtractor()

    def run(
        self, note_text: str, *, explain: bool = False
    ) -> RegistryRecord | tuple[RegistryRecord, dict[str, list[Span]]]:
        sections = self.sectionizer.sectionize(note_text)
        evidence: Dict[str, list[Span]] = {}
        seed_data: Dict[str, Any] = {}

        mrn_match = re.search(r"MRN:?\s*(\w+)", note_text, re.IGNORECASE)
        if mrn_match:
            seed_data["patient_mrn"] = mrn_match.group(1)
            evidence.setdefault("patient_mrn", []).append(
                Span(text=mrn_match.group(0).strip(), start=mrn_match.start(), end=mrn_match.end())
            )

        llm_result = self.llm_extractor.extract(note_text, sections)
        merged_data = self._merge_llm_and_seed(llm_result.value or {}, seed_data)

        record = RegistryRecord(**merged_data)
        record.evidence = {field: spans for field, spans in evidence.items()}
        if explain:
            return record, record.evidence
        return record

    @staticmethod
    def _merge_llm_and_seed(llm_data: dict[str, Any], seed_data: dict[str, Any]) -> dict[str, Any]:
        merged = dict(llm_data)
        for key, value in seed_data.items():
            if value is None:
                continue
            existing = merged.get(key)
            if existing in (None, "", [], {}):
                merged[key] = value
        return merged


__all__ = ["RegistryEngine"]
