import sys
from pathlib import Path

# Set up repository root path (assuming script is run from inside the repo or similar structure)
# Adjust if necessary based on your actual environment
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Warning: Could not import 'add_case'. Ensure the script is run within the correct repo structure.")
    # Mocking add_case for standalone verification if import fails
    def add_case(case_id, text, entities, root):
        print(f"Mock Save: {case_id} ({len(entities)} entities)")

# Container for all processed notes
BATCH_DATA = []

# Helper function to find text spans safely
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==============================================================================
# Case 1: 3691751
# ==============================================================================
id_1 = "3691751"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Eric Johnson, MD
===============================================

[INDICATION]
Primary: Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy
Category: Lung Cancer Staging
Target: 19.5mm Solid lesion, RLL posterior basal (B10)
Bronchus Sign: Positive
PET SUV: 5.4

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 91 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Fujifilm EB-580S
- Needle: 19G FNB/ProCore
- Stations sampled: 10R, 7, 2R, 4R
- Number of stations: 4 (≥3)
- ROSE available: Yes
- ROSE result: Malignant - adenocarcinoma

Procedure 2: Robotic Bronchoscopy
- Platform: Ion (Intuitive Surgical)
- Registration: CT-to-body, error 3.2mm
- Target: RLL posterior basal (B10)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Fluoroscopy

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 7
- TBNA passes: 3
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
==============================================="""

entities_1 = [
    # Indication
    {"label": "OBS_LESION",      **get_span(text_1, "NSCLC", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "lymphadenopathy", 1)},
    
    # Target
    {"label": "MEAS_SIZE",       **get_span(text_1, "19.5mm", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "Solid lesion", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "RLL posterior basal (B10)", 1)},
    
    # Findings
    {"label": "OBS_FINDING",     **get_span(text_1, "Bronchus Sign", 1)},
    
    # Anesthesia / Airway
    {"label": "MEAS_SIZE",       **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "ETT", 1)},
    {"label": "CTX_TIME",        **get_span(text_1, "91 minutes", 1)},
    
    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD",     **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "EB-580S", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "19G", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "FNB/ProCore", 1)},
    
    # Stations
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)}, # Fixed: Occurrence changed from 2 to 1 as "4R" does not appear inside "10R"
    {"label": "MEAS_COUNT",      **get_span(text_1, "4", 2)},   # "Number of stations: 4"
    {"label": "OBS_ROSE",        **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    
    # Procedure 2: Robotic
    {"label": "PROC_METHOD",     **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "Ion", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "3.2mm", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "RLL posterior basal (B10)", 2)},
    
    # Procedure 3: Radial
    {"label": "PROC_METHOD",     **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "Fluoroscopy", 1)},
    
    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION",     **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "7", 2)}, 
    {"label": "PROC_ACTION",     **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "3", 2)}, 
    {"label": "PROC_ACTION",     **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2", 2)}, 
    {"label": "OBS_ROSE",        **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Specimens & Outcome
    {"label": "SPECIMEN",        **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "BAL cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL",        **get_span(text_1, "<10mL", 1)},
    
    # Plan
    {"label": "PROC_METHOD",     **get_span(text_1, "Chest X-ray", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==============================================================================
# Execution Loop
# ==============================================================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)