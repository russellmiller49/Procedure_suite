"""Guardrails for registry extraction self-correction (Phase 6).

Includes:
- CPT keyword gating (prevents self-correction when evidence text lacks keywords)
- Omission detection (detects high-value terms in raw text that were missed)
"""

from __future__ import annotations

import re

from modules.common.logger import get_logger
from modules.common.spans import Span
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
    "32551": ["chest tube", "tube thoracostomy", "thoracostomy"],
    # Pleural: percutaneous pleural drainage catheter (pigtail) without/with imaging
    "32556": ["pigtail catheter", "pleural drainage", "seldinger"],
    "32557": ["pigtail catheter", "pleural drainage", "ultrasound", "imaging guidance", "seldinger"],
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
        "ebus lymph nodes sampled",
        "lymph nodes sampled",
        "lymph node stations",
        "site 1",
        "site 2",
        "site 3",
        "site 4",
        "subcarinal",
        "11l",
        "11rs",
        "11ri",
        "4r",
        "4l",
        "10r",
        "10l",
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
    "31627": [
        "navigational bronchoscopy",
        "navigation",
        "electromagnetic navigation",
        "enb",
        "ion",
        "intuitive ion",
        "robotic bronchoscopy",
        "monarch",
        "galaxy",
        "planning station",
    ],
    "43238": [
        "eus-b",
        "eus b",
        "endoscopic ultrasound",
        "transesophageal",
        "transgastric",
        "left adrenal",
        "adrenal mass",
        "eusb",
    ],
    "76982": [
        "elastography",
        "elastrography",
        "type 1 elastographic",
        "type 2 elastographic",
        "stiff",
        "soft (green",
        "blue)",
    ],
    "76983": [
        "elastography",
        "elastrography",
        "additional target",
        "additional targets",
        "type 1 elastographic",
        "type 2 elastographic",
    ],
    "77012": [
        "cone beam ct",
        "cone-beam ct",
        "cios",
        "spin system",
        "ct guidance",
        "ct guided",
        "3d reconstruction",
    ],
    "76377": [
        "3d rendering",
        "3-d reconstruction",
        "3d reconstruction",
        "planning station",
        "ion planning station",
    ],
    # Therapeutics: dilation
    "31630": ["balloon", "dilation", "dilate", "dilated"],
    "31631": ["balloon", "dilation", "dilate", "dilated"],
    # Therapeutics: airway stent
    "31636": ["stent", "silicone", "metal", "metallic", "hybrid", "y-stent", "dumon", "ultraflex", "aero"],
    "31637": ["stent", "silicone", "metal", "metallic", "hybrid", "y-stent", "dumon", "ultraflex", "aero"],
    "31638": ["stent", "removal", "removed", "retrieved", "extracted", "forceps", "silicone", "metal", "metallic"],
    # Therapeutics: foreign body removal
    "31635": ["foreign body", "removed", "remove", "extracted", "retrieved", "forceps"],
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
        (
            r"(?is)\b(?:perform|create|place|insert)\w*\b.{0,20}\btracheostomy\b",
            "Text indicates tracheostomy creation but extraction missed it.",
        ),
        (
            r"(?is)\b(?:perform|create|place|insert)\w*\b.{0,20}\bperc(?:utaneous)?\s+trach\b",
            "Text indicates percutaneous trach creation but extraction missed it.",
        ),
        (
            r"(?is)\bpercutaneous\s+tracheostomy\b.{0,40}\b(?:perform|create|place|insert)\w*\b",
            "Text indicates percutaneous tracheostomy but extraction missed it.",
        ),
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
        (r"(?i)\bradial\s+probe\s+ebus\b", "Text contains 'radial probe EBUS' but extraction missed it."),
        (r"(?i)\bradial\s+probe\b", "Text contains 'radial probe' (radial EBUS) but extraction missed it."),
        (r"(?i)\br-?ebus\b", "Text contains 'rEBUS' but extraction missed it."),
        (r"(?i)\brp-?ebus\b", "Text contains 'rp-EBUS' but extraction missed it."),
        (r"(?i)\bminiprobe\b", "Text contains 'miniprobe' (radial EBUS) but extraction missed it."),
    ],
    # Fix for missed linear EBUS
    "procedures_performed.linear_ebus.performed": [
        (r"(?i)\b(?:linear|convex)\s+ebus\b", "Text contains 'linear/convex EBUS' but extraction missed it."),
        (r"(?i)\bebus[- ]?tbna\b", "Text contains 'EBUS-TBNA' but extraction missed linear EBUS."),
        (r"(?i)EBUS[- ]Findings", "Text contains 'EBUS Findings' but extraction missed linear EBUS."),
        (r"(?i)EBUS Lymph Nodes Sampled", "Text contains 'EBUS Lymph Nodes Sampled' but extraction missed linear EBUS."),
        (
            r"(?is)\b(?:ebus|endobronchial\s+ultrasound)\b.{0,200}\b(?:lymph\s+node(?:s)?|lymph\s+nodes\s+sampled|lymph\s+node\s+stations?)\b",
            "Text mentions EBUS lymph node sampling but extraction missed linear EBUS.",
        ),
        (
            r"(?is)\b(?:ebus|endobronchial\s+ultrasound)\b.{0,200}\b(?:station|level)\s*\d+[RL]?\b",
            "Text mentions EBUS station/level numbers but extraction missed linear EBUS.",
        ),
    ],
    # Fix for missed EUS-B
    "procedures_performed.eus_b.performed": [
        (r"(?i)\bEUS-?B\b", "Text contains 'EUS-B' but extraction missed EUS-B."),
        (r"(?i)\bleft adrenal\b", "Text contains left adrenal mass evaluation but extraction missed EUS-B."),
        (r"(?i)\btransgastric\b|\btransesophageal\b", "Text contains transgastric/transesophageal sampling but extraction missed EUS-B."),
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
    # Fix for missed peripheral TBNA (lung/peripheral targets).
    # NOTE: Generic "TBNA" also appears in EBUS sections; patterns here require
    # navigation/peripheral-lesion context to avoid forcing nodal TBNA flags.
    "procedures_performed.peripheral_tbna.performed": [
        (
            r"(?is)\b(?:ion|robotic|navigation|navigational|\benb\b|monarch|galaxy|superdimension|peripheral|target\s+lesion|lesion|nodule|(?:lung|pulmonary)\s+(?:lesion|nodule|mass))\b.{0,250}\b(?:tbna|transbronchial\s+needle\s+aspiration|transbronchial\s+needle)\b",
            "Text indicates peripheral/lung TBNA but extraction missed it.",
        ),
        (
            r"(?is)\b(?:tbna|transbronchial\s+needle\s+aspiration|transbronchial\s+needle)\b.{0,250}\b(?:ion|robotic|navigation|navigational|\benb\b|monarch|galaxy|superdimension|peripheral|target\s+lesion|lesion|nodule|(?:lung|pulmonary)\s+(?:lesion|nodule|mass))\b",
            "Text indicates peripheral/lung TBNA but extraction missed it.",
        ),
    ],
    # Fix for missed conventional (non-EBUS) nodal TBNA.
    "procedures_performed.tbna_conventional.performed": [
        (r"(?i)\bconventional\s+tbna\b", "Text explicitly states 'conventional TBNA' but extraction missed it."),
        (r"(?i)\bblind\s+tbna\b", "Text explicitly states 'blind TBNA' but extraction missed it."),
        (
            r"(?is)\b(?:station|ln|lymph\s+node)\b[^.\n]{0,80}\b(?:2R|2L|4R|4L|5|7|8|9|10R|10L|11R(?:S|I)?|11L(?:S|I)?|12R|12L)\b[^.\n]{0,120}\b(?:tbna|transbronchial\s+needle)\b",
            "Text indicates nodal TBNA at a lymph node station but extraction missed it.",
        ),
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
        (r"(?i)\btube\s+thoracostomy\b", "Text mentions 'tube thoracostomy'."),
    ],
    # Diagnostic chest ultrasound (76604)
    "procedures_performed.chest_ultrasound.performed": [
        (r"(?i)\bchest\s+ultrasound\s+findings\b", "Text contains 'Chest ultrasound findings'."),
        (r"(?i)\bultrasound,\s*chest\b", "Text contains 'Ultrasound, chest'."),
        (r"\b76604\b", "Text lists CPT 76604 (chest ultrasound)."),
    ],
}

