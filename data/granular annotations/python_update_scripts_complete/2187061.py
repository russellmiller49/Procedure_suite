import sys
from pathlib import Path

# Set up the repository root directory
try:
    REPO_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    REPO_ROOT = Path('.').resolve().parents[2]

sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Ensures strict case-sensitivity to prevent offset errors.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 2187061
# ==========================================
t1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Michael Chen

Indication: Complicated parapneumonic effusion
Side: Right

PROCEDURE: Ultrasound-guided Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Real-time ultrasound used throughout procedure.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 10Fr pigtail catheter inserted.
1405mL turbid fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Chen, MD"""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Complicated parapneumonic effusion", 1)},
    {"label": "LATERALITY", **get_span(t1, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ultrasound-guided", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Pleural Drainage Catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Real-time ultrasound", 1)},
    {"label": "MEDICATION", **get_span(t1, "lidocaine", 1)},
    # "10Fr pigtail catheter" matches the DEV_CATHETER_SIZE example "14 Fr pigtail"
    {"label": "DEV_CATHETER_SIZE", **get_span(t1, "10Fr pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "1405mL", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "turbid fluid", 1)},
    # "Catheter" (capitalized) in "Catheter secured" is the 2nd occurrence of "Catheter" (1st is in title)
    {"label": "DEV_CATHETER", **get_span(t1, "Catheter", 2)}, 
    # "catheter" (lowercase) in "catheter in appropriate position" is 2nd occurrence (1st is in 10Fr line)
    {"label": "DEV_CATHETER", **get_span(t1, "catheter", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "no PTX", 1)}
]

BATCH_DATA.append({"id": "2187061", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)