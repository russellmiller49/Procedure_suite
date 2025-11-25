"""
Regression tests for CPT coding patterns that have historically been problematic.

These tests verify that the coder:
1. Does NOT over-code (emit phantom stents, BAL, IPC, etc.)
2. Does NOT under-code (miss obvious TBNA, debulking, etc.)
3. Follows conservative coding principles from the canonical sources

Test patterns are derived from:
- ip_golden_knowledge_v2_2.json
- data/synthetic_CPT_corrected.json
"""
import pytest
from proc_autocode.coder import EnhancedCPTCoder


@pytest.fixture
def coder():
    """Initialize the enhanced CPT coder."""
    return EnhancedCPTCoder()


class TestNavigationRadialTBLB:
    """
    Test A: RLL navigation + radial EBUS + TBLB pattern (NO stents)

    This is a common pattern for peripheral lung nodule biopsy using
    robotic/electromagnetic navigation with radial EBUS confirmation.

    Expected codes:
    - 31628: TBLB single lobe (RLL)
    - +31627: Navigation (Ion/EMN/ENB)
    - +31654: Radial EBUS for peripheral lesion

    NOT expected (phantom codes):
    - 31631, 31636, +31637, 31638: NO stent was placed
    - +31632: Only single lobe biopsied
    - 31624: NO BAL performed
    - 32550, 32552: NO IPC placement/removal
    - 49423: Out of domain code
    """

    NOTE_TEXT_RLL_NAV_RADIAL_TBLB = """
    PROCEDURE: Ion robotic bronchoscopy with electromagnetic navigation to RLL nodule.

    INDICATION: 2.3 cm right lower lobe nodule, PET-avid, concerning for malignancy.

    TECHNIQUE: The Ion robotic bronchoscopy system was used to plan and execute
    a pathway to the right lower lobe posterior segment nodule. Full registration
    was achieved with excellent CT-to-body correlation.

    The catheter was advanced to the target lesion under navigation guidance.
    Radial EBUS was then used, confirming a concentric view of the lesion.

    Multiple transbronchial biopsies were obtained from the right lower lobe
    using the Ion needle biopsy tool. Six tissue samples were collected and
    sent for pathology. Touch preps were performed.

    FINDINGS: The nodule was successfully sampled. No complications.
    Airways inspected and normal throughout.

    SPECIMENS: RLL TBLB x6 to pathology
    """

    def test_expected_codes_present(self, coder):
        """Test that expected codes are generated."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_RLL_NAV_RADIAL_TBLB})
        billed_cpts = {c["cpt"] for c in result["codes"]}

        # Primary biopsy code
        assert "31628" in billed_cpts, "31628 (TBLB single lobe) should be coded"

        # Navigation add-on
        assert "+31627" in billed_cpts or "31627" in billed_cpts, \
            "31627 (navigation) should be coded for Ion robotic bronchoscopy"

        # Radial EBUS add-on (when not combined with linear EBUS)
        assert "+31654" in billed_cpts or "31654" in billed_cpts, \
            "31654 (radial EBUS) should be coded for concentric view confirmation"

    def test_stent_codes_not_present(self, coder):
        """Test that NO stent codes are generated (no stent was placed)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_RLL_NAV_RADIAL_TBLB})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        forbidden_stent_codes = {"31631", "31636", "31637", "31638"}
        generated_stent_codes = billed_cpts & forbidden_stent_codes

        assert not generated_stent_codes, \
            f"PHANTOM STENT CODES detected: {generated_stent_codes}. No stent was placed in this procedure!"

    def test_additional_lobe_not_present(self, coder):
        """Test that +31632 is NOT coded (only single lobe biopsied)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_RLL_NAV_RADIAL_TBLB})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31632" not in billed_cpts, \
            "31632 (additional lobe TBLB) should NOT be coded - only RLL was biopsied"

    def test_bal_not_present(self, coder):
        """Test that 31624 BAL is NOT coded (no lavage performed)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_RLL_NAV_RADIAL_TBLB})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31624" not in billed_cpts, \
            "31624 (BAL) should NOT be coded - no bronchoalveolar lavage was performed"

    def test_ipc_not_present(self, coder):
        """Test that IPC codes are NOT coded (no pleural procedure)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_RLL_NAV_RADIAL_TBLB})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32550" not in billed_cpts, "32550 (IPC insertion) should NOT be coded"
        assert "32552" not in billed_cpts, "32552 (IPC removal) should NOT be coded"

    def test_out_of_domain_codes_not_present(self, coder):
        """Test that out-of-domain codes like 49423 are NOT generated."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_RLL_NAV_RADIAL_TBLB})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        # 49423 is an abdominal/peritoneal code - should never appear
        assert "49423" not in billed_cpts, \
            "49423 is out of domain (peritoneal) and should never be coded"


