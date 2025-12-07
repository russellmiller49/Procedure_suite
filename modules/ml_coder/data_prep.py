"""
Data preparation module for ML coder training.

Builds clean training CSVs from golden JSONs with iterative multi-label
stratification and encounter-level leakage checks.
"""

import glob
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from skmultilearn.model_selection import iterative_train_test_split

GOLDEN_DIR = Path("data/knowledge/golden_extractions")

EDGE_SOURCE_NAME = "synthetic_edge_case_notes_with_registry.jsonl"

# Registry procedure fields for ML prediction
PROCEDURE_FIELDS = [
    "diagnostic_bronchoscopy",
    "bal",
    "bronchial_wash",
    "brushings",
    "endobronchial_biopsy",
    "tbna_conventional",
    "linear_ebus",
    "radial_ebus",
    "navigational_bronchoscopy",
    "transbronchial_biopsy",
    "transbronchial_cryobiopsy",
    "therapeutic_aspiration",
    "foreign_body_removal",
    "airway_dilation",
    "airway_stent",
    "thermal_ablation",
    "cryotherapy",
    "blvr",
    "peripheral_ablation",
    "bronchial_thermoplasty",
    "whole_lung_lavage",
    "rigid_bronchoscopy",
]

PLEURAL_FIELDS = [
    "thoracentesis",
    "chest_tube",
    "ipc",
    "medical_thoracoscopy",
    "pleurodesis",
    "pleural_biopsy",
    "fibrinolytic_therapy",
]

# Valid IP pulmonology CPT codes
VALID_IP_CODES = {
    # Bronchoscopy codes (316xx)
    "31622", "31623", "31624", "31625", "31626", "31627", "31628", "31629",
    "31631", "31632", "31633", "31634", "31636", "31637", "31638",
    "31640", "31641", "31645", "31646", "31647",
    "31652", "31653", "31654", "31660", "31661",
    # Pleural/thoracic codes (325xx, 326xx)
    "32550", "32551", "32552", "32554", "32555", "32556", "32557", "32560", "32561",
    "32601", "32604", "32606", "32607", "32608", "32609", "32650",
    # Special procedures
    "32997",  # Total lung lavage
}

# Known typos/errors and their corrections
CODE_CORRECTIONS = {
    "31635": "31636",  # Typo -> bronchial stent
    "31630": "31631",  # Typo -> tracheal stent
    "31651": "31652",  # Typo -> EBUS 1-2 stations
    "31648": "31647",  # Typo -> catheter balloon
    "32408": "32608",  # Typo -> thoracoscopy wedge
}

# Codes to completely exclude (wrong domain)
EXCLUDED_CODES = {
    "31600",  # Tracheostomy - not IP bronch
    "33015",  # Pericardiocentesis - cardiac
}


def _clean_code(code: str) -> str | None:
    """
    Clean and validate a single CPT code.

    Returns:
        Cleaned code string, or None if code should be excluded
    """
    # Strip add-on prefix
    code = code.lstrip("+")

    # Apply known corrections
    if code in CODE_CORRECTIONS:
        return CODE_CORRECTIONS[code]

    # Exclude invalid domain codes
    if code in EXCLUDED_CODES:
        return None

    # Validate format and domain
    if code in VALID_IP_CODES:
        return code

    # Unknown code - exclude
    return None


def _clean_codes(codes: List[str]) -> List[str]:
    """Clean and validate a list of CPT codes."""
    cleaned = []
    for code in codes:
        clean = _clean_code(code)
        if clean:
            cleaned.append(clean)
    return cleaned


def _iter_golden_files() -> List[Path]:
    """Iterate over golden extraction JSON files."""
    pattern = str(GOLDEN_DIR / "consolidated_verified_notes_v2_8_part_*.json")
    return [Path(p) for p in glob.glob(pattern)]


def _extract_codes(entry: Dict[str, Any]) -> List[str]:
    """
    Extract CPT codes from an entry.

    Priority order:
    1. coding_review.final_cpt_codes (array)
    2. coding_review.cpt_summary.final_codes (array)
    3. coding_review.cpt_summary keys (if dict keyed by code)
    4. coding_review.cpt_summary[].code (if list of objects)
    5. cpt_codes (top-level fallback)
    """
    cr = entry.get("coding_review", {})
    if not isinstance(cr, dict):
        cr = {}

    # Try coding_review.final_cpt_codes first
    final_cpt = cr.get("final_cpt_codes")
    if final_cpt and isinstance(final_cpt, list):
        return [str(c) for c in final_cpt]

    # Try coding_review.cpt_summary
    summary = cr.get("cpt_summary")

    if isinstance(summary, dict):
        # Could be {"final_codes": [...]} or {"31653": {...}, "31628": {...}}
        final = summary.get("final_codes")
        if final and isinstance(final, list):
            return [str(c) for c in final]
        # Keys are the codes themselves
        codes = [k for k in summary.keys() if k.isdigit() or (k.startswith("3") and len(k) == 5)]
        if codes:
            return codes

    elif isinstance(summary, list):
        # List of objects like [{"code": "31653", ...}, ...]
        codes = []
        for item in summary:
            if isinstance(item, dict) and "code" in item:
                codes.append(str(item["code"]))
        if codes:
            return codes

    # Fallback to top-level cpt_codes
    raw = entry.get("cpt_codes", [])
    return [str(c) for c in raw]


