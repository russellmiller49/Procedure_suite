import sys
from pathlib import Path

# Set the root directory of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the system path to import the utility function
sys.path.append(str(REPO_ROOT))

# Import the add_case function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 694697_syn_1
# ==========================================
t1 = """Procedure: Ion Bronchoscopy RUL.
- Target: 27mm nodule Anterior Segment (RB3).
- Nav: Ion, 2.4mm error.
- Verify: rEBUS (eccentric), CBCT.
- Samples: 21G/23G TBNA x8, 1.1mm Cryo x5 (5s), BAL.
- ROSE: Granulomatous inflammation.
- Outcome: Stable."""

e1 = [
    {"label": "PROC_METHOD", **get_span(t1, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RB3", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion", 2)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CBCT", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "23G", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x8", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "1.1mm", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Cryo", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x5", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "5s", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Granulomatous inflammation", 1)},
]
BATCH_DATA.append({"id": "694697_syn_1", "text": t1, "entities": e1})


# ==========================================
# Note 2: 694697_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: Ms. [REDACTED] presented for biopsy of a 27mm RUL nodule. The Ion robotic platform was used to navigate to the Anterior Segment (RB3). Localization was confirmed with eccentric rEBUS and Cone Beam CT 3D reconstruction. Sampling included 8 needle passes (21G/23G), 5 cryobiopsies using a 1.1mm probe, and a bronchoalveolar lavage. ROSE results indicated granulomatous inflammation. The procedure was uncomplicated."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "27mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB3", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Cone Beam CT", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "8", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "cryobiopsies", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "1.1mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "probe", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "granulomatous inflammation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "uncomplicated", 1)},
]
BATCH_DATA.append({"id": "694697_syn_2", "text": t2, "entities": e2})


# ==========================================
# Note 3: 694697_syn_3
# ==========================================
t3 = """CPT Justification:
31629: TBNA x8 (21G/23G).
31628: Cryo x5 (1.1mm).
31624: BAL.
31627: Ion Navigation.
31654: rEBUS.
Site: RUL (RB3). Verification: CBCT/REBUS. Result: Granulomatous inflammation."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "x8", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "23G", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Cryo", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "x5", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "1.1mm", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "BAL", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RB3", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "CBCT", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "REBUS", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "Granulomatous inflammation", 1)},
]
BATCH_DATA.append({"id": "694697_syn_3", "text": t3, "entities": e3})


# ==========================================
# Note 4: 694697_syn_4
# ==========================================
t4 = """Fellow Note
Patient: [REDACTED]
Target: RUL Nodule
Steps:
1. GA/ETT.
2. Ion Nav to RB3.
3. rEBUS (eccentric) + CBCT confirmation.
4. TBNA: x8 passes.
5. Cryo: 1.1mm x 5 biopsies.
6. BAL: 40cc instilled.
7. ROSE: Granulomatous inflammation.
No complications."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB3", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x8", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Cryo", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "1.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "BAL", 1)},
    {"label": "MEAS_VOL", **get_span(t4, "40cc", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Granulomatous inflammation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No complications", 1)},
]
BATCH_DATA.append({"id": "694697_syn_4", "text": t4, "entities": e4})


# ==========================================
# Note 5: 694697_syn_5
# ==========================================
t5 = """Ashley Williams procedure note. RUL nodule 27mm. General anesthesia. Ion robot used to get to anterior segment. Eccentric view on rebus and confirmed with spin ct. Did 8 needle passes and 5 cryo biopsies plus a lavage. Rose said granulomas. Patient woke up fine."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "27mm", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "anterior segment", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "Eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rebus", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "spin ct", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "8", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "needle passes", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "cryo biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "granulomas", 1)},
]
BATCH_DATA.append({"id": "694697_syn_5", "text": t5, "entities": e5})


# ==========================================
# Note 6: 694697_syn_6
# ==========================================
t6 = """Ashley Williams. Ion Bronchoscopy. RUL Nodule (27mm). Nav to RB3. rEBUS: Eccentric. CBCT: Confirmed. Samples: 8x TBNA, 5x 1.1mm Cryo, BAL. ROSE: Granulomatous inflammation. Disposition: Stable."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "27mm", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RB3", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "Eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "CBCT", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "8x", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "5x", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "1.1mm", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Cryo", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "Granulomatous inflammation", 1)},
]
BATCH_DATA.append({"id": "694697_syn_6", "text": t6, "entities": e6})


