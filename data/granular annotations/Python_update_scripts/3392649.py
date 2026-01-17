import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 3392649
# ==========================================
id_1 = "3392649"
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Michael Chen

Indication: Hepatic hydrothorax
Side: Right

PROCEDURE: Ultrasound-guided Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Real-time ultrasound used throughout procedure.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 14Fr pigtail catheter inserted.
1011mL turbid fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Chen, MD"""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Hepatic hydrothorax", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ultrasound-guided", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Pleural", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Drainage Catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Real-time ultrasound", 1)},
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "1011mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "turbid fluid", 1)},
    # Occurrence 2 of "Catheter" (Capitalized) matches "Catheter secured"
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 2)},
    # Occurrence 2 of "catheter" (lowercase) matches "catheter in appropriate"
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no PTX", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)