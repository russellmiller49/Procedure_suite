import sys
from pathlib import Path

# Set up the repo root for imports
# Assuming the script is run from a location where 'scripts' is a sibling or child
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2582051
# ==========================================
id_1 = "2582051"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 46yo male here for bronch w EBUS staging and robotic biopsy of a 30.2mm LUL nodule that was ground-glass on CT, bronchus sign was positive, no PET done.

under general we did linear EBUS first using the Olympus BF-UC190F scope with 22g needle and sampled stations 4R x4, 2R x4, 2L x2, 10L x3, ROSE was there and showed Atypical cells at multiple stations.

then switched to Monarch robot and navigated to the LUL inferior lingula (B5) lesion, registration was 2.2mm which is fine, got radial EBUS showing eccentric view and did tool in lesion confirmation with cbct. took 8 forceps bx, 4 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Malignant - small cell carcinoma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Sarah Chen md
ip attending"""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_ACTION", **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},

    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22g", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "inferior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B5", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "cbct", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bx", 1)},
    # "4" appears in: "46yo", "4R", "x4", "x4", "4 needle". It is occurrence 5.
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 5)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},

    # Paragraph 4
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "small cell carcinoma", 1)},

    # Paragraph 5
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},

    # Paragraph 6
    {"label": "SPECIMEN", **get_span(text_1, "cyto", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical path", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)