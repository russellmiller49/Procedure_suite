from __future__ import annotations

from pathlib import Path

import pytest

from modules.registry.application.registry_service import RegistryService


def test_kitchen_sink_extraction_first_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "engine")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "1")

    note_text = Path(
        "tests/fixtures/notes/kitchen_sink_ion_nav_ebus_fiducial_dilation.txt"
    ).read_text()

    result = RegistryService().extract_fields(note_text)
    record = result.record

    assert "NAVIGATION" in (record.procedure_families or [])

    assert record.procedures_performed is not None

    assert record.procedures_performed.navigational_bronchoscopy is not None
    assert record.procedures_performed.navigational_bronchoscopy.performed is True

    assert record.procedures_performed.airway_dilation is not None
    assert record.procedures_performed.airway_dilation.performed is True

    assert record.procedures_performed.therapeutic_aspiration is not None
    assert record.procedures_performed.therapeutic_aspiration.performed is True

    assert record.procedures_performed.radial_ebus is not None
    assert record.procedures_performed.radial_ebus.performed is True

    assert record.procedures_performed.linear_ebus is not None
    assert record.procedures_performed.linear_ebus.performed is True

    assert "31626" in result.cpt_codes

    assert record.granular_data is not None
    assert record.granular_data.navigation_targets is not None
    assert record.granular_data.navigation_targets[0].fiducial_marker_placed is True
