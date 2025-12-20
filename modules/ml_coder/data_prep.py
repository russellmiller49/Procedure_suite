"""
Data preparation module for ML coder training.

Builds clean training CSVs from golden JSONs with patient-level splitting
to support Silver Standard training (Train on Synthetic+Real, Test on Real).
"""

from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Allow running this file directly
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

GOLDEN_DIR = Path("data/knowledge/golden_extractions")
EDGE_SOURCE_NAME = "synthetic_edge_case_notes_with_registry.jsonl"

# Old/low-quality source files to exclude.
EXCLUDED_SOURCE_PREFIXES = {
    "synthetic_notes_with_CPT",       # Old CSV-based data
    "synthetic_CPT_corrected",        # Old corrected data
    "recovered_metadata",             # Recovery artifacts
}

def _is_valid_source(source_file: str) -> bool:
    """Check if an entry's source_file is valid for ingestion."""
    if not source_file:
        return True
    if source_file.startswith("(from "):
        return True
    for prefix in EXCLUDED_SOURCE_PREFIXES:
        if source_file.startswith(prefix):
            return False
    return True

# Registry procedure presence flags used as multi-label targets for ML.
from modules.registry.v2_booleans import (
    PROCEDURE_BOOLEAN_FIELDS as REGISTRY_TARGET_FIELDS,
    extract_v2_booleans as _extract_v2_booleans_impl,
)

def _extract_registry_booleans(entry: Dict[str, Any]) -> Dict[str, int]:
    """Map a V2 registry entry to V3-style procedure flags."""
    return _extract_v2_booleans_impl(entry)

def _filter_rare_registry_labels(
    labels: List[List[int]],
    min_count: int = 5,
) -> Tuple[List[List[int]], List[str]]:
    """Drop registry labels that are too rare to train on."""
    if not labels:
        return [], []
    label_matrix = np.array(labels)
    label_counts = label_matrix.sum(axis=0)
    keep_mask = label_counts >= min_count
    kept_indices = np.where(keep_mask)[0]
    kept_field_names = [REGISTRY_TARGET_FIELDS[i] for i in kept_indices]
    filtered_matrix = label_matrix[:, keep_mask]
    return filtered_matrix.tolist(), kept_field_names

def _iter_golden_files() -> List[Path]:
    """Iterate over golden extraction JSON files."""
    patterns = [
        str(GOLDEN_DIR / "golden_*.json"),
        str(GOLDEN_DIR / "consolidated_verified_notes_v2_8_part_*.json"),
        str(GOLDEN_DIR / "synthetic_*.json"),
        str(GOLDEN_DIR / "*.jsonl")
    ]
    files: List[Path] = []
    for pattern in patterns:
        files.extend(Path(p) for p in glob.glob(pattern))
    
    seen: set[Path] = set()
    unique: List[Path] = []
    for p in files:
        if p in seen:
            continue
        seen.add(p)
        unique.append(p)
    return unique

def _flatten_entries(data: Any) -> List[Dict[str, Any]]:
    """Flatten entries from various JSON structures."""
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    elif isinstance(data, dict):
        entries = []
        for key, value in data.items():
            if key == "metadata":
                continue
            if isinstance(value, list):
                entries.extend([e for e in value if isinstance(e, dict)])
        return entries
    return []

def _build_registry_dataframe() -> pd.DataFrame:
    """Build a DataFrame from all extraction files with Silver Standard metadata.
    
    Extracts:
    - note_text
    - boolean procedure flags
    - is_synthetic: True if note is AI-generated
    - root_mrn: The base patient ID (groups Real + Synthetic variations)
    """
    rows = []
    for file_path in _iter_golden_files():
        try:
            # Handle JSONL vs JSON
            if file_path.suffix == '.jsonl':
                with open(file_path, "r") as f:
                    data = [json.loads(line) for line in f]
            else:
                with open(file_path, "r") as f:
                    data = json.load(f)
        except Exception as e:
            print(f"Skipping malformed file {file_path}: {e}")
            continue

        for entry in _flatten_entries(data):
            text = entry.get("note_text", "")
            source_file = entry.get("source_file", "")
            
            if not _is_valid_source(source_file):
                continue

            registry = entry.get("registry_entry") or {}
            if not text:
                continue

            mrn = str(registry.get("patient_mrn", ""))
            date = registry.get("procedure_date")

            # --- ROBUST SYNTHETIC DETECTION ---
            # 1. File name check
            file_is_syn = "synthetic" in file_path.name.lower()
            # 2. Source field check
            source_is_syn = "synthetic" in str(source_file).lower()
            # 3. MRN convention check
            mrn_is_syn = "_syn" in mrn
            # 4. Metadata check (present in golden_084.json)
            meta_is_syn = "synthetic_metadata" in entry

            is_synthetic = file_is_syn or source_is_syn or mrn_is_syn or meta_is_syn
            
            # --- ROOT MRN EXTRACTION ---
            # Extracts 'S31640-021' from 'S31640-021_syn_1' so they stay grouped
            root_mrn = mrn.split("_syn")[0] if mrn else f"unknown_{len(rows)}"

            flags = _extract_registry_booleans(registry)

            row = {
                "note_text": text,
                "patient_mrn": mrn,
                "root_mrn": root_mrn,
                "procedure_date": date,
                "source_file": source_file,
                "is_synthetic": is_synthetic,
                "is_edge_case": (source_file == EDGE_SOURCE_NAME),
            }
            row.update(flags)
            rows.append(row)

    df = pd.DataFrame(rows)
    return df

