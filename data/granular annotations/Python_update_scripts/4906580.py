import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
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
# Note 1: 4906580
# ==========================================
id_1 = "4906580"
text_1 = """EBUS PROCEDURE NOTE
Date: [REDACTED]
Patient: [REDACTED] | MRN: [REDACTED] | Age: 71M
Attending: Dr. Christine Lee, MD
Cytopathologist: Dr. Mark Thompson, MD
Location: [REDACTED]

INDICATION: 71M with 3.5cm RUL mass (SUV 12), PET-positive mediastinal nodes (4R, 7). EBUS for staging prior to treatment planning.

PROCEDURE: EBUS-TBNA

ANESTHESIA: Moderate sedation

RESULTS:

Station 4R (Right lower paratracheal):
- 20mm, heterogeneous, no CHS
- 4 passes with 22G needle
- ROSE: POSITIVE - Adenocarcinoma

Station 7 (Subcarinal):
- 24mm, round, heterogeneous
- 4 passes
- ROSE: POSITIVE - Adenocarcinoma

Station 11R (Right interlobar):
- 12mm
- 3 passes
- ROSE: POSITIVE - Adenocarcinoma

Specimens sent for cell block, molecular testing (EGFR, ALK, ROS1, PD-L1).

IMPRESSION: EBUS-TBNA confirms metastatic adenocarcinoma at stations 4R, 7, 11R. Pathologic N2 disease. Stage IIIA (cT2aN2M0).

PLAN: Medical oncology referral for concurrent chemoradiation.

Dr. Christine Lee, MD"""

entities_1 = [
    # Indication
    {"label": "MEAS_SIZE", **get_span(text_1, "3.5cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},

    # Procedure
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},

    # Station 4R Results
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Right lower paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "POSITIVE", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 1)},

    # Station 7 Results
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Subcarinal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "POSITIVE", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 2)},

    # Station 11R Results
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Right interlobar", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "POSITIVE", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 3)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},

    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 2)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)