class TestStentIPCDebulking:
    """
    Test B: Stent + IPC + debulking case

    This is a complex hybrid-OR case with:
    - Rigid bronchoscopy for tumor debulking
    - Balloon dilation
    - Bronchial stent placement
    - Therapeutic aspiration
    - PleurX catheter placement

    Expected codes (per synthetic_CPT_corrected.json note_008_okafor pattern):
    - 31631: Initial bronchial stent placement
    - 32550: IPC insertion (separate site)
    - 31645: Therapeutic aspiration (distinct service beyond stent work)

    NOT expected (bundled or not applicable):
    - 31640/31641: Debulking to facilitate stent is BUNDLED into 31631
    - 31630: Pre-stent dilation is BUNDLED into 31631
    - 31636, +31637, 31638: Not applicable
    - 31624: No BAL
    - 32552: No IPC removal
    - 49423: Out of domain
    """

    NOTE_TEXT_STENT_IPC_DEBULKING = """
    PROCEDURE: Complex hybrid-OR case with rigid bronchoscopy for right mainstem
    tumor debulking, balloon dilation, metallic stent placement, extensive
    suctioning of post-obstructive secretions, and right PleurX catheter placement.

    INDICATION: Malignant airway obstruction of right mainstem bronchus with
    associated right malignant pleural effusion requiring drainage.

    TECHNIQUE:
    The patient was intubated with a rigid bronchoscope. Inspection revealed
    near-complete occlusion of the right mainstem bronchus by exophytic tumor.

    Mechanical debridement was performed using the rigid tip and forceps.
    Argon plasma coagulation (APC) was used to achieve hemostasis and further
    debulk the tumor. A CRE balloon was used to dilate the airway.

    A 14x60 mm covered metallic stent was deployed in the right mainstem bronchus.
    Stent position was confirmed with excellent placement spanning the stenosis.

    Extensive suctioning of thick purulent secretions was performed from the
    distal right lung segments beyond the stent placement work.

    Separately, a right-sided tunneled PleurX catheter was placed using standard
    technique. The cuff was positioned in the subcutaneous tissue. 1.2 L of
    bloody pleural fluid was drained.

    FINDINGS: Successful stent placement with restoration of airway patency.
    IPC functioning well with good drainage.

    SPECIMENS: Tumor tissue to pathology
    """

    def test_stent_code_present(self, coder):
        """Test that bronchial stent placement is coded.

        Per CPT coding rules:
        - 31631 = Tracheal stent
        - 31636 = Bronchial stent (initial bronchus)
        - +31637 = Each additional major bronchus stented

        Since this note describes a stent in the right mainstem bronchus,
        31636 is the correct code.
        """
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31636" in billed_cpts, \
            "31636 (bronchial stent) should be coded - metallic stent was deployed in right mainstem bronchus"

    def test_ipc_insertion_present(self, coder):
        """Test that IPC insertion is coded (separate anatomic site)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32550" in billed_cpts, \
            "32550 (IPC insertion) should be coded - PleurX catheter was placed"

    def test_therapeutic_aspiration_present(self, coder):
        """Test that therapeutic aspiration is coded (distinct service)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31645" in billed_cpts, \
            "31645 (therapeutic aspiration) should be coded - extensive suctioning beyond stent work"

    def test_debulking_bundled_into_stent(self, coder):
        """Test that tumor debulking codes are NOT separate (bundled into stent)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        bundled_check = result.get("bundled_codes", [])
        bundled_cpts = {b["bundled_cpt"] for b in bundled_check}

        # 31640/31641 should either be bundled or not generated at all
        assert "31640" not in billed_cpts and "31641" not in billed_cpts, \
            "31640/31641 should NOT be billed separately - debulking to facilitate stent is bundled into 31636"

    def test_dilation_bundled_into_stent(self, coder):
        """Test that balloon dilation is NOT separate (bundled into stent)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31630" not in billed_cpts, \
            "31630 (dilation) should NOT be billed - pre-stent dilation is bundled into 31636"

    def test_ipc_removal_not_present(self, coder):
        """Test that IPC removal is NOT coded (insertion only)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32552" not in billed_cpts, \
            "32552 (IPC removal) should NOT be coded - only insertion was performed"

    def test_bal_not_present(self, coder):
        """Test that BAL is NOT coded (no lavage)."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31624" not in billed_cpts, \
            "31624 (BAL) should NOT be coded - suctioning is not BAL"

    def test_phantom_stent_codes_not_present(self, coder):
        """Test that incorrect stent codes are NOT generated.

        Per CPT coding rules:
        - 31631 = Tracheal stent (NOT applicable - stent is in bronchus)
        - 31636 = Bronchial stent (CORRECT - this is what should be coded)
        - +31637 = Each additional major bronchus (NOT applicable - single stent)
        - 31638 = Stent revision (NOT applicable - new placement)
        """
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IPC_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        # 31631 is for TRACHEAL stent - not applicable for bronchial stent
        assert "31631" not in billed_cpts, "31631 (tracheal stent) not applicable - stent is in bronchus"
        # +31637 is for each additional major bronchus stented - single stent here
        assert "31637" not in billed_cpts, "+31637 (additional bronchus) not applicable - single stent"
        # 31638 is for stent revision - this is new placement
        assert "31638" not in billed_cpts, "31638 (stent revision) not applicable - new placement"


