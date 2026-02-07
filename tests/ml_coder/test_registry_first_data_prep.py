#!/usr/bin/env python3
"""
Tests for Registry-First Data Preparation Module

Run with:
    pytest tests/ml_coder/test_registry_first_data_prep.py -v

Tests the registry-first data preparation workflow that extracts
training data from golden JSON files using the nested registry_entry
structure rather than CPT-based derivation.
"""

import json
import tempfile
from pathlib import Path

import pytest
import pandas as pd

from ml.lib.ml_coder.registry_data_prep import (
    RegistryLabelExtractor,
    ALL_PROCEDURE_LABELS,
    LABEL_ALIASES,
    extract_records_from_golden_dir,
    stratified_split,
    filter_rare_labels,
    prepare_registry_training_splits,
)


# =============================================================================
# Sample Golden JSON Fixtures
# =============================================================================

SAMPLE_V2_FLAT = {
    "note_text": """
    PROCEDURE NOTE
    Patient: John Doe
    Date: 2024-01-15

    Bronchoscopy performed with bronchoalveolar lavage of the right middle lobe.
    Linear EBUS used to sample station 7 and 4R lymph nodes.
    Transbronchial biopsy obtained from the right lower lobe.
    No complications.
    """,
    "registry_entry": {
        "procedures_performed": {
            "diagnostic_bronchoscopy": True,
            "bal": True,
            "linear_ebus": True,
            "transbronchial_biopsy": True,
        }
    }
}

SAMPLE_V2_NESTED = {
    "note_text": """
    BRONCHOSCOPY REPORT

    Flexible bronchoscopy with therapeutic aspiration.
    Airway stent placed in left mainstem bronchus.
    Thermal ablation of endobronchial tumor.
    """,
    "registry_entry": {
        "procedures_performed": {
            "bronchoscopy": {
                "diagnostic_bronchoscopy": True,
                "therapeutic_aspiration": True,
                "airway_stent": True,
                "thermal_ablation": True,
            }
        }
    }
}

SAMPLE_V3_GRANULAR = {
    "note_text": """
    PLEURAL PROCEDURE NOTE

    Thoracentesis performed under ultrasound guidance.
    1500ml of pleural fluid drained.
    PleurX catheter inserted.
    Talc pleurodesis performed.
    """,
    "registry_entry": {
        "granular_data": {
            "pleural": {
                "tap": True,  # Alias for thoracentesis
                "ipc_placement": True,  # Alias for ipc
                "pleurodesis": True,
            }
        }
    }
}

SAMPLE_V3_WITH_PERFORMED_KEY = {
    "note_text": """
    INTERVENTIONAL PULMONOLOGY REPORT

    Radial EBUS with navigational bronchoscopy.
    Transbronchial cryobiopsy obtained.
    """,
    "registry_entry": {
        "procedures_performed": {
            "radial_ebus": {"performed": True, "stations": ["RB4"]},
            "navigational_bronchoscopy": {"performed": True, "system": "SuperDimension"},
            "transbronchial_cryobiopsy": {"performed": True},
        }
    }
}

SAMPLE_EMPTY_REGISTRY = {
    # Note text with no procedure keywords that would trigger hydration
    "note_text": """This is a clinical note without any detectable procedure content.
    The patient was seen for a routine follow-up visit in the clinic today.
    Vital signs were stable and the patient reports feeling well.""",
    "registry_entry": {
        "procedures_performed": {
            "diagnostic_bronchoscopy": False,
            "bal": False,
        }
    }
}

SAMPLE_NO_TEXT = {
    "note_text": "",
    "registry_entry": {"procedures_performed": {"bal": True}}
}


# =============================================================================
# Unit Tests
# =============================================================================

