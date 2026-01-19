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
# Note 1: 4019379
# ==========================================
text_4019379 = """TRANSBRONCHIAL CRYOBIOPSY NOTE
Date: [REDACTED]
Patient: [REDACTED] | MRN: [REDACTED] | Age: 62F
Attending: Dr. Michael Roberts, MD
Location: [REDACTED]

INDICATION: Progressive ILD with UIP pattern on HRCT. Multidisciplinary discussion recommends tissue diagnosis to guide therapy. TBLC (transbronchial lung cryobiopsy) preferred over surgical lung biopsy given comorbidities.

PROCEDURE:
1. Flexible bronchoscopy
2. Transbronchial cryobiopsy (RLL, 2 sites)
3. BAL (RML)

ANESTHESIA: General anesthesia with ETT, blocker on standby

PROCEDURE DETAILS:
Under GA, bronchoscope advanced. Airways inspected - no endobronchial lesions.

BAL performed in RML (120mL instilled, 65mL return).

TBLC performed in RLL using 1.9mm cryoprobe (Erbe):

Site [REDACTED]
- Fluoroscopy confirmed position 2cm from pleural surface
- Freeze time: 5 seconds x 3 biopsies
- Specimens 4-5mm, excellent quality
- Mild bleeding, controlled with Fogarty balloon

Site [REDACTED]
- Freeze time: 5 seconds x 2 biopsies
- Specimens 3-4mm, good quality
- Minimal bleeding

Total: 5 cryobiopsies from 2 sites

No pneumothorax on completion fluoroscopy.

SPECIMENS: Cryobiopsy RLL x 5 (surgical pathology for ILD workup)
COMPLICATIONS: Mild bleeding - controlled with blocker
DISPOSITION: 4-hour observation, CXR, discharge if stable

Dr. Michael Roberts, MD"""

entities_4019379 = [
    # --- Indications & History ---
    {"label": "OBS_FINDING", **get_span(text_4019379, "ILD", 1)},
    {"label": "OBS_FINDING", **get_span(text_4019379, "UIP pattern", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "HRCT", 1)},
    
    # --- Procedure Methods ---
    {"label": "PROC_METHOD", **get_span(text_4019379, "TBLC", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "transbronchial lung cryobiopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "surgical lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "Transbronchial cryobiopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "BAL", 1)},
    
    # --- Anatomy (Procedure Header) ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_4019379, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4019379, "RML", 1)},
    
    # --- Devices & Instruments (Anesthesia/Setup) ---
    {"label": "DEV_INSTRUMENT", **get_span(text_4019379, "ETT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4019379, "blocker", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4019379, "bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4019379, "Airways", 1)},
    
    # --- Findings & Details ---
    {"label": "OBS_LESION", **get_span(text_4019379, "endobronchial lesions", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "BAL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4019379, "RML", 2)},
    {"label": "MEAS_VOL", **get_span(text_4019379, "120mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_4019379, "65mL", 1)},
    
    # --- TBLC Specifics ---
    {"label": "PROC_METHOD", **get_span(text_4019379, "TBLC", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4019379, "RLL", 2)},
    {"label": "MEAS_SIZE", **get_span(text_4019379, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4019379, "cryoprobe", 1)},
    
    # --- Site 1 ---
    {"label": "PROC_METHOD", **get_span(text_4019379, "Fluoroscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4019379, "2cm", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4019379, "pleural surface", 1)},
    {"label": "MEAS_TIME", **get_span(text_4019379, "5 seconds", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4019379, "4-5mm", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4019379, "Mild bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4019379, "Fogarty balloon", 1)},
    
    # --- Site 2 ---
    {"label": "MEAS_TIME", **get_span(text_4019379, "5 seconds", 2)},
    {"label": "MEAS_SIZE", **get_span(text_4019379, "3-4mm", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4019379, "Minimal bleeding", 1)},
    
    # --- Outcomes ---
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4019379, "pneumothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "fluoroscopy", 1)},
    
    # --- Specimens & Summary ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_4019379, "RLL", 3)},
    {"label": "OBS_FINDING", **get_span(text_4019379, "ILD", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4019379, "Mild bleeding", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4019379, "blocker", 2)},
    {"label": "MEAS_TIME", **get_span(text_4019379, "4-hour", 1)},
    {"label": "PROC_METHOD", **get_span(text_4019379, "CXR", 1)},
]
BATCH_DATA.append({"id": "4019379", "text": text_4019379, "entities": entities_4019379})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)