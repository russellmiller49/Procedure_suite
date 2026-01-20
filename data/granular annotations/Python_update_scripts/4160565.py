import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4160565_syn_1
# ==========================================
id_1 = "4160565_syn_1"
text_1 = """Target: 27mm nodule LUL (LB1+2).
Proc: Ion Nav, rEBUS (Concentric), CBCT.
Actions: TBNA (x7), Cryo (x6), Fiducial, BAL.
ROSE: Squamous cell CA.
Comp: None."""
entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x7", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cryo", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Fiducial", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Squamous cell CA", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4160565_syn_2
# ==========================================
id_2 = "4160565_syn_2"
text_2 = """OPERATIVE REPORT: [REDACTED] bronchoscopy for a 27mm LUL nodule. The Ion catheter was navigated to the apicoposterior segment (LB1+2). Concentric radial EBUS and Cone Beam CT confirmed the target. We performed transbronchial needle aspiration and cryobiopsy. A gold fiducial marker was placed for potential SBRT. Bronchoalveolar lavage was also collected. ROSE confirmed squamous cell carcinoma."""
entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "27mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Ion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "apicoposterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "cryobiopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "gold fiducial marker", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4160565_syn_3
# ==========================================
id_3 = "4160565_syn_3"
text_3 = """Codes: 31626 (Fiducial), 31629 (TBNA), 31628 (Cryo), 31624 (BAL), +31627 (Nav), +31654 (rEBUS).
Location: LUL (LB1+2).
Details: 27mm lesion. Multi-modal sampling plus fiducial placement. CBCT used."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Fiducial", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Cryo", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "BAL", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "rEBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LB1+2", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "fiducial placement", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "CBCT", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4160565_syn_4
# ==========================================
id_4 = "4160565_syn_4"
text_4 = """Resident Note
Pt: [REDACTED]
Attending: Dr. Anderson

