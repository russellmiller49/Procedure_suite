from unittest.mock import MagicMock

import pytest

from modules.registry.application.registry_service import RegistryService
from modules.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def __init__(self) -> None:
        self.note_texts: list[str] = []

    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        self.note_texts.append(note_text)
        return RegistryRecord(version="from-engine")


def test_agents_structurer_not_implemented_falls_back_to_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "agents_structurer")

    engine = _StubRegistryEngine()
    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=engine)

    record, warnings, meta = service.extract_record("PROCEDURE: Something happened.")

    assert record.version == "from-engine"
    assert engine.note_texts == ["PROCEDURE: Something happened."]
    assert meta["extraction_engine"] == "agents_structurer"
    assert meta.get("structurer_meta", {}).get("status") == "not_implemented"
    assert any("agents_structurer is not implemented yet" in w for w in warnings)

