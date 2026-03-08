#!/usr/bin/env python3
"""Build a frozen reporter seed fixture from canonical report text."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


def configure_eval_env() -> dict[str, str]:
    if _truthy_env("PROCSUITE_ALLOW_ONLINE"):
        return {}

    forced = {
        "PROCSUITE_SKIP_DOTENV": "1",
        "PROCSUITE_PIPELINE_MODE": "extraction_first",
        "REGISTRY_EXTRACTION_ENGINE": "parallel_ner",
        "REGISTRY_SELF_CORRECT_ENABLED": "0",
        "REGISTRY_LLM_FALLBACK_ON_COVERAGE_FAIL": "0",
        "REGISTRY_AUDITOR_SOURCE": "disabled",
        "REGISTRY_USE_STUB_LLM": "1",
        "GEMINI_OFFLINE": "1",
        "OPENAI_OFFLINE": "1",
        "REPORTER_DISABLE_LLM": "1",
        "QA_REPORTER_ALLOW_SIMPLE_FALLBACK": "0",
        "PROCSUITE_FAST_MODE": "1",
        "PROCSUITE_SKIP_WARMUP": "1",
    }

    applied: dict[str, str] = {}
    for key, value in forced.items():
        if os.environ.get(key) != value:
            os.environ[key] = value
            applied[key] = value
    return applied


_APPLIED_ENV_DEFAULTS = configure_eval_env()

from app.common.path_redaction import sanitize_path_fields
from app.common.reporter_seed_eval import load_eval_rows
from app.registry.application.registry_service import RegistryService


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prompt-field", default="prompt_text")
    parser.add_argument(
        "--completion-source",
        choices=["completion_canonical", "prompt_text"],
        default="completion_canonical",
        help="Build the fixture record from canonical completions or raw prompts.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows = load_eval_rows(args.input, prompt_field=str(args.prompt_field or "prompt_text"))
    registry_service = RegistryService()

    cases: list[dict[str, object]] = []
    for row in rows:
        source_text = row.completion_canonical if args.completion_source == "completion_canonical" else row.prompt_text
        result = registry_service.extract_fields_extraction_first(source_text)
        cases.append(
            {
                "id": row.id,
                "masked_prompt_text": row.prompt_text,
                "record": result.record.model_dump(exclude_none=False),
                "cpt_codes": [str(code) for code in list(result.cpt_codes or [])],
                "warnings": [],
                "needs_review": bool(result.needs_manual_review),
                "accepted_findings": 0,
                "dropped_findings": 0,
            }
        )

    payload = {
        "schema_version": "reporter_seed_llm_fixture.v1",
        "kind": "reporter_seed_fixture",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input_path": str(args.input),
        "output_path": str(args.output),
        "prompt_field": str(args.prompt_field or "prompt_text"),
        "completion_source": str(args.completion_source),
        "environment_defaults_applied": _APPLIED_ENV_DEFAULTS,
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(sanitize_path_fields(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote reporter seed fixture: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
