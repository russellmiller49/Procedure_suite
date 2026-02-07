from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def __init__(self) -> None:
        self.note_texts: list[str] = []

    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        self.note_texts.append(note_text)
        return RegistryRecord()


def test_registry_audit_calls_raw_ml_predictor_directly(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")

    # If the extraction-first path consults the orchestrator, this should explode.
    from app.coder.application.smart_hybrid_policy import SmartHybridOrchestrator

    monkeypatch.setattr(
        SmartHybridOrchestrator,
        "get_codes",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("SmartHybridOrchestrator.get_codes() called")),
    )

    orchestrator = MagicMock()
    orchestrator.get_codes.side_effect = RuntimeError("SmartHybridOrchestrator.get_codes() called")

    # If anything tries to invoke coder rules validation during audit, explode.
    from app.coder.rules_engine import CodingRulesEngine

    monkeypatch.setattr(
        CodingRulesEngine,
        "validate",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("CodingRulesEngine.validate() called")),
    )

    raw_note_text = "RAW NOTE: EBUS bronchoscopy performed. Station 7 sampled."

    from ml.lib.ml_coder.predictor import CaseClassification, MLCoderPredictor
    from ml.lib.ml_coder.thresholds import CaseDifficulty

    classify_calls: list[str] = []

    monkeypatch.setattr(MLCoderPredictor, "__init__", lambda self, *a, **k: None)

    def _fake_classify_case(self, note_text: str):  # type: ignore[no-untyped-def]
        classify_calls.append(note_text)
        return CaseClassification(
            predictions=[],
            high_conf=[],
            gray_zone=[],
            difficulty=CaseDifficulty.LOW_CONF,
        )

    monkeypatch.setattr(MLCoderPredictor, "classify_case", _fake_classify_case)

    service = RegistryService(
        hybrid_orchestrator=orchestrator,
        registry_engine=_StubRegistryEngine(),
    )

    service.extract_fields(raw_note_text)

    assert classify_calls == [raw_note_text]


def test_auditor_uses_raw_note_text_even_when_focusing_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "agents_focus_then_engine")

    from app.coder.application.smart_hybrid_policy import SmartHybridOrchestrator

    monkeypatch.setattr(
        SmartHybridOrchestrator,
        "get_codes",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("SmartHybridOrchestrator.get_codes() called")),
    )

    from app.coder.rules_engine import CodingRulesEngine

    monkeypatch.setattr(
        CodingRulesEngine,
        "validate",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("CodingRulesEngine.validate() called")),
    )

    raw_note_text = "RAW NOTE: Procedure section says BAL and navigation."
    focused_text = "FOCUSED NOTE: only procedure summary"

    import app.registry.application.registry_service as registry_service_module

    def _fake_focus(note_text: str):  # type: ignore[no-untyped-def]
        assert note_text == raw_note_text
        return focused_text, {"focused": True}

    # This helper will be introduced in Phase 2; set raising=False so the test
    # can be added before the implementation exists.
    monkeypatch.setattr(
        registry_service_module,
        "focus_note_for_extraction",
        _fake_focus,
        raising=False,
    )

    engine = _StubRegistryEngine()

    orchestrator = MagicMock()
    orchestrator.get_codes.side_effect = RuntimeError("SmartHybridOrchestrator.get_codes() called")

    from ml.lib.ml_coder.predictor import CaseClassification, MLCoderPredictor
    from ml.lib.ml_coder.thresholds import CaseDifficulty

    classify_calls: list[str] = []
    monkeypatch.setattr(MLCoderPredictor, "__init__", lambda self, *a, **k: None)
    monkeypatch.setattr(
        MLCoderPredictor,
        "classify_case",
        lambda self, note_text: (
            classify_calls.append(note_text)
            or CaseClassification(
                predictions=[],
                high_conf=[],
                gray_zone=[],
                difficulty=CaseDifficulty.LOW_CONF,
            )
        ),
    )

    service = RegistryService(hybrid_orchestrator=orchestrator, registry_engine=engine)
    service.extract_fields(raw_note_text)

    assert engine.note_texts == [focused_text]
    assert classify_calls == [raw_note_text]
