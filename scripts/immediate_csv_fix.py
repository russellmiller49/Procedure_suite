import pandas as pd
import csv
import os

# Configuration: Paths to your existing files
FILES = {
    "val": "data/ml_training/cleaned_v5/registry_val_clean.csv",
    "train": "data/ml_training/cleaned_v5/registry_train_clean.csv",
    "test": "data/ml_training/cleaned_v5/registry_test_clean.csv"
}

def fix_csvs():
    # 1. Fix Validation Set (Label Error)
    if os.path.exists(FILES['val']):
        print(f"Patching {FILES['val']}...")
        # Load forcing string type for CPTs to avoid "31647" (int) vs "31647,31648" (obj) issues
        df_val = pd.read_csv(FILES['val'], dtype={'verified_cpt_codes': str})
        
        # TARGET: Patient Christopher Hayes (golden_034.json, original_index 4.0)
        # Note: We use source_file/original_index as reliable identifiers
        mask = (df_val['source_file'] == 'golden_034.json') & (df_val['original_index'] == 4.0)
        
        if mask.any():
            print("  - Found Christopher Hayes row. Correcting navigational_bronchoscopy (1 -> 0).")
            df_val.loc[mask, 'navigational_bronchoscopy'] = 0
        else:
            print("  - WARNING: Christopher Hayes row not found. Skipping patch.")
            
        save_safely(df_val, FILES['val'])

    # 2. Fix Train and Test Sets (Type & Quoting)
    for name in ['train', 'test']:
        path = FILES[name]
        if os.path.exists(path):
            print(f"Standardizing {path}...")
            try:
                df = pd.read_csv(path, dtype={'verified_cpt_codes': str})
                save_safely(df, path)
            except Exception as e:
                print(f"  - CRITICAL ERROR reading {path}: {e}")
                print("    If this file is truncated, you MUST regenerate it using the updated pipeline below.")

def save_safely(df, path):
    """Saves with strict quoting to prevent CSV structure breakage."""
    # Ensure verified_cpt_codes is string (fills NaNs with empty string)
    if 'verified_cpt_codes' in df.columns:
        df['verified_cpt_codes'] = df['verified_cpt_codes'].fillna('').astype(str)
        # Clean up any accidental ".0" from float inference
        df['verified_cpt_codes'] = df['verified_cpt_codes'].apply(
            lambda x: x.replace('.0', '') if x.endswith('.0') and ',' not in x else x
        )

    # QUOTE_NONNUMERIC ensures all text fields (notes, lists of codes) are wrapped in quotes
    df.to_csv(path, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print(f"  - Saved {os.path.basename(path)} (Types standardized, Quoting enforced).")

if __name__ == "__main__":
    fix_csvs()