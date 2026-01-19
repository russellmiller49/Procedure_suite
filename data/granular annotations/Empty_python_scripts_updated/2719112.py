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
    """
    Finds the start/end indices of a term in the text for a specific occurrence.
    Raises ValueError if the term is not found the specified number of times.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Case 1: 2719112
# ==========================================
id_1 = "2719112"
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
Primary: Right upper lobe mass with ipsilateral mediastinal nodes
Category: Lung Cancer Staging
Target: 27.1mm Ground-glass lesion, LLL posterior basal (B10)
Bronchus Sign: Positive
PET SUV: 15.4

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 2
Airway: 8.0mm ETT
Duration: 85 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC260F-OL8
- Needle: 19G FNB/ProCore
- Stations sampled: 2L, 4R, 7, 11R
- Number of stations: 4 (≥3)
- ROSE available: Yes
- ROSE result: Malignant - squamous cell carcinoma

Procedure 2: Robotic Bronchoscopy
- Platform: Ion (Intuitive Surgical)
- Registration: CT-to-body, error 1.9mm
- Target: LLL posterior basal (B10)

Procedure 3: Radial EBUS
- View: Eccentric
- Confirmation: Radial EBUS

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 7
- TBNA passes: 3
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
Electronically signed: David Kim, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.1mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Ground-glass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "posterior basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B10", 1)},
    
    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "85 minutes", 1)},
    
    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19G", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)},  # "Number of stations: 4"
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    
    # Procedure 2: Robotic Bronchoscopy
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "posterior basal", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B10", 2)},
    
    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    
    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 2)},  # "Forceps biopsies: 7"
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 3)},  # "TBNA passes: 3"
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 4)},  # "Brushings: 2"
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    
    # Specimens & Outcomes
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    
    # Plan
    {"label": "CTX_TIME", **get_span(text_1, "2 hours", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)