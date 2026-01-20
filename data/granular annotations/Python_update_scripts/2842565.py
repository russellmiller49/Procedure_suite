import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 2842565
# ==========================================
id_1 = "2842565"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 59yo male here for bronch w EBUS staging and robotic biopsy of a 31.9mm LLL nodule that was ground-glass on CT, bronchus sign was negative, PET showed SUV 13.4.

under general we did linear EBUS first using the Pentax EB-1990i scope with 22g needle and sampled stations 11L x4, 2L x4, 7 x3, 11R x3, 10R x4, ROSE was there and showed Suspicious for malignancy at multiple stations.

then switched to Ion robot and navigated to the LLL anteromedial basal (B7+8) lesion, registration was 3.2mm which is fine, got radial EBUS showing adjacent view and did tool in lesion confirmation with fluoroscopy. took 6 forceps bx, 3 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Suspicious for malignancy.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Maria Santos md
ip attending"""

entities_1 = [
    {"label": "PROC_ACTION", **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anteromedial basal (B7+8)", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3.2mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bx", 1)},
    # Note: "3" appears in "31.9mm", "13.4", "x3"(1), "x3"(2), "3.2mm", then "3 needle passes". 
    # That makes "3" in "3 needle passes" the 6th occurrence.
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 6)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cyto", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical path", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "flow", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "molecular", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)