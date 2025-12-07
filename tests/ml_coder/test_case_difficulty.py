"""
Tests for ternary case difficulty classification.

Verifies:
- HIGH_CONF when predictions are above upper threshold
- GRAY_ZONE when predictions are between lower and upper thresholds
- LOW_CONF when all predictions are below lower threshold
- Per-code threshold overrides work correctly
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from modules.ml_coder.thresholds import CaseDifficulty, Thresholds


class TestThresholds:
    """Tests for the Thresholds class."""

    def test_default_thresholds(self):
        """Verify default threshold values."""
        t = Thresholds()
        assert t.upper == 0.7
        assert t.lower == 0.4
        assert t.per_code == {}

    def test_upper_for_default(self):
        """Verify upper_for returns global upper when no per-code override."""
        t = Thresholds(upper=0.8, lower=0.3)
        assert t.upper_for("31653") == 0.8

    def test_upper_for_with_override(self):
        """Verify upper_for returns per-code threshold when available."""
        t = Thresholds(upper=0.8, lower=0.3, per_code={"31653": 0.6})
        assert t.upper_for("31653") == 0.6
        assert t.upper_for("31628") == 0.8  # Falls back to global

    def test_lower_for(self):
        """Verify lower_for returns global lower threshold."""
        t = Thresholds(upper=0.8, lower=0.35)
        assert t.lower_for("31653") == 0.35
        assert t.lower_for("any_code") == 0.35

    def test_from_dict(self):
        """Verify Thresholds can be created from dict."""
        data = {"upper": 0.75, "lower": 0.45, "per_code": {"31641": 0.85}}
        t = Thresholds.from_dict(data)
        assert t.upper == 0.75
        assert t.lower == 0.45
        assert t.per_code == {"31641": 0.85}

    def test_to_dict(self):
        """Verify Thresholds can be serialized to dict."""
        t = Thresholds(upper=0.7, lower=0.4, per_code={"31653": 0.5})
        d = t.to_dict()
        assert d == {"upper": 0.7, "lower": 0.4, "per_code": {"31653": 0.5}}

    def test_from_json(self, tmp_path):
        """Verify Thresholds can be loaded from JSON file."""
        import json

        json_file = tmp_path / "thresholds.json"
        json_file.write_text(json.dumps({"upper": 0.65, "lower": 0.35, "per_code": {}}))

        t = Thresholds.from_json(json_file)
        assert t.upper == 0.65
        assert t.lower == 0.35

    def test_to_json(self, tmp_path):
        """Verify Thresholds can be saved to JSON file."""
        import json

        json_file = tmp_path / "out_thresholds.json"
        t = Thresholds(upper=0.8, lower=0.3, per_code={"31627": 0.9})
        t.to_json(json_file)

        data = json.loads(json_file.read_text())
        assert data["upper"] == 0.8
        assert data["lower"] == 0.3
        assert data["per_code"] == {"31627": 0.9}


class TestCaseDifficulty:
    """Tests for the CaseDifficulty enum."""

    def test_enum_values(self):
        """Verify enum string values."""
        assert CaseDifficulty.HIGH_CONF.value == "high_confidence"
        assert CaseDifficulty.GRAY_ZONE.value == "gray_zone"
        assert CaseDifficulty.LOW_CONF.value == "low_confidence"

    def test_enum_is_string(self):
        """Verify enum inherits from str."""
        assert isinstance(CaseDifficulty.HIGH_CONF, str)
        assert CaseDifficulty.HIGH_CONF == "high_confidence"


class TestMLCoderPredictor:
    """Tests for MLCoderPredictor case classification."""

    @pytest.fixture
    def mock_predictor(self):
        """Create a predictor with mocked model."""
        from modules.ml_coder.predictor import MLCoderPredictor

        # Mock the pipeline and mlb
        mock_pipeline = MagicMock()
        mock_mlb = MagicMock()
        mock_mlb.classes_ = ["31622", "31627", "31628", "31653", "31654"]

        with patch("joblib.load") as mock_load:
            mock_load.side_effect = [mock_pipeline, mock_mlb]
            thresholds = Thresholds(upper=0.7, lower=0.4, per_code={"31653": 0.6})
            predictor = MLCoderPredictor(
                model_path="fake_path.pkl",
                mlb_path="fake_mlb.pkl",
                thresholds=thresholds,
            )
            predictor._pipeline = mock_pipeline
            return predictor

    def test_classify_high_conf(self, mock_predictor):
        """Verify HIGH_CONF when at least one prediction above upper threshold."""
        # Set up mock to return high probability for 31653
        mock_predictor._pipeline.predict_proba.return_value = np.array(
            [[0.3, 0.2, 0.1, 0.85, 0.15]]  # 31653 at 0.85 > 0.6 (per-code)
        )

        result = mock_predictor.classify_case("EBUS staging with TBNA")

        assert result.difficulty == CaseDifficulty.HIGH_CONF
        assert len(result.high_conf) == 1
        assert result.high_conf[0].cpt == "31653"
        assert result.high_conf[0].prob == 0.85

    def test_classify_gray_zone(self, mock_predictor):
        """Verify GRAY_ZONE when predictions between lower and upper."""
        # Set up mock: 31653 at 0.55 (between 0.4 lower and 0.6 per-code upper)
        mock_predictor._pipeline.predict_proba.return_value = np.array(
            [[0.3, 0.2, 0.1, 0.55, 0.15]]
        )

        result = mock_predictor.classify_case("Some bronchoscopy note")

        assert result.difficulty == CaseDifficulty.GRAY_ZONE
        assert len(result.high_conf) == 0
        assert len(result.gray_zone) == 1
        assert result.gray_zone[0].cpt == "31653"

    def test_classify_low_conf(self, mock_predictor):
        """Verify LOW_CONF when all predictions below lower threshold."""
        # All probabilities below 0.4
        mock_predictor._pipeline.predict_proba.return_value = np.array(
            [[0.1, 0.15, 0.2, 0.35, 0.05]]
        )

        result = mock_predictor.classify_case("Unclear procedure text")

        assert result.difficulty == CaseDifficulty.LOW_CONF
        assert len(result.high_conf) == 0
        assert len(result.gray_zone) == 0

    def test_classify_multiple_high_conf(self, mock_predictor):
        """Verify multiple codes can be HIGH_CONF."""
        # 31622 at 0.8 (> 0.7 global), 31627 at 0.75 (> 0.7 global)
        mock_predictor._pipeline.predict_proba.return_value = np.array(
            [[0.8, 0.75, 0.3, 0.5, 0.25]]
        )

        result = mock_predictor.classify_case("Navigation bronch with BAL")

        assert result.difficulty == CaseDifficulty.HIGH_CONF
        assert len(result.high_conf) == 2
        high_codes = {p.cpt for p in result.high_conf}
        assert high_codes == {"31622", "31627"}

    def test_classify_mixed_high_and_gray(self, mock_predictor):
        """Verify case with both high-conf and gray-zone predictions."""
        # 31653 at 0.65 > 0.6 (high), 31628 at 0.5 (gray)
        mock_predictor._pipeline.predict_proba.return_value = np.array(
            [[0.2, 0.3, 0.5, 0.65, 0.1]]
        )

        result = mock_predictor.classify_case("EBUS with biopsy")

        assert result.difficulty == CaseDifficulty.HIGH_CONF
        assert len(result.high_conf) == 1
        assert result.high_conf[0].cpt == "31653"
        assert len(result.gray_zone) == 1
        assert result.gray_zone[0].cpt == "31628"

    def test_predictions_sorted_by_prob(self, mock_predictor):
        """Verify predictions are sorted by probability descending."""
        mock_predictor._pipeline.predict_proba.return_value = np.array(
            [[0.3, 0.9, 0.1, 0.5, 0.7]]
        )

        result = mock_predictor.classify_case("Some note")

        probs = [p.prob for p in result.predictions]
        assert probs == sorted(probs, reverse=True)

    def test_to_dict(self, mock_predictor):
        """Verify CaseClassification.to_dict works correctly."""
        mock_predictor._pipeline.predict_proba.return_value = np.array(
            [[0.1, 0.2, 0.1, 0.85, 0.15]]
        )

        result = mock_predictor.classify_case("Test note")
        d = result.to_dict()

        assert d["difficulty"] == "high_confidence"
        assert "predictions" in d
        assert "high_conf" in d
        assert "gray_zone" in d
        assert all("cpt" in p and "prob" in p for p in d["predictions"])


class TestCodePrediction:
    """Tests for CodePrediction dataclass."""

    def test_to_dict(self):
        """Verify CodePrediction.to_dict works correctly."""
        from modules.ml_coder.predictor import CodePrediction

        pred = CodePrediction(cpt="31653", prob=0.85)
        d = pred.to_dict()

        assert d == {"cpt": "31653", "prob": 0.85}


class TestCaseClassification:
    """Tests for CaseClassification dataclass."""

    def test_to_dict_complete(self):
        """Verify full CaseClassification serialization."""
        from modules.ml_coder.predictor import CaseClassification, CodePrediction

        classification = CaseClassification(
            predictions=[
                CodePrediction("31653", 0.9),
                CodePrediction("31628", 0.5),
                CodePrediction("31622", 0.2),
            ],
            high_conf=[CodePrediction("31653", 0.9)],
            gray_zone=[CodePrediction("31628", 0.5)],
            difficulty=CaseDifficulty.HIGH_CONF,
        )

        d = classification.to_dict()

        assert d["difficulty"] == "high_confidence"
        assert len(d["predictions"]) == 3
        assert len(d["high_conf"]) == 1
        assert len(d["gray_zone"]) == 1
        assert d["high_conf"][0]["cpt"] == "31653"
