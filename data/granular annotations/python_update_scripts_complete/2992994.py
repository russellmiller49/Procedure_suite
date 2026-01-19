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
# 2. Helper Definition
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 2992994
# ==========================================
text_1 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Jennifer Lee

Indication: Malignant pleural effusion - breast cancer
Side: Left

PROCEDURE: Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 10Fr pigtail catheter inserted.
1599mL turbid fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Lee, MD"""

entities_1 = [
    # Indication: Mapped to OBS_LESION per schema map (indication -> OBS_LESION)
    {"label": "OBS_LESION",         **get_span(text_1, "Malignant pleural effusion", 1)},
    {"label": "LATERALITY",         **get_span(text_1, "Left", 1)},
    
    # Procedure Info
    {"label": "PROC_ACTION",        **get_span(text_1, "Pleural Drainage Catheter Placement", 1)},
    {"label": "MEDICATION",         **get_span(text_1, "lidocaine", 1)},
    
    # "Seldinger technique" describes the "how" (PROC_METHOD)
    {"label": "PROC_METHOD",        **get_span(text_1, "Seldinger technique", 1)},
    
    # Device details
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_1, "10Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_1, "pigtail catheter", 1)},
    
    # Measurements and Findings
    {"label": "MEAS_VOL",           **get_span(text_1, "1599mL", 1)},
    {"label": "OBS_FINDING",        **get_span(text_1, "turbid", 1)},
    
    # Outcomes: "no PTX" serves as complication check (similar to "pneumothorax treated" / "no complications")
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no PTX", 1)},
]

BATCH_DATA.append({"id": "2992994", "text": text_1, "entities": entities_1})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)