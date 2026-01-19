import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a substring.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==============================================================================
# Case 1: 3801075
# ==============================================================================
id_1 = "3801075"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: David Kim, MD
===============================================

[INDICATION]
Primary: PET-avid lung mass and mediastinal lymphadenopathy
Category: Lung Cancer Staging
Target: 20.0mm Solid lesion, RML medial (B5)
Bronchus Sign: Negative
PET SUV: 6.5

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 4
Airway: 8.0mm ETT
Duration: 87 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC190F
- Needle: 22G Acquire
- Stations sampled: 2L, 4R, 11R, 11L
- Number of stations: 4 (≥3)
- ROSE available: Yes
- ROSE result: Malignant - small cell carcinoma

Procedure 2: Robotic Bronchoscopy
- Platform: Ion (Intuitive Surgical)
- Registration: CT-to-body, error 2.5mm
- Target: RML medial (B5)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Augmented fluoroscopy

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 7
- TBNA passes: 2
- Brushings: 2
- ROSE result: Malignant - NSCLC NOS

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
Electronically signed: David Kim, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication & Targets
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.0mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B5", 1)},
    
    # Anesthesia & Vitals
    {"label": "CTX_TIME", **get_span(text_1, "87 minutes", 1)},
    
    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "small cell carcinoma", 1)},
    
    # Procedure 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B5", 2)},
    
    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    
    # Procedure 4: Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "NSCLC NOS", 1)},
    
    # Specimens & Outcomes
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}, # Context: Complications: None
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)