#!/usr/bin/env python3
"""
Error review pipeline for LLM fallback cases.

Identifies cases where:
- source="hybrid_llm_fallback" (LLM was used as final judge)
- prediction ≠ golden codes (the output was incorrect)

Outputs a review file with detailed context for manual inspection
and potential addition to training data.

Usage:
    python scripts/review_llm_fallback_errors.py
    python scripts/review_llm_fallback_errors.py --input data/eval_results/eval_errors_*.jsonl
    python scripts/review_llm_fallback_errors.py --run-fresh  # Re-run evaluation first
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


@dataclass
class ReviewCase:
    """A case requiring review."""
    idx: int
    dataset: str
    note_preview: str
    gold_codes: List[str]
    predicted_codes: List[str]
    ml_only_codes: List[str]
    source: str
    difficulty: str
    false_positives: List[str]
    false_negatives: List[str]
    fallback_reason: str = ""
    rules_error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "idx": self.idx,
            "dataset": self.dataset,
            "note_preview": self.note_preview,
            "gold_codes": self.gold_codes,
            "predicted_codes": self.predicted_codes,
            "ml_only_codes": self.ml_only_codes,
            "source": self.source,
            "difficulty": self.difficulty,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "fallback_reason": self.fallback_reason,
            "rules_error": self.rules_error,
        }


def load_errors_from_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load error cases from JSONL file."""
    errors = []
    with open(path) as f:
        for line in f:
            if line.strip():
                errors.append(json.loads(line))
    return errors


def filter_llm_fallback_errors(errors: List[Dict[str, Any]]) -> List[ReviewCase]:
    """Filter to only LLM fallback cases with prediction errors."""
    return filter_errors_by_source(errors, source_filter="hybrid_llm_fallback")


def filter_fastpath_errors(errors: List[Dict[str, Any]]) -> List[ReviewCase]:
    """Filter to only fast path (ML+Rules) cases with prediction errors."""
    return filter_errors_by_source(errors, source_filter="ml_rules_fastpath")


def filter_errors_by_source(
    errors: List[Dict[str, Any]],
    source_filter: str | None = None,
) -> List[ReviewCase]:
    """Filter errors by source type."""
    review_cases = []

    for error in errors:
        source = error.get("source", "")

        # Apply source filter if specified
        if source_filter and source != source_filter:
            continue

        # Skip if it was an exception, not a prediction error
        if "error" in error and "gold" not in error:
            continue

        review_cases.append(ReviewCase(
            idx=error.get("idx", -1),
            dataset=error.get("dataset", "unknown"),
            note_preview=error.get("note_preview", ""),
            gold_codes=error.get("gold", []),
            predicted_codes=error.get("predicted", []),
            ml_only_codes=error.get("ml_only", []),
            source=source,
            difficulty=error.get("difficulty", "unknown"),
            false_positives=error.get("false_positives", []),
            false_negatives=error.get("false_negatives", []),
            fallback_reason=error.get("reason_for_fallback", ""),
            rules_error=error.get("rules_error", ""),
        ))

    return review_cases


def analyze_error_patterns(cases: List[ReviewCase]) -> Dict[str, Any]:
    """Analyze patterns in error cases."""
    analysis = {
        "total_llm_fallback_errors": len(cases),
        "by_difficulty": defaultdict(int),
        "by_fallback_reason": defaultdict(int),
        "common_false_positives": defaultdict(int),
        "common_false_negatives": defaultdict(int),
        "ml_would_have_been_correct": 0,
        "ml_partial_overlap": 0,
    }

    for case in cases:
        analysis["by_difficulty"][case.difficulty] += 1

        # Parse fallback reason
        if "gray_zone" in case.fallback_reason:
            analysis["by_fallback_reason"]["gray_zone"] += 1
        elif "low_confidence" in case.fallback_reason:
            analysis["by_fallback_reason"]["low_confidence"] += 1
        elif "rule_conflict" in case.fallback_reason:
            analysis["by_fallback_reason"]["rule_conflict"] += 1
        else:
            analysis["by_fallback_reason"]["other"] += 1

        # Track common error codes
        for code in case.false_positives:
            analysis["common_false_positives"][code] += 1
        for code in case.false_negatives:
            analysis["common_false_negatives"][code] += 1

        # Check if ML alone would have been correct
        gold_set = set(case.gold_codes)
        ml_set = set(case.ml_only_codes)
        if ml_set == gold_set:
            analysis["ml_would_have_been_correct"] += 1
        elif ml_set & gold_set:
            analysis["ml_partial_overlap"] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    analysis["by_difficulty"] = dict(analysis["by_difficulty"])
    analysis["by_fallback_reason"] = dict(analysis["by_fallback_reason"])
    analysis["common_false_positives"] = dict(
        sorted(analysis["common_false_positives"].items(), key=lambda x: -x[1])[:10]
    )
    analysis["common_false_negatives"] = dict(
        sorted(analysis["common_false_negatives"].items(), key=lambda x: -x[1])[:10]
    )

    return analysis


