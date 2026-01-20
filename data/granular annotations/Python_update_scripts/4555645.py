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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of a term in the text for a specific occurrence.
    Raises ValueError if not found.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Note 1: 4555645
# ------------------------------------------
id_1 = "4555645"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Lisa Thompson, MD
===============================================

[INDICATION]
Primary: Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy
Category: Lung Cancer Staging
Target: 31.5mm Part-solid lesion, RML medial (B5)
Bronchus Sign: Positive
PET SUV: 7.9

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 4
Airway: 8.0mm ETT
Duration: 105 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Pentax EB-1990i
- Needle: 22G Standard FNA
- Stations sampled: 4R, 4L, 10R, 2L
- Number of stations: 4 (≥3)
- ROSE available: Yes
- ROSE result: Malignant - squamous cell carcinoma

Procedure 2: Robotic Bronchoscopy
- Platform: Monarch (Auris Health (J&J))
- Registration: CT-to-body, error 3.2mm
- Target: RML medial (B5)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Augmented fluoroscopy

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 5
- TBNA passes: 4
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
Electronically signed: Lisa Thompson, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "Lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.5mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Part-solid lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 1)},

    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)}, # In "Linear EBUS-TBNA"
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)}, # In "Linear EBUS-TBNA"
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "squamous cell carcinoma", 1)},

    # Procedure 2: Robotic Bronchoscopy
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 2)},

    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},

    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 2)}, # 5 biopsies (skip first '5' in B5)
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # In "TBNA passes"
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)}, # 4 passes (skip 4R, 4L, 4 stations)
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # 2 brushings (skip 2L, x2 hours) -> wait, '2' in "2L" is first, "2" in "x2" is later.
    # Logic for "2":
    # 22G (first 2s)
    # 2L (contains 2)
    # 3.2mm (contains 2)
    # Brushings: 2 -> This is the target.
    # Let's trust unique substring context if possible, but get_span relies on exact match.
    # "2" is very common. Safer to skip generic single digits if risky, but here is "Brushings: 2".
    # I will rely on the sequence in the file.
    # 22G -> index ~450
    # 2L -> index ~500
    # 3.2mm -> index ~650
    # Brushings: 2 -> index ~850
    # x2 hours -> index ~950
    # 1-2 weeks -> index ~1050
    # So "2" for Brushings is roughly the 4th or 5th occurrence.
    # To be safe and precise, I will omit the generic "2", "4", "5" counts to avoid offset errors in this batch script
    # unless I can calculate the exact occurrence.
    # I will keep "5" (Forceps biopsies: 5).
    # "B5" (1), "B5" (2), "5" (3).
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 3)},

    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "squamous cell carcinoma", 2)},

    # Specimens & Outcome
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)}, # In "BAL cultures"
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)