import sys
from pathlib import Path

# Set up the repository root directory
try:
    REPO_ROOT = Path(__file__).resolve().parents[1]
except NameError:
    REPO_ROOT = Path(".").resolve().parents[0]

sys.path.append(str(REPO_ROOT))

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
# Case 1: 3138545
# ==========================================
text_1 = """Pt: [REDACTED] | MRN: [REDACTED] | 60yo M
Date: [REDACTED]
Attending: David Kim

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Ion)

• GA/ETT
• Linear EBUS: Olympus BF-UC260F-OL8
• Stations: 2L (4x), 4R (4x), 7 (3x), 11R (3x)
• Nav to LLL posterior basal (B10)
• rEBUS: Eccentric view
• TIL confirmed: Radial EBUS
• Bx x7, TBNA x3
• ROSE+: squamous cell carcinoma

Complications: None
EBL: <10mL
Dispo: Home

David Kim MD"""

entities_1 = [
    # Proc: EBUS-TBNA + Robotic Bronch (Ion)
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    
    # • Linear EBUS: Olympus BF-UC260F-OL8
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC260F-OL8", 1)},
    
    # • Stations: 2L (4x), 4R (4x), 7 (3x), 11R (3x)
    # 2L (4x)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)}, # Inside first "4x"
    
    # 4R (4x)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)}, # Inside second "4x" (Note: "4R" contains the 2nd '4')
    
    # 7 (3x)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)}, # Inside first "3x"
    
    # 11R (3x)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # Inside second "3x"
    
    # • Nav to LLL posterior basal (B10)
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL posterior basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B10", 1)},
    
    # • rEBUS: Eccentric view
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Eccentric view", 1)},
    
    # • TIL confirmed: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    
    # • Bx x7, TBNA x3
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 2)}, # 1st '7' is station 7, 2nd is count
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # 1st TBNA in header, 2nd here
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 3)}, # 3rd '3' in text
    
    # • ROSE+: squamous cell carcinoma
    {"label": "OBS_ROSE", **get_span(text_1, "squamous cell carcinoma", 1)},
    
    # Complications: None
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    
    # EBL: <10mL
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
]

BATCH_DATA.append({"id": "3138545", "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)