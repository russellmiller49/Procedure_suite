import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
# Adjust this logic if the script location changes relative to the root
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the scripts directory to the python path to import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 2724128
# ==========================================
id_1 = "2724128"
text_1 = """Pt: [REDACTED] | MRN: [REDACTED] | 52yo F
Date: [REDACTED]
Attending: Andrew Nakamura

Dx: Lung Cancer Staging
Proc: EBUS-TBNA + Robotic Bronch (Galaxy)

• GA/ETT
• Linear EBUS: Olympus BF-UC190F
• Stations: 11L (4x), 4L (3x), 10L (2x)
• Nav to RLL superior (B6)
• rEBUS: Adjacent view
• TIL confirmed: Radial EBUS
• Bx x6, TBNA x4
• ROSE+: Granuloma

Complications: None
EBL: <10mL
Dispo: Home

Andrew Nakamura MD"""

entities_1 = [
    # Dx: Lung Cancer Staging
    {"label": "OBS_LESION",         **get_span(text_1, "Lung Cancer", 1)},
    
    # Proc: EBUS-TBNA + Robotic Bronch
    {"label": "PROC_METHOD",        **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "Robotic", 1)},
    
    # Linear EBUS
    {"label": "PROC_METHOD",        **get_span(text_1, "Linear EBUS", 1)},
    
    # Stations: 11L (4x)
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "4x", 1)},
    
    # 4L (3x)
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "4L", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "3x", 1)},
    
    # 10L (2x)
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "2x", 1)},
    
    # Nav to RLL superior (B6)
    {"label": "PROC_METHOD",        **get_span(text_1, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "RLL superior", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "B6", 1)},
    
    # rEBUS / Radial EBUS
    {"label": "PROC_METHOD",        **get_span(text_1, "rEBUS", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "Radial EBUS", 1)},
    
    # Bx x6, TBNA x4
    {"label": "PROC_ACTION",        **get_span(text_1, "Bx", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "x6", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "TBNA", 2)}, # Second occurrence of TBNA
    {"label": "MEAS_COUNT",         **get_span(text_1, "x4", 1)},
    
    # ROSE+: Granuloma
    {"label": "OBS_ROSE",           **get_span(text_1, "Granuloma", 1)},
    
    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL",           **get_span(text_1, "<10mL", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)