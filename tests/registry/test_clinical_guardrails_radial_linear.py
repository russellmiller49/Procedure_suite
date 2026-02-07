from __future__ import annotations

from app.extraction.postprocessing.clinical_guardrails import ClinicalGuardrails
from app.registry.schema import RegistryRecord


def test_clinical_guardrails_does_not_require_review_for_combined_linear_and_radial_with_peripheral_context() -> None:
    guardrails = ClinicalGuardrails()

    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {"performed": True, "stations_sampled": ["11RS", "7"]},
            }
        }
    )
    note_text = (
        "A systematic hilar and mediastinal lymph node survey was carried out. Station 11RS and 7 were sampled. "
        "A large sheath catheter with radial ultrasound was used to the area of known nodule. "
        "Biopsies were performed with forceps with fluoroscopic guidance through the sheath."
    )

    outcome = guardrails.apply_record_guardrails(note_text, record)
    assert outcome.needs_review is False
    assert not any("Radial vs linear EBUS markers both present" in w for w in outcome.warnings)

