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
# Case: 4319679
# ==========================================
id_1 = "4319679"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Jennifer Walsh, MD
===============================================

[INDICATION]
Primary: Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy
Category: Lung Cancer Staging
Target: 23.2mm Ground-glass lesion, LLL lateral basal (B9)
Bronchus Sign: Positive
PET SUV: 16.0

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 105 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC180F
- Needle: 19G FNB/ProCore
- Stations sampled: 11R, 2L, 4L
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Suspicious for malignancy

Procedure 2: Robotic Bronchoscopy
- Platform: Galaxy (Noah Medical)
- Registration: CT-to-body, error 2.8mm
- Target: LLL lateral basal (B9)

Procedure 3: Radial EBUS
- View: Eccentric
- Confirmation: Radial EBUS

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 7
- TBNA passes: 2
- Brushings: 2
- ROSE result: Suspicious for malignancy

Specimens: Cytology, cell block, surgical pathology, BAL cultures
Complications: None
EBL: <10mL

[PLAN]
1. Post-procedure monitoring x2 hours
2. Chest X-ray - completed, no pneumothorax
3. Discharge to home if stable
4. Follow-up: 1-2 weeks for pathology
5. Tumor board review pending final results
6. Molecular testing if malignancy confirmed

===============================================
Electronically signed: Jennifer Walsh, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication / Findings
    {"label": "OBS_LESION", **get_span(text_1, "Lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.2mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lateral basal (B9)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bronchus Sign", 1)},
    
    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "105 minutes", 1)},

    # Procedure 1
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC180F", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ProCore", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Procedure 2
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)}, # Case sensitive match to "Robotic Bronchoscopy"
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lateral basal (B9)", 2)},

    # Procedure 3
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},

    # Procedure 4
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 1)},
    
    # "TBNA passes: 2" -> Counting '2' occurrences: 1="23.2", 2="23.2", 3="2L", 4="2.8mm", 5="TBNA passes: 2"
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 5)}, 
    
    # "Brushings: 2" -> Next '2'
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 6)}, 
    
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 2)},

    # Specimens / Outcomes
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)