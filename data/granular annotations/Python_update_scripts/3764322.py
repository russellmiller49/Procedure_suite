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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 3764322_syn_1
# ------------------------------------------
id_1 = "3764322_syn_1"
text_1 = """Target: 20mm LUL (LB3).
Method: Monarch.
rEBUS: Eccentric.
Bx: 19G TBNA x8, Forceps x5.
Wash: BAL LB3.
ROSE: Benign."""
entities_1 = [
    {"label": "MEAS_SIZE",      **get_span(text_1, "20mm", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "LB3", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_1, "Eccentric", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_1, "19G", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "5", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "LB3", 2)},
    {"label": "OBS_ROSE",       **get_span(text_1, "Benign", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 3764322_syn_2
# ------------------------------------------
id_2 = "3764322_syn_2"
text_2 = """OPERATIVE REPORT: Robotic bronchoscopy for 20mm LUL nodule. Navigation to Anterior Segment (LB3) achieved with 2.3mm error. rEBUS demonstrated eccentric view. 19G TBNA (8 passes) and Forceps Biopsy (5 specimens) performed under continuous visualization. BAL completed. ROSE was negative for malignancy."""
entities_2 = [
    {"label": "PROC_METHOD",    **get_span(text_2, "Robotic", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_2, "20mm", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "LUL", 1)},
    {"label": "OBS_LESION",     **get_span(text_2, "nodule", 1)},
    {"label": "PROC_METHOD",    **get_span(text_2, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "LB3", 1)},
    {"label": "PROC_METHOD",    **get_span(text_2, "rEBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_2, "eccentric", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_2, "19G", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "TBNA", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_2, "8 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Forceps", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "Biopsy", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_2, "5 specimens", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "BAL", 1)},
    {"label": "OBS_ROSE",       **get_span(text_2, "negative for malignancy", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 3764322_syn_3
# ------------------------------------------
id_3 = "3764322_syn_3"
text_3 = """Codes: 31629, 31628, 31627, 31654, 31624. Note: High number of needle passes (8). Forceps used. Navigated to LUL. rEBUS eccentric."""
entities_3 = [
    {"label": "DEV_NEEDLE",     **get_span(text_3, "needle", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_3, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Forceps", 1)},
    {"label": "PROC_METHOD",    **get_span(text_3, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_3, "LUL", 1)},
    {"label": "PROC_METHOD",    **get_span(text_3, "rEBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_3, "eccentric", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 3764322_syn_4
# ------------------------------------------
id_4 = "3764322_syn_4"
text_4 = """Resident Note: LUL Biopsy.
Monarch Robot.
1. Nav to LB3.
2. rEBUS Eccentric.
3. 19G Needle x 8.
4. Forceps x 5.
5. BAL.
ROSE: Neg for malignancy."""
entities_4 = [
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "LUL", 1)},
    {"label": "PROC_ACTION",    **get_span(text_4, "Biopsy", 1)},
    {"label": "PROC_METHOD",    **get_span(text_4, "Monarch Robot", 1)},
    {"label": "PROC_METHOD",    **get_span(text_4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "LB3", 1)},
    {"label": "PROC_METHOD",    **get_span(text_4, "rEBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_4, "Eccentric", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_4, "19G", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_4, "Needle", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_4, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_4, "5", 1)},
    {"label": "PROC_ACTION",    **get_span(text_4, "BAL", 1)},
    {"label": "OBS_ROSE",       **get_span(text_4, "Neg for malignancy", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 3764322_syn_5
# ------------------------------------------
id_5 = "3764322_syn_5"
text_5 = """jonathan adams lul nodule 20mm monarch robot navigation good 2.3mm error rebus eccentric 19g needle 8 times forceps 5 times bal done rose benign no cancer seen."""
entities_5 = [
    {"label": "ANAT_LUNG_LOC",  **get_span(text_5, "lul", 1)},
    {"label": "OBS_LESION",     **get_span(text_5, "nodule", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_5, "20mm", 1)},
    {"label": "PROC_METHOD",    **get_span(text_5, "monarch robot", 1)},
    {"label": "PROC_METHOD",    **get_span(text_5, "navigation", 1)},
    {"label": "PROC_METHOD",    **get_span(text_5, "rebus", 1)},
    {"label": "OBS_FINDING",    **get_span(text_5, "eccentric", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_5, "19g", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_5, "needle", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_5, "8 times", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_5, "5 times", 1)},
    {"label": "PROC_ACTION",    **get_span(text_5, "bal", 1)},
    {"label": "OBS_ROSE",       **get_span(text_5, "benign", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 3764322_syn_6
# ------------------------------------------
id_6 = "3764322_syn_6"
text_6 = """Anesthesia induced. Monarch robot navigated to LUL LB3. rEBUS eccentric. 19G TBNA x 8. Forceps x 5. BAL performed. ROSE negative for malignancy. Patient stable."""
entities_6 = [
    {"label": "PROC_METHOD",    **get_span(text_6, "Monarch robot", 1)},
    {"label": "PROC_METHOD",    **get_span(text_6, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_6, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_6, "LB3", 1)},
    {"label": "PROC_METHOD",    **get_span(text_6, "rEBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_6, "eccentric", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_6, "19G", 1)},
    {"label": "PROC_ACTION",    **get_span(text_6, "TBNA", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_6, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_6, "5", 1)},
    {"label": "PROC_ACTION",    **get_span(text_6, "BAL", 1)},
    {"label": "OBS_ROSE",       **get_span(text_6, "negative for malignancy", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 3764322_syn_7
# ------------------------------------------
id_7 = "3764322_syn_7"
text_7 = """[Indication] 20mm LUL nodule.
[Anesthesia] General.
[Description] Nav to LB3. rEBUS eccentric. 19G TBNA x8. Forceps x5. BAL. ROSE benign.
[Plan] Discharge."""
entities_7 = [
    {"label": "MEAS_SIZE",      **get_span(text_7, "20mm", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "LUL", 1)},
    {"label": "OBS_LESION",     **get_span(text_7, "nodule", 1)},
    {"label": "PROC_METHOD",    **get_span(text_7, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "LB3", 1)},
    {"label": "PROC_METHOD",    **get_span(text_7, "rEBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_7, "eccentric", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_7, "19G", 1)},
    {"label": "PROC_ACTION",    **get_span(text_7, "TBNA", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_7, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_7, "5", 1)},
    {"label": "PROC_ACTION",    **get_span(text_7, "BAL", 1)},
    {"label": "OBS_ROSE",       **get_span(text_7, "benign", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 3764322_syn_8
# ------------------------------------------
id_8 = "3764322_syn_8"
text_8 = """We used the Monarch robot to navigate to the anterior segment of the left upper lobe. The registration was very accurate. Radial EBUS showed an eccentric view of the 20mm nodule. We performed eight passes with a 19-gauge needle and took five forceps biopsies. A lavage was also performed. The on-site evaluation was negative for malignancy."""
entities_8 = [
    {"label": "PROC_METHOD",    **get_span(text_8, "Monarch robot", 1)},
    {"label": "PROC_METHOD",    **get_span(text_8, "navigate", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_8, "anterior segment", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_8, "left upper lobe", 1)},
    {"label": "PROC_METHOD",    **get_span(text_8, "Radial EBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_8, "eccentric", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_8, "20mm", 1)},
    {"label": "OBS_LESION",     **get_span(text_8, "nodule", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_8, "eight passes", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_8, "19-gauge", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_8, "needle", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_8, "five", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "forceps", 1)},
    {"label": "PROC_ACTION",    **get_span(text_8, "biopsies", 1)},
    {"label": "PROC_ACTION",    **get_span(text_8, "lavage", 1)},
    {"label": "OBS_ROSE",       **get_span(text_8, "negative for malignancy", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 3764322_syn_9
# ------------------------------------------
id_9 = "3764322_syn_9"
text_9 = """The robotic system was piloted to the LUL. Registration deviation was 2.3mm. The instrument reached LB3. Sonography indicated an eccentric mass. Aspiration via 19G needle was conducted 8 times. Tissue extraction via forceps occurred 5 times. Lavage was completed. Initial pathology was benign."""
entities_9 = [
    {"label": "PROC_METHOD",    **get_span(text_9, "robotic system", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_9, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_9, "LB3", 1)},
    {"label": "OBS_FINDING",    **get_span(text_9, "eccentric", 1)},
    {"label": "OBS_LESION",     **get_span(text_9, "mass", 1)},
    {"label": "PROC_ACTION",    **get_span(text_9, "Aspiration", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_9, "19G", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_9, "needle", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_9, "8 times", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_9, "5 times", 1)},
    {"label": "PROC_ACTION",    **get_span(text_9, "Lavage", 1)},
    {"label": "OBS_ROSE",       **get_span(text_9, "benign", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ------------------------------------------
# Case 10: 3764322
# ------------------------------------------
id_10 = "3764322"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: CDR Patricia Davis, MD
Fellow: LT Michelle Torres, MD (PGY-5)

Indication: Lung cancer screening detected nodule
Target: 20mm nodule in LUL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
VCV	12	321	8	80	5	20

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 2.3mm.

The device was navigated to the LUL. The outer sheath was parked and locked at the ostium of the segmental airway (LB3) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Anterior Segment of LUL.

Radial EBUS performed via the working channel. rEBUS view: Eccentric. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 19G aspiration needle under direct endoscopic and fluoroscopic guidance. 8 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 5 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Bronchoalveolar lavage performed at LB3. 40mL NS instilled with 18mL return. Sent for Cell count, Culture, and Cytology.

ROSE Result: No evidence of malignant neoplasm

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Davis, MD"""
entities_10 = [
    {"label": "OBS_LESION",     **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_10, "20mm", 1)},
    {"label": "OBS_LESION",     **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "LUL", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "Airway Inspection", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_10, "carina", 1)},
    {"label": "PROC_METHOD",    **get_span(text_10, "Monarch", 1)},
    {"label": "PROC_METHOD",    **get_span(text_10, "robotic", 1)},
    {"label": "PROC_METHOD",    **get_span(text_10, "Electromagnetic registration", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_10, "main carina", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "LB3", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "LUL", 3)},
    {"label": "PROC_METHOD",    **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",    **get_span(text_10, "rEBUS", 1)},
    {"label": "OBS_FINDING",    **get_span(text_10, "Eccentric", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_10, "19G", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_10, "aspiration needle", 1)},
    {"label": "PROC_METHOD",    **get_span(text_10, "fluoroscopic", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_10, "8 passes", 1)},
    {"label": "SPECIMEN",       **get_span(text_10, "Cytology", 1)},
    {"label": "SPECIMEN",       **get_span(text_10, "Cell block", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_10, "5 specimens", 1)},
    {"label": "SPECIMEN",       **get_span(text_10, "Surgical Pathology", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "LB3", 2)},
    {"label": "MEAS_VOL",       **get_span(text_10, "40mL", 1)},
    {"label": "MEAS_VOL",       **get_span(text_10, "18mL", 1)},
    {"label": "SPECIMEN",       **get_span(text_10, "Cell count", 1)},
    {"label": "SPECIMEN",       **get_span(text_10, "Culture", 1)},
    {"label": "SPECIMEN",       **get_span(text_10, "Cytology", 2)},
    {"label": "OBS_ROSE",       **get_span(text_10, "No evidence of malignant neoplasm", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "airway inspection", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)