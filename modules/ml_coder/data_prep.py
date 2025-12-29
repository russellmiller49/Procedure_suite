"""
Data preparation module for ML coder training.

Builds clean training CSVs from golden JSONs with patient-level splitting
to support Silver Standard training (Train on Synthetic+Real, Test on Real).

IMPORTANT: This module uses HYBRID LABELING to handle:
1. CPT bundling rules (e.g., BAL bundled into biopsy codes)
2. Schema drift between v0.4 (top-level cpt_codes) and v2.0 (nested billing)
3. Anatomy-specific code mapping (31xxx=airway, 32xxx=pleural)
"""

from __future__ import annotations

import glob
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Allow running this file directly
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

GOLDEN_DIR = Path("data/knowledge/golden_extractions")
EDGE_SOURCE_NAME = "synthetic_edge_case_notes_with_registry.jsonl"
KB_PATH = _REPO_ROOT / "data" / "knowledge" / "ip_coding_billing_v2_9.json"

# Old/low-quality source files to exclude.
EXCLUDED_SOURCE_PREFIXES = {
    "synthetic_notes_with_CPT",       # Old CSV-based data
    "synthetic_CPT_corrected",        # Old corrected data
    "recovered_metadata",             # Recovery artifacts
}


def _load_valid_ip_codes() -> Set[str]:
    """
    Load VALID_IP_CODES set from the knowledge base file.
    
    Uses scripts/code_validation.py logic to extract billable codes
    from data/knowledge/ip_coding_billing_v2_9.json.
    """
    try:
        from scripts.code_validation import build_valid_ip_codes
        
        if not KB_PATH.exists():
            # Fallback: return empty set if KB file doesn't exist
            return set()
        
        valid_codes, _ = build_valid_ip_codes(
            KB_PATH,
            keep_addon_plus=False,
            include_reference_codes=False,
        )
        return valid_codes
    except Exception as e:
        # Fallback: return empty set on any error
        import warnings
        warnings.warn(f"Failed to load VALID_IP_CODES from {KB_PATH}: {e}")
        return set()


# Valid IP codes set - built from knowledge base file
VALID_IP_CODES: Set[str] = _load_valid_ip_codes()

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


# =============================================================================
# HYBRID LABELING: CPT + Text Regex
# =============================================================================
# These functions handle CPT bundling rules and schema drift to generate
# accurate clinical labels from billing data + procedure note text.


def _normalize_cpt_codes(entry: Dict[str, Any]) -> Set[str]:
    """
    Extract and normalize CPT codes from both v0.4 and v2.0 schema formats.

    Handles:
    - v0.4: Top-level `cpt_codes` list of integers
    - v2.0: Nested `registry_entry.billing.cpt_codes` list of objects

    Returns:
        Set of CPT code strings (e.g., {"31653", "31627", "31624"})
    """
    cpts_set: Set[str] = set()

    # Check top-level simple list (v0.4 format)
    if "cpt_codes" in entry and isinstance(entry["cpt_codes"], list):
        for c in entry["cpt_codes"]:
            if isinstance(c, (int, str)):
                cpts_set.add(str(c))

    # Check nested registry billing objects (v2.0 format)
    registry = entry.get("registry_entry", {})
    if isinstance(registry, dict) and "billing" in registry:
        billing = registry["billing"]
        if isinstance(billing, dict):
            billing_codes = billing.get("cpt_codes", [])
            for item in billing_codes:
                if isinstance(item, dict):
                    code = item.get("code", "")
                    if code:
                        cpts_set.add(str(code))
                elif isinstance(item, (int, str)):
                    cpts_set.add(str(item))

    # Also check registry_entry.cpt_codes if present (some legacy formats)
    if isinstance(registry, dict) and "cpt_codes" in registry:
        reg_codes = registry["cpt_codes"]
        if isinstance(reg_codes, list):
            for c in reg_codes:
                if isinstance(c, (int, str)):
                    cpts_set.add(str(c))

    return cpts_set


