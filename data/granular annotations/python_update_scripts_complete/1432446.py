import sys
from pathlib import Path

# Set up the repository root directory
# (Assuming this script is run from a subdirectory like 'scripts/' or 'processing/')
# If run from root, this ensures paths are correct.
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the repository root to sys.path to import utility functions
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure the repository structure is correct.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to find (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
        
    Returns:
        dict: A dictionary with 'start' and 'end' keys.
        
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
            
    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ===============================================
# Case 1: 1432446
# ===============================================
id_1432446 = "1432446"
text_1432446 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Steven Park, MD
===============================================

[INDICATION]
Primary: Peripheral nodule and bilateral hilar adenopathy
Category: Lung Cancer Staging
Target: 34.7mm Part-solid lesion, LUL superior lingula (B4)
Bronchus Sign: Positive
PET SUV: 12.7

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 122 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Fujifilm EB-580S
- Needle: 21G Standard FNA
- Stations sampled: 7, 11R, 11L
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Atypical cells

Procedure 2: Robotic Bronchoscopy
- Platform: Ion (Intuitive Surgical)
- Registration: CT-to-body, error 2.5mm
- Target: LUL superior lingula (B4)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Radial EBUS

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 5
- TBNA passes: 3
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
Electronically signed: Steven Park, MD
Date: [REDACTED]
==============================================="""

entities_1432446 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1432446, "nodule", 1)},
    {"label": "LATERALITY", **get_span(text_1432446, "bilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1432446, "hilar", 1)},
    {"label": "OBS_LESION", **get_span(text_1432446, "adenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1432446, "34.7mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1432446, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1432446, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1432446, "superior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1432446, "B4", 1)},
    
    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1432446, "8.0mm", 1)},
    {"label": "CTX_TIME", **get_span(text_1432446, "122 minutes", 1)},

    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1432446, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1432446, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1432446, "Needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1432446, "21G", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1432446, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1432446, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1432446, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1432446, "3", 2)}, # "Number of stations: 3"
    {"label": "OBS_ROSE", **get_span(text_1432446, "Atypical cells", 1)},

    # Procedure 2: Robotic Bronchoscopy
    {"label": "PROC_METHOD", **get_span(text_1432446, "Robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1432446, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1432446, "superior lingula", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1432446, "B4", 2)},

    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1432446, "Radial EBUS", 1)},
    # Note: Second "Radial EBUS" is confirmation, skipping to avoid duplicate noise or mapping it again if method context.
    
    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION", **get_span(text_1432446, "Biopsy", 1)}, # From "Transbronchial Biopsy"
    {"label": "DEV_INSTRUMENT", **get_span(text_1432446, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1432446, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1432446, "5", 1)},
    {"label": "PROC_ACTION", **get_span(text_1432446, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1432446, "3", 3)}, # "TBNA passes: 3"
    {"label": "PROC_ACTION", **get_span(text_1432446, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1432446, "2", 1)},
    {"label": "OBS_ROSE", **get_span(text_1432446, "Suspicious for malignancy", 1)},

    # Specimens / Outcome
    {"label": "SPECIMEN", **get_span(text_1432446, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1432446, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1432446, "surgical pathology", 1)},
    {"label": "PROC_ACTION", **get_span(text_1432446, "BAL", 1)}, # Bronchoalveolar Lavage
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1432446, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1432446, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1432446, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1432446, "text": text_1432446, "entities": entities_1432446})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)