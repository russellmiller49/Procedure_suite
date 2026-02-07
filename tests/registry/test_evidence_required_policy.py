from __future__ import annotations

from app.registry.application.registry_service import RegistryService
from app.registry.evidence.verifier import verify_evidence_integrity
from app.registry.schema import RegistryRecord


def test_evidence_required_hard_flips_airway_dilation_when_unsupported() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {"airway_dilation": {"performed": True}},
        }
    )
    updated, warnings = verify_evidence_integrity(record, "Diagnostic bronchoscopy performed.")
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.airway_dilation is not None
    assert updated.procedures_performed.airway_dilation.performed is False
    assert "EVIDENCE_HARD_FAIL: procedures_performed.airway_dilation.performed" in warnings


def test_evidence_required_review_keeps_rigid_bronchoscopy_and_flags_review() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {"rigid_bronchoscopy": {"performed": True}},
        }
    )
    updated, warnings = verify_evidence_integrity(record, "Flexible bronchoscopy performed.")
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.rigid_bronchoscopy is not None
    assert updated.procedures_performed.rigid_bronchoscopy.performed is True
    assert "NEEDS_REVIEW: EVIDENCE_MISSING: procedures_performed.rigid_bronchoscopy.performed" in warnings


def test_evidence_required_stent_assessment_only_exempt_from_hard_policy() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {"airway_stent": {"performed": True, "action": "Assessment only"}},
        }
    )
    updated, warnings = verify_evidence_integrity(record, "Flexible bronchoscopy performed.")
    assert updated.procedures_performed is not None
    assert updated.procedures_performed.airway_stent is not None
    assert updated.procedures_performed.airway_stent.performed is True
    assert not any(
        str(w).startswith("EVIDENCE_HARD_FAIL: procedures_performed.airway_stent.performed") for w in warnings
    )


def test_extraction_first_propagates_needs_manual_review_from_review_warning(monkeypatch) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "parallel_ner")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")

    class _StubOrchestrator:
        def process(self, note_text: str, ml_predictor=None):  # noqa: ANN001,ARG002
            from dataclasses import dataclass

            @dataclass
            class _Path:
                source: str
                codes: list[str]
                confidences: dict[str, float]
                rationales: dict[str, str]
                processing_time_ms: float
                details: dict

            @dataclass
            class _Result:
                final_codes: list[str]
                final_confidences: dict[str, float]
                path_a_result: _Path
                path_b_result: _Path
                needs_review: bool
                review_reasons: list[str]
                explanations: dict[str, str]
                total_time_ms: float

            record = RegistryRecord.model_validate(
                {"procedures_performed": {"rigid_bronchoscopy": {"performed": True}}}
            )
            return _Result(
                final_codes=[],
                final_confidences={},
                path_a_result=_Path(
                    source="ner_rules",
                    codes=[],
                    confidences={},
                    rationales={},
                    processing_time_ms=0.0,
                    details={"record": record, "ner_entities": []},
                ),
                path_b_result=_Path(
                    source="ml_classification",
                    codes=[],
                    confidences={},
                    rationales={},
                    processing_time_ms=0.0,
                    details={},
                ),
                needs_review=False,
                review_reasons=[],
                explanations={},
                total_time_ms=0.0,
            )

        def _build_ner_evidence(self, ner_entities):  # noqa: ANN001,ARG002
            return {}

    service = RegistryService(parallel_orchestrator=_StubOrchestrator())
    service._get_registry_ml_predictor = lambda: None  # type: ignore[method-assign]
    result = service.extract_fields("Flexible bronchoscopy performed.")

    assert any(str(w).startswith("NEEDS_REVIEW: EVIDENCE_MISSING:") for w in (result.warnings or []))
    assert result.needs_manual_review is True
