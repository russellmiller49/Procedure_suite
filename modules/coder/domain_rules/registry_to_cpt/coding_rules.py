"""Deterministic CPT code derivation from RegistryRecord only.

This module is used by the extraction-first pipeline:
  note_text -> RegistryRecord extraction -> deterministic RegistryRecord → CPT

Non-negotiable constraint:
Rules here must accept ONLY RegistryRecord and must not parse raw note text.
"""

from __future__ import annotations

from typing import Any

from modules.registry.schema import RegistryRecord


def _performed(obj: Any) -> bool:
    if obj is None:
        return False
    performed = getattr(obj, "performed", None)
    return performed is True


def _proc(record: RegistryRecord, name: str) -> Any:
    procedures = getattr(record, "procedures_performed", None)
    if procedures is None:
        return None
    return getattr(procedures, name, None)


def _pleural(record: RegistryRecord, name: str) -> Any:
    pleural = getattr(record, "pleural_procedures", None)
    if pleural is None:
        return None
    return getattr(pleural, name, None)


def _stations_sampled(record: RegistryRecord) -> tuple[list[str], str]:
    linear = _proc(record, "linear_ebus")
    if linear is None:
        return ([], "none")

    qualifying_actions = {"needle_aspiration", "core_biopsy", "forceps_biopsy"}
    node_events = getattr(linear, "node_events", None)
    if isinstance(node_events, (list, tuple)) and node_events:
        sampled: list[str] = []
        for event in node_events:
            action = getattr(event, "action", None)
            if action not in qualifying_actions:
                continue
            station = getattr(event, "station", None)
            if station is None:
                continue
            station_clean = str(station).upper().strip()
            if station_clean:
                sampled.append(station_clean)
        return (sampled, "node_events")

    stations = getattr(linear, "stations_sampled", None)
    if not stations:
        return ([], "none")

    return ([str(s).upper().strip() for s in stations if s], "stations_sampled")


def _navigation_targets(record: RegistryRecord) -> list[Any]:
    granular = getattr(record, "granular_data", None)
    targets = getattr(granular, "navigation_targets", None) if granular is not None else None
    if not targets:
        return []
    return list(targets)


def _fiducial_marker_placed(record: RegistryRecord) -> bool:
    # Check explicit fiducial_placement procedure first
    fiducial_proc = _proc(record, "fiducial_placement")
    if _performed(fiducial_proc):
        return True

    # Check granular navigation targets (fallback)
    for target in _navigation_targets(record):
        placed = getattr(target, "fiducial_marker_placed", None)
        details = getattr(target, "fiducial_marker_details", None)
        if placed is True:
            return True
        if details is not None and str(details).strip():
            return True
    return False


def _stent_action_is_removal(action: Any) -> bool:
    if action is None:
        return False
    text = str(action).strip().lower()
    return bool(text) and ("remov" in text or "retriev" in text or "explant" in text or "extract" in text)


def _stent_action_is_placement(action: Any) -> bool:
    if action is None:
        return False
    text = str(action).strip().lower()
    return bool(text) and ("placement" in text or "revision" in text or "reposition" in text)


def _lobe_tokens(values: list[str]) -> set[str]:
    lobes: set[str] = set()
    for value in values:
        upper = value.upper()
        for token in ("RUL", "RML", "RLL", "LUL", "LLL", "LINGULA"):
            if token in upper:
                lobes.add("Lingula" if token == "LINGULA" else token)
    return lobes


def _dilation_in_distinct_lobe_from_destruction(record: RegistryRecord) -> bool:
    """Check if dilation was performed in a different lobe than destruction.

    Returns True only if granular data proves distinct anatomic locations.
    If granular data is missing, returns False (assume bundled).
    """
    granular = getattr(record, "granular_data", None)
    if not granular:
        return False

    # Get lobes for dilation
    dilation_lobes: set[str] = set()
    dilation_targets = getattr(granular, "dilation_targets", None) or []
    for target in dilation_targets:
        lobe = getattr(target, "lobe", None)
        if lobe:
            dilation_lobes.add(str(lobe).upper())

    # Get lobes for destruction/ablation
    destruction_lobes: set[str] = set()
    ablation_targets = getattr(granular, "ablation_targets", None) or []
    for target in ablation_targets:
        lobe = getattr(target, "lobe", None)
        if lobe:
            destruction_lobes.add(str(lobe).upper())

    # If no granular data for either, assume bundled
    if not dilation_lobes or not destruction_lobes:
        return False

    # Check for distinct lobes (dilation in lobe not used for destruction)
    return bool(dilation_lobes - destruction_lobes)


