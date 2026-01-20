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
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Raises ValueError if the term is not found the specified number of times.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# 3. Data Definitions
# ==========================================

# ------------------------------------------
# Case: 4546122
# ------------------------------------------
id_1 = "4546122"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Brian O'Connor, MD
===============================================

[INDICATION]
Primary: Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy
Category: Lung Cancer Staging
Target: 15.4mm Ground-glass lesion, RML lateral (B4)
Bronchus Sign: Positive
PET SUV: 4.3

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 2
Airway: 8.0mm ETT
Duration: 105 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Fujifilm EB-580S
- Needle: 21G Standard FNA
- Stations sampled: 10R, 4L, 4R, 11L
- Number of stations: 4 (≥3)
- ROSE available: Yes
- ROSE result: Adequate lymphocytes

Procedure 2: Robotic Bronchoscopy
- Platform: Monarch (Auris Health (J&J))
- Registration: CT-to-body, error 2.5mm
- Target: RML lateral (B4)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Radial EBUS

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 7
- TBNA passes: 4
- Brushings: 2
- ROSE result: Atypical cells

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
Electronically signed: Brian O'Connor, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication
    {"label": "OBS_FINDING", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.4mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lateral (B4)", 1)},

    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "105 minutes", 1)},

    # Procedure 1: Linear EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},

    # Procedure 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lateral (B4)", 2)},

    # Procedure 3: Radial
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    
    # Procedure 4: Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # Specimens / Outcomes
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},

    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")