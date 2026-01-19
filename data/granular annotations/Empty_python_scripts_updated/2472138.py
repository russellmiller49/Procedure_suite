import sys
from pathlib import Path

# Set up the repository root path (assuming script is running in a subdirectory of the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts module
# Ensure 'scripts' is a python package or in the python path
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback to local import or adjusting path if needed
    sys.path.append(str(REPO_ROOT))
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
# Case 1: 2472138_syn_1
# ==========================================
t1 = """Dx: Lung-RADS 4X, 22mm LUL.
Method: Galaxy Robot + TiLT+.
Findings: 1.5cm divergence on TiLT. Corrected.
rEBUS: Eccentric.
 intervention: TBNA x5, Forceps x7, Brush, Fiducial.
ROSE: Lymphocytes/benign."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "22mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Galaxy Robot", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "TiLT", 2)}, # "divergence on TiLT"
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "5", 1)}, # from x5
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "7", 1)}, # from x7
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Lymphocytes/benign", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_1", "text": t1, "entities": e1})

# ==========================================
# Case 2: 2472138_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: [REDACTED] biopsy of a 22mm LUL nodule. Under GA, the Galaxy bronchoscope was navigated to LB1+2. Intra-operative TiLT+ tomosynthesis revealed a 1.5cm divergence secondary to respiratory motion. Following target update, an eccentric rEBUS view was obtained. Diagnostic sampling included TBNA, forceps biopsy, and brushing. A fiducial marker was placed to facilitate SBRT if needed. ROSE cytology showed benign lymphocytes."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "22mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Galaxy bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "TiLT+ tomosynthesis", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "divergence", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 2)}, # forceps biopsy
    {"label": "PROC_ACTION", **get_span(t2, "brushing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "benign lymphocytes", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_2", "text": t2, "entities": e2})

# ==========================================
# Case 3: 2472138_syn_3
# ==========================================
t3 = """Code Selection:
31626 (Marker), 31629 (TBNA), 31623 (Brush). Add-ons: 31627 (Nav), 31654 (rEBUS).
Medical Necessity: 4X nodule requiring diagnosis and marking.
Tech: Galaxy robot with TiLT+ used to correct 1.5cm divergence."""

e3 = [
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Marker", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Galaxy robot", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "divergence", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_3", "text": t3, "entities": e3})

# ==========================================
# Case 4: 2472138_syn_4
# ==========================================
t4 = """Resident Note
Patient: S. Walker, 82F
Target: LUL 22mm
Steps:
1. Galaxy nav to LB1+2.
2. TiLT+ showed 1.5cm divergence.
3. Re-aligned.
4. rEBUS eccentric.
5. Samples: Needle, Forceps, Brush.
6. Fiducial placed.
ROSE: Benign so far."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LUL", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "22mm", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Galaxy nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "Needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Benign", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_4", "text": t4, "entities": e4})

# ==========================================
# Case 5: 2472138_syn_5
# ==========================================
t5 = """shirley walker 82 year old female lul nodule. used the galaxy system. tilt scan showed we were off by 1.5cm cause of breathing motion. fixed it. eccentric view on the radar. took a bunch of samples needle and forceps and brush. put a marker in just in case. rose says benign lymphocytes."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lul", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "galaxy system", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "tilt scan", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "marker", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "benign lymphocytes", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_5", "text": t5, "entities": e5})

# ==========================================
# Case 6: 2472138_syn_6
# ==========================================
t6 = """Lung-RADS 4X nodule. 22mm nodule in LUL. General anesthesia. Noah Galaxy bronchoscope. Navigated to LB1+2. TiLT+ sweep revealed 1.5cm divergence. Target updated. rEBUS view: Eccentric. TBNA performed. Transbronchial forceps biopsy performed. Cytology brushings obtained. Gold fiducial marker placed. ROSE Result: Lymphocytes and benign cells."""

e6 = [
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "22mm", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Noah Galaxy bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "TiLT+ sweep", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Cytology brushings", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Gold fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "Lymphocytes and benign cells", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_6", "text": t6, "entities": e6})

# ==========================================
# Case 7: 2472138_syn_7
# ==========================================
t7 = """[Indication]
22mm LUL nodule (4X).
[Anesthesia]
GA.
[Description]
Galaxy nav. TiLT+ corrected 1.5cm divergence. rEBUS eccentric. TBNA, Bx, Brush. Fiducial placed.
[Plan]
Wait for final path."""

e7 = [
    {"label": "MEAS_SIZE", **get_span(t7, "22mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Galaxy nav", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Bx", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Fiducial", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_7", "text": t7, "entities": e7})

# ==========================================
# Case 8: 2472138_syn_8
# ==========================================
t8 = """[REDACTED] a robotic biopsy of her left upper lobe nodule. Using the Galaxy system and TiLT+ technology, we id[REDACTED] and corrected a 1.5cm discrepancy in the target location caused by breathing. We obtained samples using a needle, forceps, and brush, and placed a fiducial marker. Preliminary results show benign cells."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Galaxy system", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "TiLT+ technology", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "discrepancy", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "benign cells", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_8", "text": t8, "entities": e8})

# ==========================================
# Case 9: 2472138_syn_9
# ==========================================
t9 = """Task: Robotic biopsy LUL.
Detail: Galaxy system used. TiLT+ rectified a 1.5cm divergence. rEBUS confirmed location (eccentric). We aspirated, biopsied, and brushed the lesion. A fiducial was deposited.
Pathology: ROSE showed lymphocytes."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Galaxy system", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "biopsied", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "brushed", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "lymphocytes", 1)},
]
BATCH_DATA.append({"id": "2472138_syn_9", "text": t9, "entities": e9})

# ==========================================
# Case 10: 2472138
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Lisa Anderson
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Lung-RADS 4X nodule
Target: 22mm nodule in LUL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PCV	11	392	9	80	6	16

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the LUL (LB1+2) based on the pre-operative CT navigational plan. Registration accuracy: 2.3mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 1.5cm divergence between the pre-op CT target and the actual lesion location due to respiratory motion.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Eccentric.

Transbronchial needle aspiration performed with 21G needle. 5 passes obtained. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed. 7 specimens obtained under fluoroscopic guidance with TiLT overlay. Samples sent for Surgical Pathology.

Cytology brushings obtained. Samples sent for Cytology.

Gold fiducial marker placed under TiLT-augmented fluoroscopic guidance for SBRT planning.

ROSE Result: Lymphocytes and benign cells, adequate for evaluation

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Anderson, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "22mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airways", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Noah Galaxy bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 2)}, # "introduced into the airway"
    {"label": "PROC_METHOD", **get_span(t10, "Navigational", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Tool-in-Lesion Tomosynthesis (TiLT+)", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "divergence", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Intra-operative tomosynthesis (TiLT)", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "TiLT", 2)}, # "corrected TiLT target"
    {"label": "PROC_METHOD", **get_span(t10, "TiLT", 3)}, # "TiLT system"
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 passes", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "7 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "fluoroscopic", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "TiLT", 4)}, # "TiLT overlay"
    {"label": "PROC_ACTION", **get_span(t10, "Cytology brushings", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Gold fiducial marker", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "TiLT", 5)}, # "TiLT-augmented"
    {"label": "PROC_METHOD", **get_span(t10, "fluoroscopic", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "Lymphocytes and benign cells", 1)},
]
BATCH_DATA.append({"id": "2472138", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)