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
# Note 1: 3207783
# ==========================================
text_3207783 = """PROCEDURE NOTE - WHOLE LUNG LAVAGE
Date: [REDACTED]
Patient: [REDACTED] | MRN: [REDACTED] | Age: 52M
Attending: Dr. Maria Rodriguez, MD
Anesthesia: Dr. John Smith, MD
Location: [REDACTED]

INDICATION: Pulmonary alveolar proteinosis (PAP), anti-GM-CSF autoantibody positive, progressive hypoxia (SpO2 85% on 6L NC). Therapeutic whole lung lavage.

PROCEDURE: Left whole lung lavage under general anesthesia

ANESTHESIA: General, double-lumen ETT (39Fr left-sided)

PROCEDURE DETAILS:
Left lung isolation confirmed with fiberoptic bronchoscopy through DLT. Right lung ventilated with 100% O2.

Left lung lavage:
- Warmed sterile saline (37°C) instilled in 1L aliquots
- Total instilled: 15L
- Total returned: 14.2L (95% return)
- Initial return: Milky white (classic PAP appearance)
- Final return: Nearly clear

Procedure duration: 3.5 hours
Lowest SpO2: 92% on FiO2 100%

SPECIMENS: Lavage fluid sent for cytology (lipid-laden macrophages)

COMPLICATIONS: None

POST-PROCEDURE: Patient extubated in OR. SpO2 94% on 4L NC (improved from baseline). Admitted to SICU overnight.

PLAN: CXR in AM. Consider right lung lavage in 1-2 weeks if needed.

Dr. Maria Rodriguez, MD"""

entities_3207783 = [
    {"label": "PROC_ACTION",    **get_span(text_3207783, "WHOLE LUNG LAVAGE", 1)},
    {"label": "OBS_FINDING",    **get_span(text_3207783, "Pulmonary alveolar proteinosis", 1)},
    {"label": "OBS_FINDING",    **get_span(text_3207783, "PAP", 1)},
    {"label": "OBS_FINDING",    **get_span(text_3207783, "hypoxia", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3207783, "whole lung lavage", 1)},  # Indication section
    {"label": "LATERALITY",     **get_span(text_3207783, "Left", 1)},               # Procedure section
    {"label": "PROC_ACTION",    **get_span(text_3207783, "whole lung lavage", 2)},  # Procedure section
    {"label": "DEV_INSTRUMENT", **get_span(text_3207783, "double-lumen ETT", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_3207783, "39Fr", 1)},
    {"label": "LATERALITY",     **get_span(text_3207783, "left-sided", 1)},
    {"label": "LATERALITY",     **get_span(text_3207783, "Left", 2)},               # Details: Left lung isolation
    {"label": "PROC_ACTION",    **get_span(text_3207783, "lung isolation", 1)},
    {"label": "PROC_METHOD",    **get_span(text_3207783, "fiberoptic bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3207783, "DLT", 1)},
    {"label": "LATERALITY",     **get_span(text_3207783, "Right", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3207783, "ventilated", 1)},
    {"label": "MEDICATION",     **get_span(text_3207783, "100% O2", 1)},
    {"label": "LATERALITY",     **get_span(text_3207783, "Left", 3)},               # Details: Left lung lavage
    {"label": "PROC_ACTION",    **get_span(text_3207783, "lung lavage", 3)},        # Occ 3: Matches "Left lung lavage:"
    {"label": "MEDICATION",     **get_span(text_3207783, "sterile saline", 1)},
    {"label": "MEAS_TEMP",      **get_span(text_3207783, "37°C", 1)},
    {"label": "MEAS_VOL",       **get_span(text_3207783, "1L", 1)},
    {"label": "MEAS_VOL",       **get_span(text_3207783, "15L", 1)},
    {"label": "MEAS_VOL",       **get_span(text_3207783, "14.2L", 1)},
    {"label": "OBS_FINDING",    **get_span(text_3207783, "Milky white", 1)},
    {"label": "OBS_FINDING",    **get_span(text_3207783, "PAP", 2)},
    {"label": "OBS_FINDING",    **get_span(text_3207783, "clear", 1)},
    {"label": "MEAS_TIME",      **get_span(text_3207783, "3.5 hours", 1)},
    {"label": "SPECIMEN",       **get_span(text_3207783, "Lavage fluid", 1)},
    {"label": "OBS_FINDING",    **get_span(text_3207783, "lipid-laden macrophages", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3207783, "None", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3207783, "extubated", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_3207783, "improved", 1)},
    {"label": "LATERALITY",     **get_span(text_3207783, "right", 1)},              # Plan (lowercase)
    {"label": "PROC_ACTION",    **get_span(text_3207783, "lung lavage", 4)}         # Plan
]

BATCH_DATA.append({"id": "3207783", "text": text_3207783, "entities": entities_3207783})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)