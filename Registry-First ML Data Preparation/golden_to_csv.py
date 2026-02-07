#!/usr/bin/env python3
"""
Golden JSON → ML Training CSV Converter (Registry-First Method)

This script converts golden_*.json files into properly stratified CSV files
for training registry prediction models. It extracts the 30 boolean procedure
flags from the nested registry_entry structure.

Usage:
    python golden_to_csv.py --input-dir data/knowledge/golden_extractions_final \
                            --output-dir data/ml_training \
                            --prefix registry

Output:
    - registry_train.csv (70%)
    - registry_val.csv (15%)
    - registry_test.csv (15%)

Each CSV contains:
    - note_text: The procedure note text
    - encounter_id: Unique identifier for encounter-level grouping
    - source_file: Origin golden JSON file
    - [30 boolean procedure columns]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


# =============================================================================
# V2 Boolean Fields (Canonical 30 Procedure Flags)
# =============================================================================
# These are the target labels for ML training, derived from app/registry/v2_booleans.py

BRONCHOSCOPY_PROCEDURES = [
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
    "tumor_debulking_non_thermal",
    "cryotherapy",
    "blvr",
    "peripheral_ablation",
    "bronchial_thermoplasty",
    "whole_lung_lavage",
    "rigid_bronchoscopy",
]

PLEURAL_PROCEDURES = [
    "thoracentesis",
    "chest_tube",
    "ipc",
    "medical_thoracoscopy",
    "pleurodesis",
    "pleural_biopsy",
    "fibrinolytic_therapy",
]

ALL_PROCEDURE_FLAGS = BRONCHOSCOPY_PROCEDURES + PLEURAL_PROCEDURES

# Alternate field names that map to canonical flags (V2 ↔ V3 compatibility)
FIELD_ALIASES = {
    # V3 granular → V2 canonical
    "ebus_linear": "linear_ebus",
    "ebus_radial": "radial_ebus",
    "navigation": "navigational_bronchoscopy",
    "tbna": "tbna_conventional",
    "tbb": "transbronchial_biopsy",
    "tbb_cryo": "transbronchial_cryobiopsy",
    "stent": "airway_stent",
    "dilation": "airway_dilation",
    "ablation_thermal": "thermal_ablation",
    "ablation_cryo": "cryotherapy",
    "ablation_peripheral": "peripheral_ablation",
    "thermoplasty": "bronchial_thermoplasty",
    "wll": "whole_lung_lavage",
    "rigid": "rigid_bronchoscopy",
    "thoraco": "medical_thoracoscopy",
    "ipc_placement": "ipc",
    "tube": "chest_tube",
    "tap": "thoracentesis",
}


@dataclass
class ExtractionStats:
    """Statistics for tracking extraction quality."""
    total_files: int = 0
    successful: int = 0
    skipped_no_text: int = 0
    skipped_no_registry: int = 0
    skipped_empty_labels: int = 0
    parsing_errors: int = 0
    label_counts: Counter = field(default_factory=Counter)
    
    def summary(self) -> str:
        lines = [
            f"Extraction Summary:",
            f"  Total files processed: {self.total_files}",
            f"  Successful extractions: {self.successful}",
            f"  Skipped (no note_text): {self.skipped_no_text}",
            f"  Skipped (no registry): {self.skipped_no_registry}",
            f"  Skipped (empty labels): {self.skipped_empty_labels}",
            f"  Parsing errors: {self.parsing_errors}",
            f"\nLabel Distribution (top 15):",
        ]
        for label, count in self.label_counts.most_common(15):
            lines.append(f"  {label}: {count}")
        return "\n".join(lines)


def extract_bool_from_nested(data: dict[str, Any], path: list[str]) -> bool | None:
    """Extract a boolean value from a nested dict using a path.
    
    Args:
        data: Nested dictionary
        path: List of keys to traverse (e.g., ["procedures_performed", "bronchoscopy", "bal"])
        
    Returns:
        Boolean value if found, None otherwise
    """
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    
    if isinstance(current, bool):
        return current
    if isinstance(current, dict):
        # Check for "performed" sub-key (common pattern)
        return current.get("performed", None)
    return None


def extract_procedures_from_registry(registry: dict[str, Any]) -> dict[str, bool]:
    """Extract all procedure boolean flags from a registry entry.
    
    Handles multiple schema versions (V2, V3) and nested structures.
    
    Args:
        registry: Registry entry dictionary
        
    Returns:
        Dict mapping canonical procedure names to boolean values
    """
    result = {flag: False for flag in ALL_PROCEDURE_FLAGS}
    
    # Path patterns to search for procedure flags
    search_paths = [
        # V2 flat structure
        [],
        # V2 procedures_performed section
        ["procedures_performed"],
        # V2 procedures_performed.bronchoscopy
        ["procedures_performed", "bronchoscopy"],
        # V2 procedures_performed.pleural
        ["procedures_performed", "pleural"],
        # V3 granular_data section
        ["granular_data"],
        # V3 granular_data.bronchoscopy
        ["granular_data", "bronchoscopy"],
        # V3 granular_data.pleural
        ["granular_data", "pleural"],
    ]
    
    def get_nested(d: dict, path: list[str]) -> dict | None:
        """Navigate to nested dict."""
        current = d
        for key in path:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        return current if isinstance(current, dict) else None
    
    for path in search_paths:
        section = get_nested(registry, path) if path else registry
        if not section:
            continue
            
        for key, value in section.items():
            # Normalize key to canonical form
            canonical = FIELD_ALIASES.get(key, key)
            
            if canonical not in ALL_PROCEDURE_FLAGS:
                continue
                
            # Extract boolean value
            if isinstance(value, bool):
                if value:  # Only set True, don't overwrite with False
                    result[canonical] = True
            elif isinstance(value, dict):
                # Check for "performed" key
                performed = value.get("performed")
                if performed is True:
                    result[canonical] = True
                # Also check for any truthy nested values indicating procedure was done
                if any(v is True for v in value.values() if isinstance(v, bool)):
                    result[canonical] = True
    
    return result


def generate_encounter_id(file_path: Path, note_text: str) -> str:
    """Generate a stable encounter ID for grouping.
    
    Uses file path + first 100 chars of note to create a stable hash.
    This ensures all windows from the same note stay in the same split.
    """
    content = f"{file_path.stem}:{note_text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def load_golden_json(file_path: Path) -> dict[str, Any] | None:
    """Load and validate a golden JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error in {file_path.name}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Error loading {file_path.name}: {e}")
        return None


