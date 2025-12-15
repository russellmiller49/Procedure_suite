"""Deterministic CPT code derivation from registry flags + text analysis.

This module implements the extraction-first architecture:
    Text -> ML Model -> Registry Flags -> Deterministic Rules -> CPT Codes

Key insight: The ML model predicts binary flags (linear_ebus=True), but CPT codes
often require counts (stations >= 3). We use a hybrid approach:
- ML model: Detects WHAT procedures happened (boolean flags)
- Regex: Extracts HOW MANY (station counts, biopsy sites, etc.)

Usage:
    from data.rules.coding_rules import derive_all_codes

    registry = {"linear_ebus": True, "transbronchial_biopsy": True, ...}
    note_text = "EBUS-TBNA of stations 4R, 7, and 11L..."

    codes = derive_all_codes(registry, note_text)
    # Returns: ["31653", "31628", ...]
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

# ============================================================================
# Regex Helpers for Count Extraction
# ============================================================================

# EBUS station patterns
STATION_PATTERNS = [
    # Explicit station mentions: "station 7", "station 4R"
    r"\bstation\s+(\d+[RLrl]?)\b",
    # Numbered with laterality: "4R", "11L", "7" (standalone)
    r"\b(\d{1,2}[RLrl])\b",
    # Subcarinal: "7", "subcarinal", "level 7"
    r"\b(subcarinal|level\s*7)\b",
    # Paratracheal: "2R", "2L", "4R", "4L"
    r"\b([24][RLrl])\b",
    # Hilar: "10R", "10L", "11R", "11L"
    r"\b(1[01][RLrl])\b",
    # Station 7 alone (common)
    r"\bstation\s+(7)\b",
]

# Lobe patterns for biopsy counting
LOBE_PATTERNS = [
    r"\b(right\s+upper\s+lobe|RUL)\b",
    r"\b(right\s+middle\s+lobe|RML)\b",
    r"\b(right\s+lower\s+lobe|RLL)\b",
    r"\b(left\s+upper\s+lobe|LUL)\b",
    r"\b(lingula)\b",
    r"\b(left\s+lower\s+lobe|LLL)\b",
]

# Bronchial segment patterns
SEGMENT_PATTERNS = [
    r"\b(apical|posterior|anterior|lateral|medial|superior|inferior)\s+(segment|bronchus)\b",
    r"\b(B[1-9]|B10)\b",  # Bronchial segment nomenclature
]


def get_ebus_station_count(text: str) -> int:
    """Count unique EBUS stations mentioned in text.

    Looks for patterns like:
    - "station 7", "station 4R"
    - "4R", "11L" (standalone)
    - "subcarinal"

    Args:
        text: Clinical procedure note text

    Returns:
        Number of unique stations mentioned
    """
    text_lower = text.lower()
    stations = set()

    # Normalize station mentions
    for pattern in STATION_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            # Normalize: "4r" -> "4R", "subcarinal" -> "7"
            if isinstance(match, tuple):
                match = match[0]
            match = match.upper().strip()

            # Map subcarinal to station 7
            if "SUBCARINAL" in match or "LEVEL 7" in match.upper():
                stations.add("7")
            else:
                # Extract just the number+laterality
                num_match = re.search(r"(\d+[RL]?)", match)
                if num_match:
                    stations.add(num_match.group(1))

    return len(stations)


def get_biopsy_lobe_count(text: str) -> int:
    """Count distinct lobes where biopsies were taken.

    Args:
        text: Clinical procedure note text

    Returns:
        Number of unique lobes mentioned with biopsy
    """
    text_lower = text.lower()
    lobes = set()

    # Look for lobe mentions near "biopsy" keywords
    biopsy_context = re.findall(
        r".{0,100}(biops[yied]+|tbbx|tblb|transbronchial).{0,100}",
        text_lower,
        re.IGNORECASE,
    )

    for context in biopsy_context:
        for pattern in LOBE_PATTERNS:
            matches = re.findall(pattern, context, re.IGNORECASE)
            lobes.update(m.upper() if isinstance(m, str) else m[0].upper() for m in matches)

    # Also check for explicit multi-lobe mentions
    if re.search(r"\b(multiple|several|both)\s+lobes?\b", text_lower):
        # At least 2 if "multiple lobes" mentioned
        return max(len(lobes), 2)

    return len(lobes)


def get_stent_count(text: str) -> int:
    """Count stents placed.

    Args:
        text: Clinical procedure note text

    Returns:
        Number of stents placed
    """
    text_lower = text.lower()

    # Look for explicit stent counts
    count_patterns = [
        r"(\d+)\s*(?:x\s*)?stents?\s+(?:placed|deployed|inserted)",
        r"(?:placed|deployed|inserted)\s*(\d+)\s*stents?",
        r"(\d+)\s*(?:silicone|metal|hybrid)\s+stents?",
    ]

    for pattern in count_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))

    # Check for single stent mentions
    if re.search(r"\bstent\s+(?:placed|deployed|inserted)\b", text_lower):
        return 1

    # Check for "a stent" or "one stent"
    if re.search(r"\b(?:a|one|single)\s+stent\b", text_lower):
        return 1

    return 0


def has_navigation_evidence(text: str) -> bool:
    """Check for navigation platform evidence in text.

    Args:
        text: Clinical procedure note text

    Returns:
        True if navigation platform mentioned
    """
    text_lower = text.lower()

    platforms = [
        r"\b(superDimension|superd)\b",
        r"\b(iLogic|illogic)\b",
        r"\b(Ion|Intuitive)\b",
        r"\b(Monarch)\b",
        r"\b(Galaxy)\b",
        r"\b(Veran|SPiN)\b",
        r"\b(electromagnetic\s+navigation|EMN)\b",
        r"\b(robotic\s+bronchoscopy)\b",
        r"\b(shape\s*-?\s*sensing)\b",
    ]

    for pattern in platforms:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True

    return False


def has_bal_evidence(text: str) -> bool:
    """Check for bronchoalveolar lavage evidence.

    Args:
        text: Clinical procedure note text

    Returns:
        True if BAL performed
    """
    text_lower = text.lower()

    bal_patterns = [
        r"\bbal\b",
        r"\bbronchoalveolar\s+lavage\b",
        r"\blavage\s+(?:performed|obtained|sent)\b",
        r"\blavage\s+fluid\b",
    ]

    for pattern in bal_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def has_aspiration_evidence(text: str) -> bool:
    """Check for therapeutic aspiration evidence.

    Args:
        text: Clinical procedure note text

    Returns:
        True if therapeutic aspiration performed
    """
    text_lower = text.lower()

    aspiration_patterns = [
        r"\b(therapeutic|large\s+volume)\s+aspiration\b",
        r"\b(aspirat(?:ed|ion))\s+\d+\s*(?:cc|ml|mL)\b",
        r"\b(mucus|blood|clot)\s+(?:plugs?|removal|aspirat)\b",
        r"\bsuctioned?\s+(?:out|blood|mucus|clot)\b",
    ]

    for pattern in aspiration_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


# ============================================================================
# CPT Derivation Rules
# ============================================================================

def rule_31622(registry: dict, note_text: str) -> bool:
    """Diagnostic bronchoscopy (with or without cell washing).

    Only billable when NO other bronchoscopic procedure is performed.
    Bundled into any interventional procedure.

    Args:
        registry: Registry boolean flags from ML prediction
        note_text: Original procedure note text

    Returns:
        True if 31622 should be coded
    """
    # 31622 is diagnostic only - bundled into any interventional
    if not registry.get("diagnostic_bronchoscopy"):
        return False

    # Check if any interventional procedure was done
    interventional_flags = [
        "transbronchial_biopsy",
        "transbronchial_cryobiopsy",
        "endobronchial_biopsy",
        "linear_ebus",
        "radial_ebus",
        "navigational_bronchoscopy",
        "therapeutic_aspiration",
        "foreign_body_removal",
        "airway_dilation",
        "airway_stent",
        "thermal_ablation",
        "cryotherapy",
        "blvr",
        "bronchial_thermoplasty",
    ]

    for flag in interventional_flags:
        if registry.get(flag):
            return False  # Bundled into interventional

    return True


def rule_31624(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with bronchoalveolar lavage (BAL).

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31624 should be coded
    """
    if registry.get("bal"):
        return True

    # Double-check with text evidence
    return has_bal_evidence(note_text)


