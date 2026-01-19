import sys
from pathlib import Path

# Set the root directory of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure this script is run from a location where 'scripts' is a sibling or in python path
try:
    from scripts.add_training_case import add_case
except ImportError:
    # If running directly from the wrong dir, we might need to adjust sys.path
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2889333
# ==========================================
id_1 = "2889333"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 81yo female here for bronch w EBUS staging and robotic biopsy of a 23.2mm LLL nodule that was ground-glass on CT, bronchus sign was positive, PET showed SUV 16.0.

under general we did linear EBUS first using the Olympus BF-UC180F scope with 19g needle and sampled stations 11R x4, 2L x2, 4L x4, ROSE was there and showed Suspicious for malignancy at multiple stations.

then switched to Galaxy robot and navigated to the LLL lateral basal (B9) lesion, registration was 2.8mm which is fine, got radial EBUS showing eccentric view and did tool in lesion confirmation with radial ebus. took 7 forceps bx, 2 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Suspicious for malignancy.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Jennifer Walsh md
ip attending"""

entities_1 = [
    # Paragraph 2
    {"label": "PROC_ACTION", **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},
    
    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19g", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Paragraph 4
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL lateral basal (B9)", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "eccentric view", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # "23.2mm", "x2" (first), "2" (needle passes)
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    
    # Paragraph 5
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 2)},
    
    # Paragraph 6
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},
    
    # Paragraph 7
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)