#!/usr/bin/env python3
"""
Regenerate data/ml_training/granular_ner/stats.json from current JSONL artifacts.

Inputs (all under --base-dir, default: data/ml_training/granular_ner):
  - ner_dataset_all.jsonl  (required) (records: {"id","text","entities":[{"start","end","label","text"}] ...})
  - spans.jsonl            (optional) (records: {"note_id","label","span_text","start_char","end_char","hydration_status"})

Outputs:
  - stats.json (same top-level shape as extract_ner_from_excel.py stats)

This is useful when stats.json becomes stale/out-of-sync after manual edits,
reruns, de-duplication, or incremental appends.

Important:
- Alignment stats + label_counts are recomputed from ner_dataset_all.jsonl
  (the actual training file).
- hydration_status_counts (if present) is computed from spans.jsonl only.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


@dataclass
class Stats:
    total_files: int = 0
    successful_files: int = 0
    total_notes: int = 0
    total_spans_raw: int = 0
    total_spans_valid: int = 0
    alignment_warnings: int = 0
    alignment_errors: int = 0
    label_counts: Counter | None = None
    hydration_status_counts: Counter | None = None
    duplicate_note_ids: int = 0

    def to_jsonable(self) -> dict:
        return {
            "total_files": self.total_files,
            "successful_files": self.successful_files,
            "total_notes": self.total_notes,
            "total_spans_raw": self.total_spans_raw,
            "total_spans_valid": self.total_spans_valid,
            "alignment_warnings": self.alignment_warnings,
            "alignment_errors": self.alignment_errors,
            "label_counts": dict((self.label_counts or Counter()).most_common()),
            "hydration_status_counts": dict(self.hydration_status_counts or Counter()),
            "duplicate_note_ids": self.duplicate_note_ids,
        }


def _iter_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield line_num, json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path} at line {line_num}: {e}") from e


def regenerate(base_dir: Path) -> tuple[Stats, list[str]]:
    ner_path = base_dir / "ner_dataset_all.jsonl"
    spans_path = base_dir / "spans.jsonl"

    if not ner_path.exists():
        raise FileNotFoundError(f"Missing required file: {ner_path}")

    stats = Stats(label_counts=Counter(), hydration_status_counts=Counter())

    # --- Records / "files" ---
    seen_ids: set[str] = set()
    dup_ids: set[str] = set()
    record_ids: list[str] = []
    success_ids: set[str] = set()

    for _, rec in _iter_jsonl(ner_path):
        rid = rec.get("id") or rec.get("note_id")
        if not rid:
            continue
        rid = str(rid)
        record_ids.append(rid)
        if rid in seen_ids:
            dup_ids.add(rid)
        else:
            seen_ids.add(rid)

        text = rec.get("text") or ""
        entities = rec.get("entities") or rec.get("spans") or []
        if isinstance(entities, list) and len(entities) > 0:
            success_ids.add(rid)

        # Validate entities (alignment + label counts) against the record text.
        if not isinstance(text, str):
            text = str(text)

        if not isinstance(entities, list):
            stats.alignment_errors += 1
            continue

        for ent in entities:
            stats.total_spans_raw += 1

            # Support both dict entities and list-style [start,end,label] / [start,end,label,text]
            if isinstance(ent, dict):
                start = ent.get("start")
                end = ent.get("end")
                label = ent.get("label")
                expected = ent.get("text")
            elif isinstance(ent, (list, tuple)) and len(ent) >= 3:
                start, end, label = ent[0], ent[1], ent[2]
                expected = ent[3] if len(ent) >= 4 else None
            else:
                stats.alignment_errors += 1
                continue

            try:
                start_i = int(start)
                end_i = int(end)
            except (TypeError, ValueError):
                stats.alignment_errors += 1
                continue

            if start_i < 0 or end_i < 0 or end_i > len(text) or start_i > end_i:
                stats.alignment_errors += 1
                continue

            extracted = text[start_i:end_i]
            if expected is None:
                # If no expected text was provided, treat as valid offsets-only.
                stats.total_spans_valid += 1
                stats.label_counts[str(label or "")] += 1
                continue

            expected_s = str(expected)
            if extracted == expected_s:
                stats.total_spans_valid += 1
                stats.label_counts[str(label or "")] += 1
                continue

            if _normalize_whitespace(extracted) == _normalize_whitespace(expected_s):
                stats.alignment_warnings += 1
                stats.total_spans_valid += 1
                stats.label_counts[str(label or "")] += 1
                continue

            stats.alignment_errors += 1

    stats.total_files = len(seen_ids)
    stats.total_notes = len(seen_ids)
    stats.successful_files = len(success_ids)
    stats.duplicate_note_ids = len(dup_ids)

    # --- Optional hydration status counts (from spans.jsonl) ---
    if spans_path.exists():
        for _, span in _iter_jsonl(spans_path):
            hydration = span.get("hydration_status")
            if hydration:
                stats.hydration_status_counts[str(hydration)] += 1

    # Return duplicate IDs for convenience
    dup_list = sorted(list(dup_ids))
    return stats, dup_list


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate granular_ner stats.json from JSONL files")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data/ml_training/granular_ner"),
        help="Directory containing ner_dataset_all.jsonl / notes.jsonl / spans.jsonl",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write stats.json (default: print only).",
    )
    args = parser.parse_args()

    stats, dup_ids = regenerate(args.base_dir)
    payload = stats.to_jsonable()

    print(json.dumps(payload, indent=2))
    if dup_ids:
        print("\nDuplicate note IDs detected:")
        for nid in dup_ids:
            print(f" - {nid}")

    if args.write:
        out_path = args.base_dir / "stats.json"
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

