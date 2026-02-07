from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.deterministic_extractors import run_deterministic_extractors
from app.registry.schema import RegistryRecord


def test_diagnostic_bronchoscopy_inspection_derives_31622() -> None:
    note_text = (
        "INDICATION FOR OPERATION: tracheal stenosis. Risks of bronchoscopy discussed.\n"
        "ANESTHESIA: General Anesthesia\n"
        "INSTRUMENT:\n"
        "Flexible Therapeutic Bronchoscope\n"
        "PROCEDURE IN DETAIL:\n"
        "After induction of anesthesia, the airway was inspected.\n"
        "The remainder of the airway was inspected with normal appearing anatomy bilaterally.\n"
        "There were some secretions noted throughout the airway and these were suctioned and cleared.\n"
        "The patient tolerated the procedure well.\n"
    )

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord.model_validate({"procedures_performed": seed.get("procedures_performed", {})})
    assert record.procedures_performed is not None
    assert record.procedures_performed.diagnostic_bronchoscopy is not None
    assert record.procedures_performed.diagnostic_bronchoscopy.performed is True

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31622" in codes


def test_diagnostic_bronchoscopy_not_inferred_from_consent_only() -> None:
    note_text = (
        "INDICATION FOR OPERATION: COPD.\n"
        "The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed.\n"
        "Informed consent was signed.\n"
    )
    seed = run_deterministic_extractors(note_text)
    procs = seed.get("procedures_performed", {}) or {}
    assert "diagnostic_bronchoscopy" not in procs

