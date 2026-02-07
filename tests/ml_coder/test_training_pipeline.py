"""
Tests for ML coder training pipeline.

Verifies:
- NoteTextCleaner is in the pipeline
- Calibrated classifier provides predict_proba
- Pipeline can fit on synthetic data
- Evaluation metrics are computed correctly
"""

import numpy as np
import pandas as pd
import pytest


class TestNoteTextCleaner:
    """Tests for the NoteTextCleaner transformer."""

    def test_removes_electronically_signed(self):
        """Verify electronic signature boilerplate is removed."""
        from ml.lib.ml_coder.preprocessing import NoteTextCleaner

        cleaner = NoteTextCleaner()
        texts = ["Patient presented with cough. Electronically signed by Dr. Smith"]
        result = cleaner.transform(texts)

        assert "electronically signed" not in result[0].lower()
        assert "Patient presented with cough" in result[0]

    def test_removes_dictated_but_not_read(self):
        """Verify dictation disclaimer is removed."""
        from ml.lib.ml_coder.preprocessing import NoteTextCleaner

        cleaner = NoteTextCleaner()
        texts = ["Procedure went well. Dictated but not read by physician."]
        result = cleaner.transform(texts)

        assert "dictated but not read" not in result[0].lower()

    def test_handles_none_and_empty(self):
        """Verify graceful handling of None and empty strings."""
        from ml.lib.ml_coder.preprocessing import NoteTextCleaner

        cleaner = NoteTextCleaner()
        texts = [None, "", "Normal text"]
        result = cleaner.transform(texts)

        assert result[0] == ""
        assert result[1] == ""
        assert result[2] == "Normal text"

    def test_normalizes_whitespace(self):
        """Verify excessive whitespace is normalized."""
        from ml.lib.ml_coder.preprocessing import NoteTextCleaner

        cleaner = NoteTextCleaner()
        texts = ["Patient   has\n\nmultiple    spaces"]
        result = cleaner.transform(texts)

        assert "  " not in result[0]
        assert "\n" not in result[0]

    def test_fit_returns_self(self):
        """Verify fit() returns self for pipeline compatibility."""
        from ml.lib.ml_coder.preprocessing import NoteTextCleaner

        cleaner = NoteTextCleaner()
        result = cleaner.fit(["some text"])

        assert result is cleaner


class TestBuildPipeline:
    """Tests for the _build_pipeline function."""

    def test_pipeline_has_cleaner(self):
        """Verify NoteTextCleaner is in the pipeline."""
        from ml.lib.ml_coder.preprocessing import NoteTextCleaner
        from ml.lib.ml_coder.training import _build_pipeline

        pipeline = _build_pipeline()
        step_names = [name for name, _ in pipeline.steps]

        assert "clean" in step_names

        # Get the cleaner step
        cleaner = pipeline.named_steps["clean"]
        assert isinstance(cleaner, NoteTextCleaner)

    def test_pipeline_has_tfidf(self):
        """Verify TfidfVectorizer is in the pipeline."""
        from sklearn.feature_extraction.text import TfidfVectorizer

        from ml.lib.ml_coder.training import _build_pipeline

        pipeline = _build_pipeline()
        tfidf = pipeline.named_steps["tfidf"]

        assert isinstance(tfidf, TfidfVectorizer)
        assert tfidf.ngram_range == (1, 3)
        assert tfidf.max_features == 3000

    def test_pipeline_has_classifier(self):
        """Verify OneVsRestClassifier is in the pipeline."""
        from sklearn.multiclass import OneVsRestClassifier

        from ml.lib.ml_coder.training import _build_pipeline

        pipeline = _build_pipeline()
        clf = pipeline.named_steps["clf"]

        assert isinstance(clf, OneVsRestClassifier)


