#!/usr/bin/env python3
"""Canonical extraction evaluation harness."""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.common.quality_eval import (  # noqa: E402
    build_standard_report,
    detect_input_format,
    evaluate_extraction_expectations,
    iter_legacy_golden_entries,
    load_unified_quality_corpus,
    maybe_write_report,
    normalize_code,
)


def _quality_signal_codes(result: Any) -> list[str]:
    codes: list[str] = []
    for signal in list(getattr(result, "quality_signals", []) or []):
        code = getattr(signal, "code", None)
        if code:
            codes.append(str(code))
    return sorted(set(codes))


def _extract_runtime_result(service: Any, note_text: str) -> Any:
    return service.extract_fields_extraction_first(note_text)


def _result_actual_payload(
    *,
    result: Any,
    expected_codes: list[str] | None = None,
    source_file: str | None = None,
) -> dict[str, Any]:
    actual = {
        "predicted_codes": sorted({code for code in (normalize_code(item) for item in (result.cpt_codes or [])) if code}),
        "warnings": [str(item) for item in list(getattr(result, "warnings", []) or []) if str(item)],
        "needs_manual_review": bool(getattr(result, "needs_manual_review", False)),
        "coder_difficulty": str(getattr(result, "coder_difficulty", "unknown") or "unknown"),
        "quality_signal_codes": _quality_signal_codes(result),
        "validation_errors": [str(item) for item in list(getattr(result, "validation_errors", []) or []) if str(item)],
        "audit_warnings": [str(item) for item in list(getattr(result, "audit_warnings", []) or []) if str(item)],
        "record": result.record.model_dump(exclude_none=False),
    }
    if expected_codes is not None:
        actual["expected_codes"] = expected_codes
    if source_file is not None:
        actual["source_file"] = source_file
    return actual


def _result_metrics_payload(result: Any) -> dict[str, Any]:
    warning_count = len(list(getattr(result, "warnings", []) or []))
    quality_signal_count = len(list(getattr(result, "quality_signals", []) or []))
    return {
        "warning_count": warning_count,
        "quality_signal_count": quality_signal_count,
        "needs_manual_review": bool(getattr(result, "needs_manual_review", False)),
    }


def _extract_note_text(entry: dict[str, Any]) -> str:
    for key in ("note_text", "note", "text", "raw_text"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _extract_expected_codes(entry: dict[str, Any]) -> list[str]:
    for key in ("cpt_codes", "codes", "expected_codes"):
        value = entry.get(key)
        if isinstance(value, list):
            output: list[str] = []
            for item in value:
                if isinstance(item, str):
                    normalized = normalize_code(item)
                    if normalized:
                        output.append(normalized)
            return output
    return []


def _extract_note_id(entry: dict[str, Any]) -> str | None:
    registry = entry.get("registry_entry")
    if isinstance(registry, dict):
        for key in ("patient_mrn", "note_id", "patient_id"):
            value = registry.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    for key in ("note_id", "noteId", "id"):
        value = entry.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate extraction against golden fixtures.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help=(
            "Directory containing legacy golden_*.json fixtures, a single legacy golden JSON file, "
            "or the unified quality corpus JSON."
        ),
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="golden_*.json",
        help="Glob pattern for fixture files when --input is a legacy golden directory.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Max cases to evaluate (0 = no limit).")
    parser.add_argument(
        "--input-format",
        type=str,
        default="auto",
        choices=["auto", "legacy_golden", "unified_quality_corpus"],
        help="Force the input fixture format instead of auto-detecting it.",
    )
    parser.add_argument(
        "--extraction-engine",
        type=str,
        default="",
        help="Override REGISTRY_EXTRACTION_ENGINE for evaluation (for example: engine, parallel_ner).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the machine-readable JSON report.",
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="Exit non-zero if the pass rate is below this percent (0-100).",
    )
    return parser.parse_args(argv)


def _resolve_format(input_path: Path, requested_format: str) -> str:
    if requested_format == "legacy_golden":
        return "legacy_golden"
    if requested_format == "unified_quality_corpus":
        return "unified_quality_corpus"
    detected = detect_input_format(input_path)
    if detected.startswith("legacy_golden"):
        return "legacy_golden"
    return detected


