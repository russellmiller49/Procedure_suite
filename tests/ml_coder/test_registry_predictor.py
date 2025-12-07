"""Tests for registry ML predictor."""

import numpy as np
import pytest

from modules.ml_coder.registry_predictor import (
    RegistryMLPredictor,
    RegistryFieldPrediction,
    RegistryCaseClassification,
)


class MockModel:
    """Mock model for testing predict_proba."""

    def __init__(self, proba_values: np.ndarray):
        """Initialize with fixed probability values to return."""
        self._proba = proba_values

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        """Return fixed probabilities."""
        return np.array([self._proba])


class TestRegistryFieldPrediction:
    """Tests for RegistryFieldPrediction dataclass."""

    def test_to_dict(self):
        """Verify to_dict serialization."""
        pred = RegistryFieldPrediction(
            field="linear_ebus",
            probability=0.85,
            threshold=0.5,
            is_positive=True,
        )
        result = pred.to_dict()

        assert result["field"] == "linear_ebus"
        assert result["probability"] == 0.85
        assert result["threshold"] == 0.5
        assert result["is_positive"] is True


class TestRegistryCaseClassification:
    """Tests for RegistryCaseClassification dataclass."""

    def test_to_dict_truncates_long_note(self):
        """Verify long note text is truncated in to_dict."""
        long_note = "x" * 300
        classification = RegistryCaseClassification(
            note_text=long_note,
            predictions=[],
            positive_fields=["linear_ebus"],
            difficulty="HIGH_CONF",
        )
        result = classification.to_dict()

        assert len(result["note_text"]) <= 203  # 200 + "..."
        assert result["note_text"].endswith("...")

    def test_to_dict_short_note(self):
        """Verify short note text is not truncated."""
        short_note = "Short procedure note"
        classification = RegistryCaseClassification(
            note_text=short_note,
            predictions=[],
            positive_fields=[],
            difficulty="LOW_CONF",
        )
        result = classification.to_dict()

        assert result["note_text"] == short_note


class TestRegistryMLPredictor:
    """Tests for RegistryMLPredictor class."""

    def test_init_with_injected_model(self):
        """Verify predictor can be initialized with injected dependencies."""
        labels = ["linear_ebus", "radial_ebus", "navigational_bronchoscopy"]
        thresholds = {"linear_ebus": 0.5, "radial_ebus": 0.6, "navigational_bronchoscopy": 0.5}
        mock_model = MockModel(np.array([0.8, 0.4, 0.7]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        assert predictor.available is True
        assert predictor.labels == labels
        assert predictor.thresholds == thresholds

    def test_predict_proba_with_injected_model(self):
        """Verify predict_proba returns correct predictions."""
        labels = ["linear_ebus", "radial_ebus", "navigational_bronchoscopy"]
        thresholds = {"linear_ebus": 0.5, "radial_ebus": 0.6, "navigational_bronchoscopy": 0.5}
        mock_model = MockModel(np.array([0.8, 0.4, 0.7]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        preds = predictor.predict_proba("Test note")

        # Should be sorted by probability descending
        assert preds[0].field == "linear_ebus"
        assert preds[0].probability == 0.8
        assert preds[0].is_positive is True

        assert preds[1].field == "navigational_bronchoscopy"
        assert preds[1].probability == 0.7
        assert preds[1].is_positive is True

        assert preds[2].field == "radial_ebus"
        assert preds[2].probability == 0.4
        assert preds[2].is_positive is False  # Below threshold of 0.6

    def test_predict_proba_empty_text(self):
        """Verify predict_proba handles empty text gracefully."""
        labels = ["linear_ebus", "radial_ebus"]
        thresholds = {"linear_ebus": 0.5, "radial_ebus": 0.5}
        mock_model = MockModel(np.array([0.8, 0.7]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        preds = predictor.predict_proba("")

        # All should be 0 probability and not positive
        assert all(p.probability == 0.0 for p in preds)
        assert all(not p.is_positive for p in preds)

    def test_predict_returns_positive_fields(self):
        """Verify predict returns list of positive field names."""
        labels = ["linear_ebus", "radial_ebus", "navigational_bronchoscopy"]
        thresholds = {"linear_ebus": 0.5, "radial_ebus": 0.6, "navigational_bronchoscopy": 0.5}
        mock_model = MockModel(np.array([0.8, 0.4, 0.7]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        positive = predictor.predict("Test note")

        assert "linear_ebus" in positive
        assert "navigational_bronchoscopy" in positive
        assert "radial_ebus" not in positive  # Below threshold

    def test_classify_case_high_conf(self):
        """Verify classify_case returns HIGH_CONF when positives exist."""
        labels = ["linear_ebus", "radial_ebus"]
        thresholds = {"linear_ebus": 0.5, "radial_ebus": 0.5}
        mock_model = MockModel(np.array([0.8, 0.7]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        result = predictor.classify_case("Test note")

        assert result.difficulty == "HIGH_CONF"
        assert "linear_ebus" in result.positive_fields
        assert "radial_ebus" in result.positive_fields

    def test_classify_case_low_conf(self):
        """Verify classify_case returns LOW_CONF when no positives."""
        labels = ["linear_ebus", "radial_ebus"]
        thresholds = {"linear_ebus": 0.9, "radial_ebus": 0.9}  # High thresholds
        mock_model = MockModel(np.array([0.3, 0.4]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        result = predictor.classify_case("Test note")

        assert result.difficulty == "LOW_CONF"
        assert len(result.positive_fields) == 0

    def test_classify_batch(self):
        """Verify classify_batch processes multiple notes."""
        labels = ["linear_ebus"]
        thresholds = {"linear_ebus": 0.5}
        mock_model = MockModel(np.array([0.8]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        results = predictor.classify_batch(["Note 1", "Note 2", "Note 3"])

        assert len(results) == 3
        assert all(r.difficulty == "HIGH_CONF" for r in results)

    def test_threshold_for_default(self):
        """Verify threshold_for returns 0.5 for unknown fields."""
        labels = ["linear_ebus"]
        thresholds = {"linear_ebus": 0.7}
        mock_model = MockModel(np.array([0.8]))

        predictor = RegistryMLPredictor(
            model=mock_model,
            label_names=labels,
            thresholds=thresholds,
        )

        assert predictor.threshold_for("linear_ebus") == 0.7
        assert predictor.threshold_for("unknown_field") == 0.5

    def test_unavailable_predictor_returns_zeros(self):
        """Verify unavailable predictor returns zero probabilities."""
        # Create predictor that fails to load (no files exist)
        predictor = RegistryMLPredictor(
            model_path="/nonexistent/path/model.pkl",
        )

        assert predictor.available is False

        # predict_proba should return empty predictions (no labels loaded)
        preds = predictor.predict_proba("Test note")
        assert len(preds) == 0

        # predict should return empty list
        positive = predictor.predict("Test note")
        assert positive == []
