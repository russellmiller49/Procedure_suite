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
    "32551": ["chest tube", "tube thoracostomy", "thoracostomy", "pleur-evac", "pleurovac"],
    # Pleural: percutaneous pleural drainage catheter (pigtail) without/with imaging
    "32556": ["pigtail catheter", "pleural drainage", "seldinger", "pleurovac"],
    "32557": ["pigtail catheter", "pleural drainage", "ultrasound", "imaging guidance", "seldinger", "pleurovac"],
    # Diagnostic chest ultrasound
    "76604": ["chest ultrasound", "ultrasound findings", "with image documentation", "image saved"],
    # Bronchoscopy add-ons / performed flags
    "31623": ["brushing", "brushings", "bronchial brushing"],
    "31624": [
        "bronchoalveolar lavage",
        "broncho alveolar lavage",
        "broncho-alveolar lavage",
        "bronchial alveolar lavage",
        "bal",
        "lavage",
    ],
    "31626": ["fiducial", "fiducial marker", "fiducial placement"],
    "31628": [
        "transbronchial biopsy",
        "transbronchial biops",
        "transbronchial bx",
        "transbronchial forceps biopsy",
        "transbronchial forceps biops",
        "tbbx",
        "tblb",
    ],
    "31629": ["tbna", "transbronchial needle aspiration", "transbronchial needle"],
    "31652": [
        "ebus",
        "endobronchial ultrasound",
        "tbna",
        "transbronchial needle aspiration",
        "transbronchial needle",
    ],
    "31653": [
        "ebus",
        "endobronchial ultrasound",
        "tbna",
        "transbronchial needle aspiration",
        "transbronchial needle",
    ],
    # Tumor debulking / destruction
    "31640": [
        "31640",
        "mechanical debulk",
        "mechanical excision",
        "tumor excision",
        "forceps debulk",
        "rigid coring",
        "microdebrider",
        "snare resection",
    ],
    "31641": [
        "31641",
        "apc",
        "argon plasma",
        "electrocautery",
        "laser",
        "ablation",
        "tumor base ablation",
        "cryotherapy",
    ],
    "31654": ["radial ebus", "radial ultrasound", "rp-ebus", "r-ebus", "rebus", "miniprobe"],
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
        (r"(?i)\bebbx\b", "Text contains 'EBBx' (endobronchial biopsy abbreviation)."),
        (r"(?i)\blesions?\s+were\s+biopsied\b", "Text states 'lesions were biopsied' (likely endobronchial)."),
        (r"(?i)\bbiopsy\s+of\s+(?:the\s+)?(?:lesion|mass|polyp)\b", "Text describes biopsy of a lesion/mass/polyp."),
    ],
    # Fix for missed BAL
    "procedures_performed.bal.performed": [
        (r"(?i)\bbroncho[-\s]?alveolar\s+lavage\b", "Text contains 'bronchoalveolar lavage' but extraction missed it."),
        (r"(?i)\bbronchial\s+alveolar\s+lavage\b", "Text contains 'bronchial alveolar lavage' but extraction missed it."),
        (r"(?i)\bbal\b(?!\s*score)", "Text contains 'BAL' but extraction missed it."),
    ],
    # Fix for missed radial EBUS
    "procedures_performed.radial_ebus.performed": [
        (r"(?i)\bradial\s+ebus\b", "Text contains 'radial EBUS' but extraction missed it."),
        (r"(?i)\br-?ebus\b", "Text contains 'rEBUS' but extraction missed it."),
        (r"(?i)\brp-?ebus\b", "Text contains 'rp-EBUS' but extraction missed it."),
        (r"(?i)\bminiprobe\b", "Text contains 'miniprobe' (radial EBUS) but extraction missed it."),
    ],
    # Fix for missed cryotherapy / tumor destruction
    "procedures_performed.cryotherapy.performed": [
        (r"(?i)\bcryotherap(?:y|ies)\b", "Text mentions 'cryotherapy' but extraction missed it."),
        (r"(?i)\bcryo(?:therapy|ablation|debulk(?:ing)?)\b", "Text mentions cryotherapy/cryo debulking but extraction missed it."),
    ],
    # Fixes missed neck ultrasound (Report #3)
    "procedures_performed.neck_ultrasound.performed": [
        (r"(?i)\bneck\s+ultrasound\b", "Text contains 'neck ultrasound'."),
        (r"(?i)\bultrasound\s+of\s+(?:the\s+)?neck\b", "Text contains 'ultrasound of the neck'."),
    ],
    # Fix for missed brushings (Report #1 & #7)
    "procedures_performed.brushings.performed": [
        (r"(?i)\bbrush(?:ings?)?\b", "Text mentions 'brush' or 'brushings'."),
        (r"(?i)triple\s+needle", "Text mentions 'triple needle' (implies brushing/sampling)."),
    ],
    # Fix for missed conventional TBNA
    "procedures_performed.tbna_conventional.performed": [
        (r"(?i)\btbna\b", "Text contains 'TBNA' but extraction missed it."),
        (r"(?i)\btransbronchial\s+needle\s+aspiration\b", "Text contains 'transbronchial needle aspiration'."),
        (r"(?i)\btransbronchial\s+needle\b", "Text contains 'transbronchial needle'."),
    ],
    # Fix for missed navigational bronchoscopy
    "procedures_performed.navigational_bronchoscopy.performed": [
        (r"(?i)\bnavigational\s+bronchoscopy\b", "Text mentions navigational bronchoscopy."),
        (r"(?i)\belectromagnetic\s+navigation\b", "Text mentions electromagnetic navigation."),
        (r"(?i)\benb\b", "Text mentions ENB navigation."),
        (r"(?i)\bion\b", "Text mentions ION navigation."),
        (r"(?i)\bmonarch\b", "Text mentions Monarch navigation."),
        (r"(?i)\brobotic\s+bronchoscopy\b", "Text mentions robotic bronchoscopy."),
        (r"(?i)\bsuperdimension\b", "Text mentions SuperDimension navigation."),
    ],
    # Fix for missed transbronchial cryobiopsy
    "procedures_performed.transbronchial_cryobiopsy.performed": [
        (r"(?i)\btransbronchial\s+cryo\b", "Text mentions transbronchial cryo biopsy."),
        (r"(?i)\bcryo\s*biops(?:y|ies)\b", "Text mentions cryobiopsy."),
        (r"(?i)\bcryobiops(?:y|ies)\b", "Text mentions cryobiopsy."),
        (r"(?i)\btblc\b", "Text mentions TBLC."),
    ],
    # Fix for missed fiducial marker placement
    "granular_data.navigation_targets.fiducial_marker_placed": [
        (r"(?i)\bfiducial\s+marker\b", "Text mentions fiducial marker placement."),
        (r"(?i)\bfiducial\s+placement\b", "Text mentions fiducial placement."),
        (r"(?i)\bfiducials?\b[^.\n]{0,40}\bplaced\b", "Text mentions fiducials placed."),
    ],
    # Fix for missed peripheral ablation
    "procedures_performed.peripheral_ablation.performed": [
        (r"(?i)\bmicrowave\s+ablation\b", "Text mentions microwave ablation."),
        (r"(?i)\bmwa\b", "Text mentions MWA."),
        (r"(?i)\bradiofrequency\s+ablation\b", "Text mentions radiofrequency ablation."),
        (r"(?i)\brfa\b", "Text mentions RFA."),
        (r"(?i)\bcryoablation\b", "Text mentions cryoablation."),
        (r"(?i)\bcryo\s*ablation\b", "Text mentions cryo ablation."),
    ],
    # Fix for missed rigid bronchoscopy (Report #3)
    "procedures_performed.rigid_bronchoscopy.performed": [
        (r"(?i)rigid\s+bronchoscop", "Text mentions 'rigid bronchoscopy'."),
        (r"(?i)rigid\s+optic", "Text mentions 'rigid optic'."),
        (r"(?i)rigid\s+barrel", "Text mentions 'rigid barrel'."),
    ],
    # Fix for missed thermal/ablation keywords (Report #3)
    "procedures_performed.thermal_ablation.performed": [
        (r"(?i)electrocautery", "Text mentions 'electrocautery'."),
        (r"(?i)\blaser\b", "Text mentions 'laser'."),
        (r"(?i)\bapc\b", "Text mentions 'APC' (Argon Plasma Coagulation)."),
        (r"(?i)argon\s+plasma", "Text mentions 'Argon Plasma'."),
    ],
    # Pleural: chest tube / pleural drainage catheter placement
    "pleural_procedures.chest_tube.performed": [
        (r"(?i)\bpigtail\s+catheter\b", "Text mentions 'pigtail catheter' (pleural drain)."),
        (r"(?i)\bchest\s+tube\b", "Text mentions 'chest tube' but extraction missed it."),
        (r"(?i)\bpleurovac\b", "Text mentions 'Pleurovac' (drainage device)."),
        (r"(?i)\btube\s+thoracostomy\b", "Text mentions 'tube thoracostomy'."),
    ],
    # Diagnostic chest ultrasound (76604)
    "procedures_performed.chest_ultrasound.performed": [
        (r"(?i)\bchest\s+ultrasound\s+findings\b", "Text contains 'Chest ultrasound findings'."),
        (r"(?i)\bultrasound,\s*chest\b", "Text contains 'Ultrasound, chest'."),
        (r"\b76604\b", "Text lists CPT 76604 (chest ultrasound)."),
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
        def _walk(current: object | None, parts: list[str]) -> bool:
            if current is None:
                return False
            if not parts:
                return bool(current)

            part = parts[0]
            remaining = parts[1:]

            if isinstance(current, list):
                return any(_walk(item, parts) for item in current)

            if hasattr(current, part):
                return _walk(getattr(current, part), remaining)

            if isinstance(current, dict) and part in current:
                return _walk(current[part], remaining)

            return False

        return _walk(record, path.split("."))
    except Exception as exc:  # pragma: no cover
        logger.error("Error checking field population for %s: %s", path, exc)
        return False


def keyword_guard_passes(*, cpt: str, evidence_text: str) -> bool:
    """Return True if any configured keywords hit in evidence_text (case-insensitive)."""
    ok, _reason = keyword_guard_check(cpt=cpt, evidence_text=evidence_text)
    return ok


def keyword_guard_check(*, cpt: str, evidence_text: str) -> tuple[bool, str]:
    """Return (passes, reason) for keyword gating."""
    keywords = CPT_KEYWORDS.get(str(cpt), [])
    if not keywords:
        return False, "no keywords configured"

    text = (evidence_text or "").lower()
    if not text.strip():
        return False, "empty evidence text"

    for keyword in keywords:
        needle = (keyword or "").strip().lower()
        if not needle:
            continue
        if _keyword_hit(text, needle):
            return True, f"matched '{needle}'"
    return False, "no keyword hit"


def _keyword_hit(text_lower: str, needle_lower: str) -> bool:
    if " " in needle_lower or len(needle_lower) >= 5:
        return needle_lower in text_lower
    # Short token (e.g., "ipc", "bal", "tap"): require word boundary to reduce false positives.
    return re.search(rf"\b{re.escape(needle_lower)}\b", text_lower) is not None


__all__ = [
    "CPT_KEYWORDS",
    "REQUIRED_PATTERNS",
    "keyword_guard_check",
    "keyword_guard_passes",
    "scan_for_omissions",
]