class TestRegistryLabelExtractor:
    """Tests for RegistryLabelExtractor class."""

    def test_extract_flat_structure(self):
        """Test extraction from flat V2 structure."""
        extractor = RegistryLabelExtractor()
        registry = SAMPLE_V2_FLAT["registry_entry"]

        labels = extractor.extract(registry)

        assert labels["diagnostic_bronchoscopy"] == 1
        assert labels["bal"] == 1
        assert labels["linear_ebus"] == 1
        assert labels["transbronchial_biopsy"] == 1
        assert labels["thoracentesis"] == 0  # Not present

    def test_extract_nested_structure(self):
        """Test extraction from nested V2 structure."""
        extractor = RegistryLabelExtractor()
        registry = SAMPLE_V2_NESTED["registry_entry"]

        labels = extractor.extract(registry)

        assert labels["diagnostic_bronchoscopy"] == 1
        assert labels["therapeutic_aspiration"] == 1
        assert labels["airway_stent"] == 1
        assert labels["thermal_ablation"] == 1

    def test_extract_with_aliases(self):
        """Test extraction with alias key names."""
        extractor = RegistryLabelExtractor()
        registry = SAMPLE_V3_GRANULAR["registry_entry"]

        labels = extractor.extract(registry)

        # tap → thoracentesis
        assert labels["thoracentesis"] == 1
        # ipc_placement → ipc
        assert labels["ipc"] == 1
        assert labels["pleurodesis"] == 1

    def test_extract_with_performed_key(self):
        """Test extraction from dicts with 'performed' key."""
        extractor = RegistryLabelExtractor()
        registry = SAMPLE_V3_WITH_PERFORMED_KEY["registry_entry"]

        labels = extractor.extract(registry)

        assert labels["radial_ebus"] == 1
        assert labels["navigational_bronchoscopy"] == 1
        assert labels["transbronchial_cryobiopsy"] == 1

    def test_extract_empty_registry(self):
        """Test extraction from empty registry returns all zeros."""
        extractor = RegistryLabelExtractor()
        registry = SAMPLE_EMPTY_REGISTRY["registry_entry"]

        labels = extractor.extract(registry)

        assert all(v == 0 for v in labels.values())

    def test_all_labels_present(self):
        """Verify all canonical labels are always returned."""
        extractor = RegistryLabelExtractor()

        labels = extractor.extract({})

        assert len(labels) == len(ALL_PROCEDURE_LABELS)
        assert set(labels.keys()) == set(ALL_PROCEDURE_LABELS)


class TestExtractRecordsFromGoldenDir:
    """Tests for extract_records_from_golden_dir function."""

    def test_extract_multiple_files(self):
        """Test extraction from directory with multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create sample files
            for i, sample in enumerate([SAMPLE_V2_FLAT, SAMPLE_V2_NESTED, SAMPLE_V3_GRANULAR]):
                path = tmpdir / f"golden_{i:03d}.json"
                with open(path, "w") as f:
                    json.dump(sample, f)

            records, stats = extract_records_from_golden_dir(tmpdir)

            assert len(records) == 3
            assert stats["successful"] == 3
            assert stats["total_files"] == 3

    def test_skip_empty_text(self):
        """Test that files with empty text are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            path = tmpdir / "golden_001.json"
            with open(path, "w") as f:
                json.dump(SAMPLE_NO_TEXT, f)

            records, stats = extract_records_from_golden_dir(tmpdir)

            assert len(records) == 0
            assert stats["skipped_no_text"] == 1

    def test_skip_empty_registry(self):
        """Test that files with empty labels are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            path = tmpdir / "golden_001.json"
            with open(path, "w") as f:
                json.dump(SAMPLE_EMPTY_REGISTRY, f)

            records, stats = extract_records_from_golden_dir(tmpdir)

            assert len(records) == 0
            assert stats["skipped_empty_labels"] == 1

    def test_encounter_id_stability(self):
        """Test that encounter IDs are stable across runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            path = tmpdir / "golden_001.json"
            with open(path, "w") as f:
                json.dump(SAMPLE_V2_FLAT, f)

            records1, _ = extract_records_from_golden_dir(tmpdir)
            records2, _ = extract_records_from_golden_dir(tmpdir)

            assert records1[0]["encounter_id"] == records2[0]["encounter_id"]


