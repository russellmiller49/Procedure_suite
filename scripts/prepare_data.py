import pandas as pd
from pathlib import Path

from modules.ml_coder.utils import clean_cpt_codes, join_codes

def main():
    # Path to your uploaded synthetic CSV
    input_path = Path("data/cpt_multilabel_training_data_updated.csv")
    output_path = Path("data/cpt_training_data_cleaned.csv")
    
    if not input_path.exists():
        print(f"Error: Could not find {input_path}")
        return

    print("Reading raw data...")
    df = pd.read_csv(input_path)
    
    # Apply cleaning
    print("Fixing CPT code formats...")
    df["verified_cpt_codes"] = df["verified_cpt_codes"].apply(clean_cpt_codes)
    df["verified_cpt_codes"] = df["verified_cpt_codes"].apply(join_codes)
    
    # Drop rows that ended up empty
    df = df[df["verified_cpt_codes"] != ""]
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path} with {len(df)} valid rows.")

if __name__ == "__main__":
    main()
