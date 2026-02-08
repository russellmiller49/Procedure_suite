from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import RegistryService
from app.registry.schema import RegistryRecord
from ml.lib.ml_coder.predictor import MLCoderPredictor


class _StubRegistryEngine:
    def run(self, _note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        return RegistryRecord()


def test_extraction_first_raw_ml_missing_artifacts_does_not_crash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "engine")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")

    def _raise_missing_model(self, *_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise FileNotFoundError("data/models/cpt_classifier.pkl")

    monkeypatch.setattr(MLCoderPredictor, "__init__", _raise_missing_model)

    service = RegistryService(
        hybrid_orchestrator=None,
        registry_engine=_StubRegistryEngine(),
        parallel_orchestrator=MagicMock(),
    )

    result = service.extract_fields("PROCEDURE IN DETAIL: Diagnostic bronchoscopy was completed.")

    assert result.coder_difficulty == "unavailable"
    assert result.needs_manual_review is True
    assert any("RAW_ML_UNAVAILABLE" in warning for warning in result.audit_warnings)
    assert result.audit_report is not None
    assert any("RAW_ML_UNAVAILABLE" in warning for warning in result.audit_report.warnings)