def get_clinical_labels(entry: Dict[str, Any], text: str) -> Dict[str, int]:
    """
    Generate clinical labels using Hybrid Logic (CPT + Text Regex).

    This handles:
    1. CPT Bundling: Minor procedures (BAL) may be missing from billing even
       though they were clinically performed (bundled into major procedures).
    2. Schema Drift: Different JSON versions have different CPT code locations.
    3. Anatomy Mismatch: Distinguishes pleural (32xxx) vs airway (31xxx) codes.

    Args:
        entry: The full entry dict from golden JSON
        text: The procedure note text

    Returns:
        Dict mapping procedure field names to 0/1 labels
    """
    text_lower = text.lower() if text else ""
    cpts_set = _normalize_cpt_codes(entry)

    labels: Dict[str, int] = {}

    # =========================================================================
    # PLEURAL DETECTION (Must check first - prevents cross-contamination)
    # =========================================================================
    # 32xxx codes are Pleural procedures
    is_pleural_code = any(
        c.startswith("326") or c.startswith("325") or c.startswith("324")
        for c in cpts_set
    )
    is_pleural_text = bool(re.search(
        r"medical thoracoscopy|pleuroscopy|pleural biopsy|thoracoscopy.*biopsy|"
        r"rigid thoracoscopy|semi-rigid thoracoscopy",
        text_lower
    ))
    is_pleural_case = is_pleural_code or is_pleural_text

    # --- Medical Thoracoscopy ---
    labels["medical_thoracoscopy"] = 1 if (
        "32601" in cpts_set or "32606" in cpts_set or "32609" in cpts_set or
        is_pleural_text
    ) else 0

    # --- Pleural Biopsy ---
    labels["pleural_biopsy"] = 1 if (
        "32609" in cpts_set or
        bool(re.search(r"pleural biopsy|biopsy.*pleura|parietal pleura.*biopsy", text_lower))
    ) else 0

    # --- Thoracentesis ---
    labels["thoracentesis"] = 1 if (
        "32554" in cpts_set or "32555" in cpts_set or
        bool(re.search(r"\bthoracentesis\b|thoracentesis performed", text_lower))
    ) else 0

    # --- Chest Tube ---
    labels["chest_tube"] = 1 if (
        "32551" in cpts_set or
        bool(re.search(r"chest tube|tube thoracostomy", text_lower))
    ) else 0

    # --- IPC (Tunneled Pleural Catheter) ---
    labels["ipc"] = 1 if (
        "32550" in cpts_set or
        bool(re.search(r"\bipc\b|pleurx|tunneled.*catheter|tunneled pleural", text_lower))
    ) else 0

    # --- Pleurodesis ---
    labels["pleurodesis"] = 1 if (
        "32560" in cpts_set or
        bool(re.search(r"pleurodesis|talc.*poudrage|chemical pleurodesis", text_lower))
    ) else 0

    # --- Fibrinolytic Therapy ---
    labels["fibrinolytic_therapy"] = 1 if (
        bool(re.search(r"fibrinolytic|tpa.*pleural|alteplase.*pleural|streptokinase", text_lower))
    ) else 0

    # =========================================================================
    # BRONCHOSCOPY / AIRWAY PROCEDURES
    # =========================================================================
    # Only set airway labels if NOT a purely pleural case

    # --- BAL (Fixing the Bundling Error) ---
    # BAL (31624) is often bundled into biopsy codes even though it was performed
    labels["bal"] = 1 if (
        "31624" in cpts_set or
        bool(re.search(r"\bbal\b|bronchoalveolar lavage|mini-bal|mini bal", text_lower))
    ) else 0

    # --- Bronchial Wash ---
    labels["bronchial_wash"] = 1 if (
        "31622" in cpts_set or
        bool(re.search(r"bronchial wash|bronchial washing", text_lower))
    ) else 0

    # --- Brushings ---
    labels["brushings"] = 1 if (
        "31623" in cpts_set or
        bool(re.search(r"\bbrushings?\b|bronchial brush|cytology brush", text_lower))
    ) else 0

    # --- Endobronchial Biopsy ---
    labels["endobronchial_biopsy"] = 1 if (
        "31625" in cpts_set or
        bool(re.search(r"endobronchial biopsy|ebb\b|mucosal biopsy", text_lower))
    ) and not is_pleural_case else 0

    # --- Transbronchial Biopsy (Preventing Pleural Cross-Contamination) ---
    has_tbbx_code = any(c in cpts_set for c in ["31628", "31629", "31632", "31633"])
    has_tbbx_text = bool(re.search(
        r"transbronchial biopsy|tbbx\b|forceps biopsy|transbronchial lung biopsy",
        text_lower
    ))
    labels["transbronchial_biopsy"] = 1 if (
        (has_tbbx_code or has_tbbx_text) and not is_pleural_case
    ) else 0

    # --- Transbronchial Cryobiopsy ---
    labels["transbronchial_cryobiopsy"] = 1 if (
        "31629" in cpts_set or "31633" in cpts_set or
        bool(re.search(r"cryobiopsy|cryo.*biopsy|transbronchial cryo", text_lower))
    ) and not is_pleural_case else 0

    # --- TBNA Conventional ---
    labels["tbna_conventional"] = 1 if (
        "31629" in cpts_set or  # Note: 31629 can be TBNA with fluoro
        bool(re.search(r"\btbna\b|transbronchial needle aspir", text_lower))
    ) and not is_pleural_case else 0

    # --- Linear EBUS ---
    labels["linear_ebus"] = 1 if (
        any(c in cpts_set for c in ["31652", "31653", "31654"]) or
        bool(re.search(r"linear ebus|ebus-tbna|ebus tbna|endobronchial ultrasound.*tbna", text_lower))
    ) else 0

    # --- Radial EBUS ---
    labels["radial_ebus"] = 1 if (
        bool(re.search(r"radial ebus|r-ebus|rebus\b|radial probe", text_lower))
    ) else 0

    # --- Navigational Bronchoscopy ---
    labels["navigational_bronchoscopy"] = 1 if (
        "31627" in cpts_set or
        bool(re.search(
            r"navigation|ion\s+bronchoscopy|superDimension|monarch|"
            r"electromagnetic navigation|emn\b|robotic bronch",
            text_lower
        ))
    ) else 0

    # --- Fiducial Placement ---
    labels["fiducial_placement"] = 1 if (
        "31626" in cpts_set or
        bool(re.search(r"fiducial|gold marker|gold seed|fiduciary marker", text_lower))
    ) else 0

    # --- Thermal Ablation (often bundled/unbilled) ---
    labels["thermal_ablation"] = 1 if (
        "31641" in cpts_set or
        bool(re.search(r"\bapc\b|argon plasma|electrocautery|thermal ablation|laser ablation", text_lower))
    ) else 0

    # --- Cryotherapy ---
    labels["cryotherapy"] = 1 if (
        "31641" in cpts_set or  # Can be used for cryo debulking
        bool(re.search(r"cryotherapy|cryo.*debulk|cryospray|spray cryo", text_lower))
    ) else 0

    # --- Airway Dilation ---
    labels["airway_dilation"] = 1 if (
        "31630" in cpts_set or "31631" in cpts_set or
        bool(re.search(r"balloon dilation|airway dilation|bronchial dilation|dilated.*airway", text_lower))
    ) else 0

    # --- Airway Stent ---
    labels["airway_stent"] = 1 if (
        "31636" in cpts_set or "31637" in cpts_set or
        bool(re.search(r"airway stent|bronchial stent|tracheal stent|stent.*placed|dumon", text_lower))
    ) else 0

    # --- Foreign Body Removal ---
    labels["foreign_body_removal"] = 1 if (
        "31635" in cpts_set or
        bool(re.search(r"foreign body|stent removal|removed.*stent|fb removal", text_lower))
    ) else 0

    # --- Therapeutic Aspiration ---
    labels["therapeutic_aspiration"] = 1 if (
        bool(re.search(r"therapeutic aspiration|mucus plug.*removal|clot.*aspir", text_lower))
    ) else 0

    # --- BLVR ---
    labels["blvr"] = 1 if (
        "31647" in cpts_set or "31651" in cpts_set or
        bool(re.search(r"\bblvr\b|bronchoscopic lung volume reduction|valve.*placement|zephyr valve", text_lower))
    ) else 0

    # --- Peripheral Ablation ---
    labels["peripheral_ablation"] = 1 if (
        bool(re.search(r"peripheral ablation|microwave ablation|mwa\b|rfa\b|radiofrequency ablation", text_lower))
    ) else 0

    # --- Bronchial Thermoplasty ---
    labels["bronchial_thermoplasty"] = 1 if (
        "31660" in cpts_set or "31661" in cpts_set or
        bool(re.search(r"bronchial thermoplasty|\bbt\b.*asthma|thermoplasty", text_lower))
    ) else 0

    # --- Whole Lung Lavage ---
    labels["whole_lung_lavage"] = 1 if (
        "31624" in cpts_set or  # Can be billed for WLL
        bool(re.search(r"whole lung lavage|wll\b|pap.*lavage|therapeutic lavage", text_lower))
    ) else 0

    # --- Rigid Bronchoscopy ---
    labels["rigid_bronchoscopy"] = 1 if (
        "31622" in cpts_set or  # Base bronch code often used with rigid
        bool(re.search(r"rigid bronchoscopy|rigid scope|rigid.*bronch", text_lower))
    ) else 0

    # =========================================================================
    # DIAGNOSTIC BRONCHOSCOPY (Derived flag)
    # =========================================================================
    # Set if any bronchoscopic procedure detected AND it's not purely pleural
    bronch_indicators = [
        labels.get("linear_ebus", 0),
        labels.get("radial_ebus", 0),
        labels.get("navigational_bronchoscopy", 0),
        labels.get("transbronchial_biopsy", 0),
        labels.get("transbronchial_cryobiopsy", 0),
        labels.get("blvr", 0),
        labels.get("peripheral_ablation", 0),
        labels.get("thermal_ablation", 0),
        labels.get("cryotherapy", 0),
        labels.get("airway_dilation", 0),
        labels.get("airway_stent", 0),
        labels.get("foreign_body_removal", 0),
        labels.get("bronchial_thermoplasty", 0),
        labels.get("whole_lung_lavage", 0),
        labels.get("rigid_bronchoscopy", 0),
        labels.get("bal", 0),
        labels.get("bronchial_wash", 0),
        labels.get("brushings", 0),
        labels.get("endobronchial_biopsy", 0),
        labels.get("tbna_conventional", 0),
        labels.get("fiducial_placement", 0),
        labels.get("therapeutic_aspiration", 0),
    ]

    # Also check for generic bronchoscopy CPT codes or text
    has_bronch_code = any(c.startswith("316") for c in cpts_set)
    has_bronch_text = bool(re.search(r"bronchoscopy|bronchoscopic", text_lower))

    labels["diagnostic_bronchoscopy"] = 1 if (
        (any(bronch_indicators) or has_bronch_code or has_bronch_text)
        and not (is_pleural_case and not any(bronch_indicators))
    ) else 0

    return labels


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

