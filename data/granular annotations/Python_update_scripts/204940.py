import sys
from pathlib import Path

# Set the root directory of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the add_case utility
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is running from the correct repository structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a tuple (start, end).
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
    return start, start + len(term)

# ==========================================
# Note 1: 204940_syn_1
# ==========================================
id_1 = "204940_syn_1"
text_1 = """Indication: 9mm RLL nodule.
System: Galaxy.
Verif: Fluoro + rEBUS (Concentric).
Action: TBNA x4, Bx x6, Brush, BAL (RB10).
ROSE: Negative."""
entities_1 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "9mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "nodule", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "Galaxy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "Fluoro", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "TBNA", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x4", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "Bx", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x6", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "Brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "BAL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RB10", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "Negative", 1)))},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 204940_syn_2
# ==========================================
id_2 = "204940_syn_2"
text_2 = """PROCEDURE: A 9mm RLL nodule was investigated using the Galaxy robotic scope. Navigation to RB10 was verified with fluoroscopy and a concentric rEBUS view. Diagnostic maneuvers included TBNA, forceps biopsy, brushing, and a bronchoalveolar lavage (BAL) of the target segment. ROSE was negative for malignancy."""
entities_2 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_2, "9mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_2, "RLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "nodule", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "Galaxy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "robotic scope", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_2, "RB10", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "fluoroscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "biopsy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "brushing", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "bronchoalveolar lavage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "BAL", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_2, "negative", 1)))},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 204940_syn_3
# ==========================================
id_3 = "204940_syn_3"
text_3 = """Codes: 31629 (TBNA), 31624 (BAL), 31623 (Brush), 31627 (Nav), 31654 (rEBUS).
Target: RLL (RB10).
Note: BAL performed for culture/cytology."""
entities_3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "TBNA", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "BAL", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "Brush", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "Nav", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "rEBUS", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_3, "RLL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_3, "RB10", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "BAL", 2)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_3, "cytology", 1)))},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 204940_syn_4
# ==========================================
id_4 = "204940_syn_4"
text_4 = """Resident Note
Pt: [REDACTED]
RLL 9mm
1. Galaxy to RB10.
2. Fluoro ok.
3. rEBUS concentric.
4. TBNA, Bx, Brush.
5. BAL performed.
6. ROSE negative."""
entities_4 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_4, "RLL", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_4, "9mm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_4, "Galaxy", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_4, "RB10", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_4, "Fluoro", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_4, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "TBNA", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Bx", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "BAL", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_4, "negative", 1)))},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 204940_syn_5
# ==========================================
id_5 = "204940_syn_5"
text_5 = """[REDACTED] rll nodule 9mm. galaxy robot. fluoroscopy check good. concentric rebus. did needle forceps brush and a wash bal. rose said no cancer seen."""
entities_5 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_5, "rll", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "nodule", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_5, "9mm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_5, "galaxy robot", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_5, "fluoroscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_5, "rebus", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "needle", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_5, "wash", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_5, "bal", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_5, "no cancer seen", 1)))},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 204940_syn_6
# ==========================================
id_6 = "204940_syn_6"
text_6 = """Peripheral pulmonary nodule. 9mm nodule in RLL. General anesthesia. Noah Galaxy bronchoscope. Navigated to RB10. Fluoroscopic guidance used. rEBUS view: Concentric. TBNA (22G). Transbronchial forceps biopsy. Cytology brushings. Bronchoalveolar lavage performed. ROSE Result: No evidence of malignant neoplasm."""
entities_6 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "Peripheral pulmonary nodule", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_6, "9mm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "nodule", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "RLL", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "Noah Galaxy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "bronchoscope", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "RB10", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "Fluoroscopic", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "TBNA", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_6, "22G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "biopsy", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_6, "Cytology", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "brushings", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "Bronchoalveolar lavage", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_6, "No evidence of malignant neoplasm", 1)))},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 204940_syn_7
# ==========================================
id_7 = "204940_syn_7"
text_7 = """[Indication]
9mm RLL nodule.
[Anesthesia]
GA.
[Description]
Galaxy nav RB10. Fluoro/rEBUS concentric. TBNA, Bx, Brush, BAL performed.
[Plan]
CXR, discharge."""
entities_7 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_7, "9mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_7, "RLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "nodule", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "Galaxy", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_7, "RB10", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "Fluoro", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "TBNA", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "Bx", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "Brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "BAL", 1)))},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 204940_syn_8
# ==========================================
id_8 = "204940_syn_8"
text_8 = """[REDACTED] a robotic biopsy of her small RLL nodule. We used the Galaxy system, confirmed position with fluoroscopy and ultrasound, and took samples including a lung wash (BAL). Preliminary results are negative."""
entities_8 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "robotic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "biopsy", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_8, "RLL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "nodule", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "Galaxy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "fluoroscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "ultrasound", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "lung wash", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "BAL", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_8, "negative", 1)))},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 204940_syn_9
# ==========================================
id_9 = "204940_syn_9"
text_9 = """Task: Robotic RLL sampling.
Methods: TBNA, forceps, brush, BAL.
Guidance: Galaxy, Fluoro, rEBUS (concentric).
Result: ROSE negative."""
entities_9 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "Robotic", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_9, "RLL", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "BAL", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "Galaxy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "Fluoro", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "rEBUS", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_9, "negative", 1)))},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 204940
# ==========================================
id_10 = "204940"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Michael Chen

Indication: Peripheral pulmonary nodule
Target: 9mm nodule in RLL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PCV	13	399	17	80	8	17

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the RLL (RB10) based on the pre-operative CT navigational plan. Registration accuracy: 2.1mm.

Fluoroscopic guidance used to confirm scope position relative to target. Navigation alignment confirmed.

Radial EBUS performed to confirm lesion location. rEBUS view: Concentric.

Transbronchial needle aspiration performed with 22G needle. 4 passes obtained. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed. 6 specimens obtained under fluoroscopic guidance with TiLT overlay. Samples sent for Surgical Pathology.

Cytology brushings obtained. Samples sent for Cytology.

Bronchoalveolar lavage performed at target segment. 40mL instilled, 12mL return. Sent for Cytology and Culture.

ROSE Result: No evidence of malignant neoplasm

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Chen, MD"""
entities_10 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "Peripheral pulmonary nodule", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_10, "9mm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "nodule", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RLL", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "Trachea", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "carina", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "Noah Galaxy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "bronchoscope", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "electromagnetic", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RLL", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RB10", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "Fluoroscopic", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "Radial EBUS", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Transbronchial needle aspiration", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_10, "22G", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_10, "4 passes", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "Cytology", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "Cell block", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Transbronchial forceps biopsy", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_10, "6 specimens", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "Cytology", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "brushings", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "Cytology", 3)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Bronchoalveolar lavage", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_10, "40mL", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_10, "12mL", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "Cytology", 4)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_10, "No evidence of malignant neoplasm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "Galaxy", 2)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "scope", 2)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_10, "No immediate complications", 1)))},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)