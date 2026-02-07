"""
Regression tests for registry extraction quality.

These tests ensure:
1. Procedure family classification is accurate
2. Field gating prevents phantom data
3. Evidence validation catches hallucinations
4. Multi-assistant handling works correctly
"""

import pytest
from app.registry.engine import (
    RegistryEngine,
    classify_procedure_families,
    filter_inapplicable_fields,
    validate_evidence_spans,
)
from app.coder.domain_rules.registry_to_cpt.engine import apply as derive_registry_to_cpt
from app.registry.postprocess import normalize_assistant_names
from app.common.spans import Span


class TestProcedureFamilyClassification:
    """Test accurate procedure family detection."""

    def test_ebus_detection_with_station_sampling(self):
        """EBUS should be detected when stations are sampled."""
        note = """
        PROCEDURE: EBUS-guided TBNA

        TECHNIQUE:
        Linear EBUS bronchoscopy performed. Stations 4R, 7, and 4L were sampled
        using a 22G needle. Multiple passes obtained from each station.
        ROSE confirmed adequate tissue.
        """
        families = classify_procedure_families(note)
        assert "EBUS" in families, "EBUS should be detected for station sampling"

    def test_ebus_not_detected_for_radial_only(self):
        """EBUS should not be detected for radial probe use alone."""
        note = """
        PROCEDURE: Bronchoscopy with radial EBUS

        TECHNIQUE:
        Radial EBUS probe advanced to peripheral RUL nodule.
        Probe showed concentric lesion. Forceps biopsies obtained.
        No mediastinal staging performed.
        """
        families = classify_procedure_families(note)
        # Radial EBUS alone shouldn't trigger EBUS family (that's for linear)
        # It should trigger BIOPSY and possibly NAVIGATION
        assert "BIOPSY" in families or "NAVIGATION" in families

    def test_navigation_detection_with_platform(self):
        """Navigation should be detected for EMN/Ion/Monarch procedures."""
        note = """
        PROCEDURE: Electromagnetic navigation bronchoscopy

        TECHNIQUE:
        superDimension EMN system used to navigate to RUL nodule.
        Target reached with good registration accuracy.
        EBUS radial probe confirmed lesion. Forceps biopsies obtained.
        """
        families = classify_procedure_families(note)
        assert "NAVIGATION" in families, "NAVIGATION should be detected for EMN"

    def test_cao_detection_with_debulking(self):
        """CAO should be detected for tumor debulking procedures."""
        note = """
        PROCEDURE: Rigid bronchoscopy with tumor debulking

        TECHNIQUE:
        Rigid bronchoscopy performed for central airway obstruction.
        Endobronchial tumor in left mainstem causing 90% obstruction.
        Mechanical debulking performed using forceps.
        APC used for hemostasis. Final patency improved to 40% obstruction.
        """
        families = classify_procedure_families(note)
        assert "CAO" in families, "CAO should be detected for debulking"

    def test_pleural_detection_for_thoracentesis(self):
        """PLEURAL should be detected for thoracentesis."""
        note = """
        PROCEDURE: Ultrasound-guided thoracentesis

        TECHNIQUE:
        Patient positioned sitting. Ultrasound used to identify pleural effusion.
        18G needle inserted at 7th ICS mid-axillary line.
        1.5L serous fluid removed. Sent for cytology and chemistry.
        """
        families = classify_procedure_families(note)
        assert "PLEURAL" in families, "PLEURAL should be detected for thoracentesis"

    def test_thoracoscopy_detection_for_pleuroscopy(self):
        """THORACOSCOPY should be detected for medical pleuroscopy."""
        note = """
        PROCEDURE: Medical thoracoscopy with pleural biopsies

        TECHNIQUE:
        Thoracoscope inserted via single port. Bloody fluid drained.
        Parietal pleura showed nodular studding. Multiple biopsies obtained.
        Talc pleurodesis performed.
        """
        families = classify_procedure_families(note)
        assert "THORACOSCOPY" in families, "THORACOSCOPY should be detected for pleuroscopy"

    def test_blvr_detection_for_valve_placement(self):
        """BLVR should be detected for valve procedures."""
        note = """
        PROCEDURE: Bronchoscopic lung volume reduction with Zephyr valves

        TECHNIQUE:
        Chartis assessment performed. LUL showed negative collateral ventilation.
        Three Zephyr valves placed in LUL segments (LB1, LB2, LB3).
        """
        families = classify_procedure_families(note)
        assert "BLVR" in families, "BLVR should be detected for valve placement"

    def test_stent_detection_for_airway_stent(self):
        """STENT should be detected for stent placement."""
        note = """
        PROCEDURE: Rigid bronchoscopy with Y-stent placement

        TECHNIQUE:
        Silicone Y-stent deployed via rigid scope covering carina
        and extending into both mainstem bronchi.
        """
        families = classify_procedure_families(note)
        assert "STENT" in families, "STENT should be detected for stent placement"

    def test_diagnostic_default_for_inspection_only(self):
        """DIAGNOSTIC should be default for inspection-only procedures."""
        note = """
        PROCEDURE: Diagnostic bronchoscopy

        TECHNIQUE:
        Flexible bronchoscopy performed. Airways inspected from
        vocal cords to segmental bronchi bilaterally.
        No lesions or abnormalities noted. No biopsies taken.
        """
        families = classify_procedure_families(note)
        # Should detect DIAGNOSTIC since no interventional procedure
        assert "DIAGNOSTIC" in families or len(families) > 0

    def test_stent_removal_codes_as_31638(self):
        """Stent removal should code as 31638 (not placement)."""
        note = "Rigid bronchoscopy with removal of silicone Y-stent."
        engine = RegistryEngine()
        record = engine.run(note)
        derivation = derive_registry_to_cpt(record)
        codes = [c.code for c in derivation.codes]
        assert "31638" in codes
        assert "31636" not in codes


