import sys
from pathlib import Path

# Dynamic REPO_ROOT calculation to locate the utility function
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term in the text.
    Strictly prevents ValueError by ensuring exact matches.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 3311679
# ==========================================
t1 = """Pt: [REDACTED] | MRN: [REDACTED] | 66yo F
Date: [REDACTED]
Attending: Steven Park

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Galaxy)

• GA/ETT
• Linear EBUS: Fujifilm EB-580S
• Stations: 11R (2x), 4R (4x), 11L (3x)
• Nav to RLL superior (B6)
• rEBUS: Eccentric view
• TIL confirmed: CBCT
• Bx x4, TBNA x3
• ROSE+: small cell carcinoma

Complications: None
EBL: <10mL
Dispo: Home

Steven Park MD"""

e1 = [
    # Dx: Lung Cancer Staging
    {"label": "OBS_LESION", **get_span(t1, "Lung Cancer", 1)},

    # Proc: EBUS-TBNA + Robotic Bronch (Galaxy)
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Robotic Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Galaxy", 1)},

    # Linear EBUS: Fujifilm EB-580S
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},

    # Stations: 11R (2x), 4R (4x), 11L (3x)
    {"label": "ANAT_LN_STATION", **get_span(t1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2x", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4x", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3x", 1)},

    # Nav to RLL superior (B6)
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL superior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B6", 1)},

    # rEBUS: Eccentric view
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Eccentric view", 1)},

    # TIL confirmed: CBCT
    {"label": "PROC_METHOD", **get_span(t1, "CBCT", 1)},

    # Bx x4, TBNA x3
    {"label": "PROC_ACTION", **get_span(t1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x4", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "x3", 1)},

    # ROSE+: small cell carcinoma
    {"label": "OBS_ROSE", **get_span(t1, "small cell carcinoma", 1)},

    # Complications: None
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)}
]
BATCH_DATA.append({"id": "3311679", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)