def extract_record(file_path: Path, data: dict[str, Any], stats: ExtractionStats) -> dict[str, Any] | None:
    """Extract a single training record from golden JSON data.
    
    Args:
        file_path: Source file path
        data: Parsed JSON data
        stats: Statistics tracker
        
    Returns:
        Flattened record dict or None if extraction failed
    """
    # Extract note text
    note_text = data.get("note_text") or data.get("text") or data.get("note")
    if not note_text or not isinstance(note_text, str) or len(note_text.strip()) < 50:
        stats.skipped_no_text += 1
        return None
    
    note_text = note_text.strip()
    
    # Extract registry entry
    registry = data.get("registry_entry") or data.get("registry") or data.get("extraction")
    if not registry or not isinstance(registry, dict):
        stats.skipped_no_registry += 1
        return None
    
    # Extract procedure flags
    procedures = extract_procedures_from_registry(registry)
    
    # Check if at least one procedure is True
    if not any(procedures.values()):
        # Try to salvage from CPT codes if available
        cpt_codes = data.get("cpt_codes") or data.get("codes") or []
        if not cpt_codes:
            stats.skipped_empty_labels += 1
            return None
    
    # Build record
    record = {
        "note_text": note_text,
        "encounter_id": generate_encounter_id(file_path, note_text),
        "source_file": file_path.name,
    }
    
    # Add procedure flags
    for flag in ALL_PROCEDURE_FLAGS:
        value = procedures.get(flag, False)
        record[flag] = 1 if value else 0
        if value:
            stats.label_counts[flag] += 1
    
    stats.successful += 1
    return record


