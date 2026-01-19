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
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3560623
# ==========================================
text_3560623 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Lisa Anderson

Indication: Complicated parapneumonic effusion
Side: Left

PROCEDURE: Tube Thoracostomy
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide accessible.
Bedside ultrasound confirmed effusion without septations.
Site: 5th intercostal space, anterior to mid-axillary line.
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Blunt dissection technique. 32Fr chest tube inserted.
Immediate drainage: 1587mL serosanguinous fluid.
Tube secured with sutures. Connected to Pleur-evac at -20cmH2O.
CXR obtained - tube in good position.

DISPOSITION: Floor admission.
Plan: Daily CXR, assess for tube removal criteria.

Anderson, MD"""

entities_3560623 = [
    # Indication: Complicated parapneumonic effusion
    {"label": "OBS_FINDING", **get_span(text_3560623, "effusion", 1)},
    # Side: Left
    {"label": "LATERALITY", **get_span(text_3560623, "Left", 1)},
    
    # PROCEDURE: Tube Thoracostomy
    {"label": "PROC_METHOD", **get_span(text_3560623, "Tube Thoracostomy", 1)},
    
    # Bedside ultrasound
    {"label": "PROC_METHOD", **get_span(text_3560623, "Bedside ultrasound", 1)},
    # confirmed effusion
    {"label": "OBS_FINDING", **get_span(text_3560623, "effusion", 2)},
    # without septations
    {"label": "OBS_FINDING", **get_span(text_3560623, "septations", 1)},
    
    # Site: 5th intercostal space
    {"label": "ANAT_PLEURA", **get_span(text_3560623, "5th intercostal space", 1)},
    # anterior to mid-axillary line
    {"label": "ANAT_PLEURA", **get_span(text_3560623, "mid-axillary line", 1)},
    
    # Local anesthesia with 1% lidocaine
    {"label": "MEDICATION", **get_span(text_3560623, "lidocaine", 1)},
    
    # Blunt dissection technique
    {"label": "PROC_ACTION", **get_span(text_3560623, "Blunt dissection", 1)},
    # 32Fr chest tube inserted
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3560623, "32Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3560623, "chest tube", 1)},
    
    # Immediate drainage: 1587mL serosanguinous fluid
    {"label": "MEAS_VOL", **get_span(text_3560623, "1587mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_3560623, "serosanguinous", 1)},
    
    # Connected to Pleur-evac at -20cmH2O
    {"label": "MEAS_PRESS", **get_span(text_3560623, "-20cmH2O", 1)},
    
    # CXR obtained
    {"label": "PROC_METHOD", **get_span(text_3560623, "CXR", 1)}
]

BATCH_DATA.append({"id": "3560623", "text": text_3560623, "entities": entities_3560623})


# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)