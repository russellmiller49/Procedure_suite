from app.registry.application.quality_passes import (
    QualitySignal,
    quality_signals_to_legacy_warnings,
)
from app.registry.application.registry_service import RegistryService


def test_quality_signal_adapter_preserves_legacy_warning_order() -> None:
    signals = [
        QualitySignal(
            version="quality_signal.v1",
            phase="phase_a",
            signal_type="legacy_warning",
            code="FIRST",
            severity="warning",
            message="FIRST: something happened",
            legacy_warning="FIRST: something happened",
        ),
        QualitySignal(
            version="quality_signal.v1",
            phase="phase_b",
            signal_type="source_type",
            code="SOURCE_TYPE",
            severity="info",
            message="source_type=masked_note_text",
        ),
        QualitySignal(
            version="quality_signal.v1",
            phase="phase_c",
            signal_type="legacy_warning",
            code="SECOND",
            severity="review",
            message="NEEDS_REVIEW: check this",
            legacy_warning="NEEDS_REVIEW: check this",
        ),
    ]

    assert quality_signals_to_legacy_warnings(signals) == [
        "FIRST: something happened",
        "NEEDS_REVIEW: check this",
    ]


def test_extract_fields_extraction_first_records_quality_pass_metadata() -> None:
    note_text = """
PROCEDURE:
Flexible bronchoscopy with bronchoalveolar lavage.

PROCEDURE IN DETAIL:
Flexible bronchoscopy was performed. Bronchoalveolar lavage was performed in the right middle lobe.
No immediate complications.
""".strip()

    result = RegistryService().extract_fields(note_text)

    assert result.quality_phase_order == [
        "masked_text_prep",
        "deterministic_uplift",
        "narrative_template_reconciliation",
        "precision_guardrails",
        "evidence_verification",
        "cpt_derivation",
        "omission_audit",
    ]
    assert result.quality_signals
    assert any(signal.signal_type == "source_type" for signal in result.quality_signals)
