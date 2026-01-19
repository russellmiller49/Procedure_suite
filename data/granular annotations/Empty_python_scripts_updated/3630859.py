import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
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
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3630859
# ==========================================
t1 = """Pt: [REDACTED] | MRN: [REDACTED] | 61yo F
Date: [REDACTED]
Attending: Robert Patel

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Ion)

• GA/ETT
• Linear EBUS: Fujifilm EB-580S
• Stations: 10L (3x), 4L (2x), 11L (2x)
• Nav to RUL anterior (B3)
• rEBUS: Eccentric view
• TIL confirmed: CBCT
• Bx x8, TBNA x4
• ROSE+: NSCLC NOS

Complications: None
EBL: <10mL
Dispo: Home

Robert Patel MD"""

e1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(t1, "Lung Cancer", 1)},
    
    # Procedure Methods/Actions (Header)
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Robotic Bronch", 1)},
    
    # Detailed Steps
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},
    
    # Stations and Counts
    {"label": "ANAT_LN_STATION", **get_span(t1, "10L", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 1)}, # Inside (3x)
    {"label": "ANAT_LN_STATION", **get_span(t1, "4L", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2", 1)}, # Inside (2x) for 4L
    {"label": "ANAT_LN_STATION", **get_span(t1, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2", 2)}, # Inside (2x) for 11L
    
    # Navigation & Anatomy
    {"label": "PROC_METHOD", **get_span(t1, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL anterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B3", 1)},
    
    # Confirmation/Guidance
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CBCT", 1)},
    
    # Biopsies and Counts
    {"label": "PROC_ACTION", **get_span(t1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "8", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "4", 2)}, # 2nd occurrence of '4', first is inside '4L'
    
    # ROSE
    {"label": "OBS_ROSE", **get_span(t1, "NSCLC NOS", 1)},
    
    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)}
]

BATCH_DATA.append({"id": "3630859", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)