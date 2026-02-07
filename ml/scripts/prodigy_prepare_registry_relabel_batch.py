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
import logging
import random
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Repo root on sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS  # noqa: E402


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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
        "--filter-missing-label",
        action="append",
        default=[],
        help="Only include rows where this label column is NOT positive (i.e., 0/false). Repeatable.",
    )
    p.add_argument(
        "--min-positives",
        type=int,
        default=0,
        help="Skip rows with fewer than N total positive labels (across all canonical labels).",
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
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed used when shuffling before applying --limit",
    )
    p.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle rows after filtering (before applying --limit).",
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

    logger.info("Reading CSV: %s", args.input_csv)
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

    labels = list(REGISTRY_LABELS)

    # Normalize user-provided filter labels too (trim whitespace).
    filter_labels = [str(x).strip() for x in (args.filter_label or []) if str(x).strip()]
    filter_missing = [str(x).strip() for x in (args.filter_missing_label or []) if str(x).strip()]

    missing_filter = [c for c in (filter_labels + filter_missing) if c not in df.columns]
    if missing_filter:
        raise SystemExit(f"Missing filter label columns in CSV: {missing_filter}")

    logger.info("Loaded %d rows. Applying filters...", len(df))

    # Ensure canonical label columns exist (missing labels treated as 0).
    for label in labels:
        if label not in df.columns:
            df[label] = 0

    # Filter: must have at least one of filter_labels positive (unless none provided).
    if filter_labels:
        must_pos = df[filter_labels].fillna(0).applymap(_coerce01).sum(axis=1)
        df = df[must_pos >= 1].copy()

    # Filter: must have filter_missing labels NOT positive.
    if filter_missing:
        any_missing_pos = df[filter_missing].fillna(0).applymap(_coerce01).sum(axis=1)
        df = df[any_missing_pos == 0].copy()

    # Filter: minimum number of total positives across all canonical labels.
    min_pos = int(args.min_positives or 0)
    if min_pos > 0:
        total_pos = df[labels].fillna(0).applymap(_coerce01).sum(axis=1)
        df = df[total_pos >= min_pos].copy()

    if args.shuffle and len(df) > 1:
        rng = random.Random(int(args.seed))
        df = df.sample(frac=1.0, random_state=rng.randint(0, 2**31 - 1)).reset_index(drop=True)

    if args.limit and int(args.limit) > 0:
        df = df.head(int(args.limit))

    # Emit Prodigy tasks
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Selected %d rows for review.", len(df))

    written = 0
    with args.output_file.open("w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            note_text = str(row.get("note_text") or "").strip()
            if not note_text:
                continue

            cats: dict[str, int] = {label: _coerce01(row.get(label, 0)) for label in labels}

            # Optional prefill logic for specific cleanup workflows.
            if args.prefill_non_thermal_from_rigid and "tumor_debulking_non_thermal" in cats:
                rigid = cats.get("rigid_bronchoscopy", 0)
                thermal = cats.get("thermal_ablation", 0)
                cryo = cats.get("cryotherapy", 0)
                if rigid == 1 and thermal == 0 and cryo == 0:
                    cats["tumor_debulking_non_thermal"] = 1

            meta = {
                "source_csv": str(args.input_csv),
                "filter_labels": filter_labels,
                "filter_missing_label": filter_missing,
                "filter_hit": (filter_labels[0] if filter_labels else "manual"),
            }
            if "encounter_id" in df.columns:
                meta["encounter_id"] = str(row.get("encounter_id") or "")

            task = {
                # Prodigy `textcat.manual` expects a `text` field by default. We keep
                # this configurable for compatibility, but `text` is recommended.
                args.text_key: note_text,
                "cats": cats,
                "_view_id": "textcat",
                "meta": meta,
                # Non-exclusive is critical for registry multi-label.
                "config": {"exclusive": False},
            }

            f.write(json.dumps(task, ensure_ascii=False) + "\n")
            written += 1

    logger.info("Wrote %d tasks to %s", written, args.output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
