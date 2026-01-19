import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3477246
# ==========================================
id_1 = "3477246"
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Sarah Williams

Indication: Recurrent symptomatic malignant effusion
Side: Right

PROCEDURE: Tunneled Pleural Catheter Insertion
Informed consent obtained. Timeout performed.
Patient positioned lateral decubitus, Right side up.
Preprocedure ultrasound confirmed large free-flowing effusion.
Site [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Aspira tunneled pleural catheter kit used.
Subcutaneous tunnel created. Pleural space entered with Seldinger technique.
Catheter advanced and position confirmed. 1126mL serosanguinous fluid drained.
Catheter secured with sutures. Sterile dressing applied.
CXR obtained - catheter in good position, lung re-expanded.

DISPOSITION: Home with drainage supplies. Teaching provided.
F/U: Clinic 1-2 weeks, drain PRN for symptoms.

Williams, MD"""

entities_1 = [
    # Indication: Recurrent symptomatic malignant effusion
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 1)},

    # Side: Right
    {"label": "LATERALITY", **get_span(text_1, "Right", 1)},

    # PROCEDURE: Tunneled Pleural Catheter Insertion
    {"label": "DEV_CATHETER", **get_span(text_1, "Tunneled Pleural Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Insertion", 1)},

    # Patient positioned lateral decubitus, Right side up.
    {"label": "LATERALITY", **get_span(text_1, "Right", 2)},

    # Preprocedure ultrasound confirmed large free-flowing effusion.
    {"label": "PROC_METHOD", **get_span(text_1, "ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 2)},

    # Local anesthesia with 1% lidocaine.
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},

    # Aspira tunneled pleural catheter kit used.
    {"label": "DEV_CATHETER", **get_span(text_1, "Aspira tunneled pleural catheter", 1)},

    # Pleural space entered with Seldinger technique.
    {"label": "ANAT_PLEURA", **get_span(text_1, "Pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Seldinger technique", 1)},

    # Catheter advanced...
    # Note: "Catheter" occ 1 is in "Tunneled Pleural Catheter". 
    # occ 2 is "Catheter advanced".
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 2)},

    # ...1126mL serosanguinous fluid drained.
    {"label": "MEAS_VOL", **get_span(text_1, "1126mL", 1)},

    # Catheter secured... (occ 3)
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 3)},

    # CXR obtained...
    {"label": "PROC_METHOD", **get_span(text_1, "CXR", 1)},

    # ...catheter in good position... (lowercase)
    # Note: "catheter" lowercase occ 1 is in "Aspira tunneled pleural catheter".
    # occ 2 is "catheter in good position".
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 2)},

    # ...lung re-expanded.
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "lung re-expanded", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)