#!/usr/bin/env python3
"""Export Prodigy multi-label annotations for registry procedure flags.

Supports two modes:
  - DB mode:   --dataset <name> (requires Prodigy installed and configured)
  - File mode: --input-jsonl <path> (reads a Prodigy-exported JSONL file; CI friendly)

Outputs a training CSV compatible with `ml/scripts/train_roberta.py`:
  - note_text
  - label columns (0/1) for each item in `REGISTRY_LABELS`
  - label_source="prodigy"
  - label_confidence=1.0
  - optional metadata columns (encounter_id/source_file/prodigy_dataset)

Input formats supported:
  - Prodigy `choice` style: uses `accept: [label, ...]`
  - Prodigy `textcat` style: may store `accept` OR `cats: {label: 0/1}`
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from typing import Any, Iterable

# Add repo root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from ml.lib.ml_coder.registry_label_schema import (  # noqa: E402, I001
    REGISTRY_LABELS,
    compute_encounter_id,
)

logger = logging.getLogger(__name__)


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping invalid JSON at %s:%d", path, line_num)
                continue
            if isinstance(obj, dict):
                yield obj


def load_prodigy_dataset(dataset: str) -> list[dict[str, Any]]:
    try:
        from prodigy.components.db import connect
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "Prodigy is not installed; use --input-jsonl for file mode or install prodigy."
        ) from exc

    db = connect()
    if dataset not in db:  # pragma: no cover
        available = getattr(db, "datasets", [])
        raise SystemExit(f"Prodigy dataset not found: {dataset}. Available: {available}")

    examples = db.get_dataset_examples(dataset)
    return list(examples)


def _normalize_text(text: Any) -> str:
    return str(text or "").strip()


def _accept_list(example: dict[str, Any]) -> list[str]:
    accept = example.get("accept")
    if accept is None:
        return []
    if isinstance(accept, list):
        return [str(x) for x in accept if str(x).strip()]
    return [str(accept).strip()] if str(accept).strip() else []


def _accepted_labels(example: dict[str, Any], labels: list[str]) -> list[str]:
    accepted = _accept_list(example)
    if accepted:
        return accepted

    cats = example.get("cats")
    if isinstance(cats, dict):
        out: list[str] = []
        for label in labels:
            val = cats.get(label)
            if isinstance(val, bool):
                if val:
                    out.append(label)
                continue
            if isinstance(val, int | float):
                if float(val) >= 0.5:
                    out.append(label)
        return out
    return []

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dataset", type=str, help="Prodigy dataset name (DB mode)")
    group.add_argument("--input-jsonl", type=Path, help="Prodigy-exported JSONL file (file mode)")

    parser.add_argument("--output-csv", type=Path, required=True, help="Output training CSV")
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=None,
        help="Optional exported JSONL (deduped)",
    )
    parser.add_argument(
        "--label-source",
        type=str,
        default="human",
        help="Label source value to write",
    )
    parser.add_argument(
        "--label-confidence",
        type=float,
        default=1.0,
        help="Label confidence value to write",
    )
    parser.add_argument(
        "--include-empty-accept",
        action="store_true",
        help="Include examples with empty/missing accept as all-zero labels",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args(argv)

    labels = list(REGISTRY_LABELS)

    dataset_name = None
    source_file = None
    if args.dataset:
        dataset_name = args.dataset
        examples = load_prodigy_dataset(args.dataset)
    else:
        source_file = args.input_jsonl.name if args.input_jsonl else None
        examples = list(iter_jsonl(args.input_jsonl))

    rows_by_encounter: dict[str, dict[str, Any]] = {}
    for ex in examples:
        if ex.get("answer") != "accept":
            continue

        text = _normalize_text(ex.get("text") or ex.get("note_text") or ex.get("note"))
        if not text:
            continue

        accepted = _accepted_labels(ex, labels)
        if not accepted and not args.include_empty_accept:
            continue

        accepted_set = set(accepted)
        label_row = {label: int(label in accepted_set) for label in labels}

        meta = ex.get("meta") if isinstance(ex.get("meta"), dict) else {}
        encounter_id = compute_encounter_id(text)

        row: dict[str, Any] = {
            "note_text": text,
            "encounter_id": encounter_id,
            "source_file": meta.get("source_file") or meta.get("source") or source_file,
            "label_source": str(args.label_source),
            "label_confidence": float(args.label_confidence),
            "prodigy_dataset": dataset_name or meta.get("prodigy_dataset") or None,
        }
        row.update(label_row)
        rows_by_encounter[encounter_id] = row  # last write wins

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "note_text",
        "encounter_id",
        "source_file",
        "label_source",
        "label_confidence",
        "prodigy_dataset",
        *labels,
    ]

    rows = list(rows_by_encounter.values())
    with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    if args.output_jsonl:
        args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_jsonl, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    logger.info("Wrote %d rows to %s", len(rows), args.output_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
