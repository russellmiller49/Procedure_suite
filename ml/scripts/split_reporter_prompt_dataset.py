#!/usr/bin/env python3
"""Split reporter prompt dataset by note family (no leakage)."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path("data/ml_training/reporter_prompt/v1/reporter_prompt_pairs.jsonl")
DEFAULT_OUTPUT_DIR = Path("data/ml_training/reporter_prompt/v1")
DEFAULT_SEED = 42
DEFAULT_TRAIN_RATIO = 0.80
DEFAULT_VAL_RATIO = 0.10
DEFAULT_TEST_RATIO = 0.10


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--train-ratio", type=float, default=DEFAULT_TRAIN_RATIO)
    parser.add_argument("--val-ratio", type=float, default=DEFAULT_VAL_RATIO)
    parser.add_argument("--test-ratio", type=float, default=DEFAULT_TEST_RATIO)
    return parser.parse_args(argv)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _validate_ratios(train_ratio: float, val_ratio: float, test_ratio: float) -> None:
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"Ratios must sum to 1.0; got {total}")


def _split_families(
    families: list[str],
    *,
    seed: int,
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
) -> tuple[set[str], set[str], set[str]]:
    _validate_ratios(train_ratio, val_ratio, test_ratio)
    unique = sorted(set(families))
    rng = random.Random(seed)
    rng.shuffle(unique)

    total = len(unique)
    n_train = int(total * train_ratio)
    n_val = int(total * val_ratio)
    n_test = total - n_train - n_val

    train = set(unique[:n_train])
    val = set(unique[n_train : n_train + n_val])
    test = set(unique[n_train + n_val : n_train + n_val + n_test])
    return train, val, test


def split_rows_by_note_family(
    rows: list[dict[str, Any]],
    *,
    seed: int,
    train_ratio: float,
    val_ratio: float,
    test_ratio: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    families = [str(row.get("note_family") or "unknown") for row in rows]
    train_fam, val_fam, test_fam = _split_families(
        families,
        seed=seed,
        train_ratio=train_ratio,
        val_ratio=val_ratio,
        test_ratio=test_ratio,
    )

    train_rows: list[dict[str, Any]] = []
    val_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    for row in rows:
        fam = str(row.get("note_family") or "unknown")
        if fam in train_fam:
            train_rows.append(row)
        elif fam in val_fam:
            val_rows.append(row)
        elif fam in test_fam:
            test_rows.append(row)
        else:
            test_rows.append(row)

    manifest = {
        "seed": seed,
        "ratios": {
            "train": train_ratio,
            "val": val_ratio,
            "test": test_ratio,
        },
        "families": {
            "train": sorted(train_fam),
            "val": sorted(val_fam),
            "test": sorted(test_fam),
            "counts": {
                "train": len(train_fam),
                "val": len(val_fam),
                "test": len(test_fam),
            },
        },
        "rows": {
            "total": len(rows),
            "train": len(train_rows),
            "val": len(val_rows),
            "test": len(test_rows),
        },
        "contract": "reporter_prompt_pairs.v1",
    }

    # Hard leakage assertion.
    if train_fam & val_fam or train_fam & test_fam or val_fam & test_fam:
        raise AssertionError("Note-family leakage detected between splits")

    return train_rows, val_rows, test_rows, manifest


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.exists():
        raise FileNotFoundError(f"Input JSONL not found: {args.input}")

    rows = load_jsonl(args.input)
    if not rows:
        raise RuntimeError(f"No rows in input JSONL: {args.input}")

    train_rows, val_rows, test_rows, manifest = split_rows_by_note_family(
        rows,
        seed=args.seed,
        train_ratio=float(args.train_ratio),
        val_ratio=float(args.val_ratio),
        test_ratio=float(args.test_ratio),
    )

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    train_path = output_dir / "reporter_prompt_train.jsonl"
    val_path = output_dir / "reporter_prompt_val.jsonl"
    test_path = output_dir / "reporter_prompt_test.jsonl"
    manifest_path = output_dir / "reporter_prompt_split_manifest.json"

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
