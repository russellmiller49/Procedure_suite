"""
Registry-First Data Preparation Module

This module provides functions for preparing ML training data from golden JSON files
using the registry-first approach. The key function is `prepare_registry_training_splits()`
which is referenced in CLAUDE.md as the entry point for generating training data.

Integration with existing codebase:
    - Place this file at: ml/lib/ml_coder/registry_data_prep.py
    - Import in data_prep.py: from .registry_data_prep import prepare_registry_training_splits
    - Or use standalone: python -m ml.lib.ml_coder.registry_data_prep

Example:
    from ml.lib.ml_coder.registry_data_prep import prepare_registry_training_splits
    
    train_df, val_df, test_df = prepare_registry_training_splits()
    train_df.to_csv("data/ml_training/registry_train.csv", index=False)
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# =============================================================================
# Canonical Procedure Flags (V2 Schema)
# =============================================================================
# These 30 boolean flags are the ML targets for registry-first prediction.
# See: app/registry/v2_booleans.py for the authoritative source.

BRONCHOSCOPY_LABELS = [
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

PLEURAL_LABELS = [
    "thoracentesis",
    "chest_tube",
    "ipc",
    "medical_thoracoscopy",
    "pleurodesis",
    "pleural_biopsy",
    "fibrinolytic_therapy",
]

ALL_PROCEDURE_LABELS = BRONCHOSCOPY_LABELS + PLEURAL_LABELS

# Alias mapping for V2 ↔ V3 schema compatibility
LABEL_ALIASES = {
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
class RegistryExtractionResult:
    """Result from extracting training data from golden JSONs."""
    
    df: pd.DataFrame
    label_columns: list[str]
    stats: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


class RegistryLabelExtractor:
    """Extracts boolean procedure labels from nested registry structures.
    
    Handles multiple schema versions (V2 flat, V3 granular) and various
    nesting patterns found in golden JSON files.
    """
    
    # Paths to search for procedure flags in registry structure
    SEARCH_PATHS = [
        [],  # Top level
        ["procedures_performed"],
        ["procedures_performed", "bronchoscopy"],
        ["procedures_performed", "pleural"],
        ["granular_data"],
        ["granular_data", "bronchoscopy"],
        ["granular_data", "pleural"],
    ]
    
    def __init__(self, labels: list[str] = None, aliases: dict[str, str] = None):
        self.labels = labels or ALL_PROCEDURE_LABELS
        self.aliases = aliases or LABEL_ALIASES
    
    def _get_nested(self, data: dict, path: list[str]) -> dict | None:
        """Navigate to a nested dict by path."""
        current = data
        for key in path:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        return current if isinstance(current, dict) else None
    
    def _normalize_key(self, key: str) -> str:
        """Convert alias key to canonical label name."""
        return self.aliases.get(key, key)
    
    def _extract_bool(self, value: Any) -> bool | None:
        """Extract boolean from value (handles dict with 'performed' key)."""
        if isinstance(value, bool):
            return value
        if isinstance(value, dict):
            # Check for "performed" key
            if "performed" in value:
                return value["performed"] is True
            # Check for any True boolean in the dict
            return any(v is True for v in value.values() if isinstance(v, bool))
        return None
    
    def extract(self, registry: dict[str, Any]) -> dict[str, int]:
        """Extract all procedure labels from a registry entry.
        
        Args:
            registry: Registry entry dictionary
            
        Returns:
            Dict mapping label names to binary values (0/1)
        """
        result = {label: 0 for label in self.labels}
        
        for path in self.SEARCH_PATHS:
            section = self._get_nested(registry, path) if path else registry
            if not section:
                continue
            
            for key, value in section.items():
                canonical = self._normalize_key(key)
                if canonical not in self.labels:
                    continue
                
                extracted = self._extract_bool(value)
                if extracted is True:
                    result[canonical] = 1
        
        return result


def _generate_encounter_id(source: str, text: str) -> str:
    """Generate stable encounter ID for grouping."""
    content = f"{source}:{text[:100]}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def _load_golden_json(path: Path) -> dict | None:
    """Load a golden JSON file with error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.warning(f"Failed to load {path.name}: {e}")
        return None


