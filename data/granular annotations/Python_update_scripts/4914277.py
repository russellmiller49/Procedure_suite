import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts folder
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from scripts.add_training_case.")
    print("Ensure you are running this script from the correct location within the repository.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact string to find.
        occurrence (int): The 1-based index of the occurrence to find.
        
    Returns:
        tuple: (start_index, end_index) or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return start, start + len(term)

# ==========================================
# Case 1: 4914277
# ==========================================
id_1 = "4914277"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 64yo male here for bronch w EBUS staging and robotic biopsy of a 25.0mm LUL nodule that was solid on CT, bronchus sign was positive, PET showed SUV 9.6.

under general we did linear EBUS first using the Fujifilm EB-580S scope with 21g needle and sampled stations 7 x4, 11L x2, 10R x4, 4L x3, ROSE was there and showed Granuloma at multiple stations.

then switched to Monarch robot and navigated to the LUL anterior (B3) lesion, registration was 1.6mm which is fine, got radial EBUS showing eccentric view and did tool in lesion confirmation with fluoroscopy. took 4 forceps bx, 3 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Malignant - squamous cell carcinoma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Andrew Nakamura md
ip attending"""

entities_1 = [
    # "bronch" -> PROC_ACTION (Bronchoscopy)
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "bronch", 2)))},
    # "EBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "EBUS", 1)))},
    # "robotic" -> PROC_METHOD
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "robotic", 1)))},
    # "biopsy" -> PROC_ACTION
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "biopsy", 1)))},
    # "25.0mm" -> MEAS_SIZE
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "25.0mm", 1)))},
    # "LUL" -> ANAT_LUNG_LOC
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "LUL", 1)))},
    # "nodule" -> OBS_LESION
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "nodule", 1)))},
    # "bronchus sign" -> OBS_FINDING
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(text_1, "bronchus sign", 1)))},
    
    # "linear EBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "linear EBUS", 1)))},
    # "Fujifilm EB-580S" -> DEV_INSTRUMENT (Scope/Device)
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Fujifilm EB-580S", 1)))},
    # "21g" -> DEV_NEEDLE
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "21g", 1)))},
    # "needle" -> DEV_NEEDLE (generic)
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "needle", 1)))},
    
    # Lymph Node Stations
    # "stations 7" -> ANAT_LN_STATION
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "stations 7", 1)))},
    # "x4" -> MEAS_COUNT (passes for st 7)
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x4", 1)))},
    # "11L" -> ANAT_LN_STATION
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "11L", 1)))},
    # "x2" -> MEAS_COUNT (passes for 11L)
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x2", 1)))},
    # "10R" -> ANAT_LN_STATION
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "10R", 1)))},
    # "x4" -> MEAS_COUNT (passes for 10R)
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x4", 2)))},
    # "4L" -> ANAT_LN_STATION
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "4L", 1)))},
    # "x3" -> MEAS_COUNT (passes for 4L)
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x3", 1)))},
    
    # "Granuloma" -> OBS_ROSE
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "Granuloma", 1)))},
    
    # "Monarch robot" -> PROC_METHOD
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "Monarch robot", 1)))},
    # "LUL" -> ANAT_LUNG_LOC
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "LUL", 2)))},
    # "B3" -> ANAT_LUNG_LOC
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "B3", 1)))},
    # "lesion" -> OBS_LESION
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "lesion", 1)))},
    # "radial EBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "radial EBUS", 1)))},
    # "eccentric view" -> OBS_FINDING
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(text_1, "eccentric view", 1)))},
    # "fluoroscopy" -> PROC_METHOD
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "fluoroscopy", 1)))},
    
    # "forceps" -> DEV_INSTRUMENT
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "forceps", 1)))},
    # "bx" -> PROC_ACTION (biopsy)
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "bx", 1)))},
    # "3 needle passes" -> MEAS_COUNT
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "3 needle passes", 1)))},
    # "needle" -> DEV_NEEDLE (inside the count phrase, usually we capture the tool separately too if possible, but distinct spans preferred. Here we capture "needle" separate from the count phrase if distinct, but overlapping is tricky. Let's act strictly: "needle" is the device.)
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "needle", 2)))},
    # "brushings" -> PROC_ACTION
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "brushings", 1)))},
    # "x2" -> MEAS_COUNT
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x2", 2)))},
    # "BAL" -> PROC_ACTION
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "BAL", 1)))},
    
    # "Malignant" -> OBS_ROSE
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "Malignant", 1)))},
    # "squamous cell carcinoma" -> OBS_ROSE
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "squamous cell carcinoma", 1)))},
    
    # "no bleeding" -> OUTCOME_COMPLICATION
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_1, "no bleeding", 1)))},
    # "no ptx" -> OUTCOME_COMPLICATION
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_1, "no ptx", 1)))},
    
    # "cell block" -> SPECIMEN
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_1, "cell block", 1)))},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)