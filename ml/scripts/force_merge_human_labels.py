import pandas as pd
import argparse
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS  # noqa: E402
from ml.lib.ml_coder.registry_label_constraints import apply_label_constraints  # noqa: E402


_CONSTRAINT_LABELS = [
    "bal",
    "bronchial_wash",
    "transbronchial_cryobiopsy",
    "transbronchial_biopsy",
    "rigid_bronchoscopy",
    "tumor_debulking_non_thermal",
]


def force_merge(human_csv_path: str, target_dir: str):
    human_path = Path(human_csv_path)
    if not human_path.exists():
        logger.error(f"Human CSV not found: {human_path}")
        return

    logger.info(f"Loading human labels from {human_path}...")
    human_df = pd.read_csv(human_path)
    
    # Ensure encounter_id exists
    if "encounter_id" not in human_df.columns:
        logger.error("Human CSV missing 'encounter_id' column. Cannot merge.")
        return

    human_df["encounter_id"] = human_df["encounter_id"].astype(str).str.strip()

    # Clean human df: set index to encounter_id
    human_df = human_df.set_index("encounter_id")
    
    # Identify label columns (canonical only; avoid accidentally treating meta cols as labels)
    label_cols = [c for c in REGISTRY_LABELS if c in human_df.columns]
    
    # Filter human_df to just labels to avoid overwriting text/metadata accidentally
    human_labels = human_df[label_cols]
    
    total_updates = 0
    
    # Process each split
    for split_name in ["train", "val", "test"]:
        split_path = Path(target_dir) / f"registry_{split_name}.csv"
        if not split_path.exists():
            logger.warning(f"Skipping {split_name} (not found at {split_path})")
            continue
            
        logger.info(f"Processing {split_name} split...")
        split_df = pd.read_csv(split_path)
        
        if "encounter_id" not in split_df.columns:
            logger.warning(f"Split {split_name} missing 'encounter_id'. Skipping.")
            continue

        split_df["encounter_id"] = split_df["encounter_id"].astype(str).str.strip()
            
        # Set index for alignment
        split_df = split_df.set_index("encounter_id")
        
        # Find intersection of IDs
        common_ids = split_df.index.intersection(human_labels.index)
        
        if common_ids.empty:
            logger.info(f"  No overlapping IDs in {split_name}.")
        else:
            # Only update columns that exist in this split CSV.
            # (Prep may omit rare labels; force-merge shouldn't crash.)
            split_label_cols = [c for c in label_cols if c in split_df.columns]
            missing_cols = [c for c in label_cols if c not in split_df.columns]
            if missing_cols:
                logger.info(
                    f"  Note: {len(missing_cols)} label columns not present in {split_name} split; "
                    f"skipping those (e.g. {missing_cols[:5]})."
                )

            if not split_label_cols:
                logger.warning(f"  No canonical label columns found in {split_name} split to update.")
            else:
                # FORCE UPDATE: Overwrite split values with human values where IDs match
                split_df.update(human_labels[split_label_cols])

                # Re-apply deterministic constraints on updated rows to avoid
                # reintroducing known contradictions (e.g., debulking without rigid).
                constraint_cols = [c for c in _CONSTRAINT_LABELS if c in split_df.columns]
                if constraint_cols:
                    for eid in common_ids.tolist():
                        row = split_df.loc[eid]
                        note_text = str(row.get("note_text") or "")
                        labels = {c: int(row.get(c, 0)) for c in constraint_cols}
                        apply_label_constraints(labels, note_text=note_text, inplace=True)
                        for c, v in labels.items():
                            split_df.at[eid, c] = int(v)
            
            # Count how many cells actually changed (optional debug)
            # Just logging row count is enough for now
            logger.info(f"  Overwrote labels for {len(common_ids)} rows in {split_name}.")
            total_updates += len(common_ids)
            
        # Reset index and save
        split_df = split_df.reset_index()
        split_df.to_csv(split_path, index=False)
        logger.info(f"  Saved updated {split_name} CSV.")

    logger.info(f"✅ Force merge complete. Total encounter updates: {total_updates}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Force overwrite training labels with human verified data.")
    parser.add_argument("--human-csv", required=True, help="Path to master human labels CSV")
    parser.add_argument("--target-dir", default="data/ml_training", help="Directory containing registry_{train,val,test}.csv")
    args = parser.parse_args()
    
    force_merge(args.human_csv, args.target_dir)
