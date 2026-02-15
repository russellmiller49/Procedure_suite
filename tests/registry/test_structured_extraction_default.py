from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def __init__(self) -> None:
        self.note_texts: list[str] = []

    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        self.note_texts.append(note_text)
        return RegistryRecord(version="from-engine")


def test_structured_extraction_default_uses_engine_when_llm_unconfigured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Baseline test env sets stub/offline; with engine unset the service should
    # choose legacy `engine` without emitting structurer-unavailable warnings.
    monkeypatch.delenv("REGISTRY_EXTRACTION_ENGINE", raising=False)
    monkeypatch.delenv("STRUCTURED_EXTRACTION_ENABLED", raising=False)

    engine = _StubRegistryEngine()
    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=engine)

    record, warnings, meta = service.extract_record("PROCEDURE: Something happened.")

    assert record.version == "from-engine"
    assert engine.note_texts == ["PROCEDURE: Something happened."]
    assert meta["extraction_engine"] == "engine"
    assert not any("agents_structurer unavailable" in str(w).lower() for w in warnings)

