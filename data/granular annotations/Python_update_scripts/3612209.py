#!/usr/bin/env python3
"""Blank patient update script (auto-generated).

Source JSON: data/knowledge/patient_note_texts/3612209.json
"""


def main() -> None:
    # TODO: implement per-patient updates here
    pass


if __name__ == "__main__":
    main()
import sys
from pathlib import Path

# Set up the repository root to import the utility script
# This logic assumes the script is running in a subdirectory of the repo (e.g., /data_processing/)
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the 'add_case' function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from scripts.add_training_case.")
    print(f"Current REPO_ROOT: {REPO_ROOT}")
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
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return start, start + len(term)

# ==========================================
# Note 1: 3612209_syn_1
# ==========================================
t1 = """Action: Monarch to LLL (LB10).
Imaging: rEBUS adjacent.
Bx: 22G TBNA x6. Protected brush.
Wash: BAL LB10.
ROSE: Atypical/Suspicious.
Status: Stable."""
e1 = [
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t1, "Monarch", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t1, "LLL", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t1, "LB10", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t1, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t1, "22G", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t1, "TBNA", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t1, "x6", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t1, "Protected brush", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t1, "BAL", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t1, "LB10", 2)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t1, "Atypical/Suspicious", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 3612209_syn_2
# ==========================================
t2 = """PROCEDURE PERFORMED: Robotic-assisted bronchoscopy with electromagnetic navigation. The target was a 14mm nodule in the posterior-basal segment of the LLL. Registration error was 2.2mm. Upon reaching the target, radial EBUS confirmed an adjacent relationship. Diagnostic maneuvers included Transbronchial Needle Aspiration (22G, 6 passes) and Protected Cytology Brushing. Bronchoalveolar lavage was also obtained. Cytopathology review suggests malignancy."""
e2 = [
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t2, "Robotic-assisted", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t2, "bronchoscopy", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t2, "electromagnetic navigation", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t2, "14mm", 1)))},
    {"label": "OBS_LESION",     **dict(zip(["start", "end"], get_span(t2, "nodule", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t2, "posterior-basal segment of the LLL", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t2, "2.2mm", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t2, "radial EBUS", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t2, "Transbronchial Needle Aspiration", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t2, "22G", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t2, "6", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t2, "Protected Cytology Brushing", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t2, "Bronchoalveolar lavage", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t2, "malignancy", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 3612209_syn_3
# ==========================================
t3 = """Billing 31629 (TBNA), 31623 (Brush), 31627 (Nav), 31654 (EBUS), 31624 (BAL). Navigation utilized to reach LB10. Continuous visualization used for 6 needle passes and brushing. rEBUS confirmed target."""
e3 = [
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t3, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t3, "Brush", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t3, "Nav", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t3, "EBUS", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t3, "BAL", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t3, "Navigation", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t3, "LB10", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t3, "6", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t3, "needle", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t3, "brushing", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t3, "rEBUS", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 3612209_syn_4
# ==========================================
t4 = """Procedure Log: LLL Biopsy.
Method: Monarch Robot.
Target: 14mm nodule.
1. Registration (2.2mm).
2. Nav to LB10.
3. rEBUS (Adjacent).
4. 22G Needle x 6.
5. Brush.
6. BAL.
Result: ROSE suspicious."""
e4 = [
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t4, "LLL", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t4, "Biopsy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t4, "Monarch Robot", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t4, "14mm", 1)))},
    {"label": "OBS_LESION",     **dict(zip(["start", "end"], get_span(t4, "nodule", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t4, "2.2mm", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t4, "Nav", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t4, "LB10", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t4, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t4, "22G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t4, "Needle", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t4, "6", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t4, "Brush", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t4, "BAL", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t4, "suspicious", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 3612209_syn_5
# ==========================================
t5 = """ryan williams bronchoscopy robotic lll nodule 14mm navigated to lb10 error 2.2mm rebus adjacent used 22g needle 6 times then the brush bal done rose says suspicious for cancer no bleeding pt did great."""
e5 = [
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t5, "bronchoscopy", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t5, "robotic", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t5, "lll", 1)))},
    {"label": "OBS_LESION",     **dict(zip(["start", "end"], get_span(t5, "nodule", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t5, "14mm", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t5, "navigated", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t5, "lb10", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t5, "2.2mm", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t5, "rebus", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t5, "22g", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t5, "needle", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t5, "6", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t5, "brush", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t5, "bal", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t5, "suspicious for cancer", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t5, "no bleeding", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 3612209_syn_6
# ==========================================
t6 = """General anesthesia was induced. The Monarch robotic endoscope was inserted. Electromagnetic registration was completed. The device was navigated to the LLL posterior-basal segment. rEBUS view was adjacent. 22G TBNA was performed for 6 passes. Protected cytology brushings were obtained. BAL was performed. ROSE showed atypical cells suspicious for malignancy. The patient was extubated and stable."""
e6 = [
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t6, "Monarch robotic endoscope", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t6, "Electromagnetic registration", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t6, "LLL posterior-basal segment", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t6, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t6, "22G", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t6, "TBNA", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t6, "6", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t6, "Protected cytology brushings", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t6, "BAL", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t6, "atypical cells suspicious for malignancy", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 3612209_syn_7
# ==========================================
t7 = """[Indication] 14mm LLL nodule.
[Anesthesia] General.
[Description] Robotic nav to LB10. rEBUS adjacent. 22G TBNA x6. Brush biopsy. BAL. ROSE suspicious.
[Plan] Monitor. Discharge."""
e7 = [
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t7, "14mm", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t7, "LLL", 1)))},
    {"label": "OBS_LESION",     **dict(zip(["start", "end"], get_span(t7, "nodule", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t7, "Robotic nav", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t7, "LB10", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t7, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t7, "22G", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t7, "TBNA", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t7, "x6", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t7, "Brush biopsy", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t7, "BAL", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t7, "suspicious", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 3612209_syn_8
# ==========================================
t8 = """We successfully navigated the robotic scope to the posterior-basal segment of the left lower lobe. The registration was highly accurate. Radial EBUS imaging showed the lesion adjacent to the airway. We collected samples using a 22-gauge needle for six passes and also utilized a protected cytology brush. A lavage was performed at the site. The preliminary results indicated atypical cells."""
e8 = [
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t8, "robotic scope", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t8, "posterior-basal segment of the left lower lobe", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t8, "Radial EBUS", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t8, "22-gauge", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t8, "needle", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t8, "six", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t8, "protected cytology brush", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t8, "lavage", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t8, "atypical cells", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 3612209_syn_9
# ==========================================
t9 = """The robotic system was directed to the LLL. Registration deviation was 2.2mm. The instrument reached the LB10 bronchus. Ultrasound verification showed an adjacent lesion. Aspiration via 22G needle was conducted 6 times. Brushings were gathered under direct sight. Lavage was completed. Initial findings were wary for malignancy."""
e9 = [
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t9, "robotic system", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t9, "LLL", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t9, "2.2mm", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t9, "LB10", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t9, "Ultrasound", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t9, "Aspiration", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t9, "22G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t9, "needle", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t9, "6", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t9, "Brushings", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t9, "Lavage", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t9, "wary for malignancy", 1)))},
]
BATCH_DATA.append({"id": "3612209_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 3612209
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Christopher Brown
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Multiple pulmonary nodules - dominant lesion biopsy
Target: 14mm nodule in LLL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PRVC\t10\t353\t14\t80\t8\t24

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 2.2mm.

The device was navigated to the LLL. The outer sheath was parked and locked at the ostium of the segmental airway (LB10) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Posterior-Basal Segment of LLL.

Radial EBUS performed via the working channel. rEBUS view: Adjacent. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 22G aspiration needle under direct endoscopic and fluoroscopic guidance. 6 passes performed. Samples sent for Cytology and Cell block.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

Bronchoalveolar lavage performed at LB10. 40mL NS instilled with 14mL return. Sent for Cell count, Culture, and Cytology.

ROSE Result: Atypical cells present, suspicious for malignancy

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Brown, MD"""
e10 = [
    {"label": "OBS_LESION",     **dict(zip(["start", "end"], get_span(t10, "nodules", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t10, "biopsy", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t10, "14mm", 1)))},
    {"label": "OBS_LESION",     **dict(zip(["start", "end"], get_span(t10, "nodule", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t10, "LLL", 1)))},
    {"label": "ANAT_AIRWAY",    **dict(zip(["start", "end"], get_span(t10, "trachea", 1)))},
    {"label": "ANAT_AIRWAY",    **dict(zip(["start", "end"], get_span(t10, "carina", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "Monarch robotic endoscope", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t10, "Electromagnetic registration", 1)))},
    {"label": "ANAT_AIRWAY",    **dict(zip(["start", "end"], get_span(t10, "main carina", 1)))},
    {"label": "ANAT_AIRWAY",    **dict(zip(["start", "end"], get_span(t10, "right and left mainstem bronchi", 1)))},
    {"label": "ANAT_AIRWAY",    **dict(zip(["start", "end"], get_span(t10, "lobar carinas", 1)))},
    {"label": "MEAS_SIZE",      **dict(zip(["start", "end"], get_span(t10, "2.2mm", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t10, "LLL", 2)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t10, "LB10", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t10, "Posterior-Basal Segment of LLL", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t10, "Radial EBUS", 1)))},
    {"label": "PROC_METHOD",    **dict(zip(["start", "end"], get_span(t10, "rEBUS", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t10, "Transbronchial needle aspiration", 1)))},
    {"label": "DEV_NEEDLE",     **dict(zip(["start", "end"], get_span(t10, "22G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "aspiration needle", 1)))},
    {"label": "MEAS_COUNT",     **dict(zip(["start", "end"], get_span(t10, "6", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t10, "Protected cytology brushings", 1)))},
    {"label": "PROC_ACTION",    **dict(zip(["start", "end"], get_span(t10, "Bronchoalveolar lavage", 1)))},
    {"label": "ANAT_LUNG_LOC",  **dict(zip(["start", "end"], get_span(t10, "LB10", 2)))},
    {"label": "MEAS_VOL",       **dict(zip(["start", "end"], get_span(t10, "40mL", 1)))},
    {"label": "MEAS_VOL",       **dict(zip(["start", "end"], get_span(t10, "14mL", 1)))},
    {"label": "OBS_ROSE",       **dict(zip(["start", "end"], get_span(t10, "Atypical cells present, suspicious for malignancy", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t10, "no significant bleeding", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t10, "No immediate complications", 1)))},
]
BATCH_DATA.append({"id": "3612209", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)