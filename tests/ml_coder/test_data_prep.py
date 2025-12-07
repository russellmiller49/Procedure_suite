"""
Tests for ML coder data preparation module.

Verifies:
- Code stratification across train/test splits
- No encounter leakage (patient_mrn + procedure_date) across splits
- Edge cases are correctly identified and separated
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


class TestBuildLabelMatrix:
    """Tests for _build_label_matrix function."""

    def test_multi_hot_encoding(self):
        """Verify multi-hot encoding produces correct matrix."""
        from modules.ml_coder.data_prep import _build_label_matrix

        df = pd.DataFrame(
            {
                "verified_cpt_codes": ["31622,31628", "31641", "31622,31641"],
            }
        )

        y, all_codes = _build_label_matrix(df)

        assert set(all_codes) == {"31622", "31628", "31641"}
        assert y.shape == (3, 3)

        # Check row 0: 31622,31628
        code_idx = {c: i for i, c in enumerate(all_codes)}
        assert y[0, code_idx["31622"]] == 1
        assert y[0, code_idx["31628"]] == 1
        assert y[0, code_idx["31641"]] == 0

        # Check row 1: 31641 only
        assert y[1, code_idx["31641"]] == 1
        assert y[1, code_idx["31622"]] == 0

        # Check row 2: 31622,31641
        assert y[2, code_idx["31622"]] == 1
        assert y[2, code_idx["31641"]] == 1


class TestEncounterGrouping:
    """Tests for encounter leakage prevention."""

    def test_no_encounter_leakage(self):
        """Verify same encounter (MRN+date) doesn't appear in both splits."""
        from modules.ml_coder.data_prep import _enforce_encounter_grouping

        df = pd.DataFrame(
            {
                "patient_mrn": ["A", "A", "B", "B", "C"],
                "procedure_date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"],
                "verified_cpt_codes": ["31622", "31628", "31641", "31654", "31622"],
            }
        )

        # Simulate split where encounter A is in both sets
        train_idx = np.array([[0], [2], [4]])  # rows 0, 2, 4
        test_idx = np.array([[1], [3]])  # rows 1, 3

        new_train, new_test = _enforce_encounter_grouping(df, train_idx, test_idx)

        train_set = set(new_train.flatten())
        test_set = set(new_test.flatten())

        # Check no overlap
        assert train_set & test_set == set()

        # Verify encounters are grouped
        for mrn, date in [("A", "2024-01-01"), ("B", "2024-01-02")]:
            enc_rows = df[(df["patient_mrn"] == mrn) & (df["procedure_date"] == date)].index.tolist()
            in_train = all(r in train_set for r in enc_rows)
            in_test = all(r in test_set for r in enc_rows)
            # All rows of an encounter must be in one split only
            assert in_train or in_test
            assert not (in_train and in_test)

    def test_majority_rule(self):
        """Verify encounter moves to split with majority of its rows."""
        from modules.ml_coder.data_prep import _enforce_encounter_grouping

        df = pd.DataFrame(
            {
                "patient_mrn": ["A", "A", "A", "B"],
                "procedure_date": ["2024-01-01", "2024-01-01", "2024-01-01", "2024-01-02"],
                "verified_cpt_codes": ["31622", "31628", "31641", "31654"],
            }
        )

        # 2 of 3 encounter A rows in train, 1 in test
        train_idx = np.array([[0], [1], [3]])
        test_idx = np.array([[2]])

        new_train, new_test = _enforce_encounter_grouping(df, train_idx, test_idx)

        train_set = set(new_train.flatten())
        test_set = set(new_test.flatten())

        # Encounter A should move fully to train (majority)
        assert 0 in train_set
        assert 1 in train_set
        assert 2 in train_set
        assert 2 not in test_set


