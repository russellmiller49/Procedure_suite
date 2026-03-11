from __future__ import annotations

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.deterministic_extractors import extract_blvr
from app.registry.schema import RegistryRecord


def test_extract_blvr_parses_x4_deployment_and_negative_cv() -> None:
    note_text = """
    PRE-PROCEDURE DIAGNOSIS
    Severe emphysema with hyperinflation, planned BLVR.

    POST-PROCEDURE DIAGNOSIS
    Same, status post endobronchial valve placement to the left upper lobe.

    PROCEDURES PERFORMED
    Flexible bronchoscopy
    Collateral ventilation assessment
    Endobronchial valve deployment x4, left upper lobe

    FINDINGS
    No endobronchial lesions. Airway anatomy suitable for valve therapy.
    Collateral ventilation assessment of the left upper lobe was negative.
    Left upper lobe segments were sized and treated with four valves.
    """.strip()

    extracted = extract_blvr(note_text)
    blvr = extracted.get("blvr") or {}

    assert blvr.get("performed") is True
    assert blvr.get("procedure_type") == "Valve placement"
    assert blvr.get("target_lobe") == "LUL"
    assert blvr.get("number_of_valves") == 4
    assert blvr.get("collateral_ventilation_assessment") == "Chartis negative"


def test_extract_blvr_parses_parenthetical_total_valve_count() -> None:
    note_text = """
    Procedure in detail:
    Flexible bronchoscope introduced. Chartis balloon occlusion testing of LUL
    demonstrated pattern consistent with no collateral ventilation. Segmental
    measurements performed; valves deployed to apicoposterior and anterior segments
    and lingula (total 4 valves). Valves seated well. No bleeding.
    """.strip()

    extracted = extract_blvr(note_text)
    blvr = extracted.get("blvr") or {}

    assert blvr.get("performed") is True
    assert blvr.get("procedure_type") == "Valve placement"
    assert blvr.get("target_lobe") == "LUL"
    assert blvr.get("number_of_valves") == 4
    assert blvr.get("collateral_ventilation_assessment") == "Chartis negative"


def test_clinical_guardrails_blvr_overrides_lower_count_from_explicit_four_valves() -> None:
    note_text = """
    PRE-PROCEDURE DIAGNOSIS
    Severe emphysema with hyperinflation, planned BLVR.

    POST-PROCEDURE DIAGNOSIS
    Same, status post endobronchial valve placement to the left upper lobe.

    PROCEDURES PERFORMED
    Flexible bronchoscopy
    Collateral ventilation assessment
    Endobronchial valve deployment x4, left upper lobe

    FINDINGS
    No endobronchial lesions. Airway anatomy suitable for valve therapy.
    Collateral ventilation assessment of the left upper lobe was negative.
    Left upper lobe segments were sized and treated with four valves.
    """.strip()

    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "blvr": {
                    "performed": True,
                    "procedure_type": "Valve placement",
                    "target_lobe": "Lingula",
                    "number_of_valves": 3,
                    "collateral_ventilation_assessment": "Chartis indeterminate",
                }
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    blvr = updated.procedures_performed.blvr
    assert blvr is not None
    assert blvr.target_lobe == "LUL"
    assert blvr.number_of_valves == 4
    assert blvr.collateral_ventilation_assessment == "Chartis negative"


def test_clinical_guardrails_blvr_overrides_higher_count_from_parenthetical_total() -> None:
    note_text = """
    Procedure in detail:
    Flexible bronchoscope introduced. Chartis balloon occlusion testing of LUL
    demonstrated pattern consistent with no collateral ventilation. Segmental
    measurements performed; valves deployed to apicoposterior and anterior segments
    and lingula (total 4 valves). Valves seated well. No bleeding.
    """.strip()

    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "blvr": {
                    "performed": True,
                    "procedure_type": "Valve placement",
                    "target_lobe": "LUL",
                    "number_of_valves": 6,
                    "collateral_ventilation_assessment": "Chartis indeterminate",
                }
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    blvr = updated.procedures_performed.blvr
    assert blvr is not None
    assert blvr.target_lobe == "LUL"
    assert blvr.number_of_valves == 4
    assert blvr.collateral_ventilation_assessment == "Chartis negative"