def _build_registry_dataframe(use_hybrid_labels: bool = True) -> pd.DataFrame:
    """Build a DataFrame from all extraction files with Silver Standard metadata.

    Extracts:
    - note_text
    - boolean procedure flags (using hybrid CPT + text approach)
    - is_synthetic: True if note is AI-generated
    - root_mrn: The base patient ID (groups Real + Synthetic variations)

    Args:
        use_hybrid_labels: If True, use get_clinical_labels() which handles CPT
            bundling rules and text regex fallback. If False, use only the
            registry-based extraction (legacy behavior).
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

            # --- HYBRID LABELING ---
            # Use CPT codes + text regex for robust label generation
            if use_hybrid_labels:
                # Hybrid approach: CPT codes + text regex (handles bundling)
                flags = get_clinical_labels(entry, text)

                # Also extract registry-based flags as fallback/supplement
                registry_flags = _extract_registry_booleans(registry)

                # Merge: prefer hybrid labels, but fill in any missing fields
                # from registry extraction (for procedures not in hybrid logic)
                for field in REGISTRY_TARGET_FIELDS:
                    if field not in flags:
                        flags[field] = registry_flags.get(field, 0)
                    # Also set to 1 if registry extraction found it (OR logic)
                    elif registry_flags.get(field, 0) == 1:
                        flags[field] = 1
            else:
                # Legacy behavior: only registry-based extraction
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