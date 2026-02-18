from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def run_with_warnings(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        record = RegistryRecord.model_validate(
            {
                "procedure_families": ["BLVR"],
                "procedures_performed": {"blvr": {"performed": True}},
            }
        )
        return record, []


def test_extraction_first_applies_modifier_22_from_apply_to_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=_StubRegistryEngine())

    note_text = (
        "22 Substantially greater work than normal.\n"
        "IP CODE MOD DETAILS:\n"
        "Unusual Procedure:\n"
        "This resulted in >50% increased work.\n"
        "Apply to: 31647 Bronchial valve insert initial lobe\n"
        "\n"
        "PROCEDURE IN DETAIL:\n"
        "Endobronchial valves were placed.\n"
    )

    result = service.extract_fields(note_text)

    assert result.record.billing is not None
    cpt = result.record.billing.cpt_codes or []
    match = next((item for item in cpt if str(item.code) == "31647"), None)
    assert match is not None
    assert "22" in (match.modifiers or [])

