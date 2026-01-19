from unittest.mock import MagicMock

import pytest

from modules.registry.application.registry_service import RegistryService
from modules.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def __init__(self, record: RegistryRecord) -> None:
        self.record = record
        self.note_texts: list[str] = []

    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        self.note_texts.append(note_text)
        return self.record


def _raise(*_args, **_kwargs):  # type: ignore[no-untyped-def]
    raise RuntimeError("Unexpected call in extraction-first audit path")


def test_audit_compare_report_computes_missing_sets_and_high_conf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("REGISTRY_ML_AUDIT_USE_BUCKETS", "1")
    monkeypatch.setenv("REGISTRY_ML_AUDIT_TOP_K", "7")
    monkeypatch.setenv("REGISTRY_ML_AUDIT_MIN_PROB", "0.42")
    monkeypatch.setenv("REGISTRY_ML_SELF_CORRECT_MIN_PROB", "0.95")

    # Guardrails: orchestrator/rules must never be invoked for audit compare.
    from modules.coder.application.smart_hybrid_policy import SmartHybridOrchestrator
    from modules.coder.rules_engine import CodingRulesEngine

    monkeypatch.setattr(SmartHybridOrchestrator, "get_codes", _raise)
    monkeypatch.setattr(CodingRulesEngine, "validate", _raise)

    # Deterministic derivation: derive 31624 via BAL performed.
    record = RegistryRecord(procedures_performed={"bal": {"performed": True}})
    engine = _StubRegistryEngine(record)

    # RAW-ML: high-conf suggests IPC (32550), but deterministic derivation misses it.
    from modules.ml_coder.predictor import CaseClassification, CodePrediction, MLCoderPredictor
    from modules.ml_coder.thresholds import CaseDifficulty

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

    service = RegistryService(
        hybrid_orchestrator=MagicMock(),
        registry_engine=engine,
    )

    raw_note = "HPI: Mentions tunneled pleural catheter.\n\nPROCEDURE: BAL performed."
    result = service.extract_fields(raw_note)

    assert classify_calls == [raw_note]
    assert result.audit_report is not None

    report = result.audit_report
    assert report.derived_codes == ["31624"]
    assert [p.cpt for p in report.ml_audit_codes] == ["32550"]
    assert [p.cpt for p in report.missing_in_derived] == ["32550"]
    assert report.missing_in_ml == ["31624"]
    assert [p.cpt for p in report.high_conf_omissions] == ["32550"]

    assert report.config.use_buckets is True
    assert report.config.top_k == 7
    assert report.config.min_prob == 0.42
    assert report.config.self_correct_min_prob == 0.95

    assert result.needs_manual_review is True
    assert any("32550" in w for w in result.audit_warnings)


def test_audit_compare_report_created_when_auditor_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_ML_AUDIT_USE_BUCKETS", "1")
    monkeypatch.setenv("REGISTRY_ML_AUDIT_TOP_K", "9")
    monkeypatch.setenv("REGISTRY_ML_AUDIT_MIN_PROB", "0.11")
    monkeypatch.setenv("REGISTRY_ML_SELF_CORRECT_MIN_PROB", "0.91")

    # Guardrails: orchestrator/rules must never be invoked for audit compare.
    from modules.coder.application.smart_hybrid_policy import SmartHybridOrchestrator
    from modules.coder.rules_engine import CodingRulesEngine

    monkeypatch.setattr(SmartHybridOrchestrator, "get_codes", _raise)
    monkeypatch.setattr(CodingRulesEngine, "validate", _raise)

    # RAW-ML must not run when auditor is disabled.
    from modules.ml_coder.predictor import MLCoderPredictor

    monkeypatch.setattr(MLCoderPredictor, "classify_case", _raise)

    record = RegistryRecord(procedures_performed={"bal": {"performed": True}})
    service = RegistryService(
        hybrid_orchestrator=MagicMock(),
        registry_engine=_StubRegistryEngine(record),
    )

    result = service.extract_fields("PROCEDURE: BAL performed.")
    assert result.audit_report is not None

    report = result.audit_report
    assert report.ml_audit_codes == []
    assert report.missing_in_derived == []
    assert report.high_conf_omissions == []
    assert report.missing_in_ml == ["31624"]
    assert any("REGISTRY_AUDITOR_SOURCE=disabled" in w for w in report.warnings)
    assert result.audit_warnings == []
    assert result.needs_manual_review is False


def test_audit_compare_report_treats_equivalent_codes_as_not_missing() -> None:
    from modules.ml_coder.predictor import CaseClassification, CodePrediction
    from modules.ml_coder.thresholds import CaseDifficulty
    from modules.registry.audit.compare import build_audit_compare_report
    from modules.registry.audit.raw_ml_auditor import RawMLAuditConfig

    cfg = RawMLAuditConfig(
        use_buckets=True,
        top_k=25,
        min_prob=0.50,
        self_correct_min_prob=0.95,
    )

    preds = [
        CodePrediction(cpt="31652", prob=0.99),  # linear EBUS (1-2) vs 31653
        CodePrediction(cpt="32554", prob=0.99),  # thoracentesis no imaging vs 32555
        CodePrediction(cpt="31640", prob=0.99),  # excision vs 31641
    ]
    ml_case = CaseClassification(
        predictions=preds,
        high_conf=preds,
        gray_zone=[],
        difficulty=CaseDifficulty.HIGH_CONF,
    )

    report = build_audit_compare_report(
        derived_codes=["31653", "32555", "31641"],
        cfg=cfg,
        ml_case=ml_case,
        audit_preds=preds,
    )

    assert [p.cpt for p in report.missing_in_derived] == []
    assert report.high_conf_omissions == []