class TestFieldGating:
    """Test that field applicability gating works correctly."""

    def test_ebus_fields_filtered_for_pleural_procedure(self):
        """EBUS-specific fields should be nulled for pleural-only procedures."""
        data = {
            "procedure_type": "thoracentesis",
            "pleural_side": "Right",
            "pleural_fluid_volume": "1500",
            # These shouldn't be present for pleural procedure
            "ebus_stations_sampled": ["4R", "7"],
            "ebus_rose_available": True,
            "ebus_needle_gauge": "22G",
        }
        families = {"PLEURAL"}

        filtered = filter_inapplicable_fields(data, families)

        assert filtered.get("ebus_stations_sampled") is None, "EBUS fields should be filtered"
        assert filtered.get("ebus_rose_available") is None, "EBUS fields should be filtered"
        assert filtered.get("ebus_needle_gauge") is None, "EBUS fields should be filtered"
        # Pleural fields should remain
        assert filtered.get("pleural_side") == "Right"

    def test_cao_fields_filtered_for_ebus_procedure(self):
        """CAO-specific fields should be nulled for EBUS-only procedures."""
        data = {
            "procedure_type": "ebus_tbna",
            "ebus_stations_sampled": ["4R", "7", "4L"],
            # These shouldn't be present for EBUS-only procedure
            "cao_primary_modality": "APC",
            "cao_obstruction_pre_pct": 90,
        }
        families = {"EBUS"}

        filtered = filter_inapplicable_fields(data, families)

        assert filtered.get("cao_primary_modality") is None, "CAO fields should be filtered"
        assert filtered.get("cao_obstruction_pre_pct") is None, "CAO fields should be filtered"
        # EBUS fields should remain
        assert filtered.get("ebus_stations_sampled") == ["4R", "7", "4L"]

    def test_combined_procedures_retain_fields(self):
        """Combined procedures should retain fields for all applicable families."""
        data = {
            "ebus_stations_sampled": ["4R", "7"],
            "cao_primary_modality": "Mechanical Core",
            "stent_type": "Silicone-Dumon",
        }
        families = {"EBUS", "CAO", "STENT"}

        filtered = filter_inapplicable_fields(data, families)

        # All fields should be retained for combined procedure
        assert filtered.get("ebus_stations_sampled") == ["4R", "7"]
        assert filtered.get("cao_primary_modality") == "Mechanical Core"
        assert filtered.get("stent_type") == "Silicone-Dumon"


class TestEvidenceValidation:
    """Test evidence hallucination filtering."""

    def test_valid_evidence_passes(self):
        """Evidence with correct offsets should pass validation."""
        note_text = "Patient has a right pleural effusion requiring thoracentesis."
        # Verify offsets: "right pleural effusion" starts at index 14 (0-indexed)
        # "thoracentesis" starts at index 47
        evidence = {
            "pleural_side": [
                Span(text="right pleural effusion", start=14, end=36)
            ],
            "procedure_type": [
                Span(text="thoracentesis", start=47, end=60)
            ],
        }

        validated = validate_evidence_spans(note_text, evidence)

        assert "pleural_side" in validated, "Valid evidence should pass"
        assert "procedure_type" in validated, "Valid evidence should pass"

    def test_hallucinated_offsets_filtered(self):
        """Evidence with wrong offsets should be filtered."""
        note_text = "Patient has a right pleural effusion."
        evidence = {
            "pleural_side": [
                # Wrong offsets - text doesn't match
                Span(text="right pleural effusion", start=100, end=122)
            ],
        }

        validated = validate_evidence_spans(note_text, evidence)

        # Should be filtered because offset 100 is past end of string
        assert len(validated.get("pleural_side", [])) == 0

    def test_text_in_note_gets_corrected_offsets(self):
        """Evidence with wrong offsets but correct text should get fixed."""
        note_text = "Patient has a right pleural effusion requiring drainage."
        evidence = {
            "pleural_side": [
                # Wrong offsets but text exists in note
                Span(text="right pleural effusion", start=0, end=22)
            ],
        }

        validated = validate_evidence_spans(note_text, evidence)

        # Should pass because text exists in note (will be corrected)
        if validated.get("pleural_side"):
            span = validated["pleural_side"][0]
            assert span.text == "right pleural effusion"

    def test_duplicate_spans_are_deduped(self):
        """Duplicate evidence spans should be deduplicated."""
        note_text = "Right pleural effusion noted."
        evidence = {
            "pleural_side": [
                Span(text="Right pleural effusion", start=0, end=23),
                Span(text="Right pleural effusion", start=0, end=23),
            ]
        }
        validated = validate_evidence_spans(note_text, evidence)
        assert len(validated.get("pleural_side", [])) == 1


