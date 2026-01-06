"""
Data preparation module for registry ML training.

Builds clean training CSVs from golden JSONs and existing registry data
with patient-level splitting to support Silver Standard training
(Train on Synthetic+Real, Test on Real).

Key design goals:
- Single Source of Truth: In production, labels are derived using the canonical implementation.
  Here, we map Golden JSON structured data (CPT codes + Registry Fields) into the target
  boolean schema found in registry_train.csv.
- Extraction-First: Uses structured evidence from JSONs as ground-truth labels for the
  synthetic partition.

Registry-First Alternative:
  For the registry-first approach that extracts labels directly from the nested
  registry_entry structure (rather than CPT-based derivation), use:

      from modules.ml_coder.registry_data_prep import prepare_registry_training_splits
      train_df, val_df, test_df = prepare_registry_training_splits()
"""

import glob
import json
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path

# Define the boolean procedure columns found in registry_train.csv
BOOLEAN_COLUMNS = [
    'diagnostic_bronchoscopy', 'bal', 'bronchial_wash', 'brushings',
    'endobronchial_biopsy', 'tbna_conventional', 'linear_ebus', 'radial_ebus',
    'navigational_bronchoscopy', 'transbronchial_biopsy',
    'transbronchial_cryobiopsy', 'therapeutic_aspiration',
    'foreign_body_removal', 'airway_dilation', 'airway_stent',
    'thermal_ablation', 'cryotherapy', 'blvr', 'peripheral_ablation',
    'whole_lung_lavage', 'rigid_bronchoscopy', 'thoracentesis', 'chest_tube',
    'ipc', 'medical_thoracoscopy', 'pleurodesis', 'fibrinolytic_therapy'
]

