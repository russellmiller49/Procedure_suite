#!/usr/bin/env python3
"""Prepare a Prodigy relabel batch from an existing human-labeled registry CSV.

Use case:
- You previously annotated registry procedure flags (e.g. in an older label schema).
- You added/renamed labels (e.g. updated the canonical label schema).
- You want to **re-annotate a focused subset** (e.g. all rigid bronchoscopy cases)
  in a fresh Prodigy dataset using the updated label set.

This script:
- Loads a human CSV (with note_text + label columns)
- Filters rows where one or more filter labels are positive (default: rigid_bronchoscopy)
- Expands cats to the *current* canonical label list from `modules/ml_coder/registry_label_schema.py`
- Emits Prodigy `textcat.manual` tasks:
    {"text": "...", "cats": {...}, "_view_id": "textcat", "meta": {...}}

Typical usage:

  python scripts/prodigy_prepare_registry_relabel_batch.py \
    --input-csv data/ml_training/registry_human_v1_backup.csv \
    --output-file data/ml_training/registry_rigid_review.jsonl \
    --filter-label rigid_bronchoscopy \
    --prefill-non-thermal-from-rigid \
    --limit 0

Then annotate in a new dataset:

  make registry-prodigy-annotate \
    REG_PRODIGY_DATASET=registry_v2_rigid_relabel \
    REG_PRODIGY_BATCH_FILE=data/ml_training/registry_rigid_review.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Repo root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ml_coder.registry_label_schema import REGISTRY_LABELS  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--input-csv",
        type=Path,
        required=True,
        help="Human-labeled registry CSV (must include note_text)",
    )
    p.add_argument(
        "--output-file",
        type=Path,
        default=Path("data/ml_training/registry_rigid_review.jsonl"),
        help="Output Prodigy JSONL for relabeling",
    )
    p.add_argument(
        "--filter-label",
        action="append",
        default=["rigid_bronchoscopy"],
        help="Only include rows where this label column is positive. Repeatable.",
    )
    p.add_argument(
        "--min-positives",
        type=int,
        default=1,
        help="Min number of positive filter labels required (default: 1)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of rows to emit (0 = no limit)",
    )
    p.add_argument(
        "--prefill-non-thermal-from-rigid",
        action="store_true",
        help=(
            "Heuristic prefill: set tumor_debulking_non_thermal=1 when rigid_bronchoscopy=1 "
            "and thermal_ablation=0 and cryotherapy=0. (You still review/edit in Prodigy.)"
        ),
    )
    p.add_argument(
        "--text-key",
        choices=["text", "note_text"],
        default="text",
        help="Key to use for the task text in Prodigy JSONL",
    )
    return p.parse_args(argv)


def _coerce01(v: Any) -> int:
    try:
        return 1 if int(v) != 0 else 0
    except Exception:
        return 1 if bool(v) else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input_csv.exists():
        raise SystemExit(f"Input CSV not found: {args.input_csv}")

    df = pd.read_csv(args.input_csv)
    # Be tolerant of messy CSV headers (common when edited/exported in Excel):
    # - trailing spaces
    # - BOM markers
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
    if "note_text" not in df.columns:
        raise SystemExit(
            "Input CSV must contain a 'note_text' column (after header normalization). "
            f"Found columns: {list(df.columns)[:10]}..."
        )

    # Normalize user-provided filter labels too (trim whitespace).
    filter_labels = [str(x).strip() for x in (args.filter_label or []) if str(x).strip()]
    missing_filter = [c for c in filter_labels if c not in df.columns]
    if missing_filter:
        raise SystemExit(f"Missing filter label columns in CSV: {missing_filter}")

    # Filter rows
    if filter_labels:
        pos = df[filter_labels].fillna(0).astype(int).sum(axis=1)
        df = df[pos >= int(args.min_positives)].copy()

    if args.limit and int(args.limit) > 0:
        df = df.head(int(args.limit))

    labels = list(REGISTRY_LABELS)

    # Emit Prodigy tasks
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    for _, row in df.iterrows():
        note_text = str(row.get("note_text") or "").strip()
        if not note_text:
            continue

        cats: dict[str, int] = {}
        for label in labels:
            if label in df.columns:
                cats[label] = _coerce01(row.get(label))
            else:
                cats[label] = 0

        if args.prefill_non_thermal_from_rigid and "tumor_debulking_non_thermal" in cats:
            rigid = cats.get("rigid_bronchoscopy", 0)
            thermal = cats.get("thermal_ablation", 0)
            cryo = cats.get("cryotherapy", 0)
            if rigid == 1 and thermal == 0 and cryo == 0:
                cats["tumor_debulking_non_thermal"] = 1

        meta = {
            "source_csv": str(args.input_csv),
            "filter_labels": filter_labels,
        }
        if "encounter_id" in df.columns:
            meta["encounter_id"] = str(row.get("encounter_id") or "")

        task = {
            args.text_key: note_text,
            "cats": cats,
            "_view_id": "textcat",
            "meta": meta,
            "config": {"exclusive": False},
        }

        args.output_file.write_text("", encoding="utf-8") if written == 0 else None
        with args.output_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(task, ensure_ascii=False) + "\n")
        written += 1

    print(f"Wrote {written} relabel tasks to {args.output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
