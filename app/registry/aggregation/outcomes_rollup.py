"""Longitudinal outcome rollup for case aggregation.

Derives the case-level ``longitudinal_outcomes`` block from the canonical case
snapshot (clinical_course updates, imaging follow-ups, pathology results) and
the appended event rows. Runs after per-event patching so it sees the merged,
lock-respecting state; the block itself honors a manual-override lock on the
``longitudinal_outcomes`` pointer.
"""

from __future__ import annotations

import re
from typing import Any

from app.registry.aggregation.locks import is_pointer_locked, pointer_join


DAY30_WINDOW = 30

_MALIGNANT_RE = re.compile(
    r"\b(?:adenocarcinoma|squamous\s+cell|small\s+cell|non[-\s]?small\s+cell|nsclc|sclc|"
    r"carcinoma|carcinoid|malignan\w+|metasta\w+|lymphoma|mesothelioma|sarcoma|"
    r"positive\s+for\s+malignan\w+)\b",
    re.IGNORECASE,
)
_MALIGNANT_NEG_RE = re.compile(
    r"\b(?:no|negative\s+for|without|free\s+of)\b[^.\n;]{0,60}\bmalignan\w+\b"
    r"|\bmalignan\w+\b[^.\n;]{0,20}\bnot\s+identified\b",
    re.IGNORECASE,
)
_BENIGN_SPECIFIC_RE = re.compile(
    r"\b(?:granulom\w+|sarcoid\w*|hamartoma|infecti\w+|organizing\s+pneumonia|"
    r"amyloid\w*|tuberculo\w+|histoplasm\w+|fungal|aspergill\w+|benign)\b",
    re.IGNORECASE,
)
_NONDIAGNOSTIC_RE = re.compile(
    r"\b(?:non[-\s]?diagnostic|insufficient|inadequate|scant\s+cellularity|"
    r"blood\s+and\s+debris\s+only|no\s+lesional\s+tissue)\b",
    re.IGNORECASE,
)


def classify_diagnostic_yield(final_diagnosis: str | None) -> str | None:
    """Classify a pathology final diagnosis into a diagnostic-yield category."""
    text = str(final_diagnosis or "").strip()
    if not text:
        return None
    if _NONDIAGNOSTIC_RE.search(text):
        return "Nondiagnostic"
    if _MALIGNANT_RE.search(text) and not _MALIGNANT_NEG_RE.search(text):
        return "Malignant"
    if _BENIGN_SPECIFIC_RE.search(text):
        return "Benign-specific"
    if _MALIGNANT_NEG_RE.search(text):
        return "Benign-specific"
    return "Unknown"


def _stations_sampled(registry_json: dict[str, Any]) -> set[str]:
    procedures = registry_json.get("procedures_performed")
    linear = procedures.get("linear_ebus") if isinstance(procedures, dict) else None
    stations = linear.get("stations_sampled") if isinstance(linear, dict) else None
    if not isinstance(stations, list):
        return set()
    return {str(s).strip().upper() for s in stations if str(s).strip()}


def station_concordance_flags(
    registry_json: dict[str, Any],
    node_updates: list[dict[str, Any]] | None,
) -> list[str]:
    """QA flags when pathology stations disagree with the procedure record."""
    sampled = _stations_sampled(registry_json)
    if not sampled or not node_updates:
        return []
    flags: list[str] = []
    path_stations = {
        str(u.get("station") or "").strip().upper()
        for u in node_updates
        if isinstance(u, dict) and str(u.get("station") or "").strip()
    }
    unexpected = sorted(path_stations - sampled)
    if unexpected:
        flags.append("path_station_not_in_stations_sampled:" + ",".join(unexpected))
    missing = sorted(sampled - path_stations)
    if path_stations and missing:
        flags.append("sampled_station_missing_from_path:" + ",".join(missing))
    return flags


def _iter_clinical_updates(registry_json: dict[str, Any]) -> list[dict[str, Any]]:
    course = registry_json.get("clinical_course")
    updates = course.get("updates") if isinstance(course, dict) else None
    return [u for u in updates if isinstance(u, dict)] if isinstance(updates, list) else []


