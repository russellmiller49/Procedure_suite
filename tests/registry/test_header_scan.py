from unittest.mock import MagicMock

import pytest

from modules.registry.application.registry_service import (
    RegistryService,
    _extract_procedure_header_block,
    _scan_header_for_codes,
)
from modules.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        return RegistryRecord()


def _stub_raw_ml_empty(monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_header_scan_extracts_codes() -> None:
    note = (
        "HPI: cough and weight loss.\n"
        "PROCEDURE:\n"
        "31653 EBUS-TBNA of station 7.\n"
        "ANESTHESIA: General\n"
    )
    header = _extract_procedure_header_block(note)
    assert header is not None
    assert "31653" in header
    assert _scan_header_for_codes(note) == {"31653"}


def test_header_scan_skips_indication_for_operation_noise() -> None:
    note = (
        "INDICATION FOR OPERATION: 74 year old female with tracheal stenosis.\n"
        "PROCEDURE:\n"
        "31622 Dx bronchoscopy/cell washing\n"
        "PROCEDURE IN DETAIL: The airway was inspected.\n"
        "ANESTHESIA: General\n"
    )
    header = _extract_procedure_header_block(note)
    assert header is not None
    assert "31622" in header
    assert "tracheal stenosis" not in header.lower()
    assert _scan_header_for_codes(note) == {"31622"}


def test_header_trigger_adds_high_conf_omissions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")

    _stub_raw_ml_empty(monkeypatch)

    service = RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=_StubRegistryEngine())
    note_text = (
        "PROCEDURE:\n"
        "31653 EBUS-TBNA of station 7.\n"
        "ANESTHESIA: General\n"
    )
    result = service.extract_fields(note_text)

    assert result.audit_report is not None
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}
    assert omissions.get("31653") == "HEADER_EXPLICIT"
    assert any("HEADER_EXPLICIT:" in warning for warning in result.audit_warnings)
