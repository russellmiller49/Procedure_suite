from __future__ import annotations

import json

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.ner_mapping.entity_to_registry import NERToRegistryMapper
from app.registry.schema import RegistryRecord
from app.reporting.engine import (
    ReporterEngine,
    _load_procedure_order,
    build_procedure_bundle_from_extraction,
    default_schema_registry,
    default_template_registry,
)
from app.reporting.llm_findings import (
    FindingV1,
    ReporterFindingsV1,
    build_synthetic_ner_result,
    seed_registry_record_from_llm_findings,
    validate_findings_against_text,
)


def test_validate_findings_against_text_drops_missing_or_weak_evidence() -> None:
    text = "A procedure was performed today.\nBAL performed in RUL."
    findings = ReporterFindingsV1(
        findings=[
            FindingV1(
                procedure_key="bal",
                action="diagnostic",
                finding_text="BAL performed in RUL",
                evidence_quote="BAL performed in RUL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                action="diagnostic",
                finding_text="31624 BAL performed in RUL",
                evidence_quote="BAL performed in RUL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                action="diagnostic",
                finding_text="BAL performed",
                evidence_quote="BAL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="not_a_proc",
                action="diagnostic",
                finding_text="BAL performed in RUL",
                evidence_quote="BAL performed in RUL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                action="diagnostic",
                finding_text="BAL performed",
                evidence_quote="NOT PRESENT IN TEXT",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                action="diagnostic",
                finding_text="Procedure performed",
                evidence_quote="performed today",
                confidence=0.9,
            ),
        ]
    )

    accepted, warnings = validate_findings_against_text(findings, masked_prompt_text=text, min_evidence_len=10)

    assert len(accepted) == 1
    assert accepted[0].evidence_quote == "BAL performed in RUL"

    warn_text = "\n".join(warnings)
    assert "contains_cpt_code" in warn_text
    assert "evidence_too_short" in warn_text
    assert "invalid_procedure_key" in warn_text
    assert "missing_evidence_quote" in warn_text
    assert "keyword_missing" in warn_text


def test_validate_findings_against_text_requires_aspiration_action_intent() -> None:
    text = "\n".join(
        [
            "Mucus plugs cleared RB4, RB5, LB4, LB5.",
            "Airways inspected and stent in good position.",
        ]
    )
    findings = ReporterFindingsV1(
        findings=[
            FindingV1(
                procedure_key="therapeutic_aspiration",
                action="aspiration",
                finding_text="Therapeutic aspiration performed to clear mucus plugs",
                evidence_quote="Mucus plugs cleared RB4, RB5, LB4, LB5.",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="therapeutic_aspiration",
                action="aspiration",
                finding_text="Therapeutic aspiration performed",
                evidence_quote="Airways inspected and stent in good position.",
                confidence=0.9,
            ),
        ]
    )

    accepted, warnings = validate_findings_against_text(findings, masked_prompt_text=text, min_evidence_len=10)

    assert len(accepted) == 1
    assert accepted[0].evidence_quote == "Mucus plugs cleared RB4, RB5, LB4, LB5."
    assert any("missing_action_intent" in warning for warning in warnings)


def test_findings_to_synthetic_ner_to_registry_flags() -> None:
    text = "\n".join(
        [
            "EBUS TBNA biopsied station 7",
            "BAL performed with return sent for cytology",
            "Transbronchial biopsy performed in LLL",
        ]
    )

    findings = ReporterFindingsV1(
        findings=[
            FindingV1(
                procedure_key="linear_ebus",
                action="diagnostic",
                finding_text="EBUS TBNA biopsied station 7",
                evidence_quote="EBUS TBNA biopsied station 7",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                action="diagnostic",
                finding_text="BAL performed",
                evidence_quote="BAL performed with return sent for cytology",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="transbronchial_biopsy",
                action="diagnostic",
                finding_text="Transbronchial biopsy performed in LLL",
                evidence_quote="Transbronchial biopsy performed in LLL",
                confidence=0.9,
            ),
        ]
    )

    accepted, warnings = validate_findings_against_text(findings, masked_prompt_text=text, min_evidence_len=10)
    assert warnings == []

    ner = build_synthetic_ner_result(masked_prompt_text=text, accepted_findings=accepted)
    mapping = NERToRegistryMapper().map_entities(ner)
    record = mapping.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.bal is not None
    assert record.procedures_performed.bal.performed is True

    assert record.procedures_performed.linear_ebus is not None
    assert record.procedures_performed.linear_ebus.performed is True
    assert "7" in (record.procedures_performed.linear_ebus.stations_sampled or [])

    assert record.procedures_performed.transbronchial_biopsy is not None
    assert record.procedures_performed.transbronchial_biopsy.performed is True
    assert record.procedures_performed.transbronchial_biopsy.locations == ["LLL"]

    # Guard against easy accidental overlaps (e.g., "bronchial biopsy" substring).
    endobronchial = record.procedures_performed.endobronchial_biopsy
    assert endobronchial is None or endobronchial.performed is not True


