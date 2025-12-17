"""
smart_splitter.py (updated)

Use this if you already generated registry_train_clean.csv / registry_val_clean.csv / registry_test_clean.csv
but your label distribution is drifting (e.g., val is overloaded with navigational/radial EBUS).

This script:
- Loads the existing splits, concatenates them
- Optionally patches unmapped/zero-label rows (if any remain)
- Adds text-based labels for bronchial_wash / photodynamic_therapy
- Redacts CPT leakage + PHI-like tokens from note_text
- Re-splits using multi-label stratified group splitting

By default, it groups by:
  1) group_id (best, if present)
  2) source_file (fallback)
  3) row id (last resort)

Example:
  python smart_splitter_updated.py \
      --data_dir data/ml_training/cleaned_v2 \
      --output_dir data/ml_training/cleaned_v3_balanced \
      --group_col group_id
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple
import re

import numpy as np
import pandas as pd


LABEL_COLS: List[str] = [
    # Bronchoscopy
    "diagnostic_bronchoscopy", "bal", "bronchial_wash", "brushings",
    "endobronchial_biopsy", "transbronchial_biopsy", "transbronchial_cryobiopsy",
    "tbna_conventional", "linear_ebus", "radial_ebus", "navigational_bronchoscopy",
    "therapeutic_aspiration", "foreign_body_removal", "airway_dilation", "airway_stent",
    "thermal_ablation", "cryotherapy", "mechanical_debulking", "brachytherapy_catheter",
    "blvr", "peripheral_ablation", "bronchial_thermoplasty", "whole_lung_lavage",
    "rigid_bronchoscopy", "photodynamic_therapy",
    # Pleural / Thoracic
    "thoracentesis", "chest_tube", "ipc", "medical_thoracoscopy",
    "pleural_biopsy", "pleurodesis", "fibrinolytic_therapy",
]
TEXT_COL = "note_text"


def redact_note_text(text: str) -> str:
    if text is None:
        return ""
    t = str(text).replace("\r", "\n")
    t = re.sub(r"\bMRN\b\s*[:#]?\s*\d{3,}", "[ID]", t, flags=re.I)
    t = re.sub(r"\bDOB\b\s*[:#]?\s*(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},\s+\d{4})", "[DATE]", t, flags=re.I)
    # Remove any stray MRN/DOB tokens that may remain after number scrubbing
    t = re.sub(r"\bMRN\b", "[ID]", t, flags=re.I)
    t = re.sub(r"\bDOB\b", "[DATE]", t, flags=re.I)
    t = re.sub(r"\b(?:\d{1,2}[/-]){2}\d{2,4}\b", "[DATE]", t)
    t = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "[DATE]", t)
    t = re.sub(r"\b\d{1,2}:\d{2}\b", "[TIME]", t)
    t = re.sub(r"\b\d{6,}\b", "[ID]", t)
    t = re.sub(r"\b\d{5}\b", "[CODE]", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def add_text_based_labels(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    tl = out[TEXT_COL].fillna("").astype(str).str.lower()
    wash_mask = tl.str.contains("bronchial wash") | tl.str.contains("bronchial washing") | tl.str.contains("washings")
    out.loc[wash_mask, "bronchial_wash"] = 1
    pdt_mask = tl.str.contains("photodynamic") | tl.str.contains(r"\bpdt\b", regex=True)
    out.loc[pdt_mask, "photodynamic_therapy"] = 1
    return out


def patch_zero_label_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "verified_cpt_codes" not in out.columns:
        return out
    zero_mask = out[LABEL_COLS].sum(axis=1) == 0
    if not zero_mask.any():
        return out

    code_to_labels = {
        "32556": ["chest_tube"],
        "32557": ["chest_tube"],
        "32551": ["chest_tube"],
        "32552": ["ipc"],
        "32550": ["ipc"],
        "32602": ["medical_thoracoscopy", "pleural_biopsy"],
        "32662": ["medical_thoracoscopy"],
        "31640": ["diagnostic_bronchoscopy", "mechanical_debulking"],
        "31641": ["diagnostic_bronchoscopy", "mechanical_debulking"],
        "31634": ["diagnostic_bronchoscopy"],
    }

    for idx in out.index[zero_mask]:
        code = str(out.at[idx, "verified_cpt_codes"]).strip()
        text = str(out.at[idx, TEXT_COL] or "")
        tl = text.lower()

        for lab in code_to_labels.get(code, []):
            if lab in out.columns:
                out.at[idx, lab] = 1

        if code == "31634" and any(k in tl for k in ["chartis", "collateral ventilation", "zephyr", "valve", "lung volume reduction", "emphysema"]):
            out.at[idx, "blvr"] = 1

        if code == "31600":
            # salvage obvious navigation cases; otherwise remain 0 (likely true tracheostomy)
            if any(k in tl for k in ["robotic", "ion ", "ion-", "monarch", "shape-sensing", "navigat"]):
                out.at[idx, "diagnostic_bronchoscopy"] = 1
                out.at[idx, "navigational_bronchoscopy"] = 1

    return out


def stratified_group_split(
    df: pd.DataFrame,
    group_col: str,
    label_cols: List[str],
    fracs: Tuple[float, float, float] = (0.8, 0.1, 0.1),
    seed: int = 42,
    size_weight: float = 5.0,
    label_weight: float = 1.0,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)

    grp = df.groupby(group_col, dropna=False)
    group_ids = grp.size().index.tolist()
    group_size = grp.size().to_dict()
    group_label = grp[label_cols].sum().to_dict(orient="index")

    total_rows = float(len(df))
    total_label = df[label_cols].sum().values.astype(float)
    target_rows = np.array(fracs, dtype=float) * total_rows
    target_label = np.outer(fracs, total_label)

    w = 1.0 / (total_label + 1e-6)
    scores = []
    for gid in group_ids:
        gl = np.array([group_label[gid][c] for c in label_cols], dtype=float)
        scores.append(float((gl * w).sum()))
    order = np.argsort([-s + rng.normal(0, 1e-6) for s in scores])
    ordered = [group_ids[i] for i in order]

    k = 3
    L = len(label_cols)
    split_groups: List[List[str]] = [[] for _ in range(k)]
    split_rows = np.zeros(k)
    split_label = np.zeros((k, L))

    denom = np.where(target_label > 0, target_label, 1.0)

    for gid in ordered:
        g_rows = float(group_size[gid])
        g_label = np.array([group_label[gid][c] for c in label_cols], dtype=float)

        best_s = None
        best_cost = None
        for s in range(k):
            new_rows = split_rows.copy()
            new_rows[s] += g_rows
            new_label = split_label.copy()
            new_label[s] += g_label

            size_cost = (((new_rows - target_rows) / np.maximum(target_rows, 1.0)) ** 2).sum()
            label_cost = (((new_label - target_label) / denom) ** 2).sum()
            cost = size_weight * size_cost + label_weight * label_cost

            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_s = s

        split_groups[best_s].append(gid)
        split_rows[best_s] += g_rows
        split_label[best_s] += g_label

    train_df = df[df[group_col].isin(split_groups[0])].copy()
    val_df = df[df[group_col].isin(split_groups[1])].copy()
    test_df = df[df[group_col].isin(split_groups[2])].copy()

    return train_df, val_df, test_df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", required=True, help="Directory containing registry_train_clean.csv etc.")
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--group_col", default="group_id")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train_frac", type=float, default=0.8)
    ap.add_argument("--val_frac", type=float, default=0.1)
    ap.add_argument("--test_frac", type=float, default=0.1)
    ap.add_argument("--drop_zero_label_rows", action="store_true")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df_list = []
    for split in ["train", "val", "test"]:
        f = data_dir / f"registry_{split}_clean.csv"
        if not f.exists():
            raise FileNotFoundError(f"Missing {f}")
        d = pd.read_csv(f)
        d["_orig_split"] = split
        df_list.append(d)

    df = pd.concat(df_list, ignore_index=True)

    # Ensure labels are clean ints
    for c in LABEL_COLS:
        if c not in df.columns:
            raise ValueError(f"Missing label column: {c}")
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        df[c] = (df[c] > 0).astype(int)

    # choose group col
    group_col = args.group_col
    if group_col not in df.columns:
        if "group_id" in df.columns:
            group_col = "group_id"
        elif "source_file" in df.columns:
            group_col = "source_file"
        else:
            group_col = "__row_id__"
            df[group_col] = np.arange(len(df))

    # Patch + text labels
    df = patch_zero_label_rows(df)
    df = add_text_based_labels(df)

    if args.drop_zero_label_rows:
        before = len(df)
        df = df[df[LABEL_COLS].sum(axis=1) > 0].copy()
        print(f"Dropped {before - len(df)} rows with 0 labels.")

    # Redact leakage/PHI
    df[TEXT_COL] = df[TEXT_COL].apply(redact_note_text)

    # Re-split
    fracs = (args.train_frac, args.val_frac, args.test_frac)
    train_df, val_df, test_df = stratified_group_split(
        df, group_col=group_col, label_cols=LABEL_COLS, fracs=fracs, seed=args.seed
    )

    # Save
    train_df.drop(columns=["_orig_split"], errors="ignore").to_csv(out_dir / "registry_train_clean.csv", index=False)
    val_df.drop(columns=["_orig_split"], errors="ignore").to_csv(out_dir / "registry_val_clean.csv", index=False)
    test_df.drop(columns=["_orig_split"], errors="ignore").to_csv(out_dir / "registry_test_clean.csv", index=False)

    with open(out_dir / "registry_label_fields.json", "w") as f:
        json.dump(LABEL_COLS, f, indent=2)

    print(f"Saved to: {out_dir}")
    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

    prev = pd.DataFrame({
        "train": train_df[LABEL_COLS].mean(),
        "val": val_df[LABEL_COLS].mean(),
        "test": test_df[LABEL_COLS].mean(),
    })
    prev["abs_train_val"] = (prev["train"] - prev["val"]).abs()
    print("\nTop label prevalence drifts (|train - val|):")
    print(prev.sort_values("abs_train_val", ascending=False).head(10).to_string())

if __name__ == "__main__":
    main()