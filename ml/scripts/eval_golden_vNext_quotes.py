#!/usr/bin/env python3
"""Validate vNext golden fixtures: evidence quotes must be anchorable.

This is a lightweight CI guardrail for Phase 4:
- Fixtures live under `data/knowledge/golden_extractions_vNext/approved/`.
- Each fixture stores note_text + migrated_evidence[].draft.{prefix_3_words, exact_quote,
  suffix_3_words}.
- At runtime, spans are computed deterministically by the quote anchor.

This script:
- skips gracefully when no fixtures are present (repo may not include them)
- never prints note text or quotes (only ids/counts)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _iter_json_files(input_dir: Path, pattern: str) -> Iterable[Path]:
    if input_dir.is_file():
        yield input_dir
        return
    if not input_dir.exists() or not input_dir.is_dir():
        return
    yield from sorted(input_dir.glob(pattern))


@dataclass(frozen=True)
class EvalCounts:
    fixtures: int = 0
    evidence_total: int = 0
    evidence_anchor_ok: int = 0
    evidence_quote_missing: int = 0
    evidence_not_substring: int = 0
    evidence_unanchorable: int = 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate vNext fixtures (quote anchoring).")
    p.add_argument(
        "--input",
        type=Path,
        default=Path("data/knowledge/golden_extractions_vNext/approved"),
        help="Directory containing approved vNext fixtures (JSON).",
    )
    p.add_argument(
        "--pattern",
        type=str,
        default="*.json",
        help="Glob pattern for fixture files when --input is a directory.",
    )
    p.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="Exit non-zero if anchored rate is below this percent (0-100).",
    )
    return p.parse_args(argv)


def _as_str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    files = list(_iter_json_files(args.input, args.pattern))
    if not files:
        print(f"eval_golden_vNext_quotes: no fixtures found under {args.input}; skipping.")
        return 0

    from app.evidence.quote_anchor import anchor_quote

    counts = EvalCounts(fixtures=len(files))

    for path in files:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            print(f"eval_golden_vNext_quotes: failed to parse {path.name}")
            continue

        if not isinstance(obj, dict):
            continue

        note_text = _as_str(obj.get("note_text"))
        migrated = obj.get("migrated_evidence")
        if not note_text or not isinstance(migrated, list):
            continue

        for item in migrated:
            if not isinstance(item, dict):
                continue
            draft = item.get("draft")
            if not isinstance(draft, dict):
                continue

            counts = EvalCounts(
                fixtures=counts.fixtures,
                evidence_total=counts.evidence_total + 1,
                evidence_anchor_ok=counts.evidence_anchor_ok,
                evidence_quote_missing=counts.evidence_quote_missing,
                evidence_not_substring=counts.evidence_not_substring,
                evidence_unanchorable=counts.evidence_unanchorable,
            )

            quote = _as_str(draft.get("exact_quote")).strip()
            if not quote:
                counts = EvalCounts(
                    fixtures=counts.fixtures,
                    evidence_total=counts.evidence_total,
                    evidence_anchor_ok=counts.evidence_anchor_ok,
                    evidence_quote_missing=counts.evidence_quote_missing + 1,
                    evidence_not_substring=counts.evidence_not_substring,
                    evidence_unanchorable=counts.evidence_unanchorable,
                )
                continue

            if quote not in note_text:
                counts = EvalCounts(
                    fixtures=counts.fixtures,
                    evidence_total=counts.evidence_total,
                    evidence_anchor_ok=counts.evidence_anchor_ok,
                    evidence_quote_missing=counts.evidence_quote_missing,
                    evidence_not_substring=counts.evidence_not_substring + 1,
                    evidence_unanchorable=counts.evidence_unanchorable,
                )
                continue

            prefix = _as_str(draft.get("prefix_3_words")).strip() or None
            suffix = _as_str(draft.get("suffix_3_words")).strip() or None
            anchored = anchor_quote(note_text, quote, prefix=prefix, suffix=suffix)
            if anchored.span is None:
                counts = EvalCounts(
                    fixtures=counts.fixtures,
                    evidence_total=counts.evidence_total,
                    evidence_anchor_ok=counts.evidence_anchor_ok,
                    evidence_quote_missing=counts.evidence_quote_missing,
                    evidence_not_substring=counts.evidence_not_substring,
                    evidence_unanchorable=counts.evidence_unanchorable + 1,
                )
                continue

            counts = EvalCounts(
                fixtures=counts.fixtures,
                evidence_total=counts.evidence_total,
                evidence_anchor_ok=counts.evidence_anchor_ok + 1,
                evidence_quote_missing=counts.evidence_quote_missing,
                evidence_not_substring=counts.evidence_not_substring,
                evidence_unanchorable=counts.evidence_unanchorable,
            )

    total = counts.evidence_total
    ok = counts.evidence_anchor_ok
    rate = (ok / total) * 100.0 if total else 0.0

    print(
        "eval_golden_vNext_quotes: "
        f"fixtures={counts.fixtures} evidence_total={total} anchored_ok={ok} "
        f"rate={rate:.1f}% missing_quote={counts.evidence_quote_missing} "
        f"not_substring={counts.evidence_not_substring} unanchorable={counts.evidence_unanchorable}"
    )

    if args.fail_under is not None and total > 0 and rate < float(args.fail_under):
        print(f"eval_golden_vNext_quotes: FAIL (rate {rate:.1f}% < {float(args.fail_under):.1f}%)")
        return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
