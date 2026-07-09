from __future__ import annotations

from app.registry.deterministic_extractors import extract_endobronchial_biopsy
from app.registry.schema import RegistryRecord
from app.registry.self_correction.keyword_guard import apply_required_overrides


def _override_flag(note_text: str) -> bool | None:
    record = RegistryRecord.model_validate({})
    updated, _w = apply_required_overrides(note_text, record)
    ebbx = getattr(getattr(updated, "procedures_performed", None), "endobronchial_biopsy", None)
    return getattr(ebbx, "performed", None)


def test_modifier22_menu_text_does_not_force_endobronchial_biopsy() -> None:
    text = (
        "This patient required significant airway management. This resulted in >40% increased "
        "work due to increased intensity and technical difficulty. Apply to: 31625 "
        "Endobronchial Biopsy(s)\n"
        "PROCEDURE IN DETAIL: The airways were inspected. No biopsies were taken.\n"
    )
    assert _override_flag(text) is not True
    assert extract_endobronchial_biopsy(text) == {}


def test_forceps_biopsies_with_lesion_in_previous_sentence_recovered() -> None:
    text = (
        "The airways were inspected and patient was found to have endobronchial lesion noted "
        "in the right lower lobe superior segment. Multiple forceps biopsies were obtained at "
        "this time."
    )
    proc = extract_endobronchial_biopsy(text).get("endobronchial_biopsy") or {}
    assert proc.get("performed") is True
    assert "RLL" in (proc.get("locations") or [])


def test_narrative_endobronchial_biopsy_still_detected() -> None:
    text = "Endobronchial biopsies were obtained from the tumor at the lower trachea."
    proc = extract_endobronchial_biopsy(text).get("endobronchial_biopsy") or {}
    assert proc.get("performed") is True


def test_nodal_only_ebus_does_not_get_endobronchial_biopsy() -> None:
    text = (
        "EBUS was performed. Station 7 was identified and sampled by TBNA with 4 passes. "
        "Forceps biopsies were not performed."
    )
    assert extract_endobronchial_biopsy(text) == {}


def test_peripheral_nodule_forceps_biopsy_not_misrouted_to_endobronchial() -> None:
    text = (
        "Radial EBUS localized the RLL nodule with a concentric view. "
        "Transbronchial forceps biopsies were obtained from the peripheral nodule."
    )
    assert extract_endobronchial_biopsy(text) == {}
