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
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4694863
# ==========================================
t1 = """Pt: [REDACTED] | MRN: [REDACTED] | 81yo F
Date: [REDACTED]
Attending: Rachel Goldman

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Galaxy)

• GA/ETT
• Linear EBUS: Pentax EB-1990i
• Stations: 4L (2x), 7 (3x), 10R (4x)
• Nav to LUL inferior lingula (B5)
• rEBUS: Concentric view
• TIL confirmed: Radial EBUS
• Bx x7, TBNA x4
• ROSE+: Adequate lymphocytes, no malignancy

Complications: None
EBL: <10mL
Dispo: Home

Rachel Goldman MD"""

e1 = [
    # Dx/Indications
    {"label": "OBS_LESION", **get_span(t1, "Lung Cancer", 1)},
    
    # Procedures & Methods
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Robotic Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Pentax EB-1990i", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    
    # Anatomy - Stations & Lungs
    {"label": "ANAT_LN_STATION", **get_span(t1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)}, # Matches Station 7
    {"label": "ANAT_LN_STATION", **get_span(t1, "10R", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "inferior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B5", 1)}, # Segmental mapping similar to RB1 example
    
    # Actions & Counts
    {"label": "MEAS_COUNT", **get_span(t1, "2x", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3x", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4x", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x7", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)}, # Second occurrence in text
    {"label": "MEAS_COUNT", **get_span(t1, "x4", 1)}, # Count for second TBNA
    
    # Observations & Results
    {"label": "OBS_ROSE", **get_span(t1, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "no malignancy", 1)},
    
    # Outcomes & Measures
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)}, # Context: Complications: None
    {"label": "MEAS_VOL", **get_span(t1, "10mL", 1)}
]

BATCH_DATA.append({"id": "4694863", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)