def rule_31625(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with transbronchial lung biopsy (single lobe).

    Use 31628 for transbronchial biopsy.
    31625 is the older code - prefer 31628.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31625 should be coded
    """
    # Prefer 31628 over 31625 for TBLB
    return False


def rule_31627(registry: dict, note_text: str) -> bool:
    """Computer-assisted, image-guided navigation (add-on).

    This is an add-on code - requires a primary bronchoscopy procedure.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31627 should be coded
    """
    if not registry.get("navigational_bronchoscopy"):
        return False

    # Verify navigation platform evidence in text
    return has_navigation_evidence(note_text)


def rule_31628(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with transbronchial lung biopsy, single lobe.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31628 should be coded
    """
    return registry.get("transbronchial_biopsy", False)


def rule_31629(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with conventional TBNA (non-EBUS).

    Should NOT be used when linear EBUS is performed.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31629 should be coded
    """
    if registry.get("tbna_conventional"):
        # But NOT if linear EBUS was done (use 31652/31653 instead)
        if registry.get("linear_ebus"):
            return False
        return True
    return False


def rule_31632(registry: dict, note_text: str) -> bool:
    """Additional transbronchial lung biopsy, each additional lobe (add-on).

    Use when biopsies taken from more than one lobe.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31632 should be coded
    """
    if not registry.get("transbronchial_biopsy"):
        return False

    # Check if multiple lobes were biopsied
    lobe_count = get_biopsy_lobe_count(note_text)
    return lobe_count >= 2


def rule_31641(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with destruction of tumor or relief of stenosis.

    Includes thermal ablation, cryotherapy, mechanical debulking.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31641 should be coded
    """
    return registry.get("thermal_ablation", False) or registry.get("cryotherapy", False)


def rule_31645(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with therapeutic aspiration, initial.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31645 should be coded
    """
    if registry.get("therapeutic_aspiration"):
        return True

    # Double-check with text evidence
    return has_aspiration_evidence(note_text)


def rule_31652(registry: dict, note_text: str) -> bool:
    """EBUS-TBNA, 1-2 lymph node stations sampled.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31652 should be coded
    """
    if not registry.get("linear_ebus"):
        return False

    station_count = get_ebus_station_count(note_text)
    return 1 <= station_count <= 2


def rule_31653(registry: dict, note_text: str) -> bool:
    """EBUS-TBNA, 3 or more lymph node stations sampled.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31653 should be coded
    """
    if not registry.get("linear_ebus"):
        return False

    station_count = get_ebus_station_count(note_text)
    return station_count >= 3


def rule_31654(registry: dict, note_text: str) -> bool:
    """Radial EBUS used during bronchoscopy (add-on).

    This is an add-on code.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31654 should be coded
    """
    return registry.get("radial_ebus", False)


def rule_31631(registry: dict, note_text: str) -> bool:
    """Tracheal stent placement.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31631 should be coded
    """
    if not registry.get("airway_stent"):
        return False

    # Check for tracheal location
    text_lower = note_text.lower()
    return bool(re.search(r"\b(trachea|tracheal)\b", text_lower))


def rule_31636(registry: dict, note_text: str) -> bool:
    """Bronchial stent placement.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31636 should be coded
    """
    if not registry.get("airway_stent"):
        return False

    # Check for bronchial location (not tracheal)
    text_lower = note_text.lower()
    has_bronchial = bool(re.search(r"\b(bronch|mainstem|lobar)\b", text_lower))
    has_tracheal = bool(re.search(r"\b(trachea|tracheal)\b", text_lower))

    return has_bronchial and not has_tracheal


def rule_31637(registry: dict, note_text: str) -> bool:
    """Each additional bronchial stent (add-on to 31636).

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31637 should be coded
    """
    if not registry.get("airway_stent"):
        return False

    stent_count = get_stent_count(note_text)
    return stent_count >= 2


def rule_31647(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with balloon occlusion for valve placement (BLVR).

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31647 should be coded
    """
    return registry.get("blvr", False)


def rule_31660(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with bronchial thermoplasty.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31660 should be coded
    """
    return registry.get("bronchial_thermoplasty", False)


def rule_31635(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with balloon dilation.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31635 should be coded
    """
    return registry.get("airway_dilation", False)


def rule_32550(registry: dict, note_text: str) -> bool:
    """Insertion of indwelling tunneled pleural catheter (IPC).

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 32550 should be coded
    """
    return registry.get("ipc", False)


def rule_32554(registry: dict, note_text: str) -> bool:
    """Thoracentesis, aspiration of pleural space, without imaging guidance.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 32554 should be coded
    """
    if registry.get("thoracentesis"):
        # Check if imaging guidance was used
        text_lower = note_text.lower()
        has_imaging = bool(
            re.search(r"\b(ultrasound|us|ct|fluoroscop)\s*guid", text_lower)
        )
        return not has_imaging
    return False


def rule_32555(registry: dict, note_text: str) -> bool:
    """Thoracentesis, aspiration of pleural space, with imaging guidance.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 32555 should be coded
    """
    if registry.get("thoracentesis"):
        text_lower = note_text.lower()
        has_imaging = bool(
            re.search(r"\b(ultrasound|us|ct|fluoroscop)\s*guid", text_lower)
        )
        return has_imaging
    return False


def rule_32556(registry: dict, note_text: str) -> bool:
    """Chest tube insertion, percutaneous.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 32556 should be coded
    """
    return registry.get("chest_tube", False)


def rule_32601(registry: dict, note_text: str) -> bool:
    """Thoracoscopy, diagnostic (medical thoracoscopy).

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 32601 should be coded
    """
    return registry.get("medical_thoracoscopy", False)


def rule_32560(registry: dict, note_text: str) -> bool:
    """Pleurodesis, chemical (includes thoracentesis).

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 32560 should be coded
    """
    return registry.get("pleurodesis", False)


def rule_32561(registry: dict, note_text: str) -> bool:
    """Instillation of fibrinolytic agent.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 32561 should be coded
    """
    return registry.get("fibrinolytic_therapy", False)


def rule_31640(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with excision of tumor.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31640 should be coded
    """
    # This is typically mechanical debulking without ablation
    # If ablation was used, 31641 is preferred
    if registry.get("thermal_ablation") or registry.get("cryotherapy"):
        return False

    # Check for mechanical debulking keywords
    text_lower = note_text.lower()
    return bool(re.search(r"\b(debulk|excis|resect)\s*(tumor|mass|lesion)\b", text_lower))


def rule_31623(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with brushing.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31623 should be coded
    """
    return registry.get("brushings", False)


def rule_31625_endobronchial(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with endobronchial biopsy.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if endobronchial biopsy code should be added
    """
    return registry.get("endobronchial_biopsy", False)


def rule_31633(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with transbronchial cryobiopsy.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31633 should be coded
    """
    return registry.get("transbronchial_cryobiopsy", False)


def rule_31634(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with balloon occlusion.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31634 should be coded
    """
    # Check for balloon occlusion in non-BLVR context
    if registry.get("blvr"):
        return False  # Use 31647 for BLVR

    text_lower = note_text.lower()
    return bool(re.search(r"\bballoon\s+occlusion\b", text_lower))


def rule_31638(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with revision/removal of stent.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31638 should be coded
    """
    text_lower = note_text.lower()
    return bool(re.search(r"\bstent\s+(remov|revis|replac|exchang)\b", text_lower))


def rule_31643(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with foreign body removal.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31643 should be coded
    """
    return registry.get("foreign_body_removal", False)


def rule_31661(registry: dict, note_text: str) -> bool:
    """Bronchoscopy with bronchial thermoplasty, 2 or more lobes.

    Args:
        registry: Registry boolean flags
        note_text: Original procedure note text

    Returns:
        True if 31661 should be coded
    """
    if not registry.get("bronchial_thermoplasty"):
        return False

    # Count lobes treated
    text_lower = note_text.lower()

    # Look for multi-lobe mentions
    lobe_count = 0
    for pattern in LOBE_PATTERNS:
        if re.search(pattern, text_lower):
            lobe_count += 1

    return lobe_count >= 2


# ============================================================================
# Rule Registry and Main Derivation Function
# ============================================================================

# Map CPT codes to their rule functions
CPT_RULES: dict[str, Callable[[dict, str], bool]] = {
    "31622": rule_31622,
    "31623": rule_31623,
    "31624": rule_31624,
    "31627": rule_31627,
    "31628": rule_31628,
    "31629": rule_31629,
    "31632": rule_31632,
    "31633": rule_31633,
    "31634": rule_31634,
    "31635": rule_31635,
    "31638": rule_31638,
    "31640": rule_31640,
    "31641": rule_31641,
    "31643": rule_31643,
    "31645": rule_31645,
    "31647": rule_31647,
    "31652": rule_31652,
    "31653": rule_31653,
    "31654": rule_31654,
    "31660": rule_31660,
    "31661": rule_31661,
    "31631": rule_31631,
    "31636": rule_31636,
    "31637": rule_31637,
    "32550": rule_32550,
    "32554": rule_32554,
    "32555": rule_32555,
    "32556": rule_32556,
    "32560": rule_32560,
    "32561": rule_32561,
    "32601": rule_32601,
}

# Add-on codes that require a primary procedure
ADDON_CODES = {
    "31627",  # Navigation (add-on)
    "31632",  # Additional lobe TBLB (add-on)
    "31637",  # Additional bronchial stent (add-on)
    "31654",  # Radial EBUS (add-on)
}

# Primary bronchoscopy codes
PRIMARY_BRONCH_CODES = {
    "31622", "31623", "31624", "31628", "31629", "31633",
    "31635", "31640", "31641", "31645", "31647", "31652",
    "31653", "31660", "31661", "31631", "31636", "31643",
}

# Mutually exclusive code groups
MUTUALLY_EXCLUSIVE = [
    {"31652", "31653"},  # EBUS 1-2 stations vs 3+ stations
    {"31631", "31636"},  # Tracheal vs bronchial stent (usually)
    {"31660", "31661"},  # Thermoplasty single vs multi-lobe
    {"32554", "32555"},  # Thoracentesis without vs with imaging
]


def derive_all_codes_from_registry_and_text(registry: dict, note_text: str) -> list[str]:
    """Derive CPT codes from registry flags and note text.

    This is the main entry point for deterministic CPT derivation.
    Uses ML-predicted registry flags + regex-based count extraction.

    Args:
        registry: Dict of boolean registry flags from ML prediction
        note_text: Original clinical procedure note text

    Returns:
        List of applicable CPT codes
    """
    derived_codes = []

    # Apply all rules
    for code, rule_fn in CPT_RULES.items():
        try:
            if rule_fn(registry, note_text):
                derived_codes.append(code)
        except Exception:
            # Log but don't fail on individual rule errors
            continue

    # Handle mutual exclusions (prefer more specific code)
    for exclusive_group in MUTUALLY_EXCLUSIVE:
        present = exclusive_group.intersection(derived_codes)
        if len(present) > 1:
            # For EBUS, prefer 31653 (3+ stations) if both present
            if "31653" in present:
                derived_codes = [c for c in derived_codes if c != "31652"]
            # For thoracentesis, prefer imaging-guided if both present
            elif "32555" in present:
                derived_codes = [c for c in derived_codes if c != "32554"]
            # For thermoplasty, prefer multi-lobe if both present
            elif "31661" in present:
                derived_codes = [c for c in derived_codes if c != "31660"]

    # Validate add-on codes have primary procedure
    has_primary_bronch = any(c in PRIMARY_BRONCH_CODES for c in derived_codes)
    if not has_primary_bronch:
        derived_codes = [c for c in derived_codes if c not in ADDON_CODES]

    # Sort for consistent output
    return sorted(derived_codes)


def get_code_audit(registry: dict, note_text: str, codes: list[str]) -> dict:
    """Generate audit trail explaining why each code was/wasn't derived.

    Args:
        registry: Dict of boolean registry flags
        note_text: Original procedure note text
        codes: List of derived CPT codes

    Returns:
        Dict with audit information for each code
    """
    audit = {}

    for code, rule_fn in CPT_RULES.items():
        try:
            result = rule_fn(registry, note_text)
            included = code in codes

            # Build explanation
            if code in {"31652", "31653"}:
                station_count = get_ebus_station_count(note_text)
                explanation = f"linear_ebus={registry.get('linear_ebus')}, stations={station_count}"
            elif code == "31627":
                nav_evidence = has_navigation_evidence(note_text)
                explanation = f"navigational_bronchoscopy={registry.get('navigational_bronchoscopy')}, platform_found={nav_evidence}"
            elif code == "31632":
                lobe_count = get_biopsy_lobe_count(note_text)
                explanation = f"transbronchial_biopsy={registry.get('transbronchial_biopsy')}, lobes={lobe_count}"
            else:
                # Generic explanation
                relevant_flags = [
                    f"{k}={v}" for k, v in registry.items()
                    if v and k in rule_fn.__doc__.lower() if rule_fn.__doc__
                ]
                explanation = ", ".join(relevant_flags) if relevant_flags else "See rule logic"

            audit[code] = {
                "rule_result": result,
                "included": included,
                "explanation": explanation,
            }

        except Exception as e:
            audit[code] = {
                "rule_result": False,
                "included": False,
                "explanation": f"Error: {e}",
            }

    return audit


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_against_golden(
    golden_records: list[dict],
    verbose: bool = False,
) -> dict:
    """Validate rules engine against golden extraction records.

    Args:
        golden_records: List of records with 'note_text', 'registry_entry', 'cpt_codes'
        verbose: Print details for mismatches

    Returns:
        Dict with accuracy metrics and mismatches
    """
    correct = 0
    total = 0
    mismatches = []

    for record in golden_records:
        note_text = record.get("note_text", "")
        registry = record.get("registry_entry", {})
        expected_codes = set(str(c) for c in record.get("cpt_codes", []))

        derived = set(derive_all_codes_from_registry_and_text(registry, note_text))

        if derived == expected_codes:
            correct += 1
        else:
            mismatches.append({
                "note_id": record.get("note_id", "unknown"),
                "expected": sorted(expected_codes),
                "derived": sorted(derived),
                "missing": sorted(expected_codes - derived),
                "extra": sorted(derived - expected_codes),
            })

            if verbose:
                print(f"\nMismatch: {record.get('note_id', 'unknown')}")
                print(f"  Expected: {sorted(expected_codes)}")
                print(f"  Derived:  {sorted(derived)}")
                print(f"  Missing:  {sorted(expected_codes - derived)}")
                print(f"  Extra:    {sorted(derived - expected_codes)}")

        total += 1

    accuracy = correct / total if total > 0 else 0.0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "mismatches": mismatches,
    }


__all__ = [
    "derive_all_codes",
    "derive_all_codes_from_registry_and_text",
    "get_code_audit",
    "validate_against_golden",
    "get_ebus_station_count",
    "get_biopsy_lobe_count",
    "CPT_RULES",
]


# -----------------------------------------------------------------------------
# RegistryRecord-only deterministic CPT rules shim
# -----------------------------------------------------------------------------

from modules.coder.domain_rules.registry_to_cpt.coding_rules import (
    derive_all_codes as derive_all_codes,  # noqa: F401
)
