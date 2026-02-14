#!/usr/bin/env python3
"""Legacy golden evaluator (read-only).

This script runs the extraction-first pipeline against golden fixtures and
computes a simple baseline pass rate (primarily CPT code set equality).

It is intentionally conservative:
- it does not modify fixtures
- it can be safely skipped when fixture data is not present in the repo/CI
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _normalize_code(code: str) -> str:
    raw = (code or "").strip()
    if not raw:
        return ""
    raw = raw.lstrip("+").strip()
    return raw


def _iter_fixture_files(input_path: Path, pattern: str) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    if not input_path.exists():
        return
    if not input_path.is_dir():
        return
    yield from sorted(input_path.glob(pattern))


def _load_entries(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    if isinstance(data, dict):
        for key in ("entries", "records", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return [d for d in value if isinstance(d, dict)]
    raise ValueError(f"Unrecognized fixture JSON shape in {path}")


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
            out: list[str] = []
            for item in value:
                if isinstance(item, str):
                    norm = _normalize_code(item)
                    if norm:
                        out.append(norm)
            return out
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


@dataclass(frozen=True)
class CaseResult:
    note_id: str | None
    expected_codes: list[str]
    predicted_codes: list[str]
    exact_match: bool


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate extraction against golden fixtures.")
    p.add_argument(
        "--input",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help="Directory containing golden_*.json (arrays) OR a single JSON file.",
    )
    p.add_argument(
        "--pattern",
        type=str,
        default="golden_*.json",
        help="Glob pattern for fixture files when --input is a directory.",
    )
    p.add_argument("--limit", type=int, default=0, help="Max cases to evaluate (0 = no limit).")
    p.add_argument(
        "--extraction-engine",
        type=str,
        default="",
        help="Override REGISTRY_EXTRACTION_ENGINE for evaluation (e.g., engine, parallel_ner).",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write a JSON report.",
    )
    p.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="Exit non-zero if exact-match rate is below this percent (0-100).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.extraction_engine:
        os.environ["REGISTRY_EXTRACTION_ENGINE"] = str(args.extraction_engine).strip()

    fixture_files = list(_iter_fixture_files(args.input, args.pattern))
    if not fixture_files:
        print(f"eval_golden: no fixture files found under {args.input}; skipping.")
        return 0

    try:
        from app.registry.application.registry_service import RegistryService
        from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
    except Exception as exc:
        print(f"eval_golden: import error: {exc}", file=sys.stderr)
        return 2

    service = RegistryService()

    results: list[CaseResult] = []
    evaluated = 0

    for path in fixture_files:
        try:
            entries = _load_entries(path)
        except Exception as exc:
            print(f"eval_golden: failed to load {path}: {exc}", file=sys.stderr)
            continue

        for entry in entries:
            note_text = _extract_note_text(entry)
            if not note_text.strip():
                continue

            expected_codes = _extract_expected_codes(entry)
            note_id = _extract_note_id(entry)

            record, _warnings, _meta = service.extract_record(note_text, note_id=note_id)
            predicted_codes, _rationales, _derive_warnings = derive_all_codes_with_meta(record)

            expected_set = {c for c in (_normalize_code(c) for c in expected_codes) if c}
            predicted_set = {c for c in (_normalize_code(c) for c in predicted_codes) if c}

            results.append(
                CaseResult(
                    note_id=note_id,
                    expected_codes=sorted(expected_set),
                    predicted_codes=sorted(predicted_set),
                    exact_match=expected_set == predicted_set,
                )
            )

            evaluated += 1
            if args.limit and evaluated >= int(args.limit):
                break
        if args.limit and evaluated >= int(args.limit):
            break

    if evaluated <= 0:
        print("eval_golden: no runnable cases found; skipping.")
        return 0

    exact_matches = sum(1 for r in results if r.exact_match)
    rate = (exact_matches / evaluated) * 100.0

    failures = [r for r in results if not r.exact_match]
    missing_counter: Counter[str] = Counter()
    extra_counter: Counter[str] = Counter()
    for r in failures:
        expected_set = set(r.expected_codes)
        predicted_set = set(r.predicted_codes)
        missing_counter.update(expected_set - predicted_set)
        extra_counter.update(predicted_set - expected_set)

    print(f"eval_golden: evaluated={evaluated} exact_code_match={exact_matches} ({rate:.1f}%)")

    if failures:
        top_missing = ", ".join([f"{c}({n})" for c, n in missing_counter.most_common(10)])
        top_extra = ", ".join([f"{c}({n})" for c, n in extra_counter.most_common(10)])
        if top_missing:
            print(f"  top_missing: {top_missing}")
        if top_extra:
            print(f"  top_extra: {top_extra}")

    if args.output:
        report = {
            "evaluated": evaluated,
            "exact_code_match": exact_matches,
            "exact_code_match_rate": rate,
            "extraction_engine": os.getenv("REGISTRY_EXTRACTION_ENGINE", ""),
            "results": [
                {
                    "note_id": r.note_id,
                    "exact_match": r.exact_match,
                    "expected_codes": r.expected_codes,
                    "predicted_codes": r.predicted_codes,
                }
                for r in results
            ],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"eval_golden: wrote report to {args.output}")

    if args.fail_under is not None and rate < float(args.fail_under):
        print(f"eval_golden: FAIL (rate {rate:.1f}% < {float(args.fail_under):.1f}%)", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
