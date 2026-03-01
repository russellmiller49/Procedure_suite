#!/usr/bin/env python3
"""Evaluate GPT findings->registry->report pipeline on reporter_prompt split.

This is the Structured-First reporter POC (v2):
masked prompt text -> GPT findings (evidence-cited) -> synthetic NER -> registry flags
-> guardrails -> deterministic registry->CPT -> reporter templates.

Safety:
- This script is OFFLINE by default and uses a deterministic local findings stub.
- To allow real GPT calls for extraction, set:
  PROCSUITE_ALLOW_ONLINE=1
  LLM_PROVIDER=openai_compat
  OPENAI_API_KEY=...
  OPENAI_MODEL_STRUCTURER=gpt-5-mini
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def configure_eval_env() -> dict[str, str]:
    """Force deterministic settings and guard against unintended LLM calls.

    By default this script runs offline; set PROCSUITE_ALLOW_ONLINE=1 to enable
    real GPT calls for the findings extraction step.
    """
    allow_online = _truthy_env("PROCSUITE_ALLOW_ONLINE")

    forced = {
        # Avoid loading repo-local dotenv (which may contain API keys).
        "PROCSUITE_SKIP_DOTENV": "1",
        # Required runtime invariant (keep scripts aligned with service behavior).
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        # No LLM self-correct/fallback during eval scoring.
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        "REGISTRY_LLM_FALLBACK_ON_COVERAGE_FAIL": "0",
        # Disable RAW-ML auditing (may call LLM depending on config).
        "REGISTRY_AUDITOR_SOURCE": "disabled",
        # Force stub/offline LLMs in the registry service even if keys are present.
        "REGISTRY_USE_STUB_LLM": "1",
        "GEMINI_OFFLINE": "1",
        # Reporter-only fallback should not be used for this evaluation.
        "QA_REPORTER_ALLOW_SIMPLE_FALLBACK": "0",
        "PROCSUITE_FAST_MODE": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
    }

    if allow_online:
        forced.update(
            {
                "OPENAI_OFFLINE": "0",
                "REPORTER_DISABLE_LLM": "0",
            }
        )
    else:
        forced.update(
            {
                "OPENAI_OFFLINE": "1",
                "REPORTER_DISABLE_LLM": "1",
            }
        )

    applied: dict[str, str] = {}
    for key, value in forced.items():
        if os.environ.get(key) != value:
            os.environ[key] = value
            applied[key] = value
    return applied


_APPLIED_ENV_DEFAULTS = configure_eval_env()

from app.api.services.qa_pipeline import ReportingStrategy, SimpleReporterStrategy
from app.registry.application.registry_service import RegistryService
from app.reporting.engine import ReporterEngine, _load_procedure_order, default_schema_registry, default_template_registry
from app.reporting.inference import InferenceEngine
from app.reporting.validation import ValidationEngine
from app.reporting.llm_findings import build_record_payload_for_reporting, seed_registry_record_from_llm_findings
from ml.lib.reporter_prompt_masking import mask_prompt_cpt_noise
from ml.scripts.generate_reporter_gold_dataset import (
    CRITICAL_FLAG_EXACT,
    CRITICAL_FLAG_PREFIXES,
    collect_performed_flags,
)

DEFAULT_INPUT = Path("data/ml_training/reporter_prompt/v1/reporter_prompt_test.jsonl")
DEFAULT_OUTPUT = Path("data/ml_training/reporter_prompt/v1/reporter_prompt_llm_findings_eval_report.json")

PROMOTION_GATES = {
    "required_section_coverage": 0.99,
    "avg_cpt_jaccard": 0.30,
    "avg_performed_flag_f1": 0.40,
    "critical_extra_flag_rate": 0.03,
}

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


@dataclass(frozen=True)
class EvalRow:
    id: str
    prompt_text: str
    completion_canonical: str


class _OfflineFindingsLLM:
    """Deterministic local stub for offline evaluator sanity runs."""

    def generate(self, _prompt: str, **_kwargs: Any) -> str:
        return json.dumps(
            {
                "version": "reporter_findings_v1",
                "context": None,
                "findings": [],
                "notes": ["offline_stub"],
            }
        )


def warning_prefix(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "UNKNOWN"
    if ":" in raw:
        return raw.split(":", 1)[0].strip() or "UNKNOWN"
    if " " in raw:
        return raw.split(" ", 1)[0].strip() or "UNKNOWN"
    return raw


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--prompt-version",
        default=os.getenv("REPORTER_FINDINGS_PROMPT_VERSION", "v1"),
        help="Prompt version tag used by app/reporting/prompts/llm_findings_<version>.txt",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=2,
        help="Max parse/schema repair retries for llm_findings extraction.",
    )
    parser.add_argument(
        "--save-failures",
        type=Path,
        default=None,
        help="Optional JSONL output for PHI-safe failure artifacts.",
    )
    parser.add_argument(
        "--prompt-field",
        default="prompt_text",
        help="Which JSONL field to use as prompt text (default: prompt_text). "
        "Common options: prompt_text, prompt_text_masked.",
    )
    return parser.parse_args(argv)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def to_rows(raw: list[dict[str, Any]], *, prompt_field: str) -> list[EvalRow]:
    out: list[EvalRow] = []
    for idx, row in enumerate(raw, start=1):
        row_id = str(row.get("id") or f"row_{idx}")
        prompt = str(row.get(prompt_field) or "").strip()
        if not prompt and prompt_field == "prompt_text_masked":
            raw_prompt = str(row.get("prompt_text") or "").strip()
            if raw_prompt:
                prompt = mask_prompt_cpt_noise(raw_prompt)
        if not prompt:
            prompt = str(row.get("prompt_text") or "").strip()
        completion = str(row.get("completion_canonical") or "").strip()
        if not prompt or not completion:
            continue
        out.append(EvalRow(id=row_id, prompt_text=prompt, completion_canonical=completion))
    return out


def maybe_subsample(rows: list[EvalRow], max_cases: int, seed: int) -> list[EvalRow]:
    if max_cases <= 0 or len(rows) <= max_cases:
        return rows
    rng = random.Random(seed)
    picked = rng.sample(rows, max_cases)
    picked.sort(key=lambda item: item.id)
    return picked


def normalize_text(text: str) -> str:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return "\n".join(lines)


def similarity_ratio(reference: str, candidate: str) -> float:
    return SequenceMatcher(None, normalize_text(reference), normalize_text(candidate)).ratio()


def missing_sections(report_text: str) -> list[str]:
    upper = (report_text or "").upper()
    return [header for header in REQUIRED_SECTION_HEADERS if header.upper() not in upper]


def _is_critical_flag(path: str) -> bool:
    return path in CRITICAL_FLAG_EXACT or path.startswith(CRITICAL_FLAG_PREFIXES)


def extract_flags_and_cpt(note_text: str, registry_service: RegistryService) -> tuple[set[str], set[str]]:
    result = registry_service.extract_fields_extraction_first(note_text)
    record_data = result.record.model_dump(exclude_none=True)
    flags = collect_performed_flags(record_data)
    cpt = {str(code) for code in (result.cpt_codes or [])}
    return flags, cpt


def cpt_jaccard(gold: set[str], pred: set[str]) -> float:
    union = gold | pred
    if not union:
        return 1.0
    return float(len(gold & pred) / len(union))


def flag_f1(gold: set[str], pred: set[str]) -> tuple[float, int, int]:
    tp = len(gold & pred)
    fp = len(pred - gold)
    fn = len(gold - pred)
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    if prec + rec == 0:
        return 0.0, fp, fn
    return (2 * prec * rec / (prec + rec)), fp, fn


def _avg(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def evaluate_gates(summary: dict[str, Any]) -> dict[str, Any]:
    checks: dict[str, Any] = {}
    primary_pass = True

    for key, threshold in PROMOTION_GATES.items():
        observed = float(summary.get(key, 0.0))
        if key == "critical_extra_flag_rate":
            passed = observed <= threshold
        else:
            passed = observed >= threshold
        checks[key] = {
            "observed": round(observed, 4),
            "threshold": threshold,
            "passed": passed,
        }
        if not passed:
            primary_pass = False

    return {
        "primary_gates_passed": primary_pass,
        "all_checks": checks,
        "deployment_recommendation": "allow_optional_qa_integration" if primary_pass else "do_not_integrate",
    }


def build_structured_strategy() -> ReportingStrategy:
    templates = default_template_registry()
    schemas = default_schema_registry()
    reporter_engine = ReporterEngine(
        templates,
        schemas,
        procedure_order=_load_procedure_order(),
    )
    registry_engine = RegistryService()
    return ReportingStrategy(
        reporter_engine=reporter_engine,
        inference_engine=InferenceEngine(),
        validation_engine=ValidationEngine(templates, schemas),
        registry_engine=registry_engine,
        simple_strategy=SimpleReporterStrategy(),
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.exists():
        raise FileNotFoundError(f"Input dataset not found: {args.input}")

    os.environ["REPORTER_FINDINGS_PROMPT_VERSION"] = str(args.prompt_version).strip() or "v1"
    os.environ["REPORTER_LLM_FINDINGS_MAX_RETRIES"] = str(max(0, int(args.max_retries)))
    allow_online = _truthy_env("PROCSUITE_ALLOW_ONLINE")
    if allow_online and not os.getenv("OPENAI_API_KEY"):
        print("PROCSUITE_ALLOW_ONLINE=1 but OPENAI_API_KEY is not set.")
        return 2

    raw_rows = load_jsonl(args.input)
    prompt_field = str(getattr(args, "prompt_field", "prompt_text")).strip() or "prompt_text"
    rows = maybe_subsample(to_rows(raw_rows, prompt_field=prompt_field), int(args.max_cases), int(args.seed))

    reporter = build_structured_strategy()
    registry_service = RegistryService()
    offline_llm = None if allow_online else _OfflineFindingsLLM()
    if allow_online:
        print("Mode: online (real OpenAI calls allowed)")
    else:
        print("Mode: offline (deterministic local findings stub)")

    per_case: list[dict[str, Any]] = []
    failure_artifacts: list[dict[str, Any]] = []
    sim_scores: list[float] = []
    cpt_scores: list[float] = []
    f1_scores: list[float] = []
    accepted_counts: list[float] = []
    full_shell_count = 0
    failures = 0
    critical_extra_cases = 0
    parse_error_cases = 0
    validation_issue_cases = 0
    parse_validation_issue_cases = 0
    warning_prefix_counts: Counter[str] = Counter()

    for row in rows:
        try:
            seed = seed_registry_record_from_llm_findings(row.prompt_text, llm=offline_llm)
            record_payload = build_record_payload_for_reporting(seed)
            rendered = reporter.render(
                text=seed.masked_prompt_text,
                registry_data={"record": record_payload},
            )
            markdown = str(rendered.get("markdown") or "")
            if not markdown.strip():
                raise RuntimeError("Empty markdown output")

            sim = similarity_ratio(row.completion_canonical, markdown)
            sim_scores.append(sim)

            miss = missing_sections(markdown)
            if not miss:
                full_shell_count += 1

            gold_flags, gold_cpt = extract_flags_and_cpt(row.completion_canonical, registry_service)
            pred_flags, pred_cpt = extract_flags_and_cpt(markdown, registry_service)

            cpt_score = cpt_jaccard(gold_cpt, pred_cpt)
            f1, fp, fn = flag_f1(gold_flags, pred_flags)
            critical_extra = sorted([flag for flag in (pred_flags - gold_flags) if _is_critical_flag(flag)])
            if critical_extra:
                critical_extra_cases += 1

            cpt_scores.append(cpt_score)
            f1_scores.append(f1)
            accepted_counts.append(float(seed.accepted_findings))

            seed_warnings = list(seed.warnings or [])
            seed_warning_prefixes = sorted({warning_prefix(w) for w in seed_warnings if str(w).strip()})
            for prefix in seed_warning_prefixes:
                warning_prefix_counts[prefix] += 1
            has_parse_error = bool(seed.parse_error)
            has_validation_issue = any(
                str(w).startswith("LLM_FINDINGS_DROPPED:")
                or str(w).startswith("LLM_FINDINGS_REPAIR_FAILED:")
                for w in seed_warnings
            )
            if has_parse_error:
                parse_error_cases += 1
            if has_validation_issue:
                validation_issue_cases += 1
            if has_parse_error or has_validation_issue:
                parse_validation_issue_cases += 1
                failure_artifacts.append(
                    {
                        "id": row.id,
                        "error_type": None,
                        "warning_prefixes": seed_warning_prefixes,
                        "warning_count": int(len(seed_warnings)),
                        "accepted_findings": int(seed.accepted_findings),
                        "dropped_findings": int(seed.dropped_findings),
                        "parse_error": has_parse_error,
                        "used_retries": int(seed.used_retries),
                    }
                )

            per_case.append(
                {
                    "id": row.id,
                    "text_similarity": round(sim, 4),
                    "missing_sections": miss,
                    "cpt_jaccard": round(cpt_score, 4),
                    "performed_flag_f1": round(f1, 4),
                    "critical_extra_flags": critical_extra,
                    "flag_false_positive_count": fp,
                    "flag_false_negative_count": fn,
                    "accepted_findings": int(seed.accepted_findings),
                    "dropped_findings": int(seed.dropped_findings),
                    "parse_error": bool(seed.parse_error),
                    "used_retries": int(seed.used_retries),
                    "warning_prefixes": seed_warning_prefixes,
                    "seed_warnings_count": int(len(seed.warnings or [])),
                    "error": None,
                }
            )
        except Exception as exc:  # noqa: BLE001
            failures += 1
            parse_validation_issue_cases += 1
            err_prefix = warning_prefix(type(exc).__name__)
            warning_prefix_counts[err_prefix] += 1
            failure_artifacts.append(
                {
                    "id": row.id,
                    "error_type": type(exc).__name__,
                    "warning_prefixes": [err_prefix],
                    "warning_count": 0,
                    "accepted_findings": 0,
                    "dropped_findings": 0,
                    "parse_error": False,
                    "used_retries": 0,
                }
            )
            per_case.append(
                {
                    "id": row.id,
                    "text_similarity": 0.0,
                    "missing_sections": REQUIRED_SECTION_HEADERS,
                    "cpt_jaccard": 0.0,
                    "performed_flag_f1": 0.0,
                    "critical_extra_flags": [],
                    "flag_false_positive_count": 0,
                    "flag_false_negative_count": 0,
                    "accepted_findings": 0,
                    "dropped_findings": 0,
                    "parse_error": False,
                    "used_retries": 0,
                    "warning_prefixes": [err_prefix],
                    "seed_warnings_count": 0,
                    "error": f"{type(exc).__name__}",
                }
            )

    total = len(rows)
    successful = total - failures

    summary = {
        "total_cases": total,
        "successful_cases": successful,
        "failed_cases": failures,
        "avg_text_similarity": round(_avg(sim_scores), 4),
        "required_section_coverage": round((full_shell_count / successful) if successful else 0.0, 4),
        "avg_cpt_jaccard": round(_avg(cpt_scores), 4),
        "avg_performed_flag_f1": round(_avg(f1_scores), 4),
        "critical_extra_flag_rate": round((critical_extra_cases / successful) if successful else 0.0, 4),
        "avg_accepted_findings": round(_avg(accepted_counts), 4),
        "parse_error_rate": round((parse_error_cases / total) if total else 0.0, 4),
        "validation_issue_rate": round((validation_issue_cases / total) if total else 0.0, 4),
        "parse_validation_failure_rate": round((parse_validation_issue_cases / total) if total else 0.0, 4),
        "most_common_warning_prefixes": [
            {"prefix": prefix, "count": int(count)}
            for prefix, count in warning_prefix_counts.most_common(10)
        ],
    }

    payload = {
        "created_at": datetime_now_iso(),
        "input_path": str(args.input),
        "output_path": str(args.output),
        "prompt_field": prompt_field,
        "prompt_version": str(args.prompt_version),
        "max_retries": int(args.max_retries),
        "allow_online": bool(allow_online),
        "row_count": total,
        "environment_defaults_applied": _APPLIED_ENV_DEFAULTS,
        "summary": summary,
        "promotion_gate_report": evaluate_gates(summary),
        "per_case": per_case,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.save_failures is not None:
        write_jsonl(args.save_failures, failure_artifacts)
        print(f"Wrote PHI-safe failures: {args.save_failures}")

    print(f"Primary gates passed: {payload['promotion_gate_report']['primary_gates_passed']}")
    print(f"Wrote report: {args.output}")
    return 0


def datetime_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