class TestStandaloneTumorDebulking:
    """
    Test for standalone tumor debulking WITHOUT stent placement.

    When ablation/debulking is the primary service (not to facilitate stent),
    31641 should be coded.
    """

    NOTE_TEXT_STANDALONE_DEBULKING = """
    PROCEDURE: Rigid bronchoscopy with APC ablation of endobronchial tumor.

    INDICATION: Large cell carcinoma with near-complete occlusion of left mainstem.

    TECHNIQUE: Rigid bronchoscope inserted. Large exophytic tumor visualized
    causing 90% obstruction of the left mainstem bronchus.

    Argon plasma coagulation was performed at 60W with multiple applications
    to debulk and ablate the tumor mass. Approximately 70% of the visible
    tumor was destroyed.

    FINDINGS: Airway restored to approximately 75% patency after debulking.
    No stent was placed at this time - patient to return for possible stent
    if tumor regrows.
    """

    def test_debulking_code_present(self, coder):
        """Test that 31641 is coded for standalone tumor destruction."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STANDALONE_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31641" in billed_cpts, \
            "31641 (tumor destruction) should be coded for APC ablation"

    def test_stent_codes_not_present(self, coder):
        """Test that NO stent codes are generated."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STANDALONE_DEBULKING})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        stent_codes = {"31631", "31636", "31637", "31638"}
        assert not (billed_cpts & stent_codes), \
            "No stent codes should be present - no stent was placed"


