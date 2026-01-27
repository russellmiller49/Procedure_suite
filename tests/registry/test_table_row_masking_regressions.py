from __future__ import annotations

from pathlib import Path

from modules.registry.deterministic_extractors import run_deterministic_extractors
from modules.registry.processing.masking import mask_offset_preserving


def test_note_315_blank_modality_rows_do_not_trigger_cryo_or_apc() -> None:
    note_text = Path("tests/fixtures/notes/note_315.txt").read_text(encoding="utf-8")
    seed_text = mask_offset_preserving(note_text)
    seed = run_deterministic_extractors(seed_text)

    procs = seed.get("procedures_performed") or {}
    assert isinstance(procs, dict)

    thermal = procs.get("thermal_ablation") or {}
    assert isinstance(thermal, dict)
    assert thermal.get("performed") is True
    assert thermal.get("modality") == "Electrocautery"

    cryo = procs.get("cryotherapy")
    assert not (isinstance(cryo, dict) and cryo.get("performed") is True)


def test_note_289_soft_coag_does_not_default_to_apc() -> None:
    note_text = Path("tests/fixtures/notes/note_289.txt").read_text(encoding="utf-8")
    seed_text = mask_offset_preserving(note_text)
    seed = run_deterministic_extractors(seed_text)

    procs = seed.get("procedures_performed") or {}
    assert isinstance(procs, dict)

    thermal = procs.get("thermal_ablation") or {}
    assert isinstance(thermal, dict)
    assert thermal.get("performed") is True
    assert thermal.get("modality") == "Electrocautery"

    cryo = procs.get("cryotherapy") or {}
    assert isinstance(cryo, dict)
    assert cryo.get("performed") is True