class TestPipelineFit:
    """Tests for fitting the pipeline on synthetic data."""

    @pytest.fixture
    def synthetic_data(self):
        """Create synthetic training data with enough samples for 3-fold CV."""
        # Need at least 3 samples per class for CalibratedClassifierCV with cv=3
        base_texts = [
            "EBUS-TBNA performed, sampled stations 4R, 7, 11L",
            "Navigation bronchoscopy to RUL nodule with radial EBUS",
            "Transbronchial biopsy of LLL mass",
            "Rigid bronchoscopy with tumor ablation using APC",
            "EBUS staging with 4 lymph node stations sampled",
            "Navigation to peripheral nodule, TBBX performed",
            "Bronchoscopy with BAL for infection workup",
            "EBUS-TBNA of subcarinal node",
            "Linear EBUS with TBNA of hilar nodes",
            "Navigation bronch with R-EBUS confirmation",
            "TBBx from RLL lesion under fluoro",
            "EBUS-TBNA staging three stations",
        ]
        # Multi-hot encoded labels - ensure each class has at least 4 samples
        base_labels = np.array([
            [1, 0, 0, 0],  # 31653
            [0, 1, 1, 0],  # 31627, 31654
            [0, 0, 0, 1],  # 31628
            [1, 0, 0, 0],  # 31653
            [1, 0, 0, 0],  # 31653
            [0, 1, 0, 1],  # 31627, 31628
            [0, 0, 0, 1],  # 31628
            [1, 0, 0, 0],  # 31653
            [1, 0, 0, 0],  # 31653
            [0, 1, 1, 0],  # 31627, 31654
            [0, 0, 0, 1],  # 31628
            [1, 0, 0, 0],  # 31653
        ])
        # Repeat to ensure enough samples
        texts = base_texts * 2
        labels = np.tile(base_labels, (2, 1))
        return texts, labels

    def test_pipeline_fits_without_error(self, synthetic_data):
        """Verify pipeline can fit on synthetic data."""
        from ml.lib.ml_coder.training import _build_pipeline

        texts, labels = synthetic_data
        pipeline = _build_pipeline()

        # Should not raise
        pipeline.fit(texts, labels)

    def test_pipeline_has_predict_proba(self, synthetic_data):
        """Verify fitted pipeline has predict_proba method."""
        from ml.lib.ml_coder.training import _build_pipeline

        texts, labels = synthetic_data
        pipeline = _build_pipeline()
        pipeline.fit(texts, labels)

        assert hasattr(pipeline, "predict_proba")

        # Test predict_proba returns valid probabilities
        proba = pipeline.predict_proba(texts[:2])
        assert proba.shape == (2, 4)
        assert np.all(proba >= 0)
        assert np.all(proba <= 1)

    def test_pipeline_predict_returns_binary(self, synthetic_data):
        """Verify predict returns binary predictions."""
        from ml.lib.ml_coder.training import _build_pipeline

        texts, labels = synthetic_data
        pipeline = _build_pipeline()
        pipeline.fit(texts, labels)

        preds = pipeline.predict(texts[:2])
        assert preds.shape == (2, 4)
        assert set(np.unique(preds)).issubset({0, 1})


class TestReliabilityCurve:
    """Tests for reliability curve computation."""

    def test_compute_reliability_curve(self):
        """Verify reliability curve is computed correctly."""
        from ml.lib.ml_coder.training import _compute_reliability_curve

        # Perfect calibration: 0.5 prob -> 50% positive
        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        y_prob = np.array([0.45, 0.55, 0.45, 0.55, 0.45, 0.55, 0.45, 0.55, 0.45, 0.55])

        result = _compute_reliability_curve(y_true, y_prob, n_bins=5)

        assert "bin_centers" in result
        assert "bin_precisions" in result
        assert "bin_counts" in result
        assert len(result["bin_centers"]) == len(result["bin_precisions"])

    def test_empty_bins_handled(self):
        """Verify empty probability bins don't cause errors."""
        from ml.lib.ml_coder.training import _compute_reliability_curve

        # All predictions in high confidence range
        y_true = np.array([1, 1, 1, 1])
        y_prob = np.array([0.9, 0.95, 0.85, 0.92])

        result = _compute_reliability_curve(y_true, y_prob, n_bins=10)

        # Should only have bins where there are predictions
        assert len(result["bin_centers"]) <= 10


class TestTrainModelIntegration:
    """Integration tests for train_model function."""

    def test_train_model_creates_artifacts(self, tmp_path, monkeypatch):
        """Verify train_model creates model and mlb files."""
        from ml.lib.ml_coder import training

        # Create synthetic CSV
        train_csv = tmp_path / "train.csv"
        pd.DataFrame({
            "note_text": [
                "EBUS staging with TBNA of 4R and 7",
                "Navigation bronchoscopy with radial EBUS",
                "Transbronchial biopsy performed",
                "EBUS sampling of subcarinal node",
            ] * 3,  # Repeat for enough samples
            "verified_cpt_codes": [
                "31653",
                "31627,31654",
                "31628",
                "31653",
            ] * 3,
        }).to_csv(train_csv, index=False)

        # Redirect model output to tmp_path
        models_dir = tmp_path / "models"
        monkeypatch.setattr(training, "MODELS_DIR", models_dir)
        monkeypatch.setattr(training, "PIPELINE_PATH", models_dir / "cpt_classifier.pkl")
        monkeypatch.setattr(training, "MLB_PATH", models_dir / "mlb.pkl")

        # Train
        pipeline, mlb = training.train_model(train_csv)

        # Verify artifacts exist
        assert (models_dir / "cpt_classifier.pkl").exists()
        assert (models_dir / "mlb.pkl").exists()

        # Verify model works
        assert hasattr(pipeline, "predict_proba")
        assert len(mlb.classes_) > 0
