"""Unit tests for procedure type auto-detection."""

from __future__ import annotations

import pytest

from app.coder.application.procedure_type_detector import (
    detect_procedure_type,
    detect_procedure_type_from_codes,
)


# ============================================================================
# EBUS Detection Tests
# ============================================================================


class TestEBUSDetection:
    """Tests for EBUS procedure type detection."""

    def test_ebus_from_codes(self):
        """Test EBUS detection from CPT codes."""
        assert detect_procedure_type_from_codes(["31652"]) == "bronch_ebus"
        assert detect_procedure_type_from_codes(["31653"]) == "bronch_ebus"
        assert detect_procedure_type_from_codes(["31652", "31624"]) == "bronch_ebus"

    def test_ebus_from_text_ebus_keyword(self):
        """Test EBUS detection from text with 'EBUS' keyword."""
        text = "EBUS bronchoscopy was performed for staging"
        assert detect_procedure_type(text) == "bronch_ebus"

    def test_ebus_from_text_station_pattern(self):
        """Test EBUS detection from text with station references."""
        text = "Samples obtained from station 4R, station 7, and station 11L"
        assert detect_procedure_type(text) == "bronch_ebus"

    def test_ebus_from_text_tbna(self):
        """Test EBUS detection from TBNA keyword."""
        text = "Transbronchial needle aspiration performed at multiple sites"
        assert detect_procedure_type(text) == "bronch_ebus"

    def test_ebus_combined_text_and_codes(self):
        """Test EBUS detection with both text and codes."""
        text = "Flexible bronchoscopy with EBUS for mediastinal staging"
        codes = ["31652", "31624"]
        assert detect_procedure_type(text, codes) == "bronch_ebus"


# ============================================================================
# BLVR Detection Tests
# ============================================================================


class TestBLVRDetection:
    """Tests for BLVR procedure type detection."""

    def test_blvr_from_codes(self):
        """Test BLVR detection from CPT codes."""
        assert detect_procedure_type_from_codes(["31647"]) == "blvr"
        assert detect_procedure_type_from_codes(["31648"]) == "blvr"

    def test_blvr_from_text_valve(self):
        """Test BLVR detection from valve-related keywords."""
        text = "Endobronchial valve placement in the right upper lobe"
        assert detect_procedure_type(text) == "blvr"

    def test_blvr_from_text_zephyr(self):
        """Test BLVR detection from Zephyr keyword."""
        text = "Zephyr valves placed in RUL for emphysema treatment"
        assert detect_procedure_type(text) == "blvr"

    def test_blvr_from_text_chartis(self):
        """Test BLVR detection from Chartis keyword."""
        text = "Chartis assessment showed no collateral ventilation"
        assert detect_procedure_type(text) == "blvr"

    def test_blvr_from_text_lvr(self):
        """Test BLVR detection from lung volume reduction text."""
        text = "Bronchoscopic lung volume reduction procedure performed"
        assert detect_procedure_type(text) == "blvr"


# ============================================================================
# Therapeutic Bronchoscopy Detection Tests
# ============================================================================


class TestTherapeuticDetection:
    """Tests for therapeutic bronchoscopy detection."""

    def test_therapeutic_from_codes(self):
        """Test therapeutic detection from CPT codes."""
        assert detect_procedure_type_from_codes(["31637"]) == "bronch_therapeutic"
        assert detect_procedure_type_from_codes(["31641"]) == "bronch_therapeutic"

    def test_therapeutic_from_text_stent(self):
        """Test therapeutic detection from stent keywords."""
        text = "Airway stent placement for tracheal stenosis"
        assert detect_procedure_type(text) == "bronch_therapeutic"

    def test_therapeutic_from_text_ablation(self):
        """Test therapeutic detection from ablation keywords."""
        text = "Endobronchial ablation of tumor with electrocautery"
        assert detect_procedure_type(text) == "bronch_therapeutic"

    def test_therapeutic_from_text_laser(self):
        """Test therapeutic detection from laser keyword."""
        text = "Laser resection of endobronchial tumor"
        assert detect_procedure_type(text) == "bronch_therapeutic"

    def test_therapeutic_from_text_foreign_body(self):
        """Test therapeutic detection from foreign body removal."""
        text = "Foreign body removal from right main bronchus"
        assert detect_procedure_type(text) == "bronch_therapeutic"


# ============================================================================
# Pleural Procedure Detection Tests
# ============================================================================