_NEGATION_CUES = r"(?:no|not|without|declined|deferred|aborted)"

# Field-specific "do not treat as performed" cues.
#
# Example: "D/c chest tube" should not trigger a chest tube placement override.
_CHEST_TUBE_REMOVAL_CUES_RE = re.compile(
    r"(?i)(?:\bd/c\b|\bdc\b|\bdiscontinu(?:e|ed|ation)\b|\bremove(?:d|al)?\b|\bpull(?:ed)?\b|\bwithdrawn\b)"
)
_CHEST_TUBE_INSERTION_CUES_RE = re.compile(
    r"(?i)\b(?:place(?:d|ment)?|insert(?:ed|ion)?|tube\s+thoracostomy|thoracostomy|pigtail|seldinger)\b"
)
_TBNA_EBUS_CONTEXT_RE = re.compile(
    r"(?i)\b(?:ebus|endobronchial\s+ultrasound|convex\s+probe|ebus[-\s]?tbna)\b"
)
_EBUS_STATION_TOKEN_RE = re.compile(
    r"(?i)\b(?:2R|2L|4R|4L|7|10R|10L|11R(?:S|I)?|11L(?:S|I)?)\b"
)
_PERIPHERAL_TBNA_STRONG_CUES_RE = re.compile(
    r"(?i)\b(?:"
    r"ion|robotic|navigation|navigational|\benb\b|monarch|galaxy|superdimension|"
    r"peripheral|target\s+lesion|"
    r"(?:lung|pulmonary)\s+(?:lesion|nodule|mass)|"
    r"(?:lesion|nodule)\b"
    r")\b"
)


