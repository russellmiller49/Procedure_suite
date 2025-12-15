from unittest.mock import MagicMock

import pytest

from modules.registry.application.registry_service import RegistryService
from modules.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        return RegistryRecord()


def _stub_raw_ml_high_conf(monkeypatch: pytest.MonkeyPatch, *, cpt: str, prob: float = 0.99) -> None:
    from modules.ml_coder.predictor import CaseClassification, CodePrediction, MLCoderPredictor
    from modules.ml_coder.thresholds import CaseDifficulty

    pred = CodePrediction(cpt=cpt, prob=prob)

    monkeypatch.setattr(MLCoderPredictor, "__init__", lambda self, *a, **k: None)
    monkeypatch.setattr(
        MLCoderPredictor,
        "classify_case",
        lambda self, raw_note_text: CaseClassification(
            predictions=[pred],
            high_conf=[pred],
            gray_zone=[],
            difficulty=CaseDifficulty.HIGH_CONF,
        ),
    )


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


def test_self_correction_successful_patch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")

    _stub_raw_ml_high_conf(monkeypatch, cpt="32550", prob=0.99)

    from modules.registry.self_correction.judge import PatchProposal, RegistryCorrectionJudge

    mocked = MagicMock(
        return_value=PatchProposal(
            rationale="Procedure explicitly documented",
            json_patch=[{"op": "add", "path": "/pleural_procedures/ipc/performed", "value": True}],
            evidence_quote="indwelling pleural catheter",
        )
    )
    monkeypatch.setattr(RegistryCorrectionJudge, "propose_correction", mocked)

    orchestrator = MagicMock()
    orchestrator.get_codes.side_effect = RuntimeError("SmartHybridOrchestrator.get_codes() called")

    service = RegistryService(hybrid_orchestrator=orchestrator, registry_engine=_StubRegistryEngine())
    note_text = (
        "PROCEDURE:\n"
        "The patient underwent insertion of an indwelling pleural catheter (PleurX).\n"
        "No complications."
    )
    result = service.extract_fields(note_text)

    assert "32550" in result.cpt_codes
    assert any(w.startswith("AUTO_CORRECTED: 32550") for w in result.warnings)
    mocked.assert_called()
    assert result.record.pleural_procedures is not None
    assert result.record.pleural_procedures.ipc is not None
    assert result.record.pleural_procedures.ipc.performed is True
    assert result.self_correction
    assert result.self_correction[0].trigger.target_cpt == "32550"


def test_self_correction_rejects_hallucinated_quote(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")

    _stub_raw_ml_high_conf(monkeypatch, cpt="32550", prob=0.99)

    from modules.registry.self_correction.judge import PatchProposal, RegistryCorrectionJudge

    def _hallucinating_judge(  # type: ignore[no-untyped-def]
        self,
        note_text: str,
        record: RegistryRecord,
        discrepancy: str,
        *,
        focused_procedure_text: str | None = None,
    ) -> PatchProposal:
        return PatchProposal(
            rationale="hallucinated for test",
            json_patch=[{"op": "add", "path": "/pleural_procedures/ipc/performed", "value": True}],
            evidence_quote="THIS QUOTE DOES NOT APPEAR IN THE NOTE",
        )

    monkeypatch.setattr(RegistryCorrectionJudge, "propose_correction", _hallucinating_judge)

    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=_StubRegistryEngine())
    result = service.extract_fields(
        "PROCEDURE:\nInsertion of an indwelling pleural catheter (PleurX).\nNo complications."
    )

    assert "32550" not in result.cpt_codes
    assert result.record.pleural_procedures is None
    assert any("SELF_CORRECT_SKIPPED: 32550" in w for w in result.warnings)


