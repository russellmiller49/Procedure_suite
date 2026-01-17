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
# 2. Helper Definition
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Case 1: 1672478
# ==========================================
id_1 = "1672478"
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: 7/24/1951
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Emily Thompson

Indication: Malignant pleural effusion - unknown primary
Side: Right

PROCEDURE: Tunneled Pleural Catheter Insertion
Informed consent obtained. Timeout performed.
Patient positioned lateral decubitus, Right side up.
Preprocedure ultrasound confirmed large free-flowing effusion.
Site [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Rocket tunneled pleural catheter kit used.
Subcutaneous tunnel created. Pleural space entered with Seldinger technique.
Catheter advanced and position confirmed. 1381mL straw-colored fluid drained.
Catheter secured with sutures. Sterile dressing applied.
CXR obtained - catheter in good position, lung re-expanded.

DISPOSITION: Home with drainage supplies. Teaching provided.
F/U: Clinic 1-2 weeks, drain PRN for symptoms.

Thompson, MD"""

entities_1 = [
    # Indication: Malignant pleural effusion (Effusion is a finding)
    {"label": "OBS_FINDING", **get_span(text_1, "effusion", 1)},
    # Side: Right
    {"label": "LATERALITY", **get_span(text_1, "Right", 1)},
    # Procedure Title
    {"label": "DEV_CATHETER", **get_span(text_1, "Tunneled Pleural Catheter", 1)},
    # Right side up
    {"label": "LATERALITY", **get_span(text_1, "Right", 2)},
    # Preprocedure ultrasound
    {"label": "PROC_METHOD", **get_span(text_1, "ultrasound", 1)},
    # free-flowing effusion
    {"label": "OBS_FINDING", **get_span(text_1, "effusion", 2)},
    # Medication
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    # Device: Rocket kit
    {"label": "DEV_CATHETER", **get_span(text_1, "Rocket tunneled pleural catheter", 1)},
    # Anatomy
    {"label": "ANAT_PLEURA", **get_span(text_1, "Pleural space", 1)},
    # Catheter advanced (Capitalized 'Catheter' appears in "Tunneled Pleural Catheter" first, so this is occ 2)
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 2)},
    # Volume
    {"label": "MEAS_VOL", **get_span(text_1, "1381mL", 1)},
    # Catheter secured (occ 3 of Capitalized 'Catheter')
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 3)},
    # CXR check - catheter (lowercase, occ 2 - occ 1 is in 'Rocket...catheter')
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 2)},
    # Outcome
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "lung re-expanded", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)