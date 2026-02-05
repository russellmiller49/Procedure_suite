"""Tests for the label hydration module.

Tests the 3-tier extraction with hydration:
1. Tier 1: Structured extraction from registry_entry
2. Tier 2: CPT-based derivation from cpt_codes
3. Tier 3: Keyword hydration from note_text
"""

import pytest
from modules.ml_coder.label_hydrator import (
    HydratedLabels,
    hydrate_labels_from_text,
    extract_labels_with_hydration,
    KEYWORD_TO_PROCEDURE_MAP,
    NEGATION_PATTERNS,
)
from modules.registry.v2_booleans import PROCEDURE_BOOLEAN_FIELDS


class TestHydrateLabelsFromText:
    """Tests for keyword-based label extraction from note text."""

    def test_ebus_keywords(self):
        """Test EBUS-related keyword detection."""
        text = "Patient underwent EBUS bronchoscopy with TBNA of stations 4R and 7."
        labels = hydrate_labels_from_text(text)

        assert "linear_ebus" in labels
        assert "diagnostic_bronchoscopy" in labels
        assert labels["linear_ebus"] >= 0.6
        assert labels["diagnostic_bronchoscopy"] >= 0.6

    def test_radial_ebus_keywords(self):
        """Test radial EBUS detection."""
        text = "Radial EBUS was used to localize the peripheral nodule."
        labels = hydrate_labels_from_text(text)

        assert "radial_ebus" in labels
        assert labels["radial_ebus"] >= 0.6

    def test_navigational_bronchoscopy(self):
        """Test navigation bronchoscopy detection."""
        text = "Electromagnetic navigation bronchoscopy was performed using the Ion system."
        labels = hydrate_labels_from_text(text)

        assert "navigational_bronchoscopy" in labels
        assert labels["navigational_bronchoscopy"] >= 0.6

    def test_blvr_keywords(self):
        """Test BLVR detection."""
        text = "BLVR with Zephyr valve placement in the left upper lobe."
        labels = hydrate_labels_from_text(text)

        assert "blvr" in labels
        assert labels["blvr"] >= 0.6

    def test_thoracentesis_keywords(self):
        """Test thoracentesis detection."""
        text = "Ultrasound-guided thoracentesis performed, 1.5L of fluid removed."
        labels = hydrate_labels_from_text(text)

        assert "thoracentesis" in labels
        assert labels["thoracentesis"] >= 0.6

    def test_chest_tube_keywords(self):
        """Test chest tube detection."""
        text = "A 28 French chest tube was placed in the right pleural space."
        labels = hydrate_labels_from_text(text)

        assert "chest_tube" in labels

    def test_pleurodesis_keywords(self):
        """Test pleurodesis detection."""
        text = "Talc poudrage was performed for chemical pleurodesis."
        labels = hydrate_labels_from_text(text)

        assert "pleurodesis" in labels

    def test_cryotherapy_keywords(self):
        """Test cryotherapy detection."""
        text = "Cryotherapy was applied to the endobronchial lesion."
        labels = hydrate_labels_from_text(text)

        assert "cryotherapy" in labels

    def test_stent_keywords(self):
        """Test airway stent detection."""
        text = "A Dumon stent was placed in the left main bronchus."
        labels = hydrate_labels_from_text(text)

        assert "airway_stent" in labels

    def test_stent_present_well_positioned_does_not_hydrate(self):
        """Avoid stent 'present/well positioned' false positives."""
        text = "Known airway stent well positioned and patent."
        labels = hydrate_labels_from_text(text)

        assert "airway_stent" not in labels or labels.get("airway_stent", 0) < 0.6

    def test_chest_tube_discontinued_does_not_hydrate(self):
        """Avoid chest tube removal/discontinue false positives."""
        text = "D/c chest tube."
        labels = hydrate_labels_from_text(text)

        assert "chest_tube" not in labels or labels.get("chest_tube", 0) < 0.6

    def test_negation_filtering(self):
        """Test that negated keywords are filtered out."""
        text = "No EBUS was performed during this procedure."
        labels = hydrate_labels_from_text(text)

        # EBUS should not be detected due to negation
        assert "linear_ebus" not in labels or labels.get("linear_ebus", 0) < 0.6

    def test_negation_not_performed(self):
        """Test 'not performed' negation."""
        text = "Thoracentesis was not performed due to patient refusal."
        labels = hydrate_labels_from_text(text)

        assert "thoracentesis" not in labels or labels.get("thoracentesis", 0) < 0.6

    def test_negation_without(self):
        """Test 'without' negation."""
        text = "Bronchoscopy was performed without EBUS guidance."
        labels = hydrate_labels_from_text(text)

        # EBUS should not be detected
        assert "linear_ebus" not in labels or labels.get("linear_ebus", 0) < 0.6

    def test_empty_text(self):
        """Test empty text returns empty labels."""
        labels = hydrate_labels_from_text("")
        assert labels == {}

    def test_irrelevant_text(self):
        """Test text with no procedure keywords."""
        text = "The patient was seen for a routine follow-up visit."
        labels = hydrate_labels_from_text(text)

        # Should have few or no labels
        assert len(labels) == 0 or all(v < 0.6 for v in labels.values())

    def test_threshold_filtering(self):
        """Test that threshold properly filters low-confidence matches."""
        text = "Simple bronchoscopy performed."
        labels_low = hydrate_labels_from_text(text, threshold=0.5)
        labels_high = hydrate_labels_from_text(text, threshold=0.9)

        # Higher threshold should result in fewer or equal matches
        assert len(labels_high) <= len(labels_low)

    def test_cpt_code_patterns(self):
        """Test CPT code pattern detection."""
        text = "Procedure code: 31653 was billed for this encounter."
        labels = hydrate_labels_from_text(text)

        assert "linear_ebus" in labels

    def test_multiple_procedures(self):
        """Test detection of multiple procedures in same note."""
        text = """
        EBUS bronchoscopy with TBNA performed.
        Additionally, thoracentesis was done to drain the pleural effusion.
        """
        labels = hydrate_labels_from_text(text)

        assert "linear_ebus" in labels
        assert "thoracentesis" in labels
        assert "diagnostic_bronchoscopy" in labels


