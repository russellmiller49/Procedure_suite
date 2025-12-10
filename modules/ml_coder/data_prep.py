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

# Old/low-quality source files to exclude (embedded provenance metadata)
# Only entries with empty source_file or source_file starting with "(from " are kept
EXCLUDED_SOURCE_PREFIXES = {
    "synthetic_notes_with_registry",  # Old v1 data
    "synthetic_notes_with_CPT",       # Old CSV-based data
    "synthetic_CPT_corrected",        # Old corrected data
    "recovered_metadata",             # Recovery artifacts
}


def _is_valid_source(source_file: str) -> bool:
    """Check if an entry's source_file indicates high-quality golden data.

    Returns True if:
    - source_file is empty (no provenance, assumed golden)
    - source_file starts with "(from " (derived from golden file itself)
    - source_file doesn't match any excluded prefix
    """
    if not source_file:
        return True
    if source_file.startswith("(from "):
        return True
    # Check against excluded prefixes
    for prefix in EXCLUDED_SOURCE_PREFIXES:
        if source_file.startswith(prefix):
            return False
    return True

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

# Registry procedure presence flags used as multi-label targets for ML.
# Imported from the canonical source in modules/registry/v2_booleans.py
# This ensures a single source of truth for V2 -> V3 boolean mapping.
#
# NOTE: If data/knowledge/IP_Registry.json changes, update the source module
# at modules/registry/v2_booleans.py to keep schema and ML labels in sync.
from modules.registry.v2_booleans import (
    PROCEDURE_BOOLEAN_FIELDS as REGISTRY_TARGET_FIELDS,
    extract_v2_booleans as _extract_v2_booleans_impl,
)

# Valid IP pulmonology CPT codes
VALID_IP_CODES = {
    # Bronchoscopy codes (316xx)
    "31622", "31623", "31624", "31625", "31626", "31627", "31628", "31629",
    "31631", "31632", "31633", "31634", "31635", "31636", "31637", "31638",
    "31640", "31641", "31645", "31646", "31647",
    "31652", "31653", "31654", "31660", "31661",
    # Pleural/thoracic codes (325xx, 326xx)
    "32550", "32551", "32552", "32554", "32555", "32556", "32557", "32560", "32561",
    "32601", "32604", "32606", "32607", "32608", "32609", "32650",
    # Special procedures
    "32997",  # Total lung lavage
}

