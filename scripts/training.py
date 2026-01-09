#!/usr/bin/env python3
"""
Generate an unlabeled JSONL file for Registry Prodigy annotation from an existing
registry training CSV.

This is a convenience helper for the Registry "Diamond Loop":
- Start with `data/ml_training/registry_train.csv` (or train/val/test)
- Filter to "weak" classes to create a high-yield annotation pool
- Emit JSONL where each line has `note_text` (or `text`) for Prodigy prep.

Next step (model-assisted / pre-annotated Prodigy tasks):
- Convert the unlabeled notes JSONL into a Prodigy-ready batch with prefilled
  labels from the *current* registry model (ONNX bundle when available, sklearn
  fallback otherwise):

  make registry-prodigy-prepare \
    REG_PRODIGY_INPUT_FILE=data/ml_training/registry_unlabeled_notes.jsonl \
    REG_PRODIGY_COUNT=200

Typical usage:

  python scripts/training.py \
    --csv data/ml_training/registry_train.csv \
    --out data/ml_training/registry_unlabeled_notes.jsonl \
    --weak-classes bronchial_wash therapeutic_aspiration rigid_bronchoscopy peripheral_ablation \
    --limit 500
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import pandas as pd


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--csv",
        type=Path,
        default=Path("data/ml_training/registry_train.csv"),
        help="Input training CSV containing note_text and label columns",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("data/ml_training/registry_unlabeled_notes.jsonl"),
        help="Output JSONL file for Prodigy batch prep",
    )
    p.add_argument(
        "--text-key",
        choices=["note_text", "text"],
        default="note_text",
        help="Key to write in JSONL (Prodigy prep accepts note_text or text)",
    )
    p.add_argument(
        "--weak-classes",
        nargs="*",
        default=[
            "bronchial_wash",
            "therapeutic_aspiration",
            "rigid_bronchoscopy",
            "peripheral_ablation",
        ],
        help="If provided, select rows where any of these labels are positive",
    )
    p.add_argument(
        "--min-positives",
        type=int,
        default=1,
        help="Minimum number of positive weak classes required for selection (default: 1)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of notes to write (0 = no limit)",
    )
    p.add_argument("--seed", type=int, default=42, help="Random seed for sampling/shuffle")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")

    df = pd.read_csv(args.csv)
    if "note_text" not in df.columns:
        raise SystemExit(f"CSV missing required column 'note_text': {args.csv}")

    weak = [c for c in (args.weak_classes or []) if c]
    if weak:
        missing = [c for c in weak if c not in df.columns]
        if missing:
            raise SystemExit(f"CSV missing weak class columns: {missing}")
        positives = df[weak].fillna(0).astype(int).sum(axis=1)
        target_df = df[positives >= int(args.min_positives)].copy()
    else:
        target_df = df.copy()

    # Shuffle to avoid ordering artifacts.
    rng = random.Random(int(args.seed))
    indices = list(target_df.index)
    rng.shuffle(indices)
    target_df = target_df.loc[indices]

    if args.limit and int(args.limit) > 0:
        target_df = target_df.head(int(args.limit))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0
    with args.out.open("w", encoding="utf-8") as f:
        for text in target_df["note_text"].fillna("").astype(str):
            text = text.strip()
            if not text:
                continue
            f.write(json.dumps({args.text_key: text}, ensure_ascii=False) + "\n")
            n_written += 1

    if weak:
        print(f"Wrote {n_written} notes targeting weak classes: {weak}")
    else:
        print(f"Wrote {n_written} notes (no weak-class filter)")
    print(f"Output: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