class TestExtractLabelsWithHydration:
    """Tests for the 3-tier extraction function."""

    def test_tier1_structured_extraction(self):
        """Test Tier 1: Structured extraction from registry_entry."""
        entry = {
            "note_text": "Patient underwent bronchoscopy.",
            "registry_entry": {
                "linear_ebus_stations": ["4R", "7"],
                "pleural_procedure_type": "Thoracentesis",
            },
        }

        result = extract_labels_with_hydration(entry)

        assert result.source == "structured"
        assert result.confidence == 0.95
        assert result.labels["linear_ebus"] == 1
        assert result.labels["thoracentesis"] == 1

    def test_tier1_v3_nested_format(self):
        """Test Tier 1 with V3 nested format."""
        entry = {
            "note_text": "Patient underwent bronchoscopy.",
            "registry_entry": {
                "procedures_performed": {
                    "linear_ebus": {"performed": True},
                    "transbronchial_biopsy": {"performed": True},
                }
            },
        }

        result = extract_labels_with_hydration(entry)

        assert result.source == "structured"
        assert result.labels["linear_ebus"] == 1
        assert result.labels["transbronchial_biopsy"] == 1

    def test_tier2_cpt_fallback(self):
        """Test Tier 2: CPT-based fallback when registry is empty."""
        entry = {
            "note_text": "Patient underwent bronchoscopy.",
            "registry_entry": {},
            "cpt_codes": [31653, 31624],
        }

        result = extract_labels_with_hydration(entry)

        assert result.source == "cpt"
        assert result.confidence == 0.80
        assert result.labels["linear_ebus"] == 1
        assert result.labels["bal"] == 1

    def test_tier3_keyword_fallback(self):
        """Test Tier 3: Keyword hydration when CPT is empty."""
        entry = {
            "note_text": "EBUS bronchoscopy with TBNA of stations 4R and 7 performed.",
            "registry_entry": {},
            "cpt_codes": [],
        }

        result = extract_labels_with_hydration(entry)

        assert result.source == "keyword"
        assert result.confidence <= 0.60
        assert result.labels["linear_ebus"] == 1
        assert result.labels["diagnostic_bronchoscopy"] == 1

    def test_tier3_masks_history_and_plan_sections_for_keyword_hydration(self):
        entry = {
            "note_text": (
                "HISTORY: airway stent placed in 2024.\n"
                "PLAN: possible stent placement next week.\n"
                "PROCEDURE: bronchoscopy performed.\n"
            ),
            "registry_entry": {},
            "cpt_codes": [],
        }

        result = extract_labels_with_hydration(entry)
        assert result.labels["airway_stent"] == 0

    def test_empty_extraction(self):
        """Test empty result when no labels can be extracted."""
        entry = {
            "note_text": "Routine follow-up visit.",
            "registry_entry": {},
            "cpt_codes": [],
        }

        result = extract_labels_with_hydration(entry)

        assert result.source == "empty"
        assert result.confidence == 0.0
        assert all(v == 0 for v in result.labels.values())

    def test_hydrated_fields_tracking(self):
        """Test that hydrated_fields correctly tracks fallback fields."""
        entry = {
            "note_text": "BLVR with Zephyr valves performed.",
            "registry_entry": {},
            "cpt_codes": [31647],
        }

        result = extract_labels_with_hydration(entry)

        # CPT fallback should track which fields were hydrated
        assert "blvr" in result.hydrated_fields or result.labels["blvr"] == 1

    def test_all_procedure_fields_present(self):
        """Test that result always includes all procedure fields."""
        entry = {
            "note_text": "Simple bronchoscopy.",
            "registry_entry": {},
        }

        result = extract_labels_with_hydration(entry)

        # All procedure fields should be in labels
        for field in PROCEDURE_BOOLEAN_FIELDS:
            assert field in result.labels
            assert result.labels[field] in (0, 1)

    def test_note_text_override(self):
        """Test note_text parameter override."""
        entry = {
            "note_text": "Original text",
            "registry_entry": {},
        }

        result = extract_labels_with_hydration(
            entry,
            note_text="EBUS bronchoscopy with TBNA performed.",
        )

        # Should use overridden text for keyword hydration
        assert result.labels["linear_ebus"] == 1


