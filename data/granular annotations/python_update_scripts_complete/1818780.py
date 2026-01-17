import sys
from pathlib import Path

# Set the repository root (assuming script is run from the repo structure)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure you are running from the correct repository context.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1818780
# ==========================================
id_1 = "1818780"
text_1 = """bronchoscopy note - [REDACTED]

pt [REDACTED] mrn [REDACTED] is a 62yo male here for bronch w EBUS staging and robotic biopsy of a 27.1mm LLL nodule that was ground-glass on CT, bronchus sign was positive, PET showed SUV 15.4.

under general we did linear EBUS first using the Olympus BF-UC260F-OL8 scope with 19g needle and sampled stations 2L x4, 4R x4, 7 x3, 11R x3, ROSE was there and showed Malignant - squamous cell carcinoma at multiple stations.

then switched to Ion robot and navigated to the LLL posterior basal (B10) lesion, registration was 1.9mm which is fine, got radial EBUS showing eccentric view and did tool in lesion confirmation with radial ebus. took 7 forceps bx, 3 needle passes, brushings x2, BAL sent for cultures.

ROSE from the nodule was Atypical cells.

no bleeding no ptx   patient did well

specimens to path for cyto, surgical path, cell block, flow, molecular if needed

d/c home after recovery with standard precautions, f/u 1-2wks for path

David Kim md
ip attending"""

entities_1 = [
    # "bronch": Colloquial for Bronchoscopy
    {"label": "PROC_ACTION", **get_span(text_1, "bronch", 1)},
    # "EBUS": Guidance/technology
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    # "robotic": Guidance/technology
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    # "biopsy": Specific intervention
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    # "27.1mm": Linear dimension
    {"label": "MEAS_SIZE", **get_span(text_1, "27.1mm", 1)},
    # "LLL": Lung parenchyma/lobe
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    # "nodule": Target abnormality
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    # "ground-glass": General clinical finding
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    # "bronchus sign": General clinical finding
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},
    
    # "linear EBUS": Guidance/technology
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    # "Olympus BF-UC260F-OL8": Instrument/Scope
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC260F-OL8", 1)},
    # "19g": Needle size
    {"label": "DEV_NEEDLE", **get_span(text_1, "19g", 1)},
    # "needle": Needle device
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 1)},
    # "sampled": Action (TBNA equivalent)
    {"label": "PROC_ACTION", **get_span(text_1, "sampled", 1)},
    
    # Stations and counts
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)}, # Associated with 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 2)}, # Associated with 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)}, # Station 7
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 1)}, # Associated with 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x3", 2)}, # Associated with 11R
    
    # "Malignant - squamous cell carcinoma": ROSE result
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},
    
    # "Ion robot": Guidance/technology
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robot", 1)},
    # "LLL posterior basal (B10)": Lung location
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL posterior basal (B10)", 1)},
    # "lesion": Target abnormality
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    # "radial EBUS": Guidance/technology
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    # "eccentric view": General finding (ultrasound view)
    {"label": "OBS_FINDING", **get_span(text_1, "eccentric view", 1)},
    # "radial ebus": Guidance/technology (lowercase)
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    
    # "7": Count (forceps bx)
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 2)},
    # "forceps": Instrument
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    # "bx": Action (Biopsy)
    {"label": "PROC_ACTION", **get_span(text_1, "bx", 1)},
    
    # "3": Count (needle passes)
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)}, # "7 x3" was earlier, need to be careful with counts. 
    # Logic check:
    # 1. "2L x4" -> x4 (1)
    # 2. "4R x4" -> x4 (2)
    # 3. "7 x3" -> 7 (1), x3 (1)
    # 4. "11R x3" -> 11R, x3 (2)
    # 5. "took 7 forceps" -> 7 (2)
    # 6. "3 needle passes" -> 3 (1) (Previous 3 was part of 'x3') -> Wait, "x3" contains "3". 
    #    get_span uses exact string match. "x3" does not match "3". "3" matches "3".
    #    Does "x3" contain "3"? Yes. 
    #    Python find("3") on "7 x3, 11R x3":
    #    First "3" is inside "x3" (1). Second "3" is inside "x3" (2).
    #    Third "3" is in "3 needle passes".
    #    So "3" occurrence is 3.
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 3)}, 

    # "needle": Device (Needle passes)
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 2)},
    
    # "brushings": Action/Intervention
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    # "x2": Count
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    # "BAL": Action (Lavage)
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    
    # "nodule": Target (2nd occurrence)
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    # "Atypical cells": ROSE result
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    
    # "no bleeding": Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    # "no ptx": Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},
    
    # "cyto": Specimen
    {"label": "SPECIMEN", **get_span(text_1, "cyto", 1)},
    # "surgical path": Specimen
    {"label": "SPECIMEN", **get_span(text_1, "surgical path", 1)},
    # "cell block": Specimen
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    # "flow": Specimen
    {"label": "SPECIMEN", **get_span(text_1, "flow", 1)},
    # "molecular": Specimen
    {"label": "SPECIMEN", **get_span(text_1, "molecular", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)