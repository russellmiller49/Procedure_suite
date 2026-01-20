import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is running from the correct directory structure.")
    sys.exit(1)

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
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Case 1: 2783660
# ==========================================
text_2783660 = """Pt: [REDACTED] | MRN: [REDACTED] | 56yo F
Date: [REDACTED]
Attending: David Kim

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Galaxy)

• GA/ETT
• Linear EBUS: Fujifilm EB-580S
• Stations: 2R (4x), 10R (3x), 2L (2x)
• Nav to RLL medial basal (B7)
• rEBUS: Adjacent view
• TIL confirmed: Radial EBUS
• Bx x5, TBNA x4
• ROSE+: NSCLC NOS

Complications: None
EBL: <10mL
Dispo: Home

David Kim MD"""

entities_2783660 = [
    # Proc: EBUS-TBNA + Robotic Bronch (Galaxy)
    {"label": "PROC_METHOD", **get_span(text_2783660, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_2783660, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_2783660, "Robotic", 1)},
    {"label": "PROC_METHOD", **get_span(text_2783660, "Galaxy", 1)},
    
    # • Linear EBUS: Fujifilm EB-580S
    {"label": "PROC_METHOD", **get_span(text_2783660, "Linear EBUS", 1)},
    
    # • Stations: 2R (4x), 10R (3x), 2L (2x)
    {"label": "ANAT_LN_STATION", **get_span(text_2783660, "2R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2783660, "4x", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2783660, "10R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2783660, "3x", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2783660, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2783660, "2x", 1)},
    
    # • Nav to RLL medial basal (B7)
    {"label": "PROC_METHOD", **get_span(text_2783660, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2783660, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2783660, "medial basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2783660, "B7", 1)},
    
    # • rEBUS: Adjacent view
    {"label": "PROC_METHOD", **get_span(text_2783660, "rEBUS", 1)},
    
    # • TIL confirmed: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_2783660, "Radial EBUS", 1)},
    
    # • Bx x5, TBNA x4
    {"label": "PROC_ACTION", **get_span(text_2783660, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2783660, "x5", 1)},
    {"label": "PROC_ACTION", **get_span(text_2783660, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_2783660, "x4", 1)},
    
    # • ROSE+: NSCLC NOS
    {"label": "OBS_ROSE", **get_span(text_2783660, "NSCLC NOS", 1)},
    
    # Complications: None
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2783660, "None", 1)}
]

BATCH_DATA.append({"id": "2783660", "text": text_2783660, "entities": entities_2783660})

# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")