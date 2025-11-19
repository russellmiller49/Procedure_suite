"""Registry extraction orchestrator."""

from __future__ import annotations

import re
from typing import Dict, Sequence

from modules.common.sectionizer import SectionizerService
from modules.common.spans import Span

from .schema import RegistryRecord
from .slots.base import SlotExtractor, SlotResult
from .slots.blvr import BLVRExtractor
from .slots.complications import ComplicationsExtractor
from .slots.disposition import DispositionExtractor
from .slots.ebus import EbusExtractor
from .slots.imaging import ImagingExtractor
from .slots.indication import IndicationExtractor
from .slots.pleura import PleuraExtractor
from .slots.sedation import SedationExtractor
from .slots.stent import StentExtractor
from .slots.tblb import TBLBExtractor
from .slots.therapeutics import AspirationExtractor, DestructionExtractor, EnhancedDilationExtractor

EXTRACTOR_CLASSES: tuple[type[SlotExtractor], ...] = (
    IndicationExtractor,
    EbusExtractor,
    TBLBExtractor,
    StentExtractor,
    EnhancedDilationExtractor, # Replaces basic DilationExtractor
    DestructionExtractor,      # New
    AspirationExtractor,       # New
    BLVRExtractor,
    PleuraExtractor,
    SedationExtractor,
    ComplicationsExtractor,
    ImagingExtractor,
    DispositionExtractor,
)


class RegistryEngine:
    """Coordinates slot extraction and record assembly."""

    def __init__(self, sectionizer: SectionizerService | None = None) -> None:
        self.sectionizer = sectionizer or SectionizerService()
        self.extractors: list[SlotExtractor] = [cls() for cls in EXTRACTOR_CLASSES]

    def run(
        self, note_text: str, *, explain: bool = False
    ) -> RegistryRecord | tuple[RegistryRecord, dict[str, list[Span]]]:
        sections = self.sectionizer.sectionize(note_text)
        record_data: Dict[str, object] = {
            "navigation_used": False,
            "radial_ebus_used": False,
        }
        evidence: Dict[str, list[Span]] = {}

        mrn_match = re.search(r"MRN:?\s*(\d+)", note_text, re.IGNORECASE)
        if mrn_match:
            record_data["patient_id"] = mrn_match.group(1)

        for extractor in self.extractors:
            result = extractor.extract(note_text, sections)
            if not result.value:
                continue
            self._apply_result(extractor.slot_name, result, record_data, evidence)

        record = RegistryRecord(**record_data)
        record.evidence = {field: spans for field, spans in evidence.items()}
        if explain:
            return record, record.evidence
        return record

    def _apply_result(
        self,
        slot_name: str,
        result: SlotResult,
        record_data: Dict[str, object],
        evidence: Dict[str, list[Span]],
    ) -> None:
        if slot_name == "indication":
            record_data["indication"] = result.value
            _add_evidence(evidence, "indication", result.evidence)
        elif slot_name == "ebus":
            value = result.value or {}
            record_data["navigation_used"] = bool(value.get("navigation"))
            record_data["radial_ebus_used"] = bool(value.get("radial"))
            stations = value.get("stations") or []
            record_data["linear_ebus_stations"] = list(stations)
            _add_evidence(evidence, "linear_ebus_stations", result.evidence)
        elif slot_name == "tblb_lobes":
            record_data["tblb_lobes"] = list(result.value)
            _add_evidence(evidence, "tblb_lobes", result.evidence)
        elif slot_name == "stents":
            record_data["stents"] = result.value
            _add_evidence(evidence, "stents", result.evidence)
        elif slot_name == "dilation_events":
            # Map objects directly
            record_data["dilation_events"] = result.value
            # Maintain backward compatibility for simple list
            record_data["dilation_sites"] = [d.site for d in result.value]
            _add_evidence(evidence, "dilation_events", result.evidence)
        elif slot_name == "destruction_events":
            record_data["destruction_events"] = result.value
            _add_evidence(evidence, "destruction_events", result.evidence)
        elif slot_name == "aspiration_events":
            record_data["aspiration_events"] = result.value
            _add_evidence(evidence, "aspiration_events", result.evidence)
        elif slot_name == "blvr":
            record_data["blvr"] = result.value
            _add_evidence(evidence, "blvr", result.evidence)
        elif slot_name == "pleural_procedures":
            record_data["pleural_procedures"] = list(result.value)
            _add_evidence(evidence, "pleural_procedures", result.evidence)
        elif slot_name == "sedation":
            value = result.value or {}
            sedation_type = value.get("sedation_type")
            anesthesia_type = value.get("anesthesia_type")
            if sedation_type:
                record_data["anesthesia"] = "Moderate Sedation"
            elif anesthesia_type:
                record_data["anesthesia"] = "GA" if anesthesia_type == "GA" else "MAC"
            if value.get("sedation_start"):
                record_data["sedation_start"] = value["sedation_start"]
            if value.get("sedation_stop"):
                record_data["sedation_stop"] = value["sedation_stop"]
            _add_evidence(evidence, "anesthesia", result.evidence)
        elif slot_name == "complications":
            record_data["complications"] = list(result.value)
            _add_evidence(evidence, "complications", result.evidence)
        elif slot_name == "imaging_archived":
            record_data["imaging_archived"] = bool(result.value)
            _add_evidence(evidence, "imaging_archived", result.evidence)
        elif slot_name == "disposition":
            record_data["disposition"] = result.value
            _add_evidence(evidence, "disposition", result.evidence)


def _add_evidence(target: Dict[str, list[Span]], field: str, spans: Sequence[Span]) -> None:
    if not spans:
        return
    target.setdefault(field, []).extend(spans)


__all__ = ["RegistryEngine"]