def extract_records_from_golden_dir(
    golden_dir: Path,
    extractor: RegistryLabelExtractor = None,
    min_text_length: int = 50,
) -> tuple[list[dict], dict[str, Any]]:
    """Extract training records from all golden JSONs in a directory.
    
    Args:
        golden_dir: Directory containing golden_*.json files
        extractor: Label extractor instance (uses default if None)
        min_text_length: Minimum note text length to include
        
    Returns:
        Tuple of (records list, statistics dict)
    """
    extractor = extractor or RegistryLabelExtractor()
    
    stats = {
        "total_files": 0,
        "successful": 0,
        "skipped_no_text": 0,
        "skipped_no_registry": 0,
        "skipped_empty_labels": 0,
        "parse_errors": 0,
        "label_counts": Counter(),
    }
    
    records = []
    json_files = sorted(golden_dir.glob("golden_*.json"))
    
    for path in json_files:
        stats["total_files"] += 1
        
        data = _load_golden_json(path)
        if data is None:
            stats["parse_errors"] += 1
            continue
        
        # Extract note text
        note_text = data.get("note_text") or data.get("text") or data.get("note")
        if not note_text or not isinstance(note_text, str):
            stats["skipped_no_text"] += 1
            continue
        
        note_text = note_text.strip()
        if len(note_text) < min_text_length:
            stats["skipped_no_text"] += 1
            continue
        
        # Extract registry
        registry = data.get("registry_entry") or data.get("registry") or data.get("extraction")
        if not registry or not isinstance(registry, dict):
            stats["skipped_no_registry"] += 1
            continue
        
        # Extract labels
        labels = extractor.extract(registry)
        
        # Require at least one positive label
        if not any(v == 1 for v in labels.values()):
            stats["skipped_empty_labels"] += 1
            continue
        
        # Build record
        record = {
            "note_text": note_text,
            "encounter_id": _generate_encounter_id(path.stem, note_text),
            "source_file": path.name,
            **labels,
        }
        records.append(record)
        stats["successful"] += 1
        
        # Update label counts
        for label, value in labels.items():
            if value == 1:
                stats["label_counts"][label] += 1
    
    return records, stats


