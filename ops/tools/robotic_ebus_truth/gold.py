"""Decide what a note states, then build the gold ClinicalRevision from exactly that.

Gold values come only from stated units; each carries the exact span of the
sentence that states it. Rows whose required parent was never stated are dropped,
so the gold never asserts a link the note cannot support. Every gold record must
validate against the contract with no approval errors.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any

import app.registry_workbench  # noqa: F401  (puts packages/*/src on sys.path)
from ip_registry_contracts.launch import ENTITY_MODELS, PROFILE, VERSION
from ip_registry_contracts.models import ClinicalRevision, approval_errors
from ip_registry_engine.focused import stable_id

from ops.tools.robotic_ebus_truth.scenarios import Scenario

PRIMARY_KEYS = {
    "targets": "target_id",
    "ebus_sessions": "ebus_session_id",
    "station_surveys": "station_survey_id",
    "navigation_runs": "navigation_run_id",
    "localization_events": "localization_event_id",
    "sampling_acquisitions": "sampling_pass_id",
    "specimens": "specimen_id",
    "sampling_specimen_links": "sampling_specimen_link_id",
    "complications": "adverse_event_id",
}
REQUIRED_PARENTS = {
    "station_surveys": ("ebus_session_id",),
    "navigation_runs": ("target_id",),
    "localization_events": ("target_id",),
    "sampling_specimen_links": ("sampling_pass_id", "specimen_id"),
}
PARENT_COLLECTION = {
    "target_id": "targets",
    "ebus_session_id": "ebus_sessions",
    "station_survey_id": "station_surveys",
    "navigation_run_id": "navigation_runs",
    "sampling_pass_id": "sampling_acquisitions",
    "specimen_id": "specimens",
}
SEQUENCES = {
    "navigation_runs": "run_sequence_number",
    "localization_events": "event_sequence_number",
}
COLLECTION_ORDER = (
    "procedures",
    *[c for c in ENTITY_MODELS if c not in {"case_details", "pathology_results", "follow_up"}],
)


class GoldError(ValueError):
    pass


def plan_statements(scenario: Scenario, seed: int) -> set[str]:
    """Core units are always stated; others with their weight."""
    rng = random.Random(seed)
    return {u.id for u in scenario.units if u.core or rng.random() < u.weight}


def build_gold(
    scenario: Scenario,
    stated: set[str],
    spans: dict[str, tuple[int, int]],
    text: str,
    *,
    document_id: str,
    digest: str,
) -> dict[str, Any]:
    values: dict[tuple[str, str], dict[str, Any]] = defaultdict(dict)
    evidence: dict[tuple[str, str, str], tuple[tuple[int, int], str]] = {}
    for unit in scenario.units:
        if unit.id not in stated or unit.id not in spans:
            continue
        for collection, local, field, value in unit.sets:
            values[(collection, local)][field] = value
            evidence[(collection, local, field)] = (spans[unit.id], unit.assertion)

    present = {
        collection: [r for r in rows if (collection, r["local_id"]) in values]
        for collection, rows in scenario.rows.items()
    }
    changed = True
    while changed:
        changed = False
        ids = {(c, r["local_id"]) for c, rows in present.items() for r in rows}
        for collection, rows in present.items():
            keep = [
                r
                for r in rows
                if all(
                    (PARENT_COLLECTION[p], r["parents"].get(p)) in ids
                    for p in REQUIRED_PARENTS.get(collection, ())
                )
            ]
            if len(keep) != len(rows):
                present[collection], changed = keep, True
    ids = {(c, r["local_id"]) for c, rows in present.items() for r in rows}

    def uuid(collection: str, local: str) -> str:
        return stable_id(scenario.family_id, f"truth:{collection}:{local}")

    revision: dict[str, Any] = {
        "schema_version": VERSION,
        "registry_profile": PROFILE,
        "event_date": scenario.event_date.isoformat(),
        "case_details": {},
        **{c: [] for c in COLLECTION_ORDER},
        "field_provenance": [],
    }
    provenance = revision["field_provenance"]

    def cite(path: str, key: tuple[str, str, str]) -> None:
        (start, end), assertion = evidence[key]
        provenance.append(
            {
                "field_path": path,
                "source_document_id": document_id,
                "source_digest": digest,
                "source_start": start,
                "source_end": end,
                "source_excerpt": text[start:end],
                "raw_value": text[start:end],
                "value_origin": "extracted",
                "assertion_context": assertion,
                "review_status": "reviewed",
                "extractor_model_version": "truth-first-generator",
            }
        )

    for field, value in values.get(("case_details", "case_details"), {}).items():
        revision["case_details"][field] = value
        cite(f"/case_details/{field}", ("case_details", "case_details", field))
    for field, value in values.get(("revision", "revision"), {}).items():
        revision[field] = value
        cite(f"/{field}", ("revision", "revision", field))

    sequences: dict[tuple[str, str | None], int] = defaultdict(int)
    for collection in COLLECTION_ORDER:
        for row in present.get(collection, []):
            local = row["local_id"]
            index = len(revision[collection])
            data: dict[str, Any] = {}
            if collection in PRIMARY_KEYS:
                data[PRIMARY_KEYS[collection]] = uuid(collection, local)
            for parent_field, parent_local in row["parents"].items():
                parent = PARENT_COLLECTION[parent_field]
                if (parent, parent_local) in ids:
                    data[parent_field] = uuid(parent, parent_local)
            if collection in SEQUENCES:
                slot = (collection, row["parents"].get("target_id"))
                sequences[slot] += 1
                data[SEQUENCES[collection]] = sequences[slot]
            fields = values[(collection, local)]
            if collection == "sampling_acquisitions" and "target_id" in data:
                data["attribution_status"] = "attributed"
            if (
                collection == "sampling_acquisitions"
                and fields.get("acquisition_record_granularity") == "single_pass"
            ):
                slot = ("single_pass", row["parents"].get("target_id"))
                sequences[slot] += 1
                data["pass_sequence_number"] = sequences[slot]
            for field, value in fields.items():
                data[field] = value
                cite(f"/{collection}/{index}/{field}", (collection, local, field))
            revision[collection].append(data)

    try:
        validated = ClinicalRevision.model_validate(revision)
    except ValueError as exc:
        raise GoldError(f"{scenario.family_id}: gold violates the contract: {exc}") from exc
    errors = approval_errors(validated)
    if errors:
        raise GoldError(f"{scenario.family_id}: gold has approval errors {errors}")
    # Store only real values and real evidence: validation re-creates the
    # not_documented provenance for every empty field, so it is not written out.
    dumped = validated.model_dump(mode="json", exclude_none=True)
    dumped["field_provenance"] = [
        p
        for p in dumped["field_provenance"]
        if not (p["value_origin"] == "missing" and p.get("missingness_reason") == "not_documented")
    ]
    return dumped


__all__ = ["GoldError", "build_gold", "plan_statements"]
