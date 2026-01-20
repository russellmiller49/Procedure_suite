import sys
from pathlib import Path

# Adjust this path logic to match your actual repository structure
# Example: If this script is in `repo/scripts/`, REPO_ROOT is `repo/`
# If this script is in `repo/`, REPO_ROOT is `repo/`
# This dynamic snippet assumes the script is being run from a standard location relative to the root
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the scripts folder to sys.path so we can import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of 'term' in 'text'.
    Indices are character-based.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 4946567
# ==========================================
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 55yo female here for bronch w EBUS staging and robotic biopsy of a 19.4mm RUL nodule that was solid on CT, bronchus sign was positive, PET showed SUV 6.7.

under general we did linear EBUS first using the Olympus BF-UC180F scope with 19g needle and sampled stations 10R x2, 2L x2, 11L x3, ROSE was there and showed Malignant - adenocarcinoma at multiple stations.

then switched to Monarch robot and navigated to the RUL anterior (B3) lesion, registration was 1.5mm which is fine, got radial EBUS showing concentric view and did tool in lesion confirmation with augmented fluoroscopy. took 6 forceps bx, 3 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Granuloma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Eric Johnson md
ip attending"""

entities_1 = [
    # --- Paragraph 1 ---
    {"label": "PROC_ACTION",    **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_1, "19.4mm", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION",     **get_span(text_1, "nodule", 1)},

    # --- Paragraph 2 ---
    {"label": "PROC_METHOD",    **get_span(text_1, "linear EBUS", 1)},
    # "Olympus BF-UC180F" is a specific scope model, usually DEV_INSTRUMENT implies tools like brushes/forceps, skipping to prevent noise unless strictly required.
    {"label": "DEV_NEEDLE",     **get_span(text_1, "19g", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "x2", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "x2", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "x3", 1)},
    {"label": "OBS_ROSE",       **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE",       **get_span(text_1, "adenocarcinoma", 1)},

    # --- Paragraph 3 ---
    {"label": "PROC_METHOD",    **get_span(text_1, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "RUL anterior", 1)},
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "B3", 1)},
    {"label": "OBS_LESION",     **get_span(text_1, "lesion", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "fluoroscopy", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "6", 1)}, # 6 forceps bx
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "bx", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "3", 1)}, # 3 needle passes
    {"label": "DEV_NEEDLE",     **get_span(text_1, "needle", 2)}, # "19g needle" was 1st
    {"label": "PROC_ACTION",    **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT",     **get_span(text_1, "x2", 3)}, # brushings x2
    {"label": "PROC_ACTION",    **get_span(text_1, "BAL", 1)},

    # --- Paragraph 4 ---
    {"label": "OBS_LESION",     **get_span(text_1, "nodule", 2)},
    {"label": "OBS_ROSE",       **get_span(text_1, "Granuloma", 1)},

    # --- Paragraph 5 ---
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},

    # --- Paragraph 6 ---
    # "cyto", "surgical path" are departments/test types. "cell block" is a specific specimen type.
    {"label": "SPECIMEN",       **get_span(text_1, "cell block", 1)},
]

BATCH_DATA.append({"id": "4946567", "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)