#!/usr/bin/env python3
# ruff: noqa: E402 -- Bootstrap the isolated package without installing the development application.
"""Freeze the launch selection against the supplied workbook without editing it."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/ip_registry_contracts/src"))
from ip_registry_contracts.launch import ENTITY_MODELS, NATIONAL_ENTITY_FIELDS, FieldProvenance
from ip_registry_contracts.models import ClinicalRevision, ProcedureEvent

TABLES = {
    "case_details": [
        "procedure",
        "procedure_baseline",
        "patient",
        "anesthesia_summary",
        "airway_event",
        "procedure_personnel",
    ],
    "targets": ["peripheral_lesion", "nodal_target", "target_identity"],
    "ebus_sessions": ["ebus_session"],
    "station_surveys": ["ebus_station_survey"],
    "navigation_runs": ["navigation_run"],
    "localization_events": ["localization_event"],
    "sampling_acquisitions": ["sampling_pass", "device_use"],
    "specimens": ["specimen"],
    "sampling_specimen_links": ["sampling_specimen_link"],
    "pathology_results": ["pathology_result"],
    "complications": ["adverse_event", "anesthesia_summary"],
    "follow_up": ["followup_contact"],
    "procedures": ["procedure"],
    "field_provenance": ["field_provenance", "source_document"],
}
ALIASES = {
    "procedures.category": "procedure.performed_modalities",
    "procedures.performance": "procedure.performed_modalities",
    "procedures.planned": "procedure.planned_modalities",
    "procedures.completion": "procedure.procedure_status",
    "procedures.abort_reason": "procedure.procedure_abort_reason",
    "case_details.indication": "clinical_pathway.primary_indication",
    "case_details.intent": "procedure.combined_diagnosis_and_staging",
    "case_details.anesthesia_type": "anesthesia_summary.actual_anesthesia_type",
    "case_details.airway_size_value": "airway_event.device_size_value",
    "case_details.airway_size_unit": "airway_event.device_size_unit",
    "case_details.procedure_duration_minutes": "procedure.bronchoscope_in_datetime",
    "targets.target_id": "target_identity.target_identity_id",
    "targets.site": "target_identity.anatomic_target_kind",
    "targets.diagnostic_attempted": "peripheral_lesion.prespecified_biopsy_target",
    "targets.rose_adequate": "nodal_target.target_specimen_adequate",
    "targets.rose_result": "sampling_pass.rose_result",
    "targets.pet_description": "peripheral_lesion.pet_avid",
    "targets.size_axis_explicit": "nodal_target.short_axis_mm",
    "targets.pet_suv_max": "peripheral_lesion.suvmax",
    "targets.measurement_modality": "nodal_target.short_axis_mm",
    "targets.needle_gauge": "sampling_pass.needle_gauge",
    "station_surveys.size_axis_explicit": "ebus_station_survey.largest_short_axis_mm",
    "navigation_runs.target_id": "navigation_run.lesion_id",
    "localization_events.target_id": "localization_event.lesion_id",
    "sampling_acquisitions.attribution_status": "specimen.target_attribution_status",
    "sampling_acquisitions.tool_size_mm": "device_use.device_size_or_gauge",
    "sampling_acquisitions.rose_adequate": "nodal_target.target_specimen_adequate",
    "specimens.pathology": "pathology_result.index_result_class",
    "specimens.intended_purpose": "sampling_pass.intended_specimen_purpose",
    "pathology_results.source_document_id": "source_document.source_document_id",
    "complications.category": "adverse_event.event_type",
    "complications.state": "followup_contact.interval_procedure_related_event",
    "complications.relative_day_offset": "adverse_event.event_onset_datetime",
    "complications.unplanned_ventilation": "anesthesia_summary.unplanned_postprocedure_ventilation",
    "follow_up.window": "followup_contact.planned_timepoint",
    "follow_up.complete": "followup_contact.contact_completed",
    "follow_up.alive": "followup_contact.vital_status",
    "follow_up.unplanned_admission": "followup_contact.interval_hospitalization",
    "follow_up.ed_visit": "followup_contact.interval_ed_visit",
    "follow_up.icu_admission": "adverse_event.new_icu_admission",
    "follow_up.unplanned_ventilation": "anesthesia_summary.unplanned_postprocedure_ventilation",
    "follow_up.procedure_related_event": "followup_contact.interval_procedure_related_event",
    "field_provenance.field_path": "field_provenance.field_name",
    "field_provenance.source_digest": "source_document.content_hash",
    "field_provenance.source_start": "field_provenance.source_locator",
    "field_provenance.source_end": "field_provenance.source_locator",
}
ADAPTATIONS = {
    "case_details.intent": "Coded purpose of this component/case: diagnosis, staging, combined diagnosis/staging, restaging or molecular rebiopsy. Do not infer from billing codes.",
    "case_details.procedure_duration_minutes": "Documented total procedure duration in minutes; if calculated, use documented bronchoscope-in and final bronchoscope-out times and retain the derivation. An isolated timestamp is insufficient.",
    "targets.target_id": "Encounter-local target row ID. Station identity and individual-node or longitudinal target identity remain separate.",
    "targets.diagnostic_attempted": "Navigation, localization or sampling started for this prespecified biopsy target. Planned-only targets and docking without a diagnostic attempt do not establish this flag; failures remain attempts.",
    "targets.size_axis_explicit": "True only when ultrasound measurement is explicitly identified as short axis in the source. Unspecified or long-axis measurements do not populate short_axis_mm.",
    "targets.measurement_modality": "Documented ultrasound route of the explicit short-axis measurement. A CT or unspecified measurement cannot be substituted.",
    "targets.rose_adequate": "Adequacy explicitly documented at rapid on-site evaluation for this target. Final specimen adequacy does not establish ROSE adequacy.",
    "sampling_acquisitions.rose_adequate": "Adequacy explicitly documented at ROSE for this acquisition. Keep separate from final pathology adequacy.",
    "targets.pet_description": "Original documented PET assessment. No PET result is inferred from a planned study or from the lesion diagnosis.",
    "station_surveys.size_axis_explicit": "Whether the largest ultrasound size is explicitly documented as short axis, without inferring an axis from one or two unlabeled measurements.",
    "specimens.pathology": "Optional compatibility summary only. Target diagnostic measures use attributed, non-superseded final/amended pathology_results with explicit index scope.",
    "complications.state": "Presence, explicit absence, uncertainty or missing documentation of the named immediate/interval event. Absence must be documented for the applicable event/window.",
    "complications.relative_day_offset": "Documented or locally derived day offset from the procedure, limited to days 0–30. Missing timing remains null; do not default to day zero.",
    "follow_up.window": "Assessment interval: days 0–7 or days 8–30. This records the interval assessed, not simply the day a follow-up note was authored.",
    "follow_up.complete": "Explicitly completed ascertainment for the entire selected interval. A contact alone does not establish complete ascertainment or negative outcomes.",
    "procedures.category": "Launch component: diagnostic robotic bronchoscopy or transbronchial linear EBUS. Generic peripheral navigation, standalone radial EBUS/EUS-B and robotic ablation are not relabeled as eligible components.",
    "procedures.performance": "Documented component action state, with started attempts retained even when unsuccessful or aborted. Unknown eligibility requires review.",
    "procedures.completion": "Completion of the named component, recorded independently from whether it was attempted/performed.",
    "field_provenance.source_start": "Zero-based character offset in the exact immutable source text; inclusive start. Paired with exclusive end, source ID, SHA-256 and verbatim excerpt.",
    "field_provenance.source_end": "Zero-based exclusive end in the exact immutable source text. Whitespace is retained so excerpt and offsets agree.",
}


def build(source, output):
    from openpyxl import load_workbook

    book = load_workbook(source, read_only=True, data_only=False)
    rows = list(book["Data_Dictionary"].values)
    headers = rows[0]
    master = {
        f"{r[0]}.{r[1]}": {**dict(zip(headers, r)), "source_row": i}
        for i, r in enumerate(rows[1:], 2)
        if len(r) > 1 and r[1]
    }
    selected, used = [], set()
    models = {**ENTITY_MODELS, "procedures": ProcedureEvent, "field_provenance": FieldProvenance}
    for collection, model in models.items():
        schema = model.model_json_schema()
        for field, info in model.model_fields.items():
            path = collection + "." + field
            candidates = [TABLES[collection][0] + "." + field]
            candidates += [table + "." + field for table in TABLES[collection]]
            candidates += [k for k in master if k.endswith("." + field)]
            if path in ALIASES:
                candidates.insert(0, ALIASES[path])
            matched = next((k for k in candidates if k in master), None)
            reference = master.get(matched, {})
            if matched:
                used.add(matched)
            selected.append(
                {
                    "contract_path": path,
                    "entity": collection,
                    "field": field,
                    "dictionary_key": matched,
                    "source_sheet": "Data_Dictionary",
                    "source_row": reference.get("source_row"),
                    "mapping": "direct"
                    if matched and matched.rsplit(".", 1)[1] == field
                    else "adapted"
                    if matched
                    else "implementation_extension",
                    "definition": ADAPTATIONS.get(
                        path, reference.get("Definition / capture instruction")
                    )
                    or "Launch contract metadata; see the typed contract and validation rules.",
                    "source_definition": reference.get("Definition / capture instruction"),
                    "source_type": reference.get("Data type"),
                    "source_allowed_values_units": reference.get("Allowed values / units"),
                    "contract_schema": schema["properties"][field],
                    "contract_units": "minutes"
                    if field.endswith("_minutes")
                    else "mm"
                    if field.endswith("_mm")
                    else "years"
                    if field.endswith("_years")
                    else "day_offset"
                    if field == "relative_day_offset"
                    else "count"
                    if field.endswith("_count")
                    else None,
                    "required_when": reference.get("Required when"),
                    "preferred_source": reference.get("Preferred source"),
                    "capture_method": reference.get("Capture method"),
                    "missingness_policy": reference.get("Missingness policy")
                    or "Null with an explicit missingness reason; never infer a negative.",
                    "validation_notes": reference.get("Validation / notes"),
                    "clinical_destination": "encrypted_revision." + path,
                    "national_destination": path
                    if field in NATIONAL_ENTITY_FIELDS.get(collection, ())
                    or (collection == "procedures" and field != "abort_reason")
                    else None,
                    "source_url": reference.get("Source URL"),
                    "collection_tier": reference.get("Collection tier"),
                    "review_status": "selected_by_launch_plan",
                }
            )
    bindings = [
        {
            "contract_path": path,
            "dictionary_key": key,
            "source_row": master[key]["source_row"],
            "definition": master[key]["Definition / capture instruction"],
            "clinical_destination": destination,
            "national_destination": national,
        }
        for path, key, destination, national in [
            (
                "context.patient_id",
                "patient.patient_id",
                "patient_scoped_context",
                "patient_export_id",
            ),
            (
                "context.procedure_id",
                "procedure.procedure_id",
                "procedure.id",
                "procedure_export_id",
            ),
            (
                "context.site_id",
                "registry_case.site_id",
                "authenticated_site_context",
                "facility_id",
            ),
            ("context.case_id", "registry_case.case_id", "procedure.id", "procedure_export_id"),
            (
                "event_date",
                "procedure.procedure_datetime",
                "encrypted_revision.event_date",
                "procedure_year",
            ),
        ]
    ]
    used.update(b["dictionary_key"] for b in bindings)
    document = {
        "schema_version": "0.2.0",
        "registry_profile": "robotic_ebus_v1",
        "source_workbook": source.name,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "clinical_qualification": "pending",
        "fields": selected,
        "context_bindings": bindings,
        "roadmap": [dict(dictionary_key=k, **v) for k, v in master.items() if k not in used],
        "clinical_schema": ClinicalRevision.model_json_schema(),
        "qa_rules": [
            dict(zip(next(iter(book["QA_Rules"].values)), row))
            for row in list(book["QA_Rules"].values)[1:]
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "launch_contract_fields": len(selected),
                "source_fields_selected": len(used),
                "roadmap_fields": len(document["roadmap"]),
                "implementation_extensions": [
                    r["contract_path"]
                    for r in selected
                    if r["mapping"] == "implementation_extension"
                ],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/knowledge/robotic_ebus_v1/launch_dictionary.json",
    )
    args = parser.parse_args()
    build(args.source, args.output)
