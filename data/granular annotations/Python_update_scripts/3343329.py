import sys
from pathlib import Path

# ==========================================
# Setup: Path Configuration
# ==========================================
# Dynamically determine the repository root (assumed to be 2 levels up)
try:
    REPO_ROOT = Path(__file__).resolve().parents[1]
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the repository to sys.path to access utility scripts
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

# ==========================================
# Helper: Span Extraction
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Case-sensitive.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 3343329
# ------------------------------------------
id_1 = "3343329"
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: CDR Patricia Davis, MD

Indication: Complicated parapneumonic effusion
Side: Left

PROCEDURE: Tube Thoracostomy
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide accessible.
Bedside ultrasound confirmed effusion without septations.
Site: 6th intercostal space, anterior to mid-axillary line.
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Blunt dissection technique. 28Fr chest tube inserted.
Immediate drainage: 670mL serosanguinous fluid.
Tube secured with sutures. Connected to Pleur-evac at -20cmH2O.
CXR obtained - tube in good position.

DISPOSITION: Floor admission.
Plan: Daily CXR, assess for tube removal criteria.

Davis, MD"""

entities_1 = [
    # Indication: "Complicated parapneumonic effusion" -> OBS_LESION maps to indication
    {"label": "OBS_LESION", **get_span(text_1, "parapneumonic effusion", 1)},
    # Side: "Left" -> LATERALITY
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)},
    # Procedure: "Tube Thoracostomy" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(text_1, "Tube Thoracostomy", 1)},
    # Method: "Bedside ultrasound" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_1, "ultrasound", 1)},
    # Finding/Target: "effusion" -> OBS_LESION
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 2)},
    # Anatomy: "6th intercostal space" -> ANAT_PLEURA (chest wall boundary)
    {"label": "ANAT_PLEURA", **get_span(text_1, "6th intercostal space", 1)},
    # Anatomy: "mid-axillary line" -> ANAT_PLEURA (boundary)
    {"label": "ANAT_PLEURA", **get_span(text_1, "mid-axillary line", 1)},
    # Medication: "lidocaine" -> MEDICATION
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    # Drain Size: "28Fr" -> MEAS_PLEURAL_DRAIN (explicit size meas)
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "28Fr", 1)},
    # Device: "chest tube" -> DEV_CATHETER
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    # Volume: "670mL" -> MEAS_VOL
    {"label": "MEAS_VOL", **get_span(text_1, "670mL", 1)},
    # Finding: "serosanguinous fluid" -> OBS_FINDING
    {"label": "OBS_FINDING", **get_span(text_1, "serosanguinous fluid", 1)},
    # Pressure: "-20cmH2O" -> MEAS_PRESS
    {"label": "MEAS_PRESS", **get_span(text_1, "-20cmH2O", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)