class TestPleuralDetection:
    """Tests for pleural procedure detection."""

    def test_pleural_from_codes(self):
        """Test pleural detection from CPT codes."""
        assert detect_procedure_type_from_codes(["32607"]) == "pleural"
        assert detect_procedure_type_from_codes(["32555"]) == "pleural"

    def test_pleural_from_text_pleuroscopy(self):
        """Test pleural detection from pleuroscopy keyword."""
        text = "Medical pleuroscopy performed for pleural biopsy"
        assert detect_procedure_type(text) == "pleural"

    def test_pleural_from_text_thoracentesis(self):
        """Test pleural detection from thoracentesis keyword."""
        text = "Thoracentesis performed with drainage of 1500ml"
        assert detect_procedure_type(text) == "pleural"

    def test_pleural_from_text_chest_tube(self):
        """Test pleural detection from chest tube keyword."""
        text = "Chest tube inserted for pneumothorax"
        assert detect_procedure_type(text) == "pleural"

    def test_pleural_from_text_talc(self):
        """Test pleural detection from talc pleurodesis."""
        text = "Talc poudrage performed for malignant effusion"
        assert detect_procedure_type(text) == "pleural"

    def test_pleural_from_text_ipc(self):
        """Test pleural detection from IPC keyword."""
        text = "Indwelling pleural catheter placed for recurrent effusion"
        assert detect_procedure_type(text) == "pleural"


# ============================================================================
# Diagnostic Bronchoscopy Detection Tests
# ============================================================================


class TestDiagnosticDetection:
    """Tests for diagnostic bronchoscopy detection."""

    def test_diagnostic_from_codes(self):
        """Test diagnostic detection from CPT codes."""
        # Note: diagnostic codes have lower weight, so need no competing signals
        assert detect_procedure_type_from_codes(["31622"]) == "bronch_diagnostic"
        assert detect_procedure_type_from_codes(["31628"]) == "bronch_diagnostic"

    def test_diagnostic_from_text_bal(self):
        """Test diagnostic detection from BAL keyword."""
        text = "Bronchoalveolar lavage performed for infection workup"
        assert detect_procedure_type(text) == "bronch_diagnostic"

    def test_diagnostic_from_text_tblb(self):
        """Test diagnostic detection from TBLB keyword."""
        text = "Transbronchial lung biopsy of right lower lobe"
        assert detect_procedure_type(text) == "bronch_diagnostic"

    def test_diagnostic_fallback(self):
        """Test that generic bronchoscopy text falls back to diagnostic."""
        text = "Diagnostic bronchoscopy performed, airways normal"
        assert detect_procedure_type(text) == "bronch_diagnostic"


# ============================================================================
# Unknown/Edge Cases
# ============================================================================


class TestUnknownCases:
    """Tests for unknown and edge cases."""

    def test_empty_text_no_codes(self):
        """Test that empty input returns unknown."""
        assert detect_procedure_type("") == "unknown"
        assert detect_procedure_type("", []) == "unknown"

    def test_unrelated_text(self):
        """Test that unrelated text returns unknown."""
        text = "Patient presented for routine follow-up visit"
        assert detect_procedure_type(text) == "unknown"

    def test_case_insensitive(self):
        """Test that detection is case-insensitive."""
        assert detect_procedure_type("EBUS performed") == "bronch_ebus"
        assert detect_procedure_type("ebus performed") == "bronch_ebus"
        assert detect_procedure_type("Ebus Performed") == "bronch_ebus"


# ============================================================================
# Priority Tests
# ============================================================================


class TestDetectionPriority:
    """Tests for correct prioritization when multiple signals present."""

    def test_blvr_over_ebus(self):
        """Test that BLVR takes priority over EBUS when both present."""
        text = "EBUS bronchoscopy with Chartis assessment for valve placement"
        codes = ["31652", "31647"]  # EBUS + BLVR codes
        result = detect_procedure_type(text, codes)
        # BLVR should win due to higher specificity
        assert result == "blvr"

    def test_ebus_over_diagnostic(self):
        """Test that EBUS takes priority over diagnostic."""
        text = "Bronchoscopy with BAL and EBUS sampling"
        codes = ["31624", "31652"]
        result = detect_procedure_type(text, codes)
        assert result == "bronch_ebus"

    def test_codes_stronger_than_text(self):
        """Test that codes provide stronger signal than text alone."""
        # Text suggests diagnostic, but code is EBUS
        text = "Bronchoscopy with bronchoalveolar lavage"
        codes = ["31652"]  # EBUS code
        result = detect_procedure_type(text, codes)
        assert result == "bronch_ebus"
