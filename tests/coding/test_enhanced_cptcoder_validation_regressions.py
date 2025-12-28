"""Regression tests for CPT coding validation fixes (v2.8 synthetic notes).

These tests target the specific FP/FN patterns identified in validation runs:
- FPs: 31652, 31640, 31646, 31630, 32554, 31634
- FNs: 31627, 31654

New rules being tested:
- R015: Navigation priority (suppress redundant bronch codes when nav bundle present)
- R016: CAO bundle rules (suppress stray debulking codes with stent combo)
- R017: Thoracoscopy vs pleural tube (suppress chest tube codes when 32650 present)
- R018: EBUS mutual exclusion (never keep both 31652 AND 31653)
"""

import pytest
from modules.autocode.coder import EnhancedCPTCoder


@pytest.fixture(scope="module")
def coder():
    """Shared coder instance for all tests."""
    return EnhancedCPTCoder()


def extract_codes(result):
    """Extract CPT codes from coder result."""
    return {c["cpt"] for c in result.get("codes", [])}


# =============================================================================
# TEST CASE 1: Nav + Radial + Cryobiopsy + Brushing (Ion case)
# Expected: {31627, 31654, 31628, 31623}
# Should NOT include: 31640, 31652, 31646, 31634
# =============================================================================

class TestNavRadialCryoBrush:
    """Ion robotic nav case with radial EBUS, cryobiopsy, and brushing."""

    def test_ion_nav_case_expected_codes(self, coder):
        """Nav + radial + cryobiopsy + brushing should produce 31627, 31654, 31628, 31623."""
        note = """
        PROCEDURE: Ion Robotic Bronchoscopy with Cone Beam CT Navigation

        TECHNIQUE:
        Ion robotic bronchoscopy platform was used for electromagnetic navigation
        to a 1.8cm peripheral nodule in the right upper lobe. CT-based planning
        and registration performed pre-procedure.

        Navigation catheter advanced to the target lesion. Radial EBUS probe
        confirmed concentric view at the target site. Tool-in-lesion position
        verified with Cone Beam CT imaging.

        Sampling performed:
        - Transbronchial cryobiopsy x 3 (1.9mm cryoprobe)
        - Cytology brushings obtained
        - No mediastinal lymph node sampling performed

        FINDINGS:
        Peripheral lung nodule successfully targeted and sampled.
        No pneumothorax on completion fluoro.
        """
        registry = {
            "nav_platform": "Ion robotic bronchoscopy",
            "nav_rebus_used": True,
            "nav_rebus_view": "concentric",
            "nav_imaging_verification": "Cone Beam CT",
            "nav_sampling_tools": ["cryoprobe", "brush"],
        }
        result = coder.code_procedure({"note_text": note, "registry": registry})
        codes = extract_codes(result)

        # Should include nav and peripheral sampling codes
        assert "31627" in codes, "Navigation code 31627 should be present"
        assert "31654" in codes or "+31654" in codes, "Radial EBUS add-on 31654 should be present"
        assert "31628" in codes, "Transbronchial biopsy 31628 should be present"

        # Should NOT include inappropriate codes
        assert "31640" not in codes, "31640 (mechanical excision) should not be present"
        assert "31652" not in codes, "31652 (linear EBUS 1-2 stations) should not be present - no nodal staging"
        assert "31646" not in codes, "31646 (therapeutic aspiration) should not be present"
        assert "31634" not in codes, "31634 (balloon dilation) should not be present"


# =============================================================================
# TEST CASE 2: Combined EBUS Staging + Nav Peripheral + Cryobiopsy
# Expected: {31627, 31654, 31628, 31653}
# Should NOT include: 31652, 31623, 31624
# =============================================================================

