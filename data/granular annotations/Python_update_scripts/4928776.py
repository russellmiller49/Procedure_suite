import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
# Adjust this logic if the script is placed elsewhere relative to the root
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repo root to sys.path so we can import the utility
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4928776
# ==========================================
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: CAPT Russell Miller, MD

Indication: Complicated parapneumonic effusion
Side: Left

PROCEDURE: Ultrasound-guided Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Real-time ultrasound used throughout procedure.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 12Fr pigtail catheter inserted.
1531mL turbid fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Miller, MD"""

entities_1 = [
    # Indication: Complicated parapneumonic effusion -> OBS_LESION (maps to indication)
    {"label": "OBS_LESION", **get_span(text_1, "Complicated parapneumonic effusion", 1)},
    
    # Side: Left -> LATERALITY
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)},
    
    # PROCEDURE: Ultrasound-guided -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_1, "Ultrasound-guided", 1)},
    
    # Pleural Drainage Catheter -> DEV_CATHETER
    {"label": "DEV_CATHETER", **get_span(text_1, "Pleural Drainage Catheter", 1)},
    
    # Real-time ultrasound -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_1, "Real-time ultrasound", 1)},
    
    # lidocaine -> MEDICATION
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    
    # 12Fr -> DEV_CATHETER_SIZE
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "12Fr", 1)},
    
    # pigtail catheter -> DEV_CATHETER
    {"label": "DEV_CATHETER", **get_span(text_1, "pigtail catheter", 1)},
    
    # 1531mL -> MEAS_VOL
    {"label": "MEAS_VOL", **get_span(text_1, "1531mL", 1)},
    
    # turbid -> OBS_FINDING (General finding description)
    {"label": "OBS_FINDING", **get_span(text_1, "turbid", 1)},
    
    # fluid -> SPECIMEN (Physical sample/substance)
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)},
]

BATCH_DATA.append({"id": "4928776", "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)