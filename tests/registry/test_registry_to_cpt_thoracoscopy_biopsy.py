from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.registry.postprocess import enrich_medical_thoracoscopy_biopsies_taken
from modules.registry.schema import RegistryRecord


def test_registry_to_cpt_thoracoscopy_with_pleural_biopsy_derives_32609() -> None:
    record = RegistryRecord.model_validate(
        {
            "pleural_procedures": {
                "medical_thoracoscopy": {"performed": True, "biopsies_taken": True},
            }
        }
    )

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "32609" in codes
    assert "32601" not in codes


def test_registry_to_cpt_thoracoscopy_without_biopsy_derives_32601() -> None:
    record = RegistryRecord.model_validate(
        {
            "pleural_procedures": {
                "medical_thoracoscopy": {"performed": True},
            }
        }
    )

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "32601" in codes
    assert "32609" not in codes


def test_postprocess_sets_medical_thoracoscopy_biopsies_taken_from_text() -> None:
    record = RegistryRecord.model_validate(
        {
            "pleural_procedures": {
                "medical_thoracoscopy": {"performed": True},
            }
        }
    )

    note_text = "Biopsies of the abnormal areas in the parietal pleura were performed with forceps."
    warnings = enrich_medical_thoracoscopy_biopsies_taken(record, note_text)

    thor = record.pleural_procedures.medical_thoracoscopy  # type: ignore[union-attr]
    assert thor.biopsies_taken is True
    assert "pleural_procedures.medical_thoracoscopy.biopsies_taken" in (record.evidence or {})
    assert any("AUTO_THORACOSCOPY_BIOPSY" in w for w in warnings)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "32609" in codes

