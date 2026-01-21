import sys
from pathlib import Path

# Calculate the root of the repository to import the utility function
REPO_ROOT = Path(__file__).resolve().parent.parent
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
# Note 1: 1225416
# ==========================================
id_1 = "1225416"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 67yo male here for bronch w EBUS staging and robotic biopsy of a 29.4mm LLL nodule that was part-solid on CT, bronchus sign was negative, no PET done.

under general we did linear EBUS first using the Pentax EB-1990i scope with 22g needle and sampled stations 10R x3, 10L x2, 11R x3, ROSE was there and showed Suspicious for malignancy at multiple stations.

then switched to Ion robot and navigated to the LLL lateral basal (B9) lesion, registration was 1.8mm which is fine, got radial EBUS showing adjacent view and did tool in lesion confirmation with fluoroscopy. took 6 forceps bx, 2 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Malignant - squamous cell carcinoma.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

Brian O'Connor md
ip attending"""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_ACTION",       **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "29.4mm", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION",        **get_span(text_1, "nodule", 1)},

    # Paragraph 2
    {"label": "PROC_METHOD",       **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_1, "22g", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_1, "needle", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "sampled", 1)},
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "10R", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "x3", 1)},
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "x2", 1)},
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "11R", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "x3", 2)},
    {"label": "OBS_ROSE",          **get_span(text_1, "Suspicious for malignancy", 1)},

    # Paragraph 3
    {"label": "PROC_METHOD",       **get_span(text_1, "Ion robot", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "lateral basal (B9)", 1)},
    {"label": "OBS_LESION",        **get_span(text_1, "lesion", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "fluoroscopy", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "6", 1)}, # Associated with forceps bx
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "bx", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "2", 1)}, # Associated with needle passes
    {"label": "DEV_NEEDLE",        **get_span(text_1, "needle", 2)},
    {"label": "PROC_ACTION",       **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "x2", 2)}, # Associated with brushings
    {"label": "PROC_ACTION",       **get_span(text_1, "BAL", 1)},

    # Paragraph 4
    {"label": "OBS_ROSE",          **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE",          **get_span(text_1, "squamous cell carcinoma", 1)},

    # Paragraph 5
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},

    # Paragraph 6
    {"label": "SPECIMEN",          **get_span(text_1, "cell block", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)