class TestStratifiedSplit:
    """Tests for stratified_split function."""

    def test_split_sizes(self):
        """Test that split sizes are approximately correct."""
        df = pd.DataFrame({
            "note_text": [f"Note {i}" for i in range(100)],
            "encounter_id": [f"enc_{i}" for i in range(100)],
            "label_a": [1 if i % 3 == 0 else 0 for i in range(100)],
            "label_b": [1 if i % 5 == 0 else 0 for i in range(100)],
        })

        train, val, test = stratified_split(
            df,
            label_columns=["label_a", "label_b"],
            train_size=0.70,
            val_size=0.15,
            test_size=0.15,
        )

        # Allow some tolerance for rounding
        assert 60 <= len(train) <= 80
        assert 10 <= len(val) <= 25
        assert 10 <= len(test) <= 25
        assert len(train) + len(val) + len(test) == 100

    def test_no_data_leakage(self):
        """Test that encounters don't appear in multiple splits."""
        df = pd.DataFrame({
            "note_text": [f"Note {i}" for i in range(100)],
            "encounter_id": [f"enc_{i // 2}" for i in range(100)],  # 2 rows per encounter
            "label_a": [1 if i % 3 == 0 else 0 for i in range(100)],
        })

        train, val, test = stratified_split(df, label_columns=["label_a"])

        train_enc = set(train["encounter_id"])
        val_enc = set(val["encounter_id"])
        test_enc = set(test["encounter_id"])

        assert len(train_enc & val_enc) == 0
        assert len(train_enc & test_enc) == 0
        assert len(val_enc & test_enc) == 0

    def test_reproducibility(self):
        """Test that same seed produces same split."""
        df = pd.DataFrame({
            "note_text": [f"Note {i}" for i in range(50)],
            "encounter_id": [f"enc_{i}" for i in range(50)],
            "label_a": [1 if i % 2 == 0 else 0 for i in range(50)],
        })

        train1, val1, test1 = stratified_split(df, label_columns=["label_a"], random_state=42)
        train2, val2, test2 = stratified_split(df, label_columns=["label_a"], random_state=42)

        assert list(train1["encounter_id"]) == list(train2["encounter_id"])


class TestFilterRareLabels:
    """Tests for filter_rare_labels function."""

    def test_filters_below_threshold(self):
        """Labels with counts below min_count should be removed."""
        df = pd.DataFrame({
            "note_text": [f"Note {i}" for i in range(10)],
            "encounter_id": [f"enc_{i}" for i in range(10)],
            "frequent_label": [1] * 10,  # count = 10
            "rare_label": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # count = 2
        })

        filtered, remaining, dropped = filter_rare_labels(
            df,
            label_columns=["frequent_label", "rare_label"],
            min_count=5,
        )

        assert "frequent_label" in remaining
        assert "rare_label" in dropped
        assert "frequent_label" in filtered.columns
        assert "rare_label" not in filtered.columns

    def test_keeps_labels_at_threshold(self):
        """Labels with count exactly at min_count should be kept."""
        df = pd.DataFrame({
            "note_text": [f"Note {i}" for i in range(10)],
            "encounter_id": [f"enc_{i}" for i in range(10)],
            "exact_threshold": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],  # count = 5
        })

        filtered, remaining, dropped = filter_rare_labels(
            df,
            label_columns=["exact_threshold"],
            min_count=5,
        )

        assert "exact_threshold" in remaining
        assert len(dropped) == 0