def derive_all_codes_with_meta(
    record: RegistryRecord,
) -> tuple[list[str], dict[str, str], list[str]]:
    """Return (codes, rationales, warnings)."""
    codes: list[str] = []
    rationales: dict[str, str] = {}
    warnings: list[str] = []

    # --- Bronchoscopy family ---
    diagnostic = _proc(record, "diagnostic_bronchoscopy")
    if _performed(diagnostic):
        interventional_names = [
            "bal",
            "brushings",
            "endobronchial_biopsy",
            "tbna_conventional",
            "linear_ebus",
            "radial_ebus",
            "navigational_bronchoscopy",
            "transbronchial_biopsy",
            "transbronchial_cryobiopsy",
            "therapeutic_aspiration",
            "foreign_body_removal",
            "airway_dilation",
            "airway_stent",
            "thermal_ablation",
            "cryotherapy",
            "blvr",
            "bronchial_thermoplasty",
            "whole_lung_lavage",
            "rigid_bronchoscopy",
        ]
        if any(_performed(_proc(record, name)) for name in interventional_names):
            warnings.append("Diagnostic bronchoscopy present but bundled into another bronchoscopic procedure")
        else:
            codes.append("31622")
            rationales["31622"] = "diagnostic_bronchoscopy.performed=true and no interventional bronchoscopy procedures"

    if _performed(_proc(record, "brushings")):
        codes.append("31623")
        rationales["31623"] = "brushings.performed=true"

    if _performed(_proc(record, "bal")):
        codes.append("31624")
        rationales["31624"] = "bal.performed=true"

    # Transbronchial lung biopsy (31628) and cryobiopsy are billed under 31628,
    # with add-on 31632 for additional lobes when documented.
    tbbx = _proc(record, "transbronchial_biopsy")
    cryo_tbbx = _proc(record, "transbronchial_cryobiopsy")
    if _performed(tbbx) or _performed(cryo_tbbx):
        codes.append("31628")
        if _performed(tbbx):
            rationales["31628"] = "transbronchial_biopsy.performed=true"
        else:
            rationales["31628"] = "transbronchial_cryobiopsy.performed=true"

        # Additional lobe add-on (31632) requires multi-lobe locations.
        locations = None
        for proc in (tbbx, cryo_tbbx):
            if proc is None:
                continue
            locations = getattr(proc, "locations", None) or getattr(proc, "sites", None)
            if locations:
                break
        if locations:
            lobes = _lobe_tokens([str(x) for x in locations if x])
            if len(lobes) >= 2:
                codes.append("31632")
                rationales["31632"] = f"transbronchial_biopsy.locations spans lobes={sorted(lobes)}"

    # Conventional (non-EBUS) TBNA (31629) with add-on 31633 for additional lobes.
    tbna = _proc(record, "tbna_conventional")
    if _performed(tbna):
        codes.append("31629")
        rationales["31629"] = "tbna_conventional.performed=true"

        locations = getattr(tbna, "locations", None) or getattr(tbna, "sites", None)
        if locations:
            lobes = _lobe_tokens([str(x) for x in locations if x])
            if len(lobes) >= 2:
                codes.append("31633")
                rationales["31633"] = f"tbna_conventional.locations spans lobes={sorted(lobes)}"

    # Linear EBUS TBNA (31652/31653) based on station count.
    if _performed(_proc(record, "linear_ebus")):
        stations, station_source = _stations_sampled(record)
        station_count = len(set(s for s in stations if s))
        if station_count >= 3:
            codes.append("31653")
            rationales["31653"] = (
                f"linear_ebus.performed=true and sampled_station_count={station_count} (>=3) "
                f"from {station_source}"
            )
        elif station_count in (1, 2):
            codes.append("31652")
            rationales["31652"] = (
                f"linear_ebus.performed=true and sampled_station_count={station_count} (1-2) "
                f"from {station_source}"
            )
        else:
            if station_source == "node_events":
                warnings.append(
                    "linear_ebus.performed=true but node_events contains no qualifying sampling actions; "
                    "cannot derive 31652/31653"
                )
            else:
                warnings.append(
                    "linear_ebus.performed=true but stations_sampled missing/empty; cannot derive 31652/31653"
                )

    # Radial EBUS (add-on code for peripheral lesion localization)
    if _performed(_proc(record, "radial_ebus")):
        codes.append("31654")
        rationales["31654"] = "radial_ebus.performed=true"

    # Navigation add-on
    if _performed(_proc(record, "navigational_bronchoscopy")):
        codes.append("31627")
        rationales["31627"] = "navigational_bronchoscopy.performed=true"

    # Fiducial marker placement (navigation add-on)
    if _fiducial_marker_placed(record):
        codes.append("31626")
        rationales["31626"] = "granular_data.navigation_targets indicates fiducial marker placement"

    # Therapeutic aspiration
    if _performed(_proc(record, "therapeutic_aspiration")):
        codes.append("31645")
        rationales["31645"] = "therapeutic_aspiration.performed=true"

    # Foreign body removal
    if _performed(_proc(record, "foreign_body_removal")):
        codes.append("31635")
        rationales["31635"] = "foreign_body_removal.performed=true"

    # Airway dilation
    if _performed(_proc(record, "airway_dilation")):
        codes.append("31630")
        rationales["31630"] = "airway_dilation.performed=true"

    # Airway stent
    stent = _proc(record, "airway_stent")
    if stent is not None:
        action = getattr(stent, "action", None)
        removal_flag = getattr(stent, "airway_stent_removal", None)
        is_removal = removal_flag is True or _stent_action_is_removal(action)
        is_placement = _performed(stent) and not is_removal
        if not is_placement and _stent_action_is_placement(action):
            is_placement = True

        if is_removal:
            codes.append("31638")
            rationales["31638"] = "airway_stent.airway_stent_removal=true or action indicates removal"
        elif is_placement:
            codes.append("31636")
            rationales["31636"] = "airway_stent.performed=true and no removal flag"

    # Thermal ablation (tumor destruction) → 31641
    if _performed(_proc(record, "thermal_ablation")):
        codes.append("31641")
        rationales["31641"] = "thermal_ablation.performed=true"

    # Cryotherapy (tumor destruction) → 31641
    # Note: If both thermal_ablation and cryotherapy performed, only one 31641
    if _performed(_proc(record, "cryotherapy")) and "31641" not in codes:
        codes.append("31641")
        rationales["31641"] = "cryotherapy.performed=true"

    # BLVR valve family
    blvr = _proc(record, "blvr")
    if _performed(blvr):
        procedure_type = getattr(blvr, "procedure_type", None)
        num_valves = getattr(blvr, "number_of_valves", None)
        if procedure_type == "Valve removal":
            codes.append("31649")
            rationales["31649"] = "blvr.procedure_type='Valve removal'"
        else:
            codes.append("31647")
            rationales["31647"] = "blvr.procedure_type!='Valve removal' (default to valve placement family)"
            if isinstance(num_valves, int) and num_valves >= 2:
                codes.append("31648")
                rationales["31648"] = f"blvr.number_of_valves={num_valves} (>=2)"

    # Bronchial thermoplasty: 31660 initial + 31661 additional lobes.
    bt = _proc(record, "bronchial_thermoplasty")
    if _performed(bt):
        codes.append("31660")
        rationales["31660"] = "bronchial_thermoplasty.performed=true"
        areas = getattr(bt, "areas_treated", None)
        if areas and len(areas) >= 2:
            codes.append("31661")
            rationales["31661"] = f"bronchial_thermoplasty.areas_treated_count={len(areas)} (>=2)"

    # Tracheostomy: distinguish established route vs new percutaneous trach.
    established_trach_route = getattr(record, "established_tracheostomy_route", False) is True
    if established_trach_route:
        codes.append("31615")
        rationales["31615"] = "established_tracheostomy_route=true"

    # Percutaneous tracheostomy (new trach creation)
    if _performed(_proc(record, "percutaneous_tracheostomy")):
        if established_trach_route:
            warnings.append(
                "percutaneous_tracheostomy.performed=true but established_tracheostomy_route=true; suppressing 31600"
            )
        else:
            codes.append("31600")
            rationales["31600"] = "percutaneous_tracheostomy.performed=true and established_tracheostomy_route=false"

    # Neck ultrasound (often pre-tracheostomy vascular mapping)
    if _performed(_proc(record, "neck_ultrasound")):
        codes.append("76536")
        rationales["76536"] = "neck_ultrasound.performed=true"

    # --- Pleural family ---
    if _performed(_pleural(record, "ipc")):
        codes.append("32550")
        rationales["32550"] = "pleural_procedures.ipc.performed=true"

    thora = _pleural(record, "thoracentesis")
    if _performed(thora):
        guidance = getattr(thora, "guidance", None)
        if guidance == "Ultrasound":
            codes.append("32555")
            rationales["32555"] = "thoracentesis.performed=true and guidance='Ultrasound'"
        else:
            codes.append("32554")
            rationales["32554"] = "thoracentesis.performed=true and guidance!='Ultrasound'"

    if _performed(_pleural(record, "chest_tube")):
        codes.append("32551")
        rationales["32551"] = "pleural_procedures.chest_tube.performed=true"

    if _performed(_pleural(record, "medical_thoracoscopy")):
        codes.append("32601")
        rationales["32601"] = "pleural_procedures.medical_thoracoscopy.performed=true"

    if _performed(_pleural(record, "pleurodesis")):
        codes.append("32560")
        rationales["32560"] = "pleural_procedures.pleurodesis.performed=true"

    if _performed(_pleural(record, "fibrinolytic_therapy")):
        codes.append("32561")
        rationales["32561"] = "pleural_procedures.fibrinolytic_therapy.performed=true"

    # ---------------------------------------------------------------------
    # Post-processing: mutual exclusions & add-on safety
    # ---------------------------------------------------------------------
    derived = sorted(set(codes))

    # Mutually exclusive: 31652 vs 31653 (prefer 31653)
    if "31652" in derived and "31653" in derived:
        derived = [c for c in derived if c != "31652"]
        rationales.pop("31652", None)

    # Mutually exclusive: 32554 vs 32555 (prefer imaging-guided)
    if "32554" in derived and "32555" in derived:
        derived = [c for c in derived if c != "32554"]
        rationales.pop("32554", None)

    # Bundling: Dilation (31630) vs Destruction (31641) / Excision (31640)
    # If destruction/excision is present, bundle dilation unless in distinct lobe
    destruction_codes = {"31641", "31640"}
    if any(c in destruction_codes for c in derived) and "31630" in derived:
        distinct_lobes = _dilation_in_distinct_lobe_from_destruction(record)
        if not distinct_lobes:
            derived = [c for c in derived if c != "31630"]
            warnings.append(
                "31630 (dilation) bundled into destruction/excision code - "
                "add granular lobe data if performed in distinct anatomic location"
            )
            rationales.pop("31630", None)

    # Add-on codes require a primary bronchoscopy.
    addon_codes = {"31626", "31627", "31632", "31648", "31654", "31661"}
    primary_bronch = {
        "31622",
        "31623",
        "31624",
        "31628",
        "31629",
        "31641",
        "31647",
        "31652",
        "31653",
        "31660",
    }
    if not any(c in primary_bronch for c in derived):
        derived = [c for c in derived if c not in addon_codes]
        for c in addon_codes:
            rationales.pop(c, None)

    return derived, rationales, warnings


def derive_all_codes(record: RegistryRecord) -> list[str]:
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    return codes


__all__ = ["derive_all_codes", "derive_all_codes_with_meta"]