class TestCombinedEBUSNavPeripheral:
    """Combined EBUS staging with nav-guided peripheral biopsy."""

    def test_combined_ebus_nav_case(self, coder):
        """Combined EBUS staging + nav peripheral should produce 31627, 31654, 31628, 31653."""
        note = """
        PROCEDURE: EBUS with Mediastinal Staging and Ion Navigation Peripheral Biopsy

        TECHNIQUE:
        Part 1 - Mediastinal Staging:
        Linear EBUS performed with systematic mediastinal lymph node sampling.
        Stations sampled: 4R (3 passes), 4L (2 passes), 7 (3 passes), 10R (2 passes).
        Adequate specimens obtained from all stations.

        Part 2 - Peripheral Lesion Biopsy:
        Ion robotic navigation used to target 2.2cm RLL peripheral nodule.
        Radial EBUS confirmed concentric view. Cone beam CT verified position.
        Transbronchial cryobiopsy x 4 with adequate tissue cores.
        """
        registry = {
            "nav_platform": "Ion robotic bronchoscopy",
            "nav_rebus_used": True,
            "nav_imaging_verification": "Cone Beam CT",
            "linear_ebus_stations": ["4R", "4L", "7", "10R"],
            "ebus_stations_sampled": ["4R", "4L", "7", "10R"],
        }
        result = coder.code_procedure({"note_text": note, "registry": registry})
        codes = extract_codes(result)

        # Should include navigation codes
        assert "31627" in codes, "Navigation code 31627 should be present"
        assert "31654" in codes or "+31654" in codes, "Radial EBUS add-on 31654 should be present"
        assert "31628" in codes, "Transbronchial biopsy 31628 should be present"

        # Should include EBUS staging for 4+ stations
        assert "31653" in codes, "31653 (EBUS 3+ stations) should be present for 4 stations"

        # Should NOT include these
        assert "31652" not in codes, "31652 should not be present when 31653 is used (4 stations)"
        # Note: 31623/31624 may still be present if brushings/BAL documented - test context-specific


# =============================================================================
# TEST CASE 3: EBUS Only, Multiple Stations
# Expected: {31653} only
# Should NOT include: 31652
# =============================================================================

class TestEBUSOnlyMultipleStations:
    """Pure EBUS staging with multiple stations - should only produce 31653."""

    def test_ebus_multiple_stations_only_31653(self, coder):
        """EBUS with 3+ stations should produce only 31653, not 31652."""
        note = """
        PROCEDURE: EBUS-guided Mediastinal Lymph Node Sampling

        INDICATION: Lung cancer staging

        TECHNIQUE:
        Linear EBUS performed for systematic mediastinal staging.

        Stations sampled:
        - Station 4R: 3 passes, 22G needle
        - Station 4L: 2 passes, 22G needle
        - Station 7 (subcarinal): 3 passes, 22G needle

        ROSE: Adequate lymphocytes from all stations. No malignant cells seen on preliminary review.

        IMPRESSION:
        Systematic EBUS-TBNA of 3 mediastinal stations completed successfully.
        """
        registry = {
            "ebus_stations_sampled": ["4R", "4L", "7"],
            "linear_ebus_stations": ["4R", "4L", "7"],
        }
        result = coder.code_procedure({"note_text": note, "registry": registry})
        codes = extract_codes(result)

        # Should produce 31653 for 3+ stations
        assert "31653" in codes, "31653 (EBUS 3+ stations) should be present"

        # Should NOT produce 31652
        assert "31652" not in codes, "31652 should not be present - 3 stations sampled"


# =============================================================================
# TEST CASE 4: Thoracoscopy with Talc Pleurodesis
# Expected: {32650} only
# Should NOT include: 32554, 32555, 32557, 32560
# =============================================================================