def test_synthetic_ner_extracts_station_and_lobe_helpers_for_tbna_and_bal() -> None:
    text = "\n".join(
        [
            "TBNA performed at station 4R.",
            "BAL performed in RML.",
        ]
    )
    findings = ReporterFindingsV1(
        findings=[
            FindingV1(
                procedure_key="tbna_conventional",
                action="diagnostic",
                finding_text="TBNA performed at station 4R",
                evidence_quote="TBNA performed at station 4R.",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                action="diagnostic",
                finding_text="BAL performed in RML",
                evidence_quote="BAL performed in RML.",
                confidence=0.9,
            ),
        ]
    )

    accepted, warnings = validate_findings_against_text(findings, masked_prompt_text=text, min_evidence_len=10)
    assert warnings == []

    ner = build_synthetic_ner_result(masked_prompt_text=text, accepted_findings=accepted)
    station_entities = [e for e in ner.entities if e.label == "ANAT_LN_STATION"]
    lobe_entities = [e for e in ner.entities if e.label == "ANAT_LUNG_LOC"]

    assert any((entity.text or "").upper() == "4R" for entity in station_entities)
    assert any((entity.text or "").upper() == "RML" for entity in lobe_entities)


def test_synthetic_ner_uses_keyword_bearing_text_for_mapping() -> None:
    text = "Complex clot removal via cryotherapy."

    findings = ReporterFindingsV1(
        findings=[
            # finding_text intentionally omits the keyword; evidence contains it.
            FindingV1(
                procedure_key="cryotherapy",
                action="other",
                finding_text="Clot removal performed",
                evidence_quote="Complex clot removal via cryotherapy.",
                confidence=0.9,
            )
        ]
    )

    accepted, warnings = validate_findings_against_text(findings, masked_prompt_text=text, min_evidence_len=10)
    assert warnings == []

    ner = build_synthetic_ner_result(masked_prompt_text=text, accepted_findings=accepted)
    mapping = NERToRegistryMapper().map_entities(ner)
    record = mapping.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.cryotherapy is not None
    assert record.procedures_performed.cryotherapy.performed is True


def test_tumor_debulking_maps_to_mechanical_debulking_field() -> None:
    text = "Mechanical debulking performed for obstructing tumor."

    findings = ReporterFindingsV1(
        findings=[
            FindingV1(
                procedure_key="tumor_debulking",
                action="other",
                finding_text="Tumor debulking performed",
                evidence_quote="Mechanical debulking performed for obstructing tumor.",
                confidence=0.9,
            )
        ]
    )

    accepted, warnings = validate_findings_against_text(findings, masked_prompt_text=text, min_evidence_len=10)
    assert warnings == []

    ner = build_synthetic_ner_result(masked_prompt_text=text, accepted_findings=accepted)
    mapping = NERToRegistryMapper().map_entities(ner)
    record = mapping.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.mechanical_debulking is not None
    assert record.procedures_performed.mechanical_debulking.performed is True

def test_guardrails_stent_inspection_only_overrides_placement() -> None:
    note_text = "Known airway stent in good position. Stent patency evaluated."
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "airway_stent": {
                    "performed": True,
                    "action": "Placement",
                }
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    assert outcome.record is not None
    assert outcome.record.procedures_performed is not None
    assert outcome.record.procedures_performed.airway_stent is not None
    assert outcome.record.procedures_performed.airway_stent.action == "Assessment only"


def test_build_bundle_from_airway_flags_renders_procedure_keywords() -> None:
    record = {
        "procedures_performed": {
            "navigational_bronchoscopy": {"performed": True},
            "thermal_ablation": {"performed": True},
            "cryotherapy": {"performed": True},
            "therapeutic_aspiration": {"performed": True},
            "airway_dilation": {"performed": True},
            "airway_stent": {"performed": True, "action": "Placement"},
            "balloon_occlusion": {"performed": True},
        }
    }
    source_text = (
        "Ion robotic bronchoscopy performed. Balloon dilation of RMS. APC applied to tumor. "
        "Cryotherapy performed. Successful therapeutic aspiration of mucus. Airway stent deployed. "
        "Balloon occlusion with Arndt."
    )

    bundle = build_procedure_bundle_from_extraction(record, source_text=source_text)
    proc_types = {proc.proc_type for proc in bundle.procedures}

    assert "robotic_navigation" in proc_types
    assert "therapeutic_aspiration" in proc_types
    assert "airway_dilation" in proc_types
    assert "endobronchial_tumor_destruction" in proc_types
    assert "airway_stent_placement" in proc_types
    assert "endobronchial_blocker" in proc_types
    assert "cryo_extraction_mucus" in proc_types or "endobronchial_cryoablation" in proc_types

    engine = ReporterEngine(
        default_template_registry(),
        default_schema_registry(),
        procedure_order=_load_procedure_order(),
    )
    markdown = engine.compose_report(bundle)
    lower = markdown.lower()
    assert "airway dilation" in lower
    assert "therapeutic aspiration" in lower
    assert "argon plasma" in lower or " apc" in lower
    assert "airway stent" in lower


