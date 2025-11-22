import sys
from pathlib import Path

# Ensure we can import from modules
sys.path.append(str(Path.cwd()))

from modules.ml_coder.training import train_model

def main():
    # Point to the CLEANED csv from Phase 1
    csv_path = "data/cpt_training_data_cleaned.csv"
    
    print(f"Starting training on {csv_path}...")
    try:
        pipeline, mlb = train_model(csv_path)
        print("\nTraining successfully completed.")
        print(f"Model artifacts saved to data/models/")
        print(f"Classes learned: {len(mlb.classes_)}")
    except Exception as e:
        print(f"\nTraining Failed: {e}")

if __name__ == "__main__":
    main()