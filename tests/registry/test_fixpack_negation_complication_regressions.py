from __future__ import annotations

from pathlib import Path

import pytest

from app.registry.application.registry_service import RegistryService


def _march_2026_notes_dir() -> Path:
    return Path(__file__).resolve().parents[2].parent / "proc_suite_notes" / "new_synthetic_notes_3_5_26"


def _load_march_2026_note(*, batch: str, note_name: str) -> str:
    note_path = _march_2026_notes_dir() / batch / f"{note_name}.txt"
    if not note_path.is_file():
        raise FileNotFoundError(note_path)
    return note_path.read_text(encoding="utf-8")


def _extract_fields_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    return RegistryService().extract_fields(note_text)


@pytest.mark.parametrize("note_name", ["note_004", "note_039"])
def test_real_notes_routine_hemostasis_do_not_create_bleeding_complication(
    monkeypatch: pytest.MonkeyPatch,
    note_name: str,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_1", note_name=note_name)
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    complications = result.record.complications

    if complications is None:
        return

    assert complications.any_complication is not True
    assert not any("bleeding" in str(item).lower() for item in (complications.complication_list or []))
    bleeding = complications.bleeding
    assert bleeding is None or bleeding.occurred is not True
    assert bleeding is None or bleeding.bleeding_grade_nashville in (None, 0)


def test_real_note_009_negated_endobronchial_lesion_is_not_preserved_in_inspection_findings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_6", note_name="note_009")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    procedures = result.record.procedures_performed
    assert procedures is not None

    diagnostic = procedures.diagnostic_bronchoscopy
    assert diagnostic is not None
    assert diagnostic.performed is True

    findings = (diagnostic.inspection_findings or "").lower()
    assert "lesion" not in findings
    assert "tumor" not in findings
    assert "mass" not in findings

    abnormalities = [str(item).lower() for item in (diagnostic.airway_abnormalities or [])]
    assert not any("lesion" in item or "tumor" in item or "mass" in item for item in abnormalities)
