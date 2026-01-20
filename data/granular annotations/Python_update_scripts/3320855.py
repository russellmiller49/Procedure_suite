import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from a subdirectory)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure your repository structure is correct and 'scripts' is a python package.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    Returns a dictionary suitable for unpacking.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 3320855
# ==========================================
t_3320855 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 61yo female here for bronch w EBUS staging and robotic biopsy of a 31.2mm LUL nodule that was solid on CT, bronchus sign was positive, PET showed SUV 5.0.

under general we did linear EBUS first using the Olympus BF-UC180F scope with 22g needle and sampled stations 10R x4, 4R x2, 2L x4, 2R x4, 4L x3, ROSE was there and showed Malignant - NSCLC NOS at multiple stations.

then switched to Monarch robot and navigated to the LUL inferior lingula (B5) lesion, registration was 2.2mm which is fine, got radial EBUS showing concentric view and did tool in lesion confirmation with cbct. took 6 forceps bx, 2 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Malignant - squamous cell carcinoma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Brian O'Connor md
ip attending"""

e_3320855 = [
    # Paragraph 1
    {"label": "PROC_ACTION", **get_span(t_3320855, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t_3320855, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t_3320855, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t_3320855, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t_3320855, "31.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3320855, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t_3320855, "nodule", 1)},
    
    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(t_3320855, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t_3320855, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(t_3320855, "needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t_3320855, "10R", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "x4", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t_3320855, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "x2", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t_3320855, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "x4", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t_3320855, "2R", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "x4", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t_3320855, "4L", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "x3", 1)},
    {"label": "OBS_ROSE", **get_span(t_3320855, "Malignant - NSCLC NOS", 1)},
    
    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(t_3320855, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3320855, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3320855, "inferior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3320855, "B5", 1)},
    {"label": "OBS_LESION", **get_span(t_3320855, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t_3320855, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t_3320855, "cbct", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_3320855, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t_3320855, "bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "2", 1)},
    {"label": "DEV_NEEDLE", **get_span(t_3320855, "needle", 2)},
    {"label": "PROC_ACTION", **get_span(t_3320855, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3320855, "x2", 2)},
    {"label": "PROC_ACTION", **get_span(t_3320855, "BAL", 1)},
    
    # Paragraph 4
    {"label": "OBS_LESION", **get_span(t_3320855, "nodule", 2)},
    {"label": "OBS_ROSE", **get_span(t_3320855, "Malignant - squamous cell carcinoma", 1)},
    
    # Paragraph 5
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3320855, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3320855, "no ptx", 1)},
    
    # Paragraph 6
    {"label": "SPECIMEN", **get_span(t_3320855, "cyto", 1)},
    {"label": "SPECIMEN", **get_span(t_3320855, "surgical path", 1)},
    {"label": "SPECIMEN", **get_span(t_3320855, "cell block", 1)},
]

BATCH_DATA.append({"id": "3320855", "text": t_3320855, "entities": e_3320855})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")