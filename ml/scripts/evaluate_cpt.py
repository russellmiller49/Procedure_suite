import json
from pathlib import Path

# Ensure imports resolve
import sys
sys.path.append(str(Path.cwd()))

import joblib  # noqa: E402
import pandas as pd  # noqa: E402

from ml.lib.ml_coder.training import MLB_PATH, PIPELINE_PATH  # noqa: E402
from ml.lib.ml_coder.utils import clean_cpt_codes, join_codes  # noqa: E402


def load_models():
    if not PIPELINE_PATH.exists() or not MLB_PATH.exists():
        raise FileNotFoundError("Trained models not found. Run make train-cpt first.")
    pipeline = joblib.load(PIPELINE_PATH)
    mlb = joblib.load(MLB_PATH)
    return pipeline, mlb


def main():
    input_path = Path("data/cpt_multilabel_training_data_updated.csv")
    error_log = Path("data/cpt_errors.jsonl")

    if not input_path.exists():
        print(f"Missing CPT data at {input_path}")
        return

    pipeline, mlb = load_models()

    df = pd.read_csv(input_path)
    df["note_text"] = df["note_text"].astype(str)
    df["gold_codes"] = df["verified_cpt_codes"].apply(clean_cpt_codes)

    error_log.write_text("")
    total = 0
    correct = 0

    with error_log.open("a") as elog:
        for _, row in df.iterrows():
            note = row["note_text"]
            gold_codes = row["gold_codes"]
            if not gold_codes:
                continue
            total += 1

            pred_binary = pipeline.predict([note])
            pred_codes = mlb.inverse_transform(pred_binary)[0]
            pred_set = set(pred_codes)
            gold_set = set(gold_codes)

            if pred_set == gold_set:
                correct += 1
                continue

            entry = {
                "note_text": note[:2000],
                "gold_codes": list(gold_set),
                "predicted_codes": list(pred_set),
            }
            elog.write(json.dumps(entry) + "\n")

    acc = (correct / total) * 100 if total else 0
    print(f"Evaluated {total} examples. Exact-match accuracy: {acc:.1f}%")
    print(f"CPT error log written to {error_log}")


if __name__ == "__main__":
    main()
