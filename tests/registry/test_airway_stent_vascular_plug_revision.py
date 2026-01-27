from __future__ import annotations

from pathlib import Path

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.registry.deterministic_extractors import run_deterministic_extractors
from modules.registry.processing.masking import mask_offset_preserving
from modules.registry.schema import RegistryRecord


def _derive_codes_for_note(path: str) -> tuple[RegistryRecord, list[str]]:
    note_text = Path(path).read_text(encoding="utf-8")
    seed_text = mask_offset_preserving(note_text)
    seed = run_deterministic_extractors(seed_text)
    record = RegistryRecord(**seed)
    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    return record, codes


def test_note_274_vascular_plug_revision_derives_31638() -> None:
    record, codes = _derive_codes_for_note("tests/fixtures/notes/note_274.txt")
    assert "31638" in codes
    assert record.procedures_performed is not None
    stent = record.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Revision/Repositioning"


def test_note_275_vascular_plug_revision_derives_31638() -> None:
    record, codes = _derive_codes_for_note("tests/fixtures/notes/note_275.txt")
    assert "31638" in codes
    assert record.procedures_performed is not None
    stent = record.procedures_performed.airway_stent
    assert stent is not None
    assert stent.action == "Revision/Repositioning"

