from __future__ import annotations

from pathlib import Path

import pytest

from app.registry.application.registry_service import RegistryService


def test_note_279_regression_no_cryo_or_laser_hallucination(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")

    note_path = Path("data/granular annotations/Additional_notes/note_279.txt")
    if not note_path.is_file():
        pytest.skip(f"Fixture note not available: {note_path}")
    note_text = note_path.read_text(encoding="utf-8")

    # Ensure this fixture actually contains the CPT-definition bait text.
    assert "cryotherapy" in note_text.lower()
    assert "laser therapy" in note_text.lower()

    result = RegistryService().extract_fields(note_text)
    record = result.record
    procedures = getattr(record, "procedures_performed", None)
    assert procedures is not None

    outcomes = getattr(procedures, "therapeutic_outcomes", None)
    assert outcomes is not None
    assert getattr(outcomes, "pre_obstruction_pct", None) == 80
    assert getattr(outcomes, "post_obstruction_pct", None) == 60

    cryotherapy = getattr(procedures, "cryotherapy", None)
    assert cryotherapy is None or getattr(cryotherapy, "performed", None) is not True

    thermal_ablation = getattr(procedures, "thermal_ablation", None)
    assert thermal_ablation is None or getattr(thermal_ablation, "performed", None) is not True

    assert not any("HARD_OVERRIDE" in str(w) and "cryo" in str(w).lower() for w in result.warnings)