def stratified_split(
    df: pd.DataFrame,
    label_columns: list[str],
    group_column: str = "encounter_id",
    train_size: float = 0.70,
    val_size: float = 0.15,
    test_size: float = 0.15,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Perform multi-label stratified split with encounter grouping.
    
    Uses iterative stratification when skmultilearn is available,
    otherwise falls back to random split with encounter grouping.
    
    Args:
        df: Input DataFrame
        label_columns: Binary label column names
        group_column: Column for encounter-level grouping
        train_size: Training set fraction
        val_size: Validation set fraction
        test_size: Test set fraction
        random_state: Random seed
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    np.random.seed(random_state)
    
    # Get unique encounters
    encounters = df[group_column].unique()
    n_encounters = len(encounters)
    
    # Build encounter-level label matrix
    enc_to_labels = {}
    for enc_id in encounters:
        mask = df[group_column] == enc_id
        label_vec = tuple(int(df.loc[mask, col].max()) for col in label_columns)
        enc_to_labels[enc_id] = label_vec
    
    enc_array = np.array(encounters)
    label_matrix = np.array([enc_to_labels[e] for e in encounters])
    
    # Try skmultilearn for proper stratification
    try:
        from skmultilearn.model_selection import IterativeStratification
        
        # Split train vs rest
        strat1 = IterativeStratification(
            n_splits=2,
            order=2,
            sample_distribution_per_fold=[1 - train_size, train_size],
            random_state=random_state,
        )
        train_idx, rest_idx = next(strat1.split(enc_array.reshape(-1, 1), label_matrix))
        
        train_encounters = set(enc_array[train_idx])
        rest_enc = enc_array[rest_idx]
        rest_labels = label_matrix[rest_idx]
        
        # Split val vs test
        val_frac = val_size / (val_size + test_size)
        strat2 = IterativeStratification(
            n_splits=2,
            order=2,
            sample_distribution_per_fold=[1 - val_frac, val_frac],
            random_state=random_state + 1,
        )
        val_idx, test_idx = next(strat2.split(rest_enc.reshape(-1, 1), rest_labels))
        
        val_encounters = set(rest_enc[val_idx])
        test_encounters = set(rest_enc[test_idx])
        
        logger.info("Using skmultilearn iterative stratification")
        
    except ImportError:
        logger.warning("skmultilearn not installed, using random split")
        
        np.random.shuffle(enc_array)
        n_train = int(n_encounters * train_size)
        n_val = int(n_encounters * val_size)
        
        train_encounters = set(enc_array[:n_train])
        val_encounters = set(enc_array[n_train:n_train + n_val])
        test_encounters = set(enc_array[n_train + n_val:])
    
    train_df = df[df[group_column].isin(train_encounters)].copy()
    val_df = df[df[group_column].isin(val_encounters)].copy()
    test_df = df[df[group_column].isin(test_encounters)].copy()
    
    return train_df, val_df, test_df


def filter_rare_labels(
    df: pd.DataFrame,
    label_columns: list[str],
    min_count: int = 5,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Remove labels with fewer than min_count positive examples.
    
    Args:
        df: Input DataFrame
        label_columns: Label column names
        min_count: Minimum required positive examples
        
    Returns:
        Tuple of (filtered_df, remaining_labels, dropped_labels)
    """
    remaining = []
    dropped = []
    
    for col in label_columns:
        if df[col].sum() >= min_count:
            remaining.append(col)
        else:
            dropped.append(col)
    
    if dropped:
        df = df.drop(columns=dropped)
        logger.warning(f"Dropped {len(dropped)} rare labels: {dropped}")
    
    return df, remaining, dropped


def prepare_registry_training_splits(
    golden_dir: Path | str = None,
    min_label_count: int = 5,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Main entry point for registry-first training data preparation.
    
    This function:
    1. Scans all golden_*.json files in the golden directory
    2. Extracts note text and 30 boolean procedure flags
    3. Filters rare labels (< min_label_count examples)
    4. Performs iterative multi-label stratification
    5. Ensures encounter-level grouping (no data leakage)
    
    Args:
        golden_dir: Directory with golden_*.json files. Defaults to 
                    data/knowledge/golden_extractions_final or golden_extractions
        min_label_count: Minimum positive examples required per label
        train_ratio: Training set fraction (default 0.70)
        val_ratio: Validation set fraction (default 0.15)
        test_ratio: Test set fraction (default 0.15)
        random_state: Random seed for reproducibility
        
    Returns:
        Tuple of (train_df, val_df, test_df) DataFrames
        
    Raises:
        FileNotFoundError: If golden directory doesn't exist
        ValueError: If no valid records could be extracted
        
    Example:
        >>> train_df, val_df, test_df = prepare_registry_training_splits()
        >>> train_df.to_csv("data/ml_training/registry_train.csv", index=False)
    """
    # Resolve golden directory
    if golden_dir is None:
        candidates = [
            Path("data/knowledge/golden_extractions_final"),
            Path("data/knowledge/golden_extractions_scrubbed"),
            Path("data/knowledge/golden_extractions"),
        ]
        for candidate in candidates:
            if candidate.exists():
                golden_dir = candidate
                break
        else:
            raise FileNotFoundError(
                "No golden extractions directory found. "
                "Expected one of: " + ", ".join(str(c) for c in candidates)
            )
    else:
        golden_dir = Path(golden_dir)
    
    if not golden_dir.exists():
        raise FileNotFoundError(f"Golden directory not found: {golden_dir}")
    
    logger.info(f"Loading golden JSONs from: {golden_dir}")
    
    # Extract records
    records, stats = extract_records_from_golden_dir(golden_dir)
    
    if not records:
        raise ValueError(
            f"No valid records extracted. Stats: "
            f"total={stats['total_files']}, "
            f"no_text={stats['skipped_no_text']}, "
            f"no_registry={stats['skipped_no_registry']}, "
            f"empty_labels={stats['skipped_empty_labels']}"
        )
    
    logger.info(
        f"Extracted {len(records)} records from {stats['total_files']} files"
    )
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Filter rare labels
    df, remaining_labels, dropped = filter_rare_labels(
        df, ALL_PROCEDURE_LABELS, min_count=min_label_count
    )
    
    logger.info(f"Using {len(remaining_labels)} labels after filtering")
    
    # Perform stratified split
    train_df, val_df, test_df = stratified_split(
        df,
        label_columns=remaining_labels,
        group_column="encounter_id",
        train_size=train_ratio,
        val_size=val_ratio,
        test_size=test_ratio,
        random_state=random_state,
    )
    
    # Log split statistics
    logger.info(
        f"Split complete: train={len(train_df)}, "
        f"val={len(val_df)}, test={len(test_df)}"
    )
    
    return train_df, val_df, test_df


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Command-line interface for registry data preparation."""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    
    parser = argparse.ArgumentParser(
        description="Prepare registry-first ML training data from golden JSONs"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Golden extractions directory",
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
        help="Prefix for output files",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=5,
        help="Minimum label count",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    
    args = parser.parse_args()
    
    train_df, val_df, test_df = prepare_registry_training_splits(
        golden_dir=args.input_dir,
        min_label_count=args.min_count,
        random_state=args.seed,
    )
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    train_df.to_csv(args.output_dir / f"{args.prefix}_train.csv", index=False)
    val_df.to_csv(args.output_dir / f"{args.prefix}_val.csv", index=False)
    test_df.to_csv(args.output_dir / f"{args.prefix}_test.csv", index=False)
    
    print(f"Written to {args.output_dir}:")
    print(f"  {args.prefix}_train.csv ({len(train_df)} rows)")
    print(f"  {args.prefix}_val.csv ({len(val_df)} rows)")
    print(f"  {args.prefix}_test.csv ({len(test_df)} rows)")


if __name__ == "__main__":
    main()
