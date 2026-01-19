import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
# Adjust logical parent count based on actual folder structure if needed.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Could not import 'add_case'. Ensure you are running from the correct repository context.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a strictly case-sensitive term.
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
# Note 1: 3628963
# ==========================================
id_1 = "3628963"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 48yo female here for bronch w EBUS staging and robotic biopsy of a 28.6mm RLL nodule that was ground-glass on CT, bronchus sign was negative, PET showed SUV 8.9.

under general we did linear EBUS first using the Olympus BF-UC260F-OL8 scope with 21g needle and sampled stations 10R x2, 11R x2, 11L x4, 2R x4, 4L x4, ROSE was there and showed Atypical cells at multiple stations.

then switched to Ion robot and navigated to the RLL lateral basal (B9) lesion, registration was 2.6mm which is fine, got radial EBUS showing adjacent view and did tool in lesion confirmation with augmented fluoroscopy. took 5 forceps bx, 4 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Malignant - adenocarcinoma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Michael Rodriguez md
ip attending"""

entities_1 = [
    # "EBUS" staging
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    # "robotic" biopsy
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    # "biopsy" of...
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    # "28.6mm"
    {"label": "MEAS_SIZE", **get_span(text_1, "28.6mm", 1)},
    # "RLL" nodule
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    # "nodule"
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    # "ground-glass"
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    
    # "linear EBUS"
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    # "Olympus BF-UC260F-OL8"
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC260F-OL8", 1)},
    # "21g"
    {"label": "DEV_NEEDLE", **get_span(text_1, "21g", 1)},
    # "needle"
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 1)},
    
    # Stations and counts
    # "10R"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    # "x2" (1st occ)
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    # "11R"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    # "x2" (2nd occ)
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 2)},
    # "11L"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    # "x4" (1st occ)
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)},
    # "2R"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 1)},
    # "x4" (2nd occ)
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 2)},
    # "4L"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    # "x4" (3rd occ)
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 3)},
    
    # "Atypical cells"
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    
    # "Ion robot"
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robot", 1)},
    # "RLL" lateral basal
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    # "lateral basal (B9)"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lateral basal (B9)", 1)},
    # "lesion"
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    # "radial EBUS"
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    # "fluoroscopy"
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    
    # Sampling actions
    # "5"
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 1)},
    # "forceps"
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    # "bx"
    {"label": "PROC_ACTION", **get_span(text_1, "bx", 1)},
    # "4"
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)}, # "4L" captured the first '4', but '4 needle passes' is distinct '4' surrounded by spaces usually.
    # Actually, in '4L', '4' is part of the token. In "4 needle", '4' is standalone.
    # Text find for "4" -> 1st: "48yo", 2nd: "11L x4", 3rd: "2R x4", 4th: "4L", 5th: "4L x4", 6th: "4 needle".
    # Let's count strictly in the text:
    # "... 48yo ..." -> 1
    # "... 11L x4 ..." -> 2
    # "... 2R x4 ..." -> 3
    # "... 4L ..." -> 4
    # "... 4L x4 ..." -> 5
    # "... took 5 forceps bx, 4 needle ..." -> 6
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 6)}, 
    
    # "needle"
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 2)},
    # "brushings"
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    # "x2" (3rd occ)
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 3)},
    # "BAL"
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    
    # Results
    # "Malignant"
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    # "adenocarcinoma"
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 1)},
    
    # Outcomes
    # "no bleeding"
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    # "no ptx"
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},
    
    # Specimens
    # "cyto"
    {"label": "SPECIMEN", **get_span(text_1, "cyto", 1)},
    # "surgical path"
    {"label": "SPECIMEN", **get_span(text_1, "surgical path", 1)},
    # "cell block"
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    # "flow"
    {"label": "SPECIMEN", **get_span(text_1, "flow", 1)},
    # "molecular"
    {"label": "SPECIMEN", **get_span(text_1, "molecular", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)