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
# Note 1: 447155
# ==========================================
id_1 = "447155"
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Rachel Kim

Indication: Malignant pleural effusion - NSCLC
Side: Left

PROCEDURE: Tunneled Pleural Catheter Insertion
Informed consent obtained. Timeout performed.
Patient positioned lateral decubitus, Left side up.
Preprocedure ultrasound confirmed large free-flowing effusion.
Site [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Aspira tunneled pleural catheter kit used.
Subcutaneous tunnel created. Pleural space entered with Seldinger technique.
Catheter advanced and position confirmed. 2104mL serosanguinous fluid drained.
Catheter secured with sutures. Sterile dressing applied.
CXR obtained - catheter in good position, lung re-expanded.

DISPOSITION: Home with drainage supplies. Teaching provided.
F/U: Clinic 1-2 weeks, drain PRN for symptoms.

Kim, MD"""

entities_1 = [
    {"label": "OBS_LESION",      **get_span(text_1, "Malignant pleural effusion", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "NSCLC", 1)},
    {"label": "LATERALITY",      **get_span(text_1, "Left", 1)},
    {"label": "DEV_CATHETER",    **get_span(text_1, "Tunneled Pleural Catheter", 1)},
    {"label": "LATERALITY",      **get_span(text_1, "Left", 2)},
    {"label": "PROC_METHOD",     **get_span(text_1, "ultrasound", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "effusion", 2)},
    {"label": "MEDICATION",      **get_span(text_1, "lidocaine", 1)},
    {"label": "DEV_CATHETER",    **get_span(text_1, "Aspira tunneled pleural catheter", 1)},
    {"label": "ANAT_PLEURA",     **get_span(text_1, "Pleural space", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER",    **get_span(text_1, "Catheter", 2)},
    {"label": "MEAS_VOL",        **get_span(text_1, "2104mL", 1)},
    {"label": "OBS_FINDING",     **get_span(text_1, "serosanguinous fluid", 1)},
    {"label": "DEV_CATHETER",    **get_span(text_1, "Catheter", 3)},
    {"label": "DEV_CATHETER",    **get_span(text_1, "catheter", 2)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "lung re-expanded", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)