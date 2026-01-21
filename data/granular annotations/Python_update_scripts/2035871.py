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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2035871_syn_1
# ==========================================
t1 = """Ind: Malignant CAO, RLL.
Proc: Rigid bronch, Forceps debulk, Balloon dilation.
Action: Mech removal + dilation of stenosis.
Result: 72% -> 15%.
EBL: 75mL.
Plan: ICU."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Malignant CAO", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Rigid bronch", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "debulk", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "dilation", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "removal", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "dilation", 2)},
    {"label": "OBS_FINDING", **get_span(t1, "stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "72%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "15%", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "75mL", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2035871_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: Ms. [REDACTED] underwent rigid bronchoscopy for malignant obstruction of the Right Lower Lobe (RLL) orifice. Initial inspection revealed 72% occlusion. Mechanical debulking was performed using biopsy forceps (CPT 31640). Following tumor removal, residual stenosis was addressed via balloon dilation to maximize airway diameter. Final obstruction was estimated at 15%."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t2, "malignant obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Right Lower Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RLL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "72% occlusion", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "biopsy forceps", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "removal", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "residual stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "15%", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2035871_syn_3
# ==========================================
t3 = """Coding: 31640 (Tumor excision via forceps).
Note: Balloon dilation performed for residual stenosis (incidental to debulking or separate 31630 depending on payer rules, here coded as 31640 primary modality).
Site: RLL Orifice.
Outcome: Significant patency improvement."""

e3 = [
    {"label": "OBS_LESION", **get_span(t3, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "excision", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "dilation", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "residual stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "debulking", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RLL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "Significant patency improvement", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2035871_syn_4
# ==========================================
t4 = """Procedure: Forceps Debulking + Balloon
Pt: [REDACTED]
Steps:
1. GA induced.
2. Tumor at RLL (72%).
3. Forceps used to remove tumor.
4. Balloon used to dilate the area.
5. Good result (15% residual).
Plan: ICU."""

e4 = [
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t4, "72%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 2)},
    {"label": "PROC_ACTION", **get_span(t4, "remove", 1)},
    {"label": "OBS_LESION", **get_span(t4, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 2)},
    {"label": "PROC_ACTION", **get_span(t4, "dilate", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "15% residual", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2035871_syn_5
# ==========================================
t5 = """[REDACTED] note. she has a tumor blocking the RLL. we went in with the rigid scope and grabbed the tumor with the forceps. cleared most of it out. then used a balloon to stretch it open a bit more. looks good now only 15 percent blocked. blood loss 75ml. icu for tonight."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RLL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid scope", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "balloon", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "15 percent blocked", 1)},
    {"label": "MEAS_VOL", **get_span(t5, "75ml", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2035871_syn_6
# ==========================================
t6 = """Malignant central airway obstruction. Pre-procedure 72% obstruction at RLL orifice. Under general anesthesia, rigid bronchoscopy performed. Endobronchial tumor id[REDACTED] at RLL orifice. Rigid bronchoscopy debulking with biopsy forceps performed with sequential tumor removal. Balloon dilation performed for residual stenosis. Post-procedure 15% residual obstruction. EBL 75mL."""

e6 = [
    {"label": "OBS_LESION", **get_span(t6, "Malignant central airway obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "72% obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Endobronchial tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL", 2)},
    {"label": "PROC_METHOD", **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "biopsy forceps", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(t6, "removal", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "dilation", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "residual stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "15% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "75mL", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2035871_syn_7
# ==========================================
t7 = """[Indication]
Malignancy, 72% RLL obstruction.
[Anesthesia]
General.
[Description]
Rigid bronchoscopy. Forceps debulking. Balloon dilation. Residual obstruction 15%.
[Plan]
ICU admission."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Malignancy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "72%", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "Residual obstruction 15%", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2035871_syn_8
# ==========================================
t8 = """We performed a rigid bronchoscopy on Ms. [REDACTED] to treat a malignant obstruction in the Right Lower Lobe orifice. We primarily used biopsy forceps to mechanically remove the tumor. After the bulk was removed, we used a balloon to dilate the airway and treat the residual stenosis. The obstruction was reduced from 72% to 15%."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t8, "malignant obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "Right Lower Lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "biopsy forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "remove", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "dilate", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "residual stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "72%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "15%", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2035871_syn_9
# ==========================================
t9 = """Under general anesthesia, rigid bronchoscopy was executed. An endobronchial tumor was found at the RLL orifice. Rigid bronchoscopy debulking with biopsy forceps was carried out with sequential tumor extraction. Balloon dilation was performed for residual stenosis. Post-procedure ~15% residual blockage."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "endobronchial tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "biopsy forceps", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(t9, "extraction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "dilation", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "residual stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "~15% residual blockage", 1)}
]
BATCH_DATA.append({"id": "2035871_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2035871 (Original)
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. James Rodriguez

Indication: Malignant central airway obstruction
Pre-procedure: ~72% obstruction at RLL orifice

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at RLL orifice.
Rigid bronchoscopy debulking with biopsy forceps performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Balloon dilation performed for residual stenosis.
Post-procedure: ~15% residual obstruction.
EBL: ~75mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Rodriguez, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Malignant central airway obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "~72% obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Endobronchial tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "biopsy forceps", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "removal", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "debulking", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "dilation", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "residual stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "~15% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "~75mL", 1)}
]
BATCH_DATA.append({"id": "2035871", "text": t10, "entities": e10})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)