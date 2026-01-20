import sys
from pathlib import Path

# Set the root directory of the repository
# Fixed path resolution to go up 4 levels (data/granular annotations/Python_update_scripts -> root)
REPO_ROOT = Path(__file__).resolve().parents[3]

# Append the scripts folder to the system path to allow imports
sys.path.append(str(REPO_ROOT / "scripts"))

# Import the utility function to add the case
from add_training_case import add_case

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

# ===============================================
# Case 1: 4591666
# ===============================================
id_1 = "4591666"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Amanda Foster, MD
===============================================

[INDICATION]
Primary: Lung nodule evaluation with mediastinal lymphadenopathy workup
Category: Lung Cancer Staging
Target: 27.1mm Solid lesion, RLL superior (B6)
Bronchus Sign: Negative
PET SUV: 6.1

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 108 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC190F
- Needle: 22G FNB/ProCore
- Stations sampled: 4L, 2R, 2L
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Suspicious for malignancy

Procedure 2: Robotic Bronchoscopy
- Platform: Ion (Intuitive Surgical)
- Registration: CT-to-body, error 1.8mm
- Target: RLL superior (B6)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Augmented fluoroscopy

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 5
- TBNA passes: 2
- Brushings: 2
- ROSE result: Malignant - squamous cell carcinoma

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
Electronically signed: Amanda Foster, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.1mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Solid lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "(B6)", 1)},
    
    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "108 minutes", 1)},
    
    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # Matches "Number of stations: 3"
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Procedure 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "(B6)", 2)},
    
    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    
    # Procedure 4: Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    # Updated occurrence for "2" to account for: 27.1mm, 22G(x2), 2R, 2L, Procedure 2
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 7)}, # "TBNA passes: 2"
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 8)}, # "Brushings: 2"
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "squamous cell carcinoma", 1)},
    
    # Specimens & Outcomes
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    
    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)