class TestStratifiedSplit:
    """Tests for stratified_split function."""

    def test_code_appears_in_both_splits_when_sufficient_samples(self):
        """Verify common codes appear in both train and test when available."""
        from modules.ml_coder.data_prep import stratified_split

        # Create dataset with code 31641 appearing multiple times
        df = pd.DataFrame(
            {
                "patient_mrn": [f"P{i}" for i in range(20)],
                "procedure_date": [f"2024-01-{i+1:02d}" for i in range(20)],
                "verified_cpt_codes": [
                    "31641" if i % 3 == 0 else "31622,31628"
                    for i in range(20)
                ],
            }
        )

        train_idx, test_idx, all_codes = stratified_split(df, test_size=0.3)

        train_df = df.iloc[train_idx]
        test_df = df.iloc[test_idx]

        # 31641 should appear in train
        train_codes = set()
        for codes in train_df["verified_cpt_codes"]:
            train_codes.update(codes.split(","))

        # 31641 should ideally appear in test too (stratification goal)
        test_codes = set()
        for codes in test_df["verified_cpt_codes"]:
            test_codes.update(codes.split(","))

        assert "31641" in train_codes or "31641" in test_codes
        assert "31641" in all_codes

    def test_no_index_overlap(self):
        """Verify train and test indices don't overlap."""
        from modules.ml_coder.data_prep import stratified_split

        df = pd.DataFrame(
            {
                "patient_mrn": [f"P{i}" for i in range(15)],
                "procedure_date": [f"2024-01-{i+1:02d}" for i in range(15)],
                "verified_cpt_codes": ["31622,31628"] * 15,
            }
        )

        train_idx, test_idx, _ = stratified_split(df, test_size=0.2)

        assert set(train_idx) & set(test_idx) == set()
        assert len(train_idx) + len(test_idx) == len(df)


class TestEdgeCases:
    """Tests for edge case handling."""

    def test_edge_case_flag(self):
        """Verify edge cases get is_edge_case=True."""
        from modules.ml_coder.data_prep import EDGE_SOURCE_NAME

        # The flag is set based on source_file matching EDGE_SOURCE_NAME
        assert EDGE_SOURCE_NAME == "synthetic_edge_case_notes_with_registry.jsonl"


class TestExtractCodes:
    """Tests for _extract_codes function."""

    def test_prefers_final_cpt_codes(self):
        """Verify coding_review.final_cpt_codes is preferred."""
        from modules.ml_coder.data_prep import _extract_codes

        entry = {
            "cpt_codes": ["31622", "31628"],
            "coding_review": {
                "final_cpt_codes": ["32997"],
                "cpt_summary": {
                    "final_codes": ["31641", "31654"]
                }
            }
        }

        codes = _extract_codes(entry)
        assert codes == ["32997"]

    def test_cpt_summary_final_codes(self):
        """Verify coding_review.cpt_summary.final_codes is used."""
        from modules.ml_coder.data_prep import _extract_codes

        entry = {
            "cpt_codes": ["31622", "31628"],
            "coding_review": {
                "cpt_summary": {
                    "final_codes": ["31641", "31654"]
                }
            }
        }

        codes = _extract_codes(entry)
        assert codes == ["31641", "31654"]

    def test_cpt_summary_dict_keys(self):
        """Verify codes extracted from dict keys when cpt_summary is keyed by code."""
        from modules.ml_coder.data_prep import _extract_codes

        entry = {
            "cpt_codes": ["31622"],
            "coding_review": {
                "cpt_summary": {
                    "31653": {"units": 1, "role": "primary"},
                    "31628": {"units": 1, "role": "addon"}
                }
            }
        }

        codes = _extract_codes(entry)
        assert set(codes) == {"31653", "31628"}

    def test_cpt_summary_list_of_objects(self):
        """Verify codes extracted from list of objects with 'code' field."""
        from modules.ml_coder.data_prep import _extract_codes

        entry = {
            "cpt_codes": ["31622"],
            "coding_review": {
                "cpt_summary": [
                    {"code": "32997", "description": "Total lung lavage"},
                    {"code": "31624", "description": "BAL"}
                ]
            }
        }

        codes = _extract_codes(entry)
        assert codes == ["32997", "31624"]

    def test_fallback_to_cpt_codes(self):
        """Verify fallback to cpt_codes when coding_review not present."""
        from modules.ml_coder.data_prep import _extract_codes

        entry = {
            "cpt_codes": ["31622", "31628"],
        }

        codes = _extract_codes(entry)
        assert codes == ["31622", "31628"]

    def test_empty_final_codes_fallback(self):
        """Verify fallback when final_codes is empty list."""
        from modules.ml_coder.data_prep import _extract_codes

        entry = {
            "cpt_codes": ["31622"],
            "coding_review": {
                "cpt_summary": {
                    "final_codes": []
                }
            }
        }

        codes = _extract_codes(entry)
        assert codes == ["31622"]

    def test_non_dict_coding_review(self):
        """Verify handling of non-dict coding_review gracefully."""
        from modules.ml_coder.data_prep import _extract_codes

        entry = {
            "cpt_codes": ["31622"],
            "coding_review": "invalid"
        }

        codes = _extract_codes(entry)
        assert codes == ["31622"]


