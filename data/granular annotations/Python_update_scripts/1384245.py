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
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# 3. Data Definitions
# ==========================================

# ------------------------------------------
# Case 1: 1384245
# ------------------------------------------
id_1 = "1384245"
text_1 = """bronchoscopy note - [REDACTED]
pt [REDACTED] mrn [REDACTED] is a 57yo female here for bronch w EBUS staging and robotic biopsy of a 16.3mm RLL nodule that was ground-glass on CT, bronchus sign was positive, PET showed SUV 6.9.
under general we did linear EBUS first using the Olympus BF-UC190F scope with 22g needle and sampled stations 11L x4, 4L x3, 10L x2, ROSE was there and showed Granuloma at multiple stations.
then switched to Galaxy robot and navigated to the RLL superior (B6) lesion, registration was 3.4mm which is fine, got radial EBUS showing adjacent view and did tool in lesion confirmation with radial ebus. took 6 forceps bx, 4 needle passes, brushings x2, BAL sent for cultures.
ROSE from the nodule was Malignant - squamous cell carcinoma.
no bleeding no ptx    patient did well
specimens to path for cyto, surgical path, cell block, flow, molecular if needed
d/c home after recovery with standard precautions, f/u 1-2wks for path
Andrew Nakamura md
ip attending"""

entities_1 = [
    # "bronch w EBUS staging and robotic biopsy"
    {"label": "PROC_ACTION",      **get_span(text_1, "bronch", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION",      **get_span(text_1, "biopsy", 1)},
    
    # "16.3mm RLL nodule that was ground-glass"
    {"label": "MEAS_SIZE",        **get_span(text_1, "16.3mm", 1)},
    {"label": "ANAT_LUNG_LOC",    **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION",       **get_span(text_1, "nodule", 1)},
    {"label": "OBS_FINDING",      **get_span(text_1, "ground-glass", 1)},
    
    # "linear EBUS... 22g needle"
    {"label": "PROC_METHOD",      **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE",       **get_span(text_1, "22g", 1)},
    
    # "stations 11L x4, 4L x3, 10L x2"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "4", 1)},  # Occ 1: matches '4' in "x4"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "3", 2)},  # Occ 2: matches '3' in "x3" (after 16.3mm)
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2", 3)},  # Occ 3: matches '2' in "x2" (after 22g which has two 2s)
    
    # "showed Granuloma"
    {"label": "OBS_ROSE",        **get_span(text_1, "Granuloma", 1)},
    
    # "Galaxy robot and navigated to RLL superior (B6) lesion"
    {"label": "PROC_METHOD",      **get_span(text_1, "robot", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC",    **get_span(text_1, "RLL superior", 1)},
    {"label": "ANAT_LUNG_LOC",    **get_span(text_1, "B6", 1)},
    {"label": "OBS_LESION",       **get_span(text_1, "lesion", 1)},
    
    # "radial EBUS... radial ebus"
    {"label": "PROC_METHOD",      **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "radial ebus", 1)},
    
    # "6 forceps bx, 4 needle passes, brushings x2, BAL"
    {"label": "MEAS_COUNT",      **get_span(text_1, "6", 4)},  # Occ 4: after 16.3, 6.9, B6
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION",      **get_span(text_1, "bx", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "4", 4)},  # Occ 4: after x4, 4L, 3.4
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "needle", 2)}, # Occ 2: after "22g needle"
    {"label": "PROC_ACTION",      **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2", 4)},  # Occ 4: after 22g(x2), 10L x2
    {"label": "PROC_ACTION",      **get_span(text_1, "BAL", 1)},
    
    # "ROSE... Malignant - squamous cell carcinoma"
    {"label": "OBS_ROSE",         **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE",         **get_span(text_1, "squamous cell carcinoma", 1)},
    
    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no ptx", 1)},
    
    # Specimens
    {"label": "SPECIMEN",         **get_span(text_1, "cell block", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)