import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
import os
import json

# CONFIG
DATA_DIR = "data/ml_training/cleaned_v2"
OUTPUT_DIR = "data/ml_training/cleaned_v3_balanced"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_prep():
    print("Loading data...")
    # Load all 3 splits and combine
    df_list = []
    for split in ['train', 'val', 'test']:
        p = f"{DATA_DIR}/registry_{split}_clean.csv"
        if os.path.exists(p):
            df_list.append(pd.read_csv(p))

    df_all = pd.concat(df_list, ignore_index=True)
    return df_all

def main():
    df_all = load_and_prep()

    # Identify labels
    label_cols = [c for c in df_all.columns if c not in ['note_text', 'verified_cpt_codes', 'source_file', 'original_split']]

    # 1. DROP EMPTY COLUMNS
    global_sums = df_all[label_cols].sum()
    empty_cols = global_sums[global_sums == 0].index.tolist()
    if empty_cols:
        print(f"Dropping globally empty labels: {empty_cols}")
        df_all = df_all.drop(columns=empty_cols)
        label_cols = [c for c in label_cols if c not in empty_cols]

    # 2. IDENTIFY SINGLE-SOURCE LABELS (CRITICAL FIX)
    # If a label exists in ONLY one source_file, that file MUST go to Train.
    forced_train_files = set()

    print("\nChecking for single-source labels...")
    for col in label_cols:
        pos_rows = df_all[df_all[col] == 1]
        unique_sources = pos_rows['source_file'].unique()

        if len(unique_sources) == 1:
            source = unique_sources[0]
            print(f"  [FORCE TRAIN] Label '{col}' found only in {source}. Locking to Train.")
            forced_train_files.add(source)

    # Separate Forced Data from Mutable Data
    df_forced = df_all[df_all['source_file'].isin(forced_train_files)]
    df_mutable = df_all[~df_all['source_file'].isin(forced_train_files)]

    print(f"Locked {len(df_forced)} rows to Train. Optimizing split for remaining {len(df_mutable)} rows...")

    # 3. OPTIMIZE SPLIT (on mutable data only)
    best_score = -1
    best_seed = -1
    best_splits = None

    # Iterate 1000 seeds
    for seed in range(1000):
        # Split 1: Train vs Rest
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=seed)
        train_idx, rest_idx = next(splitter.split(df_mutable, groups=df_mutable['source_file']))

        train_mutable = df_mutable.iloc[train_idx]
        rest_set = df_mutable.iloc[rest_idx]

        # Split 2: Rest -> Val/Test
        val_splitter = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed)
        val_idx, test_idx = next(val_splitter.split(rest_set, groups=rest_set['source_file']))

        val_set = rest_set.iloc[val_idx]
        test_set = rest_set.iloc[test_idx]

        # Combine Forced Train with Mutable Train
        full_train = pd.concat([df_forced, train_mutable])

        # Scoring: Count rare labels present in Val OR Test
        score = 0
        for col in label_cols:
            total_count = df_all[col].sum()
            if total_count < 300: # Focus on rare stuff
                # Check representation
                has_train = full_train[col].sum() > 0
                has_val = val_set[col].sum() > 0
                has_test = test_set[col].sum() > 0

                # We prioritize Train existence first (critical), then Val/Test
                if has_train:
                    if has_val: score += 1
                    if has_test: score += 1

        if score > best_score:
            best_score = score
            best_seed = seed
            best_splits = (full_train, val_set, test_set)

    print(f"Found best split with seed {best_seed} (Score: {best_score})")
    train_final, val_final, test_final = best_splits

    # 4. VERIFY AND SAVE
    print("\n--- Final Distribution of Rare Labels ---")
    print(f"{'Label':<30} | {'Train':<5} | {'Val':<5} | {'Test':<5}")
    rare_labels = [l for l in label_cols if df_all[l].sum() < 300]
    for l in rare_labels:
        print(f"{l:<30} | {train_final[l].sum():<5} | {val_final[l].sum():<5} | {test_final[l].sum():<5}")

    print(f"\nSaving to {OUTPUT_DIR}...")
    train_final.to_csv(f"{OUTPUT_DIR}/registry_train_clean.csv", index=False)
    val_final.to_csv(f"{OUTPUT_DIR}/registry_val_clean.csv", index=False)
    test_final.to_csv(f"{OUTPUT_DIR}/registry_test_clean.csv", index=False)

    # Save Label Def
    with open(f"{OUTPUT_DIR}/registry_label_fields.json", "w") as f:
        json.dump(label_cols, f, indent=2)

    print("Done.")

if __name__ == "__main__":
    main()
