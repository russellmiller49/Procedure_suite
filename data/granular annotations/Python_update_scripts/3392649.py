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
# Note 1: 3392649
# ==========================================
id_3392649 = "3392649"
text_3392649 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Michael Chen

Indication: Hepatic hydrothorax
Side: Right

PROCEDURE: Ultrasound-guided Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Real-time ultrasound used throughout procedure.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 14Fr pigtail catheter inserted.
1011mL turbid fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Chen, MD"""

entities_3392649 = [
    # Indication: Hepatic hydrothorax -> OBS_LESION (maps to indication)
    {"label": "OBS_LESION", **get_span(text_3392649, "Hepatic hydrothorax", 1)},
    
    # Side: Right -> LATERALITY
    {"label": "LATERALITY", **get_span(text_3392649, "Right", 1)},
    
    # PROCEDURE: Ultrasound-guided -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_3392649, "Ultrasound-guided", 1)},
    
    # Pleural (in Pleural Drainage) -> ANAT_PLEURA
    {"label": "ANAT_PLEURA", **get_span(text_3392649, "Pleural", 1)},
    
    # Catheter (in Catheter Placement) -> DEV_CATHETER
    {"label": "DEV_CATHETER", **get_span(text_3392649, "Catheter", 1)},
    
    # Real-time ultrasound -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_3392649, "Real-time ultrasound", 1)},
    
    # lidocaine -> MEDICATION
    {"label": "MEDICATION", **get_span(text_3392649, "lidocaine", 1)},
    
    # Seldinger technique -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_3392649, "Seldinger technique", 1)},
    
    # 14Fr pigtail catheter -> DEV_CATHETER_SIZE (matches "14 Fr pigtail" pattern)
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3392649, "14Fr pigtail catheter", 1)},
    
    # 1011mL -> MEAS_VOL
    {"label": "MEAS_VOL", **get_span(text_3392649, "1011mL", 1)},
    
    # turbid fluid -> SPECIMEN (fluid matches SPECIMEN, turbid matches findings, keeping specific specimen phrase)
    {"label": "SPECIMEN", **get_span(text_3392649, "turbid fluid", 1)},
    
    # Catheter (in Catheter secured) -> DEV_CATHETER
    {"label": "DEV_CATHETER", **get_span(text_3392649, "Catheter", 2)},
    
    # catheter (in catheter in appropriate position) -> DEV_CATHETER
    # Note: 1st lowercase "catheter" is inside "14Fr pigtail catheter". 2nd is standalone.
    {"label": "DEV_CATHETER", **get_span(text_3392649, "catheter", 2)},
    
    # no PTX -> OUTCOME_COMPLICATION
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3392649, "no PTX", 1)},
]

BATCH_DATA.append({"id": id_3392649, "text": text_3392649, "entities": entities_3392649})


# ==========================================
# 3. Execution Loop
# ==========================================

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)