def _evaluate_legacy_goldens(
    *,
    input_path: Path,
    pattern: str,
    limit: int,
) -> dict[str, Any]:
    try:
        from app.registry.application.registry_service import RegistryService
    except Exception as exc:  # pragma: no cover - import surface exercised in runtime
        print(f"eval_golden: import error: {exc}", file=sys.stderr)
        return {"exit_code": 2}

    entries = iter_legacy_golden_entries(input_path, pattern)
    if not entries:
        print(f"eval_golden: no fixture files found under {input_path}; skipping.")
        return {"exit_code": 0}

    service = RegistryService()
    per_case: list[dict[str, Any]] = []
    missing_counter: Counter[str] = Counter()
    extra_counter: Counter[str] = Counter()
    coder_difficulty_counter: Counter[str] = Counter()
    manual_review_count = 0

    for source_file, entry in entries:
        note_text = _extract_note_text(entry)
        if not note_text.strip():
            continue

        expected_codes = sorted({code for code in (_extract_expected_codes(entry) or []) if code})
        note_id = _extract_note_id(entry) or f"legacy_case_{len(per_case) + 1}"
        result = _extract_runtime_result(service, note_text)
        predicted = sorted({code for code in (normalize_code(item) for item in (result.cpt_codes or [])) if code})
        exact_match = expected_codes == predicted
        coder_difficulty = str(getattr(result, "coder_difficulty", "unknown") or "unknown")
        coder_difficulty_counter.update([coder_difficulty])
        if bool(getattr(result, "needs_manual_review", False)):
            manual_review_count += 1

        failures: list[dict[str, Any]] = []
        missing = sorted(set(expected_codes) - set(predicted))
        extra = sorted(set(predicted) - set(expected_codes))
        if missing:
            missing_counter.update(missing)
            failures.append(
                {
                    "type": "missing_codes",
                    "message": f"missing expected codes {missing}",
                    "expected": expected_codes,
                    "actual": predicted,
                }
            )
        if extra:
            extra_counter.update(extra)
            failures.append(
                {
                    "type": "unexpected_codes",
                    "message": f"found extra codes {extra}",
                    "expected": expected_codes,
                    "actual": predicted,
                }
            )

        per_case.append(
            {
                "id": note_id,
                "tags": [],
                "status": "passed" if exact_match else "failed",
                "metrics": {"exact_match": exact_match, **_result_metrics_payload(result)},
                "actual": _result_actual_payload(
                    result=result,
                    expected_codes=expected_codes,
                    source_file=source_file,
                ),
                "failures": failures,
            }
        )

        if limit and len(per_case) >= limit:
            break

    if not per_case:
        print("eval_golden: no runnable cases found; skipping.")
        return {"exit_code": 0}

    exact_matches = sum(1 for case in per_case if case["status"] == "passed")
    rate = round(exact_matches / len(per_case), 4)
    report = build_standard_report(
        kind="extraction",
        input_path=str(input_path),
        output_path=None,
        source_format="legacy_golden",
        corpus_name="legacy_golden",
        per_case=per_case,
        summary_metrics={
            "exact_code_match_cases": exact_matches,
            "exact_code_match_rate": rate,
            "top_missing_codes": missing_counter.most_common(10),
            "top_extra_codes": extra_counter.most_common(10),
            "needs_manual_review_cases": manual_review_count,
            "coder_difficulty_counts": dict(coder_difficulty_counter),
        },
        runtime={"extraction_engine": os.getenv("REGISTRY_EXTRACTION_ENGINE", "")},
    )
    return {"exit_code": 0, "report": report}


def _evaluate_unified_quality_corpus(
    *,
    input_path: Path,
    limit: int,
) -> dict[str, Any]:
    try:
        from app.registry.application.registry_service import RegistryService
    except Exception as exc:  # pragma: no cover - import surface exercised in runtime
        print(f"eval_golden: import error: {exc}", file=sys.stderr)
        return {"exit_code": 2}

    payload = load_unified_quality_corpus(input_path)
    cases = list(payload.get("cases") or [])
    if limit:
        cases = cases[:limit]
    if not cases:
        print("eval_golden: no runnable cases found; skipping.")
        return {"exit_code": 0}

    service = RegistryService()
    per_case: list[dict[str, Any]] = []
    coder_difficulty_counter: Counter[str] = Counter()
    manual_review_count = 0
    for case in cases:
        note_text = str(case.get("note_text") or "")
        if not note_text.strip():
            continue
        case_id = str(case.get("id") or f"case_{len(per_case) + 1}")
        result = _extract_runtime_result(service, note_text)
        coder_difficulty_counter.update([str(getattr(result, "coder_difficulty", "unknown") or "unknown")])
        if bool(getattr(result, "needs_manual_review", False)):
            manual_review_count += 1
        case_report = evaluate_extraction_expectations(
            case=case,
            record_dict=result.record.model_dump(exclude_none=False),
            predicted_codes=list(result.cpt_codes or []),
            warnings=list(getattr(result, "warnings", []) or []),
        )
        case_report["metrics"].update(_result_metrics_payload(result))
        case_report["actual"].update(_result_actual_payload(result=result))
        per_case.append(case_report)

    report = build_standard_report(
        kind="extraction",
        input_path=str(input_path),
        output_path=None,
        source_format="unified_quality_corpus",
        corpus_name=str(payload.get("fixture_name") or "unified_quality_corpus"),
        per_case=per_case,
        summary_metrics={
            "exact_code_match_cases": sum(1 for case in per_case if case["status"] == "passed"),
            "exact_code_match_rate": round(
                sum(1 for case in per_case if case["status"] == "passed") / len(per_case),
                4,
            )
            if per_case
            else 0.0,
            "needs_manual_review_cases": manual_review_count,
            "coder_difficulty_counts": dict(coder_difficulty_counter),
        },
        runtime={"extraction_engine": os.getenv("REGISTRY_EXTRACTION_ENGINE", "")},
    )
    return {"exit_code": 0, "report": report}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.extraction_engine:
        os.environ["REGISTRY_EXTRACTION_ENGINE"] = str(args.extraction_engine).strip()

    input_format = _resolve_format(args.input, args.input_format)
    if input_format == "legacy_golden":
        outcome = _evaluate_legacy_goldens(input_path=args.input, pattern=args.pattern, limit=int(args.limit))
    else:
        outcome = _evaluate_unified_quality_corpus(input_path=args.input, limit=int(args.limit))

    exit_code = int(outcome.get("exit_code", 0))
    report = outcome.get("report")
    if report is None:
        return exit_code

    report["output_path"] = str(args.output) if args.output else None
    maybe_write_report(args.output, report)

    summary = report["summary"]
    print(
        "eval_golden: "
        f"cases={summary['total_cases']} "
        f"passed={summary['passed_cases']} "
        f"failed={summary['failed_cases']} "
        f"pass_rate={summary['pass_rate']:.4f}"
    )
    if args.output:
        print(f"eval_golden: wrote report to {args.output}")

    if args.fail_under is not None:
        threshold = float(args.fail_under) / 100.0
        if float(summary["pass_rate"]) < threshold:
            print(
                f"eval_golden: FAIL (rate {summary['pass_rate'] * 100:.1f}% < {float(args.fail_under):.1f}%)",
                file=sys.stderr,
            )
            return 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