1. Nav to LUL LB1+2.
2. rEBUS concentric.
3. CBCT confirmed.
4. TBNA, Cryo, BAL performed.
5. Fiducial placed.
6. ROSE: Squamous cell.
7. Stable."""
entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Cryo", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Fiducial placed", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Squamous cell", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4160565_syn_5
# ==========================================
id_5 = "4160565_syn_5"
text_5 = """matthew young procedure note. 27mm nodule lul apicoposterior. used ion robot. radial ebus concentric. spin ct good. extensive sampling 7 needles 6 cryos. put in a fiducial too. did a bal. rose said squamous cell carcinoma. no bleeding."""
entities_5 = [
    {"label": "MEAS_SIZE", **get_span(text_5, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lul", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "apicoposterior", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ion robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "radial ebus", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "spin ct", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "needles", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "cryos", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fiducial", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "bal", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4160565_syn_6
# ==========================================
id_6 = "4160565_syn_6"
text_6 = """Robotic navigation bronchoscopy (Ion) for 27mm LUL nodule (LB1+2). Registration error 2.0mm. Radial EBUS: Concentric. Cone Beam CT: Confirmed. Sampling: TBNA (7 passes), Cryobiopsy (6 samples), BAL. Fiducial marker placed. ROSE: Squamous cell carcinoma. No complications."""
entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Robotic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Ion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "27mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "7 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Cryobiopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "6 samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "Squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4160565_syn_7
# ==========================================
id_7 = "4160565_syn_7"
text_7 = """[Indication]
Suspected malignancy, 27mm LUL.
[Anesthesia]
General.
[Description]
Ion nav to LB1+2. rEBUS: Concentric. CBCT: Confirmed.
- TBNA
- Cryo
- Fiducial placement
- BAL
ROSE: Squamous cell.
[Plan]
Oncology."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "malignancy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "27mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Ion nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Cryo", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Fiducial placement", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "Squamous cell", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4160565_syn_8
# ==========================================
id_8 = "4160565_syn_8"
text_8 = """[REDACTED] a 27mm nodule in the LUL. We used the Ion robot to reach the apicoposterior segment. Position was verified with concentric radial EBUS and Cone Beam CT. We took needle and cryobiopsy samples, placed a fiducial marker, and performed a lavage. The on-site pathologist id[REDACTED] squamous cell carcinoma."""
entities_8 = [
    {"label": "MEAS_SIZE", **get_span(text_8, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Ion robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "apicoposterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Cone Beam CT", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "cryobiopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "fiducial marker", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4160565_syn_9
# ==========================================
id_9 = "4160565_syn_9"
text_9 = """Operation: Robotic-assisted bronchoscopy.
Lesion: LUL Apicoposterior (LB1+2).
Validation: rEBUS (Concentric) and CBCT.
Actions: The lesion was sampled via needle, cryoprobe, and lavage. A fiducial was implanted. ROSE confirmed squamous cell carcinoma."""
entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic-assisted bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Apicoposterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "CBCT", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "cryoprobe", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "lavage", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4160565
# ==========================================
id_10 = "4160565"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Lisa Anderson
Fellow: LCDR Sarah Kim, MD (PGY-6)

Indication: Suspected lung malignancy
Target: 27mm nodule in LUL

PROCEDURE:

After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings:

The endotracheal tube is in good position. The visualized portion of the trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy are normal; there are no endobronchial lesions.

Successful therapeutic aspiration was performed to clean out the LUL Lingula Carina (LC1), Bronchus Intermedius, Right Mainstem, Left Mainstem, Carina, Left Carina (LC2) from mucus.

CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target. The navigational plan was reviewed and verified. This was then loaded into robotic bronchoscopy platform.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PRVC	14	300	13	80	6	22

Robotic navigation bronchoscopy was performed with Ion platform. Partial registration was used. Registration error: 2.0mm. Ion robotic catheter was used to engage the Apicoposterior Segment of LUL (LB1+2). Target lesion is approximately 27mm in diameter. Under navigational guidance the Ion robotic catheter was advanced to 1.9cm away from the planned target.

Radial EBUS was performed to confirm lesion location. rEBUS view: Concentric. Continuous margin noted.

Needle was advanced into the lesion. Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation. Cios Spin system was used for evaluation of nodule location. Low dose spin was performed to acquire CT imaging. This was passed on to Ion platform system for reconstruction and nodule location. The 3D images were interpreted on an independent workstation (Ion). I personally interpreted the cone beam CT and 3-D reconstruction.

Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location. Vision probe removed for biopsy; catheter position maintained via shape-sensing lock. Repeat imaging confirmed tool-in-lesion.

Transbronchial needle aspiration was performed with 21G and 23G Needle through the extended working channel catheter. Total 7 samples were collected. Samples sent for Cytology and Cell block.

Transbronchial cryobiopsy was performed with 1.7mm cryoprobe via the extended working channel catheter. Freeze time of 7 seconds was used. Total 6 samples were collected. Samples sent for Pathology.

Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.

Bronchoalveolar lavage was performed at Apicoposterior Segment of LUL (LB1+2). Instilled 60cc of NS, suction returned with 29cc of NS. Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

ROSE Result: Malignant cells id[REDACTED], consistent with squamous cell carcinoma

Vision probe was re-inserted to inspect the airway. No significant bleeding observed. The catheter was retracted. Final airway inspection showed no complications.

The patient tolerated the procedure well without immediate complications.

DISPOSITION: Recovery, then discharge if stable. CXR to rule out pneumothorax.
Follow-up: Results conference in 5-7 days.

Anderson, MD"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "lung malignancy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "tracheobronchial tree", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LC1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Bronchus Intermedius", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Right Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Left Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Carina", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Left Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LC2", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Robotic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Apicoposterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB1+2", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "27mm", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Cone Beam CT", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Cios Spin", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Vision probe", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "23G Needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "7 samples", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.7mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cryoprobe", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "7 seconds", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6 samples", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Pathology", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Fiducial marker", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "0.8mm x 3mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Apicoposterior Segment", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 4)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB1+2", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "60cc", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "29cc", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cytology", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "squamous cell carcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Vision probe", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no complications", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)