def derive_booleans_from_json(entry: dict) -> dict:
    """
    Derives boolean flags from a golden JSON entry using CPT codes
    and registry_entry fields to match the registry_train.csv schema.
    """
    # Normalize CPT codes to a set of integers
    raw_cpts = entry.get('cpt_codes', [])
    cpt_codes = set()
    for c in raw_cpts:
        try:
            cpt_codes.add(int(c))
        except (ValueError, TypeError):
            continue

    reg = entry.get('registry_entry', {})
    
    # Initialize row with 0s
    row = {col: 0 for col in BOOLEAN_COLUMNS}
    
    # --- Heuristic Mapping Logic based on CPTs and Registry Fields ---

    # 1. Diagnostic Bronchoscopy
    # Set to 1 if specific diagnostic bronchoscopy codes are present.
    # Note: BLVR (31647) and Therapeutic codes do not trigger this on their own.
    diagnostic_cpts = [
        31622, 31623, 31624, 31625, 31626, 31627, 31628, 31629, 
        31651, 31652, 31653, 31654
    ]
    if any(c in cpt_codes for c in diagnostic_cpts):
        row['diagnostic_bronchoscopy'] = 1

    # 2. BAL (31624)
    if 31624 in cpt_codes:
        row['bal'] = 1
        
    # 3. Bronchial Wash (31622 implies basic bronch, wash often bundled)
    if 31622 in cpt_codes:
        row['bronchial_wash'] = 1
        
    # 4. Brushings (31623)
    if 31623 in cpt_codes:
        row['brushings'] = 1
        
    # 5. Endobronchial Biopsy (31625)
    if 31625 in cpt_codes:
        row['endobronchial_biopsy'] = 1
        
    # 6. Transbronchial Biopsy (31628, 31632)
    if 31628 in cpt_codes or 31632 in cpt_codes:
        row['transbronchial_biopsy'] = 1

    # 7. Linear EBUS (31651, 31652, 31653)
    if any(c in cpt_codes for c in [31651, 31652, 31653]) or reg.get('linear_ebus_stations'):
        row['linear_ebus'] = 1
        
    # 8. TBNA Conventional (31629)
    # Logic: If 31629 is present AND Linear EBUS codes are NOT present, it is conventional.
    if 31629 in cpt_codes:
        if row['linear_ebus'] == 0:
            row['tbna_conventional'] = 1
            
    # 9. Radial EBUS (31654)
    if 31654 in cpt_codes or reg.get('nav_rebus_used') is True:
        row['radial_ebus'] = 1
        
    # 10. Navigational Bronchoscopy (31627)
    if 31627 in cpt_codes or reg.get('nav_platform'):
        row['navigational_bronchoscopy'] = 1
        
    # 11. Transbronchial Cryobiopsy
    # Distinct from TBBX in registry. Look for explicit registry flag or keyword.
    if reg.get('nav_cryobiopsy_for_nodule') is True:
        row['transbronchial_cryobiopsy'] = 1
        
    # 12. Therapeutic Aspiration (31645, 31646)
    if any(c in cpt_codes for c in [31645, 31646]):
        row['therapeutic_aspiration'] = 1
        
    # 13. Foreign Body Removal (31635)
    if 31635 in cpt_codes or reg.get('fb_object_type'):
        row['foreign_body_removal'] = 1
        
    # 14. Airway Dilation (31630, 31631, 31634)
    if any(c in cpt_codes for c in [31630, 31631, 31634]):
        row['airway_dilation'] = 1
        
    # 15. Airway Stent (31636, 31637, 31638)
    if any(c in cpt_codes for c in [31636, 31637, 31638]):
        row['airway_stent'] = 1
        
    # 16. Peripheral Ablation
    # Rely on the registry flag 'ablation_peripheral_performed'
    if reg.get('ablation_peripheral_performed') is True:
        row['peripheral_ablation'] = 1
        
    # 17. Thermal Ablation (Central)
    # 31641 is "Destruction of tumor". If not peripheral, assume central/thermal.
    elif 31641 in cpt_codes:
        row['thermal_ablation'] = 1
        
    # 18. Cryotherapy (Central)
    # Usually implies central airway treatment if not peripheral.
    # Check modality text.
    modality = str(reg.get('ablation_modality', '')).lower()
    if 'cryo' in modality and row['peripheral_ablation'] == 0:
        row['cryotherapy'] = 1
        # If it was caught by thermal_ablation logic above (via 31641), reset thermal if specific cryo column used?
        # Typically datasets distinguish them. For safety, we leave thermal=1 unless strictly exclusive.
        # Based on CSV row 6 (Cryoablation): Peripheral=1, Thermal=0, Cryo=0 (as it's peripheral).
        # This matches the logic above (elif 31641).
    
    # 19. BLVR (31647-31651)
    if any(c in cpt_codes for c in [31647, 31648, 31649, 31651]) or reg.get('blvr_valve_type'):
        row['blvr'] = 1
        
    # 20. Whole Lung Lavage (32997)
    if 32997 in cpt_codes or reg.get('wll_volume_instilled_l'):
        row['whole_lung_lavage'] = 1
        
    # 21. Rigid Bronchoscopy (31600, 31601)
    if 31600 in cpt_codes or 31601 in cpt_codes:
        row['rigid_bronchoscopy'] = 1
        
    # 22. Medical Thoracoscopy (32601)
    if 32601 in cpt_codes:
        row['medical_thoracoscopy'] = 1
        
    # 23. Pleurodesis (32650)
    if 32650 in cpt_codes or reg.get('pleurodesis_performed') is True:
        row['pleurodesis'] = 1
        
    # 24. Thoracentesis (32554, 32555)
    if 32554 in cpt_codes or 32555 in cpt_codes:
        row['thoracentesis'] = 1
        
    # 25. Chest Tube (32551)
    if 32551 in cpt_codes or str(reg.get('pleural_procedure_type')) == 'Chest Tube':
        row['chest_tube'] = 1

    # 26. IPC (32550)
    if 32550 in cpt_codes:
        row['ipc'] = 1
        
    # 27. Fibrinolytic Therapy (32560)
    if 32560 in cpt_codes:
        row['fibrinolytic_therapy'] = 1
        
    return row

