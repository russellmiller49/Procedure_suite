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
# Note 1: 4146357
# ==========================================
id_1 = "4146357"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 82yo female here for bronch w EBUS staging and robotic biopsy of a 16.3mm RUL nodule that was part-solid on CT, bronchus sign was positive, PET showed SUV 12.4.

under general we did linear EBUS first using the Olympus BF-UC180F scope with 21g needle and sampled stations 2L x2, 10L x4, 7 x4, ROSE was there and showed Malignant - adenocarcinoma at multiple stations.

then switched to Monarch robot and navigated to the RUL anterior (B3) lesion, registration was 3.0mm which is fine, got radial EBUS showing eccentric view and did tool in lesion confirmation with augmented fluoroscopy. took 6 forceps bx, 2 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Malignant - adenocarcinoma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Maria Santos md
ip attending"""

entities_1 = [
    {"label": "PROC_ACTION",        **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "16.3mm", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION",         **get_span(text_1, "nodule", 1)},
    
    # EBUS Staging
    {"label": "PROC_METHOD",        **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Olympus BF-UC180F", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_1, "21g", 1)},
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "2L", 1)},
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "10L", 1)},
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "7", 1)},
    {"label": "OBS_ROSE",           **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    
    # Robotic Nodule Biopsy
    {"label": "PROC_METHOD",        **get_span(text_1, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "fluoroscopy", 1)},
    
    # Samples
    {"label": "MEAS_COUNT",         **get_span(text_1, "6", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "bx", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "2", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_1, "needle", 2)}, # "needle passes"
    {"label": "PROC_ACTION",        **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "BAL", 1)},
    
    # Results/Outcomes
    {"label": "OBS_ROSE",           **get_span(text_1, "Malignant - adenocarcinoma", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},
    
    # Specimens
    {"label": "SPECIMEN",           **get_span(text_1, "cyto", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "surgical path", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "flow", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "molecular", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)