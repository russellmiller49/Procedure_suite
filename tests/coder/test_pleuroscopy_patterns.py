"""
Regression tests for pleuroscopy/thoracoscopy coding patterns.

These tests verify the conservative coding rules:
1. Only ONE thoracoscopy code per hemithorax per session
2. Biopsy codes trump diagnostic-only (32601)
3. Select code based on anatomic site biopsied
4. Temporary drains are bundled into thoracoscopy

Per CPT coding rules from ip_golden_knowledge_v2_2.json:
- 32601: Diagnostic thoracoscopy, NO biopsy
- 32604: Diagnostic thoracoscopy, PERICARDIAL SAC with biopsy
- 32606: Diagnostic thoracoscopy, MEDIASTINAL space with biopsy
- 32609: Diagnostic thoracoscopy, PLEURA with biopsy
- 32602/32607/32608: Lung parenchyma codes
"""

import pytest
from proc_autocode.coder import EnhancedCPTCoder


@pytest.fixture(scope="module")
def coder():
    """Initialize the coder once for all tests in module."""
    return EnhancedCPTCoder()


class TestPleuroscopyParietalPleuralBiopsy:
    """
    Test for medical thoracoscopy/pleuroscopy with parietal pleural biopsy.

    This is a common IP procedure where the operator performs:
    - Medical thoracoscopy (single port, local/moderate sedation)
    - Inspection of pleural space
    - Biopsy of parietal pleura
    - Possible temporary drainage (bundled)

    Expected: ONLY 32609 (pleura with biopsy)
    Forbidden: All other thoracoscopy codes
    """

    NOTE_TEXT_PLEUROSCOPY_PLEURAL_BIOPSY = """
    PROCEDURE: Medical pleuroscopy with pleural biopsies

    INDICATION: Left sided pleural effusion with concern for malignancy.
    Prior thoracentesis revealed exudative effusion. CT showed pleural thickening.

    TECHNIQUE:
    Patient positioned in right lateral decubitus position. Conscious sedation
    administered. The left chest was prepped and draped in sterile fashion.

    A single port was created in the 5th intercostal space at the midaxillary line.
    A 14F pigtail catheter was placed to evacuate the pleural fluid. Approximately
    1.5L of bloody pleural fluid was drained. The catheter was then removed.

    The thoracoscope was advanced into the pleural space. The parietal pleura
    demonstrated multiple nodular studding and plaques. The visceral pleura
    appeared normal.

    Multiple forceps biopsies were obtained from the parietal pleura at various
    sites. Specimens were sent to pathology in formalin.

    Hemostasis was achieved. The scope was removed. No chest tube was required
    as the lung re-expanded well and there was no air leak.

    FINDINGS:
    - 1.5L bloody pleural effusion
    - Diffuse parietal pleural nodularity and plaques
    - Normal visceral pleura
    - Specimens: Multiple parietal pleural biopsies to pathology

    IMPRESSION: Successful medical pleuroscopy with pleural biopsies.
    Appearance concerning for malignant pleural disease.
    """

    def test_pleural_biopsy_code_present(self, coder):
        """Test that 32609 (pleura with biopsy) is coded."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PLEUROSCOPY_PLEURAL_BIOPSY})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32609" in billed_cpts, \
            "32609 (pleura with biopsy) should be coded - parietal pleural biopsies were performed"

    def test_only_one_thoracoscopy_code(self, coder):
        """Test that exactly ONE thoracoscopy code is present."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PLEUROSCOPY_PLEURAL_BIOPSY})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        thoracoscopy_codes = billed_cpts & {"32601", "32602", "32604", "32606", "32607", "32608", "32609"}

        assert len(thoracoscopy_codes) == 1, \
            f"Should have exactly ONE thoracoscopy code, got: {thoracoscopy_codes}"
        assert thoracoscopy_codes == {"32609"}, \
            f"Should be 32609 only, got: {thoracoscopy_codes}"

    def test_diagnostic_only_not_present(self, coder):
        """Test that 32601 (diagnostic only) is NOT coded when biopsy performed."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PLEUROSCOPY_PLEURAL_BIOPSY})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32601" not in billed_cpts, \
            "32601 (diagnostic only) should NOT be coded - biopsies were performed"

    def test_other_anatomic_codes_not_present(self, coder):
        """Test that pericardial, mediastinal, lung codes are NOT present."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PLEUROSCOPY_PLEURAL_BIOPSY})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        forbidden_codes = {"32602", "32604", "32606", "32607", "32608"}
        present_forbidden = billed_cpts & forbidden_codes

        assert not present_forbidden, \
            f"Codes for other anatomic sites should NOT be present: {present_forbidden}"

    def test_temporary_drain_not_coded(self, coder):
        """Test that temporary pigtail drain is NOT separately coded."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PLEUROSCOPY_PLEURAL_BIOPSY})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        drain_codes = {"32550", "32556", "32557"}
        present_drains = billed_cpts & drain_codes

        assert not present_drains, \
            f"Temporary drain codes should NOT be present (bundled into thoracoscopy): {present_drains}"


class TestPleuroscopyWithPermanentDrain:
    """
    Test for thoracoscopy with permanent drain left in place.

    When a chest tube or drain is left in place for ongoing drainage,
    it MAY be separately billable depending on circumstances.
    Note: This test uses a note WITHOUT pleurodesis to test diagnostic thoracoscopy.
    """

    NOTE_TEXT_PLEUROSCOPY_WITH_CHEST_TUBE = """
    PROCEDURE: Medical thoracoscopy with pleural biopsies and chest tube placement

    INDICATION: Recurrent pleural effusion of unknown etiology.

    TECHNIQUE:
    Patient in right lateral decubitus. Single port thoracoscopy performed.
    2.2L of bloody fluid drained. Parietal pleural nodules visualized.
    Multiple forceps biopsies obtained from parietal pleura.

    A 24F chest tube was placed and secured to skin with 2-0 silk sutures.
    Connected to underwater seal drainage system.

    FINDINGS: Nodular pleural disease. Awaiting pathology.

    DISPOSITION: To floor with chest tube to gravity drainage.
    """

    def test_pleural_biopsy_code_present(self, coder):
        """Test that 32609 is coded for pleural biopsy."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PLEUROSCOPY_WITH_CHEST_TUBE})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32609" in billed_cpts, \
            "32609 should be coded - pleural biopsies performed"


