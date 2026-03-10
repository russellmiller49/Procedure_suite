from __future__ import annotations

import pytest

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.application.registry_service import RegistryService
from app.registry.deterministic_extractors import extract_peripheral_ablation
from app.registry.postprocess.complications_reconcile import reconcile_complications_from_narrative
from app.registry.schema import RegistryRecord


def _extract(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "engine")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    service = RegistryService()
    return service.extract_fields(note_text)


def test_combined_ebus_and_eus_b_counts_only_bronchoscopic_stations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    note_text = (
        "PROCEDURE:\n"
        "Combined EBUS-TBNA and EUS-B staging.\n"
        "EBUS Findings:\n"
        "Site 1: Station 4R lymph node. Sampling was performed with 5 passes using a 22G needle.\n"
        "Site 2: Station 7 lymph node. Sampling was performed with 4 passes using a 22G needle.\n"
        "EUS-B Findings:\n"
        "Site 3: Station 8 lymph node via esophagus. Sampling was performed with 3 passes using a 25G needle.\n"
        "Site 4: Station 9 lymph node via esophagus. Sampling was performed with 2 passes using a 25G needle.\n"
        "SPECIMENS:\n"
        "- TBNA of 4R node station\n"
        "- TBNA of 7 node station\n"
        "- EUS-B FNA of station 8\n"
        "- EUS-B FNA of station 9\n"
        "Complications: None.\n"
    )

    result = _extract(monkeypatch, note_text)
    procedures = result.record.procedures_performed
    assert procedures is not None

    linear = procedures.linear_ebus
    assert linear is not None
    assert linear.performed is True
    assert set(linear.stations_sampled or []) == {"4R", "7"}

    eus_b = procedures.eus_b
    assert eus_b is not None
    assert eus_b.performed is True

    assert "31652" in result.cpt_codes
    assert "31653" not in result.cpt_codes


def test_extract_peripheral_ablation_ignores_ct_guided_percutaneous_ablation() -> None:
    note_text = (
        "PROCEDURE:\n"
        "CT-guided percutaneous microwave ablation of a right lower lobe lung lesion.\n"
        "A microwave antenna was advanced through the chest wall into the lesion under computed tomography guidance.\n"
    )

    assert extract_peripheral_ablation(note_text) == {}


def test_extraction_first_clears_bronchoscopic_ablation_for_percutaneous_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    note_text = (
        "PROCEDURE:\n"
        "CT-guided percutaneous radiofrequency ablation of a pleural-based right lower lobe lesion.\n"
        "Under CT guidance a coaxial probe was advanced through the chest wall into the lesion and ablation was completed.\n"
        "No bronchoscopy was performed.\n"
    )

    result = _extract(monkeypatch, note_text)
    procedures = result.record.procedures_performed
    assert procedures is not None
    assert procedures.peripheral_ablation is None or procedures.peripheral_ablation.performed is not True
    assert "31641" not in result.cpt_codes


def test_reconcile_complications_ignores_routine_hemostasis_without_true_complication() -> None:
    note_text = (
        "A small amount of oozing from the biopsy site resolved after wedging the bronchoscope, suction, "
        "and cold saline. Hemostasis was confirmed and there was no active bleeding.\n"
    )
    record = RegistryRecord.model_validate({})

    reconcile_complications_from_narrative(record, note_text)

    complications = record.complications
    assert complications is None or complications.any_complication is not True


def test_clinical_guardrails_clear_routine_hemostasis_false_positive() -> None:
    note_text = (
        "A small amount of oozing from the biopsy site resolved after wedging the bronchoscope, suction, "
        "and cold saline. Hemostasis was confirmed and there was no active bleeding.\n"
    )
    record = RegistryRecord.model_validate(
        {
            "complications": {
                "any_complication": True,
                "complication_list": ["Bleeding - Moderate"],
                "events": [{"type": "Bleeding", "notes": "Controlled with cold saline."}],
                "bleeding": {"occurred": True, "bleeding_grade_nashville": 2},
            }
        }
    )

    outcome = ClinicalGuardrails().apply_record_guardrails(note_text, record)
    updated = outcome.record

    assert updated is not None
    assert updated.complications is not None
    assert updated.complications.any_complication is False
    assert updated.complications.complication_list == []
    assert updated.complications.events == []
    assert updated.complications.bleeding is not None
    assert updated.complications.bleeding.occurred is False
    assert updated.complications.bleeding.bleeding_grade_nashville == 0