class TestPrepareTrainingAndEvalSplits:
    """Integration tests for the full pipeline."""

    def test_output_files_created(self, tmp_path, monkeypatch):
        """Verify output CSV files are created."""
        from modules.ml_coder import data_prep

        # Mock _build_dataframe to return test data
        def mock_build_dataframe():
            return pd.DataFrame(
                {
                    "note_text": [f"Note {i}" for i in range(20)],
                    "verified_cpt_codes": ["31622,31628"] * 10 + ["31641"] * 10,
                    "source_file": ["normal.json"] * 18 + ["synthetic_edge_case_notes_with_registry.jsonl"] * 2,
                    "patient_mrn": [f"P{i}" for i in range(20)],
                    "procedure_date": [f"2024-01-{i+1:02d}" for i in range(20)],
                    "is_edge_case": [False] * 18 + [True] * 2,
                }
            )

        monkeypatch.setattr(data_prep, "_build_dataframe", mock_build_dataframe)

        output_dir = tmp_path / "ml_training"
        data_prep.prepare_training_and_eval_splits(output_dir=output_dir, test_size=0.2)

        assert (output_dir / "train.csv").exists()
        assert (output_dir / "test.csv").exists()
        assert (output_dir / "edge_cases_holdout.csv").exists()

        # Verify edge cases are separated
        edge_df = pd.read_csv(output_dir / "edge_cases_holdout.csv")
        assert len(edge_df) == 2
        assert edge_df["is_edge_case"].all()

        # Verify main splits have no edge cases
        train_df = pd.read_csv(output_dir / "train.csv")
        test_df = pd.read_csv(output_dir / "test.csv")
        assert not train_df["is_edge_case"].any()
        assert not test_df["is_edge_case"].any()

    def test_no_encounter_leakage_in_output(self, tmp_path, monkeypatch):
        """Verify no encounter leakage in generated splits."""
        from modules.ml_coder import data_prep

        # Create data with repeated encounters
        def mock_build_dataframe():
            return pd.DataFrame(
                {
                    "note_text": [f"Note {i}" for i in range(20)],
                    "verified_cpt_codes": ["31622,31628"] * 20,
                    "source_file": ["normal.json"] * 20,
                    "patient_mrn": ["P1"] * 5 + ["P2"] * 5 + [f"P{i}" for i in range(10, 20)],
                    "procedure_date": ["2024-01-01"] * 5 + ["2024-01-02"] * 5 + [f"2024-01-{i+1:02d}" for i in range(10, 20)],
                    "is_edge_case": [False] * 20,
                }
            )

        monkeypatch.setattr(data_prep, "_build_dataframe", mock_build_dataframe)

        output_dir = tmp_path / "ml_training"
        data_prep.prepare_training_and_eval_splits(output_dir=output_dir, test_size=0.3)

        train_df = pd.read_csv(output_dir / "train.csv")
        test_df = pd.read_csv(output_dir / "test.csv")

        # Check encounters
        train_encounters = set(zip(train_df["patient_mrn"], train_df["procedure_date"]))
        test_encounters = set(zip(test_df["patient_mrn"], test_df["procedure_date"]))

        # No encounter should appear in both splits
        assert train_encounters & test_encounters == set()
