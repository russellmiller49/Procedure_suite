import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to enable imports
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.add_training_case import add_case

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
# Case 1: 2751013
# ===============================================
id_1 = "2751013"
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
Target: 14.5mm Ground-glass lesion, RUL anterior (B3)
Bronchus Sign: Positive
PET SUV: N/A

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 136 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Fujifilm EB-580S
- Needle: 19G FNB/ProCore
- Stations sampled: 11L, 7, 2L
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Malignant - NSCLC NOS

Procedure 2: Robotic Bronchoscopy
- Platform: Monarch (Auris Health (J&J))
- Registration: CT-to-body, error 3.2mm
- Target: RUL anterior (B3)

Procedure 3: Radial EBUS
- View: Concentric
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
7. Electronically signed: Brian O'Connor, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication / Lesion
    {"label": "MEAS_SIZE",       **get_span(text_1, "14.5mm", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "Ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "anterior (B3)", 1)},
    
    # Anesthesia / Airway
    {"label": "MEAS_SIZE",       **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "ETT", 1)},
    
    # Procedure 1: EBUS-TBNA
    {"label": "PROC_METHOD",     **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Fujifilm EB-580S", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "19G", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "FNB/ProCore", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    # "7" appears in ID (1st) and "11L, 7" (2nd)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 2)}, 
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "OBS_ROSE",        **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Procedure 2: Robotic
    {"label": "PROC_METHOD",     **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "anterior (B3)", 2)},
    
    # Procedure 3: Radial
    {"label": "PROC_METHOD",     **get_span(text_1, "Radial EBUS", 1)},
    
    # Procedure 4: Biopsy
    {"label": "PROC_ACTION",     **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Forceps", 1)},
    # "7" in "Forceps biopsies: 7" is the 3rd occurrence (ID, Station 7, Count 7)
    {"label": "MEAS_COUNT",      **get_span(text_1, "7", 3)},
    {"label": "PROC_ACTION",     **get_span(text_1, "TBNA", 2)}, # 1st was in "EBUS-TBNA" title line
    {"label": "MEAS_COUNT",      **get_span(text_1, "4", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "Brushings", 1)},
    {"label": "OBS_ROSE",        **get_span(text_1, "Atypical cells", 1)},
    
    # Specimens & Outcomes
    {"label": "SPECIMEN",        **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "BAL cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL",        **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)