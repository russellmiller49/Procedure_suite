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
# Note 1: 3345858
# ==========================================
t1 = """Pt: [REDACTED] | MRN: [REDACTED] | 61yo F
Date: [REDACTED]
Attending: Steven Park

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Ion)

• GA/ETT
• Linear EBUS: Fujifilm EB-580S
• Stations: 7 (2x), 11R (4x), 11L (4x)
• Nav to LUL superior lingula (B4)
• rEBUS: Adjacent view
• TIL confirmed: Radial EBUS
• Bx x5, TBNA x3
• ROSE+: Atypical cells

Complications: None
EBL: <10mL
Dispo: Home

Steven Park MD"""

e1 = [
    # Proc: EBUS-TBNA...
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Robotic Bronch", 1)},
    
    # • Linear EBUS...
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},
    
    # • Stations: 7 (2x), 11R (4x), 11L (4x)
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4", 2)},
    
    # • Nav to LUL superior lingula (B4)
    {"label": "PROC_METHOD", **get_span(t1, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "superior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B4", 1)},
    
    # • rEBUS: Adjacent view
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    
    # • TIL confirmed: Radial EBUS
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    
    # • Bx x5, TBNA x3
    {"label": "PROC_ACTION", **get_span(t1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "5", 2)},  # 1st '5' is in EB-580S
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 1)},
    
    # • ROSE+: Atypical cells
    {"label": "OBS_ROSE", **get_span(t1, "Atypical cells", 1)},
    
    # Complications: None
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)},
    
    # EBL: <10mL
    {"label": "MEAS_VOL", **get_span(t1, "10mL", 1)},
]
BATCH_DATA.append({"id": "3345858", "text": t1, "entities": e1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)