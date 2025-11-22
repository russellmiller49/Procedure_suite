import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

# --- Configuration ---
INPUT_CSV = "data/cpt_multilabel_training_data_updated.csv"
MODELS_DIR = Path("data/models")

def clean_cpt_codes(raw_value):
    """
    Fixes concatenated CPT codes (e.g., '3,162,831,654' -> ['31628', '31654'])
    """
    if not isinstance(raw_value, str):
        return []
    
    # Remove all non-digit characters
    clean_digits = raw_value.replace(",", "").replace(" ", "").replace(".", "")
    
    # CPT codes are 5 digits long. Chunk the string.
    codes = [clean_digits[i:i+5] for i in range(0, len(clean_digits), 5)]
    
    # Filter for valid 5-digit codes only
    return [c for c in codes if len(c) == 5]

def train():
    print(f"Loading data from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    
    # 1. Preprocess Labels
    print("Cleaning CPT codes...")
    df["cpt_list"] = df["verified_cpt_codes"].apply(clean_cpt_codes)
    
    # Remove rows with no valid codes
    df = df[df["cpt_list"].map(len) > 0]
    print(f"Training on {len(df)} valid records.")

    # 2. Prepare Features (X) and Labels (y)
    X = df["note_text"].astype(str).tolist()
    y_raw = df["cpt_list"].tolist()

    # 3. Binarize Labels (Multi-label format)
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(y_raw)
    print(f"Found {len(mlb.classes_)} unique CPT codes.")

    # 4. Build Pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, stop_words="english")),
        ("clf", OneVsRestClassifier(RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)))
    ])

    # 5. Train
    print("Training model (this may take a moment)...")
    pipeline.fit(X, y)

    # 6. Save Artifacts
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODELS_DIR / "cpt_classifier.pkl")
    joblib.dump(mlb, MODELS_DIR / "mlb.pkl")
    
    print(f"Success! Models saved to {MODELS_DIR}/")

if __name__ == "__main__":
    train()