"""Deterministic confidence scorer with hook for future ML models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from proc_schemas.billing import BillingLine

_MODEL_PATH = Path(__file__).resolve().parent / "models" / "confidence.pkl"


@dataclass
class ConfidenceResult:
    score: float
    details: Dict[str, float]


def score_confidence(features: Dict[str, float], codes: List[BillingLine], ncci_conflicts: List[Dict]) -> ConfidenceResult:
    base = 0.4
    base += 0.05 * min(features.get("stations", 0), 4)
    base += 0.04 * min(features.get("targets", 0), 4)
    if features.get("has_umls"):
        base += 0.1
    if features.get("laterality"):
        base += 0.05
    base += 0.02 * len(codes)
    base -= 0.1 * len(ncci_conflicts)
    score = max(0.1, min(base, 0.98))
    details = {
        "stations_weight": features.get("stations", 0),
        "targets_weight": features.get("targets", 0),
        "codes_count": len(codes),
        "conflicts": len(ncci_conflicts),
    }
    return ConfidenceResult(score=score, details=details)