def test_balloon_occlusion_air_leak_prefers_bpf_localization_template() -> None:
    record = {"procedures_performed": {"balloon_occlusion": {"performed": True}}}
    source_text = "Persistent air leak. Serial occlusion with an Arndt balloon to localize leak to RLL."
    bundle = build_procedure_bundle_from_extraction(record, source_text=source_text)
    proc_types = {proc.proc_type for proc in bundle.procedures}
    assert "bpf_localization_occlusion" in proc_types


def test_airway_stent_assessment_only_maps_to_surveillance_procedure() -> None:
    record = {"procedures_performed": {"airway_stent": {"performed": True, "action": "Assessment only"}}}
    source_text = "Known airway stent in good position. Stent patency evaluated."
    bundle = build_procedure_bundle_from_extraction(record, source_text=source_text)
    proc_types = {proc.proc_type for proc in bundle.procedures}
    assert "stent_surveillance" in proc_types
    assert "airway_stent_placement" not in proc_types


class _StubLLM:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def generate(self, _prompt: str, *args: object, **kwargs: object) -> str:  # noqa: ARG002
        return json.dumps(self._payload)


def test_seed_llm_findings_backfills_lobes_and_stations_without_creating_linear_ebus() -> None:
    note = "\n".join(
        [
            "TBNA performed at station 4R.",
            "BAL performed in RUL.",
            "Brushings performed in LLL.",
        ]
    )
    llm = _StubLLM(
        {
            "version": "reporter_findings_v1",
            "findings": [
                {
                    "procedure_key": "tbna_conventional",
                    "action": "diagnostic",
                    "anatomy": ["station 4R"],
                    "finding_text": "TBNA performed at station 4R",
                    "evidence_quote": "TBNA performed at station 4R.",
                    "confidence": 0.9,
                },
                {
                    "procedure_key": "bal",
                    "action": "diagnostic",
                    "anatomy": ["RUL"],
                    "finding_text": "BAL performed in RUL",
                    "evidence_quote": "BAL performed in RUL.",
                    "confidence": 0.9,
                },
                {
                    "procedure_key": "brushings",
                    "action": "diagnostic",
                    "anatomy": ["LLL"],
                    "finding_text": "Brushings performed in LLL",
                    "evidence_quote": "Brushings performed in LLL.",
                    "confidence": 0.9,
                },
            ],
            "notes": [],
        }
    )

    seed = seed_registry_record_from_llm_findings(note, llm=llm)
    record = seed.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.tbna_conventional is not None
    assert record.procedures_performed.tbna_conventional.performed is True
    assert record.procedures_performed.tbna_conventional.stations_sampled == ["4R"]

    assert record.procedures_performed.linear_ebus is not None
    assert record.procedures_performed.linear_ebus.performed is True
    assert record.procedures_performed.linear_ebus.stations_sampled == ["4R"]

    assert record.procedures_performed.bal is not None
    assert record.procedures_performed.bal.location == "RUL"

    assert record.procedures_performed.brushings is not None
    assert record.procedures_performed.brushings.locations == ["LLL"]


def test_seed_llm_findings_backfills_blvr_valve_count_and_segments() -> None:
    note = "Placed size 6 Spiration valve RB9. Placed size 6 valve RB10."
    llm = _StubLLM(
        {
            "version": "reporter_findings_v1",
            "findings": [
                {
                    "procedure_key": "blvr",
                    "action": "placement",
                    "anatomy": ["RB9"],
                    "finding_text": "BLVR valve placed in RB9 size 6",
                    "evidence_quote": "Placed size 6 Spiration valve RB9.",
                    "confidence": 0.9,
                },
                {
                    "procedure_key": "blvr",
                    "action": "placement",
                    "anatomy": ["RB10"],
                    "finding_text": "BLVR valve placed in RB10 size 6",
                    "evidence_quote": "Placed size 6 valve RB10.",
                    "confidence": 0.9,
                },
            ],
            "notes": [],
        }
    )

    seed = seed_registry_record_from_llm_findings(note, llm=llm)
    record = seed.record

    assert record.procedures_performed is not None
    assert record.procedures_performed.blvr is not None
    assert record.procedures_performed.blvr.performed is True
    assert record.procedures_performed.blvr.procedure_type == "Valve placement"
    assert record.procedures_performed.blvr.valve_type == "Spiration (Olympus)"
    assert record.procedures_performed.blvr.valve_sizes == ["6"]
    assert record.procedures_performed.blvr.segments_treated == ["RB9", "RB10"]
    assert record.procedures_performed.blvr.number_of_valves == 2
