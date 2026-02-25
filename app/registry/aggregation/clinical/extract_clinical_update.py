"""Deterministic clinical-update extractor (MVP)."""

from __future__ import annotations

import re
from typing import Any

from app.registry.aggregation.sanitize import compact_text


_PERFORMANCE_RE = re.compile(
    r"\b(?:ECOG\s*[:=]?\s*\d(?:\s*[-/]\s*\d)?|performance\s+status\s*[:=]?\s*[^\n\.;]{1,50})\b",
    re.IGNORECASE,
)

_TREATMENT_RE = re.compile(
    r"\b(?:started|initiated|completed|discontinued|held|resumed)\b[^\n\.;]{0,120}\b(?:therapy|immunotherapy|chemotherapy|radiation|treatment|steroid|antibiotic)s?\b",
    re.IGNORECASE,
)

_COMPLICATION_KEYWORDS = [
    "pneumothorax",
    "hemoptysis",
    "bleeding",
    "hypoxia",
    "fever",
    "infection",
    "respiratory failure",
]


def _symptom_change(text: str) -> str | None:
    value = text.lower()
    if re.search(r"\b(?:improved|better|resolving)\b", value):
        return "Better"
    if re.search(r"\b(?:worse|worsened|progressive|declined)\b", value):
        return "Worse"
    if re.search(r"\b(?:stable|unchanged)\b", value):
        return "Stable"
    return None


def _extract_complication_text(text: str) -> str | None:
    value = text or ""
    for keyword in _COMPLICATION_KEYWORDS:
        match = re.search(rf"\b{re.escape(keyword)}\b[^\n\.;]{{0,100}}", value, re.IGNORECASE)
        if match:
            return compact_text(match.group(0), max_chars=160)
    return None


def extract_clinical_update_event(
    text: str,
    *,
    update_type: str,
    relative_day_offset: int | None,
) -> dict[str, Any]:
    """Extract minimal structured clinical update fields."""

    clean = text or ""
    qa_flags: list[str] = []

    performance_status_text = None
    performance_match = _PERFORMANCE_RE.search(clean)
    if performance_match:
        performance_status_text = compact_text(performance_match.group(0), max_chars=80)

    treatment_change_text = None
    treatment_match = _TREATMENT_RE.search(clean)
    if treatment_match:
        treatment_change_text = compact_text(treatment_match.group(0), max_chars=140)

    complication_text = _extract_complication_text(clean)
    symptom_change = _symptom_change(clean)

    summary_text = compact_text(clean, max_chars=220)
    if not any([performance_status_text, treatment_change_text, complication_text, symptom_change]):
        qa_flags.append("minimal_structure_extracted")

    return {
        "clinical_update": {
            "relative_day_offset": int(relative_day_offset or 0),
            "update_type": update_type,
            "performance_status_text": performance_status_text,
            "symptom_change": symptom_change,
            "treatment_change_text": treatment_change_text,
            "complication_text": complication_text,
            "summary_text": summary_text or None,
            "qa_flags": sorted(set(qa_flags)),
        },
        "qa_flags": sorted(set(qa_flags)),
    }


__all__ = ["extract_clinical_update_event"]
