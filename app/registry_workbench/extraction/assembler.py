"""Turn Claude's sparse facts into a validated robotic_ebus_v1 proposal.

Everything here is deterministic. Facts become values only with an anchored
verbatim quote and an active or negated assertion. Planned, historical and
uncertain statements become unresolved mentions. A value that trips a contract
validator is kept as an unresolved conflict (null value, claim in ``raw_value``)
so approval stays blocked until a reviewer decides. Rows are rendered in their
final order before provenance is written, because provenance paths are positional.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from ip_registry_contracts.launch import ENTITY_MODELS, PROFILE, VERSION
from ip_registry_contracts.models import ClinicalRevision, approval_errors
from ip_registry_engine.focused import stable_id
from pydantic import ValidationError

from app.llm_extraction.anchoring import AnchoredSpan, anchor
from app.llm_extraction.facts_schema import FACT_ARRAYS, FactValueError
from app.registry_workbench.extraction.contract_spec import (
    PRIMARY_KEYS,
    PROCEDURE_COLLECTIONS,
    SEQUENCE_FIELDS,
    SINGLETON_REVISION,
    ContractSpec,
    contract_spec,
)

# Only used to run the revision validators; the encounter supplies the real date.
VALIDATION_EVENT_DATE = date(2000, 1, 1)
MAX_REPAIR_PASSES = 40
NEGATED_VALUES = {"present": "absent", "performed": "not_performed"}
# A negated complication category is an explicit denial of that event.
DENIED_EVENT_FIELD = "complications.category"
# "No complications" denies nothing in particular: that belongs in complication_assessment,
# not in a row for an unnamed "other" event.
GENERIC_EVENT = "other_approved"
# Values that already say "no": a sentence such as "EBUS was not started" states this value,
# and a model that marks it negated is describing the sentence, not negating the value.
STATED_NEGATIVES = {*NEGATED_VALUES.values(), "not_started"}
DEFERRED_ASSERTIONS = {
    "planned": "planned_only",
    "historical": "historical",
    "uncertain": "uncertain",
}

# Row validator code -> fields that become unresolved conflicts.
ROW_TRIPS = {
    "short_axis_requires_explicit_ultrasound_axis": ("short_axis_mm", "largest_short_axis_mm"),
    "til_requires_actual_sampling_tool_and_lesion_confirmation": ("tool_lesion_relationship",),
    "single_pass_count_must_be_one": ("reported_pass_count",),
    "attribution_requires_target": ("attribution_status", "target_attribution_status"),
    "event_outside_launch_followup": ("relative_day_offset",),
    "event_window_day_mismatch": ("relative_day_offset", "event_time_window"),
    "completion_requires_started_component": ("completion",),
    "started_component_cannot_be_not_started": ("completion",),
}


@dataclass
class Fact:
    value: Any
    span: AnchoredSpan | None = None
    assertion: str | None = "active"
    origin: str = "extracted"
    missing_reason: str | None = None
    conflict: bool = False
    raw: str | None = None


@dataclass
class RowDraft:
    collection: str
    local_id: str
    anchor: AnchoredSpan | None = None
    parents: dict[str, str] = field(default_factory=dict)
    values: dict[str, Fact] = field(default_factory=dict)

    def value(self, name: str) -> Any:
        fact = self.values.get(name)
        return None if fact is None else fact.value


@dataclass
class Assembly:
    proposal: dict[str, Any]
    unresolved: list[dict[str, Any]]
    stats: dict[str, int]
    errors: list[str]
    approval_errors: list[str]

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def has_started_component(self) -> bool:
        return any(
            p.get("performance") in {"performed", "attempted"} for p in self.proposal["procedures"]
        )


def _error_code(message: str) -> str:
    return re.sub(r"^Value error,\s*", "", message).strip()


class Assembler:
    def __init__(
        self,
        *,
        source_text: str,
        prepared_text: str,
        source_document_id: str,
        source_digest: str,
        extractor_version: str,
        collections: tuple[str, ...] = PROCEDURE_COLLECTIONS,
    ) -> None:
        self.text = source_text
        self.prepared = prepared_text
        self.document_id = source_document_id
        self.digest = source_digest
        self.extractor_version = extractor_version[:500]
        self.spec: ContractSpec = contract_spec(collections)
        self.collections = collections
        self.rows: dict[str, list[RowDraft]] = {name: [] for name in collections}
        self.by_id: dict[tuple[str, str], RowDraft] = {}
        self.unresolved: list[dict[str, Any]] = []
        self.stats: dict[str, int] = {}
        for name in (c.name for c in self.spec.collections if c.singleton):
            self._add_row(name, name, None)

    # -- ingestion ---------------------------------------------------------

    def _count(self, key: str, n: int = 1) -> None:
        self.stats[key] = self.stats.get(key, 0) + n

    def _note(self, kind: str, note: str, span: AnchoredSpan | None = None) -> None:
        item: dict[str, Any] = {"kind": kind, "note": note[:500]}
        if span is not None:
            item.update(start=span.start, end=span.end, excerpt=self.text[span.start : span.end])
        self.unresolved.append(item)

    def _anchor(self, quote: str, near: int | None = None) -> AnchoredSpan | None:
        span = anchor(self.prepared, quote, near=near)
        if span is None:
            return None
        # Excerpts come from the stored source, not the masked copy sent to the model.
        return AnchoredSpan(
            span.start, span.end, self.text[span.start : span.end], span.method, span.occurrences
        )

    def _add_row(self, collection: str, local_id: str, span: AnchoredSpan | None) -> RowDraft:
        row = RowDraft(collection, local_id, span)
        self.rows[collection].append(row)
        self.by_id[(collection, local_id)] = row
        return row

    def _singleton(self, collection: str) -> bool:
        return self.spec.collection(collection).singleton

    def _ingest_rows(self, rows: list[dict[str, Any]]) -> None:
        for item in rows:
            collection, local_id = item.get("collection"), str(item.get("local_id") or "").strip()
            if collection not in self.rows or self._singleton(collection) or not local_id:
                self._count("rows_rejected")
                continue
            if (collection, local_id) in self.by_id:
                self._count("rows_duplicate")
                continue
            span = self._anchor(item.get("anchor_quote") or "")
            row = self._add_row(collection, local_id, span)
            self._count("rows")
            allowed = self.spec.collection(collection).parents
            for parent in item.get("parents") or []:
                key, parent_id = parent.get("field"), str(parent.get("local_id") or "").strip()
                if key in allowed and parent_id:
                    row.parents[key] = parent_id

    def _row_for(self, local_id: str, collection: str) -> RowDraft | None:
        if self._singleton(collection):
            return self.by_id[(collection, collection)]
        row = self.by_id.get((collection, local_id))
        if row is None and local_id:
            self._count("rows_implicit")
            row = self._add_row(collection, local_id, None)
        return row

    def _ingest_fact(self, item: dict[str, Any]) -> None:
        path = item.get("field") or ""
        spec = self.spec.fields.get(path)
        if spec is None:
            self._count("facts_unknown_field")
            return
        self._count("facts")
        row = self._row_for(str(item.get("local_id") or "").strip(), spec.collection)
        if row is None:
            self._count("facts_unknown_row")
            return
        span = self._anchor(
            item.get("evidence_quote") or "", near=row.anchor.start if row.anchor else None
        )
        if span is None:
            self._count("facts_unanchored")
            self._note("unmapped_detail", f"unanchored evidence for {path}")
            return
        assertion = item.get("assertion")
        if assertion in DEFERRED_ASSERTIONS:
            self._count("facts_deferred")
            self._note(DEFERRED_ASSERTIONS[assertion], f"{path} = {item.get('value')!r}", span)
            return
        try:
            value = spec.coerce(item.get("value"))
        except FactValueError as exc:
            self._count("facts_invalid_value")
            self._note("unmapped_detail", str(exc), span)
            return
        if assertion == "negated" and path == DENIED_EVENT_FIELD and value != GENERIC_EVENT:
            # "No pneumothorax" names an event and denies it. The contract records that
            # as the category with state=absent, not as a negated category.
            if row.values.get("state") is None:
                row.values["state"] = Fact("absent", span, "negated")
                self._count("denied_events")
        elif assertion == "negated":
            if spec.kind == "bool":
                value = False
            elif spec.kind == "enum" and value in NEGATED_VALUES:
                value = NEGATED_VALUES[value]
            elif not (spec.kind == "enum" and value in STATED_NEGATIVES):
                self._count("facts_deferred")
                self._note("uncertain", f"negated {path} = {value!r}", span)
                return
        existing = row.values.get(spec.field)
        if existing is not None and existing.origin != "missing":
            if existing.value != value and not existing.conflict:
                existing.conflict = True
                existing.raw = json.dumps([existing.value, value])
                self._count("facts_conflicting")
            else:
                self._count("facts_duplicate")
            return
        row.values[spec.field] = Fact(value, span, assertion)
        self._count("facts_applied")

    def _ingest_missing(self, items: list[dict[str, Any]]) -> None:
        for item in items:
            spec = self.spec.fields.get(item.get("field") or "")
            if spec is None:
                continue
            row = self._row_for(str(item.get("local_id") or "").strip(), spec.collection)
            if row is None or spec.field in row.values:
                continue
            span = self._anchor(
                item.get("evidence_quote") or "", near=row.anchor.start if row.anchor else None
            )
            row.values[spec.field] = Fact(None, span, None, "missing", item.get("reason"))
            self._count("missing_explicit")

    def _ingest_unresolved(self, items: list[dict[str, Any]]) -> None:
        for item in items:
            self._note(
                item.get("kind") or "unmapped_detail",
                item.get("note") or "",
                self._anchor(item.get("evidence_quote") or ""),
            )

    # -- structural integrity ---------------------------------------------

    def _drop(self, row: RowDraft, reason: str) -> None:
        self.rows[row.collection].remove(row)
        del self.by_id[(row.collection, row.local_id)]
        self._count("rows_dropped")
        self._note(
            "unmapped_detail", f"{row.collection} {row.local_id} dropped: {reason}", row.anchor
        )

    def _prune(self) -> None:
        """Drop rows missing required fields or parents, cascading to their children."""
        changed = True
        while changed:
            changed = False
            for collection in self.collections:
                if self._singleton(collection):
                    continue
                for row in list(self.rows[collection]):
                    for key, parent_id in list(row.parents.items()):
                        if (
                            self.spec.collection(collection).parents[key],
                            parent_id,
                        ) not in self.by_id:
                            del row.parents[key]
                            self._count("parents_unresolved")
                    missing = [
                        f for f in self.spec.required.get(collection, ()) if row.value(f) is None
                    ]
                    missing += [
                        p
                        for p in self.spec.required_parents.get(collection, ())
                        if p not in row.parents
                    ]
                    if missing:
                        self._drop(row, "missing " + ", ".join(missing))
                        changed = True

    def _conflict(self, row: RowDraft, name: str) -> bool:
        fact = row.values.get(name)
        if fact is None or fact.value is None:
            return False
        fact.raw = fact.raw or json.dumps(fact.value)
        fact.value, fact.conflict, fact.missing_reason = None, True, "unknown"
        self._count("validator_conflicts")
        return True

    def _target_of(self, row: RowDraft) -> str | None:
        return row.parents.get("target_id")

    def _fix_link(self, code: str) -> bool:
        get = self.by_id.get
        if code == "inspected_station_cannot_have_sampling_results":
            for target in self.rows.get("targets", []):
                survey = get(("station_surveys", target.parents.get("station_survey_id", "")))
                if (
                    survey is not None
                    and survey.value("station_sampled") is False
                    and (
                        target.value("sampling_attempted") is True
                        or target.value("needle_pass_count")
                        or target.value("rose_result")
                    )
                ):
                    return self._conflict(survey, "station_sampled")
        if code == "target_station_context_mismatch":
            for target in self.rows.get("targets", []):
                survey = get(("station_surveys", target.parents.get("station_survey_id", "")))
                if survey is not None and (
                    survey.value("iaslc_station") != target.value("iaslc_station")
                    or (
                        "ebus_session_id" in target.parents
                        and survey.parents.get("ebus_session_id")
                        != target.parents["ebus_session_id"]
                    )
                ):
                    del target.parents["station_survey_id"]
                    self._note(
                        "conflicting_statements",
                        f"target {target.local_id} station differs from survey",
                        target.anchor,
                    )
                    return True
        if code == "navigation_localization_target_mismatch":
            for event in self.rows.get("localization_events", []):
                run = get(("navigation_runs", event.parents.get("navigation_run_id", "")))
                if run is not None and self._target_of(run) != self._target_of(event):
                    del event.parents["navigation_run_id"]
                    return True
        if code in {
            "sampling_localization_target_mismatch",
            "sampling_requires_reconfirmation_after_tool_change",
        }:
            for acquisition in self.rows.get("sampling_acquisitions", []):
                event = get(
                    (
                        "localization_events",
                        acquisition.parents.get("localization_event_id_before_pass", ""),
                    )
                )
                if event is not None and (
                    self._target_of(event) != self._target_of(acquisition)
                    or event.value("catheter_or_tool_changed_after_confirmation") is True
                ):
                    del acquisition.parents["localization_event_id_before_pass"]
                    self._note(
                        "conflicting_statements",
                        f"acquisition {acquisition.local_id} confirmation link removed: {code}",
                        acquisition.anchor,
                    )
                    return True
        if code == "sampling_specimen_target_mismatch":
            for link in self.rows.get("sampling_specimen_links", []):
                if link.value("link_certainty") == "confirmed":
                    acquisition = get(("sampling_acquisitions", link.parents["sampling_pass_id"]))
                    specimen = get(("specimens", link.parents["specimen_id"]))
                    if (
                        acquisition is not None
                        and specimen is not None
                        and self._attribution(specimen, "target_attribution_status") == "attributed"
                        and self._target_of(acquisition) != self._target_of(specimen)
                    ):
                        link.values["link_certainty"] = Fact(
                            "uncertain", link.values["link_certainty"].span, origin="derived"
                        )
                        return True
        if code == "duplicate_procedure_component":
            seen = set()
            for row in self.rows.get("procedures", []):
                if row.value("category") in seen:
                    self._drop(row, "duplicate procedure component")
                    return True
                seen.add(row.value("category"))
        component = {
            "robotic_navigation_requires_robotic_component": ("navigation_runs",),
            "navigation_requires_started_robotic_component": ("navigation_runs",),
            "ebus_session_requires_linear_component": ("ebus_sessions", "station_surveys"),
            "station_survey_requires_started_linear_component": (
                "ebus_sessions",
                "station_surveys",
            ),
        }.get(code)
        if component:
            for collection in component:
                for row in list(self.rows.get(collection, [])):
                    self._drop(row, code)
            self._prune()
            return True
        return False

    # -- rendering ---------------------------------------------------------

    def _attribution(self, row: RowDraft, name: str) -> str | None:
        explicit = row.value(name)
        if explicit is not None or row.values.get(name) is not None:
            return explicit
        return "attributed" if "target_id" in row.parents else None

    def _uuid(self, collection: str, local_id: str) -> str:
        return stable_id(self.digest, f"anthropic:{collection}:{local_id}")

    def _provenance(self, path: str, fact: Fact) -> dict[str, Any]:
        entry: dict[str, Any] = {
            "field_path": path,
            "value_origin": fact.origin,
            "extractor_model_version": self.extractor_version,
            "conflict_status": "unresolved" if fact.conflict else "none",
        }
        if fact.span is not None:
            entry.update(
                source_document_id=self.document_id,
                source_digest=self.digest,
                source_start=fact.span.start,
                source_end=fact.span.end,
                source_excerpt=fact.span.excerpt,
                raw_value=fact.raw if fact.raw is not None else fact.span.excerpt,
            )
        elif fact.raw is not None:
            entry["raw_value"] = fact.raw
        if fact.origin == "extracted":
            entry["assertion_context"] = fact.assertion or "active"
        if fact.value is None:
            entry["missingness_reason"] = fact.missing_reason or "unknown"
        if fact.origin == "derived":
            entry["derivation_rule_version"] = self.extractor_version
        return entry

    def render(self) -> tuple[dict[str, Any], dict[tuple[str, int], RowDraft]]:
        proposal: dict[str, Any] = {
            "schema_version": VERSION,
            "registry_profile": PROFILE,
            "procedures": [],
            **{key: {} if key == "case_details" else [] for key in ENTITY_MODELS},
        }
        provenance: list[dict[str, Any]] = []
        index_map: dict[tuple[str, int], RowDraft] = {}
        sequences: dict[tuple[str, str | None], int] = {}

        def emit(prefix: str, target: dict[str, Any], name: str, fact: Fact) -> None:
            if fact.value is not None:
                target[name] = fact.value
            provenance.append(self._provenance(f"{prefix}/{name}", fact))

        for collection in self.collections:
            if collection == SINGLETON_REVISION:
                for name, fact in self.rows[collection][0].values.items():
                    emit("", proposal, name, fact)
                continue
            if collection == "case_details":
                for name, fact in self.rows[collection][0].values.items():
                    emit("/case_details", proposal["case_details"], name, fact)
                continue
            for index, row in enumerate(self.rows[collection]):
                index_map[(collection, index)] = row
                prefix, data = f"/{collection}/{index}", {}
                proposal[collection].append(data)
                derived = lambda value: Fact(value, row.anchor, None, "derived")  # noqa: E731
                if collection in PRIMARY_KEYS:
                    emit(
                        prefix,
                        data,
                        PRIMARY_KEYS[collection],
                        derived(self._uuid(collection, row.local_id)),
                    )
                for key, parent_id in row.parents.items():
                    parent = self.spec.collection(collection).parents[key]
                    emit(prefix, data, key, derived(self._uuid(parent, parent_id)))
                sequence = SEQUENCE_FIELDS.get(collection)
                if sequence and (
                    collection != "sampling_acquisitions"
                    or row.value("acquisition_record_granularity") == "single_pass"
                ):
                    slot = (collection, self._target_of(row))
                    sequences[slot] = sequences.get(slot, 0) + 1
                    emit(prefix, data, sequence, derived(sequences[slot]))
                for name in ("attribution_status", "target_attribution_status"):
                    if (
                        collection in {"sampling_acquisitions", "specimens"}
                        and name in ENTITY_MODELS[collection].model_fields
                    ):
                        if (
                            row.values.get(name) is None
                            and self._attribution(row, name) == "attributed"
                        ):
                            emit(prefix, data, name, derived("attributed"))
                for name, fact in row.values.items():
                    emit(prefix, data, name, fact)
        proposal["field_provenance"] = provenance
        return proposal, index_map

    # -- validation --------------------------------------------------------

    def _validate(self) -> tuple[ClinicalRevision | None, list[str]]:
        errors: list[str] = []
        for _ in range(MAX_REPAIR_PASSES):
            proposal, index_map = self.render()
            if not proposal["procedures"]:
                return None, ["no_procedure_component"]
            try:
                revision = ClinicalRevision.model_validate(
                    {**proposal, "event_date": VALIDATION_EVENT_DATE}
                )
                return revision, []
            except ValidationError as exc:
                fixed, errors = False, []
                for err in exc.errors():
                    code, loc = _error_code(err["msg"]), err["loc"]
                    errors.append(code)
                    if len(loc) >= 2 and (loc[0], loc[1]) in index_map:
                        row = index_map[(loc[0], loc[1])]
                        if len(loc) >= 3 and isinstance(loc[2], str) and loc[2] in row.values:
                            fixed = self._conflict(row, loc[2]) or fixed
                        elif code in ROW_TRIPS:
                            fixed = (
                                any([self._conflict(row, name) for name in ROW_TRIPS[code]])
                                or fixed
                            )
                        else:
                            self._drop(row, code)
                            self._prune()
                            fixed = True
                    elif (
                        loc
                        and loc[0] == "case_details"
                        and len(loc) >= 2
                        and isinstance(loc[1], str)
                    ):
                        fixed = self._conflict(self.rows["case_details"][0], loc[1]) or fixed
                    elif not loc:
                        fixed = self._fix_link(code)
                        if fixed:
                            self._prune()
                        break
                if not fixed:
                    return None, errors
        return None, errors or ["repair_passes_exhausted"]

    def assemble(self, facts: dict[str, Any]) -> Assembly:
        self._ingest_rows(facts.get("rows") or [])
        for array in sorted(set(FACT_ARRAYS.values())):
            for item in facts.get(array) or []:
                self._ingest_fact(item)
        self._ingest_missing(facts.get("missing_facts") or [])
        self._ingest_unresolved(facts.get("unresolved") or [])
        self._prune()
        revision, errors = self._validate()
        proposal, _ = self.render()
        for item in proposal["field_provenance"]:
            if (
                "source_start" in item
                and self.text[item["source_start"] : item["source_end"]] != item["source_excerpt"]
            ):
                raise ValueError("proposal_evidence_mismatch")
        return Assembly(
            proposal=proposal,
            unresolved=self.unresolved,
            stats=self.stats,
            errors=errors,
            approval_errors=approval_errors(revision) if revision is not None else [],
        )


def assemble(facts: dict[str, Any], **kwargs: Any) -> Assembly:
    return Assembler(**kwargs).assemble(facts)


__all__ = ["Assembler", "Assembly", "VALIDATION_EVENT_DATE", "assemble"]
