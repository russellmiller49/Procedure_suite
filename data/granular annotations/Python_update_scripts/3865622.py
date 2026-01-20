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
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text: {text[:50]}...")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# 3. Data Definitions
# ==========================================

# --- Case 1: 3865622_syn_1 ---
id_1 = "3865622_syn_1"
text_1 = """Target: 31mm RLL nodule.
Device: Galaxy, TiLT+.
Nav: 1.8cm divergence (positioning). Corrected.
rEBUS: Concentric.
Intervention: TBNA x6, Bx x5, Brush, Fiducial.
ROSE: Malignant (SqCC)."""
entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "31mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "TiLT+", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "SqCC", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# --- Case 2: 3865622_syn_2 ---
id_2 = "3865622_syn_2"
text_2 = """OPERATIVE NOTE: [REDACTED] biopsy of a 31mm RLL nodule. The Galaxy system was used. TiLT+ tomosynthesis revealed a 1.8cm divergence due to patient positioning, which was corrected intra-operatively. rEBUS showed a concentric view. We performed TBNA, forceps biopsy, and brushing. A fiducial was placed for SBRT planning. ROSE confirmed squamous cell carcinoma."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "31mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Galaxy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "TiLT+ tomosynthesis", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "forceps biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "brushing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# --- Case 3: 3865622_syn_3 ---
id_3 = "3865622_syn_3"
text_3 = """Codes: 31626 (Marker), 31629 (TBNA), 31623 (Brush), 31627 (Nav), 31654 (rEBUS).
Note: High complexity. TiLT+ required to correct 1.8cm positioning divergence."""
entities_3 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Marker", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "divergence", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# --- Case 4: 3865622_syn_4 ---
id_4 = "3865622_syn_4"
text_4 = """Resident Note
Pt: A. Brown
RLL Nodule 31mm
1. Galaxy nav RB9.
2. TiLT showed 1.8cm error.
3. Fixed target.
4. rEBUS concentric.
5. Samples + Fiducial.
6. ROSE: Cancer (SqCC)."""
entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "31mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Galaxy nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "concentric", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "Samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Cancer", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "SqCC", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# --- Case 5: 3865622_syn_5 ---
id_5 = "3865622_syn_5"
text_5 = """[REDACTED] rll nodule big one 31mm. galaxy robot. tilt spin showed 1.8cm divergence cause of how she was laying. fixed it. concentric ultrasound. six needle passes five forceps bites and a brush. put a marker in. rose is cancer squamous."""
entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "31mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "galaxy robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "tilt spin", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "divergence", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "concentric", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "six", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "five", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "squamous", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# --- Case 6: 3865622_syn_6 ---
id_6 = "3865622_syn_6"
text_6 = """Peripheral pulmonary nodule. 31mm nodule in RLL. General anesthesia. Noah Galaxy bronchoscope. Navigated to RB9. TiLT+ sweep revealed 1.8cm divergence. Target updated. rEBUS view: Concentric. TBNA (21G). Transbronchial forceps biopsy. Cytology brushings. Gold fiducial marker placed. ROSE Result: Malignant cells id[REDACTED], consistent with squamous cell carcinoma."""
entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "Peripheral pulmonary nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "31mm", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Noah Galaxy bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Transbronchial forceps biopsy", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "Cytology brushings", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Gold fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# --- Case 7: 3865622_syn_7 ---
id_7 = "3865622_syn_7"
text_7 = """[Indication]
31mm RLL nodule.
[Anesthesia]
GA.
[Description]
Galaxy nav. TiLT+ corrected 1.8cm divergence. rEBUS concentric. TBNA, Bx, Brush, Fiducial.
[Plan]
Oncology."""
entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "31mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Galaxy nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Bx", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Fiducial", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# --- Case 8: 3865622_syn_8 ---
id_8 = "3865622_syn_8"
text_8 = """[REDACTED] biopsy of her RLL nodule. The Galaxy system with TiLT+ id[REDACTED] a 1.8cm positioning error which we corrected. We obtained excellent samples and placed a fiducial marker. The preliminary pathology confirms squamous cell carcinoma."""
entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Galaxy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "1.8cm", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# --- Case 9: 3865622_syn_9 ---
id_9 = "3865622_syn_9"
text_9 = """Procedure: Robotic RLL biopsy and marking.
Correction: 1.8cm divergence fixed via TiLT+.
Sampling: Needle, forceps, brush.
Addition: Fiducial implanted.
Result: Squamous cell carcinoma."""
entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "marking", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "TiLT+", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "Needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "Squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# --- Case 10: 3865622 ---
id_10 = "3865622"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. James Rodriguez
Fellow: Dr. Maria Santos (PGY-6)

Indication: Peripheral pulmonary nodule
Target: 31mm nodule in RLL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
VCV	14	374	12	80	5	17

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the RLL (RB9) based on the pre-operative CT navigational plan. Registration accuracy: 2.3mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 1.8cm divergence between the pre-op CT target and the actual lesion location due to patient positioning.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Concentric.

Transbronchial needle aspiration performed with 21G needle. 6 passes obtained. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed. 5 specimens obtained under fluoroscopic guidance with TiLT overlay. Samples sent for Surgical Pathology.

Cytology brushings obtained. Samples sent for Cytology.

Gold fiducial marker placed under TiLT-augmented fluoroscopic guidance for SBRT planning.

ROSE Result: Malignant cells id[REDACTED], consistent with squamous cell carcinoma

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Rodriguez, MD"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Peripheral pulmonary nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "31mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Noah Galaxy bronchoscope", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "electromagnetic field generator", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB9", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.3mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Tool-in-Lesion Tomosynthesis (TiLT+)", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "C-arm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Intra-operative tomosynthesis (TiLT)", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6 passes", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Samples", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "5 specimens", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Samples", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "Cytology brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Samples", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Gold fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "squamous cell carcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Galaxy scope", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)