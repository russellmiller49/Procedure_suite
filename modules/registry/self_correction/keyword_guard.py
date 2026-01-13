"""Guardrails for registry extraction self-correction (Phase 6).

Includes:
- CPT keyword gating (prevents self-correction when evidence text lacks keywords)
- Omission detection (detects high-value terms in raw text that were missed)
"""

from __future__ import annotations

import re

from modules.common.logger import get_logger
from modules.registry.schema import RegistryRecord

logger = get_logger("keyword_guard")

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
    "31654": ["radial ebus", "radial ultrasound", "rp-ebus"],
    "31627": ["navigational bronchoscopy", "navigation", "electromagnetic navigation", "enb"],
}

# -----------------------------------------------------------------------------
# Omission Detection ("Safety Net")
# -----------------------------------------------------------------------------
# Dictionary mapping a Registry Field Path -> List of (Regex, Failure Message).
# If the Regex matches the text, the Registry Field MUST be True (or populated).
# -----------------------------------------------------------------------------
REQUIRED_PATTERNS: dict[str, list[tuple[str, str]]] = {
    # Fixes missed tracheostomy (Report #3)
    "procedures_performed.percutaneous_tracheostomy.performed": [
        (r"(?i)\btracheostomy\b", "Text contains 'tracheostomy' but extraction missed it."),
        (r"(?i)\bportex\b", "Text contains 'Portex' (trach device) but extraction missed it."),
        (r"(?i)\bshiley\b", "Text contains 'Shiley' (trach device) but extraction missed it."),
        (r"(?i)\bperc\s+trach\b", "Text contains 'perc trach' but extraction missed it."),
        (r"(?i)\bpercutaneous\s+tracheostomy\b", "Text contains 'percutaneous tracheostomy' but extraction missed it."),
    ],
    # Fixes missed endobronchial biopsy (Report #2)
    "procedures_performed.endobronchial_biopsy.performed": [
        (r"(?i)\bendobronchial\s+biopsy\b", "Text explicitly states 'endobronchial biopsy'."),
        (r"(?i)\blesions?\s+were\s+biopsied\b", "Text states 'lesions were biopsied' (likely endobronchial)."),
        (r"(?i)\bbiopsy\s+of\s+(?:the\s+)?(?:lesion|mass|polyp)\b", "Text describes biopsy of a lesion/mass/polyp."),
    ],
    # Fixes missed neck ultrasound (Report #3)
    "procedures_performed.neck_ultrasound.performed": [
        (r"(?i)\bneck\s+ultrasound\b", "Text contains 'neck ultrasound'."),
        (r"(?i)\bultrasound\s+of\s+(?:the\s+)?neck\b", "Text contains 'ultrasound of the neck'."),
    ],
}


def scan_for_omissions(note_text: str, record: RegistryRecord) -> list[str]:
    """Scan raw text for required patterns missing from the extracted record.

    Returns warning strings suitable for surfacing in API responses and for
    triggering manual review or a retry/self-correction loop.
    """
    warnings: list[str] = []

    for field_path, rules in REQUIRED_PATTERNS.items():
        if _is_field_populated(record, field_path):
            continue

        for pattern, msg in rules:
            if re.search(pattern, note_text or ""):
                warning = f"SILENT_FAILURE: {msg} (Pattern: '{pattern}')"
                warnings.append(warning)
                logger.warning(warning, extra={"field": field_path, "pattern": pattern})
                break

    return warnings


def _is_field_populated(record: RegistryRecord, path: str) -> bool:
    """Safely navigate the RegistryRecord using dot-notation and check truthiness."""
    try:
        current: object | None = record
        for part in path.split("."):
            if current is None:
                return False

            if hasattr(current, part):
                current = getattr(current, part)
                continue

            if isinstance(current, dict) and part in current:
                current = current[part]
                continue

            return False

        return bool(current)
    except Exception as exc:  # pragma: no cover
        logger.error("Error checking field population for %s: %s", path, exc)
        return False


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


__all__ = [
    "CPT_KEYWORDS",
    "REQUIRED_PATTERNS",
    "keyword_guard_passes",
    "scan_for_omissions",
]
