#!/usr/bin/env python3
"""Merge Prodigy-labeled registry procedure flags into the existing train split.

Rules:
- Hard guard: refuse to merge any Prodigy example whose note_text appears in val/test.
- Deduplicate by note_text, preferring Prodigy labels when duplicates exist.
- Ensure output contains all 29 canonical label columns (missing columns filled with 0).
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.registry.label_fields import load_registry_procedure_labels

logger = logging.getLogger(__name__)


DEFAULT_LABEL_FIELDS = Path("data/ml_training/registry_label_fields.json")


def _normalize_text(text: str) -> str:
    return (text or "").strip()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(_normalize_text(text).encode("utf-8")).hexdigest()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-train-csv",
        type=Path,
        default=Path("data/ml_training/registry_train.csv"),
        help="Base training CSV to augment",
    )
    parser.add_argument(
        "--val-csv",
        type=Path,
        default=Path("data/ml_training/registry_val.csv"),
        help="Validation CSV (leakage guard)",
    )
    parser.add_argument(
        "--test-csv",
        type=Path,
        default=Path("data/ml_training/registry_test.csv"),
        help="Test CSV (leakage guard)",
    )
    parser.add_argument(
        "--prodigy-csv",
        type=Path,
        default=Path("data/ml_training/registry_prodigy_labels.csv"),
        help="Prodigy-labeled CSV to merge in",
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("data/ml_training/registry_train_augmented.csv"),
        help="Output augmented train CSV",
    )
    parser.add_argument(
        "--label-fields",
        type=Path,
        default=DEFAULT_LABEL_FIELDS,
        help="JSON list of canonical registry labels",
    )
    return parser.parse_args(argv)


def _require_note_text(df, path: Path) -> None:
    if "note_text" not in df.columns:
        raise ValueError(f"Missing required column 'note_text' in {path}")


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args(argv)

    labels = load_registry_procedure_labels(args.label_fields)
    if len(labels) != 29:
        raise ValueError(f"Expected 29 registry labels, got {len(labels)}")

    import pandas as pd

    train_df = pd.read_csv(args.base_train_csv)
    val_df = pd.read_csv(args.val_csv)
    test_df = pd.read_csv(args.test_csv)
    prodigy_df = pd.read_csv(args.prodigy_csv)

    _require_note_text(train_df, args.base_train_csv)
    _require_note_text(val_df, args.val_csv)
    _require_note_text(test_df, args.test_csv)
    _require_note_text(prodigy_df, args.prodigy_csv)

    val_test_hashes = set(_sha256_text(t) for t in val_df["note_text"].fillna("").astype(str).tolist())
    val_test_hashes |= set(_sha256_text(t) for t in test_df["note_text"].fillna("").astype(str).tolist())

    prodigy_hashes = [_sha256_text(t) for t in prodigy_df["note_text"].fillna("").astype(str).tolist()]
    leaked = [h for h in prodigy_hashes if h in val_test_hashes]
    if leaked:
        raise SystemExit(
            f"Refusing to merge: {len(leaked)} Prodigy examples appear in val/test splits."
        )

    # Ensure label columns exist (fill missing with 0).
    for df in (train_df, prodigy_df):
        for label in labels:
            if label not in df.columns:
                df[label] = 0
            df[label] = pd.to_numeric(df[label], errors="coerce").fillna(0).clip(0, 1).astype(int)

    # Ensure required metadata columns exist.
    for df, source in ((train_df, "base"), (prodigy_df, "prodigy")):
        if "label_source" not in df.columns:
            df["label_source"] = source
        if "label_confidence" not in df.columns:
            df["label_confidence"] = 1.0

    # Prefer Prodigy rows when note_text duplicates exist.
    prodigy_df["_priority"] = 1
    train_df["_priority"] = 0

    combined = pd.concat([prodigy_df, train_df], ignore_index=True)
    combined["_note_hash"] = combined["note_text"].fillna("").astype(str).map(_sha256_text)

    combined.sort_values(by=["_priority"], ascending=False, inplace=True)
    merged = combined.drop_duplicates(subset=["_note_hash"], keep="first").drop(columns=["_priority", "_note_hash"])

    # Stable column order: base cols first (plus any prodigy-only cols), then labels.
    base_cols = [c for c in train_df.columns if c not in labels and c not in {"_priority"}]
    for c in prodigy_df.columns:
        if c in {"_priority"}:
            continue
        if c not in base_cols and c not in labels:
            base_cols.append(c)
    out_cols = [c for c in base_cols if c in merged.columns] + [c for c in labels if c in merged.columns]
    merged = merged.reindex(columns=out_cols)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.out_csv, index=False)
    logger.info("Wrote %d rows to %s", len(merged), args.out_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

