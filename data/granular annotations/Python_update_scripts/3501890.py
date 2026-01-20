import sys
from pathlib import Path

# ==========================================
# Script Setup & Utility
# ==========================================

# Calculate the repository root (assuming this script is in a subdirectory like 'scripts/')
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the repository
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure REPO_ROOT is correct and the script is in the right location.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a term in the text.
    Raises ValueError if the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 3501890
# ==========================================
id_1 = "3501890"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 47yo male here for bronch w EBUS staging and robotic biopsy of a 30.4mm RML nodule that was solid on CT, bronchus sign was negative, PET showed SUV 13.0.

under general we did linear EBUS first using the Olympus BF-UC260F-OL8 scope with 22g needle and sampled stations 2R x3, 11R x3, 4R x3, 7 x2, ROSE was there and showed Adequate lymphocytes at multiple stations.

then switched to Monarch robot and navigated to the RML lateral (B4) lesion, registration was 2.6mm which is fine, got radial EBUS showing adjacent view and did tool in lesion confirmation with radial ebus. took 4 forceps bx, 2 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Suspicious for malignancy.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Lisa Thompson md
ip attending"""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.4mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    
    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC260F-OL8 scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robot", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML lateral (B4)", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    # Occurrences for "4": 47yo(1), 30.4mm(2), 4R(3), B4(4), 4 forceps(5)
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 5)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bx", 1)},
    # Occurrences for "2": 22g(1), 2R(2), x2(after 7)(3), 2.6mm(4), 2 needle(5)
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 5)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},

    # Paragraph 4
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Paragraph 5
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},

    # Paragraph 6
    {"label": "SPECIMEN", **get_span(text_1, "specimens", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cyto", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical path", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "flow", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "molecular", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")