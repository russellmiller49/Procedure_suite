"""Parallel pathway CPT coding module.

Combines deterministic NER+Rules pathway with probabilistic ML classification
for robust CPT code derivation with reconciliation and review flagging.
"""

from modules.coder.parallel_pathway.orchestrator import (
    ParallelPathwayOrchestrator,
    ParallelPathwayResult,
    PathwayResult,
)
from modules.coder.parallel_pathway.confidence_combiner import (
    ConfidenceCombiner,
    ConfidenceFactors,
)
from modules.coder.parallel_pathway.reconciler import CodeReconciler, ReconciledCode

__all__ = [
    "ParallelPathwayOrchestrator",
    "ParallelPathwayResult",
    "PathwayResult",
    "ConfidenceCombiner",
    "ConfidenceFactors",
    "CodeReconciler",
    "ReconciledCode",
]