def main():
    # 1. Load Real Data
    real_csv_path = 'data/ml_training/registry_train.csv'
    
    print(f"Loading real data from {real_csv_path}...")
    try:
        if os.path.exists(real_csv_path):
            df_real = pd.read_csv(real_csv_path)
        else:
            print(f"Warning: {real_csv_path} not found. Proceeding with empty real dataframe.")
            df_real = pd.DataFrame(columns=['note_text'] + BOOLEAN_COLUMNS)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # 2. Split Real Data (Train/Test)
    # Test set is purely Real data (Silver Standard methodology)
    if len(df_real) > 5:
        train_real, test_real = train_test_split(df_real, test_size=0.2, random_state=42)
    else:
        print("Warning: Not enough real data to split. Using all for training.")
        train_real = df_real
        test_real = pd.DataFrame(columns=df_real.columns)
    
    # 3. Load Synthetic Data (Golden JSONs)
    synthetic_rows = []
    # Search in the canonical golden extractions directory
    golden_dir = Path('data/knowledge/golden_extractions_final')
    json_files = glob.glob(str(golden_dir / 'golden_*.json'))
    
    print(f"Loading synthetic data from {len(json_files)} JSON files...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure data is a list
                if isinstance(data, dict):
                    data = [data]
                    
                for entry in data:
                    note_text = entry.get('note_text', '')
                    if not note_text: 
                        continue
                    
                    # Derive labels from structure
                    labels = derive_booleans_from_json(entry)
                    
                    row_data = {'note_text': note_text}
                    row_data.update(labels)
                    synthetic_rows.append(row_data)
        except Exception as e:
            print(f"Warning: Failed to process {json_file}: {e}")
                
    if synthetic_rows:
        df_synthetic = pd.DataFrame(synthetic_rows)
        # Fill missing columns in synthetic with 0
        for col in BOOLEAN_COLUMNS:
            if col not in df_synthetic.columns:
                df_synthetic[col] = 0
    else:
        print("Warning: No synthetic data found.")
        df_synthetic = pd.DataFrame(columns=['note_text'] + BOOLEAN_COLUMNS)

    # 4. Combine Synthetic + Real Train
    # Ensure column order matches
    cols = ['note_text'] + BOOLEAN_COLUMNS
    
    # Filter only columns that exist (intersection of schema and df)
    valid_cols = [c for c in cols if c in df_synthetic.columns]
    df_synthetic = df_synthetic[valid_cols]
    
    # Reindex real data to ensure matching columns
    train_real = train_real.reindex(columns=cols, fill_value=0)
    test_real = test_real.reindex(columns=cols, fill_value=0)
    df_synthetic = df_synthetic.reindex(columns=cols, fill_value=0)
    
    df_train_final = pd.concat([df_synthetic, train_real], ignore_index=True)
    
    # 5. Save Outputs
    output_dir = Path("processed_data")
    output_dir.mkdir(exist_ok=True)
    
    train_path = output_dir / 'train.csv'
    test_path = output_dir / 'test.csv'
    
    df_train_final.to_csv(train_path, index=False)
    test_real.to_csv(test_path, index=False)
    
    print("-" * 30)
    print(f"Processed {len(df_real)} real records and {len(df_synthetic)} synthetic records.")
    print(f"Train Set (Synthetic + 80% Real): {len(df_train_final)} rows.")
    print(f"Test Set (20% Real):              {len(test_real)} rows.")
    print("-" * 30)
    print(f"Files saved to {output_dir}")

if __name__ == '__main__':
    main()


# =============================================================================
# V2 Booleans Integration
# =============================================================================
# Import the canonical boolean field list and extraction function from
# modules/registry/v2_booleans.py for backward compatibility.

from modules.registry.v2_booleans import (
    PROCEDURE_BOOLEAN_FIELDS,
    extract_v2_booleans,
)

# Alias for backward compatibility with existing code
# Keep as list (not tuple) to match original PROCEDURE_BOOLEAN_FIELDS type
REGISTRY_TARGET_FIELDS = list(PROCEDURE_BOOLEAN_FIELDS)


def _extract_registry_booleans(entry: dict) -> dict:
    """Wrapper for extract_v2_booleans for backward compatibility.

    Args:
        entry: Registry entry dictionary from golden JSON.

    Returns:
        Dict mapping field names to 0/1 values.
    """
    return extract_v2_booleans(entry)


def _filter_rare_registry_labels(
    labels: list[list[int]],
    min_count: int = 5,
) -> tuple[list[list[int]], list[str]]:
    """Filter out labels with fewer than min_count positive examples.

    Args:
        labels: List of label vectors (each vector is a list of 0/1 ints).
        min_count: Minimum positive count required to keep a label.

    Returns:
        Tuple of (filtered_labels, kept_field_names).
    """
    if not labels:
        return [], []

    import numpy as np

    # Convert to array for easier computation
    arr = np.array(labels)
    n_labels = arr.shape[1] if arr.ndim > 1 else 0

    if n_labels == 0:
        return [], []

    # Count positives for each label
    counts = arr.sum(axis=0)

    # Find which labels to keep
    keep_mask = counts >= min_count
    kept_indices = np.where(keep_mask)[0]

    # Filter labels and get field names
    if len(kept_indices) == 0:
        return [], []

    filtered = arr[:, kept_indices].tolist()
    kept_names = [REGISTRY_TARGET_FIELDS[i] for i in kept_indices]

    return filtered, kept_names


# =============================================================================
# Registry-First Data Prep Re-exports
# =============================================================================
# Import registry-first functions for convenient access from this module.
# These are imported last to avoid circular import issues.

from .registry_data_prep import (
    prepare_registry_training_splits,
    RegistryLabelExtractor,
    ALL_PROCEDURE_LABELS,
    extract_records_from_golden_dir,
    stratified_split,
    filter_rare_labels,
)