def iterative_stratified_split(
    df: pd.DataFrame,
    label_columns: list[str],
    group_column: str = "encounter_id",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Perform stratified split with encounter-level grouping.
    
    Uses iterative stratification for multi-label classification,
    ensuring all rows from the same encounter stay in the same split.
    
    Args:
        df: Input DataFrame
        label_columns: List of binary label column names
        group_column: Column to group by (prevent data leakage)
        train_ratio: Fraction for training set
        val_ratio: Fraction for validation set
        test_ratio: Fraction for test set
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"
    
    np.random.seed(random_state)
    
    # Get unique encounters and their label vectors
    encounter_groups = df.groupby(group_column)
    encounters = list(encounter_groups.groups.keys())
    
    # Aggregate labels per encounter (any True in group → True for encounter)
    encounter_labels = {}
    for enc_id in encounters:
        group = encounter_groups.get_group(enc_id)
        label_vec = tuple(int(group[col].max()) for col in label_columns)
        encounter_labels[enc_id] = label_vec
    
    # Convert to arrays for stratification
    enc_array = np.array(encounters)
    label_matrix = np.array([encounter_labels[e] for e in encounters])
    
    # Try scikit-multilearn's iterative stratification if available
    try:
        from skmultilearn.model_selection import IterativeStratification
        
        # First split: train vs (val+test)
        stratifier = IterativeStratification(
            n_splits=2,
            order=2,
            sample_distribution_per_fold=[1 - train_ratio, train_ratio],
            random_state=random_state,
        )
        
        train_idx, rest_idx = next(stratifier.split(enc_array.reshape(-1, 1), label_matrix))
        train_encounters = set(enc_array[train_idx])
        rest_encounters = enc_array[rest_idx]
        rest_labels = label_matrix[rest_idx]
        
        # Second split: val vs test
        val_fraction = val_ratio / (val_ratio + test_ratio)
        stratifier2 = IterativeStratification(
            n_splits=2,
            order=2,
            sample_distribution_per_fold=[1 - val_fraction, val_fraction],
            random_state=random_state + 1,
        )
        
        val_idx, test_idx = next(stratifier2.split(rest_encounters.reshape(-1, 1), rest_labels))
        val_encounters = set(rest_encounters[val_idx])
        test_encounters = set(rest_encounters[test_idx])
        
        logger.info("Using skmultilearn iterative stratification")
        
    except ImportError:
        logger.warning("skmultilearn not available, falling back to simple stratification")
        
        # Simple random split with encounter grouping
        np.random.shuffle(enc_array)
        n = len(enc_array)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        
        train_encounters = set(enc_array[:n_train])
        val_encounters = set(enc_array[n_train:n_train + n_val])
        test_encounters = set(enc_array[n_train + n_val:])
    
    # Split DataFrame based on encounter assignments
    train_df = df[df[group_column].isin(train_encounters)].copy()
    val_df = df[df[group_column].isin(val_encounters)].copy()
    test_df = df[df[group_column].isin(test_encounters)].copy()
    
    return train_df, val_df, test_df


def filter_rare_labels(
    df: pd.DataFrame,
    label_columns: list[str],
    min_count: int = 5,
) -> tuple[pd.DataFrame, list[str]]:
    """Remove label columns that appear fewer than min_count times.
    
    Args:
        df: Input DataFrame
        label_columns: List of label column names
        min_count: Minimum number of positive examples required
        
    Returns:
        Tuple of (filtered_df, remaining_label_columns)
    """
    remaining = []
    dropped = []
    
    for col in label_columns:
        count = df[col].sum()
        if count >= min_count:
            remaining.append(col)
        else:
            dropped.append((col, count))
            df = df.drop(columns=[col])
    
    if dropped:
        logger.warning(f"Dropped {len(dropped)} rare labels: {dropped}")
    
    return df, remaining


def validate_split(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    label_columns: list[str],
) -> bool:
    """Validate that splits have no data leakage and acceptable label coverage."""
    # Check for encounter leakage
    train_enc = set(train_df["encounter_id"])
    val_enc = set(val_df["encounter_id"])
    test_enc = set(test_df["encounter_id"])
    
    if train_enc & val_enc:
        logger.error("Data leakage: encounters in both train and val")
        return False
    if train_enc & test_enc:
        logger.error("Data leakage: encounters in both train and test")
        return False
    if val_enc & test_enc:
        logger.error("Data leakage: encounters in both val and test")
        return False
    
    # Check label coverage in train
    for col in label_columns:
        train_count = train_df[col].sum()
        if train_count == 0:
            logger.warning(f"No positive examples of '{col}' in train set")
    
    logger.info(f"Split validation passed: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert golden JSONs to ML training CSVs (registry-first method)"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/knowledge/golden_extractions_final"),
        help="Directory containing golden_*.json files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/ml_training"),
        help="Output directory for CSV files",
    )
    parser.add_argument(
        "--prefix",
        default="registry",
        help="Prefix for output CSV files (e.g., registry_train.csv)",
    )
    parser.add_argument(
        "--min-label-count",
        type=int,
        default=5,
        help="Minimum positive examples required for a label",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.70,
        help="Fraction of data for training",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.15,
        help="Fraction of data for validation",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.15,
        help="Fraction of data for testing",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing files",
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    # Find golden JSON files
    json_files = sorted(args.input_dir.glob("golden_*.json"))
    if not json_files:
        logger.error(f"No golden_*.json files found in {args.input_dir}")
        sys.exit(1)
    
    logger.info(f"Found {len(json_files)} golden JSON files in {args.input_dir}")
    
    # Extract records
    stats = ExtractionStats()
    records = []
    
    for file_path in json_files:
        stats.total_files += 1
        
        data = load_golden_json(file_path)
        if data is None:
            stats.parsing_errors += 1
            continue
        
        record = extract_record(file_path, data, stats)
        if record:
            records.append(record)
    
    logger.info(f"\n{stats.summary()}")
    
    if not records:
        logger.error("No valid records extracted")
        sys.exit(1)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    logger.info(f"Created DataFrame with {len(df)} records, {len(df.columns)} columns")
    
    # Filter rare labels
    df, remaining_labels = filter_rare_labels(
        df, ALL_PROCEDURE_FLAGS, min_count=args.min_label_count
    )
    logger.info(f"Remaining labels after filtering: {len(remaining_labels)}")
    
    # Perform stratified split
    train_df, val_df, test_df = iterative_stratified_split(
        df,
        label_columns=remaining_labels,
        group_column="encounter_id",
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_state=args.random_seed,
    )
    
    # Validate splits
    if not validate_split(train_df, val_df, test_df, remaining_labels):
        logger.error("Split validation failed")
        sys.exit(1)
    
    # Calculate label statistics per split
    logger.info("\nLabel distribution per split:")
    for name, split_df in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        total_labels = sum(split_df[col].sum() for col in remaining_labels)
        logger.info(f"  {name}: {len(split_df)} samples, {total_labels} total positive labels")
    
    if args.dry_run:
        logger.info("Dry run complete - no files written")
        return
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write CSV files
    train_path = args.output_dir / f"{args.prefix}_train.csv"
    val_path = args.output_dir / f"{args.prefix}_val.csv"
    test_path = args.output_dir / f"{args.prefix}_test.csv"
    
    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    logger.info(f"\nWritten:")
    logger.info(f"  {train_path} ({len(train_df)} rows)")
    logger.info(f"  {val_path} ({len(val_df)} rows)")
    logger.info(f"  {test_path} ({len(test_df)} rows)")
    
    # Write metadata
    meta_path = args.output_dir / f"{args.prefix}_meta.json"
    meta = {
        "source_dir": str(args.input_dir),
        "total_files": stats.total_files,
        "successful_extractions": stats.successful,
        "label_columns": remaining_labels,
        "split_sizes": {
            "train": len(train_df),
            "val": len(val_df),
            "test": len(test_df),
        },
        "label_counts": dict(stats.label_counts),
        "random_seed": args.random_seed,
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    logger.info(f"  {meta_path}")


if __name__ == "__main__":
    main()
