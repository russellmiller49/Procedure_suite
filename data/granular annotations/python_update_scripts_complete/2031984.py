import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text: {text[:50]}...")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2031984
# ==========================================
t1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 53yo male here for bronch w EBUS staging and robotic biopsy of a 27.1mm RLL nodule that was solid on CT, bronchus sign was negative, PET showed SUV 6.1.

under general we did linear EBUS first using the Olympus BF-UC190F scope with 22g needle and sampled stations 4L x3, 2R x3, 2L x2, ROSE was there and showed Suspicious for malignancy at multiple stations.

then switched to Ion robot and navigated to the RLL superior (B6) lesion, registration was 1.8mm which is fine, got radial EBUS showing adjacent view and did tool in lesion confirmation with augmented fluoroscopy. took 5 forceps bx, 2 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Malignant - squamous cell carcinoma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Amanda Foster md
ip attending"""

e1 = [
    {"label": "PROC_ACTION", **get_span(t1, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "27.1mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "solid", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "2L", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Suspicious for malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion robot", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL superior (B6)", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "augmented fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "bx", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "needle", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "ptx", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cyto", 1)},
    {"label": "SPECIMEN", **get_span(t1, "surgical path", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cell block", 1)}
]

BATCH_DATA.append({"id": "2031984", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)