def test_self_correction_rejects_forbidden_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")

    _stub_raw_ml_high_conf(monkeypatch, cpt="32550", prob=0.99)

    from modules.registry.self_correction.judge import PatchProposal, RegistryCorrectionJudge

    def _forbidden_path_judge(  # type: ignore[no-untyped-def]
        self,
        note_text: str,
        record: RegistryRecord,
        discrepancy: str,
        *,
        focused_procedure_text: str | None = None,
    ) -> PatchProposal:
        return PatchProposal(
            rationale="forbidden path for test",
            json_patch=[{"op": "add", "path": "/patient_demographics/mrn", "value": "123"}],
            evidence_quote="Insertion of an indwelling pleural catheter",
        )

    monkeypatch.setattr(RegistryCorrectionJudge, "propose_correction", _forbidden_path_judge)

    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=_StubRegistryEngine())
    result = service.extract_fields(
        "PROCEDURE:\nInsertion of an indwelling pleural catheter (PleurX).\nNo complications."
    )

    assert "32550" not in result.cpt_codes
    assert result.record.pleural_procedures is None
    assert any("SELF_CORRECT_SKIPPED: 32550" in w for w in result.warnings)


def test_self_correction_not_run_when_auditor_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")

    from modules.registry.self_correction.judge import RegistryCorrectionJudge

    mocked = MagicMock()
    mocked.side_effect = RuntimeError("RegistryCorrectionJudge.propose_correction should not be called")
    monkeypatch.setattr(RegistryCorrectionJudge, "propose_correction", mocked)

    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=_StubRegistryEngine())
    service.extract_fields("Synthetic note text describing insertion of an indwelling pleural catheter (PleurX).")
    mocked.assert_not_called()


def test_self_correction_keyword_guard_skips_without_calling_judge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")

    _stub_raw_ml_high_conf(monkeypatch, cpt="32550", prob=0.99)

    from modules.registry.self_correction.judge import RegistryCorrectionJudge

    mocked = MagicMock()
    mocked.side_effect = RuntimeError("RegistryCorrectionJudge.propose_correction should not be called")
    monkeypatch.setattr(RegistryCorrectionJudge, "propose_correction", mocked)

    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=_StubRegistryEngine())
    result = service.extract_fields("PROCEDURE:\nBronchoscopy performed.\nNo complications.")

    mocked.assert_not_called()
    assert "32550" not in result.cpt_codes
    assert any("SELF_CORRECT_SKIPPED: 32550: keyword guard failed" in w for w in result.warnings)


def test_self_correction_evidence_must_be_in_focused_text_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "agents_focus_then_engine")

    _stub_raw_ml_high_conf(monkeypatch, cpt="32550", prob=0.99)

    from modules.registry.application import registry_service as registry_service_module

    def _focus(note_text: str) -> tuple[str, dict[str, object]]:
        return (
            "PROCEDURE:\nBronchoscopy performed.\nNo IPC placed.\nNo complications.",
            {"status": "ok"},
        )

    monkeypatch.setattr(registry_service_module, "focus_note_for_extraction", _focus)

    from modules.registry.self_correction.judge import PatchProposal, RegistryCorrectionJudge

    mocked = MagicMock(
        return_value=PatchProposal(
            rationale="unsupported evidence quote for focused text",
            json_patch=[{"op": "add", "path": "/pleural_procedures/ipc/performed", "value": True}],
            evidence_quote="PleurX",
        )
    )
    monkeypatch.setattr(RegistryCorrectionJudge, "propose_correction", mocked)

    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=_StubRegistryEngine())
    raw_note_text = (
        "HPI:\nPatient has a PleurX catheter in place.\n\n"
        "PROCEDURE:\nBronchoscopy performed.\nNo IPC placed.\nNo complications."
    )
    result = service.extract_fields(raw_note_text)

    mocked.assert_called()
    assert "32550" not in result.cpt_codes
    assert result.record.pleural_procedures is None
    assert any(
        "SELF_CORRECT_SKIPPED: 32550: Quote not found verbatim in focused procedure text" in w
        for w in result.warnings
    )
