import sys
from pathlib import Path

# Set up the repository root dynamically
# Assumes this script is run from within the repository structure
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 2480663
# ==========================================
id_1 = "2480663"
text_1 = """Pt: [REDACTED] | MRN: [REDACTED] | 77yo F
Date: [REDACTED]
Attending: Jennifer Walsh

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Galaxy)

• GA/ETT
• Linear EBUS: Olympus BF-UC180F
• Stations: 11R (4x), 2L (2x), 4L (4x)
• Nav to LLL lateral basal (B9)
• rEBUS: Eccentric view
• TIL confirmed: Radial EBUS
• Bx x7, TBNA x2
• ROSE+: Suspicious for malignancy

Complications: None
EBL: <10mL
Dispo: Home

Jennifer Walsh MD"""

entities_1 = [
    # Indications
    {"label": "OBS_LESION", **get_span(text_1, "Lung Cancer", 1)},
    
    # Procedures / Methods
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    
    # Actions (Biopsy/TBNA)
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    
    # Lymph Node Stations & Anatomy
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL lateral basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B9", 1)},
    
    # Measurements (Counts)
    {"label": "MEAS_COUNT", **get_span(text_1, "4x", 1)}, # For 11R
    {"label": "MEAS_COUNT", **get_span(text_1, "2x", 1)}, # For 2L
    {"label": "MEAS_COUNT", **get_span(text_1, "4x", 2)}, # For 4L
    {"label": "MEAS_COUNT", **get_span(text_1, "x7", 1)}, # For Bx
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)}, # For TBNA
    
    # ROSE / Findings
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Outcomes / Volumes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)