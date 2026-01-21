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
# Note 1: 2189773
# ==========================================
id_1 = "2189773"
text_1 = """PROCEDURE NOTE
Date: [REDACTED] | Patient: Henry Smith | MRN: [REDACTED]
Attending: Dr. Angela Morrison, MD | Location: [REDACTED]

PROCEDURE: Indwelling pleural catheter access and drainage

INDICATION: Established left PleurX catheter (placed 3 weeks ago) for malignant mesothelioma with recurrent effusion. Patient reports increased dyspnea and has not been able to drain at home due to suspected catheter occlusion.

PROCEDURE: Under sterile technique, the PleurX catheter was accessed. Initial aspiration revealed thick loculated fluid. The catheter was flushed with 10mL saline with return of cloudy fluid. A total of 850mL of serosanguinous fluid was drained. tPA 4mg/40mL NS was instilled per protocol for suspected fibrinous occlusion. Patient to clamp for 2 hours then attempt drainage.

SPECIMENS: Pleural fluid to cytology, culture

COMPLICATIONS: None

PLAN: Home health to continue daily drainage. Return if unable to drain. Consider fibrinolytic protocol if recurrent.

Angela Morrison, MD"""

entities_1 = [
    # Header/Title
    {"label": "DEV_CATHETER", **get_span(text_1, "Indwelling pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "access", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "drainage", 1)},

    # Indication Section
    {"label": "LATERALITY", **get_span(text_1, "left", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "PleurX catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "malignant mesothelioma", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "occlusion", 1)}, # suspected catheter occlusion

    # Procedure Body
    {"label": "DEV_CATHETER", **get_span(text_1, "PleurX catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "accessed", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "loculated fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "flushed", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "cloudy fluid", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "850mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "serosanguinous fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "drained", 1)}, # "was drained"
    {"label": "MEDICATION", **get_span(text_1, "tPA", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "40mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "instilled", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "fibrinous occlusion", 1)},

    # Specimens Section
    {"label": "SPECIMEN", **get_span(text_1, "Pleural fluid", 1)},

    # Complications Section
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)