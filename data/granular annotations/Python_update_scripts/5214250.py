import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo or typical structure)
# If this logic needs to be exact for a specific environment, adjust REPO_ROOT accordingly.
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the scripts directory to sys.path to enable imports
sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback/Placeholder if the import fails during local testing without the full repo
    def add_case(case_id, text, entities, repo_root):
        print(f"Processing Case: {case_id}")
        print(f"Text Length: {len(text)}")
        print(f"Entities Found: {len(entities)}")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring in a text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 5214250
# ==========================================
t1 = """Pt: [REDACTED] | MRN: [REDACTED] | 43yo M
Date: [REDACTED]
Attending: Lisa Thompson

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Monarch)

• GA/ETT
• Linear EBUS: Olympus BF-UC260F-OL8
• Stations: 2R (3x), 11R (3x), 4R (3x), 7 (2x)
• Nav to RML lateral (B4)
• rEBUS: Adjacent view
• TIL confirmed: Radial EBUS
• Bx x4, TBNA x2
• ROSE+: Adequate lymphocytes

Complications: None
EBL: <10mL
Dispo: Home

Lisa Thompson MD"""

e1 = [
    # "Lung Cancer" -> OBS_LESION
    {"label": "OBS_LESION", **get_span(t1, "Lung Cancer", 1)},
    
    # "EBUS" in "EBUS-TBNA" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    # "TBNA" in "EBUS-TBNA" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    # "Robotic Bronch" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(t1, "Robotic Bronch", 1)},
    # "Monarch" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(t1, "Monarch", 1)},
    
    # "Linear EBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},
    # "Olympus BF-UC260F-OL8" -> DEV_INSTRUMENT
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Olympus BF-UC260F-OL8", 1)},
    
    # Stations
    # "2R" -> ANAT_LN_STATION
    {"label": "ANAT_LN_STATION", **get_span(t1, "2R", 1)},
    # "3x" (first, after 2R) -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(t1, "3x", 1)},
    
    # "11R" -> ANAT_LN_STATION
    {"label": "ANAT_LN_STATION", **get_span(t1, "11R", 1)},
    # "3x" (second, after 11R) -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(t1, "3x", 2)},
    
    # "4R" -> ANAT_LN_STATION
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    # "3x" (third, after 4R) -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(t1, "3x", 3)},
    
    # "7" -> ANAT_LN_STATION (Station 7)
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    # "2x" -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(t1, "2x", 1)},
    
    # "Nav" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(t1, "Nav", 1)},
    # "RML" -> ANAT_LUNG_LOC
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 1)},
    # "lateral" -> ANAT_LUNG_LOC (modifier)
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "lateral", 1)},
    # "B4" -> ANAT_LUNG_LOC
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B4", 1)},
    
    # "rEBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    
    # "Radial EBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    
    # "Bx" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(t1, "Bx", 1)},
    # "x4" -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(t1, "x4", 1)},
    
    # "TBNA" (second occurrence) -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    # "x2" (second occurrence of 'x' notation, strictly text 'x2') -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(t1, "x2", 1)},
    
    # "Adequate lymphocytes" -> OBS_ROSE
    {"label": "OBS_ROSE", **get_span(t1, "Adequate lymphocytes", 1)},
    
    # "None" (after Complications) -> OUTCOME_COMPLICATION
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)},
    
    # "10mL" -> MEAS_VOL
    {"label": "MEAS_VOL", **get_span(t1, "10mL", 1)},
]

BATCH_DATA.append({"id": "5214250", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)