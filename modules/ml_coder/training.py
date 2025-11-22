"""Training utilities for the CPT multi-label classifier."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

from modules.common.logger import get_logger
from modules.ml_coder.utils import clean_cpt_codes

logger = get_logger("ml_coder.training")

MODELS_DIR = Path("data/models")
PIPELINE_PATH = MODELS_DIR / "cpt_classifier.pkl"
MLB_PATH = MODELS_DIR / "mlb.pkl"


def _load_training_rows(csv_path: Path) -> tuple[list[str], list[list[str]]]:
    """Load and clean note/cpt rows from the provided CSV file."""

    df = pd.read_csv(csv_path)
    if df.empty:
        msg = f"Training file {csv_path} is empty."
        raise ValueError(msg)

    required_cols = {"note_text", "verified_cpt_codes"}
    missing = required_cols - set(df.columns)
    if missing:
        cols = ", ".join(sorted(missing))
        msg = f"Training file is missing required columns: {cols}"
        raise ValueError(msg)

    cleaned = df.dropna(subset=["note_text", "verified_cpt_codes"]).copy()
    cleaned["note_text"] = cleaned["note_text"].astype(str)
    cleaned["verified_cpt_codes"] = cleaned["verified_cpt_codes"].apply(clean_cpt_codes)
    cleaned = cleaned[cleaned["verified_cpt_codes"].map(bool)]

    texts = cleaned["note_text"].tolist()
    labels = cleaned["verified_cpt_codes"].tolist()

    if not texts:
        msg = "No valid training rows remain after cleaning the CSV."
        raise ValueError(msg)

    logger.info("Loaded %s training rows from %s", len(texts), csv_path)
    return texts, labels


def _build_pipeline() -> Pipeline:
    """Create the scikit-learn pipeline used for training/prediction."""

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2),
    )
    classifier = OneVsRestClassifier(
        RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    )
    return Pipeline(
        steps=[
            ("tfidf", vectorizer),
            ("clf", classifier),
        ]
    )


def train_model(csv_path: str | Path) -> tuple[Pipeline, MultiLabelBinarizer]:
    """Train the classifier on the supplied CSV and persist the artifacts."""

    csv_file = Path(csv_path)
    logger.info("Starting ML training from %s", csv_file)

    texts, labels = _load_training_rows(csv_file)
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(labels)

    pipeline = _build_pipeline()
    pipeline.fit(texts, y)
    logger.info("Model fit complete. Persisting artifacts to %s", MODELS_DIR)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, PIPELINE_PATH)
    joblib.dump(mlb, MLB_PATH)

    logger.info("Saved classifier to %s", PIPELINE_PATH)
    logger.info("Saved label binarizer to %s", MLB_PATH)

    return pipeline, mlb


__all__ = ["train_model", "PIPELINE_PATH", "MLB_PATH"]
