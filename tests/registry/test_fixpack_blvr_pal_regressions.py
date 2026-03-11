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


def test_real_note_004_blvr_preserves_lul_count_and_bundles_same_session_chartis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_4", note_name="note_004")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    procedures = result.record.procedures_performed
    assert procedures is not None
    blvr = procedures.blvr
    assert blvr is not None
    assert blvr.performed is True
    assert blvr.procedure_type == "Valve placement"
    assert blvr.target_lobe == "LUL"
    assert blvr.number_of_valves == 4

    assert "31647" in result.cpt_codes
    assert "31634" not in result.cpt_codes


def test_real_note_007_checkbox_blvr_keeps_lul_and_four_valves(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_4", note_name="note_007")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    procedures = result.record.procedures_performed
    assert procedures is not None
    blvr = procedures.blvr
    assert blvr is not None
    assert blvr.performed is True
    assert blvr.procedure_type == "Valve placement"
    assert blvr.target_lobe == "LUL"
    assert blvr.number_of_valves == 4

    assert "31647" in result.cpt_codes
    assert "31634" not in result.cpt_codes


def test_real_note_018_pal_sequential_valves_keep_two_and_suppress_localization_31634(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_4", note_name="note_018")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    procedures = result.record.procedures_performed
    assert procedures is not None
    blvr = procedures.blvr
    assert blvr is not None
    assert blvr.performed is True
    assert blvr.procedure_type == "Valve placement"
    assert blvr.target_lobe == "RLL"
    assert blvr.number_of_valves == 2

    assert "31647" in result.cpt_codes
    assert "31634" not in result.cpt_codes
