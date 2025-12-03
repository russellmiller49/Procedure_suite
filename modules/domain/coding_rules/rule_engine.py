"""Rule-based coding engine.

This engine applies deterministic rules to identify CPT codes from procedure notes.
It wraps the existing coder logic to provide the RuleResult format expected by
the HybridPolicy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from modules.domain.knowledge_base.repository import KnowledgeBaseRepository
from observability.logging_config import get_logger

logger = get_logger("rule_engine")


@dataclass
class RuleCandidate:
    """A candidate code from rule-based detection."""

    code: str
    confidence: float
    rationale: str
    rule_path: str
    evidence_text: str = ""


@dataclass
class RuleEngineResult:
    """Result from the rule-based coding engine."""

    candidates: list[RuleCandidate] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def codes(self) -> list[str]:
        """Get list of codes."""
        return [c.code for c in self.candidates]

    @property
    def confidence(self) -> dict[str, float]:
        """Get code -> confidence mapping."""
        return {c.code: c.confidence for c in self.candidates}


class RuleEngine:
    """Rule-based CPT code detection engine.

    This engine uses pattern matching and clinical rules to identify
    procedures performed in a note.
    """

    VERSION = "rule_engine_v1"

    def __init__(self, kb_repo: KnowledgeBaseRepository):
        self.kb_repo = kb_repo

    @property
    def version(self) -> str:
        return self.VERSION

    def generate_candidates(self, report_text: str) -> RuleEngineResult:
        """Generate code candidates from the procedure note.

        This is a simplified rule engine that looks for keyword patterns.
        For production, this would integrate with the existing
        modules/coder/engine.py logic.

        Args:
            report_text: The procedure note text.

        Returns:
            RuleEngineResult with candidates and warnings.
        """
        candidates: list[RuleCandidate] = []
        warnings: list[str] = []
        text_lower = report_text.lower()

        # Navigation
        if any(kw in text_lower for kw in ["navigation", "enb", "superdimension", "ion", "monarch"]):
            candidates.append(
                RuleCandidate(
                    code="31627",
                    confidence=0.9,
                    rationale="Navigation bronchoscopy detected",
                    rule_path="navigation_keyword_match",
                )
            )

        # EBUS-TBNA
        if "ebus" in text_lower or "endobronchial ultrasound" in text_lower:
            # Count stations mentioned
            station_count = self._count_ebus_stations(text_lower)
            if station_count >= 3:
                candidates.append(
                    RuleCandidate(
                        code="31653",
                        confidence=0.85,
                        rationale=f"EBUS-TBNA with {station_count} stations",
                        rule_path="ebus_station_count>=3",
                    )
                )
            elif station_count >= 1:
                candidates.append(
                    RuleCandidate(
                        code="31652",
                        confidence=0.85,
                        rationale=f"EBUS-TBNA with {station_count} stations",
                        rule_path="ebus_station_count<3",
                    )
                )

        # Radial EBUS
        if any(kw in text_lower for kw in ["radial ebus", "r-ebus", "radial probe"]):
            candidates.append(
                RuleCandidate(
                    code="+31654",
                    confidence=0.8,
                    rationale="Radial EBUS detected",
                    rule_path="radial_ebus_keyword",
                )
            )

        # Transbronchial biopsy
        if any(kw in text_lower for kw in ["transbronchial biopsy", "tblb", "tbbx", "forceps biopsy"]):
            candidates.append(
                RuleCandidate(
                    code="31628",
                    confidence=0.9,
                    rationale="Transbronchial biopsy detected",
                    rule_path="tblb_keyword_match",
                )
            )

        # TBNA (not EBUS)
        if "tbna" in text_lower and "ebus" not in text_lower:
            candidates.append(
                RuleCandidate(
                    code="31629",
                    confidence=0.8,
                    rationale="Conventional TBNA detected",
                    rule_path="tbna_keyword_match",
                )
            )

        # BAL
        if any(kw in text_lower for kw in ["bronchoalveolar lavage", " bal ", "bal performed"]):
            candidates.append(
                RuleCandidate(
                    code="31624",
                    confidence=0.85,
                    rationale="Bronchoalveolar lavage detected",
                    rule_path="bal_keyword_match",
                )
            )

        # Dilation
        if any(kw in text_lower for kw in ["balloon dilation", "dilation performed", "bronchial dilation"]):
            candidates.append(
                RuleCandidate(
                    code="31630",
                    confidence=0.8,
                    rationale="Airway dilation detected",
                    rule_path="dilation_keyword_match",
                )
            )

        # Stent placement
        if any(kw in text_lower for kw in ["stent placed", "stent deployed", "stent insertion"]):
            if "trachea" in text_lower:
                candidates.append(
                    RuleCandidate(
                        code="31631",
                        confidence=0.9,
                        rationale="Tracheal stent placement detected",
                        rule_path="tracheal_stent_keyword",
                    )
                )
            else:
                candidates.append(
                    RuleCandidate(
                        code="31636",
                        confidence=0.85,
                        rationale="Bronchial stent placement detected",
                        rule_path="bronchial_stent_keyword",
                    )
                )

        # Tumor destruction
        if any(kw in text_lower for kw in [
            "tumor destruction", "debulking", "cryotherapy", "laser", "electrocautery",
            "ablation", "apc", "argon plasma"
        ]):
            candidates.append(
                RuleCandidate(
                    code="31641",
                    confidence=0.85,
                    rationale="Tumor destruction/debulking detected",
                    rule_path="destruction_keyword_match",
                )
            )

        # BLVR valves
        if any(kw in text_lower for kw in ["valve", "blvr", "zephyr", "spiration"]):
            if "removal" not in text_lower:
                candidates.append(
                    RuleCandidate(
                        code="31647",
                        confidence=0.85,
                        rationale="BLVR valve placement detected",
                        rule_path="blvr_keyword_match",
                    )
                )

        # Thoracentesis
        if any(kw in text_lower for kw in ["thoracentesis", "pleural aspiration", "pleural tap"]):
            if "ultrasound" in text_lower or "imaging" in text_lower:
                candidates.append(
                    RuleCandidate(
                        code="32555",
                        confidence=0.85,
                        rationale="Thoracentesis with imaging detected",
                        rule_path="thoracentesis_imaging_keyword",
                    )
                )
            else:
                candidates.append(
                    RuleCandidate(
                        code="32554",
                        confidence=0.8,
                        rationale="Thoracentesis detected",
                        rule_path="thoracentesis_keyword",
                    )
                )

        return RuleEngineResult(candidates=candidates, warnings=warnings)

    def _count_ebus_stations(self, text_lower: str) -> int:
        """Count the number of EBUS stations mentioned."""
        # Common lymph node station patterns
        station_patterns = [
            r"\b4[rl]\b",  # 4R, 4L
            r"\b7\b",  # Station 7
            r"\b10[rl]\b",  # 10R, 10L
            r"\b11[rl]\b",  # 11R, 11L
            r"\bsubcarinal\b",
            r"\bparatracheal\b",
            r"\bhilar\b",
        ]

        stations_found = set()
        for pattern in station_patterns:
            import re
            if re.search(pattern, text_lower):
                stations_found.add(pattern)

        # Also check for explicit station counts
        count_match = re.search(r"(\d+)\s*stations?\b", text_lower)
        if count_match:
            return int(count_match.group(1))

        return len(stations_found)
