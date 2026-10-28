"""Derive the LLM-facing field specs from the launch contract, never by hand.

Primary keys, provenance, sequence numbers and derived fields are assigned by the
assembler; foreign keys become row ``parents``. Everything else is a fact.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.llm_extraction.facts_schema import CollectionSpec, FieldSpec, build_facts_schema
from app.registry_workbench._contracts import DICTIONARY_PATH
from ip_registry_contracts.launch import ENTITY_MODELS, MissingReason
from ip_registry_contracts.models import ClinicalRevision, ProcedureEvent

SINGLETON_REVISION = "revision"

# Foreign key -> parent collection (mirrors launch.validate_links ``references``).
REFERENCES = {
    "target_id": "targets",
    "ebus_session_id": "ebus_sessions",
    "station_survey_id": "station_surveys",
    "navigation_run_id": "navigation_runs",
    "localization_event_id_before_pass": "localization_events",
    "specimen_id": "specimens",
    "sampling_pass_id": "sampling_acquisitions",
    "supersedes_pathology_result_id": "pathology_results",
}
PRIMARY_KEYS = {
    "targets": "target_id",
    "ebus_sessions": "ebus_session_id",
    "station_surveys": "station_survey_id",
    "navigation_runs": "navigation_run_id",
    "localization_events": "localization_event_id",
    "sampling_acquisitions": "sampling_pass_id",
    "specimens": "specimen_id",
    "sampling_specimen_links": "sampling_specimen_link_id",
    "pathology_results": "pathology_result_id",
    "complications": "adverse_event_id",
}
# Assigned from row order within the parent target.
SEQUENCE_FIELDS = {
    "navigation_runs": "run_sequence_number",
    "localization_events": "event_sequence_number",
    "sampling_acquisitions": "pass_sequence_number",
}
# Derived later from pathology with a versioned rule; never extracted from a note.
DERIVED_FIELDS = {("targets", "node_interpretation")}

PROCEDURE_COLLECTIONS = (
    "procedures",
    "case_details",
    "targets",
    "ebus_sessions",
    "station_surveys",
    "navigation_runs",
    "localization_events",
    "sampling_acquisitions",
    "specimens",
    "sampling_specimen_links",
    "complications",
    SINGLETON_REVISION,
)
UNRESOLVED_KINDS = (
    "planned_only",
    "historical",
    "uncertain",
    "conflicting_statements",
    "outside_launch_scope",
    "unmapped_detail",
)
MISSING_REASONS = tuple(r for r in MissingReason.__args__ if r != "not_documented")  # type: ignore[attr-defined]


@dataclass(frozen=True)
class ContractSpec:
    collections: tuple[CollectionSpec, ...]
    required: dict[str, tuple[str, ...]]
    required_parents: dict[str, tuple[str, ...]]

    @property
    def fields(self) -> dict[str, FieldSpec]:
        return {spec.path: spec for c in self.collections for spec in c.fields}

    def collection(self, name: str) -> CollectionSpec:
        return next(c for c in self.collections if c.name == name)

    def schema(self) -> dict[str, Any]:
        return build_facts_schema(
            self.collections, missing_reasons=MISSING_REASONS, unresolved_kinds=UNRESOLVED_KINDS
        )


def _resolve(prop: dict[str, Any], defs: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in prop:
        return defs[prop["$ref"].rsplit("/", 1)[-1]]
    options = [o for o in prop.get("anyOf", []) if o.get("type") != "null"]
    if options:
        option = options[0]
        return defs[option["$ref"].rsplit("/", 1)[-1]] if "$ref" in option else option
    return prop


def _field_spec(collection: str, name: str, prop: dict[str, Any]) -> FieldSpec | None:
    kind = prop.get("type")
    if "enum" in prop:
        return FieldSpec(collection, name, "enum", values=tuple(prop["enum"]))
    if kind == "boolean":
        return FieldSpec(collection, name, "bool")
    if kind in {"number", "integer"}:
        return FieldSpec(
            collection,
            name,
            "integer" if kind == "integer" else "number",
            minimum=prop.get("minimum"),
            maximum=prop.get("maximum"),
        )
    if kind == "string" and prop.get("format") in {"uuid4", "uuid"}:
        return None
    if kind == "string":
        return FieldSpec(collection, name, "text", max_length=prop.get("maxLength"))
    return None


def _model_specs(collection: str, model: Any):
    schema = model.model_json_schema()
    defs = schema.get("$defs", {})
    specs, parents, required, required_parents = [], {}, [], []
    for name, raw in schema["properties"].items():
        if name in REFERENCES and REFERENCES[name] != collection:
            parents[name] = REFERENCES[name]
            if model.model_fields[name].is_required():
                required_parents.append(name)
            continue
        if (collection, name) in DERIVED_FIELDS or SEQUENCE_FIELDS.get(collection) == name:
            continue
        spec = _field_spec(collection, name, _resolve(raw, defs))
        if spec is None:
            continue
        specs.append(spec)
        if model.model_fields[name].is_required():
            required.append(name)
    return tuple(specs), parents, tuple(required), tuple(required_parents)


@lru_cache(maxsize=None)
def contract_spec(collections: tuple[str, ...] = PROCEDURE_COLLECTIONS) -> ContractSpec:
    built, required, required_parents = [], {}, {}
    for name in collections:
        if name == SINGLETON_REVISION:
            defs = ClinicalRevision.model_json_schema()["$defs"]
            prop = _resolve(ClinicalRevision.model_json_schema()["properties"]["complication_assessment"], defs)
            built.append(
                CollectionSpec(
                    name, (FieldSpec(name, "complication_assessment", "enum", values=tuple(prop["enum"])),), True
                )
            )
            continue
        model = ProcedureEvent if name == "procedures" else ENTITY_MODELS[name]
        specs, parents, req, req_parents = _model_specs(name, model)
        built.append(CollectionSpec(name, specs, singleton=name == "case_details", parents=parents))
        required[name] = req
        required_parents[name] = req_parents
    return ContractSpec(tuple(built), required, required_parents)


@lru_cache(maxsize=1)
def dictionary() -> dict[str, Any]:
    return json.loads(DICTIONARY_PATH.read_text())


def dictionary_fields() -> dict[str, dict[str, Any]]:
    return {entry["contract_path"]: entry for entry in dictionary()["fields"]}


__all__ = [
    "ContractSpec",
    "MISSING_REASONS",
    "PRIMARY_KEYS",
    "PROCEDURE_COLLECTIONS",
    "REFERENCES",
    "SEQUENCE_FIELDS",
    "SINGLETON_REVISION",
    "UNRESOLVED_KINDS",
    "contract_spec",
    "dictionary",
    "dictionary_fields",
]
