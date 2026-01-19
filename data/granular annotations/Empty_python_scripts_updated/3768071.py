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
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ==========================================
# Note: 3768071
# ==========================================
id_1 = "3768071"
text_1 = """Pt: [REDACTED] | MRN: [REDACTED] | 77yo M
Date: [REDACTED]
Attending: Rachel Goldman

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Ion)

• GA/ETT
• Linear EBUS: Pentax EB-1990i
• Stations: 2L (3x), 4L (2x), 10R (2x), 10L (3x), 11L (2x)
• Nav to LUL apicoposterior (B1+2)
• rEBUS: Concentric view
• TIL confirmed: Fluoroscopy
• Bx x7, TBNA x2
• ROSE+: Atypical cells

Complications: None
EBL: <10mL
Dispo: Home

Rachel Goldman MD"""

entities_1 = [
    # Indication / Diagnosis
    {"label": "OBS_LESION", **get_span(text_1, "Lung Cancer", 1)},

    # Procedures & Methods
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    
    # Stations & Counts (Strict order mapping)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "3x", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2x", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2x", 2)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "3x", 2)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2x", 3)},

    # Navigation & Locations
    {"label": "PROC_METHOD",   **get_span(text_1, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "apicoposterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B1+2", 1)},

    # rEBUS & Findings
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Concentric view", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Fluoroscopy", 1)},

    # Actions & Samples
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "MEAS_COUNT",  **get_span(text_1, "x7", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT",  **get_span(text_1, "x2", 1)}, # Note: format is "x2" here, distinct from "2x" above

    # Results & Outcomes
    {"label": "OBS_ROSE",             **get_span(text_1, "Atypical cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL",             **get_span(text_1, "10mL", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)