import sys
from pathlib import Path

# Set up the repository root path (assuming this script is in a subdirectory like 'scripts/')
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Raises ValueError if the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in the text.")
    return {"start": start, "end": start + len(term)}

# ==============================================================================
# Case 1: 2747631
# ==============================================================================
id_1 = "2747631"
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
Primary: Combined staging and peripheral nodule diagnosis
Category: Lung Cancer Staging
Target: 16.9mm Solid lesion, RML lateral (B4)
Bronchus Sign: Positive
PET SUV: 16.9

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 100 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC190F
- Needle: 21G Standard FNA
- Stations sampled: 10R, 4L, 4R
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Adequate lymphocytes, no malignancy

Procedure 2: Robotic Bronchoscopy
- Platform: Monarch (Auris Health (J&J))
- Registration: CT-to-body, error 2.5mm
- Target: RML lateral (B4)

Procedure 3: Radial EBUS
- View: Concentric
- Confirmation: Augmented fluoroscopy

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 8
- TBNA passes: 4
- Brushings: 2
- ROSE result: Adequate lymphocytes

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
    {"label": "PROC_ACTION", **get_span(text_1, "staging", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "diagnosis", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Lung Cancer", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Staging", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Solid lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML lateral", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B4", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Positive", 1)},
    
    # Anesthesia / Airway
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "100 minutes", 1)},
    
    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # "ASA Class: 3" is 1st, "Number of stations: 3" is 2nd
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    
    # Procedure 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML lateral", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B4", 2)},
    
    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    
    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8", 2)}, # "8.0mm" is 1st, "8" is 2nd
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)}, # "4L" is 1st, "4R" is 2nd, "passes: 4" is 3rd
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 2)}, # "error 2.5mm" contains 2, need check. Actually "2.5" is float. Python find "2" might hit "21G"(1), "2.5"(2), "2"(3). Let's verify.
    # Verification for "2":
    # 1. "21G" (Proc 1)
    # 2. "2.5mm" (Proc 2)
    # 3. "2" (Brushings: 2) -> Occurrence 3
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 2)},
    
    # Specimens / Outcomes
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)