def generate_review_report(
    cases: List[ReviewCase],
    analysis: Dict[str, Any],
    output_dir: Path,
    report_prefix: str = "llm_fallback",
) -> Path:
    """Generate a human-readable review report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"{report_prefix}_review_{timestamp}.md"

    with open(report_path, "w") as f:
        title = report_prefix.replace("_", " ").title()
        f.write(f"# {title} Error Review Report\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- Total errors reviewed: **{analysis['total_llm_fallback_errors']}**\n")
        f.write(f"- Cases where ML alone was correct: {analysis['ml_would_have_been_correct']}\n")
        f.write(f"- Cases where ML had partial overlap: {analysis['ml_partial_overlap']}\n\n")

        f.write("### Errors by Difficulty\n\n")
        for diff, count in sorted(analysis["by_difficulty"].items()):
            f.write(f"- {diff}: {count}\n")

        f.write("\n### Errors by Fallback Reason\n\n")
        for reason, count in sorted(analysis["by_fallback_reason"].items()):
            f.write(f"- {reason}: {count}\n")

        f.write("\n### Common False Positives (LLM suggested but shouldn't have)\n\n")
        for code, count in analysis["common_false_positives"].items():
            f.write(f"- {code}: {count} occurrences\n")

        f.write("\n### Common False Negatives (LLM missed)\n\n")
        for code, count in analysis["common_false_negatives"].items():
            f.write(f"- {code}: {count} occurrences\n")

        f.write("\n---\n\n")
        f.write("## Cases for Review\n\n")

        for i, case in enumerate(cases, 1):
            f.write(f"### Case {i} (idx={case.idx}, {case.dataset})\n\n")
            f.write(f"**Difficulty:** {case.difficulty}\n\n")
            f.write(f"**Fallback Reason:** {case.fallback_reason or 'N/A'}\n\n")

            if case.rules_error:
                f.write(f"**Rules Error:** {case.rules_error}\n\n")

            f.write("**Codes:**\n")
            f.write(f"- Gold: `{', '.join(case.gold_codes)}`\n")
            f.write(f"- Predicted: `{', '.join(case.predicted_codes)}`\n")
            f.write(f"- ML-only: `{', '.join(case.ml_only_codes)}`\n\n")

            if case.false_positives:
                f.write(f"- ❌ False Positives: `{', '.join(case.false_positives)}`\n")
            if case.false_negatives:
                f.write(f"- ⚠️ False Negatives: `{', '.join(case.false_negatives)}`\n")

            f.write("\n**Note Preview:**\n")
            f.write("```\n")
            f.write(case.note_preview[:500])
            if len(case.note_preview) > 500:
                f.write("...[truncated]")
            f.write("\n```\n\n")

            # Actionable recommendation
            f.write("**Recommendation:** ")
            if set(case.ml_only_codes) == set(case.gold_codes):
                f.write("ML was correct but LLM overrode it. Review LLM prompt constraints.\n")
            elif case.false_negatives and not case.false_positives:
                f.write("LLM missed codes. Consider adding to training data or improving prompt.\n")
            elif case.false_positives and not case.false_negatives:
                f.write("LLM hallucinated codes. Review prompt constraints for these codes.\n")
            else:
                f.write("Mixed errors. Manual review needed.\n")

            f.write("\n---\n\n")

    return report_path


def run_fresh_evaluation() -> Path:
    """Run the evaluation script and return the errors file path."""
    import subprocess

    print("Running fresh evaluation...")
    result = subprocess.run(
        ["python3", "scripts/eval_hybrid_pipeline.py"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Evaluation failed: {result.stderr}")
        raise RuntimeError("Evaluation failed")

    # Find the most recent errors file
    errors_dir = Path("data/eval_results")
    errors_files = sorted(errors_dir.glob("eval_errors_*.jsonl"), reverse=True)
    if not errors_files:
        raise FileNotFoundError("No errors file found after evaluation")

    return errors_files[0]


def main():
    parser = argparse.ArgumentParser(description="Review pipeline prediction errors")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to errors JSONL file (default: most recent in data/eval_results/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/eval_results"),
        help="Output directory for review report",
    )
    parser.add_argument(
        "--run-fresh",
        action="store_true",
        help="Run fresh evaluation before analyzing errors",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also output cases as JSON for programmatic use",
    )
    parser.add_argument(
        "--mode",
        choices=["llm_fallback", "fastpath", "all"],
        default="all",
        help="Which errors to review: llm_fallback, fastpath, or all (default: all)",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Find or generate errors file
    if args.run_fresh:
        errors_path = run_fresh_evaluation()
    elif args.input:
        errors_path = args.input
    else:
        # Find most recent errors file
        errors_dir = Path("data/eval_results")
        errors_files = sorted(errors_dir.glob("eval_errors_*.jsonl"), reverse=True)
        if not errors_files:
            print("No errors file found. Run with --run-fresh to generate one.")
            return
        errors_path = errors_files[0]

    print(f"Loading errors from: {errors_path}")
    errors = load_errors_from_jsonl(errors_path)
    print(f"  Total error entries: {len(errors)}")

    # Filter errors based on mode
    if args.mode == "llm_fallback":
        review_cases = filter_llm_fallback_errors(errors)
        report_prefix = "llm_fallback"
        mode_desc = "LLM fallback"
    elif args.mode == "fastpath":
        review_cases = filter_fastpath_errors(errors)
        report_prefix = "fastpath"
        mode_desc = "fast path (ML+Rules)"
    else:
        review_cases = filter_errors_by_source(errors, source_filter=None)
        report_prefix = "all_errors"
        mode_desc = "all"

    print(f"  {mode_desc.capitalize()} errors: {len(review_cases)}")

    if not review_cases:
        print(f"No {mode_desc} errors found. The pipeline is performing well!")
        return

    # Analyze patterns
    analysis = analyze_error_patterns(review_cases)

    # Generate report
    report_path = generate_review_report(
        review_cases, analysis, args.output_dir, report_prefix=report_prefix
    )
    print(f"\nReview report saved to: {report_path}")

    # Optionally output JSON
    if args.json:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = args.output_dir / f"{report_prefix}_cases_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump({
                "analysis": analysis,
                "cases": [c.to_dict() for c in review_cases],
            }, f, indent=2)
        print(f"JSON output saved to: {json_path}")

    # Print summary
    print("\n" + "=" * 60)
    print(f"SUMMARY ({mode_desc.upper()} ERRORS)")
    print("=" * 60)
    print(f"Total errors: {len(review_cases)}")

    # Break down by source if showing all
    if args.mode == "all":
        by_source = defaultdict(int)
        for case in review_cases:
            by_source[case.source] += 1
        print("\nBy source:")
        for source, count in sorted(by_source.items(), key=lambda x: -x[1]):
            print(f"  {source}: {count}")

    print(f"\nCases where ML alone was correct: {analysis['ml_would_have_been_correct']}")
    print(f"\nBy difficulty:")
    for diff, count in sorted(analysis["by_difficulty"].items(), key=lambda x: -x[1]):
        print(f"  {diff}: {count}")

    if analysis["by_fallback_reason"]:
        print(f"\nBy fallback reason:")
        for reason, count in sorted(analysis["by_fallback_reason"].items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")

    print(f"\nTop false positive codes (predicted but shouldn't have):")
    for code, count in list(analysis["common_false_positives"].items())[:5]:
        print(f"  {code}: {count}")
    print(f"\nTop false negative codes (missed):")
    for code, count in list(analysis["common_false_negatives"].items())[:5]:
        print(f"  {code}: {count}")


if __name__ == "__main__":
    main()
