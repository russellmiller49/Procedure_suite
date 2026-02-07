import inspect
from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


class _AssertingRegistryEngine:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def run(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("RegistryEngine.run called (expected run_with_warnings)")

    def run_with_warnings(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        self.calls.append({"note_text": note_text, "context": context})
        if context is not None:
            assert "verified_cpt_codes" not in context
            assert "ml_metadata" not in context
        return RegistryRecord(), ["ENGINE_WARNING"]


def test_extraction_first_does_not_consult_cpt_or_orchestrator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")

    engine = _AssertingRegistryEngine()

    orchestrator = MagicMock()
    orchestrator.get_codes.side_effect = RuntimeError("orchestrator called (should not happen)")

    service = RegistryService(hybrid_orchestrator=orchestrator, registry_engine=engine)

    # Guard against CPT-seeded merge in extraction-first mode.
    monkeypatch.setattr(
        service,
        "_merge_cpt_fields_into_record",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("_merge_cpt_fields_into_record called")),
    )

    # Stub RAW-ML predictor so the extraction-first path can complete once implemented.
    from ml.lib.ml_coder.predictor import CaseClassification, MLCoderPredictor
    from ml.lib.ml_coder.thresholds import CaseDifficulty

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

    result = service.extract_fields("Synthetic note text describing a bronchoscopy procedure.")

    # The test is primarily a call-graph guardrail:
    # - No orchestrator
    # - No CPT merge
    # - No CPT hints passed into extraction
    assert orchestrator.get_codes.call_count == 0
    assert engine.calls, "expected extractor to run"
    assert isinstance(result.record, RegistryRecord)
    assert "ENGINE_WARNING" in result.warnings
