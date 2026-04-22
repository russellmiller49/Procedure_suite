from __future__ import annotations

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.deterministic_extractors import extract_brushings, extract_endobronchial_biopsy
from app.registry.schema import RegistryRecord


def test_extract_brushings_ignores_not_obtained_sentence() -> None:
    note_text = (
        "A flexible bronchoscopy was performed under moderate sedation. "
        "Mild diffuse erythema without focal endobronchial lesion. "
        "BAL performed in the right middle lobe with 100 mL instilled, 36 mL returned. "
        "Cytology brushings and endobronchial biopsies were not obtained. "
        "No specimen other than BAL.\n"
    )

    assert extract_brushings(note_text) == {}


def test_extract_brushings_prefers_intervention_location_over_header_only_mention() -> None:
    note_text = (
        "Procedure: Bronchoscopy, endobronchial biopsy, brushings, BAL, linear EBUS-TBNA.\n"
        "Interventions:\n"
        "Cytology brush x2 from LUL lesion.\n"
    )

    result = extract_brushings(note_text)

    assert result.get("brushings", {}).get("performed") is True
    assert result.get("brushings", {}).get("locations") == ["LUL"]


def test_extract_endobronchial_biopsy_ignores_not_obtained_sentence() -> None:
    note_text = (
        "A flexible bronchoscopy was performed under moderate sedation. "
        "Mild diffuse erythema without focal endobronchial lesion. "
        "BAL performed in the right middle lobe with 100 mL instilled, 36 mL returned. "
        "Cytology brushings and endobronchial biopsies were not obtained. "
        "No specimen other than BAL.\n"
    )

    assert extract_endobronchial_biopsy(note_text) == {}


def test_clinical_guardrails_clear_negated_airway_sampling_and_preserve_erythema() -> None:
    note_text = (
        "A flexible bronchoscopy was performed under moderate sedation. "
        "Mild diffuse erythema without focal endobronchial lesion. "
        "BAL performed in the right middle lobe with 100 mL instilled, 36 mL returned. "
        "Cytology brushings and endobronchial biopsies were not obtained. "
        "No specimen other than BAL.\n"
    )
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "brushings": {"performed": True},
                "endobronchial_biopsy": {"performed": True},
                "diagnostic_bronchoscopy": {
                    "performed": True,
                    "inspection_findings": "Mild diffuse erythema without focal endobronchial lesion.",
                    "airway_abnormalities": ["Endobronchial lesion", "Mucosal abnormality"],
                },
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.brushings is not None
    assert updated.procedures_performed.brushings.performed is False
    assert updated.procedures_performed.endobronchial_biopsy is not None
    assert updated.procedures_performed.endobronchial_biopsy.performed is False

    diagnostic = updated.procedures_performed.diagnostic_bronchoscopy
    assert diagnostic is not None
    assert diagnostic.airway_abnormalities == ["Mucosal abnormality"]
    assert diagnostic.inspection_findings == "Mild diffuse erythema"


def test_clinical_guardrails_clear_without_endobronchial_abnormality_phrase() -> None:
    note_text = (
        "Monarch robotic bronchoscopy platform used to reach a left lower lobe posterior basal target. "
        "Outer sheath and inner scope positioning allowed stable access. "
        "Radial EBUS demonstrated an eccentric view. "
        "Airways otherwise without endobronchial abnormality.\n"
    )
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "diagnostic_bronchoscopy": {
                    "performed": True,
                    "inspection_findings": "Airways otherwise without endobronchial abnormality. lesion with robotic platform",
                    "airway_abnormalities": ["Endobronchial lesion"],
                }
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.procedures_performed is not None
    diagnostic = updated.procedures_performed.diagnostic_bronchoscopy
    assert diagnostic is not None
    assert diagnostic.airway_abnormalities in (None, [])
    assert diagnostic.inspection_findings is None
