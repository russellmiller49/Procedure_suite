"""Self-correction helper for CPT classifier errors."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.common.llm import GeminiLLM


def load_cpt_errors(path: str) -> list[dict[str, Any]]:
    error_path = Path(path)
    if not error_path.exists():
        return []
    with error_path.open() as f:
        rows: list[dict[str, Any]] = []
        for line in f:
            if not line.strip():
                continue
            parsed = json.loads(line)
            if isinstance(parsed, dict):
                rows.append(parsed)
        return rows


def group_errors_by_code(errors: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for err in errors:
        gold = set(err.get("gold_codes", []))
        pred = set(err.get("predicted_codes", []))
        missing = gold - pred
        extra = pred - gold
        for code in missing:
            grouped[code].append({"type": "missing", **err})
        for code in extra:
            grouped[code].append({"type": "extra", **err})
    return grouped


def build_prompt_for_code(code: str, examples: list[dict[str, Any]]) -> str:
    lines = [
        f"We have a CPT classification model with recurring errors for code {code}.",
        "Provide lexical cues or rule suggestions to improve detection.",
        "Examples:",
    ]
    for idx, ex in enumerate(examples, start=1):
        lines.append(
            f"Example {idx} ({ex.get('type')}):\n  Note excerpt: {ex.get('note_text','')[:600]}\n"
            f"  Gold: {ex.get('gold_codes')}\n  Predicted: {ex.get('predicted_codes')}"
        )
    lines.append(
        (
            "Return JSON with keys: {\n"
            '  "suggested_rules": "text or pseudo-code for rule-based cues",\n'
            '  "keywords": ["list", "of", "keywords"],\n'
            '  "comments": "why these cues should help"\n}'
        )
    )
    return "\n".join(lines)


def suggest_corrections_for_code(code: str, examples: list[dict[str, Any]]) -> dict[str, Any]:
    prompt = build_prompt_for_code(code, examples)
    llm = GeminiLLM()
    try:
        raw = llm.generate(prompt)
        parsed = json.loads(raw.strip().strip("`"))
        if isinstance(parsed, dict):
            return parsed
        return {"error": "LLM returned non-object JSON"}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"LLM failed: {exc}"}


__all__ = [
    "load_cpt_errors",
    "group_errors_by_code",
    "suggest_corrections_for_code",
]
