from unittest.mock import MagicMock

import pytest

from modules.registry.application.registry_service import RegistryService
from modules.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        return RegistryRecord()


def test_self_correction_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.delenv("REGISTRY_SELF_CORRECT_ENABLED", raising=False)

    orchestrator = MagicMock()
    orchestrator.get_codes.side_effect = RuntimeError("SmartHybridOrchestrator.get_codes() called")

    # Stub RAW-ML predictor so the extraction-first path can complete once implemented.
    from modules.ml_coder.predictor import CaseClassification, MLCoderPredictor
    from modules.ml_coder.thresholds import CaseDifficulty

    monkeypatch.setattr(MLCoderPredictor, "__init__", lambda self, *a, **k: None)
    monkeypatch.setattr(
        MLCoderPredictor,
        "classify_case",
        lambda self, raw_note_text: CaseClassification(
            predictions=[],
            high_conf=[],
            gray_zone=[],
            difficulty=CaseDifficulty.LOW_CONF,
        ),
    )

    service = RegistryService(hybrid_orchestrator=orchestrator, registry_engine=_StubRegistryEngine())
    service.extract_fields("Synthetic note text describing a bronchoscopy procedure.")