def _paragraph_window(note_text: str, start: int, end: int) -> str:
    lookback_start = max(0, start - 800)
    paragraph_break = note_text.rfind("\n\n", lookback_start, start)
    if paragraph_break != -1:
        lookback_start = paragraph_break + 2
    paragraph_end = note_text.find("\n\n", end)
    if paragraph_end == -1:
        paragraph_end = min(len(note_text), end + 800)
    return note_text[lookback_start:paragraph_end]


def _looks_like_ebus_nodal_tbna_only(note_text: str, match: re.Match[str]) -> bool:
    """Return True when the match sits in an EBUS nodal TBNA paragraph (not peripheral TBNA)."""
    if not note_text:
        return False
    window = _paragraph_window(note_text, match.start(), match.end())
    if not _TBNA_EBUS_CONTEXT_RE.search(window):
        return False
    if not (_EBUS_STATION_TOKEN_RE.search(window) or re.search(r"(?i)\bstation\(s\)?\b", window)):
        return False
    # If strong peripheral cues are present in the same paragraph, do not suppress:
    # peripheral TBNA can co-occur with EBUS (distinct site).
    if _PERIPHERAL_TBNA_STRONG_CUES_RE.search(window):
        return False
    return True


def _match_is_negated(note_text: str, match: re.Match[str], *, field_path: str | None = None) -> bool:
    """Return True when a keyword match is negated in local context."""
    if not note_text:
        return False

    start, end = match.start(), match.end()
    before = note_text[max(0, start - 120) : start]
    after = note_text[end : end + 120]

    if re.search(rf"(?i)\b{_NEGATION_CUES}\b[^.\n]{{0,60}}$", before):
        return True

    if re.search(rf"(?i)^[^.\n]{{0,60}}\b{_NEGATION_CUES}\b", after):
        return True

    if field_path == "procedures_performed.percutaneous_tracheostomy.performed":
        window = note_text[max(0, start - 80) : min(len(note_text), end + 80)]
        if re.search(r"(?i)\bexisting\s+tracheostomy\b", window):
            return True
        if re.search(r"(?i)\b(?:through|via)\s+tracheostomy\b", window):
            return True
        if re.search(r"(?i)\btracheostomy\s+tube\b", window):
            return True

    if field_path == "pleural_procedures.chest_tube.performed":
        window = note_text[max(0, start - 30) : min(len(note_text), end + 30)]
        if _CHEST_TUBE_REMOVAL_CUES_RE.search(window) and not _CHEST_TUBE_INSERTION_CUES_RE.search(window):
            return True

    if field_path == "procedures_performed.tbna_conventional.performed":
        # TBNA language inside an EBUS paragraph should not trigger conventional TBNA.
        lookback_start = max(0, start - 800)
        paragraph_break = note_text.rfind("\n\n", lookback_start, start)
        if paragraph_break != -1:
            lookback_start = paragraph_break + 2
        paragraph_end = note_text.find("\n\n", end)
        if paragraph_end == -1:
            paragraph_end = min(len(note_text), end + 800)
        window = note_text[lookback_start:paragraph_end]
        if _TBNA_EBUS_CONTEXT_RE.search(window):
            return True

    return False


