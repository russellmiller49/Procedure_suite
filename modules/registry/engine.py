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
        self,
        note_text: str, *, explain: bool = False, include_evidence: bool = True
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

        # Apply heuristics for EBUS and new fields
        self._apply_ebus_heuristics(merged_data, note_text)

        # Defaults based on cross-field context
        sedation_val = merged_data.get("sedation_type")
        airway_val = merged_data.get("airway_type")
        if airway_val in (None, "", []) :
            if sedation_val == "General":
                merged_data["airway_type"] = "ETT"
            elif sedation_val in ("Moderate", "Deep"):
                merged_data["airway_type"] = "Native"

        # If pleural procedure present but no guidance, default to Blind
        if merged_data.get("pleural_procedure_type") and not merged_data.get("pleural_guidance"):
            merged_data["pleural_guidance"] = "Blind"

        # Ensure version is set if missing (Pydantic default might not trigger if key is missing in dict passed to **)
        if not merged_data.get("version"):
            merged_data["version"] = "0.5.0"

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

    def _apply_ebus_heuristics(self, data: dict[str, Any], text: str) -> None:
        """Apply regex/keyword heuristics for EBUS, sedation reversal, and basic BLVR."""
        
        # --- EBUS Heuristics ---
        # ebus_scope_brand
        if "Olympus" in text and ("BF-UC" in text or "EBUS" in text):
            data["ebus_scope_brand"] = "Olympus"
        elif "Fujifilm" in text or "EB-530" in text or "Fuji" in text:
            data["ebus_scope_brand"] = "Fuji"
        elif "Pentax" in text or "EB-1970" in text:
            data["ebus_scope_brand"] = "Pentax"
        
        # ebus_stations_sampled
        stations_found = set()
        station_pattern = r"Station\s*(2R|2L|4R|4L|7|10R|10L|11R|11L)"
        for match in re.finditer(station_pattern, text, re.IGNORECASE):
            snippet = text[match.end():match.end()+100].lower()
            if any(kw in snippet for kw in ["pass", "sample", "needle", "tbna", "aspirat"]):
                if "not sampled" not in snippet:
                    stations_found.add(match.group(1).upper())
        if stations_found:
            data["ebus_stations_sampled"] = sorted(list(stations_found))

        # ebus_needle_gauge
        gauge_match = re.search(r"(21|22|25)G", text, re.IGNORECASE)
        if gauge_match:
            data["ebus_needle_gauge"] = f"{gauge_match.group(1)}G"

        # ebus_needle_type
        if any(kw in text for kw in ["FNB", "core biopsy", "Acquire"]):
            data["ebus_needle_type"] = "FNB"
        elif "needle" in text.lower() or "tbna" in text.lower():
             if data.get("ebus_needle_type") not in ["FNB"]:
                data["ebus_needle_type"] = "Standard"

        # ebus_systematic_staging
        if re.search(r"Systematic.*(evaluation|staging|N3)", text, re.IGNORECASE):
             if "No systematic" in text or "not systematic" in text.lower():
                 data["ebus_systematic_staging"] = False
             else:
                 data["ebus_systematic_staging"] = True
        elif "No systematic" in text:
             data["ebus_systematic_staging"] = False

        # ebus_rose_available
        if "ROSE" in text or "rapid on-site" in text.lower():
            data["ebus_rose_available"] = True
            if "ROSE not available" in text or "no ROSE" in text.lower():
                data["ebus_rose_available"] = False

        # ebus_rose_result
        if data.get("ebus_rose_available"):
            rose_snippets = []
            for match in re.finditer(r"ROSE\b.*?(?::|-|is|shows|demonstrates|positive|negative)?\s*(.*?)(?:\n|\.|;)", text, re.IGNORECASE):
                rose_snippets.append(match.group(1).lower())
            
            combined_rose = " ".join(rose_snippets)
            if "malignan" in combined_rose or "adenocarcinoma" in combined_rose or "squamous" in combined_rose or "tumor" in combined_rose or "carcinoma" in combined_rose:
                data["ebus_rose_result"] = "Malignant"
            elif "granuloma" in combined_rose:
                data["ebus_rose_result"] = "Granuloma"
            elif "lymphoma" in combined_rose or "lymphoid proliferation" in combined_rose:
                data["ebus_rose_result"] = "Atypical lymphoid proliferation"
            elif "atypical" in combined_rose:
                data["ebus_rose_result"] = "Atypical cells present"
            elif "benign" in combined_rose or "reactive" in combined_rose or "lymphocytes" in combined_rose:
                data["ebus_rose_result"] = "Benign"
            elif "nondiagnostic" in combined_rose or "insufficient" in combined_rose:
                data["ebus_rose_result"] = "Nondiagnostic"

        # ebus_intranodal_forceps_used
        if "intranodal forceps" in text.lower() or "ebus-ifb" in text.lower():
            data["ebus_intranodal_forceps_used"] = True
        
        # ebus_photodocumentation_complete
        if re.search(r"(Complete\s*)?(Photodocumentation|Photodoc|Photos).*(all.*(accessible.*)?stations|complete|taken|archived)|all.*stations.*photographed", text, re.IGNORECASE):
            data["ebus_photodocumentation_complete"] = True
        elif "photos all stations" in text.lower():
            data["ebus_photodocumentation_complete"] = True
        
        # --- Sedation Reversal ---
        reversal_pattern = r"(Flumazenil|Naloxone|Narcan|Romazicon).*?(given|administered|IV)"
        reversal_match = re.search(reversal_pattern, text, re.IGNORECASE)
        if reversal_match:
            data["sedation_reversal_given"] = True
            agent = reversal_match.group(1).capitalize()
            if agent == "Narcan": agent = "Naloxone"
            if agent == "Romazicon": agent = "Flumazenil"
            data["sedation_reversal_agent"] = agent
        else:
            if "no reversal agents" in text.lower():
                 data["sedation_reversal_given"] = False
                 data["sedation_reversal_agent"] = None
            elif "reversal agents" in text.lower() and "administered" not in text.lower() and "given" not in text.lower():
                 if "no reversal" in text.lower() or "reversal agents: none" in text.lower() or "(x) none" in text.lower() or "reversal agents... available" in text.lower() or "at bedside" in text.lower():
                     data["sedation_reversal_given"] = False
                     data["sedation_reversal_agent"] = None

        # --- BLVR Heuristics (Basic) ---
        if "valve" in text.lower():
            # Valve Type
            if "Zephyr" in text:
                data["blvr_valve_type"] = "Zephyr"
            elif "Spiration" in text:
                data["blvr_valve_type"] = "Spiration"
            
            # Target Lobe
            # Look for lobe mention near "valve" or "placed"
            # Simple check for lobe presence if not already set
            if not data.get("blvr_target_lobe"):
                if "left lower lobe" in text.lower() or "LLL" in text:
                    data["blvr_target_lobe"] = "LLL"
                elif "left upper lobe" in text.lower() or "LUL" in text:
                    data["blvr_target_lobe"] = "LUL"
                elif "right lower lobe" in text.lower() or "RLL" in text:
                    data["blvr_target_lobe"] = "RLL"
                elif "right middle lobe" in text.lower() or "RML" in text:
                    data["blvr_target_lobe"] = "RML"
                elif "right upper lobe" in text.lower() or "RUL" in text:
                    data["blvr_target_lobe"] = "RUL"


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