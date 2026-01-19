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
# Note 1: 3387971
# ==========================================
t_3387971 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 61yo female here for bronch w EBUS staging and robotic biopsy of a 16.9mm RML nodule that was solid on CT, bronchus sign was positive, PET showed SUV 16.9.

under general we did linear EBUS first using the Olympus BF-UC190F scope with 21g needle and sampled stations 10R x3, 4L x2, 4R x3, ROSE was there and showed Adequate lymphocytes, no malignancy at multiple stations.

then switched to Monarch robot and navigated to the RML lateral (B4) lesion, registration was 2.5mm which is fine, got radial EBUS showing concentric view and did tool in lesion confirmation with augmented fluoroscopy. took 8 forceps bx, 4 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Adequate lymphocytes.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

David Kim md
ip attending"""

e_3387971 = [
    {"label": "PROC_METHOD", **get_span(t_3387971, "bronch", 2)},
    {"label": "PROC_METHOD", **get_span(t_3387971, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t_3387971, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t_3387971, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t_3387971, "16.9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3387971, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t_3387971, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(t_3387971, "solid", 1)},
    {"label": "OBS_FINDING", **get_span(t_3387971, "bronchus sign", 1)},
    {"label": "PROC_METHOD", **get_span(t_3387971, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t_3387971, "21g", 1)},
    {"label": "DEV_NEEDLE", **get_span(t_3387971, "needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t_3387971, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t_3387971, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t_3387971, "4R", 1)},
    {"label": "OBS_ROSE", **get_span(t_3387971, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(t_3387971, "no malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t_3387971, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3387971, "RML lateral (B4)", 1)},
    {"label": "MEAS_SIZE", **get_span(t_3387971, "2.5mm", 1)},
    {"label": "PROC_METHOD", **get_span(t_3387971, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t_3387971, "concentric view", 1)},
    {"label": "OBS_FINDING", **get_span(t_3387971, "tool in lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t_3387971, "augmented fluoroscopy", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3387971, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_3387971, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t_3387971, "bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3387971, "4", 4)},
    {"label": "DEV_NEEDLE", **get_span(t_3387971, "needle", 2)},
    {"label": "PROC_ACTION", **get_span(t_3387971, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(t_3387971, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t_3387971, "Adequate lymphocytes", 2)},
    {"label": "OBS_LESION", **get_span(t_3387971, "nodule", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3387971, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3387971, "no ptx", 1)},
    {"label": "SPECIMEN", **get_span(t_3387971, "cell block", 1)}
]
BATCH_DATA.append({"id": "3387971", "text": t_3387971, "entities": e_3387971})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)