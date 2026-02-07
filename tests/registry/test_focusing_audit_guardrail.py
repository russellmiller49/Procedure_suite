from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord


class _FocusSensitiveRegistryEngine:
    def __init__(self) -> None:
        self.note_texts: list[str] = []

    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        self.note_texts.append(note_text)

        # Simulate an extractor that would only detect IPC if the keyword is present.
        if "pleurx" in (note_text or "").lower():
            return RegistryRecord(pleural_procedures={"ipc": {"performed": True}})
        return RegistryRecord()


def _raise(*_args, **_kwargs):  # type: ignore[no-untyped-def]
    raise RuntimeError("Unexpected call in extraction-first audit path")


def test_focusing_can_change_extraction_but_auditor_uses_raw_text_and_report_flags_gap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "agents_focus_then_engine")
    monkeypatch.setenv("REGISTRY_ML_AUDIT_USE_BUCKETS", "1")
    monkeypatch.setenv("REGISTRY_ML_SELF_CORRECT_MIN_PROB", "0.95")

    # Guardrails: orchestrator/rules must never be invoked for audit compare.
    from app.coder.application.smart_hybrid_policy import SmartHybridOrchestrator
    from app.coder.rules_engine import CodingRulesEngine

    monkeypatch.setattr(SmartHybridOrchestrator, "get_codes", _raise)
    monkeypatch.setattr(CodingRulesEngine, "validate", _raise)

    # RAW-ML should see the raw note text and predict IPC.
    from ml.lib.ml_coder.predictor import CaseClassification, CodePrediction, MLCoderPredictor
    from ml.lib.ml_coder.thresholds import CaseDifficulty

    classify_calls: list[str] = []

    monkeypatch.setattr(MLCoderPredictor, "__init__", lambda self, *a, **k: None)

    def _fake_classify_case(self, note_text: str):  # type: ignore[no-untyped-def]
        classify_calls.append(note_text)
        return CaseClassification(
            predictions=[CodePrediction(cpt="32550", prob=0.97)],
            high_conf=[CodePrediction(cpt="32550", prob=0.97)],
            gray_zone=[],
            difficulty=CaseDifficulty.HIGH_CONF,
        )

    monkeypatch.setattr(MLCoderPredictor, "classify_case", _fake_classify_case)

    engine = _FocusSensitiveRegistryEngine()
    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=engine)

    raw_note = (
        "HPI: Recurrent malignant pleural effusion; plan for PleurX catheter.\n"
        "PROCEDURE: Diagnostic bronchoscopy only.\n"
        "FINDINGS: Airways normal.\n"
    )

    result = service.extract_fields(raw_note)

    assert classify_calls == [raw_note]
    assert engine.note_texts, "Deterministic extraction should run"
    assert "pleurx" not in engine.note_texts[0].lower(), "Focused text should omit HPI keyword"

    assert result.audit_report is not None
    assert [p.cpt for p in result.audit_report.missing_in_derived] == ["32550"]
    assert [p.cpt for p in result.audit_report.high_conf_omissions] == ["32550"]
    assert result.needs_manual_review is True

