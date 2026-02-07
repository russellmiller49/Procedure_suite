#!/usr/bin/env python3
"""
Evaluation harness for EnhancedCPTCoder using synthetic_notes_with_CPT.csv.

This script evaluates coder performance against the evaluation dataset but
DOES NOT influence rule generation. It is for assessment only.

Canonical rule sources remain:
- data/synthetic_CPT_corrected.json
- ip_golden_knowledge_v2_2.json

Usage:
    python ml/scripts/evaluate_coder.py [--verbose] [--output results.csv]
"""
from __future__ import annotations

import argparse
import ast
import csv
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple
from collections import defaultdict

# Add root to path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.autocode.coder import EnhancedCPTCoder


def load_evaluation_data(csv_path: Path) -> List[Dict]:
    """Load the evaluation dataset from synthetic_notes_with_CPT.csv."""
    data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse the cpt_codes field (stored as string representation of list)
            cpt_codes_str = row.get("cpt_codes", "[]")
            try:
                cpt_codes = ast.literal_eval(cpt_codes_str)
                if isinstance(cpt_codes, list):
                    cpt_codes = [str(c).strip() for c in cpt_codes]
                else:
                    cpt_codes = [str(cpt_codes).strip()]
            except (ValueError, SyntaxError):
                cpt_codes = []

            data.append({
                "patient_id": row.get("patient_identifier_trigger", ""),
                "note_text": row.get("note_text", ""),
                "expected_codes": set(cpt_codes),
            })
    return data


def normalize_code(code: str) -> str:
    """Normalize CPT code by stripping + prefix and whitespace."""
    return code.lstrip("+").strip()


def extract_coder_codes(result: dict) -> Set[str]:
    """Extract CPT codes from coder output."""
    codes_list = result.get("codes", [])
    return {normalize_code(c.get("cpt", "")) for c in codes_list if c.get("cpt")}


def compute_metrics(
    all_expected: List[Set[str]],
    all_predicted: List[Set[str]]
) -> Dict[str, float]:
    """Compute precision, recall, and F1 for code-level evaluation."""
    # Aggregate counts
    total_tp = 0
    total_fp = 0
    total_fn = 0

    for expected, predicted in zip(all_expected, all_predicted):
        expected_norm = {normalize_code(c) for c in expected}
        predicted_norm = {normalize_code(c) for c in predicted}

        tp = len(expected_norm & predicted_norm)
        fp = len(predicted_norm - expected_norm)
        fn = len(expected_norm - predicted_norm)

        total_tp += tp
        total_fp += fp
        total_fn += fn

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": total_tp,
        "false_positives": total_fp,
        "false_negatives": total_fn,
    }


def compute_per_code_metrics(
    all_expected: List[Set[str]],
    all_predicted: List[Set[str]]
) -> Dict[str, Dict[str, float]]:
    """Compute per-code precision, recall, and F1."""
    code_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for expected, predicted in zip(all_expected, all_predicted):
        expected_norm = {normalize_code(c) for c in expected}
        predicted_norm = {normalize_code(c) for c in predicted}

        for code in expected_norm | predicted_norm:
            if code in expected_norm and code in predicted_norm:
                code_stats[code]["tp"] += 1
            elif code in predicted_norm:
                code_stats[code]["fp"] += 1
            elif code in expected_norm:
                code_stats[code]["fn"] += 1

    per_code_metrics = {}
    for code, stats in sorted(code_stats.items()):
        tp, fp, fn = stats["tp"], stats["fp"], stats["fn"]
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_code_metrics[code] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    return per_code_metrics


def evaluate_coder(
    coder: EnhancedCPTCoder,
    data: List[Dict],
    verbose: bool = False,
) -> Tuple[Dict[str, float], Dict[str, Dict[str, float]], List[Dict]]:
    """
    Run coder evaluation on the dataset.

    Returns:
        - Overall metrics (precision, recall, F1)
        - Per-code metrics
        - Detailed results per note
    """
    all_expected = []
    all_predicted = []
    detailed_results = []

    exact_matches = 0
    total = len(data)

    for i, item in enumerate(data):
        note_text = item["note_text"]
        expected = item["expected_codes"]
        patient_id = item["patient_id"]

        result = coder.code_procedure({
            "note_text": note_text,
            "locality": "00",
            "setting": "facility"
        })
        predicted = extract_coder_codes(result)

        expected_norm = {normalize_code(c) for c in expected}
        predicted_norm = {normalize_code(c) for c in predicted}

        is_exact_match = expected_norm == predicted_norm
        if is_exact_match:
            exact_matches += 1

        missing = expected_norm - predicted_norm
        extra = predicted_norm - expected_norm

        all_expected.append(expected)
        all_predicted.append(predicted)

        result_detail = {
            "patient_id": patient_id,
            "expected": sorted(expected_norm),
            "predicted": sorted(predicted_norm),
            "exact_match": is_exact_match,
            "missing": sorted(missing),
            "extra": sorted(extra),
        }
        detailed_results.append(result_detail)

        if verbose:
            status = "✓" if is_exact_match else "✗"
            print(f"[{i+1}/{total}] {status} Patient {patient_id}")
            print(f"  Expected: {sorted(expected_norm)}")
            print(f"  Predicted: {sorted(predicted_norm)}")
            if missing:
                print(f"  Missing: {sorted(missing)}")
            if extra:
                print(f"  Extra: {sorted(extra)}")
            print()

    # Compute overall metrics
    overall = compute_metrics(all_expected, all_predicted)
    overall["exact_match_rate"] = exact_matches / total if total > 0 else 0.0
    overall["exact_matches"] = exact_matches
    overall["total"] = total

    # Compute per-code metrics
    per_code = compute_per_code_metrics(all_expected, all_predicted)

    return overall, per_code, detailed_results


