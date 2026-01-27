from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import (
    derive_all_codes_with_meta,
    derive_units_for_codes,
)
from modules.registry.deterministic_extractors import run_deterministic_extractors
from modules.registry.schema import RegistryRecord
from modules.registry.self_correction.keyword_guard import apply_required_overrides


def test_note_281_elastography_does_not_force_tblb_and_derives_elastography_codes() -> None:
    note_text = """
    PROCEDURE:
    Linear EBUS was performed with sampling at stations 11L, 4L, and 4R.
    76981 Ultrasound Elastography, Parenchyma of Organ
    76982 Ultrasound Elastography, First target lesion
    76983 Ultrasound Elastography, Each additional target lesion

    PROCEDURE IN DETAIL:
    Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness.
    Site 1: The 11L lymph node was sampled. 4 endobronchial ultrasound guided transbronchial biopsies were performed.
    The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.
    Site 2: The 4L lymph node was sampled. 5 endobronchial ultrasound guided transbronchial biopsies were performed.
    The target lymph node demonstrated a Type 1 elastographic pattern.
    Site 3: The 4R lymph node was sampled. 6 endobronchial ultrasound guided transbronchial biopsies were performed.
    The target lymph node demonstrated a Type 1 elastographic pattern.
    """

    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)

    record, _override_warnings = apply_required_overrides(note_text, record)
    assert record.procedures_performed
    assert record.procedures_performed.linear_ebus
    assert record.procedures_performed.linear_ebus.elastography_used is True

    # "EBUS guided transbronchial biopsies" refers to nodal TBNA and must not force
    # a parenchymal transbronchial lung biopsy flag/code (31628).
    tblb = getattr(record.procedures_performed, "transbronchial_biopsy", None)
    assert tblb is None or tblb.performed is not True

    record_data = record.model_dump()
    record_data.setdefault("evidence", {})["code_evidence"] = [{"text": "76981", "start": 0, "end": 5}]
    record = RegistryRecord(**record_data)

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert "31628" not in codes
    assert "31653" in codes
    assert "76982" in codes
    assert "76983" in codes
    assert "76981" not in codes

    units = derive_units_for_codes(record, codes)
    assert units.get("76983") == 2