def _build_dataframe() -> pd.DataFrame:
    """Build a DataFrame from all golden extraction files."""
    rows = []
    for file_path in _iter_golden_files():
        with open(file_path, "r") as f:
            data = json.load(f)

        for entry in data:
            text = entry.get("note_text", "")
            codes = _clean_codes(_extract_codes(entry))
            source_file = entry.get("source_file", "")
            registry = entry.get("registry_entry") or {}
            mrn = registry.get("patient_mrn")
            date = registry.get("procedure_date")

            if not text or not codes:
                continue

            rows.append(
                {
                    "note_text": text,
                    "verified_cpt_codes": ",".join(sorted(set(codes))),
                    "source_file": source_file,
                    "patient_mrn": mrn,
                    "procedure_date": date,
                    "is_edge_case": (source_file == EDGE_SOURCE_NAME),
                }
            )

    df = pd.DataFrame(rows)
    return df


def _build_label_matrix(df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
    """Build multi-hot encoding matrix of verified_cpt_codes."""
    all_codes = sorted({c for csv in df["verified_cpt_codes"] for c in csv.split(",")})
    code_index = {c: i for i, c in enumerate(all_codes)}
    y = np.zeros((len(df), len(all_codes)), dtype=int)

    for i, csv in enumerate(df["verified_cpt_codes"]):
        for c in csv.split(","):
            y[i, code_index[c]] = 1

    return y, all_codes


def _enforce_encounter_grouping(
    df: pd.DataFrame,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Ensure that any repeated encounter (MRN+date combo) does not leak across splits.

    If an encounter appears in both train and test, all its rows are moved to
    whichever split contains the majority of them.
    """
    df = df.reset_index(drop=True)
    train_set = set(train_idx.flatten().tolist())
    test_set = set(test_idx.flatten().tolist())

    enc_to_rows: Dict[Tuple[Any, Any], List[int]] = defaultdict(list)
    for i, row in df.iterrows():
        enc = (row.get("patient_mrn"), row.get("procedure_date"))
        enc_to_rows[enc].append(i)

    for enc, rows in enc_to_rows.items():
        in_train = any(r in train_set for r in rows)
        in_test = any(r in test_set for r in rows)
        if in_train and in_test:
            # Move all encounter rows into the split where most of them are
            train_count = sum(r in train_set for r in rows)
            test_count = sum(r in test_set for r in rows)
            if train_count >= test_count:
                for r in rows:
                    test_set.discard(r)
                    train_set.add(r)
            else:
                for r in rows:
                    train_set.discard(r)
                    test_set.add(r)

    train_idx = np.array(sorted(train_set)).reshape(-1, 1)
    test_idx = np.array(sorted(test_set)).reshape(-1, 1)
    return train_idx, test_idx


def stratified_split(
    df: pd.DataFrame, test_size: float = 0.2
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Perform iterative multi-label stratified split with encounter leakage prevention.

    Returns:
        train_idx: Array of training set indices
        test_idx: Array of test set indices
        all_codes: List of all CPT codes in the dataset
    """
    y, all_codes = _build_label_matrix(df)
    X_indices = np.arange(len(df)).reshape(-1, 1)

    X_train, y_train, X_test, y_test = iterative_train_test_split(
        X_indices, y, test_size=test_size
    )

    X_train, X_test = _enforce_encounter_grouping(df, X_train, X_test)
    return X_train.flatten(), X_test.flatten(), all_codes


def prepare_training_and_eval_splits(
    output_dir: Path = Path("data/ml_training"),
    test_size: float = 0.2,
) -> None:
    """
    Build train/test/edge_case CSV splits from golden extraction data.

    Args:
        output_dir: Directory to write output CSVs
        test_size: Fraction of data to use for test set (default 0.2)

    Outputs:
        - train.csv: Training set
        - test.csv: Test/validation set
        - edge_cases_holdout.csv: Edge cases held out for special evaluation
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    df = _build_dataframe()

    # Separate edge cases for special eval
    df_main = df[~df["is_edge_case"]].reset_index(drop=True)
    df_edge = df[df["is_edge_case"]].reset_index(drop=True)

    train_idx, test_idx, all_codes = stratified_split(df_main, test_size=test_size)

    train_df = df_main.iloc[train_idx]
    test_df = df_main.iloc[test_idx]

    train_df.to_csv(output_dir / "train.csv", index=False)
    test_df.to_csv(output_dir / "test.csv", index=False)
    df_edge.to_csv(output_dir / "edge_cases_holdout.csv", index=False)

    print(f"Train samples: {len(train_df)}")
    print(f"Test samples: {len(test_df)}")
    print(f"Edge case holdout samples: {len(df_edge)}")
    print(f"Total codes: {len(all_codes)}")
    print(f"Output written to: {output_dir}")


if __name__ == "__main__":
    prepare_training_and_eval_splits()
