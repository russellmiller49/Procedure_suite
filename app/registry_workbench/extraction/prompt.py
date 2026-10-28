"""System prompt generated from the launch dictionary.

Field definitions, allowed values, units and dictionary QA rules come from
``launch_dictionary.json``; only entity summaries and the answer mechanics are
written here. Output is deterministic (no timestamps, stable ordering) so the
prompt cache prefix stays byte-identical across requests.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache

from app.registry_workbench.extraction.contract_spec import (
    PROCEDURE_COLLECTIONS,
    SINGLETON_REVISION,
    contract_spec,
    dictionary,
    dictionary_fields,
)

PROMPT_VERSION = "robotic_ebus_v1-claude-1"

ENTITY_SUMMARIES = {
    "procedures": "Procedure components of this encounter: at most one robotic_bronchoscopy and one linear_ebus row.",
    "case_details": "Patient and case context for this encounter.",
    "targets": "Each lesion or lymph node that was a target: lung lesions (site lung) and sampled or targeted nodes (site lymph_node, with iaslc_station).",
    "ebus_sessions": "One row per linear EBUS examination.",
    "station_surveys": "One row per IASLC station examined during an EBUS session, whether or not it was sampled.",
    "navigation_runs": "Each robotic navigation attempt to a lung target, in order.",
    "localization_events": "Each confirmation or localization step for a target (radial EBUS, CBCT, tomosynthesis, fluoroscopy), in order.",
    "sampling_acquisitions": "Tissue acquisition by tool and target: one aggregate row per tool when passes are only counted, single-pass rows only when each pass is described.",
    "specimens": "Specimens as labeled or described in the note (for example containers A and B).",
    "sampling_specimen_links": "Which acquisition produced which specimen.",
    "complications": "Each complication category the note addresses for this procedure.",
    SINGLETON_REVISION: "Whether the note documents a procedural complication assessment.",
}

# Dictionary QA rules that govern abstraction from a procedure note. Every rule
# in the dictionary is either here or in EXCLUDED_QA_RULES (tested).
PROMPT_QA_RULES = (
    "Q003", "Q006", "Q007", "Q008", "Q010", "Q011", "Q012", "Q013", "Q014", "Q018",
    "Q019", "Q020", "Q021", "Q023", "Q024", "Q026", "Q034", "Q039", "Q041",
)
EXCLUDED_QA_RULES = {
    "Q001": "database key integrity, enforced by the assembler",
    "Q002": "cross-patient linkage, enforced by the assembler",
    "Q004": "baseline risk-factor timing, not in the launch contract",
    "Q005": "operator case counts, not in the launch contract",
    "Q009": "staging assessment, roadmap",
    "Q015": "yield measure, computed in measures.py",
    "Q016": "yield measure, computed in measures.py",
    "Q017": "registration error, not in the launch contract",
    "Q022": "biomarkers, roadmap",
    "Q025": "follow-up ascertainment, not a procedure-note field",
    "Q027": "reference standard, roadmap",
    "Q028": "reference standard, roadmap",
    "Q029": "reference standard, roadmap",
    "Q030": "radiation exposure, roadmap",
    "Q031": "radiation exposure, roadmap",
    "Q032": "measurement metadata, enforced by contract units",
    "Q033": "workflow timestamps, not in the launch contract",
    "Q035": "provenance completeness, enforced by the assembler",
    "Q036": "source versioning, enforced by the workbench",
    "Q037": "analytic export, not extraction",
    "Q038": "deployment governance",
    "Q040": "analysis independence",
    "Q042": "research long-axis fields, roadmap",
}

ANSWER_MECHANICS = """\
How the answer is organized:
- rows: one per registry row the document supports, for every collection except case_details and revision. Give each row a short local_id that is unique within the answer (for example T1, ES1, S7, N1, L1, A1, SP1, C1). parents links a row to the rows it belongs to, by foreign-key field name and the parent's local_id. anchor_quote is a short verbatim phrase that introduces the row.
- case_details and revision are single records. Their facts use local_id "case_details" or "revision" and need no row.
- Each fact carries one supported value. evidence_quote is copied character for character from the document: the shortest phrase that states the value, with no ellipses, paraphrase or added words.
- assertion: active = done or present in this procedure; negated = explicitly not done or absent; planned = intended or scheduled; historical = a prior procedure or past history; uncertain = hedged. Only active and negated facts enter the registry; the others are kept for review.
- missing_facts: only where the document explicitly says a value is unknown, not done, not applicable, pending, failed, declined or unavailable. Silence is not a missing fact; leave the field out.
- unresolved: registry-relevant statements that fit no field, statements that conflict with each other, and procedures outside robotic bronchoscopy and linear EBUS.
- Leave out anything the document does not state. A tool, platform name, order set or template heading alone does not establish that something was done, and lines that only list billing codes are not evidence.
"""

RECORDING_RULES = """\
Recording rules:
- A station that was examined gets a station_surveys row with parent ebus_session_id. station_surveyed, station_visualized and station_sampled are separate facts; a station that was looked at but not punctured has station_sampled false and carries no needle passes, gauge or ROSE.
- A sampled station also gets a targets row (site lymph_node, iaslc_station equal to the survey's station) with parents station_survey_id and ebus_session_id; needle passes, gauge and ROSE for that node go on that target row.
- short_axis_mm and largest_short_axis_mm are recorded only when the document explicitly says the measurement is the short axis by EBUS or EUS-B; record size_axis_explicit true and the modality with it. A bare node size or a CT size is not a short axis.
- tool_lesion_relationship TIL requires cone-beam CT, tomosynthesis or CT showing the actual sampling tool inside the actual lesion: record the modality, actual_lesion_vs_virtual_target actual_lesion, sampling_tool_present true, verified_tool_component (sampling_tool, needle_tip, forceps or cryoprobe) and confirmation_basis (volumetric_imaging or tomosynthesis). Without all of these use touching, adjacent or indeterminate. A radial EBUS view is radial_ebus_view, not TIL.
- Passes counted without per-pass detail are one sampling_acquisitions row per tool and target with acquisition_record_granularity aggregate_reported and reported_pass_count. Use single_pass rows only when each pass is individually documented, and never both for the same tool and target.
- An acquisition's parent target_id is the target it sampled; localization_event_id_before_pass is the confirmation step that immediately preceded it.
- A specimen-to-acquisition link is confirmed only when the note states the mapping; otherwise it is uncertain.
- ROSE results stay in the rose fields; they are never final pathology.
- complication_assessment is present when the note documents a procedural complication and absent when it states there were none. Each addressed complication category gets a complications row with its state.
"""


@lru_cache(maxsize=None)
def _qa_rules() -> dict[str, dict[str, str]]:
    return {rule["Rule ID"]: rule for rule in dictionary()["qa_rules"]}


def _field_line(path: str) -> str:
    spec = contract_spec().fields[path]
    entry = dictionary_fields().get(path, {})
    parts = [f"- {path}"]
    if spec.kind == "enum":
        parts.append(f"(one of: {', '.join(spec.values)})")
    elif spec.kind == "integer":
        parts.append("(whole number)")
    elif spec.kind == "number":
        parts.append("(number)")
    elif spec.kind == "bool":
        parts.append("(true/false)")
    else:
        parts.append("(text)")
    definition = (entry.get("definition") or "").strip()
    if definition:
        parts.append(definition.rstrip(".") + ".")
    units = entry.get("contract_units")
    if units:
        parts.append(f"Units: {units}.")
    when = (entry.get("required_when") or "").strip()
    if when and when.lower() != "when this module applies":
        parts.append(f"Applies: {when.rstrip('.')}.")
    notes = (entry.get("validation_notes") or "").strip()
    if notes:
        parts.append(f"Note: {notes.rstrip('.')}.")
    return " ".join(parts)


@lru_cache(maxsize=None)
def system_prompt(collections: tuple[str, ...] = PROCEDURE_COLLECTIONS) -> str:
    spec = contract_spec(collections)
    sections = [
        "You abstract one source document into the robotic_ebus_v1 registry (contract 0.2.0) "
        "for robotic bronchoscopy and linear EBUS. The documents are synthetic notes. "
        "Values never default to no or zero: anything undocumented is left out.",
        ANSWER_MECHANICS,
        RECORDING_RULES,
        "Dictionary QA rules:\n"
        + "\n".join(
            f"- {rule_id}: {_qa_rules()[rule_id]['Condition / check'].strip()}" for rule_id in PROMPT_QA_RULES
        ),
    ]
    for collection in spec.collections:
        lines = [f"## {collection.name}: {ENTITY_SUMMARIES[collection.name]}"]
        if collection.parents:
            lines.append(
                "Parents: "
                + ", ".join(f"{key} -> {parent}" for key, parent in sorted(collection.parents.items()))
            )
        required = spec.required.get(collection.name, ())
        if required:
            lines.append("Required on every row: " + ", ".join(required))
        lines += [_field_line(field.path) for field in collection.fields]
        sections.append("\n".join(lines))
    return "\n\n".join(sections) + "\n"


def user_message(text: str, *, kind: str = "procedure") -> str:
    return f"Abstract this {kind} document.\n\n<document>\n{text}\n</document>"


def prompt_digest(collections: tuple[str, ...] = PROCEDURE_COLLECTIONS) -> str:
    return hashlib.sha256((PROMPT_VERSION + system_prompt(collections)).encode()).hexdigest()


__all__ = [
    "ENTITY_SUMMARIES",
    "EXCLUDED_QA_RULES",
    "PROMPT_QA_RULES",
    "PROMPT_VERSION",
    "prompt_digest",
    "system_prompt",
    "user_message",
]
