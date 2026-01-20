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
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ==========================================
# Note 1: 2150564
# ==========================================
id_1 = "2150564"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 58yo male here for bronch w EBUS staging and robotic biopsy of a 30.9mm RUL nodule that was ground-glass on CT, bronchus sign was negative, no PET done.

under general we did linear EBUS first using the Pentax EB-1990i scope with 22g needle and sampled stations 4L x2, 10R x4, 4R x4, 7 x2, ROSE was there and showed Malignant - NSCLC NOS at multiple stations.

then switched to Monarch robot and navigated to the RUL anterior (B3) lesion, registration was 2.0mm which is fine, got radial EBUS showing adjacent view and did tool in lesion confirmation with fluoroscopy. took 6 forceps bx, 4 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Granuloma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Steven Park md
ip attending"""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_METHOD",         **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD",         **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE",           **get_span(text_1, "30.9mm", 1)},
    {"label": "ANAT_LUNG_LOC",       **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION",          **get_span(text_1, "nodule", 1)},
    {"label": "OBS_FINDING",         **get_span(text_1, "ground-glass", 1)},
    
    # Paragraph 2
    {"label": "PROC_METHOD",         **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT",      **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "DEV_NEEDLE",          **get_span(text_1, "22g", 1)},
    {"label": "ANAT_LN_STATION",     **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION",     **get_span(text_1, "10R", 1)},
    {"label": "ANAT_LN_STATION",     **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION",     **get_span(text_1, "7", 1)},
    {"label": "OBS_ROSE",            **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Paragraph 3
    {"label": "DEV_INSTRUMENT",      **get_span(text_1, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC",       **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC",       **get_span(text_1, "anterior (B3)", 1)},
    {"label": "OBS_LESION",          **get_span(text_1, "lesion", 1)},
    {"label": "MEAS_SIZE",           **get_span(text_1, "2.0mm", 1)},
    {"label": "PROC_METHOD",         **get_span(text_1, "radial EBUS", 1)},
    {"label": "OBS_LESION",          **get_span(text_1, "lesion", 2)}, # In "tool in lesion"
    {"label": "PROC_METHOD",         **get_span(text_1, "fluoroscopy", 1)},
    {"label": "MEAS_COUNT",          **get_span(text_1, "6", 1)},
    {"label": "DEV_INSTRUMENT",      **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "bx", 1)},
    {"label": "MEAS_COUNT",          **get_span(text_1, "4 needle passes", 1)},
    {"label": "SPECIMEN",            **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "BAL", 1)},

    # Paragraph 4
    {"label": "OBS_LESION",          **get_span(text_1, "nodule", 2)},
    {"label": "OBS_ROSE",            **get_span(text_1, "Granuloma", 1)},

    # Paragraph 5
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "ptx", 1)},

    # Paragraph 6
    {"label": "SPECIMEN",            **get_span(text_1, "cell block", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)