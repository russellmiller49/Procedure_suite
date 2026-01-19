import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from a subfolder or root)
# Adjust this logic if the script location varies relative to the library
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the 'scripts' module
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3388681
# ==========================================
id_1 = "3388681"
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: CDR Patricia Davis, MD

Indication: Malignant pleural effusion - NSCLC
Side: Right

PROCEDURE: Ultrasound-guided Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Real-time ultrasound used throughout procedure.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 10Fr pigtail catheter inserted.
604mL serosanguinous fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Davis, MD"""

entities_1 = [
    # Indication: Malignant pleural effusion - NSCLC
    {"label": "OBS_LESION", **get_span(text_1, "Malignant pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    
    # Side: Right
    {"label": "LATERALITY", **get_span(text_1, "Right", 1)},
    
    # PROCEDURE: Ultrasound-guided...
    {"label": "PROC_METHOD", **get_span(text_1, "Ultrasound-guided", 1)},
    
    # Real-time ultrasound used...
    {"label": "PROC_METHOD", **get_span(text_1, "Real-time ultrasound", 1)},
    
    # Local anesthesia with 1% lidocaine.
    {"label": "MEDICATION", **get_span(text_1, "1% lidocaine", 1)},
    
    # 10Fr pigtail catheter inserted. (Using DEV_CATHETER_SIZE for full phrase per guide example '14 Fr pigtail')
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "10Fr pigtail catheter", 1)},
    
    # 604mL serosanguinous fluid drained.
    {"label": "MEAS_VOL", **get_span(text_1, "604mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "serosanguinous fluid", 1)},
    
    # Catheter secured.
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 2)},  # Occ 2 matches "Catheter secured" (Occ 1 is in PROCEDURE line)
    
    # Post-procedure CXR: ... no PTX.
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no PTX", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)