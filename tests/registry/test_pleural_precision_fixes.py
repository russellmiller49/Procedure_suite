from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.evidence.verifier import _find_therapeutic_aspiration_anchor
from app.registry.postprocess import enrich_medical_thoracoscopy_biopsies_taken
from app.registry.schema import RegistryRecord


def test_thoracoscopy_with_pleural_biopsies_derives_32609_not_32604() -> None:
    record = RegistryRecord.model_validate(
        {"pleural_procedures": {"medical_thoracoscopy": {"performed": True}}}
    )
    note_text = (
        "The rigid pleuroscopy telescope was introduced through the trocar. Biopsies of the "
        "abnormal areas in the parietal pleura posteriorly were performed with forceps and "
        "sent for histopathological examination with approximately 12 total biopsies taken."
    )
    warnings = enrich_medical_thoracoscopy_biopsies_taken(record, note_text)
    assert record.pleural_procedures.medical_thoracoscopy.biopsies_taken is True
    assert any("AUTO_THORACOSCOPY_BIOPSY" in str(w) for w in warnings)

    codes, _r, _w = derive_all_codes_with_meta(record)
    assert "32609" in codes
    assert "32604" not in codes
    assert "32601" not in codes


def test_thoracoscopy_without_biopsies_stays_32601() -> None:
    record = RegistryRecord.model_validate(
        {"pleural_procedures": {"medical_thoracoscopy": {"performed": True}}}
    )
    note_text = "Medical thoracoscopy was performed. The pleura appeared normal. No biopsies were taken."
    enrich_medical_thoracoscopy_biopsies_taken(record, note_text)
    codes, _r, _w = derive_all_codes_with_meta(record)
    assert "32601" in codes
    assert "32609" not in codes


def test_pleural_needle_verification_is_not_therapeutic_aspiration_anchor() -> None:
    text = (
        "A 20 gauge Yueh-centesis needle with syringe attached was inserted into the pleural "
        "space with aspiration of air / fluid to verify placement."
    )
    assert _find_therapeutic_aspiration_anchor(text) is None


def test_genuine_airway_aspiration_anchor_preserved() -> None:
    text = "Copious thick secretions were suctioned from the bilateral airways with therapeutic intent."
    assert _find_therapeutic_aspiration_anchor(text) is not None
