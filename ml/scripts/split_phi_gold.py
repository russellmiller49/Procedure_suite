#!/usr/bin/env python3
"""
Split Gold Standard PHI data into train/test sets with proper encounter grouping.

CRITICAL: Groups by id_base (note-level) before splitting to prevent data leakage.
If Note A has Window 1 and Window 2, both go to the same split.

Usage:
    python scripts/split_phi_gold.py \
        --input data/ml_training/phi_gold_standard_v1.jsonl \
        --train-out data/ml_training/phi_train_gold.jsonl \
        --test-out data/ml_training/phi_test_gold.jsonl \
        --seed 42
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_INPUT = Path("data/ml_training/phi_gold_standard_v1.jsonl")
DEFAULT_TRAIN = Path("data/ml_training/phi_train_gold.jsonl")
DEFAULT_TEST = Path("data/ml_training/phi_test_gold.jsonl")
DEFAULT_SPLIT = 0.8
DEFAULT_SEED = 42


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input gold JSONL file")
    parser.add_argument("--train-out", type=Path, default=DEFAULT_TRAIN, help="Output train JSONL file")
    parser.add_argument("--test-out", type=Path, default=DEFAULT_TEST, help="Output test JSONL file")
    parser.add_argument("--split", type=float, default=DEFAULT_SPLIT, help="Train split ratio (default: 0.8)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed for reproducibility")
    return parser.parse_args(argv)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load records from JSONL file."""
    records = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(records: List[Dict[str, Any]], path: Path) -> None:
    """Save records to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")


def split_by_note(
    records: List[Dict[str, Any]],
    train_ratio: float,
    seed: int,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Split records by note (id_base) to prevent data leakage.

    All windows from the same note stay together in the same split.
    """
    # Group records by id_base (note-level grouping)
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        id_base = record.get("id_base", record.get("id", "unknown"))
        groups[id_base].append(record)

    logger.info(f"Found {len(groups)} unique notes from {len(records)} windows")

    # Shuffle group keys (note IDs)
    group_keys = list(groups.keys())
    random.seed(seed)
    random.shuffle(group_keys)

    # Split at the specified ratio
    split_idx = int(len(group_keys) * train_ratio)
    train_keys = group_keys[:split_idx]
    test_keys = group_keys[split_idx:]

    # Flatten back to records
    train_records = [r for k in train_keys for r in groups[k]]
    test_records = [r for k in test_keys for r in groups[k]]

    return train_records, test_records


def count_labels(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count label distribution in records."""
    label_counts: Dict[str, int] = {}
    for rec in records:
        for tag in rec.get("ner_tags", []):
            if tag != "O":
                label_counts[tag] = label_counts.get(tag, 0) + 1
    return label_counts


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    # Load input data
    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        return 1

    records = load_jsonl(args.input)
    logger.info(f"Loaded {len(records)} records from {args.input}")

    if not records:
        logger.error("No records to split")
        return 1

    # Split by note (encounter-level grouping)
    train_records, test_records = split_by_note(records, args.split, args.seed)

    # Log split statistics
    train_notes = len(set(r.get("id_base", "") for r in train_records))
    test_notes = len(set(r.get("id_base", "") for r in test_records))

    logger.info(f"Train: {len(train_records)} windows from {train_notes} notes")
    logger.info(f"Test:  {len(test_records)} windows from {test_notes} notes")
    logger.info(f"Split ratio: {train_notes}/{train_notes + test_notes} = {train_notes / (train_notes + test_notes):.2%}")

    # Log label distributions
    train_labels = count_labels(train_records)
    test_labels = count_labels(test_records)
    logger.info(f"Train labels: {train_labels}")
    logger.info(f"Test labels:  {test_labels}")

    # Save outputs
    save_jsonl(train_records, args.train_out)
    save_jsonl(test_records, args.test_out)

    logger.info(f"Wrote train set to {args.train_out}")
    logger.info(f"Wrote test set to {args.test_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