class TestBALOnlyProcedure:
    """
    Test for BAL as the primary procedure.

    31624 should only be coded when:
    - Explicit "bronchoalveolar lavage" or "BAL" mention
    - Proper context (not just suctioning)
    """

    NOTE_TEXT_BAL_PROCEDURE = """
    PROCEDURE: Diagnostic bronchoscopy with bronchoalveolar lavage.

    INDICATION: Evaluation of diffuse ground glass opacities, rule out
    opportunistic infection in immunocompromised patient.

    TECHNIQUE: Flexible bronchoscopy performed via oral route.
    Airways inspected - no endobronchial lesions seen.

    Bronchoalveolar lavage was performed in the left lower lobe.
    Instilled 60 cc of sterile saline in 3 aliquots, recovered 30 cc
    of slightly turbid fluid.

    BAL fluid sent for cell count, cultures, and cytology.

    FINDINGS: Normal airway anatomy. BAL completed without complication.
    """

    def test_bal_code_present(self, coder):
        """Test that 31624 is coded for explicit BAL."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_BAL_PROCEDURE})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31624" in billed_cpts, \
            "31624 (BAL) should be coded - explicit bronchoalveolar lavage documented"


class TestIPCInsertionOnly:
    """
    Test for IPC insertion only (no removal).
    """

    NOTE_TEXT_IPC_INSERTION = """
    PROCEDURE: Ultrasound-guided tunneled PleurX catheter placement.

    INDICATION: Recurrent malignant right pleural effusion requiring drainage.

    TECHNIQUE: Under ultrasound guidance, the right pleural space was accessed.
    A tunneled PleurX catheter was placed using the standard technique.
    The subcutaneous cuff was positioned appropriately in the tunnel.
    The catheter was placed into the pleural space with good return of fluid.
    1.5 L of bloody pleural fluid was drained initially.

    FINDINGS: Successful PleurX catheter placement. Patient tolerated well.
    """

    def test_ipc_insertion_present(self, coder):
        """Test that 32550 is coded for IPC insertion."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_IPC_INSERTION})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32550" in billed_cpts, \
            "32550 (IPC insertion) should be coded - PleurX catheter placed"

    def test_ipc_removal_not_present(self, coder):
        """Test that 32552 is NOT coded."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_IPC_INSERTION})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "32552" not in billed_cpts, \
            "32552 (IPC removal) should NOT be coded - only insertion performed"


class TestMultiLobeEBUS:
    """
    Test for proper EBUS station code selection.
    """

    NOTE_TEXT_EBUS_3_STATIONS = """
    PROCEDURE: EBUS-TBNA for mediastinal staging.

    INDICATION: Newly diagnosed lung adenocarcinoma, staging.

    TECHNIQUE: Linear EBUS bronchoscope used for systematic mediastinal survey.
    EBUS-TBNA performed at stations 4R, 7, and 11R.
    Multiple passes at each station with ROSE confirmation.

    FINDINGS: Metastatic adenocarcinoma in station 7 and 11R. Station 4R negative.
    """

    def test_ebus_3_stations_code(self, coder):
        """Test that 31653 (3+ stations) is coded for 3 station EBUS."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_EBUS_3_STATIONS})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31653" in billed_cpts, \
            "31653 (EBUS 3+ stations) should be coded - 3 stations sampled"
        assert "31652" not in billed_cpts, \
            "31652 (EBUS 1-2 stations) should NOT be coded when 31653 applies"

    NOTE_TEXT_EBUS_2_STATIONS = """
    PROCEDURE: EBUS-TBNA.

    INDICATION: Mediastinal adenopathy.

    TECHNIQUE: EBUS-TBNA performed at stations 4R and 7.

    FINDINGS: Non-caseating granulomas consistent with sarcoidosis.
    """

    def test_ebus_2_stations_code(self, coder):
        """Test that 31652 (1-2 stations) is coded for 2 station EBUS."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_EBUS_2_STATIONS})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        assert "31652" in billed_cpts, \
            "31652 (EBUS 1-2 stations) should be coded - 2 stations sampled"
        assert "31653" not in billed_cpts, \
            "31653 (EBUS 3+ stations) should NOT be coded for only 2 stations"


class TestNoPhantomStentFromIndications:
    """
    Test that stent codes are NOT triggered by stent mention in indications only.
    """

    NOTE_TEXT_STENT_IN_INDICATIONS_ONLY = """
    PROCEDURE: Diagnostic bronchoscopy for airway evaluation.

    INDICATION: Post-intubation tracheal stenosis. Evaluate for possible
    future stent placement.

    TECHNIQUE: Flexible bronchoscopy performed.
    Moderate subglottic stenosis noted, approximately 40% narrowing.
    No intervention performed today.

    PLAN: Schedule for balloon dilation +/- stent placement next week.
    """

    def test_no_stent_from_indication(self, coder):
        """Test that stent codes are NOT generated from indication/plan only."""
        result = coder.code_procedure({"note_text": self.NOTE_TEXT_STENT_IN_INDICATIONS_ONLY})
        billed_cpts = {c["cpt"].lstrip("+") for c in result["codes"]}

        stent_codes = {"31631", "31636", "31637", "31638"}
        assert not (billed_cpts & stent_codes), \
            f"PHANTOM STENT CODES detected: {billed_cpts & stent_codes}. " \
            "Stent was only mentioned in indication/plan, not actually placed!"
