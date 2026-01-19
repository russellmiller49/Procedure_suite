from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from modules.coder.application.smart_hybrid_policy import HybridCoderResult
from modules.ml_coder.thresholds import CaseDifficulty
from modules.registry.application.registry_service import RegistryService
from modules.registry.engine import RegistryEngine


def test_registry_llm_timeout_falls_back_to_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "current")
    monkeypatch.setenv("PROCSUITE_ALLOW_LEGACY_PIPELINES", "1")

    note_text = Path(
        "tests/fixtures/notes/kitchen_sink_ion_nav_ebus_fiducial_dilation.txt"
    ).read_text()

    engine = RegistryEngine()

    def _timeout(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise TimeoutError("simulated LLM timeout")

    monkeypatch.setattr(engine.llm_extractor, "extract", _timeout)

    orchestrator = MagicMock()
    orchestrator.get_codes.return_value = HybridCoderResult(
        codes=[],
        source="ml_rules_fastpath",
        difficulty=CaseDifficulty.HIGH_CONF,
        metadata={},
    )

    service = RegistryService(hybrid_orchestrator=orchestrator, registry_engine=engine)
    result = service.extract_fields(note_text)

    assert "REGISTRY_LLM_TIMEOUT_FALLBACK_TO_ENGINE" in result.warnings
    assert "NAVIGATION" in (result.record.procedure_families or [])
