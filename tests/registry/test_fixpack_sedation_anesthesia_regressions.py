from __future__ import annotations

from pathlib import Path
import re

import pytest

from app.registry.application.registry_service import RegistryService


_BATCH4_RESULTS_PATH = Path(__file__).resolve().parents[2] / "extraction_test_3_6" / "my_results_batch_4.txt"


def _load_batch4_note(note_name: str) -> str:
    if not _BATCH4_RESULTS_PATH.is_file():
        raise FileNotFoundError(_BATCH4_RESULTS_PATH)

    text = _BATCH4_RESULTS_PATH.read_text(encoding="utf-8")
    match = re.search(
        rf"=+\nNOTE: {re.escape(note_name)}\n=+\n\nNOTE TEXT:\n-+\n(?P<note>.*?)\n-+\n\nRESULTS \(JSON\):",
        text,
        re.S,
    )
    if not match:
        raise ValueError(f"Note {note_name} not found in {_BATCH4_RESULTS_PATH}")
    return match.group("note").strip()


def _extract_fields_parallel_ner(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")
    return RegistryService().extract_fields(note_text)


@pytest.mark.parametrize("note_name", ["note_019", "note_030"])
def test_real_batch4_ga_context_surfaces_general_sedation(
    monkeypatch: pytest.MonkeyPatch,
    note_name: str,
) -> None:
    note_text = _load_batch4_note(note_name)

    result = _extract_fields_parallel_ner(monkeypatch, note_text)

    assert result.record.sedation is not None
    assert result.record.sedation.type == "General"
    assert "99152" not in result.cpt_codes
    assert "99153" not in result.cpt_codes
