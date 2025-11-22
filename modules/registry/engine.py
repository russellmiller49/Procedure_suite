"""Registry extraction orchestrator."""

from __future__ import annotations

import re
from typing import Any, Dict

from modules.common.sectionizer import SectionizerService
from modules.common.spans import Span
from modules.registry.extractors.llm_detailed import LLMDetailedExtractor
from modules.registry.postprocess import POSTPROCESSORS

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
        self, note_text: str, *, explain: bool = False, include_evidence: bool = True
    ) -> RegistryRecord | tuple[RegistryRecord, dict[str, list[Span]]]:
        sections = self.sectionizer.sectionize(note_text)
        evidence: Dict[str, list[Span]] = {}
        seed_data: Dict[str, Any] = {}

        mrn_match = re.search(r"MRN:?\s*(\w+)", note_text, re.IGNORECASE)
        if mrn_match:
            seed_data["patient_mrn"] = mrn_match.group(1)
            if include_evidence:
                evidence.setdefault("patient_mrn", []).append(
                    Span(text=mrn_match.group(0).strip(), start=mrn_match.start(), end=mrn_match.end())
                )

        llm_result = self.llm_extractor.extract(note_text, sections)
        llm_data_raw = llm_result.value or {}
        llm_data = llm_data_raw if isinstance(llm_data_raw, dict) else {}

        # LLM responses sometimes return an "evidence" map with offsets only. Strip or
        # normalize them so pydantic validation does not fail when building the record.
        raw_llm_evidence = None
        if isinstance(llm_data, dict):
            raw_llm_evidence = llm_data.pop("evidence", None)

        merged_data = self._merge_llm_and_seed(llm_data, seed_data)

        # Apply field-specific normalization/postprocessing before validation
        for field, func in POSTPROCESSORS.items():
            if field in merged_data:
                merged_data[field] = func(merged_data.get(field))

        # Defaults based on cross-field context
        sedation_val = merged_data.get("sedation_type")
        airway_val = merged_data.get("airway_type")
        if airway_val in (None, "", []):
            if sedation_val == "General":
                merged_data["airway_type"] = "ETT"
            elif sedation_val in ("Moderate", "Deep"):
                merged_data["airway_type"] = "Native"

        # If pleural procedure present but no guidance, default to Blind
        if merged_data.get("pleural_procedure_type") and not merged_data.get("pleural_guidance"):
            merged_data["pleural_guidance"] = "Blind"

        # EBUS fields suppressed per latest instructions
        merged_data["ebus_needle_gauge"] = None
        merged_data["ebus_rose_result"] = None

        record = RegistryRecord(**merged_data)
        normalized_evidence: dict[str, list[Span]] = {}
        if include_evidence:
            normalized_evidence = self._normalize_evidence(note_text, raw_llm_evidence)

            # Merge evidence gathered from regex seeding (e.g., MRN) with any usable LLM
            # evidence. The normalize helper already guards against malformed entries.
            for field, spans in evidence.items():
                normalized_evidence.setdefault(field, []).extend(spans)

        record.evidence = {field: spans for field, spans in normalized_evidence.items()}
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

    @staticmethod
    def _normalize_evidence(note_text: str, raw_evidence: Any) -> dict[str, list[Span]]:
        """Convert loose evidence payloads into Span objects.

        The LLM can emit evidence as dicts with start/end offsets but no text, or even
        as a single dict instead of a list. We defensively coerce these into the
        expected ``dict[str, list[Span]]`` shape and drop anything malformed.
        """

        normalized: dict[str, list[Span]] = {}
        if not isinstance(raw_evidence, dict):
            return normalized

        for field, spans in raw_evidence.items():
            span_candidates = spans if isinstance(spans, list) else [spans]
            for span_data in span_candidates:
                if not isinstance(span_data, dict):
                    continue

                start = span_data.get("start") or span_data.get("start_offset")
                end = span_data.get("end") or span_data.get("end_offset")
                if start is None or end is None:
                    continue

                try:
                    start_i = int(start)
                    end_i = int(end)
                except (TypeError, ValueError):
                    continue

                text = span_data.get("text")
                if text is None:
                    text = note_text[start_i:end_i]

                section = span_data.get("section")
                confidence = span_data.get("confidence")

                normalized.setdefault(field, []).append(
                    Span(text=str(text), start=start_i, end=end_i, section=section, confidence=confidence)
                )

        return normalized


__all__ = ["RegistryEngine"]
