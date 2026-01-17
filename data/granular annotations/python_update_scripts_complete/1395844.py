import sys
from pathlib import Path

# Set up the repository root (adjust depth as needed for your environment)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly without package structure
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1395844
# ==========================================
id_1 = "1395844"
text_1 = """Pt: [REDACTED] | MRN: [REDACTED] | 76yo M
Date: [REDACTED]
Attending: Lisa Thompson

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Monarch)

• GA/ETT
• Linear EBUS: Pentax EB-1990i
• Stations: 4R (2x), 4L (4x), 10R (2x), 2L (2x)
• Nav to RML medial (B5)
• rEBUS: Adjacent view
• TIL confirmed: Augmented fluoroscopy
• Bx x5, TBNA x4
• ROSE+: squamous cell carcinoma

Complications: None
EBL: <10mL
Dispo: Home

Lisa Thompson MD"""

entities_1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "Lung Cancer", 1)},
    
    # Procedures / Methods
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},        # In "EBUS-TBNA"
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},        # In "EBUS-TBNA"
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    
    # Devices
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    
    # Anatomy & Samples (Stations)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "2x", 1)},     # Associated with 4R
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "4x", 1)},     # Associated with 4L
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "2x", 2)},     # Associated with 10R
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "2x", 3)},     # Associated with 2L
    
    # Navigation & Targets
    {"label": "PROC_METHOD",   **get_span(text_1, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "medial", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B5", 1)},        # Segmental definition
    {"label": "PROC_METHOD",   **get_span(text_1, "rEBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "Augmented fluoroscopy", 1)},
    
    # Actions & Counts
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "MEAS_COUNT",  **get_span(text_1, "x5", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},        # In "TBNA x4"
    {"label": "MEAS_COUNT",  **get_span(text_1, "x4", 1)},
    
    # Observations / Results
    {"label": "OBS_ROSE", **get_span(text_1, "squamous cell carcinoma", 1)},
    
    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)