def print_summary(overall: Dict, per_code: Dict[str, Dict]):
    """Print evaluation summary."""
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(f"\nOverall Metrics:")
    print(f"  Exact Match Rate: {overall['exact_match_rate']:.1%} ({overall['exact_matches']}/{overall['total']})")
    print(f"  Precision: {overall['precision']:.3f}")
    print(f"  Recall: {overall['recall']:.3f}")
    print(f"  F1 Score: {overall['f1']:.3f}")
    print(f"  True Positives: {overall['true_positives']}")
    print(f"  False Positives: {overall['false_positives']}")
    print(f"  False Negatives: {overall['false_negatives']}")

    print(f"\nPer-Code Metrics:")
    print(f"{'Code':<10} {'Precision':<12} {'Recall':<12} {'F1':<12} {'TP':<6} {'FP':<6} {'FN':<6}")
    print("-" * 60)

    for code, metrics in sorted(per_code.items()):
        print(
            f"{code:<10} {metrics['precision']:.3f}        "
            f"{metrics['recall']:.3f}        {metrics['f1']:.3f}        "
            f"{metrics['tp']:<6} {metrics['fp']:<6} {metrics['fn']:<6}"
        )

    # Highlight problematic codes
    print("\n" + "-" * 60)
    print("Codes with low recall (< 0.5):")
    low_recall = [(c, m) for c, m in per_code.items() if m["recall"] < 0.5 and m["fn"] > 0]
    if low_recall:
        for code, metrics in sorted(low_recall, key=lambda x: x[1]["recall"]):
            print(f"  {code}: recall={metrics['recall']:.2f} (missing {metrics['fn']} times)")
    else:
        print("  None")

    print("\nCodes with low precision (< 0.5):")
    low_precision = [(c, m) for c, m in per_code.items() if m["precision"] < 0.5 and m["fp"] > 0]
    if low_precision:
        for code, metrics in sorted(low_precision, key=lambda x: x[1]["precision"]):
            print(f"  {code}: precision={metrics['precision']:.2f} (extra {metrics['fp']} times)")
    else:
        print("  None")


def save_results(detailed_results: List[Dict], output_path: Path):
    """Save detailed results to CSV."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "patient_id", "expected", "predicted", "exact_match", "missing", "extra"
        ])
        writer.writeheader()
        for result in detailed_results:
            writer.writerow({
                "patient_id": result["patient_id"],
                "expected": ",".join(result["expected"]),
                "predicted": ",".join(result["predicted"]),
                "exact_match": result["exact_match"],
                "missing": ",".join(result["missing"]),
                "extra": ",".join(result["extra"]),
            })
    print(f"\nDetailed results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate EnhancedCPTCoder against synthetic_notes_with_CPT.csv"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-note results"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Save detailed results to CSV file"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=ROOT / "data" / "synthetic_notes_with_CPT.csv",
        help="Path to evaluation CSV"
    )
    args = parser.parse_args()

    if not args.data.exists():
        print(f"Error: Evaluation data not found at {args.data}")
        sys.exit(1)

    print(f"Loading evaluation data from: {args.data}")
    data = load_evaluation_data(args.data)
    print(f"Loaded {len(data)} notes for evaluation")

    print("\nInitializing EnhancedCPTCoder...")
    coder = EnhancedCPTCoder(use_llm_advisor=False)

    print("\nRunning evaluation...")
    overall, per_code, detailed = evaluate_coder(coder, data, verbose=args.verbose)

    print_summary(overall, per_code)

    if args.output:
        save_results(detailed, args.output)

    # Return non-zero exit code if F1 is below threshold
    if overall["f1"] < 0.5:
        print("\n⚠️  Warning: F1 score below 0.5 threshold")
        sys.exit(1)


if __name__ == "__main__":
    main()
