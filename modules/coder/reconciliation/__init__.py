"""Reconciliation module for extraction-first architecture.

This module provides the double-check mechanism that compares:
- Path A (Extraction): Registry Extraction → Deterministic CPT Derivation
- Path B (Prediction): Legacy ML/LLM → Probabilistic CPT Prediction

The reconciliation logic identifies discrepancies and provides recommendations
for human review when the two paths disagree.

Usage:
    from modules.coder.reconciliation import CodeReconciler, reconcile_codes

    reconciler = CodeReconciler()
    result = reconciler.reconcile(
        derived_codes=["31653", "31624"],
        predicted_codes=["31653", "31624", "31625"],
    )

    print(f"Recommendation: {result.recommendation}")
    print(f"Prediction-only codes: {result.prediction_only}")

    # Full pipeline usage
    from modules.coder.reconciliation import run_extraction_first_pipeline

    result = run_extraction_first_pipeline(note_text)
    print(f"Final codes: {result.final_codes}")
"""

from modules.coder.reconciliation.reconciler import (
    CodeReconciler,
    ReconciliationResult,
    DiscrepancyType,
    reconcile_codes,
)
from modules.coder.reconciliation.pipeline import (
    ExtractionFirstPipeline,
    PipelineResult,
    run_extraction_first_pipeline,
)

__all__ = [
    "CodeReconciler",
    "ReconciliationResult",
    "DiscrepancyType",
    "reconcile_codes",
    "ExtractionFirstPipeline",
    "PipelineResult",
    "run_extraction_first_pipeline",
]