# ==========================================
# Note 7: 694697_syn_7
# ==========================================
t7 = """[Indication]
Suspicious nodule RUL.
[Anesthesia]
General.
[Description]
Ion navigation to RB3. rEBUS eccentric + CBCT. Sampled via TBNA (x8), Cryo (x5), BAL. ROSE: Granulomatous inflammation.
[Plan]
Discharge."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB3", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x8", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Cryo", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x5", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "Granulomatous inflammation", 1)},
]
BATCH_DATA.append({"id": "694697_syn_7", "text": t7, "entities": e7})


# ==========================================
# Note 8: 694697_syn_8
# ==========================================
t8 = """[REDACTED] a robotic bronchoscopy for a 27mm nodule in the Right Upper Lobe. We navigated the Ion catheter to the Anterior Segment. We confirmed the location with an eccentric radial EBUS view and Cone Beam CT. We collected eight needle aspirates, five cryobiopsies using a 1.1mm probe, and performed a bronchoalveolar lavage. The on-site evaluation showed granulomatous inflammation."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "Right Upper Lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "Anterior Segment", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Cone Beam CT", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "eight", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "needle aspirates", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "five", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "cryobiopsies", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "1.1mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "probe", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "granulomatous inflammation", 1)},
]
BATCH_DATA.append({"id": "694697_syn_8", "text": t8, "entities": e8})


# ==========================================
# Note 9: 694697_syn_9
# ==========================================
t9 = """Procedure: Robotic bronchoscopy.
Target: RUL nodule.
Technique: Guided Ion catheter to RB3. Verified with rEBUS and CBCT. Aspirated with needles (8x). Biopsied with 1.1mm cryoprobe (5x). Lavaged. ROSE Result: Granulomatous. Patient stable."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RB3", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Aspirated", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "needles", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "8x", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Biopsied", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "1.1mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "5x", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Lavaged", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "Granulomatous", 1)},
]
BATCH_DATA.append({"id": "694697_syn_9", "text": t9, "entities": e9})


# ==========================================
# Note 10: 694697
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. James Rodriguez
Fellow: Dr. Kevin Patel (PGY-5)

Indication: Suspicious nodule with high Brock score
Target: 27mm nodule in RUL

PROCEDURE:

After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings:

The endotracheal tube is in good position. The visualized portion of the trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy are normal; there are no endobronchial lesions.

Successful therapeutic aspiration was performed to clean out the Carina, Left Carina (LC2), Right Mainstem, Left Mainstem, Bronchus Intermedius, RUL Carina (RC1), Trachea (Distal 1/3) from mucus.

CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target. The navigational plan was reviewed and verified. This was then loaded into robotic bronchoscopy platform.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t14\t325\t11\t80\t5\t16

Robotic navigation bronchoscopy was performed with Ion platform. Partial registration was used. Registration error: 2.4mm. Ion robotic catheter was used to engage the Anterior Segment of RUL (RB3). Target lesion is approximately 27mm in diameter. Under navigational guidance the Ion robotic catheter was advanced to 0.6cm away from the planned target.

Radial EBUS was performed to confirm lesion location. rEBUS view: Eccentric. Continuous margin noted.

Needle was advanced into the lesion. Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation. Cios Spin system was used for evaluation of nodule location. Low dose spin was performed to acquire CT imaging. This was passed on to Ion platform system for reconstruction and nodule location. The 3D images were interpreted on an independent workstation (Ion). I personally interpreted the cone beam CT and 3-D reconstruction.

Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location. Vision probe removed for biopsy; catheter position maintained via shape-sensing lock. Repeat imaging confirmed tool-in-lesion.

Transbronchial needle aspiration was performed with 21G and 23G Needle through the extended working channel catheter. Total 8 samples were collected. Samples sent for Cytology and Cell block.

Transbronchial cryobiopsy was performed with 1.1mm cryoprobe via the extended working channel catheter. Freeze time of 5 seconds was used. Total 5 samples were collected. Samples sent for Pathology.

Bronchoalveolar lavage was performed at Anterior Segment of RUL (RB3). Instilled 40cc of NS, suction returned with 12cc of NS. Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

ROSE Result: Granulomatous inflammation

Vision probe was re-inserted to inspect the airway. No significant bleeding observed. The catheter was retracted. Final airway inspection showed no complications.

The patient tolerated the procedure well without immediate complications.

DISPOSITION: Recovery, then discharge if stable. CXR to rule out pneumothorax.
Follow-up: Results conference in 5-7 days.

Rodriguez, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "aspiration", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LC2", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Bronchus Intermedius", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RUL Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RC1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Robotic", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "navigation", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB3", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "27mm", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "robotic", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Cone Beam CT", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Cios Spin", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion", 4)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion", 5)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion", 6)},
    {"label": "PROC_METHOD", **get_span(t10, "robotic", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "8", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.1mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "cryoprobe", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "5 seconds", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Anterior Segment", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB3", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "40cc", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "12cc", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Granulomatous inflammation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "without immediate complications", 1)},
]
BATCH_DATA.append({"id": "694697", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)