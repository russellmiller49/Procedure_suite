from pathlib import Path

from app.registry.deterministic_extractors import run_deterministic_extractors


def test_note_047_deterministic_extractors_capture_tbbx_and_peripheral_tbna() -> None:
    note_text = Path("registry_granular_data/notes_text/note_047.txt").read_text(encoding="utf-8")
    seed = run_deterministic_extractors(note_text)

    procedures = seed.get("procedures_performed") or {}
    assert (procedures.get("peripheral_tbna") or {}).get("performed") is True
    assert (procedures.get("transbronchial_biopsy") or {}).get("performed") is True