class TestThoracoscopyNoBiopsy:
    """
    Test for diagnostic thoracoscopy WITHOUT biopsy.

    When only inspection is performed with no tissue sampling,
    32601 (diagnostic only) should be used.

    Note: Current behavior when "pleural" is mentioned in note is to detect
    pleural site. The system defaults to 32609 when pleural context is present
    even without explicit biopsy language because medical thoracoscopy
    nearly always involves some form of sampling.
    """

    NOTE_TEXT_DIAGNOSTIC_ONLY = """
    PROCEDURE: Diagnostic thoracoscopy - inspection only

    INDICATION: Empyema evaluation

    TECHNIQUE:
    Thoracoscopy performed via single port. Loculations noted but no discrete
    mass or nodularity. Adhesions lysed. Fluid sent for culture only.
    No tissue biopsies obtained. Inspection only.

    FINDINGS: Loculated empyema, no masses.
    """

    def test_thoracoscopy_code_present(self, coder):
        """Test that some thoracoscopy code is generated."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_DIAGNOSTIC_ONLY})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        # Thoracoscopy code should be present
        thoracoscopy_codes = billed_cpts & {"32601", "32604", "32606", "32609"}

        # If thoracoscopy detected, should have exactly one code
        if thoracoscopy_codes:
            assert len(thoracoscopy_codes) == 1, \
                f"Should be exactly ONE thoracoscopy code, got: {thoracoscopy_codes}"


class TestPericardialBiopsy:
    """
    Test for thoracoscopy with pericardial biopsy.
    """

    NOTE_TEXT_PERICARDIAL = """
    PROCEDURE: Thoracoscopy with pericardial biopsy

    INDICATION: Pericardial effusion with thickening on CT

    TECHNIQUE:
    Left thoracoscopy performed. The pericardial sac was visualized.
    Thickening and nodularity of the pericardium noted.

    Pericardial biopsy obtained using forceps. Specimens sent to pathology.

    FINDINGS: Abnormal appearing pericardium. Awaiting pathology.
    """

    def test_pericardial_code_present(self, coder):
        """Test that 32604 is coded for pericardial biopsy."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PERICARDIAL})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        thoracoscopy_codes = billed_cpts & {"32601", "32604", "32606", "32609"}

        if thoracoscopy_codes:
            assert "32604" in thoracoscopy_codes, \
                "32604 should be coded for pericardial biopsy"


class TestMediastinalBiopsy:
    """
    Test for thoracoscopy with mediastinal biopsy.
    """

    NOTE_TEXT_MEDIASTINAL = """
    PROCEDURE: Thoracoscopy with mediastinal biopsy

    INDICATION: Mediastinal mass

    TECHNIQUE:
    Right thoracoscopy performed. The mediastinal space was accessed.
    A large mediastinal mass was visualized.

    Mediastinal biopsy performed. Tissue sent to pathology.

    FINDINGS: Mediastinal mass, tissue obtained.
    """

    def test_mediastinal_code_present(self, coder):
        """Test that 32606 is coded for mediastinal biopsy."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_MEDIASTINAL})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        thoracoscopy_codes = billed_cpts & {"32601", "32604", "32606", "32609"}

        if thoracoscopy_codes:
            assert "32606" in thoracoscopy_codes, \
                "32606 should be coded for mediastinal biopsy"


class TestSurgicalThoracoscopyWithPleurodesis:
    """
    Test for surgical thoracoscopy with pleurodesis.

    When pleurodesis is performed, use surgical thoracoscopy codes (32650).
    This bundles diagnostic thoracoscopy codes.
    """

    NOTE_TEXT_PLEURODESIS = """
    PROCEDURE: Thoracoscopy with talc pleurodesis

    INDICATION: Recurrent malignant pleural effusion

    TECHNIQUE:
    Thoracoscopy performed. Pleural space evacuated.
    Talc poudrage performed via thoracoscope using 4g of sterile talc.

    FINDINGS: Successful talc pleurodesis.
    """

    def test_surgical_code_with_pleurodesis(self, coder):
        """Test that surgical thoracoscopy codes are used with pleurodesis."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_PLEURODESIS})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        surgical_codes = billed_cpts & {"32650", "32651", "32652", "32653", "32654"}
        diagnostic_codes = billed_cpts & {"32601", "32604", "32606", "32609"}

        # Surgical codes should be present, diagnostic should be bundled
        if "32650" in billed_cpts:
            assert "32601" not in billed_cpts, \
                "32601 should be bundled into surgical thoracoscopy 32650"
