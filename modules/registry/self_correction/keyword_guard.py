"""Cheap keyword guardrail for registry self-correction (Phase 6)."""

from __future__ import annotations

import re

# Minimal CPT → keywords mapping for allowlisted targets.
# This is intentionally conservative: if a CPT has no keywords configured, the
# guard fails and self-correction is skipped for that CPT.
CPT_KEYWORDS: dict[str, list[str]] = {
    # Pleural: indwelling pleural catheter (IPC / PleurX)
    "32550": ["pleurx", "indwelling pleural catheter", "tunneled pleural catheter", "ipc"],
    # Pleural: thoracentesis
    "32554": ["thoracentesis", "pleural fluid removed", "tap"],
    "32555": ["thoracentesis", "pleural fluid removed", "tap"],
    # Pleural: chest tube / thoracostomy
    "32551": ["chest tube", "thoracostomy", "pigtail catheter"],
    # Bronchoscopy add-ons / performed flags
    "31623": ["brushing", "brushings", "bronchial brushing"],
    "31624": ["bronchoalveolar lavage", "bal", "lavage"],
    "31628": ["transbronchial biopsy", "tbbx", "tblb"],
    "31629": ["transbronchial biopsy", "tbbx", "tblb", "fluoroscopy"],
    "31652": ["ebus", "endobronchial ultrasound", "tbna"],
    "31653": ["ebus", "endobronchial ultrasound", "tbna"],
    "31620": ["radial ebus", "radial ultrasound", "rp-ebus"],
    "31627": ["navigational bronchoscopy", "navigation", "electromagnetic navigation", "enb"],
}


def keyword_guard_passes(*, cpt: str, evidence_text: str) -> bool:
    """Return True if any configured keywords hit in evidence_text (case-insensitive)."""
    keywords = CPT_KEYWORDS.get(str(cpt), [])
    if not keywords:
        return False

    text = (evidence_text or "").lower()
    if not text.strip():
        return False

    for keyword in keywords:
        needle = (keyword or "").strip().lower()
        if not needle:
            continue
        if _keyword_hit(text, needle):
            return True
    return False


def _keyword_hit(text_lower: str, needle_lower: str) -> bool:
    if " " in needle_lower or len(needle_lower) >= 5:
        return needle_lower in text_lower
    # Short token (e.g., "ipc", "bal", "tap"): require word boundary to reduce false positives.
    return re.search(rf"\b{re.escape(needle_lower)}\b", text_lower) is not None


__all__ = ["CPT_KEYWORDS", "keyword_guard_passes"]