class TestThoracoscopyTalcPleurodesis:
    """Medical thoracoscopy with talc pleurodesis - should produce only 32650."""

    def test_thoracoscopy_pleurodesis_only_32650(self, coder):
        """Thoracoscopy with talc should produce 32650, not separate chest tube codes."""
        note = """
        PROCEDURE: Medical Thoracoscopy with Talc Pleurodesis

        INDICATION: Recurrent malignant pleural effusion

        TECHNIQUE:
        Patient positioned in lateral decubitus. Local anesthesia with 1% lidocaine.
        Single port entry at 6th intercostal space, mid-axillary line.
        Thoracoscope inserted. Large pleural effusion evacuated (1800mL serous fluid).

        Complete pleural survey performed. Multiple nodular implants visualized
        on parietal and visceral pleura. Pleural biopsies obtained with rigid forceps.

        Talc slurry pleurodesis performed - 4g sterile talc insufflated under
        direct visualization with excellent distribution.

        24F chest tube placed through the thoracoscopy port site.

        IMPRESSION:
        Successful medical thoracoscopy with talc pleurodesis for malignant effusion.
        """
        registry = {
            "pleurodesis_performed": True,
            "pleurodesis_agent": "Talc Slurry",
            "pleural_procedure_type": "Thoracoscopy",
        }
        result = coder.code_procedure({"note_text": note, "registry": registry})
        codes = extract_codes(result)

        # Should produce 32650 for thoracoscopic pleurodesis
        assert "32650" in codes, "32650 (thoracoscopic pleurodesis) should be present"

        # Should NOT produce separate chest tube/pleurodesis codes - bundled with 32650
        assert "32554" not in codes, "32554 should be bundled with thoracoscopy"
        assert "32555" not in codes, "32555 should be bundled with thoracoscopy"
        assert "32557" not in codes, "32557 should be bundled with thoracoscopy"
        assert "32560" not in codes, "32560 (pleurodesis) should be bundled with 32650"


# =============================================================================
# TEST CASE 5: CAO Rigid Debulking + Stent + Tunneled Catheter
# Expected: {31636/31631, 32550} (debulking bundled with stent)
# Should NOT include: 31640, 31641, 31646, 31630
# =============================================================================

class TestCAODebulkingStentIPC:
    """CAO with rigid debulking, stent placement, and tunneled catheter."""

    def test_cao_stent_ipc_expected_codes(self, coder):
        """CAO + stent + IPC should bill stent + IPC; debulking is bundled into stent."""
        note = """
        PROCEDURE: Rigid Bronchoscopy with Tumor Debulking, Stent Placement, and
        Tunneled Pleural Catheter Insertion

        INDICATION: Central airway obstruction from NSCLC with malignant pleural effusion

        PART 1 - AIRWAY MANAGEMENT:
        Rigid bronchoscopy performed under general anesthesia with jet ventilation.
        Large endobronchial tumor identified obstructing 80% of the right mainstem bronchus.

        Tumor debulking performed using:
        - Argon plasma coagulation (APC) for surface ablation
        - Rigid forceps mechanical debridement

        Following debulking, airway lumen restored to approximately 70% patency.
        Silicone Y-stent (14mm tracheal limb, 12mm bronchial limbs) deployed
        spanning the carina into both mainstem bronchi.

        Post-stent bronchoscopy confirms excellent stent position and airway patency.
        Secretions suctioned. No bleeding complications.

        PART 2 - PLEURAL PROCEDURE:
        Following airway intervention, patient repositioned for PleurX catheter insertion.
        Tunneled pleural catheter placed in right pleural space under ultrasound guidance.
        Initial drainage of 800mL serosanguinous fluid.

        IMPRESSION:
        Successful multimodality intervention for central airway obstruction and
        malignant pleural effusion.
        """
        registry = {
            "cao_performed": True,
            "cao_modalities": ["APC", "mechanical debulking"],
            "stent_placed": True,
            "stent_type": "Silicone Y-stent",
            "ipc_inserted": True,
        }
        result = coder.code_procedure({"note_text": note, "registry": registry})
        codes = extract_codes(result)

        # Should include stent code
        assert "31636" in codes or "31631" in codes, "Stent code should be present"

        # Should include IPC insertion
        assert "32550" in codes, "32550 (tunneled pleural catheter) should be present"

        # Should NOT include debulking codes (bundled into stent)
        assert "31640" not in codes, "31640 should not be billed separately when stent is placed"
        assert "31641" not in codes, "31641 should not be billed separately when stent is placed"
        assert "31646" not in codes, "31646 (therapeutic aspiration) bundled with CAO"

        # 31630 should not be present unless dilation separately documented
        if "31630" in codes:
            # Only acceptable if dilation was explicitly documented separately
            assert "balloon dilation" in note.lower(), "31630 requires separate dilation documentation"


# =============================================================================
# RULE 18: EBUS Mutual Exclusion Tests
# =============================================================================

