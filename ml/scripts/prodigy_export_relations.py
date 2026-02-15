#!/usr/bin/env python3
"""Export Prodigy accept/reject annotations for relation edges (Phase 8).

Supports two modes:
  - DB mode:   --dataset <name> (requires Prodigy installed and configured)
  - File mode: --input-jsonl <path> (reads a Prodigy-exported JSONL file; CI friendly)

Outputs:
  - JSONL where each row is an annotated edge with a binary label:
    - label=1: edge accepted
    - label=0: edge rejected

Notes:
  - This exporter is offline-safe: no LLM calls.
  - We avoid emitting any raw note text; edges are constructed from entity labels/attributes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Iterable

# Add repo root to path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

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


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _accept_list(example: dict[str, Any]) -> list[str]:
    accept = example.get("accept")
    if accept is None:
        return []
    if isinstance(accept, list):
        return [str(x) for x in accept if str(x).strip()]
    return [str(accept).strip()] if str(accept).strip() else []


def _edge_from_example(example: dict[str, Any]) -> dict[str, Any] | None:
    edge = example.get("edge")
    if isinstance(edge, dict) and edge:
        return edge
    meta = _as_dict(example.get("meta"))
    edge = meta.get("edge")
    return edge if isinstance(edge, dict) and edge else None


def _compute_edge_id(example: dict[str, Any], edge: dict[str, Any]) -> str:
    meta = _as_dict(example.get("meta"))
    edge_id = str(meta.get("edge_id") or "").strip()
    if edge_id:
        return edge_id
    case_id = str(meta.get("case_id") or "").strip()
    entity_id = str(edge.get("entity_id") or "").strip()
    relation = str(edge.get("relation") or "").strip()
    linked_to_id = str(edge.get("linked_to_id") or "").strip()
    key = f"{case_id}|{entity_id}|{relation}|{linked_to_id}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def _label_from_example(example: dict[str, Any]) -> int | None:
    accept_ids = set(_accept_list(example))
    if "reject" in accept_ids or "no" in accept_ids:
        return 0
    if "accept" in accept_ids or "yes" in accept_ids:
        return 1

    # Fallback for annotators using built-in accept/reject keys without selecting options.
    answer = str(example.get("answer") or "").strip().lower()
    if answer == "reject":
        return 0
    return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dataset", type=str, help="Prodigy dataset name (DB mode)")
    group.add_argument("--input-jsonl", type=Path, help="Prodigy-exported JSONL file (file mode)")

    parser.add_argument("--output-jsonl", type=Path, required=True, help="Output labeled edges JSONL")
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help="Optional output CSV summary (one row per edge)",
    )
    parser.add_argument(
        "--include-unlabeled",
        action="store_true",
        help="Include examples without a clear accept/reject selection as label=null",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args(argv)

    dataset_name = None
    source_file = None
    if args.dataset:
        dataset_name = args.dataset
        examples = load_prodigy_dataset(args.dataset)
    else:
        source_file = args.input_jsonl.name if args.input_jsonl else None
        examples = list(iter_jsonl(args.input_jsonl))

    rows_by_id: dict[str, dict[str, Any]] = {}
    for ex in examples:
        edge = _edge_from_example(ex)
        if edge is None:
            continue

        label = _label_from_example(ex)
        if label is None and not args.include_unlabeled:
            continue

        meta = _as_dict(ex.get("meta"))
        edge_id = _compute_edge_id(ex, edge)

        out = {
            "edge_id": edge_id,
            "case_id": meta.get("case_id") or None,
            "edge_source": meta.get("edge_source") or None,
            "relation": meta.get("relation") or edge.get("relation") or None,
            "label": label,
            "confidence": meta.get("confidence") or edge.get("confidence") or None,
            "reasoning_short": edge.get("reasoning_short") or None,
            "edge": edge,
            "source_entity": ex.get("source_entity") if isinstance(ex.get("source_entity"), dict) else None,
            "target_entity": ex.get("target_entity") if isinstance(ex.get("target_entity"), dict) else None,
            "source_path": meta.get("source_path") or meta.get("source") or source_file,
            "prodigy_dataset": dataset_name or meta.get("prodigy_dataset") or None,
            "answer": ex.get("answer") or None,
            "accept": _accept_list(ex),
        }
        rows_by_id[edge_id] = out  # last write wins

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows_by_id.values())
    with open(args.output_jsonl, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    if args.output_csv:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = [
            "edge_id",
            "case_id",
            "edge_source",
            "relation",
            "label",
            "confidence",
            "entity_id",
            "linked_to_id",
            "source_label",
            "target_label",
            "source_path",
            "prodigy_dataset",
        ]
        with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            for row in rows:
                edge = row.get("edge") if isinstance(row.get("edge"), dict) else {}
                src = row.get("source_entity") if isinstance(row.get("source_entity"), dict) else {}
                dst = row.get("target_entity") if isinstance(row.get("target_entity"), dict) else {}
                w.writerow(
                    {
                        **row,
                        "entity_id": str(edge.get("entity_id") or ""),
                        "linked_to_id": str(edge.get("linked_to_id") or ""),
                        "source_label": str(src.get("label") or ""),
                        "target_label": str(dst.get("label") or ""),
                    }
                )

    logger.info("Wrote %d labeled edges to %s", len(rows), args.output_jsonl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

