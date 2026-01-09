#!/usr/bin/env python3
"""Merge/override relabeled registry human annotations into a base human CSV.

Use case:
- You exported a big "base" human CSV from Prodigy (e.g. registry_human_v1_backup.csv).
- You later re-annotated a subset (e.g. all rigid_bronchoscopy cases) in a *new* Prodigy dataset
  and exported that subset to another CSV.
- You want the subset to **override** the base labels for matching encounter_id rows.

Behavior:
- Matches rows by `encounter_id` (required in both CSVs).
- Overwrites ONLY the canonical registry label columns (REGISTRY_LABELS).
- Adds any missing label columns to the base output (e.g. newly introduced labels).
- Preserves non-label columns from the base row (note_text/source_file/etc) by default.
- Optionally can override `prodigy_dataset`, `label_source`, `label_confidence` from the updates file.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.ml_coder.registry_label_schema import REGISTRY_LABELS, compute_encounter_id
from modules.ml_coder.registry_label_constraints import apply_label_constraints


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-csv", type=Path, required=True, help="Base human labels CSV")
    p.add_argument("--updates-csv", type=Path, required=True, help="Updates (relabel) CSV")
    p.add_argument("--out-csv", type=Path, required=True, help="Output merged CSV")
    p.add_argument(
        "--prefer-updates-meta",
        action="store_true",
        help="Also prefer updates meta columns when present (prodigy_dataset, label_source, label_confidence).",
    )
    return p.parse_args(argv)


def _ensure_cols(df: pd.DataFrame, cols: list[str], default: int = 0) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = default
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Be tolerant of messy headers (Excel exports often pad columns with spaces).
    df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
    return df


def _ensure_encounter_id(df: pd.DataFrame, *, name: str) -> pd.DataFrame:
    """
    Ensure an encounter_id column exists.

    - If missing but note_text exists, compute encounter_id from note_text.
    - If present but empty for some rows, fill those rows from note_text.
    """
    if "encounter_id" not in df.columns:
        if "note_text" not in df.columns:
            raise SystemExit(f"{name} CSV missing required column: encounter_id (and no note_text to compute it)")
        df["encounter_id"] = df["note_text"].fillna("").astype(str).map(lambda t: compute_encounter_id(t.strip()))
        return df

    # Normalize encounter_id values (trim whitespace/CRLF artifacts)
    df["encounter_id"] = df["encounter_id"].fillna("").astype(str).str.strip()

    # Fill missing/blank encounter_id values (best-effort)
    if "note_text" in df.columns:
        mask = df["encounter_id"].isna() | (df["encounter_id"].astype(str).str.strip() == "")
        if mask.any():
            df.loc[mask, "encounter_id"] = (
                df.loc[mask, "note_text"].fillna("").astype(str).map(lambda t: compute_encounter_id(t.strip()))
            )
    return df


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.base_csv.exists():
        raise SystemExit(f"Base CSV not found: {args.base_csv}")
    if not args.updates_csv.exists():
        raise SystemExit(f"Updates CSV not found: {args.updates_csv}")

    base = _normalize_columns(pd.read_csv(args.base_csv))
    updates = _normalize_columns(pd.read_csv(args.updates_csv))

    base = _ensure_encounter_id(base, name="base")
    updates = _ensure_encounter_id(updates, name="updates")

    # Ensure canonical label columns exist in both
    labels = list(REGISTRY_LABELS)
    base = _ensure_cols(base, labels, default=0)
    updates = _ensure_cols(updates, labels, default=0)

    # Deduplicate updates by encounter_id (keep last row)
    updates = updates.drop_duplicates(subset=["encounter_id"], keep="last")

    base_idx = base.set_index("encounter_id", drop=False)
    updates_idx = updates.set_index("encounter_id", drop=False)

    overlap = base_idx.index.intersection(updates_idx.index)
    new_only = updates_idx.index.difference(base_idx.index)

    # Overwrite label columns for overlapping rows
    if len(overlap) > 0:
        base_idx.loc[overlap, labels] = updates_idx.loc[overlap, labels].values

    # Optionally override a few meta fields if present in updates
    if args.prefer_updates_meta:
        for meta_col in ["prodigy_dataset", "label_source", "label_confidence"]:
            if meta_col in updates_idx.columns and meta_col in base_idx.columns:
                if len(overlap) > 0:
                    base_idx.loc[overlap, meta_col] = updates_idx.loc[overlap, meta_col]

    # Append brand-new encounter_ids from updates (common when you annotated a new batch/dataset)
    if len(new_only) > 0:
        # Ensure any updates-only columns exist on base (pandas will align on concat, but
        # we want to preserve them rather than drop them).
        to_append = updates_idx.loc[new_only].copy()
        out_idx = pd.concat([base_idx, to_append], axis=0, ignore_index=False)
    else:
        out_idx = base_idx

    # If any duplicates exist (shouldn't, but be defensive), keep the last occurrence.
    out = out_idx.reset_index(drop=True).drop_duplicates(subset=["encounter_id"], keep="last")

    if "note_text" in out.columns:
        # Apply deterministic constraints post-merge to keep human data normalized.
        if "transbronchial_cryobiopsy" in out.columns and "transbronchial_biopsy" in out.columns:
            out.loc[out["transbronchial_cryobiopsy"].astype(int) == 1, "transbronchial_biopsy"] = 1
        if "bal" in out.columns and "bronchial_wash" in out.columns:
            mask = (out["bal"].astype(int) == 1) & (out["bronchial_wash"].astype(int) == 1)
            for idx in out.index[mask]:
                row = {
                    "note_text": str(out.at[idx, "note_text"] or ""),
                    "bal": int(out.at[idx, "bal"]),
                    "bronchial_wash": int(out.at[idx, "bronchial_wash"]),
                }
                apply_label_constraints(row)
                out.at[idx, "bal"] = int(row["bal"])
                out.at[idx, "bronchial_wash"] = int(row["bronchial_wash"])

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out_csv, index=False)

    print("Merged updates into base by encounter_id.")
    print(f"Base rows: {len(base)}")
    print(f"Updates rows (deduped): {len(updates)}")
    print(f"Overridden rows (existing encounter_id): {len(overlap)}")
    print(f"Appended rows (new encounter_id): {len(new_only)}")
    print(f"Output: {args.out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
