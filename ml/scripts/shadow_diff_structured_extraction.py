#!/usr/bin/env python3
"""Shadow-diff runner: compare deterministic extraction vs StructurerAgent extraction.

Primary use-case (Phase 9):
- Run the same note through two extraction engines:
  - `REGISTRY_EXTRACTION_ENGINE=engine`
  - `REGISTRY_EXTRACTION_ENGINE=agents_structurer`
- Compare only PHI-safe signals:
  - Derived CPT code sets (deterministic Registry→CPT rules)
  - Performed-flag sets (procedures/pleural + a small granular fiducial flag)

Safety:
- Never prints or writes raw note text.
- The JSON report intentionally omits `note_text`, masked text, and evidence quotes/spans.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _normalize_code(code: str) -> str:
    raw = (code or "").strip()
    if not raw:
        return ""
    return raw.lstrip("+").strip()


def _iter_fixture_files(input_path: Path, pattern: str) -> Iterable[Path]:
    if input_path.is_file():
        yield input_path
        return
    if not input_path.exists() or not input_path.is_dir():
        return
    yield from sorted(input_path.glob(pattern))


def _as_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _extract_note_text(obj: dict[str, Any]) -> str:
    for key in ("note_text", "note", "text", "raw_text"):
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _extract_case_id(obj: dict[str, Any], *, fallback: str) -> str:
    case_id = _as_str(obj.get("case_id")).strip()
    if case_id:
        return case_id
    return fallback


def _extract_expected_codes(obj: dict[str, Any]) -> list[str]:
    for key in ("expected_cpt_codes", "cpt_codes", "codes", "expected_codes"):
        value = obj.get(key)
        if isinstance(value, list):
            out: set[str] = set()
            for item in value:
                if isinstance(item, str):
                    norm = _normalize_code(item)
                    if norm:
                        out.add(norm)
            return sorted(out)
    return []


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _collect_performed_flags(record_data: dict[str, Any]) -> set[str]:
    flags: set[str] = set()
    procs = record_data.get("procedures_performed")
    if isinstance(procs, dict):
        for name, payload in procs.items():
            if isinstance(payload, dict) and payload.get("performed") is True:
                flags.add(f"procedures_performed.{name}.performed")

    pleural = record_data.get("pleural_procedures")
    if isinstance(pleural, dict):
        for name, payload in pleural.items():
            if isinstance(payload, dict) and payload.get("performed") is True:
                flags.add(f"pleural_procedures.{name}.performed")

    if record_data.get("established_tracheostomy_route") is True:
        flags.add("established_tracheostomy_route")

    granular = record_data.get("granular_data")
    if isinstance(granular, dict):
        targets = granular.get("navigation_targets")
        if isinstance(targets, list):
            for target in targets:
                if isinstance(target, dict) and target.get("fiducial_marker_placed") is True:
                    flags.add("granular_data.navigation_targets[*].fiducial_marker_placed")
                    break

    return flags


@contextmanager
def _temp_environ(overrides: dict[str, str | None]) -> Iterable[None]:
    prev: dict[str, str | None] = {}
    for key, value in overrides.items():
        prev[key] = os.environ.get(key)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        for key, value in prev.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@dataclass(frozen=True)
class EngineRun:
    status: str
    elapsed_ms: float
    codes: list[str] | None = None
    performed_flags: list[str] | None = None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Shadow-diff registry extraction engines (PHI-safe summary signals)."
    )
    p.add_argument(
        "--input",
        type=Path,
        default=Path("data/knowledge/golden_extractions_vNext/approved"),
        help="Directory containing vNext fixtures (JSON) or a single fixture file.",
    )
    p.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="Glob pattern for fixture files when --input is a directory.",
    )
    p.add_argument("--limit", type=int, default=0, help="Max fixtures to run (0 = no limit).")
    p.add_argument(
        "--engine-a",
        type=str,
        default="engine",
        help="Baseline engine name for REGISTRY_EXTRACTION_ENGINE.",
    )
    p.add_argument(
        "--engine-b",
        type=str,
        default="agents_structurer",
        help="Comparison engine name for REGISTRY_EXTRACTION_ENGINE.",
    )
    p.add_argument(
        "--schema-version",
        type=str,
        default="",
        help="Optional REGISTRY_SCHEMA_VERSION override for both runs (e.g., v3).",
    )
    p.add_argument(
        "--output-json",
        type=Path,
        default=Path("output/shadow_diff_structured_extraction_report.json"),
        help="Path to write JSON report.",
    )
    return p.parse_args(argv)


def _run_once(
    *,
    service: Any,
    note_text: str,
    engine: str,
    schema_version: str | None,
) -> tuple[Any | None, dict[str, Any] | None, float, str | None]:
    overrides: dict[str, str | None] = {"REGISTRY_EXTRACTION_ENGINE": engine}
    if schema_version:
        overrides["REGISTRY_SCHEMA_VERSION"] = schema_version

    started = time.perf_counter()
    try:
        with _temp_environ(overrides):
            record, _warnings, meta = service.extract_record(note_text, note_id=None)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return record, meta, elapsed_ms, None
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return None, None, elapsed_ms, type(exc).__name__


def _derive_codes(*, record: Any) -> list[str]:
    from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    out = {_normalize_code(str(c)) for c in (codes or []) if _normalize_code(str(c))}
    return sorted(out)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    files = list(_iter_fixture_files(args.input, args.pattern))
    if not files:
        print(f"shadow_diff_structured_extraction: no fixtures found under {args.input}; skipping.")
        report = {
            "schema_version": "shadow_diff_structured_extraction_v1",
            "generated_at": datetime.now(tz=UTC).isoformat(),
            "input": {"path": str(args.input), "pattern": args.pattern, "limit": args.limit or 0},
            "engines": {"engine_a": args.engine_a, "engine_b": args.engine_b},
            "summary": {
                "fixtures": 0,
                "cases_total": 0,
                "cases_skipped_structurer_unavailable": 0,
                "cases_with_code_diffs": 0,
                "cases_with_performed_diffs": 0,
            },
            "cases": [],
        }
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return 0

    from app.registry.application.registry_service import RegistryService

    service = RegistryService()

    cases: list[dict[str, Any]] = []
    code_only_a: Counter[str] = Counter()
    code_only_b: Counter[str] = Counter()
    performed_only_a: Counter[str] = Counter()
    performed_only_b: Counter[str] = Counter()

    cases_total = 0
    cases_skipped_structurer_unavailable = 0
    cases_with_code_diffs = 0
    cases_with_performed_diffs = 0

    expected_cases = 0
    expected_exact_a = 0
    expected_exact_b = 0

    schema_version = (args.schema_version or "").strip().lower() or None

    for path in files:
        if args.limit and cases_total >= int(args.limit):
            break
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue

        note_text = _extract_note_text(obj)
        if not note_text.strip():
            continue

        cases_total += 1
        case_id = _extract_case_id(obj, fallback=path.stem)
        expected_codes = _extract_expected_codes(obj)

        note_hash = _sha256(note_text)
        note_length = len(note_text)

        record_a, _meta_a, elapsed_a, err_a = _run_once(
            service=service,
            note_text=note_text,
            engine=args.engine_a,
            schema_version=schema_version,
        )
        run_a: EngineRun
        if record_a is None:
            run_a = EngineRun(
                status="error",
                elapsed_ms=elapsed_a,
                codes=None,
                performed_flags=None,
            )
        else:
            try:
                codes_a = _derive_codes(record=record_a)
            except Exception as exc:
                codes_a = []
                err_a = err_a or type(exc).__name__
            flags_a = sorted(_collect_performed_flags(record_a.model_dump()))
            run_a = EngineRun(
                status="ok",
                elapsed_ms=elapsed_a,
                codes=codes_a,
                performed_flags=flags_a,
            )

        record_b, meta_b, elapsed_b, err_b = _run_once(
            service=service,
            note_text=note_text,
            engine=args.engine_b,
            schema_version=schema_version,
        )

        structurer_status: str | None = None
        structurer_available = True
        if args.engine_b.strip().lower() == "agents_structurer":
            structurer_meta = meta_b.get("structurer_meta") if isinstance(meta_b, dict) else None
            structurer_status = (
                structurer_meta.get("status") if isinstance(structurer_meta, dict) else None
            ) or "unknown"
            structurer_available = structurer_status == "ok"

        run_b: EngineRun
        if record_b is None:
            run_b = EngineRun(
                status="error",
                elapsed_ms=elapsed_b,
                codes=None,
                performed_flags=None,
            )
            structurer_available = False
        elif not structurer_available:
            cases_skipped_structurer_unavailable += 1
            run_b = EngineRun(status=structurer_status or "unavailable", elapsed_ms=elapsed_b)
        else:
            try:
                codes_b = _derive_codes(record=record_b)
            except Exception as exc:
                codes_b = []
                err_b = err_b or type(exc).__name__
            flags_b = sorted(_collect_performed_flags(record_b.model_dump()))
            run_b = EngineRun(
                status="ok",
                elapsed_ms=elapsed_b,
                codes=codes_b,
                performed_flags=flags_b,
            )

        case_obj: dict[str, Any] = {
            "fixture_file": path.name,
            "case_id": case_id,
            "note_sha256": note_hash,
            "note_length": note_length,
            "expected_cpt_codes": expected_codes,
            "engine_a": {
                "name": args.engine_a,
                "status": run_a.status,
                "elapsed_ms": round(run_a.elapsed_ms, 2),
                "codes": run_a.codes,
                "performed_flags": run_a.performed_flags,
                "error_type": err_a,
            },
            "engine_b": {
                "name": args.engine_b,
                "status": run_b.status,
                "elapsed_ms": round(run_b.elapsed_ms, 2),
                "codes": run_b.codes,
                "performed_flags": run_b.performed_flags,
                "error_type": err_b,
                "structurer_status": structurer_status,
            },
        }

        if expected_codes:
            expected_cases += 1
            expected_set = set(expected_codes)
            predicted_a = set(run_a.codes or [])
            if predicted_a == expected_set:
                expected_exact_a += 1
            if run_b.codes is not None:
                predicted_b = set(run_b.codes or [])
                if predicted_b == expected_set:
                    expected_exact_b += 1

        # Only compute diffs when both runs produced comparable signals.
        if run_a.codes is not None and run_b.codes is not None:
            a_codes = set(run_a.codes)
            b_codes = set(run_b.codes)
            only_a = sorted(a_codes - b_codes)
            only_b = sorted(b_codes - a_codes)
            if only_a or only_b:
                cases_with_code_diffs += 1
                code_only_a.update(only_a)
                code_only_b.update(only_b)

            a_flags = set(run_a.performed_flags or [])
            b_flags = set(run_b.performed_flags or [])
            only_a_flags = sorted(a_flags - b_flags)
            only_b_flags = sorted(b_flags - a_flags)
            if only_a_flags or only_b_flags:
                cases_with_performed_diffs += 1
                performed_only_a.update(only_a_flags)
                performed_only_b.update(only_b_flags)

            case_obj["diff"] = {
                "codes_only_engine_a": only_a,
                "codes_only_engine_b": only_b,
                "performed_only_engine_a": only_a_flags,
                "performed_only_engine_b": only_b_flags,
            }

        cases.append(case_obj)

    def _top(counter: Counter[str], n: int = 15) -> list[dict[str, Any]]:
        return [{"code": code, "count": count} for code, count in counter.most_common(n)]

    report = {
        "schema_version": "shadow_diff_structured_extraction_v1",
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "input": {"path": str(args.input), "pattern": args.pattern, "limit": args.limit or 0},
        "engines": {"engine_a": args.engine_a, "engine_b": args.engine_b},
        "summary": {
            "fixtures": len(files),
            "cases_total": cases_total,
            "cases_skipped_structurer_unavailable": cases_skipped_structurer_unavailable,
            "cases_with_code_diffs": cases_with_code_diffs,
            "cases_with_performed_diffs": cases_with_performed_diffs,
            "expected_cases": expected_cases,
            "expected_exact_match_engine_a": expected_exact_a,
            "expected_exact_match_engine_b": expected_exact_b,
            "top_codes_only_engine_a": _top(code_only_a),
            "top_codes_only_engine_b": _top(code_only_b),
            "top_performed_only_engine_a": _top(performed_only_a),
            "top_performed_only_engine_b": _top(performed_only_b),
        },
        "cases": cases,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        "shadow_diff_structured_extraction: "
        f"cases={cases_total} "
        f"skipped_structurer_unavailable={cases_skipped_structurer_unavailable} "
        f"code_diffs={cases_with_code_diffs} "
        f"performed_diffs={cases_with_performed_diffs} "
        f"report={args.output_json}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
