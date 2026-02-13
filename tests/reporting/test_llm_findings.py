from __future__ import annotations

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.ner_mapping.entity_to_registry import NERToRegistryMapper
from app.registry.schema import RegistryRecord
from app.reporting.llm_findings import (
    FindingV1,
    ReporterFindingsV1,
    build_synthetic_ner_result,
    validate_findings_against_text,
)


def test_validate_findings_against_text_drops_missing_or_weak_evidence() -> None:
    text = "A procedure was performed today.\nBAL performed in RUL."
    findings = ReporterFindingsV1(
        findings=[
            FindingV1(
                procedure_key="bal",
                finding_text="BAL performed in RUL",
                evidence_quote="BAL performed in RUL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                finding_text="31624 BAL performed in RUL",
                evidence_quote="BAL performed in RUL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                finding_text="BAL performed",
                evidence_quote="BAL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="not_a_proc",
                finding_text="BAL performed in RUL",
                evidence_quote="BAL performed in RUL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                finding_text="BAL performed",
                evidence_quote="NOT PRESENT IN TEXT",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
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


def test_findings_to_synthetic_ner_to_registry_flags() -> None:
    text = "\n".join(
        [
            "EBUS TBNA biopsied station 7",
            "BAL performed in RUL",
            "Transbronchial biopsy performed in LLL",
        ]
    )

    findings = ReporterFindingsV1(
        findings=[
            FindingV1(
                procedure_key="linear_ebus",
                finding_text="EBUS TBNA biopsied station 7",
                evidence_quote="EBUS TBNA biopsied station 7",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="bal",
                finding_text="BAL performed in RUL",
                evidence_quote="BAL performed in RUL",
                confidence=0.9,
            ),
            FindingV1(
                procedure_key="transbronchial_biopsy",
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


def test_synthetic_ner_uses_keyword_bearing_text_for_mapping() -> None:
    text = "Complex clot removal via cryotherapy."

    findings = ReporterFindingsV1(
        findings=[
            # finding_text intentionally omits the keyword; evidence contains it.
            FindingV1(
                procedure_key="cryotherapy",
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