class TestPrepareRegistryTrainingSplits:
    """Tests for the main prepare_registry_training_splits function."""

    def test_full_pipeline(self):
        """Test the complete pipeline end-to-end."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create sample files with unique note_text to avoid deduplication
            import copy
            samples = [SAMPLE_V2_FLAT, SAMPLE_V2_NESTED, SAMPLE_V3_GRANULAR]
            for i in range(20):
                # Deep copy and make note_text unique
                sample = copy.deepcopy(samples[i % len(samples)])
                sample["note_text"] = f"Unique note #{i}. " + sample["note_text"]
                path = tmpdir / f"golden_{i:03d}.json"
                with open(path, "w") as f:
                    json.dump(sample, f)

            train, val, test = prepare_registry_training_splits(
                golden_dir=tmpdir,
                min_label_count=1,  # Lower for small test set
                random_state=42,
            )

            assert len(train) > 0
            assert len(val) > 0
            assert len(test) > 0

            # Check all have required columns
            required_cols = ["note_text", "encounter_id", "source_file"]
            for col in required_cols:
                assert col in train.columns

    def test_raises_on_missing_dir(self):
        """Test that FileNotFoundError is raised for missing directory."""
        with pytest.raises(FileNotFoundError):
            prepare_registry_training_splits(golden_dir=Path("/nonexistent/path"))

    def test_raises_on_empty_dir(self):
        """Test that ValueError is raised when no records extracted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create file with no valid data
            path = tmpdir / "golden_001.json"
            with open(path, "w") as f:
                json.dump(SAMPLE_EMPTY_REGISTRY, f)

            with pytest.raises(ValueError):
                prepare_registry_training_splits(golden_dir=tmpdir)


# =============================================================================
# Validation Tests (Label Coverage)
# =============================================================================

class TestLabelCoverage:
    """Tests to verify label extraction covers expected cases."""

    @pytest.mark.parametrize("alias,canonical", [
        ("ebus_linear", "linear_ebus"),
        ("ebus_radial", "radial_ebus"),
        ("navigation", "navigational_bronchoscopy"),
        ("tbna", "tbna_conventional"),
        ("tbb", "transbronchial_biopsy"),
        ("tbb_cryo", "transbronchial_cryobiopsy"),
        ("tap", "thoracentesis"),
        ("ipc_placement", "ipc"),
    ])
    def test_alias_mapping(self, alias, canonical):
        """Test that all defined aliases map correctly."""
        assert LABEL_ALIASES[alias] == canonical

        extractor = RegistryLabelExtractor()
        registry = {"procedures_performed": {alias: True}}
        labels = extractor.extract(registry)

        assert labels[canonical] == 1

    def test_all_labels_present(self):
        """Verify the canonical labels are defined."""
        assert len(ALL_PROCEDURE_LABELS) == len(set(ALL_PROCEDURE_LABELS))

        # Bronchoscopy: 23
        bronch_labels = [
            "diagnostic_bronchoscopy", "bal", "bronchial_wash", "brushings",
            "endobronchial_biopsy", "tbna_conventional", "linear_ebus", "radial_ebus",
            "navigational_bronchoscopy", "transbronchial_biopsy",
            "transbronchial_cryobiopsy", "therapeutic_aspiration", "foreign_body_removal",
            "airway_dilation", "airway_stent", "thermal_ablation", "tumor_debulking_non_thermal", "cryotherapy", "blvr",
            "peripheral_ablation", "bronchial_thermoplasty", "whole_lung_lavage", "rigid_bronchoscopy"
        ]
        for label in bronch_labels:
            assert label in ALL_PROCEDURE_LABELS, f"Missing bronch label: {label}"

        # Pleural: 7
        pleural_labels = [
            "thoracentesis", "chest_tube", "ipc", "medical_thoracoscopy",
            "pleurodesis", "pleural_biopsy", "fibrinolytic_therapy"
        ]
        for label in pleural_labels:
            assert label in ALL_PROCEDURE_LABELS, f"Missing pleural label: {label}"

        # Other: 2
        other_labels = [
            "percutaneous_tracheostomy",
            "peg_insertion",
        ]
        for label in other_labels:
            assert label in ALL_PROCEDURE_LABELS, f"Missing other label: {label}"


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