def _silver_standard_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform a Patient-Level split enforcing Silver Standard logic.
    
    Logic:
    1. Group by `root_mrn` (Unique Patient).
    2. Split unique patients into Train Patients (80%) and Test Patients (20%).
    3. Train Set = All records (Real + Synthetic) for the Train Patients.
    4. Test Set = ONLY Real records for the Test Patients. (Synthetic records for Test Patients are dropped).
    """
    unique_patients = df["root_mrn"].unique()
    
    # Split patients, not rows, to prevent data leakage
    train_patients, test_patients = train_test_split(
        unique_patients, 
        test_size=test_size, 
        random_state=random_state
    )
    
    train_patients_set = set(train_patients)
    test_patients_set = set(test_patients)
    
    # Select indices
    # Train: All records belonging to Train Patients (Real + Synthetic)
    train_mask = df["root_mrn"].isin(train_patients_set)
    
    # Test: Only REAL records belonging to Test Patients
    # This prevents the model from being evaluated on synthetic text
    test_mask = df["root_mrn"].isin(test_patients_set) & (~df["is_synthetic"])
    
    return df[train_mask].index.values, df[test_mask].index.values

def _build_registry_label_matrix(df: pd.DataFrame, fields: List[str]) -> np.ndarray:
    """Build multi-hot encoding matrix from registry boolean columns."""
    y = np.zeros((len(df), len(fields)), dtype=int)
    for i, field in enumerate(fields):
        if field in df.columns:
            y[:, i] = df[field].fillna(0).astype(int).values
    return y

def prepare_registry_training_splits(
    output_dir: Path = Path("data/ml_training"),
    test_size: float = 0.2,
    min_label_count: int = 5,
) -> None:
    """Build registry procedure presence train/test CSV splits."""
    output_dir.mkdir(parents=True, exist_ok=True)
    df = _build_registry_dataframe()

    print(f"Total registry entries loaded: {len(df)}")
    if len(df) > 0:
        print(f"  - Real: {len(df[~df['is_synthetic']])}")
        print(f"  - Synthetic: {len(df[df['is_synthetic']])}")

    # Separate edge cases for holdout
    df_main = df[~df["is_edge_case"]].reset_index(drop=True)
    df_edge = df[df["is_edge_case"]].reset_index(drop=True)

    # Build label matrix and filter rare labels
    all_labels = _build_registry_label_matrix(df_main, REGISTRY_TARGET_FIELDS)
    filtered_labels, kept_fields = _filter_rare_registry_labels(
        all_labels.tolist(), min_count=min_label_count
    )

    print(f"Labels kept after filtering (>= {min_label_count} samples): {len(kept_fields)}")

    # Perform Silver Standard Split
    train_idx, test_idx = _silver_standard_split(
        df_main, test_size=test_size
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

    print(f"\n=== Registry Data Prep Summary (Silver Standard) ===")
    print(f"Train samples: {len(train_out)} (Mixed Real + Synthetic)")
    print(f"Test samples:  {len(test_out)} (Pure Real)")
    print(f"Output written to: {output_dir}")

    # Print per-label stats for train set
    print(f"\nPer-label counts in train set:")
    train_label_matrix = _build_registry_label_matrix(train_out, kept_fields)
    train_counts = train_label_matrix.sum(axis=0)
    for field, count in zip(kept_fields, train_counts):
        print(f"  {field}: {count}")

if __name__ == "__main__":
    prepare_registry_training_splits()