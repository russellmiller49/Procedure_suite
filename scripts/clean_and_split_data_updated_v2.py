"""
clean_and_split_data.py (updated)

Fixes implemented:
1) Removes label drift by using *case-level stratified group splitting* (multi-label).
2) Fixes 0-label rows from unmapped CPT codes.
3) Redacts CPT-code leakage + PHI-like tokens.
4) Adds text-based labels for bronchial_wash / photodynamic_therapy.
5) CRITICAL: Enforces CSV quoting (QUOTE_NONNUMERIC) to prevent type inference errors.
6) CRITICAL: Applies safety patch for known label errors (Christopher Hayes) if missed upstream.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import csv  # <--- Added for QUOTE_NONNUMERIC
from pathlib import Path
from typing import Dict, List, Tuple

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

META_CANDIDATES = ["verified_cpt_codes", "group_id", "source_file", "style_type", "original_index"]
TEXT_COL = "note_text"


# ----------------------------
# Text redaction
# ----------------------------

def redact_note_text(text: str) -> str:
    """
    Redacts tokens that behave like PHI or create label leakage.
    """
    if text is None or pd.isna(text):
        return ""

    t = str(text).replace("\r", "\n")

    # PHI-like IDs
    t = re.sub(
        r"\b(?:MRN|Medical\s+Record\s+Number|Medical\s+Record\s*#|Record\s+Number|Patient\s+ID|Case\s+ID)\b\s*[:#]?\s*\S+",
        "[ID]",
        t,
        flags=re.I,
    )

    # DOB + variants
    t = re.sub(
        r"\b(?:DOB|Date\s+of\s+Birth)\b\s*[:#]?\s*(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2},\s+\d{4}|\S+)",
        "[DATE]",
        t,
        flags=re.I,
    )

    # Dates / times
    t = re.sub(r"\b(?:\d{1,2}[/-]){2}\d{2,4}\b", "[DATE]", t)
    t = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "[DATE]", t)
    t = re.sub(r"\b\d{1,2}:\d{2}\b", "[TIME]", t)

    # Long numeric IDs
    t = re.sub(r"\b\d{6,}\b", "[ID]", t)

    # 5-digit sequences (CPT codes / short IDs)
    t = re.sub(r"\b\d{5}\b", "[CODE]", t)

    # Remove billing/coding sections (post-redaction)
    cleaned_lines = []
    for line in t.splitlines():
        ln = line.strip()
        if not ln:
            cleaned_lines.append(line)
            continue

        if "[CODE]" in line:
            continue
        if re.search(r"(?i)\b(billing|billable|billed|cpt|icd|icd-?10)\b", line):
            continue
        if re.search(r"(?i)\bcodes?\s*:", line):
            continue
        if re.search(r"(?i)medical\s+record\s+number|date\s+of\s+birth", line):
            continue

        cleaned_lines.append(line)

    t = "\n".join(cleaned_lines)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


# ----------------------------
# Label patching helpers
# ----------------------------

def add_text_based_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Adds missing positive labels when strongly implied by the narrative."""
    out = df.copy()
    tl = out[TEXT_COL].fillna("").astype(str).str.lower()

    # bronchial wash
    wash_mask = tl.str.contains("bronchial wash") | tl.str.contains("bronchial washing") | tl.str.contains("washings")
    out.loc[wash_mask, "bronchial_wash"] = 1

    # photodynamic therapy
    pdt_mask = tl.str.contains("photodynamic") | tl.str.contains(r"\bpdt\b", regex=True)
    out.loc[pdt_mask, "photodynamic_therapy"] = 1

    return out