def _offset(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def derive_longitudinal_outcomes(
    registry_json: dict[str, Any],
    *,
    event_rows: list[Any] | None = None,
    manual_overrides: dict[str, Any] | None = None,
) -> tuple[bool, list[str]]:
    """Compute/refresh registry_json["longitudinal_outcomes"] from merged state.

    Returns (changed, qa_flags).
    """
    pointer = pointer_join("longitudinal_outcomes")
    if is_pointer_locked(manual_overrides, pointer):
        return False, ["longitudinal_outcomes_locked"]

    qa_flags: list[str] = []
    updates = _iter_clinical_updates(registry_json)

    day30_complication: bool | None = None
    day30_readmission: bool | None = None
    day30_ed_visit: bool | None = None
    day30_mortality: bool | None = None
    survival_status: str | None = None
    last_known_offset: int | None = None
    complication_types: list[str] = []

    def _note_offset(offset: int | None) -> None:
        nonlocal last_known_offset
        if offset is None:
            return
        if last_known_offset is None or offset > last_known_offset:
            last_known_offset = offset

    for update in updates:
        offset = _offset(update.get("relative_day_offset"))
        _note_offset(offset)
        in_window = offset is not None and 0 <= offset <= DAY30_WINDOW

        if update.get("deceased") is True:
            survival_status = "Deceased"
            if in_window:
                day30_mortality = True
        elif survival_status != "Deceased":
            survival_status = "Alive"

        if not in_window:
            continue

        types = update.get("complication_types")
        has_complication = bool(types) or str(update.get("update_type") or "") == "complication"
        if has_complication:
            day30_complication = True
            for label in types or []:
                if isinstance(label, str) and label and label not in complication_types:
                    complication_types.append(label)

        if update.get("ed_visit") is True:
            day30_ed_visit = True
        if update.get("readmission") is True or (
            update.get("hospital_admission") is True and (offset or 0) > 0
        ):
            day30_readmission = True

    # Post-procedure imaging findings within the window also count as complications.
    imaging = registry_json.get("imaging_summary")
    followups = imaging.get("followups") if isinstance(imaging, dict) else None
    for snapshot in followups if isinstance(followups, list) else []:
        if not isinstance(snapshot, dict):
            continue
        offset = _offset(snapshot.get("relative_day_offset"))
        _note_offset(offset)
        if offset is None or not (0 <= offset <= DAY30_WINDOW):
            continue
        if snapshot.get("pneumothorax") is True:
            day30_complication = True
            if "pneumothorax" not in complication_types:
                complication_types.append("pneumothorax")

    reintervention: bool | None = None
    for row in event_rows or []:
        event_type = str(getattr(row, "event_type", "") or "").strip().lower()
        offset = _offset(getattr(row, "relative_day_offset", None))
        if event_type in {"procedure", "procedure_addendum"} and offset is not None and 0 < offset <= DAY30_WINDOW:
            reintervention = True

    pathology = registry_json.get("pathology_results")
    diagnostic_yield: str | None = None
    if isinstance(pathology, dict) and pathology:
        diagnostic_yield = classify_diagnostic_yield(pathology.get("final_diagnosis"))
        if diagnostic_yield in (None, "Unknown"):
            # Fall back to per-specimen results (best result wins).
            from app.registry.aggregation.pathology.specimen_yield import best_yield_from_specimens

            specimen_yield = best_yield_from_specimens(
                pathology.get("specimen_results") if isinstance(pathology.get("specimen_results"), list) else None
            )
            diagnostic_yield = specimen_yield or diagnostic_yield
        if diagnostic_yield is None:
            diagnostic_yield = "Pending"

    if survival_status is None and (updates or followups):
        survival_status = "Alive"

    block: dict[str, Any] = {
        "day30_complication": day30_complication,
        "day30_readmission": day30_readmission,
        "day30_ed_visit": day30_ed_visit,
        "day30_mortality": day30_mortality,
        "survival_status": survival_status,
        "last_known_status_day_offset": last_known_offset,
        "diagnostic_yield": diagnostic_yield,
        "reintervention_within_30d": reintervention,
        "complication_types": complication_types,
        "qa_flags": sorted(set(qa_flags)),
    }

    if all(
        value in (None, [], {})
        for key, value in block.items()
        if key != "qa_flags"
    ):
        # Nothing longitudinal known yet; leave the section absent.
        return False, qa_flags

    if registry_json.get("longitudinal_outcomes") == block:
        return False, qa_flags

    registry_json["longitudinal_outcomes"] = block
    return True, qa_flags


__all__ = [
    "classify_diagnostic_yield",
    "derive_longitudinal_outcomes",
    "station_concordance_flags",
]