class TestKeywordPatternCoverage:
    """Tests for keyword pattern coverage of all procedure fields."""

    def test_keyword_map_has_patterns(self):
        """Test that KEYWORD_TO_PROCEDURE_MAP has patterns."""
        assert len(KEYWORD_TO_PROCEDURE_MAP) > 40

    def test_all_procedures_have_keywords(self):
        """Test that most procedures have at least one keyword pattern."""
        # Collect all procedures covered by keyword patterns
        covered_procedures = set()
        for pattern, mappings in KEYWORD_TO_PROCEDURE_MAP.items():
            for proc_name, confidence in mappings:
                covered_procedures.add(proc_name)

        # At least 80% of procedures should have keywords
        coverage = len(covered_procedures) / len(PROCEDURE_BOOLEAN_FIELDS)
        assert coverage >= 0.80, f"Only {coverage*100:.0f}% coverage"

    def test_negation_patterns_exist(self):
        """Test that negation patterns are defined."""
        assert len(NEGATION_PATTERNS) >= 5


class TestIntegration:
    """Integration tests for the full hydration pipeline."""

    def test_real_world_ebus_note(self):
        """Test with realistic EBUS procedure note."""
        entry = {
            "note_text": """
            PROCEDURE: EBUS-TBNA

            FINDINGS:
            The bronchoscope was advanced through the vocal cords.
            EBUS examination of stations 4R, 7, and 11L was performed.
            TBNA was performed at each station with adequate sampling.

            IMPRESSION:
            EBUS-TBNA of mediastinal and hilar lymph nodes performed.
            """,
            "registry_entry": {
                "linear_ebus_stations": ["4R", "7", "11L"],
            },
        }

        result = extract_labels_with_hydration(entry)

        assert result.source == "structured"
        assert result.labels["linear_ebus"] == 1
        assert result.labels["diagnostic_bronchoscopy"] == 1

    def test_real_world_pleural_note(self):
        """Test with realistic pleural procedure note."""
        entry = {
            "note_text": """
            PROCEDURE: Therapeutic thoracentesis

            Large left pleural effusion identified on ultrasound.
            Under ultrasound guidance, 1.8L of serosanguinous fluid removed.

            PleurX catheter placement for recurrent effusion.
            """,
            "registry_entry": {
                "pleural_procedure_type": "Indwelling Pleural Catheter",
            },
        }

        result = extract_labels_with_hydration(entry)

        assert result.labels["ipc"] == 1

    def test_mixed_bronch_and_pleural(self):
        """Test note with both bronchoscopy and pleural procedures."""
        entry = {
            "note_text": """
            Combined procedure: bronchoscopy and thoracentesis.

            EBUS-TBNA of stations 4R and 7.
            Followed by diagnostic thoracentesis with 500ml removed.
            """,
            "registry_entry": {
                "linear_ebus_stations": ["4R", "7"],
                "pleural_procedure_type": "Thoracentesis",
            },
        }

        result = extract_labels_with_hydration(entry)

        assert result.labels["linear_ebus"] == 1
        assert result.labels["thoracentesis"] == 1
        assert result.labels["diagnostic_bronchoscopy"] == 1


