import sys
from pathlib import Path

# Set the root directory (assuming this script is in specific subdirectory structure)
# Adjust REPO_ROOT calculation as needed for your actual environment
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to sys.path to access utility functions
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a case-sensitive term.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        list: [start_index, end_index]
    
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return [start_index, start_index + len(term)]

# ==========================================
# Case 1: 1977516
# ==========================================
id_1 = "1977516"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 77yo female here for bronch w EBUS staging and robotic biopsy of a 22.6mm RUL nodule that was solid on CT, bronchus sign was negative, PET showed SUV 9.7.

under general we did linear EBUS first using the Olympus BF-UC190F scope with 22g needle and sampled stations 11R x3, 2L x2, 4R x3, 11L x3, ROSE was there and showed Malignant - adenocarcinoma at multiple stations.

then switched to Galaxy robot and navigated to the RUL apical (B1) lesion, registration was 1.8mm which is fine, got radial EBUS showing concentric view and did tool in lesion confirmation with cbct. took 4 forceps bx, 4 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Suspicious for malignancy.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Brian O'Connor md
ip attending"""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "bronch", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "EBUS", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "robotic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "biopsy", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "22.6mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RUL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "nodule", 1)))},
    
    # Paragraph 2
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "linear EBUS", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Olympus BF-UC190F scope", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "22g", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "needle", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "sampled", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "11R", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x3", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "2L", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x2", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "4R", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x3", 2)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "11L", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x3", 3)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "Malignant - adenocarcinoma", 1)))},
    
    # Paragraph 3
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "Galaxy robot", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RUL", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "apical (B1)", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "lesion", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "radial EBUS", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "cbct", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "4", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "bx", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "4", 2)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "needle", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "brushings", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x2", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "BAL", 1)))},
    
    # Paragraph 4
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "Suspicious for malignancy", 1)))},
    
    # Paragraph 5
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_1, "bleeding", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_1, "ptx", 1)))},
    
    # Paragraph 6
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_1, "cyto", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_1, "surgical path", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_1, "cell block", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_1, "flow", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_1, "molecular", 1)))},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)