def scan_for_omissions(note_text: str, record: RegistryRecord) -> list[str]:
    """Scan raw text for required patterns missing from the extracted record.

    Returns warning strings suitable for surfacing in API responses and for
    triggering manual review or a retry/self-correction loop.
    """
    warnings: list[str] = []

    for field_path, rules in REQUIRED_PATTERNS.items():
        # TBNA is satisfied by either peripheral TBNA or EBUS-TBNA sampling; do not
        # emit a conventional TBNA omission when those are present.
        if field_path == "procedures_performed.tbna_conventional.performed":
            if _is_field_populated(record, "procedures_performed.peripheral_tbna.performed"):
                continue
            if _is_field_populated(record, "procedures_performed.linear_ebus.node_events") or _is_field_populated(
                record, "procedures_performed.linear_ebus.stations_sampled"
            ):
                continue
        if _is_field_populated(record, field_path):
            continue

        for pattern, msg in rules:
            match = re.search(pattern, note_text or "")
            if match and not _match_is_negated(note_text or "", match, field_path=field_path):
                if field_path == "procedures_performed.peripheral_tbna.performed":
                    if _looks_like_ebus_nodal_tbna_only(note_text or "", match):
                        continue
                warning = f"SILENT_FAILURE: {msg} (Pattern: '{pattern}')"
                warnings.append(warning)
                logger.warning(warning, extra={"field": field_path, "pattern": pattern})
                break

    return warnings


def apply_required_overrides(note_text: str, record: RegistryRecord) -> tuple[RegistryRecord, list[str]]:
    """Force required procedure flags when high-signal patterns appear."""
    if record is None:
        return RegistryRecord(), []

    warnings: list[str] = []
    record_data = record.model_dump()
    evidence = record_data.get("evidence") or {}
    if not isinstance(evidence, dict):
        evidence = {}

    updated = False
    for field_path, rules in REQUIRED_PATTERNS.items():
        # Never force conventional nodal TBNA when peripheral TBNA or EBUS-TBNA
        # sampling is already present (prevents phantom tbna_conventional alongside EBUS).
        if field_path == "procedures_performed.tbna_conventional.performed":
            if _is_field_populated(record, "procedures_performed.peripheral_tbna.performed"):
                continue
            if _is_field_populated(record, "procedures_performed.linear_ebus.node_events") or _is_field_populated(
                record, "procedures_performed.linear_ebus.stations_sampled"
            ):
                continue
        if _is_field_populated(record, field_path):
            continue

        for pattern, msg in rules:
            match = re.search(pattern, note_text or "")
            if not match:
                continue
            if _match_is_negated(note_text or "", match, field_path=field_path):
                continue
            if field_path == "procedures_performed.peripheral_tbna.performed":
                if _looks_like_ebus_nodal_tbna_only(note_text or "", match):
                    continue

            if field_path.startswith("granular_data.navigation_targets"):
                granular = record_data.get("granular_data")
                if granular is None or not isinstance(granular, dict):
                    granular = {}

                targets_raw = granular.get("navigation_targets")
                if isinstance(targets_raw, list):
                    targets = [t for t in targets_raw if isinstance(t, dict)]
                else:
                    targets = []

                if not targets:
                    targets = [
                        {
                            "target_number": 1,
                            "target_location_text": "Unknown target",
                            "fiducial_marker_placed": True,
                        }
                    ]
                else:
                    latest = dict(targets[-1])
                    if latest.get("fiducial_marker_placed") is not True:
                        latest["fiducial_marker_placed"] = True
                    targets[-1] = latest

                granular["navigation_targets"] = targets
                record_data["granular_data"] = granular
                evidence.setdefault(field_path, []).append(
                    Span(
                        text=match.group(0).strip(),
                        start=match.start(),
                        end=match.end(),
                    )
                )
                warnings.append(f"HARD_OVERRIDE: {msg} -> {field_path}=true")
                updated = True
                break

            _set_nested_field(record_data, field_path, True)
            evidence.setdefault(field_path, []).append(
                Span(
                    text=match.group(0).strip(),
                    start=match.start(),
                    end=match.end(),
                )
            )
            warnings.append(f"HARD_OVERRIDE: {msg} -> {field_path}=true")
            updated = True
            break

    if updated:
        record_data["evidence"] = evidence
        record = RegistryRecord(**record_data)

    return record, warnings


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


def _set_nested_field(data: dict, path: str, value: object) -> None:
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current or not isinstance(current.get(part), dict):
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value


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
    "apply_required_overrides",
    "keyword_guard_check",
    "keyword_guard_passes",
    "scan_for_omissions",
]