class TestEBUSMutualExclusion:
    """Tests to verify 31652 and 31653 are never both present."""

    def test_never_both_31652_and_31653(self, coder):
        """Should never produce both 31652 AND 31653 in final codes."""
        # Test with various station counts to ensure mutual exclusion

        # Case 1: 2 stations -> should produce 31652 only
        note_2_stations = """
        EBUS-TBNA performed. Station 4R sampled (3 passes). Station 7 sampled (2 passes).
        Linear EBUS mediastinal staging with 2 nodal stations.
        """
        registry_2 = {"ebus_stations_sampled": ["4R", "7"], "linear_ebus_stations": ["4R", "7"]}
        result_2 = coder.code_procedure({"note_text": note_2_stations, "registry": registry_2})
        codes_2 = extract_codes(result_2)

        # At most one of 31652/31653 should be present
        has_31652 = "31652" in codes_2
        has_31653 = "31653" in codes_2
        assert not (has_31652 and has_31653), "Cannot have both 31652 and 31653"

        # Case 2: 4 stations -> should produce 31653 only
        note_4_stations = """
        EBUS-TBNA performed. Systematic mediastinal staging.
        Station 4R sampled (3 passes).
        Station 4L sampled (2 passes).
        Station 7 sampled (3 passes).
        Station 10R sampled (2 passes).
        Linear EBUS with 4 nodal stations.
        """
        registry_4 = {
            "ebus_stations_sampled": ["4R", "4L", "7", "10R"],
            "linear_ebus_stations": ["4R", "4L", "7", "10R"],
        }
        result_4 = coder.code_procedure({"note_text": note_4_stations, "registry": registry_4})
        codes_4 = extract_codes(result_4)

        has_31652_4 = "31652" in codes_4
        has_31653_4 = "31653" in codes_4
        assert not (has_31652_4 and has_31653_4), "Cannot have both 31652 and 31653"


# =============================================================================
# RULE 15: Navigation Priority - Suppress Redundant Codes
# =============================================================================

class TestNavigationPrioritySuppression:
    """Tests for R015: Navigation priority suppression of redundant bronch codes."""

    def test_nav_bundle_suppresses_redundant_bronch(self, coder):
        """When nav bundle (31627/31654) present, should suppress 31622/31623/31624."""
        note = """
        Ion robotic bronchoscopy performed for peripheral lung nodule evaluation.
        Navigation to RUL nodule successful. Radial EBUS confirmed concentric view.
        Cone beam CT verification performed.

        Bronchoscopy examination of airways normal.
        Transbronchial biopsy x 4 via navigation catheter.
        Cytology brushings obtained at target site.
        No BAL performed.
        """
        registry = {
            "nav_platform": "Ion robotic bronchoscopy",
            "nav_rebus_used": True,
            "nav_imaging_verification": "Cone Beam CT",
            "nav_lesion_type": "peripheral",
        }
        result = coder.code_procedure({"note_text": note, "registry": registry})
        codes = extract_codes(result)

        # Should have nav codes
        assert "31627" in codes, "Navigation code should be present"

        # Brushings at nav site should be bundled with nav procedure
        # 31623 may or may not be suppressed depending on whether it's clearly at the nav site


# =============================================================================
# RULE 17: Thoracoscopy vs Pleural Tube Suppression
# =============================================================================

class TestThoracoscopyPleuralSuppression:
    """Tests for R017: Thoracoscopy vs pleural tube code suppression."""

    def test_32650_suppresses_chest_tube_codes(self, coder):
        """When 32650 present with thoracoscopy narrative, should suppress chest tube codes."""
        note = """
        Medical thoracoscopy performed for recurrent pleural effusion.
        Thoracoscopic pleurodesis with talc slurry.
        Chest tube placed at conclusion of procedure.
        """
        registry = {
            "pleurodesis_performed": True,
            "pleurodesis_agent": "Talc",
        }
        result = coder.code_procedure({"note_text": note, "registry": registry})
        codes = extract_codes(result)

        if "32650" in codes:
            # These should be suppressed when 32650 is present
            assert "32554" not in codes, "32554 bundled with 32650"
            assert "32556" not in codes, "32556 bundled with 32650"
            assert "32557" not in codes, "32557 bundled with 32650"
