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
# Case 1: 2409175
# ==========================================
id_1 = "2409175"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Steven Park, MD
Fellow: Jason Park
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 67 years
Sex: Female
ASA Class: 4

PRE-PROCEDURE:
1. Patient id[REDACTED] confirmed with two id[REDACTED]
2. Informed consent verified on chart
3. NPO status confirmed (>8 hours)
4. Anticoagulation status reviewed - not on anticoagulation
5. Allergies reviewed - NKDA
6. Time-out performed with all team members

INDICATION:
Combined staging and peripheral nodule diagnosis
Target lesion: 27.5mm ground-glass nodule, RLL superior (B6)
Bronchus sign: Negative

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Fujifilm EB-580S
- EBUS needle: 22G Acquire
- Robotic platform: Galaxy (Noah Medical)
- Radial EBUS: 20 MHz miniprobe
- Biopsy forceps: Standard
- Cytology brushes: Standard

PROCEDURE STEPS:

PART A - LINEAR EBUS FOR STAGING:
1. Bronchoscope inserted through ETT
2. Standard airway inspection performed - airways patent, no endobronchial lesions
3. Linear EBUS scope exchanged
4. Systematic lymph node survey performed
5. Following stations id[REDACTED] and sampled:
   - Station 11R: 22.0mm, 2 passes
   - Station 4R: 13.7mm, 4 passes
   - Station 11L: 18.9mm, 3 passes

6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - small cell carcinoma

PART B - ROBOTIC NAVIGATION:
1. Galaxy system prepared and registered
2. Registration error: 2.8mm (acceptable)
3. Robotic catheter advanced to RLL superior (B6)
4. Radial EBUS deployed - Eccentric view obtained
5. Tool-in-lesion confirmed with CBCT
6. Sampling performed:
   - Forceps biopsies: 4
   - TBNA passes: 3
   - Brushings: 2
7. ROSE performed - Adequate lymphocytes, no malignancy
8. BAL obtained from RLL

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 11R, 4R, 11L) → Cytology, cell block
2. TBBx RLL → Surgical pathology
3. Brushings → Cytology
4. BAL → Cultures (bacterial, fungal, AFB)

COMPLICATIONS: None
ESTIMATED BLOOD LOSS: <10 mL

IMPRESSION:
1. Completed EBUS-TBNA mediastinal staging
2. Completed robotic bronchoscopy with peripheral lung biopsy
3. No immediate complications

PLAN:
1. Monitor in recovery x 2 hours
2. Discharge home if stable
3. Follow-up in clinic for pathology results
4. Results to be discussed at tumor board

Procedure performed under direct supervision of [REDACTED], MD

[REDACTED], PGY-6
Steven Park, MD (Attending - present for entire procedure)"""

entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "27.5mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G Acquire", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "small cell carcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "Eccentric view", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Forceps biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no active bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 4)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No immediate complications", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)