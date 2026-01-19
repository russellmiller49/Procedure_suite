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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: SYN_0_6_2852
# ==========================================
id_1 = "SYN_0_6_2852"
text_1 = """On [REDACTED] a bedside chest tube placement was performed for a right malignant pleural effusion. Ultrasound of the right chest demonstrated a moderate anechoic effusion with nodular pleura. The site was prepped. 1% lidocaine was used. A 12 Fr pigtail catheter was inserted into the right 8th intercostal space using the Seldinger technique. 450 ml of bloody fluid was drained. The catheter was sutured in place and attached to a Pneumostat. There were no complications. Post-procedure plan includes a chest xray."""

entities_1 = [
    # [cite_start]"chest tube" -> DEV_CATHETER [cite: 6]
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    
    # [cite_start]"right" -> LATERALITY [cite: 4]
    {"label": "LATERALITY", **get_span(text_1, "right", 1)},
    
    # [cite_start]"pleural effusion" -> OBS_LESION (Target abnormality) [cite: 11]
    {"label": "OBS_LESION", **get_span(text_1, "pleural effusion", 1)},
    
    # [cite_start]"Ultrasound" -> PROC_METHOD [cite: 10]
    {"label": "PROC_METHOD", **get_span(text_1, "Ultrasound", 1)},
    
    # [cite_start]"right" -> LATERALITY [cite: 4]
    {"label": "LATERALITY", **get_span(text_1, "right", 2)},
    
    # [cite_start]"effusion" -> OBS_LESION [cite: 11]
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 2)},
    
    # [cite_start]"nodular" -> OBS_FINDING [cite: 20]
    {"label": "OBS_FINDING", **get_span(text_1, "nodular", 1)},
    
    # [cite_start]"pleura" -> ANAT_PLEURA [cite: 3]
    {"label": "ANAT_PLEURA", **get_span(text_1, "pleura", 1)},
    
    # [cite_start]"lidocaine" -> MEDICATION [cite: 21]
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    
    # [cite_start]"12 Fr pigtail catheter" -> DEV_CATHETER_SIZE (Example: "14 Fr pigtail") [cite: 18]
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "12 Fr pigtail catheter", 1)},
    
    # [cite_start]"pigtail catheter" -> DEV_CATHETER [cite: 5]
    {"label": "DEV_CATHETER", **get_span(text_1, "pigtail catheter", 1)},
    
    # [cite_start]"right" -> LATERALITY [cite: 4]
    {"label": "LATERALITY", **get_span(text_1, "right", 3)},
    
    # [cite_start]"8th intercostal space" -> ANAT_PLEURA (Chest wall/entry site) [cite: 3]
    {"label": "ANAT_PLEURA", **get_span(text_1, "8th intercostal space", 1)},
    
    # [cite_start]"Seldinger technique" -> PROC_METHOD [cite: 10]
    {"label": "PROC_METHOD", **get_span(text_1, "Seldinger technique", 1)},
    
    # [cite_start]"450 ml" -> MEAS_VOL [cite: 8]
    {"label": "MEAS_VOL", **get_span(text_1, "450 ml", 1)},
    
    # [cite_start]"bloody" -> OBS_FINDING (Description of fluid) [cite: 20]
    {"label": "OBS_FINDING", **get_span(text_1, "bloody", 1)},
    
    # [cite_start]"fluid" -> SPECIMEN [cite: 22]
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)},
    
    # [cite_start]"Pneumostat" -> DEV_CATHETER (Brand of drainage device/catheter system) [cite: 5]
    {"label": "DEV_CATHETER", **get_span(text_1, "Pneumostat", 1)},
    
    # [cite_start]"no complications" -> OUTCOME_COMPLICATION [cite: 16]
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no complications", 1)},
    
    # [cite_start]"chest xray" -> PROC_METHOD (Diagnostic method) [cite: 10]
    {"label": "PROC_METHOD", **get_span(text_1, "chest xray", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)