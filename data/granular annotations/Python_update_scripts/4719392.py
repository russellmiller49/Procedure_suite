import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Case: 4719392
# ==========================================
id_1 = "4719392"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Michael Rodriguez, MD
===============================================

[INDICATION]
Primary: Right upper lobe mass with ipsilateral mediastinal nodes
Category: Lung Cancer Staging
Target: 28.6mm Ground-glass lesion, RLL lateral basal (B9)
Bronchus Sign: Negative
PET SUV: 8.9

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 4
Airway: 8.0mm ETT
Duration: 92 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC260F-OL8
- Needle: 21G Standard FNA
- Stations sampled: 10R, 11R, 11L, 2R, 4L
- Number of stations: 5 (≥3)
- ROSE available: Yes
- ROSE result: Atypical cells

Procedure 2: Robotic Bronchoscopy
- Platform: Ion (Intuitive Surgical)
- Registration: CT-to-body, error 2.6mm
- Target: RLL lateral basal (B9)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Augmented fluoroscopy

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 5
- TBNA passes: 4
- Brushings: 2
- ROSE result: Malignant - adenocarcinoma

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
Electronically signed: Michael Rodriguez, MD
Date: [REDACTED]
==============================================="""

entities_1 = [
    # [cite_start]Indication [cite: 1, 11, 8, 2]
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.6mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 1)},
    
    # [cite_start]Anesthesia/Airway [cite: 7, 13]
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "92 minutes", 1)},

    # [cite_start]Procedure 1: Linear EBUS-TBNA [cite: 10, 7, 6, 11]
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC260F-OL8", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # [cite_start]Procedure 2: Robotic [cite: 10, 2]
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 2)},

    # [cite_start]Procedure 3: Radial EBUS [cite: 10]
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},

    # [cite_start]Procedure 4: Transbronchial Biopsy [cite: 10, 7, 9, 11]
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 2)}, # "Forceps biopsies: 5"
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)}, # "TBNA passes: 4" (Assuming 4 is 3rd occurrence of digit 4, checking text... ASA Class 4, 4L, 4. It is the 3rd occurrence of '4')
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # "Brushings: 2" (28.6mm(no), 2.6mm, 2R, 2... likely 3rd or 4th occurrence. Checking: 28.6(1), 21G(2), 2R(3), 2.6(4), 2(5). Wait, '2' appears in: '28.6', '21G', '2R', '2.6', '2'. Let's use unique context if possible or exact count.)
    # Correction on '2' and '4' counts based on raw text scan:
    # '4': "ASA Class: 4" (1), "4L" (2), "passes: 4" (3). Yes, occurrence 3.
    # '2': "28.6" (1), "21G" (2), "11L"(no), "2R"(3), "2.6"(4), "2 hours"(later). Wait, "Brushings: 2" is before "2 hours". 
    # Let's count '2' in text: "28.6", "BF-UC260", "21G", "2R", "2.6", "2" (Brushings), "x2" (Plan), "1-2" (Plan). 
    # Occurrences:
    # 1. 28.6
    # 2. 260F (in Scope name)
    # 3. 21G
    # 4. 2R
    # 5. 2.6
    # 6. Brushings: 2
    # So '2' is occurrence 6. 
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 6)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},

    # [cite_start]Specimens/Outcomes [cite: 22, 16, 8]
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    
    # [cite_start]Plan [cite: 16]
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)