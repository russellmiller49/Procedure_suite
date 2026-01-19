import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

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
# Note 1: 2914317
# ==========================================
t1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Lisa Thompson, MD
===============================================

[INDICATION]
Primary: Lung nodule evaluation with mediastinal lymphadenopathy workup
Category: Lung Cancer Staging
Target: 23.3mm Solid lesion, RLL posterior basal (B10)
Bronchus Sign: Negative
PET SUV: 2.8

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 2
Airway: 8.0mm ETT
Duration: 125 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Pentax EB-1990i
- Needle: 21G Standard FNA
- Stations sampled: 10R, 4R, 7
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Malignant - squamous cell carcinoma

Procedure 2: Robotic Bronchoscopy
- Platform: Galaxy (Noah Medical)
- Registration: CT-to-body, error 2.4mm
- Target: RLL posterior basal (B10)

Procedure 3: Radial EBUS
- View: Concentric
- Confirmation: CBCT

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 6
- TBNA passes: 3
- Brushings: 2
- ROSE result: Adequate lymphocytes, no malignancy

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
Electronically signed: Lisa Thompson, MD
Date: [REDACTED]
==============================================="""

e1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(t1, "Lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "23.3mm", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Solid lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "posterior basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B10", 1)},

    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(t1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "ETT", 1)},
    {"label": "CTX_TIME", **get_span(t1, "125 minutes", 1)},

    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Pentax EB-1990i", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 1)}, # Number of stations
    {"label": "OBS_ROSE", **get_span(t1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "squamous cell carcinoma", 1)},

    # Procedure 2: Robotic Bronchoscopy
    {"label": "PROC_METHOD", **get_span(t1, "Robotic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "posterior basal", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B10", 2)},

    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CBCT", 1)},

    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "6", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 2)}, # TBNA passes
    {"label": "PROC_ACTION", **get_span(t1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2", 3)}, # Brushings count (comes after 2.4mm, 2)
    {"label": "OBS_ROSE", **get_span(t1, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "no malignancy", 1)},

    # Specimens & Outcomes
    {"label": "SPECIMEN", **get_span(t1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(t1, "surgical pathology", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "10mL", 1)},
    
    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": "2914317", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for c in BATCH_DATA:
        add_case(c['id'], c['text'], c['entities'], REPO_ROOT)