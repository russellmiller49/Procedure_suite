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
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2885591
# ==========================================
id_1 = "2885591"
text_1 = """NAVIGATION BRONCHOSCOPY NOTE
Date: [REDACTED]
Patient: [REDACTED] | MRN: [REDACTED] | Age: 58F
Attending: Dr. Michael Park, MD | Fellow: Dr. Karen Chen (PGY-6)
Location: [REDACTED]

INDICATION: 15mm LUL ground-glass nodule (SUV 3.2), bronchus sign positive. Biopsy for diagnosis.

PROCEDURE: Ion robotic bronchoscopy with transbronchial cryobiopsy

Under GA, Ion platform registration performed (fiducial-less, registration error 1.2mm). Navigation to LUL anterior segment (LB3). Radial EBUS showed concentric lesion view. Target lock confirmed. 

Cryoprobe (1.9mm) advanced under augmented fluoroscopy. Tool-in-lesion confirmed on CBCT. 3 cryobiopsies obtained (4-second freeze time each). Specimens 3-4mm, sent to surgical pathology. Mild bleeding controlled with wedge technique. No pneumothorax on completion fluoro.

FINDINGS: r-EBUS concentric view, CBCT TIL confirmed, adequate specimens

SPECIMENS: Cryobiopsy LUL x 3 - surgical pathology

COMPLICATIONS: Mild bleeding - self-limited
DISPOSITION: Outpatient discharge after 2hr CXR

Dr. Michael Park, MD"""

entities_1 = [
    # Indication
    {"label": "MEAS_SIZE", **get_span(text_1, "15mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},
    
    # Procedure Header
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "transbronchial cryobiopsy", 1)},
    
    # Procedure Body
    # "Ion" in "Ion platform" is 2nd occurrence (1st is in "Ion robotic...")
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion", 2)},
    
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL anterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB3", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric lesion view", 1)},
    
    # Paragraph 2
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cryoprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "augmented fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    
    # "3" occurrences: 1."3.2", 2."LB3", 3."3 cryobiopsies"
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 3)},
    {"label": "PROC_METHOD", **get_span(text_1, "cryobiopsies", 1)},
    
    {"label": "MEAS_TIME", **get_span(text_1, "4-second", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3-4mm", 1)},
    
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "wedge technique", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 1)},
    
    # Findings
    {"label": "PROC_METHOD", **get_span(text_1, "r-EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric view", 1)},
    
    # CBCT 2nd occurrence
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "TIL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "adequate specimens", 1)},
    
    # Specimens
    {"label": "PROC_METHOD", **get_span(text_1, "Cryobiopsy", 1)}, # Capitalized
    # LUL 3rd occurrence: 1."15mm LUL", 2."Navigation to LUL", 3."Cryobiopsy LUL"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 3)},
    
    # "x 3" occurrences: 3."3 cryo", 4."3-4mm", 5."x 3"
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 5)},
    
    # Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "bleeding", 2)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)