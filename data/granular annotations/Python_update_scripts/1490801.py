import sys
from pathlib import Path

# Set the root of the repository to the parent of the scripts folder
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function to add a training case
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The specific occurrence to find (1-based index).
        
    Returns:
        dict: A dictionary with 'start' and 'end' keys.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
            
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 1490801
# ==========================================
t1 = """Pt: [REDACTED] | MRN: [REDACTED] | 58yo M
Date: [REDACTED]
Attending: Steven Park

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Monarch)

• GA/ETT
• Linear EBUS: Pentax EB-1990i
• Stations: 4L (2x), 10R (4x), 4R (4x), 7 (2x)
• Nav to RUL anterior (B3)
• rEBUS: Adjacent view
• TIL confirmed: Fluoroscopy
• Bx x6, TBNA x4
• ROSE+: NSCLC NOS

Complications: None
EBL: <10mL
Dispo: Home

Steven Park MD"""

e1 = [
    # Dx: Lung Cancer Staging
    {"label": "OBS_LESION", **get_span(t1, "Lung Cancer", 1)},
    
    # Proc: EBUS-TBNA + Robotic Bronch
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Robotic", 1)},
    
    # • Linear EBUS: Pentax EB-1990i
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Pentax EB-1990i", 1)},
    
    # • Stations: 4L (2x), 10R (4x), 4R (4x), 7 (2x)
    {"label": "ANAT_LN_STATION", **get_span(t1, "4L", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2x", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "10R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4x", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4x", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2x", 2)},
    
    # • Nav to RUL anterior (B3)
    {"label": "PROC_METHOD", **get_span(t1, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B3", 1)},
    
    # • rEBUS: Adjacent view
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    
    # • TIL confirmed: Fluoroscopy
    {"label": "PROC_METHOD", **get_span(t1, "Fluoroscopy", 1)},
    
    # • Bx x6, TBNA x4
    {"label": "PROC_ACTION", **get_span(t1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "x4", 1)},
    
    # • ROSE+: NSCLC NOS
    {"label": "OBS_ROSE", **get_span(t1, "NSCLC NOS", 1)},
    
    # Complications: None
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)}
]

BATCH_DATA.append({"id": "1490801", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)