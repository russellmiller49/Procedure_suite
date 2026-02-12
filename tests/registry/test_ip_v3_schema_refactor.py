from __future__ import annotations

from app.registry.application.registry_builder import V3RegistryBuilder
from proc_schemas.registry.ip_v3 import IPRegistryV3


def test_ip_v3_accepts_legacy_clinical_context_alias() -> None:
    entry = IPRegistryV3(
        clinical_context={
            "lesion_characteristics": {
                "bronchus_sign": "Positive",
            }
        }
    )

    assert entry.diagnostic_focus.lesion_characteristics is not None
    assert entry.diagnostic_focus.lesion_characteristics.bronchus_sign == "Positive"
    assert entry.clinical_context.lesion_characteristics is not None
    assert entry.clinical_context.lesion_characteristics.bronchus_sign == "Positive"


def test_ip_v3_risk_assessment_fields() -> None:
    entry = IPRegistryV3(
        risk_assessment={
            "asa_class": 3,
            "anticoagulant_use": "Apixaban",
            "mallampati_score": 2,
        }
    )

    assert entry.risk_assessment.asa_class == 3
    assert entry.risk_assessment.anticoagulant_use == "Apixaban"
    assert entry.risk_assessment.mallampati_score == 2


def test_v3_builder_maps_legacy_asa_into_risk_assessment() -> None:
    builder = V3RegistryBuilder()
    missing: list[str] = []
    metadata = {
        "patient": {"patient_id": "p-1"},
        "procedure": {"procedure_date": "2026-01-01", "indication": "Lung nodule"},
        "asa_class": 4,
        "clinical_context": {"lesion_characteristics": {"bronchus_sign": "Negative"}},
    }

    patient = builder.build_patient(metadata, missing)
    procedure = builder.build_procedure("proc-1", metadata, missing)
    entry = builder.build_entry(
        procedure_id="proc-1",
        patient=patient,
        procedure=procedure,
        registry_fields={},
        metadata=metadata,
    )

    assert entry.risk_assessment.asa_class == 4
    assert entry.diagnostic_focus.lesion_characteristics is not None
    assert entry.diagnostic_focus.lesion_characteristics.bronchus_sign == "Negative"
