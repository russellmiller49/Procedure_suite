#!/usr/bin/env python3
"""Split accepted reporter gold dataset at patient level (80/10/10 by default)."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/ml_training/reporter_golden/v1/reporter_gold_accepted.jsonl")
DEFAULT_OUTPUT_DIR = Path("data/ml_training/reporter_golden/v1")
DEFAULT_SEED = 42
DEFAULT_TRAIN_RATIO = 0.80
DEFAULT_VAL_RATIO = 0.10
DEFAULT_TEST_RATIO = 0.10


@dataclass(frozen=True)
class SplitCounts:
    train_patients: int
    val_patients: int
    test_patients: int


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Accepted reporter gold JSONL.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for split JSONLs and manifest.",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed.")
    parser.add_argument("--train-ratio", type=float, default=DEFAULT_TRAIN_RATIO, help="Train ratio.")
    parser.add_argument("--val-ratio", type=float, default=DEFAULT_VAL_RATIO, help="Validation ratio.")
    parser.add_argument("--test-ratio", type=float, default=DEFAULT_TEST_RATIO, help="Test ratio.")
    return parser.parse_args(argv)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _ensure_valid_ratios(train_ratio: float, val_ratio: float, test_ratio: float) -> None:
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-9:
        raise ValueError(
            f"train+val+test ratios must sum to 1.0; got {train_ratio}+{val_ratio}+{test_ratio}={total}"
        )


def split_patient_ids(
    patient_ids: list[str],
    *,
    seed: int,
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
) -> tuple[set[str], set[str], set[str], SplitCounts]:
    _ensure_valid_ratios(train_ratio, val_ratio, test_ratio)

    ids = sorted(set(patient_ids))
    if not ids:
        return set(), set(), set(), SplitCounts(0, 0, 0)

    rng = random.Random(seed)
    rng.shuffle(ids)

    total = len(ids)
    n_train = int(total * train_ratio)
    n_val = int(total * val_ratio)
    # assign remainder to test to preserve exact total
    n_test = total - n_train - n_val

    train_ids = set(ids[:n_train])
    val_ids = set(ids[n_train : n_train + n_val])
    test_ids = set(ids[n_train + n_val : n_train + n_val + n_test])

    counts = SplitCounts(
        train_patients=len(train_ids),
        val_patients=len(val_ids),
        test_patients=len(test_ids),
    )
    return train_ids, val_ids, test_ids, counts


def split_records_by_patient(
    rows: list[dict[str, Any]],
    *,
    seed: int,
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    patient_ids = [str(row.get("patient_base_id") or "") for row in rows]
    train_ids, val_ids, test_ids, counts = split_patient_ids(
        patient_ids,
        seed=seed,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
    )

    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    for row in rows:
        pid = str(row.get("patient_base_id") or "")
        if pid in train_ids:
            train_rows.append(row)
        elif pid in val_ids:
            val_rows.append(row)
        elif pid in test_ids:
            test_rows.append(row)
        else:
            # If patient id is empty/missing, deterministic fallback to test split.
            test_rows.append(row)

    manifest = {
        "seed": seed,
        "ratios": {
            "train": train_ratio,
            "val": val_ratio,
            "test": test_ratio,
        },
        "patients": {
            "train": sorted(train_ids),
            "val": sorted(val_ids),
            "test": sorted(test_ids),
            "counts": {
                "train": counts.train_patients,
                "val": counts.val_patients,
                "test": counts.test_patients,
            },
        },
        "rows": {
            "total": len(rows),
            "train": len(train_rows),
            "val": len(val_rows),
            "test": len(test_rows),
        },
    }
    return train_rows, val_rows, test_rows, manifest


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.input.exists():
        raise FileNotFoundError(f"Input JSONL not found: {args.input}")

    rows = load_jsonl(args.input)
    if not rows:
        raise RuntimeError(f"No rows found in input: {args.input}")

    train_rows, val_rows, test_rows, manifest = split_records_by_patient(
        rows,
        seed=args.seed,
        train_ratio=float(args.train_ratio),
        val_ratio=float(args.val_ratio),
        test_ratio=float(args.test_ratio),
    )

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    train_path = output_dir / "reporter_gold_train.jsonl"
    val_path = output_dir / "reporter_gold_val.jsonl"
    test_path = output_dir / "reporter_gold_test.jsonl"
    manifest_path = output_dir / "reporter_gold_split_manifest.json"

    write_jsonl(train_path, train_rows)
    write_jsonl(val_path, val_rows)
    write_jsonl(test_path, test_rows)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Wrote train: {train_path}")
    print(f"Wrote val:   {val_path}")
    print(f"Wrote test:  {test_path}")
    print(f"Wrote split manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

