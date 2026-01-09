import pandas as pd
import os

# Paths
files = [
    "registry_human.csv", 
    "data/ml_training/registry_debulking_fixes.csv"
]

dfs = []
for f in files:
    if os.path.exists(f):
        print(f"Loading {f}...")
        dfs.append(pd.read_csv(f))
    else:
        print(f"Warning: {f} not found (skipping)")

if dfs:
    # Concatenate and drop duplicates (keeping the latest fix if IDs overlap)
    master = pd.concat(dfs, ignore_index=True)
    # Deduplicate by encounter_id, keeping the last (newest) entry
    if 'encounter_id' in master.columns:
        master = master.drop_duplicates(subset=['encounter_id'], keep='last')
    
    output_path = "data/ml_training/registry_human_MASTER.csv"
    master.to_csv(output_path, index=False)
    print(f"\n✅ Success! Combined {len(master)} human labels into {output_path}")
else:
    print("\n❌ No files found to merge.")