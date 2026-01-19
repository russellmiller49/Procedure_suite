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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Batch Data Definitions
# ==========================================
BATCH_DATA = []

# --- Note 1: 3343329 ---
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
    # Indication/Findings
    {"label": "OBS_FINDING", **get_span(text_1, "Complicated parapneumonic effusion", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)},

    # Procedure Info
    {"label": "PROC_METHOD", **get_span(text_1, "Tube Thoracostomy", 1)},
    
    # Ultrasound
    {"label": "PROC_METHOD", **get_span(text_1, "Bedside ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "effusion", 2)}, # 2nd occurrence in 'confirmed effusion'
    {"label": "OBS_FINDING", **get_span(text_1, "septations", 1)},

    # Site & Prep
    {"label": "ANAT_PLEURA", **get_span(text_1, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "mid-axillary line", 1)},
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    
    # Action & Device
    {"label": "PROC_ACTION", **get_span(text_1, "Blunt dissection", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "28Fr", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "28Fr chest tube", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    
    # Drainage & Measurements
    {"label": "MEAS_VOL", **get_span(text_1, "670mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "serosanguinous fluid", 1)},
    {"label": "MEAS_PRESS", **get_span(text_1, "-20cmH2O", 1)},
    
    # Outcomes/Imaging
    {"label": "PROC_METHOD", **get_span(text_1, "CXR", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CXR", 2)}, # Daily CXR
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)