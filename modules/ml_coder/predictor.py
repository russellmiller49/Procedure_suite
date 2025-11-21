"""Prediction service that wraps the trained CPT classifier."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

from modules.common.logger import get_logger

logger = get_logger("ml_coder.predictor")


class MLCoderService:
    """Thin wrapper around the trained classifier pipeline and binarizer."""

    def __init__(self, models_dir: str | Path | None = None) -> None:
        self.models_dir = Path(models_dir) if models_dir else Path("data/models")
        self.pipeline_path = self.models_dir / "cpt_classifier.pkl"
        self.mlb_path = self.models_dir / "mlb.pkl"
        self.pipeline: Pipeline | None = None
        self.mlb: MultiLabelBinarizer | None = None
        self.available = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        try:
            self.pipeline = joblib.load(self.pipeline_path)
            self.mlb = joblib.load(self.mlb_path)
            self.available = True
            logger.info("Loaded ML artifacts from %s", self.models_dir)
        except FileNotFoundError:
            logger.warning(
                "ML artifacts not found at %s. Machine learning predictions disabled.",
                self.models_dir,
            )
            self.available = False
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to load ML artifacts: %s", exc)
            self.available = False

    def predict(self, text: str, threshold: float = 0.5) -> List[Dict[str, float | str]]:
        """Return ML predictions for the supplied text above a probability threshold."""

        if not self.available or not self.pipeline or not self.mlb:
            return []

        normalized = text.strip()
        if not normalized:
            return []

        try:
            probabilities = self.pipeline.predict_proba([normalized])
        except AttributeError:  # pragma: no cover - should not happen with the configured model
            logger.warning("ML pipeline does not support probability predictions.")
            return []
        except Exception as exc:  # pragma: no cover - inference safety
            logger.exception("ML prediction failed: %s", exc)
            return []

        prob_array = probabilities[0]

        results: List[Dict[str, float | str]] = []
        for code, score in zip(self.mlb.classes_, prob_array):
            confidence = float(score)
            if confidence >= threshold:
                results.append(
                    {
                        "cpt": str(code),
                        "confidence": confidence,
                        "source": "ml_model",
                    }
                )

        results.sort(key=lambda item: item["confidence"], reverse=True)
        return results


__all__ = ["MLCoderService"]