def patch_zero_label_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Fills in labels for rows where all labels are 0."""
    out = df.copy()
    label_sum = out[LABEL_COLS].sum(axis=1)
    zero_idx = out.index[label_sum == 0].tolist()
    if not zero_idx:
        return out

    CODE_TO_LABELS: Dict[str, List[str]] = {
        "32556": ["chest_tube"], "32557": ["chest_tube"], "32551": ["chest_tube"],
        "32552": ["ipc"], "32550": ["ipc"],
        "32602": ["medical_thoracoscopy", "pleural_biopsy"],
        "32662": ["medical_thoracoscopy"],
        "31640": ["diagnostic_bronchoscopy", "mechanical_debulking"],
        "31641": ["diagnostic_bronchoscopy", "mechanical_debulking"],
        "31634": ["diagnostic_bronchoscopy"],
    }

    for idx in zero_idx:
        code = str(out.at[idx, "verified_cpt_codes"] if "verified_cpt_codes" in out.columns else "").strip()
        text = str(out.at[idx, TEXT_COL] or "")
        tl = text.lower()

        for lab in CODE_TO_LABELS.get(code, []):
            if lab in out.columns: out.at[idx, lab] = 1

        if code == "31634":
            if any(k in tl for k in ["chartis", "collateral ventilation", "zephyr", "valve", "lung volume reduction", "emphysema"]):
                out.at[idx, "blvr"] = 1

        if code == "31600":
            if any(k in tl for k in ["robotic", "ion ", "ion-", "monarch", "shape-sensing", "navigat"]):
                out.at[idx, "diagnostic_bronchoscopy"] = 1; out.at[idx, "navigational_bronchoscopy"] = 1
            if any(k in tl for k in ["radial ebus", "rebus", "radial endobronchial ultrasound"]):
                out.at[idx, "radial_ebus"] = 1; out.at[idx, "diagnostic_bronchoscopy"] = 1
            if "tbna" in tl:
                out.at[idx, "tbna_conventional"] = 1; out.at[idx, "diagnostic_bronchoscopy"] = 1
            if any(k in tl for k in ["cryobiopsy", "cryo biopsy"]):
                out.at[idx, "transbronchial_cryobiopsy"] = 1; out.at[idx, "diagnostic_bronchoscopy"] = 1
            if any(k in tl for k in ["transbronchial biopsy", "tbbx"]):
                out.at[idx, "transbronchial_biopsy"] = 1; out.at[idx, "diagnostic_bronchoscopy"] = 1
            if any(k in tl for k in ["brush", "brushing"]):
                out.at[idx, "brushings"] = 1; out.at[idx, "diagnostic_bronchoscopy"] = 1
            if "bal" in tl or "bronchoalveolar lavage" in tl:
                out.at[idx, "bal"] = 1; out.at[idx, "diagnostic_bronchoscopy"] = 1
    return out


# ----------------------------
# Stratified group splitting
# ----------------------------

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


# ----------------------------
# Main
# ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_csv", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--group_col", default="group_id")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train_frac", type=float, default=0.8)
    ap.add_argument("--val_frac", type=float, default=0.1)
    ap.add_argument("--test_frac", type=float, default=0.1)
    ap.add_argument("--drop_zero_label_rows", action="store_true")
    args = ap.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. LOAD WITH EXPLICIT TYPES (Fixes Mixed Types Issue)
    df = pd.read_csv(args.input_csv, dtype={'verified_cpt_codes': str})

    if "source_file" in df.columns and "original_index" in df.columns:
        # 2. SAFETY PATCH (Fixes Labeling Error if upstream missed it)
        # Christopher Hayes: golden_034.json, index 4.0 -> navigational_bronchoscopy should be 0
        patch_mask = (df["source_file"] == "golden_034.json") & (df["original_index"] == 4.0)
        if patch_mask.any():
            print(f"Applying safety patch: Setting navigational_bronchoscopy=0 for {patch_mask.sum()} row(s).")
            df.loc[patch_mask, "navigational_bronchoscopy"] = 0

    missing = [c for c in [TEXT_COL] + LABEL_COLS if c not in df.columns]
    if missing: raise ValueError(f"Input CSV missing: {missing}")

    for c in LABEL_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        df[c] = (df[c] > 0).astype(int)

    df = df[df[TEXT_COL].notna()].copy()
    df[TEXT_COL] = df[TEXT_COL].astype(str)
    df = df[df[TEXT_COL].str.strip().ne("")].copy()
    df = df[df[TEXT_COL].str.lower().ne("nan")].copy()

    group_col = args.group_col
    if group_col not in df.columns:
        if "group_id" in df.columns: group_col = "group_id"
        elif "patient_id" in df.columns: group_col = "patient_id"
        elif "source_file" in df.columns: group_col = "source_file"
        else:
            group_col = "__row_id__"
            df[group_col] = np.arange(len(df))

    df = patch_zero_label_rows(df)
    df = add_text_based_labels(df)

    if args.drop_zero_label_rows:
        df = df[df[LABEL_COLS].sum(axis=1) > 0].copy()

    df[TEXT_COL] = df[TEXT_COL].apply(redact_note_text)
    df = df[df[TEXT_COL].str.strip().ne("")].copy()

    # Ensure CPT codes are clean strings before saving
    if "verified_cpt_codes" in df.columns:
        df["verified_cpt_codes"] = df["verified_cpt_codes"].fillna("").astype(str)
        df["verified_cpt_codes"] = df["verified_cpt_codes"].apply(
            lambda x: x.replace(".0", "") if x.endswith(".0") and "," not in x else x
        )

    fracs = (args.train_frac, args.val_frac, args.test_frac)
    train_df, val_df, test_df = stratified_group_split(
        df, group_col=group_col, label_cols=LABEL_COLS, fracs=fracs, seed=args.seed
    )

    # 3. SAVE WITH QUOTING ENFORCED (Fixes "Unquoted Text" & "Truncated CSV" issues)
    # csv.QUOTE_NONNUMERIC wraps all non-number fields (like text and CPT lists) in quotes.
    train_df.to_csv(output_dir / "registry_train_clean.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
    val_df.to_csv(output_dir / "registry_val_clean.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)
    test_df.to_csv(output_dir / "registry_test_clean.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)

    with open(output_dir / "registry_label_fields.json", "w") as f:
        json.dump(LABEL_COLS, f, indent=2)

    print(f"Saved splits to: {output_dir}")
    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

if __name__ == "__main__":
    main()