# Known typos/errors and their corrections
# NOTE: 31635 is a VALID code for foreign body removal, NOT a typo
CODE_CORRECTIONS = {
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


def _extract_registry_booleans(entry: Dict[str, Any]) -> Dict[str, int]:
    """Map a V2 'Golden Extraction' registry entry to V3-style procedure flags.

    This function delegates to the canonical implementation in
    modules/registry/v2_booleans.extract_v2_booleans() to ensure
    consistent V2->V3 boolean mapping across the codebase.

    Args:
        entry: A V2 registry entry dict (typically from `registry_entry` in
               Golden Extraction JSON files).

    Returns:
        Dict mapping each field in REGISTRY_TARGET_FIELDS to 0 or 1.
        All fields are guaranteed to be present with integer values.
    """
    return _extract_v2_booleans_impl(entry)


def _filter_rare_registry_labels(
    labels: List[List[int]],
    min_count: int = 5,
) -> Tuple[List[List[int]], List[str]]:
    """Drop registry labels that are too rare to train on.

    Args:
        labels: List of multi-hot label vectors (each row is one example).
        min_count: Minimum number of positive examples required to keep a label.

    Returns:
        (filtered_labels, kept_field_names) where:
        - filtered_labels: Label matrix with rare columns removed
        - kept_field_names: List of field names that were kept
    """
    if not labels:
        return [], []

    # Convert to numpy for easier manipulation
    label_matrix = np.array(labels)

    # Compute per-column (label) counts
    label_counts = label_matrix.sum(axis=0)

    # Identify which columns meet the threshold
    keep_mask = label_counts >= min_count
    kept_indices = np.where(keep_mask)[0]

    # Build kept field names list
    kept_field_names = [REGISTRY_TARGET_FIELDS[i] for i in kept_indices]

    # Slice the label matrix to keep only non-rare columns
    filtered_matrix = label_matrix[:, keep_mask]

    # Convert back to list of lists
    filtered_labels = filtered_matrix.tolist()

    return filtered_labels, kept_field_names


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
    # Support both old consolidated format and new synthetic format
    patterns = [
        str(GOLDEN_DIR / "consolidated_verified_notes_v2_8_part_*.json"),
        str(GOLDEN_DIR / "synthetic_*.json"),
    ]
    files = []
    for pattern in patterns:
        files.extend([Path(p) for p in glob.glob(pattern)])
    return files


def _extract_codes(entry: Dict[str, Any]) -> List[str]:
    """
    Extract CPT codes from an entry.

    Priority order (ground truth first):
    1. cpt_codes (top-level ground truth)
    2. coding_review.final_cpt_codes (fallback)
    3. coding_review.cpt_summary.final_codes (fallback)
    4. coding_review.cpt_summary keys (fallback)
    5. coding_review.cpt_summary[].code (fallback)
    """
    # Primary: top-level cpt_codes is ground truth
    raw = entry.get("cpt_codes", [])
    if raw:
        return [str(c) for c in raw]

    # Fallback to coding_review if top-level missing
    cr = entry.get("coding_review", {})
    if not isinstance(cr, dict):
        cr = {}

    final_cpt = cr.get("final_cpt_codes")
    if final_cpt and isinstance(final_cpt, list):
        return [str(c) for c in final_cpt]

    summary = cr.get("cpt_summary")

    if isinstance(summary, dict):
        final = summary.get("final_codes")
        if final and isinstance(final, list):
            return [str(c) for c in final]
        codes = [k for k in summary.keys() if k.isdigit() or (k.startswith("3") and len(k) == 5)]
        if codes:
            return codes

    elif isinstance(summary, list):
        codes = []
        for item in summary:
            if isinstance(item, dict) and "code" in item:
                codes.append(str(item["code"]))
        if codes:
            return codes

    return []


def _flatten_entries(data: Any) -> List[Dict[str, Any]]:
    """Flatten entries from various JSON structures.

    Handles:
    - List of entry dicts (standard format)
    - Dict with category keys containing lists of entries (nested format)
    """
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    elif isinstance(data, dict):
        # Nested format: {"metadata": {...}, "category1": [...], "category2": [...]}
        entries = []
        for key, value in data.items():
            if key == "metadata":
                continue
            if isinstance(value, list):
                entries.extend([e for e in value if isinstance(e, dict)])
        return entries
    return []


def _build_dataframe() -> pd.DataFrame:
    """Build a DataFrame from all golden extraction files."""
    rows = []
    for file_path in _iter_golden_files():
        with open(file_path, "r") as f:
            data = json.load(f)

        for entry in _flatten_entries(data):
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


def _build_registry_dataframe() -> pd.DataFrame:
    """Build a DataFrame from golden extractions with registry boolean labels.

    Returns:
        DataFrame with columns: note_text, patient_mrn, procedure_date,
        source_file, is_edge_case, plus one column per REGISTRY_TARGET_FIELDS item.
    """
    rows = []
    for file_path in _iter_golden_files():
        with open(file_path, "r") as f:
            data = json.load(f)

        for entry in _flatten_entries(data):
            text = entry.get("note_text", "")
            source_file = entry.get("source_file", "")
            registry = entry.get("registry_entry") or {}

            if not text:
                continue

            mrn = registry.get("patient_mrn")
            date = registry.get("procedure_date")

            # Extract V3-style boolean flags from V2 registry entry
            flags = _extract_registry_booleans(registry)

            row = {
                "note_text": text,
                "patient_mrn": mrn,
                "procedure_date": date,
                "source_file": source_file,
                "is_edge_case": (source_file == EDGE_SOURCE_NAME),
            }
            row.update(flags)
            rows.append(row)

    df = pd.DataFrame(rows)
    return df


def _build_registry_label_matrix(
    df: pd.DataFrame, fields: List[str]
) -> np.ndarray:
    """Build multi-hot encoding matrix from registry boolean columns.

    Args:
        df: DataFrame with columns matching registry field names.
        fields: List of field names to extract (in order).

    Returns:
        numpy array of shape (n_samples, len(fields)) with 0/1 values.
    """
    y = np.zeros((len(df), len(fields)), dtype=int)
    for i, field in enumerate(fields):
        if field in df.columns:
            y[:, i] = df[field].fillna(0).astype(int).values
    return y


def _registry_stratified_split(
    df: pd.DataFrame,
    label_fields: List[str],
    test_size: float = 0.2,
) -> Tuple[np.ndarray, np.ndarray]:
    """Perform stratified split on registry data with encounter grouping.

    Args:
        df: DataFrame with registry data.
        label_fields: List of boolean label column names.
        test_size: Fraction for test set.

    Returns:
        (train_indices, test_indices) as numpy arrays.
    """
    y = _build_registry_label_matrix(df, label_fields)
    X_indices = np.arange(len(df)).reshape(-1, 1)

    # Use iterative stratification for multi-label split
    X_train, y_train, X_test, y_test = iterative_train_test_split(
        X_indices, y, test_size=test_size
    )

    # Enforce encounter grouping to prevent data leakage
    X_train, X_test = _enforce_encounter_grouping(df, X_train, X_test)
    return X_train.flatten(), X_test.flatten()


def prepare_registry_training_splits(
    output_dir: Path = Path("data/ml_training"),
    test_size: float = 0.2,
    min_label_count: int = 5,
) -> None:
    """
    Build registry procedure presence train/test CSV splits.

    This function extracts procedure boolean flags from V2 Golden Extraction
    registry entries, maps them to V3-style flags, filters rare labels,
    and generates stratified train/test splits.

    Args:
        output_dir: Directory to write output CSVs
        test_size: Fraction of data to use for test set (default 0.2)
        min_label_count: Minimum positive samples to keep a label (default 5)

    Outputs:
        - registry_train.csv: Training set with note_text + boolean columns
        - registry_test.csv: Test set with note_text + boolean columns
        - registry_label_fields.json: List of kept label field names (ordering)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    df = _build_registry_dataframe()

    print(f"Total registry entries loaded: {len(df)}")

    # Separate edge cases for holdout
    df_main = df[~df["is_edge_case"]].reset_index(drop=True)
    df_edge = df[df["is_edge_case"]].reset_index(drop=True)

    print(f"Main samples: {len(df_main)}, Edge case samples: {len(df_edge)}")

    # Build label matrix and filter rare labels
    all_labels = _build_registry_label_matrix(df_main, REGISTRY_TARGET_FIELDS)
    filtered_labels, kept_fields = _filter_rare_registry_labels(
        all_labels.tolist(), min_count=min_label_count
    )

    print(f"Labels kept after filtering (>= {min_label_count} samples): {len(kept_fields)}")
    print(f"Kept labels: {kept_fields}")

    # Compute per-label counts for summary
    label_counts = np.array(filtered_labels).sum(axis=0) if filtered_labels else []
    if len(label_counts) > 0:
        print(f"Label counts - min: {label_counts.min()}, median: {int(np.median(label_counts))}, max: {label_counts.max()}")

    # Perform stratified split on kept labels
    train_idx, test_idx = _registry_stratified_split(
        df_main, kept_fields, test_size=test_size
    )

    train_df = df_main.iloc[train_idx]
    test_df = df_main.iloc[test_idx]

    # Select output columns: note_text + kept boolean fields
    output_columns = ["note_text"] + kept_fields
    train_out = train_df[output_columns].copy()
    test_out = test_df[output_columns].copy()

    # Save CSVs
    train_out.to_csv(output_dir / "registry_train.csv", index=False)
    test_out.to_csv(output_dir / "registry_test.csv", index=False)

    # Save kept field names for inference ordering
    with open(output_dir / "registry_label_fields.json", "w") as f:
        json.dump(kept_fields, f, indent=2)

    # Save edge cases separately if any
    if len(df_edge) > 0:
        edge_out = df_edge[output_columns].copy()
        edge_out.to_csv(output_dir / "registry_edge_cases.csv", index=False)
        print(f"Edge case holdout samples: {len(df_edge)}")

    print(f"\n=== Registry Data Prep Summary ===")
    print(f"Train samples: {len(train_out)}")
    print(f"Test samples: {len(test_out)}")
    print(f"Number of labels: {len(kept_fields)}")
    print(f"Output written to: {output_dir}")

    # Print per-label stats for train set
    print(f"\nPer-label counts in train set:")
    train_label_matrix = _build_registry_label_matrix(train_out, kept_fields)
    train_counts = train_label_matrix.sum(axis=0)
    for field, count in zip(kept_fields, train_counts):
        print(f"  {field}: {count}")


if __name__ == "__main__":
    prepare_training_and_eval_splits()