class TestDeduplication:
    """Tests for record deduplication functionality."""

    def test_keeps_structured_over_cpt(self):
        """When same text has structured and cpt labels, keep structured."""
        from modules.ml_coder.registry_data_prep import deduplicate_records

        records = [
            {"note_text": "Test note", "label_source": "cpt", "label_confidence": 0.80, "bal": 1},
            {"note_text": "Test note", "label_source": "structured", "label_confidence": 0.95, "linear_ebus": 1},
        ]
        deduped, stats = deduplicate_records(records)

        assert len(deduped) == 1
        assert deduped[0]["label_source"] == "structured"
        assert deduped[0]["linear_ebus"] == 1
        assert stats["duplicates_removed"] == 1

    def test_keeps_cpt_over_keyword(self):
        """When same text has cpt and keyword labels, keep cpt."""
        from modules.ml_coder.registry_data_prep import deduplicate_records

        records = [
            {"note_text": "Test note", "label_source": "keyword", "label_confidence": 0.60, "bal": 1},
            {"note_text": "Test note", "label_source": "cpt", "label_confidence": 0.80, "thoracentesis": 1},
        ]
        deduped, stats = deduplicate_records(records)

        assert len(deduped) == 1
        assert deduped[0]["label_source"] == "cpt"
        assert deduped[0]["thoracentesis"] == 1
        assert stats["duplicates_removed"] == 1

    def test_keeps_higher_confidence_same_source(self):
        """When same source, keep higher confidence."""
        from modules.ml_coder.registry_data_prep import deduplicate_records

        records = [
            {"note_text": "Test note", "label_source": "keyword", "label_confidence": 0.55, "bal": 1},
            {"note_text": "Test note", "label_source": "keyword", "label_confidence": 0.65, "linear_ebus": 1},
        ]
        deduped, stats = deduplicate_records(records)

        assert len(deduped) == 1
        assert deduped[0]["label_confidence"] == 0.65
        assert deduped[0]["linear_ebus"] == 1
        assert stats["duplicates_removed"] == 1

    def test_no_duplicates_unchanged(self):
        """Records without duplicates pass through unchanged."""
        from modules.ml_coder.registry_data_prep import deduplicate_records

        records = [
            {"note_text": "Note A", "label_source": "structured", "label_confidence": 0.95},
            {"note_text": "Note B", "label_source": "cpt", "label_confidence": 0.80},
        ]
        deduped, stats = deduplicate_records(records)

        assert len(deduped) == 2
        assert stats["duplicates_removed"] == 0
        assert stats["unique_texts"] == 2

    def test_multiple_duplicates_same_text(self):
        """Multiple duplicates of same text keep best one."""
        from modules.ml_coder.registry_data_prep import deduplicate_records

        records = [
            {"note_text": "Same note", "label_source": "keyword", "label_confidence": 0.55},
            {"note_text": "Same note", "label_source": "cpt", "label_confidence": 0.75},
            {"note_text": "Same note", "label_source": "structured", "label_confidence": 0.95},
        ]
        deduped, stats = deduplicate_records(records)

        assert len(deduped) == 1
        assert deduped[0]["label_source"] == "structured"
        assert stats["duplicates_removed"] == 2

    def test_tracks_conflict_sources(self):
        """Conflicts by source are tracked correctly."""
        from modules.ml_coder.registry_data_prep import deduplicate_records

        records = [
            {"note_text": "Note 1", "label_source": "cpt", "label_confidence": 0.80},
            {"note_text": "Note 1", "label_source": "structured", "label_confidence": 0.95},
            {"note_text": "Note 2", "label_source": "keyword", "label_confidence": 0.60},
            {"note_text": "Note 2", "label_source": "cpt", "label_confidence": 0.80},
        ]
        deduped, stats = deduplicate_records(records)

        assert len(deduped) == 2
        assert stats["duplicates_removed"] == 2
        # Should track conflicts between different source types
        assert len(stats["conflicts_by_source"]) >= 1

    def test_empty_records_list(self):
        """Empty records list returns empty result."""
        from modules.ml_coder.registry_data_prep import deduplicate_records

        records = []
        deduped, stats = deduplicate_records(records)

        assert len(deduped) == 0
        assert stats["total_input"] == 0
        assert stats["duplicates_removed"] == 0