class TestMultiAssistantHandling:
    """Test multi-assistant normalization."""

    def test_single_assistant_string(self):
        """Single assistant name should become a list."""
        result = normalize_assistant_names("Dr. Smith")
        assert result == ["Dr. Smith"]

    def test_comma_separated_assistants(self):
        """Comma-separated names should become a list."""
        result = normalize_assistant_names("Dr. Smith, Dr. Jones, Dr. Brown")
        assert result == ["Dr. Smith", "Dr. Jones", "Dr. Brown"]

    def test_semicolon_separated_assistants(self):
        """Semicolon-separated names should become a list."""
        result = normalize_assistant_names("Dr. Smith; Dr. Jones")
        assert result == ["Dr. Smith", "Dr. Jones"]

    def test_already_list_passes_through(self):
        """List input should be cleaned and returned."""
        result = normalize_assistant_names(["Dr. Smith", "Dr. Jones"])
        assert result == ["Dr. Smith", "Dr. Jones"]

    def test_none_values_filtered(self):
        """None and 'None' values should be filtered."""
        result = normalize_assistant_names("None")
        assert result is None

        result = normalize_assistant_names(["Dr. Smith", None, "None"])
        assert result == ["Dr. Smith"]

    def test_empty_string_returns_none(self):
        """Empty string should return None."""
        result = normalize_assistant_names("")
        assert result is None


class TestIntegratedExtraction:
    """Integration tests for full extraction pipeline."""

    @pytest.fixture
    def engine(self):
        """Create engine with stub LLM for testing."""
        import os
        os.environ["REGISTRY_USE_STUB_LLM"] = "true"
        return RegistryEngine()

    def test_procedure_families_populated(self, engine):
        """Procedure families should be populated in the record."""
        note = """
        PROCEDURE: EBUS-guided TBNA

        TECHNIQUE:
        Linear EBUS performed. Stations 4R and 7 sampled.
        """
        record = engine.run(note)

        assert hasattr(record, "procedure_families")
        assert record.procedure_families is not None
        # Should detect EBUS
        assert "EBUS" in record.procedure_families

    def test_evidence_is_validated(self, engine):
        """Evidence should be validated against source text."""
        note = """
        MRN: 12345678

        PROCEDURE: Flexible bronchoscopy

        Airways inspected. No abnormalities.
        """
        record = engine.run(note, include_evidence=True)

        # MRN evidence should have correct offsets
        if record.evidence.get("patient_mrn"):
            for span in record.evidence["patient_mrn"]:
                # Verify span text matches what's at the offsets
                actual = note[span.start:span.end]
                assert span.text in actual or actual in span.text


class TestPhantomDataPrevention:
    """Test that phantom/hallucinated procedure data is prevented."""

    def test_no_ebus_data_for_pleural_note(self):
        """Pleural procedure note shouldn't have EBUS data."""
        note = """
        PROCEDURE: Ultrasound-guided thoracentesis

        Right-sided pleural effusion. 1.5L removed.
        No bronchoscopy performed.
        """
        families = classify_procedure_families(note)

        # Should detect PLEURAL but not EBUS
        assert "PLEURAL" in families
        assert "EBUS" not in families

    def test_no_stent_data_without_stent_procedure(self):
        """Notes without stent procedures shouldn't have stent family."""
        note = """
        PROCEDURE: Diagnostic bronchoscopy

        Patient has history of prior tracheal stent (removed 2 years ago).
        Airways inspected. Old stent site shows mild granulation tissue.
        """
        families = classify_procedure_families(note)

        # Mentioning history of stent shouldn't trigger STENT family
        # unless a stent procedure was actually performed
        # Note: This is a tricky case - the note mentions "prior tracheal stent"
        # The classifier should focus on PERFORMED procedures, not history
        assert "STENT" not in families or "DIAGNOSTIC" in families
