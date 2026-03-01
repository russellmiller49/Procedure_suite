#!/usr/bin/env python3
"""Iteratively optimize reporter findings prompt templates under a cost budget.

This script drives a prompt-only optimization loop:
1) Evaluate a base prompt version on reporter data
2) Summarize failures and sample PHI-safe masked snippets
3) Ask an optimizer model to propose a revised prompt template
4) Evaluate the candidate and keep the best one by gated metrics
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.common.llm import OpenAILLM
from app.common.structured_output import StructuredOutputSpec
from app.reporting.llm_findings import load_prompt_template
from ml.lib.reporter_prompt_masking import mask_prompt_cpt_noise

EVAL_SCRIPT = ROOT / "ops/tools/eval_reporter_prompt_llm_findings.py"
PROMPTS_DIR = ROOT / "app/reporting/prompts"
DEFAULT_INPUT = ROOT / "data/ml_training/reporter_prompt/v1/reporter_prompt_test.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "reports/reporter_prompt_optimization"

OPTIMIZER_OUTPUT_SCHEMA = StructuredOutputSpec(
    name="reporter_findings_prompt_optimizer_v1",
    strict=True,
    schema={
        "type": "object",
        "additionalProperties": False,
        "required": ["prompt_template", "rationale", "changelog", "requires_review"],
        "properties": {
            "prompt_template": {"type": "string"},
            "rationale": {"type": "string"},
            "changelog": {"type": "array", "items": {"type": "string"}},
            "requires_review": {"type": "boolean"},
        },
    },
)


@dataclass(frozen=True)
class Metrics:
    required_section_coverage: float
    critical_extra_flag_rate: float
    avg_text_similarity: float


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--base-version", default=os.getenv("REPORTER_FINDINGS_PROMPT_VERSION", "v1"))
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--max-iterations", type=int, default=5)
    parser.add_argument("--epsilon", type=float, default=0.002)
    parser.add_argument("--budget-usd", type=float, default=200.0)
    parser.add_argument("--optimizer-model", default="gpt-5.2")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--failure-examples", type=int, default=8)
    parser.add_argument("--input-cost-per-1k", type=float, default=float(os.getenv("OPENAI_COST_INPUT_PER_1K", "0.005")))
    parser.add_argument("--output-cost-per-1k", type=float, default=float(os.getenv("OPENAI_COST_OUTPUT_PER_1K", "0.015")))
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


def _extract_prompt_text(row: dict[str, Any]) -> str:
    raw = str(row.get("prompt_text_masked") or "").strip()
    if raw:
        return raw
    source = str(row.get("prompt_text") or "").strip()
    return mask_prompt_cpt_noise(source)


def _estimate_tokens(text: str) -> int:
    return max(1, int((len(text) + 3) / 4))


def _estimate_cost_usd(
    *,
    input_tokens: int,
    output_tokens: int,
    input_per_1k: float,
    output_per_1k: float,
) -> float:
    return (float(input_tokens) / 1000.0) * float(input_per_1k) + (float(output_tokens) / 1000.0) * float(output_per_1k)


def _run_eval(
    *,
    input_path: Path,
    output_path: Path,
    prompt_version: str,
    sample_size: int,
    seed: int,
    max_retries: int,
) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(EVAL_SCRIPT),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--max-cases",
        str(sample_size),
        "--seed",
        str(seed),
        "--prompt-version",
        str(prompt_version),
        "--max-retries",
        str(max_retries),
    ]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True, env=dict(os.environ))
    if completed.returncode != 0:
        raise RuntimeError(
            f"Eval script failed for {prompt_version} (exit={completed.returncode}): "
            f"{(completed.stderr or completed.stdout or '').strip()[:500]}"
        )
    with output_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _metrics_from_eval(payload: dict[str, Any]) -> Metrics:
    summary = payload.get("summary") or {}
    return Metrics(
        required_section_coverage=float(summary.get("required_section_coverage") or 0.0),
        critical_extra_flag_rate=float(summary.get("critical_extra_flag_rate") or 1.0),
        avg_text_similarity=float(summary.get("avg_text_similarity") or 0.0),
    )


def _is_better(candidate: Metrics, best: Metrics, *, epsilon: float) -> bool:
    if candidate.required_section_coverage > best.required_section_coverage + epsilon:
        return True
    if abs(candidate.required_section_coverage - best.required_section_coverage) <= epsilon:
        if candidate.critical_extra_flag_rate < best.critical_extra_flag_rate - epsilon:
            return True
        if abs(candidate.critical_extra_flag_rate - best.critical_extra_flag_rate) <= epsilon:
            if candidate.avg_text_similarity > best.avg_text_similarity + epsilon:
                return True
    return False


def _next_prompt_version() -> str:
    existing = list(PROMPTS_DIR.glob("llm_findings_v*.txt"))
    max_num = 0
    for path in existing:
        stem = path.stem
        if not stem.startswith("llm_findings_v"):
            continue
        suffix = stem[len("llm_findings_v") :]
        if suffix.isdigit():
            max_num = max(max_num, int(suffix))
    return f"v{max_num + 1}"


def _collect_failure_examples(
    *,
    eval_payload: dict[str, Any],
    input_rows: list[dict[str, Any]],
    max_examples: int,
) -> list[dict[str, Any]]:
    prompt_by_id: dict[str, str] = {}
    for idx, row in enumerate(input_rows, start=1):
        row_id = str(row.get("id") or f"row_{idx}")
        prompt_by_id[row_id] = _extract_prompt_text(row)

    out: list[dict[str, Any]] = []
    for case in list(eval_payload.get("per_case") or []):
        if len(out) >= max_examples:
            break
        row_id = str(case.get("id") or "")
        error = str(case.get("error") or "").strip()
        warning_prefixes = list(case.get("warning_prefixes") or [])
        parse_error = bool(case.get("parse_error"))
        has_problem = bool(error) or parse_error or any(
            str(prefix).startswith("LLM_FINDINGS_DROPPED") or str(prefix).startswith("LLM_FINDINGS_REPAIR_FAILED")
            for prefix in warning_prefixes
        )
        if not has_problem:
            continue
        prompt_masked = str(prompt_by_id.get(row_id) or "").strip()
        snippet = " ".join(prompt_masked.split())[:500]
        out.append(
            {
                "id": row_id,
                "error": error or None,
                "parse_error": parse_error,
                "warning_prefixes": warning_prefixes,
                "accepted_findings": int(case.get("accepted_findings") or 0),
                "dropped_findings": int(case.get("dropped_findings") or 0),
                "masked_prompt_snippet": snippet,
            }
        )
    return out


def _guardrails_softened(old_prompt: str, new_prompt: str) -> bool:
    old_lower = (old_prompt or "").lower()
    new_lower = (new_prompt or "").lower()
    required_fragments = [
        "tools do not equal intent",
        "action-on-tissue",
        "inspection",
        "omit",
    ]
    for fragment in required_fragments:
        if fragment in old_lower and fragment not in new_lower:
            return True
    return False


def _build_optimizer_prompt(
    *,
    current_prompt: str,
    eval_payload: dict[str, Any],
    examples: list[dict[str, Any]],
) -> str:
    summary = eval_payload.get("summary") or {}
    return (
        "You are optimizing a clinical extraction prompt template.\n"
        "Edit ONLY the prompt template text.\n"
        "Preserve strict anti-hallucination guardrails and performed-only constraints.\n"
        "Do not make guardrails more permissive.\n"
        "The template must include placeholders: {allowed_keys} and {masked_prompt_text}.\n\n"
        "Current metrics:\n"
        f"{json.dumps(summary, indent=2)}\n\n"
        "Representative PHI-safe failure examples:\n"
        f"{json.dumps(examples, indent=2)}\n\n"
        "Current prompt template:\n"
        f"{current_prompt}\n\n"
        "Return JSON with fields:\n"
        "- prompt_template: full revised template text\n"
        "- rationale: short explanation\n"
        "- changelog: short bullet strings\n"
        "- requires_review: true if edits may loosen safety\n"
    )


def _save_candidate(
    *,
    version: str,
    prompt_text: str,
    metadata: dict[str, Any],
) -> tuple[Path, Path]:
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    prompt_path = PROMPTS_DIR / f"llm_findings_{version}.txt"
    meta_path = PROMPTS_DIR / f"llm_findings_{version}.meta.json"
    prompt_path.write_text(prompt_text, encoding="utf-8")
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return prompt_path, meta_path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.exists():
        raise FileNotFoundError(f"Input dataset not found: {args.input}")
    if not _truthy_env("PROCSUITE_ALLOW_ONLINE"):
        print("Set PROCSUITE_ALLOW_ONLINE=1 before running optimizer (online model calls required).")
        return 2
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is required for optimizer model calls.")
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_rows = load_jsonl(args.input)
    current_prompt, current_version = load_prompt_template(args.base_version)

    eval_path = args.output_dir / f"eval_{current_version}.json"
    base_eval = _run_eval(
        input_path=args.input,
        output_path=eval_path,
        prompt_version=current_version,
        sample_size=max(1, int(args.sample_size)),
        seed=int(args.seed),
        max_retries=max(0, int(args.max_retries)),
    )
    best_eval = base_eval
    best_version = current_version
    best_prompt = current_prompt
    best_metrics = _metrics_from_eval(base_eval)
    no_improve_rounds = 0

    avg_prompt_tokens = _estimate_tokens(
        "\n".join(_extract_prompt_text(row)[:1000] for row in input_rows[: max(1, min(100, len(input_rows)))])
    )
    est_eval_cost = _estimate_cost_usd(
        input_tokens=avg_prompt_tokens * max(1, int(args.sample_size)),
        output_tokens=450 * max(1, int(args.sample_size)),
        input_per_1k=float(args.input_cost_per_1k),
        output_per_1k=float(args.output_cost_per_1k),
    )
    cumulative_est_cost = float(est_eval_cost)

    optimizer = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=str(args.optimizer_model),
        task="judge",
    )

    history: list[dict[str, Any]] = [
        {
            "round": 0,
            "version": best_version,
            "metrics": {
                "required_section_coverage": best_metrics.required_section_coverage,
                "critical_extra_flag_rate": best_metrics.critical_extra_flag_rate,
                "avg_text_similarity": best_metrics.avg_text_similarity,
            },
            "accepted": True,
        }
    ]

    for round_idx in range(1, max(1, int(args.max_iterations)) + 1):
        if cumulative_est_cost >= float(args.budget_usd):
            print(f"Stopping: estimated budget reached (${cumulative_est_cost:.2f}).")
            break

        failure_examples = _collect_failure_examples(
            eval_payload=best_eval,
            input_rows=input_rows,
            max_examples=max(1, min(10, int(args.failure_examples))),
        )
        optimizer_prompt = _build_optimizer_prompt(
            current_prompt=best_prompt,
            eval_payload=best_eval,
            examples=failure_examples,
        )
        raw_optimizer = optimizer.generate(
            optimizer_prompt,
            task="judge",
            response_schema=OPTIMIZER_OUTPUT_SCHEMA,
            prompt_version=f"optimize_llm_findings:{best_version}",
        )
        optimizer_data = json.loads(raw_optimizer)
        candidate_prompt = str(optimizer_data.get("prompt_template") or "").strip()
        if "{allowed_keys}" not in candidate_prompt or "{masked_prompt_text}" not in candidate_prompt:
            raise RuntimeError("Optimizer output missing required placeholders ({allowed_keys}, {masked_prompt_text}).")

        optimizer_cost = _estimate_cost_usd(
            input_tokens=_estimate_tokens(optimizer_prompt),
            output_tokens=_estimate_tokens(raw_optimizer),
            input_per_1k=float(args.input_cost_per_1k),
            output_per_1k=float(args.output_cost_per_1k),
        )
        cumulative_est_cost += float(optimizer_cost)

        model_requires_review = bool(optimizer_data.get("requires_review"))
        heuristic_requires_review = _guardrails_softened(best_prompt, candidate_prompt)
        requires_review = bool(model_requires_review or heuristic_requires_review)

        candidate_version = _next_prompt_version()
        candidate_meta = {
            "parent_version": best_version,
            "round": round_idx,
            "model": str(args.optimizer_model),
            "rationale": str(optimizer_data.get("rationale") or "").strip(),
            "changelog": list(optimizer_data.get("changelog") or []),
            "requires_review": requires_review,
            "heuristic_guardrail_warning": heuristic_requires_review,
            "estimated_cost_usd_cumulative": round(float(cumulative_est_cost), 4),
        }
        prompt_path, meta_path = _save_candidate(
            version=candidate_version,
            prompt_text=candidate_prompt,
            metadata=candidate_meta,
        )
        print(f"Wrote candidate prompt: {prompt_path}")
        if requires_review:
            print("WARNING: Candidate may loosen guardrails. Manual confirmation required before promotion.")
            print(f"Review marker: {meta_path}")
            history.append({"round": round_idx, "version": candidate_version, "accepted": False, "requires_review": True})
            break

        candidate_eval_path = args.output_dir / f"eval_{candidate_version}.json"
        candidate_eval = _run_eval(
            input_path=args.input,
            output_path=candidate_eval_path,
            prompt_version=candidate_version,
            sample_size=max(1, int(args.sample_size)),
            seed=int(args.seed),
            max_retries=max(0, int(args.max_retries)),
        )
        cumulative_est_cost += float(est_eval_cost)
        candidate_metrics = _metrics_from_eval(candidate_eval)

        improved = _is_better(candidate_metrics, best_metrics, epsilon=float(args.epsilon))
        if improved:
            best_eval = candidate_eval
            best_version = candidate_version
            best_prompt = candidate_prompt
            best_metrics = candidate_metrics
            no_improve_rounds = 0
        else:
            no_improve_rounds += 1

        history.append(
            {
                "round": round_idx,
                "version": candidate_version,
                "accepted": improved,
                "metrics": {
                    "required_section_coverage": candidate_metrics.required_section_coverage,
                    "critical_extra_flag_rate": candidate_metrics.critical_extra_flag_rate,
                    "avg_text_similarity": candidate_metrics.avg_text_similarity,
                },
            }
        )

        if no_improve_rounds >= 2:
            print("Stopping: improvement < epsilon for 2 consecutive rounds.")
            break

    result_path = args.output_dir / "optimization_result.json"
    result_payload = {
        "input": str(args.input),
        "base_version": current_version,
        "best_version": best_version,
        "best_metrics": {
            "required_section_coverage": best_metrics.required_section_coverage,
            "critical_extra_flag_rate": best_metrics.critical_extra_flag_rate,
            "avg_text_similarity": best_metrics.avg_text_similarity,
        },
        "history": history,
        "estimated_cost_usd": round(float(cumulative_est_cost), 4),
        "budget_usd": float(args.budget_usd),
    }
    result_path.write_text(json.dumps(result_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Best prompt version: {best_version}")
    print(f"Estimated cumulative cost: ${cumulative_est_cost:.2f}")
    print(f"Wrote optimization summary: {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
