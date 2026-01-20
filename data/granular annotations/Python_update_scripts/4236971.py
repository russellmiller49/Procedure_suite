import sys
from pathlib import Path

# Set up the repository root (assuming script is run from a subfolder or root)
# Adjust this logic as needed for your specific environment
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
# Ensure 'scripts/add_training_case.py' exists in your path
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Warning: Could not import 'add_case'. Ensure the script is in the correct repo structure.")
    # Mock function for standalone testing if import fails
    def add_case(case_id, text, entities, root):
        print(f"Processing Case: {case_id} ({len(entities)} entities)")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a substring.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ===============================================
# Case 1: 4236971
# ===============================================
id_1 = "4236971"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Rachel Goldman, MD
===============================================

[INDICATION]
Primary: Right upper lobe mass with ipsilateral mediastinal nodes
Category: Lung Cancer Staging
Target: 20.2mm Solid lesion, LUL inferior lingula (B5)
Bronchus Sign: Positive
PET SUV: 16.9

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 113 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Pentax EB-1990i
- Needle: 21G Standard FNA
- Stations sampled: 4L, 7, 10R
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Adequate lymphocytes, no malignancy

Procedure 2: Robotic Bronchoscopy
- Platform: Galaxy (Noah Medical)
- Registration: CT-to-body, error 2.3mm
- Target: LUL inferior lingula (B5)

Procedure 3: Radial EBUS
- View: Concentric
- Confirmation: Radial EBUS

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 7
- TBNA passes: 4
- Brushings: 2
- ROSE result: Malignant - small cell carcinoma

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
Electronically signed: Rachel Goldman, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal nodes", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "20.2mm", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "inferior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B5", 1)},

    # Anesthesia
    {"label": "MEAS_SIZE",     **get_span(text_1, "8.0mm", 1)},
    {"label": "CTX_TIME",      **get_span(text_1, "113 minutes", 1)},

    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD",    **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_1, "21G", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "FNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)}, # Assuming station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "3", 2)}, # "Number of stations: 3" (skip ASA Class 3)
    {"label": "OBS_ROSE",       **get_span(text_1, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE",       **get_span(text_1, "no malignancy", 1)},

    # Procedure 2: Robotic Bronchoscopy
    {"label": "PROC_METHOD",    **get_span(text_1, "Robotic", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "Bronchoscopy", 1)}, # Changed occurrence from 2 to 1 (Header is capitalized)
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "inferior lingula", 2)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "B5", 2)},

    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD",    **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "Radial EBUS", 2)}, # Confirmation

    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION",    **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "7", 2)}, # "biopsies: 7" (skip station 7)
    {"label": "PROC_ACTION",    **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "4", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "2", 1)}, # "Brushings: 2" (skip error 2.3mm)
    {"label": "OBS_ROSE",       **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE",       **get_span(text_1, "small cell carcinoma", 1)},

    # Specimens / Outcome
    {"label": "SPECIMEN",       **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN",       **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "BAL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL",       **get_span(text_1, "<10mL", 1)},

    # Plan
    {"label": "PROC_METHOD",    **get_span(text_1, "Chest X-ray", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)