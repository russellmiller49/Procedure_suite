import pandas as pd
import re
import json
import os
import numpy as np

# Configuration
REGISTRY_TRAIN = "data/ml_training/registry_train.csv"
REGISTRY_TEST = "data/ml_training/registry_test.csv"
REGISTRY_EDGE = "data/ml_training/registry_edge_cases.csv"
TRAIN_CPT = "data/ml_training/train.csv"
LABEL_FILE = "data/ml_training/registry_label_fields.json"

# Regex Rules for Flag Generation
# Maps column_name -> regex_pattern
REGEX_MAP = {
    "linear_ebus": r"ebus|linear\s*ebus|station\s*\d",
    "rigid_bronchoscopy": r"rigid\s*bronch|jet\s*ventilation",
    "foreign_body_removal": r"foreign\s*body|peanut|object\s*removal",
    "bal": r"bal\b|bronchoalveolar\s*lavage",
    "bronchial_wash": r"bronchial\s*wash|washing",
    "brushings": r"brush",
    "endobronchial_biopsy": r"endobronchial\s*biopsy|ebb\b",
    "tbna_conventional": r"tbna\b|transbronchial\s*needle\s*aspiration",
    "radial_ebus": r"radial\s*ebus|radial\s*probe",
    "navigational_bronchoscopy": r"navigation|enb\b|monarch|ion\b|veran",
    "transbronchial_biopsy": r"transbronchial\s*biopsy|tbbx\b|tbb\b",
    "transbronchial_cryobiopsy": r"cryobiopsy",
    "therapeutic_aspiration": r"therapeutic\s*aspiration",
    "airway_dilation": r"dilation|balloon|dilator",
    "airway_stent": r"stent",
    "thermal_ablation": r"apc\b|argon\s*plasma|laser|electrocautery",
    "cryotherapy": r"cryotherapy|cryo\s*ablation|cryo\s*recanalization", 
    "blvr": r"valve|zephyr|spiration",
    "peripheral_ablation": r"microwave\s*ablation",
    "bronchial_thermoplasty": r"thermoplasty",
    "whole_lung_lavage": r"whole\s*lung\s*lavage",
    "thoracentesis": r"thoracentesis",
    "chest_tube": r"chest\s*tube|thoracostomy",
    "ipc": r"indwelling\s*pleural\s*catheter|ipc\b|pleurx",
    "medical_thoracoscopy": r"thoracoscopy|pleuroscopy",
    "pleurodesis": r"pleurodesis|talc",
    "fibrinolytic_therapy": r"tpa\b|dnase|fibrinolytic",
    "diagnostic_bronchoscopy": r"diagnostic\s*bronch|inspection"
}

def fix_registry_flags(df):
    """
    Regenerates binary flags (1/0) based on regex matches in 'note_text'.
    """
    print("  Regenerating flags based on text content...")
    for col, pattern in REGEX_MAP.items():
        if col in df.columns:
            # Set to 1 if pattern matches, else 0
            df[col] = df['note_text'].str.contains(pattern, case=False, na=False).astype(int)
    return df

def fix_metadata(df):
    """
    Backfills missing metadata for Ablation/other rows.
    """
    print("  Checking for missing metadata...")
    # Identify rows where source_file is missing or empty
    mask = df['source_file'].isna() | (df['source_file'] == '')
    
    missing_count = mask.sum()
    if missing_count > 0:
        print(f"  Found {missing_count} rows with missing metadata. Backfilling...")
        df.loc[mask, 'source_file'] = 'recovered_metadata'
        df.loc[mask, 'patient_mrn'] = 'UNKNOWN'
        # Assign a valid dummy date
        df.loc[mask, 'procedure_date'] = '2025-01-01'
    else:
        print("  No missing metadata found.")
        
    return df

def main():
    # --- Part 1: Fix Registry Data (Binary Classification) ---
    registry_files = [REGISTRY_TRAIN, REGISTRY_TEST, REGISTRY_EDGE]
    labels_found = set()
    
    for fpath in registry_files:
        if os.path.exists(fpath):
            print(f"\nProcessing Registry File: {fpath}")
            df = pd.read_csv(fpath)
            
            # Identify columns that match our regex map (potential labels)
            current_labels = [c for c in df.columns if c in REGEX_MAP]
            labels_found.update(current_labels)
            
            # Fix flags
            df = fix_registry_flags(df)
            
            # Save
            df.to_csv(fpath, index=False)
            print(f"  Saved {fpath} with {len(df)} rows.")
        else:
            print(f"\nWarning: {fpath} not found.")

    # --- Part 2: Fix CPT Train Data (Metadata) ---
    if os.path.exists(TRAIN_CPT):
        print(f"\nProcessing CPT Train File: {TRAIN_CPT}")
        df_train = pd.read_csv(TRAIN_CPT)
        
        # Check if necessary columns exist, if not add them
        for col in ['source_file', 'patient_mrn', 'procedure_date']:
            if col not in df_train.columns:
                df_train[col] = ''
                
        df_train = fix_metadata(df_train)
        df_train.to_csv(TRAIN_CPT, index=False)
        print(f"  Saved {TRAIN_CPT} with {len(df_train)} rows.")
    else:
        print(f"\nWarning: {TRAIN_CPT} not found.")

    # --- Part 3: Populate Schema ---
    print(f"\nPopulating {LABEL_FILE}...")
    # Convert set to sorted list
    sorted_labels = sorted(list(labels_found))
    
    with open(LABEL_FILE, 'w') as f:
        json.dump(sorted_labels, f, indent=2)
    
    print(f"  Wrote {len(sorted_labels)} labels to {LABEL_FILE}")
    print("  Labels:", sorted_labels)
    
    print("\nData Integrity Rescue Complete.")

if __name__ == "__main__":
    main()
