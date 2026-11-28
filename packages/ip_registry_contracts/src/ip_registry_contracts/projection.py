"""Explicit hospital-to-national projection. No clinical dictionary is copied wholesale."""

from .launch import NATIONAL_ENTITY_FIELDS, PROFILE, VERSION
from .models import NationalRegistryRecord, approval_errors

ID_NAMESPACES = {
    "target_id": "target",
    "target_identity_id": "target_identity",
    "ebus_session_id": "ebus_session",
    "station_survey_id": "station_survey",
    "navigation_run_id": "navigation_run",
    "localization_event_id": "localization_event",
    "localization_event_id_before_pass": "localization_event",
    "sampling_pass_id": "sampling_pass",
    "specimen_id": "specimen",
    "sampling_specimen_link_id": "sampling_specimen_link",
    "pathology_result_id": "pathology_result",
    "supersedes_pathology_result_id": "pathology_result",
    "adverse_event_id": "adverse_event",
}


def project_national(
    revision,
    *,
    remap,
    patient_id,
    procedure_id,
    revision_number,
    facility_id,
    age_band,
    profile_id,
    profile_version,
):
    errors = approval_errors(revision)
    if errors:
        raise ValueError(",".join(errors))
    entities = {}
    for name, fields in NATIONAL_ENTITY_FIELDS.items():
        value = getattr(revision, name)
        rows = [value] if name == "case_details" else value
        projected = []
        for row in rows:
            out = {}
            for field in fields:
                value = getattr(row, field)
                out[field] = (
                    remap(ID_NAMESPACES[field], str(value))
                    if field in ID_NAMESPACES and value is not None
                    else value
                )
            projected.append(out)
        entities[name] = projected[0] if name == "case_details" else projected
    unresolved = any(s.target_attribution_status != "attributed" for s in revision.specimens)
    complete_windows = {f.window for f in revision.follow_up if f.complete}
    quality = (
        "requires_reconciliation"
        if unresolved
        else ("complete" if complete_windows == {"days_0_7", "days_8_30"} else "incomplete")
    )
    return NationalRegistryRecord(
        schema_version=VERSION,
        registry_profile=PROFILE,
        measure_version=VERSION,
        patient_export_id=remap("patient", str(patient_id)),
        procedure_export_id=remap("procedure", str(procedure_id)),
        revision=revision_number,
        facility_id=facility_id,
        procedure_year=revision.event_date.year,
        age_band=age_band,
        deidentification_profile_id=profile_id,
        deidentification_profile_version=profile_version,
        quality=quality,
        complication_assessment=revision.complication_assessment,
        procedures=[
            {
                field: getattr(p, field)
                for field in ("category", "performance", "planned", "completion")
            }
            for p in revision.procedures
        ],
        **entities,
    )


def analysis_tables(records):
    """Export normalized entities from validated immutable revisions, with no inferred rows.

    Caller owns authorization and chooses clinical or national records. Never use a
    clinical table export as a national projection.
    """
    tables = {"cases": [], "procedures": [], **{name: [] for name in NATIONAL_ENTITY_FIELDS}}
    for record_id, revision in records:
        case = {
            "record_id": str(record_id),
            "schema_version": revision.schema_version,
            "registry_profile": revision.registry_profile,
            "complication_assessment": str(revision.complication_assessment),
        }
        if hasattr(revision, "procedure_year"):
            case["procedure_year"] = revision.procedure_year
        else:
            case["event_date"] = revision.event_date.isoformat()
        tables["cases"].append(case)
        for name in ("procedures", *NATIONAL_ENTITY_FIELDS):
            value = getattr(revision, name)
            rows = [value] if name == "case_details" else value
            for row in rows:
                tables[name].append({"record_id": str(record_id), **row.model_dump(mode="json")})
    return {"schema_version": VERSION, "registry_profile": PROFILE, "tables": tables}
