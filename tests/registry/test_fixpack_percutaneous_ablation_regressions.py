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


def test_real_note_002_percutaneous_cryoablation_does_not_route_to_bronchoscopic_cryotherapy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    try:
        note_text = _load_march_2026_note(batch="batch_5", note_name="note_002")
    except FileNotFoundError as exc:
        pytest.skip(f"Fixture note not available: {exc}")

    result = _extract_fields_parallel_ner(monkeypatch, note_text)
    procedures = result.record.procedures_performed
    assert procedures is not None

    cryotherapy = procedures.cryotherapy
    assert cryotherapy is None or cryotherapy.performed is not True

    thermal = procedures.thermal_ablation
    assert thermal is None or thermal.performed is not True

    peripheral_ablation = procedures.peripheral_ablation
    assert peripheral_ablation is None or peripheral_ablation.performed is not True

    diagnostic = procedures.diagnostic_bronchoscopy
    assert diagnostic is None or diagnostic.performed is not True

    assert "31641" not in result.cpt_codes
