#!/usr/bin/env python3
"""Evaluate reporter quality against reporter gold data or the unified quality corpus."""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.common.quality_eval import (  # noqa: E402
    build_reporting_strategy,
    build_standard_report,
    detect_input_format,
    evaluate_reporter_expectations,
    load_jsonl_rows,
    load_unified_quality_corpus,
    maybe_write_report,
    missing_sections,
    normalize_text,
    render_report_markdown,
)
from app.registry.application.registry_service import RegistryService  # noqa: E402


REQUIRED_SECTION_HEADERS = [
    "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT",
    "INDICATION FOR OPERATION",
    "CONSENT",
    "PREOPERATIVE DIAGNOSIS",
    "POSTOPERATIVE DIAGNOSIS",
    "PROCEDURE",
    "ANESTHESIA",
    "MONITORING",
    "COMPLICATIONS",
    "PROCEDURE IN DETAIL",
    "IMPRESSION / PLAN",
]

DEFAULT_INPUT = Path("data/ml_training/reporter_golden/v1/reporter_gold_accepted.jsonl")
DEFAULT_OUTPUT = Path("data/ml_training/reporter_golden/v1/reporter_gold_eval_report.json")


@dataclass(frozen=True)
class EvaluationRow:
    id: str
    input_text: str
    ideal_output: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Reporter gold JSONL or unified corpus JSON.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Evaluation report JSON path.")
    parser.add_argument("--max-cases", type=int, default=0, help="Optional max case count (0 means all).")
    parser.add_argument("--seed", type=int, default=42, help="Seed for deterministic subsampling.")
    parser.add_argument(
        "--input-format",
        type=str,
        default="auto",
        choices=["auto", "reporter_gold_jsonl", "unified_quality_corpus"],
        help="Force the reporter eval input format instead of auto-detecting it.",
    )
    return parser.parse_args(argv)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return load_jsonl_rows(path)


def similarity_ratio(reference: str, candidate: str) -> float:
    return SequenceMatcher(None, normalize_text(reference), normalize_text(candidate)).ratio()


def to_eval_rows(rows: list[dict[str, Any]]) -> list[EvaluationRow]:
    output: list[EvaluationRow] = []
    for index, row in enumerate(rows, start=1):
        input_text = str(row.get("input_text") or "").strip()
        ideal_output = str(row.get("ideal_output") or row.get("ideal_output_candidate") or "").strip()
        row_id = str(row.get("id") or f"row_{index}")
        if not input_text or not ideal_output:
            continue
        output.append(EvaluationRow(id=row_id, input_text=input_text, ideal_output=ideal_output))
    return output


def maybe_subsample(rows: list[EvaluationRow], max_cases: int, seed: int) -> list[EvaluationRow]:
    if max_cases <= 0 or len(rows) <= max_cases:
        return rows
    rng = random.Random(seed)
    picked = rng.sample(rows, max_cases)
    picked.sort(key=lambda row: row.id)
    return picked


def evaluate_rows(
    rows: list[EvaluationRow],
    *,
    render_report: Callable[[str], str],
) -> dict[str, Any]:
    per_case: list[dict[str, Any]] = []
    similarities: list[float] = []
    generated_full_shell_count = 0
    failures = 0

    for row in rows:
        try:
            generated = render_report(row.input_text)
            missing = missing_sections(generated, REQUIRED_SECTION_HEADERS)
            score = similarity_ratio(row.ideal_output, generated)
            similarities.append(score)
            if not missing:
                generated_full_shell_count += 1

            per_case.append(
                {
                    "id": row.id,
                    "tags": [],
                    "status": "passed",
                    "metrics": {
                        "similarity": round(score, 4),
                        "generated_length": len(generated),
                        "ideal_length": len(row.ideal_output),
                    },
                    "actual": {
                        "missing_sections_generated": missing,
                        "missing_sections_ideal": missing_sections(row.ideal_output, REQUIRED_SECTION_HEADERS),
                        "markdown_preview": generated[:400],
                    },
                    "failures": [],
                    "similarity": round(score, 4),
                    "missing_sections_generated": missing,
                    "missing_sections_ideal": missing_sections(row.ideal_output, REQUIRED_SECTION_HEADERS),
                    "generated_length": len(generated),
                    "ideal_length": len(row.ideal_output),
                    "error": None,
                }
            )
        except Exception as exc:
            failures += 1
            per_case.append(
                {
                    "id": row.id,
                    "tags": [],
                    "status": "failed",
                    "metrics": {
                        "similarity": 0.0,
                        "generated_length": 0,
                        "ideal_length": len(row.ideal_output),
                    },
                    "actual": {
                        "missing_sections_generated": REQUIRED_SECTION_HEADERS,
                        "missing_sections_ideal": [],
                        "markdown_preview": "",
                    },
                    "failures": [
                        {
                            "type": "render_error",
                            "message": str(exc),
                            "expected": None,
                            "actual": None,
                        }
                    ],
                    "similarity": 0.0,
                    "missing_sections_generated": REQUIRED_SECTION_HEADERS,
                    "missing_sections_ideal": [],
                    "generated_length": 0,
                    "ideal_length": len(row.ideal_output),
                    "error": str(exc),
                }
            )

    avg_similarity = float(sum(similarities) / len(similarities)) if similarities else 0.0
    min_similarity = float(min(similarities)) if similarities else 0.0
    full_shell_rate = float(generated_full_shell_count / len(rows)) if rows else 0.0
    total_cases = len(rows)
    successful_cases = total_cases - failures

    summary = {
        "total_cases": total_cases,
        "passed_cases": successful_cases,
        "successful_cases": successful_cases,
        "failed_cases": failures,
        "pass_rate": round((successful_cases / total_cases), 4) if total_cases else 0.0,
        "avg_similarity": round(avg_similarity, 4),
        "min_similarity": round(min_similarity, 4),
        "generated_full_shell_rate": round(full_shell_rate, 4),
        "metrics": {
            "successful_cases": successful_cases,
            "avg_similarity": round(avg_similarity, 4),
            "min_similarity": round(min_similarity, 4),
            "generated_full_shell_rate": round(full_shell_rate, 4),
        },
    }
    failures_flat = []
    for case in per_case:
        for failure in case.get("failures") or []:
            item = {"id": case["id"], "tags": []}
            item.update(failure)
            failures_flat.append(item)
    return {
        "summary": summary,
        "per_case": per_case,
        "failures": failures_flat,
    }


