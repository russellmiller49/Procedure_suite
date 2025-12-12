import pandas as pd
import csv
import os

# Configuration
DATA_DIR = "data/ml_training/cleaned_v5"  # Adjust if your files are in a different directory
FILES = {
    "train": "registry_train_clean.csv",
    "val": "registry_val_clean.csv",
    "test": "registry_test_clean.csv"
}

def fix_and_standardize():
    print(f"Starting fixes in {DATA_DIR}...")
    
    # 1. Load Validation Set and Apply Patch
    val_path = os.path.join(DATA_DIR, FILES["val"])
    if os.path.exists(val_path):
        print(f"Patching {FILES['val']}...")
        
        # Load with explicit types to avoid warnings
        df_val = pd.read_csv(val_path, dtype={'verified_cpt_codes': str})
        
        # Locate the specific row: original_index 4.0 from golden_034.json
        mask = (
            (df_val['original_index'] == 4.0) & 
            (df_val['source_file'] == 'golden_034.json')
        )
        
        if mask.any():
            # Apply the fix: Set navigational_bronchoscopy to 0
            df_val.loc[mask, 'navigational_bronchoscopy'] = 0
            print(f"  - Fixed Row {df_val.index[mask][0]}: Set navigational_bronchoscopy = 0 for Christopher Hayes.")
        else:
            print("  - WARNING: Target row for patching not found.")
            
        # Save back to disk
        save_standardized(df_val, val_path)
    else:
        print(f"  - Error: {FILES['val']} not found.")

    # 2. Standardize Train and Test Sets (Type Casting & Quoting)
    for name in ["train", "test"]:
        file_name = FILES[name]
        file_path = os.path.join(DATA_DIR, file_name)
        
        if os.path.exists(file_path):
            print(f"Standardizing {file_name}...")
            # Force verified_cpt_codes to string on load
            df = pd.read_csv(file_path, dtype={'verified_cpt_codes': str})
            save_standardized(df, file_path)
        else:
            print(f"  - Error: {file_name} not found.")

    print("\n✅ All critical fixes applied.")

def save_standardized(df, path):
    """
    Saves the dataframe ensuring:
    1. verified_cpt_codes is treated as a string (preserving "31647" vs "31630,32551")
    2. All non-numeric fields are quoted to prevent parsing errors
    """
    # Ensure CPT codes are string and handle NaNs
    df['verified_cpt_codes'] = df['verified_cpt_codes'].fillna('').astype(str)
    
    # Remove any trailing '.0' from CPTs that might have been inferred as floats previously
    df['verified_cpt_codes'] = df['verified_cpt_codes'].apply(
        lambda x: x.replace('.0', '') if x.endswith('.0') and ',' not in x else x
    )

    # Save with quoting enabled for non-numeric fields
    df.to_csv(
        path, 
        index=False, 
        quoting=csv.QUOTE_NONNUMERIC # Forces quotes around strings
    )
    print(f"  - Saved {os.path.basename(path)} (CPT codes standardized, text quoted).")

if __name__ == "__main__":
    fix_and_standardize()