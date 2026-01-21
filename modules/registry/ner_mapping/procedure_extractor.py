"""Procedure extraction from NER entities.

Maps NER entities to procedure boolean flags in RegistryRecord.

The granular NER model may emit procedure *devices* (e.g., `DEV_STENT`) instead
of `PROC_METHOD`/`PROC_ACTION` spans; those device entities must still drive the
corresponding clinical performed flags to avoid falling back to regex uplift.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from modules.ner.inference import NEREntity, NERExtractionResult


@dataclass
class ProcedureExtractionResult:
    """Result from procedure extraction."""

    procedure_flags: Dict[str, bool]
    """Map of procedure name to performed flag."""

    evidence: Dict[str, List[str]]
    """Map of procedure name to evidence texts."""

    warnings: List[str] = field(default_factory=list)


# Mapping from keyword patterns to procedure field names
PROCEDURE_MAPPINGS: Dict[str, Tuple[Set[str], str]] = {
    # EBUS procedures
    "linear_ebus": (
        {"ebus", "convex ebus", "linear ebus", "endobronchial ultrasound"},
        "procedures_performed.linear_ebus.performed",
    ),
    "radial_ebus": (
        {"radial ebus", "radial endobronchial ultrasound", "rebus", "miniprobe", "radial probe"},
        "procedures_performed.radial_ebus.performed",
    ),

    # Navigation
    "navigational_bronchoscopy": (
        {
            "navigation",
            "enb",
            "superdimension",
            "ion",
            "monarch",
            "electromagnetic navigation",
            "robotic bronchoscopy",
            "robotic-assisted bronchoscopy",
            "robotic assisted bronchoscopy",
        },
        "procedures_performed.navigational_bronchoscopy.performed",
    ),

    # Biopsies
    "transbronchial_biopsy": (
        {"transbronchial biopsy", "tbbx", "tblb", "transbronchial lung biopsy"},
        "procedures_performed.transbronchial_biopsy.performed",
    ),
    "transbronchial_cryobiopsy": (
        {"cryobiopsy", "cryo biopsy", "transbronchial cryobiopsy", "cryo tbbx"},
        "procedures_performed.transbronchial_cryobiopsy.performed",
    ),
    "endobronchial_biopsy": (
        {"endobronchial biopsy", "ebbx", "bronchial biopsy"},
        "procedures_performed.endobronchial_biopsy.performed",
    ),

    # Sampling procedures
    "bal": (
        {"bal", "bronchoalveolar lavage", "lavage"},
        "procedures_performed.bal.performed",
    ),
    "brushings": (
        {"brushing", "brushings", "brush", "cytology brush", "bronchial brushing", "bronchial brush"},
        "procedures_performed.brushings.performed",
    ),
    "tbna_conventional": (
        {"tbna", "transbronchial needle aspiration", "transbronchial needle"},
        "procedures_performed.tbna_conventional.performed",
    ),

    # Therapeutic procedures
    "therapeutic_aspiration": (
        {"therapeutic aspiration", "suctioning", "mucus plug"},
        "procedures_performed.therapeutic_aspiration.performed",
    ),
    "airway_dilation": (
        {"dilation", "balloon dilation", "bougie", "airway dilation"},
        "procedures_performed.airway_dilation.performed",
    ),
    "airway_stent": (
        {"stent", "dumon", "y-stent", "silicone stent", "metal stent"},
        "procedures_performed.airway_stent.performed",
    ),

    # Ablation procedures
    "thermal_ablation": (
        {"apc", "argon plasma", "electrocautery", "laser", "thermal ablation"},
        "procedures_performed.thermal_ablation.performed",
    ),
    "cryotherapy": (
        {"cryotherapy", "cryo ablation", "cryo debulking"},
        "procedures_performed.cryotherapy.performed",
    ),
    "tumor_debulking": (
        {"debulking", "tumor debulking", "mechanical debridement"},
        "procedures_performed.tumor_debulking_non_thermal.performed",
    ),

    # BLVR
    "blvr": (
        {"blvr", "bronchoscopic lung volume reduction", "valve", "zephyr"},
        "procedures_performed.blvr.performed",
    ),

    # Pleural procedures
    "thoracentesis": (
        {"thoracentesis", "pleural tap"},
        "pleural_procedures.thoracentesis.performed",
    ),
    "chest_tube": (
        {"chest tube", "pigtail catheter", "tube thoracostomy"},
        "pleural_procedures.chest_tube.performed",
    ),
    "ipc": (
        {"ipc", "indwelling pleural catheter", "pleurx"},
        "pleural_procedures.ipc.performed",
    ),
    "medical_thoracoscopy": (
        {"thoracoscopy", "pleuroscopy", "medical thoracoscopy"},
        "pleural_procedures.medical_thoracoscopy.performed",
    ),
    "pleurodesis": (
        {"pleurodesis", "talc", "chemical pleurodesis"},
        "pleural_procedures.pleurodesis.performed",
    ),

    # Tracheostomy
    "percutaneous_tracheostomy": (
        {"tracheostomy", "percutaneous tracheostomy", "pdt"},
        "procedures_performed.percutaneous_tracheostomy.performed",
    ),

    # Other
    "rigid_bronchoscopy": (
        {"rigid bronchoscopy", "rigid scope"},
        "procedures_performed.rigid_bronchoscopy.performed",
    ),
    "foreign_body_removal": (
        {"foreign body", "foreign body removal", "retrieval"},
        "procedures_performed.foreign_body_removal.performed",
    ),
}


class ProcedureExtractor:
    """Extract procedure flags from NER entities."""

    def __init__(self) -> None:
        # Pre-compile patterns
        self._patterns = self._compile_patterns()

    def field_path_for(self, proc_name: str) -> str | None:
        """Return the RegistryRecord field path for a procedure key."""
        pattern = self._patterns.get(proc_name)
        if not pattern:
            return None
        return pattern[1]

    def _keyword_hit(self, text_lower: str, needle: str) -> bool:
        """Return True if needle matches text.

        Short tokens (e.g., "ion", "enb", "bal") require word boundaries to
        avoid false positives from substrings like "aspiratION".
        """
        needle_lower = (needle or "").lower()
        if " " in needle_lower or len(needle_lower) >= 5:
            return needle_lower in text_lower
        return re.search(rf"\b{re.escape(needle_lower)}\b", text_lower) is not None

    def _compile_patterns(self) -> Dict[str, Tuple[List[str], str]]:
        """Convert keyword sets to sorted lists for consistent matching."""
        patterns = {}
        for proc_name, (keywords, field_path) in PROCEDURE_MAPPINGS.items():
            # Sort by length (longest first) for greedy matching
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            patterns[proc_name] = (sorted_keywords, field_path)
        return patterns

    def extract(self, ner_result: NERExtractionResult) -> ProcedureExtractionResult:
        """
        Extract procedure flags from NER entities.

        Args:
            ner_result: NER extraction result with entities

        Returns:
            ProcedureExtractionResult with procedure flags
        """
        proc_methods = ner_result.entities_by_type.get("PROC_METHOD", [])
        proc_actions = ner_result.entities_by_type.get("PROC_ACTION", [])
        device_hints = (
            ner_result.entities_by_type.get("DEV_STENT", [])
            + ner_result.entities_by_type.get("DEV_INSTRUMENT", [])
            + ner_result.entities_by_type.get("DEV_DEVICE", [])
        )

        # Combine method and action entities for procedure detection
        all_proc_entities = proc_methods + proc_actions + device_hints

        procedure_flags: Dict[str, bool] = {}
        evidence: Dict[str, List[str]] = {}
        warnings: List[str] = []

        raw_text = ner_result.raw_text or ""
        raw_lower = raw_text.lower()
        ebus_context_re = re.compile(
            r"\b(?:ebus|endobronchial\s+ultrasound|convex\s+probe|ebus[-\s]?tbna)\b",
            re.IGNORECASE,
        )

        for entity in all_proc_entities:
            text_lower = entity.text.lower()
            if raw_lower and entity.start_char is not None and entity.end_char is not None:
                window_start = max(0, entity.start_char - 100)
                window_end = min(len(raw_lower), entity.end_char + 100)
                entity_context = raw_lower[window_start:window_end]
            else:
                entity_context = ""
            radial_keywords = self._patterns.get("radial_ebus", ([], ""))[0]
            radial_hit = any(self._keyword_hit(text_lower, kw) for kw in radial_keywords)

            for proc_name, (keywords, field_path) in self._patterns.items():
                if proc_name == "linear_ebus" and radial_hit:
                    continue
                for keyword in keywords:
                    if self._keyword_hit(text_lower, keyword):
                        if proc_name == "tbna_conventional" and entity_context and ebus_context_re.search(entity_context):
                            continue
                        # Found a match
                        procedure_flags[proc_name] = True

                        if proc_name not in evidence:
                            evidence[proc_name] = []
                        evidence[proc_name].append(entity.text)

                        break  # Only match first keyword per entity

        return ProcedureExtractionResult(
            procedure_flags=procedure_flags,
            evidence=evidence,
            warnings=warnings,
        )

    def extract_valve_count(self, ner_result: NERExtractionResult) -> int:
        """
        Extract valve count from NER entities for BLVR codes.

        Args:
            ner_result: NER extraction result

        Returns:
            Number of valves mentioned (0 if not found)
        """
        # Look for DEV_VALVE entities
        valves = ner_result.entities_by_type.get("DEV_VALVE", [])

        # Also check MEAS_COUNT entities near valve mentions
        counts = ner_result.entities_by_type.get("MEAS_COUNT", [])

        # Simple heuristic: count unique valve mentions
        return len(valves)

    def extract_lobe_locations(self, ner_result: NERExtractionResult) -> List[str]:
        """
        Extract lobe locations for transbronchial biopsy codes.

        Args:
            ner_result: NER extraction result

        Returns:
            List of unique lobe codes (RUL, RML, etc.)
        """
        lung_locs = ner_result.entities_by_type.get("ANAT_LUNG_LOC", [])

        lobes = set()
        lobe_patterns = {
            "rul": "RUL",
            "rml": "RML",
            "rll": "RLL",
            "lul": "LUL",
            "lll": "LLL",
            "lingula": "Lingula",
            "right upper": "RUL",
            "right middle": "RML",
            "right lower": "RLL",
            "left upper": "LUL",
            "left lower": "LLL",
        }

        for entity in lung_locs:
            text_lower = entity.text.lower()
            for pattern, lobe_code in lobe_patterns.items():
                if pattern in text_lower:
                    lobes.add(lobe_code)
                    break

        return sorted(lobes)
