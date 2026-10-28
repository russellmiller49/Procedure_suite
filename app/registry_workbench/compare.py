"""Align proposals and revisions by clinical natural keys for side-by-side review.

UUIDs differ between extractors, so rows are matched on what a reviewer would
match them on: lobe or station for targets, station for surveys, category for
procedures and complications, and the parent target for child rows.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

ID_FIELDS = {
    "target_id",
    "target_identity_id",
    "ebus_session_id",
    "station_survey_id",
    "navigation_run_id",
    "localization_event_id",
    "localization_event_id_before_pass",
    "sampling_pass_id",
    "specimen_id",
    "sampling_specimen_link_id",
    "pathology_result_id",
    "supersedes_pathology_result_id",
    "adverse_event_id",
    "source_document_id",
    "operator_id",
}


def _documented(value: Any) -> bool:
    # "not_documented" is the contract's explicit missing marker, not a value.
    return value is not None and value != "not_documented"


def _target_key(row: dict[str, Any]) -> str:
    if row.get("site") == "lymph_node":
        return f"node {row.get('iaslc_station') or '?'}"
    if row.get("site") == "central_mass":
        return f"central {row.get('anatomic_label') or '?'}"
    return f"lung {row.get('lobe') or '?'}"


def flatten(values: dict[str, Any] | None) -> dict[tuple[str, str, str], Any]:
    if not values:
        return {}
    out: dict[tuple[str, str, str], Any] = {}

    def keyed(collection: str, rows: list[dict[str, Any]], key_of) -> dict[str, str]:
        seen: Counter[str] = Counter()
        ids: dict[str, str] = {}
        for row in rows:
            base = key_of(row)
            seen[base] += 1
            key = base if seen[base] == 1 else f"{base} #{seen[base]}"
            for field, value in row.items():
                if field not in ID_FIELDS and _documented(value):
                    out[(collection, key, field)] = value
            primary = {
                "targets": "target_id",
                "sampling_acquisitions": "sampling_pass_id",
                "specimens": "specimen_id",
            }.get(collection)
            if primary and row.get(primary):
                ids[row[primary]] = key
        return ids

    keyed("procedures", values.get("procedures") or [], lambda r: r.get("category") or "?")
    for field, value in (values.get("case_details") or {}).items():
        if field not in ID_FIELDS and _documented(value):
            out[("case_details", "case", field)] = value
    if _documented(values.get("complication_assessment")):
        out[("revision", "revision", "complication_assessment")] = values["complication_assessment"]
    targets = keyed("targets", values.get("targets") or [], _target_key)
    keyed("ebus_sessions", values.get("ebus_sessions") or [], lambda r: "EBUS session")
    keyed(
        "station_surveys",
        values.get("station_surveys") or [],
        lambda r: f"station {r.get('iaslc_station')}",
    )

    def under(row: dict[str, Any], suffix: str) -> str:
        return f"{targets.get(row.get('target_id'), 'unattributed')} · {suffix}"

    keyed("navigation_runs", values.get("navigation_runs") or [], lambda r: under(r, "navigation"))
    keyed(
        "localization_events",
        values.get("localization_events") or [],
        lambda r: under(r, r.get("localization_modality") or "?"),
    )
    acquisitions = keyed(
        "sampling_acquisitions",
        values.get("sampling_acquisitions") or [],
        lambda r: under(
            r, f"{r.get('sampling_tool') or '?'} {r.get('acquisition_record_granularity')}"
        ),
    )
    specimens = keyed(
        "specimens",
        values.get("specimens") or [],
        lambda r: f"specimen {r.get('specimen_label') or under(r, '?')}",
    )
    keyed(
        "sampling_specimen_links",
        values.get("sampling_specimen_links") or [],
        lambda r: (
            f"{acquisitions.get(r.get('sampling_pass_id'), '?')} -> "
            f"{specimens.get(r.get('specimen_id'), '?')}"
        ),
    )
    keyed("complications", values.get("complications") or [], lambda r: r.get("category") or "?")
    keyed("follow_up", values.get("follow_up") or [], lambda r: r.get("window") or "?")
    keyed(
        "pathology_results",
        values.get("pathology_results") or [],
        lambda r: f"{specimens.get(r.get('specimen_id'), '?')} {r.get('result_status')}",
    )
    return out


def compare(sources: dict[str, dict[str, Any] | None]) -> list[dict[str, Any]]:
    flat = {label: flatten(values) for label, values in sources.items()}
    keys = sorted({key for values in flat.values() for key in values})
    rows = []
    for collection, row_key, field in keys:
        values = {label: flat[label].get((collection, row_key, field)) for label in flat}
        present = [v for v in values.values() if v is not None]
        rows.append(
            {
                "collection": collection,
                "row": row_key,
                "field": field,
                "values": values,
                "agree": len(present) == len(values) and len({repr(v) for v in present}) == 1,
            }
        )
    return rows


__all__ = ["compare", "flatten"]