def _build_renderer() -> Callable[[str], str]:
    strategy = build_reporting_strategy()
    registry_service = RegistryService()

    def _render(note_text: str) -> str:
        markdown, _payload = render_report_markdown(
            note_text=note_text,
            registry_service=registry_service,
            reporting_strategy=strategy,
        )
        return markdown

    return _render


def _resolve_input_format(input_path: Path, requested_format: str) -> str:
    if requested_format != "auto":
        return requested_format
    detected = detect_input_format(input_path)
    if detected == "reporter_gold_jsonl":
        return detected
    if detected == "unified_quality_corpus":
        return detected
    raise ValueError(f"Unsupported reporter evaluation input format for {input_path}: {detected}")


def _evaluate_unified_quality_corpus(
    *,
    input_path: Path,
    max_cases: int,
) -> dict[str, Any]:
    payload = load_unified_quality_corpus(input_path)
    cases = list(payload.get("cases") or [])
    if max_cases > 0:
        cases = cases[:max_cases]

    strategy = build_reporting_strategy()
    registry_service = RegistryService()
    per_case: list[dict[str, Any]] = []
    for case in cases:
        note_text = str(case.get("note_text") or "")
        try:
            markdown, report_payload = render_report_markdown(
                note_text=note_text,
                registry_service=registry_service,
                reporting_strategy=strategy,
            )
            per_case.append(
                evaluate_reporter_expectations(
                    case=case,
                    markdown=markdown,
                    report_payload=report_payload,
                )
            )
        except Exception as exc:
            per_case.append(
                evaluate_reporter_expectations(
                    case=case,
                    markdown="",
                    report_payload={},
                    error=exc,
                )
            )

    report = build_standard_report(
        kind="reporter",
        input_path=str(input_path),
        output_path=None,
        source_format="unified_quality_corpus",
        corpus_name=str(payload.get("fixture_name") or "unified_quality_corpus"),
        per_case=per_case,
        summary_metrics={
            "successful_cases": sum(1 for case in per_case if case["status"] == "passed"),
            "avg_similarity": 0.0,
            "min_similarity": 0.0,
            "generated_full_shell_rate": 0.0,
        },
    )
    return report


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.exists():
        raise FileNotFoundError(f"Input dataset not found: {args.input}")

    input_format = _resolve_input_format(args.input, args.input_format)
    if input_format == "reporter_gold_jsonl":
        raw_rows = load_jsonl(args.input)
        eval_rows = to_eval_rows(raw_rows)
        eval_rows = maybe_subsample(eval_rows, int(args.max_cases), int(args.seed))
        renderer = _build_renderer()
        result = evaluate_rows(eval_rows, render_report=renderer)
        report = build_standard_report(
            kind="reporter",
            input_path=str(args.input),
            output_path=str(args.output),
            source_format="reporter_gold_jsonl",
            corpus_name="reporter_gold",
            per_case=result["per_case"],
            summary_metrics=result["summary"]["metrics"],
        )
        report["summary"]["successful_cases"] = result["summary"]["successful_cases"]
        report["summary"]["avg_similarity"] = result["summary"]["avg_similarity"]
        report["summary"]["min_similarity"] = result["summary"]["min_similarity"]
        report["summary"]["generated_full_shell_rate"] = result["summary"]["generated_full_shell_rate"]
    else:
        report = _evaluate_unified_quality_corpus(input_path=args.input, max_cases=int(args.max_cases))
        report["output_path"] = str(args.output)

    maybe_write_report(args.output, report)

    summary = report["summary"]
    print(
        "Reporter gold eval: "
        f"cases={summary['total_cases']} "
        f"passed={summary['passed_cases']} "
        f"failed={summary['failed_cases']} "
        f"avg_similarity={summary.get('avg_similarity', 0.0)} "
        f"full_shell_rate={summary.get('generated_full_shell_rate', 0.0)}"
    )
    print(f"Wrote report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
