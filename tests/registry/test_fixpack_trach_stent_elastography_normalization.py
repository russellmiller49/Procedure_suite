from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.registry.deterministic_extractors import run_deterministic_extractors
from modules.registry.schema import RegistryRecord


def _derive_codes_from_note_text(note_text: str) -> tuple[list[str], dict[str, str], list[str]]:
    seed = run_deterministic_extractors(note_text)
    record = RegistryRecord(**seed)
    return derive_all_codes_with_meta(record)


def test_trach_change_note_does_not_derive_31600() -> None:
    note_text = """
    PROCEDURE:
    TRACHEOSTOMY CHANGE AFTER ESTABLISHMENT OF FISTULA TRACT
    Tracheobronchoscopy through established tracheostomy incision
    31645 Therapeutic aspiration initial episode

    PROCEDURE IN DETAIL:
    The cuff was deflated and the tracheostomy tube was easily removed.
    The new tracheostomy tube was then placed.
    Successful therapeutic aspiration was performed to clean out the trachea from mucus plug.
    """
    codes, _rationales, _warnings = _derive_codes_from_note_text(note_text)
    assert "31600" not in codes
    assert "31615" in codes


def test_stent_exchange_note_suppresses_stent_superbill_combo() -> None:
    note_text = """
    PROCEDURE:
    31635 Foreign body removal

    PROCEDURE IN DETAIL:
    Using rat tooth forceps the stent was grasped and removed enbloc.
    The following stent (Bona stent 10 x 30) was placed in the Left Mainstem.
    """
    codes, _rationales, _warnings = _derive_codes_from_note_text(note_text)
    assert "31638" in codes
    assert "31635" not in codes
    assert "31636" not in codes


def test_registry_record_normalizes_therapeutic_aspiration_material() -> None:
    record = RegistryRecord(
        procedures_performed={
            "therapeutic_aspiration": {"performed": True, "material": "Blood clot"},
        }
    )
    assert record.procedures_performed
    assert record.procedures_performed.therapeutic_aspiration
    assert record.procedures_performed.therapeutic_aspiration.material == "Blood/clot"

    record2 = RegistryRecord(
        procedures_performed={
            "therapeutic_aspiration": {"performed": True, "material": "Secretions/mucus"},
        }
    )
    assert record2.procedures_performed
    assert record2.procedures_performed.therapeutic_aspiration
    assert record2.procedures_performed.therapeutic_aspiration.material in {"Mucus", "Mucus plug", "Other"}


def test_registry_to_cpt_derives_elastography_codes() -> None:
    record = RegistryRecord(
        procedures_performed={
            "linear_ebus": {"performed": True, "elastography_used": True, "stations_sampled": ["7", "4R"]},
        }
    )
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    assert any(code in {"76981", "76982", "76983"} for code in codes)
