import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
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
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Case 1: 3710765
# ==========================================
id_1 = "3710765"
text_1 = """Pt: [REDACTED] | MRN: [REDACTED] | 57yo F
Date: [REDACTED]
Attending: Brian O'Connor

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Monarch)

• GA/ETT
• Linear EBUS: Fujifilm EB-580S
• Stations: 11L (4x), 7 (2x), 2L (3x)
• Nav to RUL anterior (B3)
• rEBUS: Concentric view
• TIL confirmed: Radial EBUS
• Bx x7, TBNA x4
• ROSE+: NSCLC NOS

Complications: None
EBL: <10mL
Dispo: Home

Brian O'Connor MD"""

entities_1 = [
    # Dx / Indications
    {"label": "OBS_LESION", **get_span(text_1, "Lung Cancer", 1)},

    # Procedures & Methods (Header)
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)}, # In EBUS-TBNA
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)}, # In EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},

    # Procedures & Methods (Body)
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    # "Fujifilm EB-580S" could be DEV_INSTRUMENT, but usually scope platform falls under method/device overlap. 
    # Sticking to strictly defined instruments in guide (forceps/brush/needle).
    
    # Stations & Counts
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4x", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2x", 1)}, # specifically "2x" for station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3x", 1)},

    # Navigation & Locations
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 1)}, # Short for Navigational
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B3", 1)},

    # rEBUS & Findings
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Concentric view", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},

    # Actions & Counts (Bx/TBNA)
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x7", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # Second occurrence in text
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)},

    # ROSE Results
    {"label": "OBS_ROSE", **get_span(text_1, "NSCLC NOS", 1)},

    # Outcomes & Measurements (Footer)
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)