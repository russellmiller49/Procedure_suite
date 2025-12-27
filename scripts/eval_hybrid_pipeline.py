#!/usr/bin/env python3
"""
Evaluation script for the ML-first Smart Hybrid Pipeline.

Compares:
- Old pipeline: ML-only predictions
- New pipeline: SmartHybridOrchestrator (ML → Rules → LLM)

Evaluates against:
- data/ml_training/test.csv (standard holdout)
- data/ml_training/edge_cases_holdout.csv (synthetic edge cases)

Output metrics:
- Per-code P/R/F1
- Overall micro/macro F1
- LLM usage rate (when LLM fallback was triggered)
- Fast path rate (ML+Rules without LLM)
- Rules rejection/modification rate
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

import pandas as pd

# Ensure imports resolve
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ml_coder.predictor import MLCoderPredictor
from modules.coder.rules_engine import CodingRulesEngine
from modules.coder.adapters.llm.gemini_advisor import MockLLMAdvisor, LLMCodeSuggestion
from modules.coder.application.smart_hybrid_policy import (
    SmartHybridOrchestrator,
    OrchestratorResult,
)


@dataclass
class CodeMetrics:
    """Per-code evaluation metrics."""
    tp: int = 0
    fp: int = 0
    fn: int = 0

    @property
    def precision(self) -> float:
        if self.tp + self.fp == 0:
            return 0.0
        return self.tp / (self.tp + self.fp)

    @property
    def recall(self) -> float:
        if self.tp + self.fn == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
        }


@dataclass
class EvalResult:
    """Overall evaluation results."""
    dataset_name: str
    total_samples: int
    exact_match: int = 0
    ml_only_exact_match: int = 0

    # Per-code metrics
    per_code_metrics: Dict[str, CodeMetrics] = field(default_factory=dict)
    ml_only_per_code: Dict[str, CodeMetrics] = field(default_factory=dict)

    # Pipeline behavior
    llm_called_count: int = 0
    fast_path_count: int = 0
    rules_modified_count: int = 0

    # Difficulty distribution
    high_conf_count: int = 0
    gray_zone_count: int = 0
    low_conf_count: int = 0

    # Errors
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def micro_f1(self, metrics: Dict[str, CodeMetrics]) -> float:
        """Calculate micro-averaged F1."""
        total_tp = sum(m.tp for m in metrics.values())
        total_fp = sum(m.fp for m in metrics.values())
        total_fn = sum(m.fn for m in metrics.values())

        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0

        if precision + recall == 0:
            return 0.0
        return 2 * precision * recall / (precision + recall)

    def macro_f1(self, metrics: Dict[str, CodeMetrics]) -> float:
        """Calculate macro-averaged F1."""
        if not metrics:
            return 0.0
        f1_scores = [m.f1 for m in metrics.values()]
        return sum(f1_scores) / len(f1_scores)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "total_samples": self.total_samples,
            "hybrid_pipeline": {
                "exact_match": self.exact_match,
                "exact_match_rate": round(self.exact_match / max(1, self.total_samples), 4),
                "micro_f1": round(self.micro_f1(self.per_code_metrics), 4),
                "macro_f1": round(self.macro_f1(self.per_code_metrics), 4),
                "per_code": {k: v.to_dict() for k, v in sorted(self.per_code_metrics.items())},
            },
            "ml_only_baseline": {
                "exact_match": self.ml_only_exact_match,
                "exact_match_rate": round(self.ml_only_exact_match / max(1, self.total_samples), 4),
                "micro_f1": round(self.micro_f1(self.ml_only_per_code), 4),
                "macro_f1": round(self.macro_f1(self.ml_only_per_code), 4),
                "per_code": {k: v.to_dict() for k, v in sorted(self.ml_only_per_code.items())},
            },
            "pipeline_behavior": {
                "llm_called_count": self.llm_called_count,
                "llm_usage_rate": round(self.llm_called_count / max(1, self.total_samples), 4),
                "fast_path_count": self.fast_path_count,
                "fast_path_rate": round(self.fast_path_count / max(1, self.total_samples), 4),
                "rules_modified_count": self.rules_modified_count,
            },
            "difficulty_distribution": {
                "high_conf": self.high_conf_count,
                "gray_zone": self.gray_zone_count,
                "low_conf": self.low_conf_count,
            },
            "error_count": len(self.errors),
        }


def parse_codes(codes_str: str) -> Set[str]:
    """Parse comma-separated CPT codes into a set."""
    if pd.isna(codes_str) or not codes_str:
        return set()
    return set(c.strip() for c in str(codes_str).split(",") if c.strip())


def update_metrics(
    metrics: Dict[str, CodeMetrics],
    predicted: Set[str],
    gold: Set[str],
) -> None:
    """Update per-code metrics based on predicted vs gold codes."""
    # True positives
    for code in predicted & gold:
        if code not in metrics:
            metrics[code] = CodeMetrics()
        metrics[code].tp += 1

    # False positives
    for code in predicted - gold:
        if code not in metrics:
            metrics[code] = CodeMetrics()
        metrics[code].fp += 1

    # False negatives
    for code in gold - predicted:
        if code not in metrics:
            metrics[code] = CodeMetrics()
        metrics[code].fn += 1


class OracleMLBasedLLMAdvisor(MockLLMAdvisor):
    """
    Mock LLM advisor that returns gold labels for evaluation purposes.

    In production evaluation, we want to isolate the ML+Rules behavior,
    so we make the LLM an oracle that always returns the correct answer.
    This lets us measure how much the pipeline relies on LLM.
    """

    def __init__(self):
        super().__init__()
        self._gold_codes: Set[str] = set()

    def set_gold_codes(self, codes: Set[str]) -> None:
        """Set the gold codes for the current sample."""
        self._gold_codes = codes

    def suggest_codes(self, report_text: str) -> List[LLMCodeSuggestion]:
        return [
            LLMCodeSuggestion(code=c, confidence=0.95, rationale="Oracle response")
            for c in self._gold_codes
        ]

    def suggest_with_context(
        self, report_text: str, context: dict
    ) -> List[LLMCodeSuggestion]:
        return self.suggest_codes(report_text)


def evaluate_dataset(
    df: pd.DataFrame,
    dataset_name: str,
    ml_predictor: MLCoderPredictor,
    rules_engine: CodingRulesEngine,
    use_oracle_llm: bool = True,
    ml_threshold: float = 0.5,
) -> EvalResult:
    """
    Evaluate the hybrid pipeline on a dataset.

    Args:
        df: DataFrame with note_text and verified_cpt_codes columns
        dataset_name: Name for reporting
        ml_predictor: ML predictor instance
        rules_engine: Rules engine instance
        use_oracle_llm: If True, use oracle LLM that returns gold codes
        ml_threshold: Threshold for ML-only baseline predictions

    Returns:
        EvalResult with all metrics
    """
    result = EvalResult(dataset_name=dataset_name, total_samples=len(df))

    # Create orchestrator with oracle LLM for evaluation
    oracle_llm = OracleMLBasedLLMAdvisor()
    orchestrator = SmartHybridOrchestrator(
        ml_predictor=ml_predictor,
        rules_engine=rules_engine,
        llm_advisor=oracle_llm,
    )

    for idx, row in df.iterrows():
        note_text = str(row["note_text"])
        gold_codes = parse_codes(row["verified_cpt_codes"])

        if not gold_codes:
            result.total_samples -= 1
            continue

        # Set oracle gold codes for this sample
        oracle_llm.set_gold_codes(gold_codes)

        try:
            # Run hybrid pipeline
            hybrid_result = orchestrator.get_codes(note_text)
            predicted = set(hybrid_result.codes)

            # Track pipeline behavior
            if hybrid_result.metadata.get("llm_called", False):
                result.llm_called_count += 1
            if hybrid_result.source == "ml_rules_fastpath":
                result.fast_path_count += 1

            # Check if rules modified the output
            ml_candidates = set(hybrid_result.metadata.get("ml_candidates", []))
            llm_raw = set(hybrid_result.metadata.get("llm_raw_codes", []))
            if ml_candidates != predicted and llm_raw != predicted:
                result.rules_modified_count += 1

            # Track difficulty distribution
            difficulty = hybrid_result.metadata.get("ml_difficulty", "")
            if "high" in difficulty:
                result.high_conf_count += 1
            elif "gray" in difficulty:
                result.gray_zone_count += 1
            else:
                result.low_conf_count += 1

            # Update hybrid metrics
            update_metrics(result.per_code_metrics, predicted, gold_codes)
            if predicted == gold_codes:
                result.exact_match += 1

            # ML-only baseline (no rules, no LLM)
            ml_only_codes = set(ml_predictor.predict(note_text, threshold=ml_threshold))
            update_metrics(result.ml_only_per_code, ml_only_codes, gold_codes)
            if ml_only_codes == gold_codes:
                result.ml_only_exact_match += 1

            # Log discrepancies for analysis
            if predicted != gold_codes:
                result.errors.append({
                    "idx": idx,
                    "note_preview": note_text[:200],
                    "gold": sorted(gold_codes),
                    "predicted": sorted(predicted),
                    "ml_only": sorted(ml_only_codes),
                    "source": hybrid_result.source,
                    "difficulty": difficulty,
                    "false_positives": sorted(predicted - gold_codes),
                    "false_negatives": sorted(gold_codes - predicted),
                })

        except Exception as e:
            result.errors.append({
                "idx": idx,
                "error": str(e),
                "note_preview": note_text[:200],
            })

    return result


def main():
    parser = argparse.ArgumentParser(description="Evaluate hybrid coding pipeline")
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=Path("data/ml_training/test.csv"),
        help="Path to test CSV",
    )
    parser.add_argument(
        "--edge-csv",
        type=Path,
        default=Path("data/ml_training/edge_cases_holdout.csv"),
        help="Path to edge cases CSV",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/eval_results"),
        help="Output directory for metrics JSON",
    )
    parser.add_argument(
        "--ml-threshold",
        type=float,
        default=0.5,
        help="Threshold for ML-only baseline predictions",
    )
    parser.add_argument(
        "--skip-edge",
        action="store_true",
        help="Skip edge cases evaluation",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading ML predictor...")
    ml_predictor = MLCoderPredictor()
    print(f"  Labels: {len(ml_predictor.labels)}")
    print(f"  Thresholds: upper={ml_predictor.thresholds.upper}, lower={ml_predictor.thresholds.lower}")

    print("\nLoading rules engine...")
    rules_engine = CodingRulesEngine()

    results = []

    # Evaluate test set
    if args.test_csv.exists():
        print(f"\nEvaluating test set: {args.test_csv}")
        test_df = pd.read_csv(args.test_csv)
        print(f"  Samples: {len(test_df)}")

        test_result = evaluate_dataset(
            test_df,
            "test_holdout",
            ml_predictor,
            rules_engine,
            ml_threshold=args.ml_threshold,
        )
        results.append(test_result)

        print(f"\n  Test Results (Hybrid Pipeline):")
        print(f"    Exact match rate: {test_result.exact_match}/{test_result.total_samples} ({test_result.exact_match/max(1,test_result.total_samples)*100:.1f}%)")
        print(f"    Micro F1: {test_result.micro_f1(test_result.per_code_metrics):.4f}")
        print(f"    Macro F1: {test_result.macro_f1(test_result.per_code_metrics):.4f}")
        print(f"\n  Test Results (ML-Only Baseline):")
        print(f"    Exact match rate: {test_result.ml_only_exact_match}/{test_result.total_samples} ({test_result.ml_only_exact_match/max(1,test_result.total_samples)*100:.1f}%)")
        print(f"    Micro F1: {test_result.micro_f1(test_result.ml_only_per_code):.4f}")
        print(f"\n  Pipeline Behavior:")
        print(f"    Fast path rate: {test_result.fast_path_count}/{test_result.total_samples} ({test_result.fast_path_count/max(1,test_result.total_samples)*100:.1f}%)")
        print(f"    LLM usage rate: {test_result.llm_called_count}/{test_result.total_samples} ({test_result.llm_called_count/max(1,test_result.total_samples)*100:.1f}%)")
        print(f"    Rules modified: {test_result.rules_modified_count}")
        print(f"\n  Difficulty Distribution:")
        print(f"    HIGH_CONF: {test_result.high_conf_count}")
        print(f"    GRAY_ZONE: {test_result.gray_zone_count}")
        print(f"    LOW_CONF: {test_result.low_conf_count}")
    else:
        print(f"\nTest CSV not found: {args.test_csv}")

    # Evaluate edge cases
    if not args.skip_edge and args.edge_csv.exists():
        print(f"\nEvaluating edge cases: {args.edge_csv}")
        edge_df = pd.read_csv(args.edge_csv)
        print(f"  Samples: {len(edge_df)}")

        edge_result = evaluate_dataset(
            edge_df,
            "edge_cases",
            ml_predictor,
            rules_engine,
            ml_threshold=args.ml_threshold,
        )
        results.append(edge_result)

        print(f"\n  Edge Case Results (Hybrid Pipeline):")
        print(f"    Exact match rate: {edge_result.exact_match}/{edge_result.total_samples} ({edge_result.exact_match/max(1,edge_result.total_samples)*100:.1f}%)")
        print(f"    Micro F1: {edge_result.micro_f1(edge_result.per_code_metrics):.4f}")
        print(f"\n  Edge Case Results (ML-Only Baseline):")
        print(f"    Exact match rate: {edge_result.ml_only_exact_match}/{edge_result.total_samples} ({edge_result.ml_only_exact_match/max(1,edge_result.total_samples)*100:.1f}%)")
        print(f"    Micro F1: {edge_result.micro_f1(edge_result.ml_only_per_code):.4f}")
        print(f"\n  Pipeline Behavior:")
        print(f"    Fast path rate: {edge_result.fast_path_count}/{edge_result.total_samples} ({edge_result.fast_path_count/max(1,edge_result.total_samples)*100:.1f}%)")
        print(f"    LLM usage rate: {edge_result.llm_called_count}/{edge_result.total_samples} ({edge_result.llm_called_count/max(1,edge_result.total_samples)*100:.1f}%)")
    elif not args.skip_edge:
        print(f"\nEdge cases CSV not found: {args.edge_csv}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = args.output_dir / f"eval_hybrid_{timestamp}.json"

    combined_results = {
        "timestamp": timestamp,
        "ml_threshold": args.ml_threshold,
        "datasets": [r.to_dict() for r in results],
    }

    with open(output_file, "w") as f:
        json.dump(combined_results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    # Also save errors log for analysis
    errors_file = args.output_dir / f"eval_errors_{timestamp}.jsonl"
    with open(errors_file, "w") as f:
        for result in results:
            for error in result.errors:
                error["dataset"] = result.dataset_name
                f.write(json.dumps(error) + "\n")

    if any(r.errors for r in results):
        print(f"Error log saved to: {errors_file}")


if __name__ == "__main__":
    main()
