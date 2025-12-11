import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
import os

# --- Configuration ---
DATA_DIR = "data/ml_training"
OUTPUT_DIR = "data/ml_training/cleaned_v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define label columns based on your schema (excluding metadata)
LABEL_COLS = [
    'diagnostic_bronchoscopy', 'bal', 'bronchial_wash', 'brushings', 
    'endobronchial_biopsy', 'transbronchial_biopsy', 'transbronchial_cryobiopsy', 
    'tbna_conventional', 'linear_ebus', 'radial_ebus', 'navigational_bronchoscopy', 
    'therapeutic_aspiration', 'foreign_body_removal', 'airway_dilation', 
    'airway_stent', 'thermal_ablation', 'cryotherapy', 'mechanical_debulking', 
    'brachytherapy_catheter', 'blvr', 'peripheral_ablation', 'bronchial_thermoplasty', 
    'whole_lung_lavage', 'rigid_bronchoscopy', 'photodynamic_therapy', 
    'thoracentesis', 'chest_tube', 'ipc', 'medical_thoracoscopy', 
    'pleural_biopsy', 'pleurodesis', 'fibrinolytic_therapy'
]

def load_data():
    print("Loading datasets...")
    # Load all existing splits
    df_train = pd.read_csv(f"{DATA_DIR}/registry_train.csv")
    df_test = pd.read_csv(f"{DATA_DIR}/registry_test.csv")
    
    # Try loading edge if it exists, otherwise ignore
    try:
        df_edge = pd.read_csv(f"{DATA_DIR}/registry_edge_cases.csv")
        df_edge['original_split'] = 'edge'
    except FileNotFoundError:
        df_edge = pd.DataFrame()
        
    df_train['original_split'] = 'train'
    df_test['original_split'] = 'test'

    # Load mapping file to get source_file (Patient/Case ID)
    df_flat = pd.read_csv(f"{DATA_DIR}/train_flat.csv")
    
    # Create a mapping dictionary: note_text -> source_file
    # We drop duplicates in map to avoid expansion
    text_to_source = df_flat.drop_duplicates('note_text').set_index('note_text')['source_file'].to_dict()
    
    return pd.concat([df_train, df_test, df_edge], ignore_index=True), text_to_source

def clean_data(df, text_to_source):
    print(f"Initial row count: {len(df)}")

    # 1. Map source_file
    df['source_file'] = df['note_text'].map(text_to_source)
    
    # Handle missing source_files (if note wasn't in train_flat)
    # We assign them a unique ID based on the note hash so they don't leak
    missing_mask = df['source_file'].isna()
    print(f"Rows missing source_file mapping: {missing_mask.sum()}")
    df.loc[missing_mask, 'source_file'] = df.loc[missing_mask, 'note_text'].apply(lambda x: f"unknown_{hash(x)}")

    # 2. Remove Garbage Rows
    # Drop if note_text is NaN
    df = df.dropna(subset=['note_text'])
    
    # Drop rows with no CPT AND all zero labels (ghost rows)
    labels_sum = df[LABEL_COLS].sum(axis=1)
    garbage_mask = (df['verified_cpt_codes'].isna()) & (labels_sum == 0)
    df = df[~garbage_mask]
    print(f"Row count after removing garbage: {len(df)}")

    # 3. Deduplicate and Fix Inconsistencies
    # We group by note_text and source_file. 
    # Logic: Take the 'max' of labels (if it was 1 in any duplicate, it's 1 now).
    # Logic: Take the first 'verified_cpt_codes' found.
    
    agg_dict = {col: 'max' for col in LABEL_COLS}
    agg_dict['verified_cpt_codes'] = 'first'
    agg_dict['source_file'] = 'first' # Should be same for grouping anyway
    
    # Grouping by note_text mainly, but keeping source_file aligned
    df_clean = df.groupby('note_text', as_index=False).agg(agg_dict)
    
    print(f"Row count after deduplication: {len(df_clean)}")
    return df_clean

def split_by_patient(df):
    print("Splitting data by source_file (Patient Level)...")
    
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
    
    # Split 1: Separate Train vs (Test + Val)
    train_idx, temp_idx = next(splitter.split(df, groups=df['source_file']))
    train_set = df.iloc[train_idx]
    temp_set = df.iloc[temp_idx]
    
    # Split 2: Separate Test vs Val (50/50 of the temp set)
    val_splitter = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=42)
    val_idx, test_idx = next(val_splitter.split(temp_set, groups=temp_set['source_file']))
    
    val_set = temp_set.iloc[val_idx]
    test_set = temp_set.iloc[test_idx]
    
    return train_set, val_set, test_set

def save_splits(train, val, test):
    print(f"Saving to {OUTPUT_DIR}...")
    print(f"Train size: {len(train)} notes")
    print(f"Val size:   {len(val)} notes")
    print(f"Test size:  {len(test)} notes")
    
    train.to_csv(f"{OUTPUT_DIR}/registry_train_clean.csv", index=False)
    val.to_csv(f"{OUTPUT_DIR}/registry_val_clean.csv", index=False)
    test.to_csv(f"{OUTPUT_DIR}/registry_test_clean.csv", index=False)
    print("Done.")

if __name__ == "__main__":
    # Load
    master_df, mapping = load_data()
    
    # Clean & Deduplicate
    df_clean = clean_data(master_df, mapping)
    
    # Split by Patient (source_file)
    train_df, val_df, test_df = split_by_patient(df_clean)
    
    # Verify no leakage
    train_patients = set(train_df['source_file'].unique())
    test_patients = set(test_df['source_file'].unique())
    overlap = train_patients.intersection(test_patients)
    
    if len(overlap) == 0:
        print("SUCCESS: No patient overlap between Train and Test.")
    else:
        print(f"WARNING: Leakage detected! {len(overlap)} overlapping patients.")
        
    # Save
    save_splits(train_df, val_df, test_df)