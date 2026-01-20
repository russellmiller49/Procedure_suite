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
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4966053
# ==========================================
id_1 = "4966053"
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
Primary: Mediastinal staging for biopsy-proven lung adenocarcinoma
Category: Lung Cancer Staging
Target: 22.6mm Solid lesion, RUL apical (B1)
Bronchus Sign: Negative
PET SUV: 9.7

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 3
Airway: 8.0mm ETT
Duration: 131 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC190F
- Needle: 22G Standard FNA
- Stations sampled: 11R, 2L, 4R, 11L
- Number of stations: 4 (≥3)
- ROSE available: Yes
- ROSE result: Malignant - adenocarcinoma

Procedure 2: Robotic Bronchoscopy
- Platform: Galaxy (Noah Medical)
- Registration: CT-to-body, error 1.8mm
- Target: RUL apical (B1)

Procedure 3: Radial EBUS
- View: Concentric
- Confirmation: CBCT

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 4
- TBNA passes: 4
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
Electronically signed: Brian O'Connor, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # Indication
    {"label": "MEAS_SIZE",      **get_span(text_1, "22.6mm", 1)},
    {"label": "OBS_LESION",     **get_span(text_1, "Solid lesion", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "RUL apical (B1)", 1)},
    
    # Anesthesia
    {"label": "CTX_TIME",       **get_span(text_1, "131 minutes", 1)},

    # Procedure 1: Linear EBUS-TBNA
    {"label": "PROC_METHOD",    **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_1, "22G", 1)},
    {"label": "ANAT_LN_STATION",**get_span(text_1, "11R", 1)},
    {"label": "ANAT_LN_STATION",**get_span(text_1, "2L", 1)},
    {"label": "ANAT_LN_STATION",**get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION",**get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "4", 1)}, # Number of stations
    {"label": "OBS_ROSE",       **get_span(text_1, "Malignant - adenocarcinoma", 1)},

    # Procedure 2: Robotic
    {"label": "PROC_METHOD",    **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "RUL apical (B1)", 2)},

    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD",    **get_span(text_1, "Radial EBUS", 1)},

    # Procedure 4: Transbronchial Biopsy
    {"label": "PROC_ACTION",    **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "4", 2)}, # Forceps biopsies: 4
    {"label": "PROC_ACTION",    **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "4", 3)}, # TBNA passes: 4
    {"label": "PROC_ACTION",    **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "2", 2)}, # Brushings: 2 (Note: '2L' was 1st occurrence of '2' char, but '2' integer is distict? '2L' contains '2'. Find searches substring. "2L" is index 572. "2" in Brushings is index 966. Safe.)
    {"label": "OBS_ROSE",       **get_span(text_1, "Suspicious for malignancy", 1)},

    # Specimens & Misc
    {"label": "SPECIMEN",       **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN",       **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",       **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN",       **get_span(text_1, "BAL cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL",       **get_span(text_1, "10mL", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)