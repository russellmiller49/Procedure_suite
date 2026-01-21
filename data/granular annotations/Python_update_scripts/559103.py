import sys
from pathlib import Path

# Set up the repository root (assumes this script is running two levels deep or similar structure)
# Adjust this based on actual environment needs, defaulting to current working directory parent if needed.
REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for standalone testing if the utility isn't in the path
    print("Warning: 'scripts.add_training_case' not found. Mocking function for dry-run.")
    def add_case(case_id, text, entities, root):
        print(f"Adding case {case_id} with {len(entities)} entities.")

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 559103_syn_1
# ==========================================
text_1 = """Indication: Large PTX.
Proc: Chest Tube (28Fr).
Site: [REDACTED]
Result: Air rush, lung re-expanded.
Plan: Admit, suction -20."""

entities_1 = [
    {"label": "OBS_LESION",         **get_span(text_1, "PTX", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_1, "Chest Tube", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "28Fr", 1)},
    {"label": "OBS_FINDING",        **get_span(text_1, "Air rush", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_1, "lung re-expanded", 1)},
    {"label": "MEAS_PRESS",         **get_span(text_1, "-20", 1)}
]
BATCH_DATA.append({"id": "559103_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 559103_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: Tube Thoracostomy.
INDICATION: Primary spontaneous pneumothorax.
PROCEDURE: The right hemithorax was prepped. Local anesthesia was infiltrated. A 28 French chest tube was inserted via blunt dissection at the 5th intercostal space. Significant air release was confirmed. The tube was secured and placed to suction. Post-procedure imaging confirmed lung re-expansion."""

entities_2 = [
    {"label": "PROC_ACTION",       **get_span(text_2, "Tube Thoracostomy", 1)},
    {"label": "OBS_LESION",        **get_span(text_2, "pneumothorax", 1)},
    {"label": "LATERALITY",        **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA",       **get_span(text_2, "hemithorax", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "28 French chest tube", 1)},
    {"label": "PROC_METHOD",       **get_span(text_2, "blunt dissection", 1)},
    {"label": "ANAT_PLEURA",       **get_span(text_2, "5th intercostal space", 1)},
    {"label": "OBS_FINDING",       **get_span(text_2, "air release", 1)},
    {"label": "OUTCOME_PLEURAL",   **get_span(text_2, "lung re-expansion", 1)}
]
BATCH_DATA.append({"id": "559103_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 559103_syn_3
# ==========================================
text_3 = """Code: 32551 (Tube thoracostomy).
Specifics: Open/blunt dissection technique used (not percutaneous/Seldinger). 28Fr tube placed. Connected to suction."""

entities_3 = [
    {"label": "PROC_ACTION",        **get_span(text_3, "Tube thoracostomy", 1)},
    {"label": "PROC_METHOD",        **get_span(text_3, "blunt dissection", 1)},
    {"label": "DEV_CATHETER_SIZE",  **get_span(text_3, "28Fr tube", 1)}
]
BATCH_DATA.append({"id": "559103_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 559103_syn_4
# ==========================================
text_4 = """Procedure: Chest Tube
Patient: [REDACTED]
1. Prep R chest.
2. Lidocaine/Fentanyl.
3. Cut at 5th ICS.
4. Clamp dissection into pleura.
5. Finger sweep.
6. Tube (28Fr) in.
7. Stitch and tape.
8. CXR: Lung up."""

entities_4 = [
    {"label": "DEV_CATHETER",       **get_span(text_4, "Chest Tube", 1)},
    {"label": "LATERALITY",         **get_span(text_4, "R", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_4, "chest", 1)},
    {"label": "MEDICATION",         **get_span(text_4, "Lidocaine", 1)},
    {"label": "MEDICATION",         **get_span(text_4, "Fentanyl", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_4, "5th ICS", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_4, "pleura", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_4, "Tube", 2)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_4, "28Fr", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_4, "Lung up", 1)}
]
BATCH_DATA.append({"id": "559103_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 559103_syn_5
# ==========================================
text_5 = """[REDACTED] spontaneous pneumo right side. pigtail didn't work so put in a real chest tube. 28 french right side 5th intercostal. big rush of air lung came up nicely on the xray. hooked to suction admitting him."""

entities_5 = [
    {"label": "OBS_LESION",         **get_span(text_5, "pneumo", 1)},
    {"label": "LATERALITY",         **get_span(text_5, "right side", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_5, "pigtail", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_5, "chest tube", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_5, "28 french", 1)},
    {"label": "LATERALITY",         **get_span(text_5, "right side", 2)},
    {"label": "ANAT_PLEURA",        **get_span(text_5, "5th intercostal", 1)},
    {"label": "OBS_FINDING",        **get_span(text_5, "rush of air", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_5, "lung came up", 1)}
]
BATCH_DATA.append({"id": "559103_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 559103_syn_6
# ==========================================
text_6 = """Right-sided tube thoracostomy performed for spontaneous pneumothorax. Standard landmark technique utilized. A 28 Fr tube was placed and secured. Connected to -20cmH2O suction with resolution of pneumothorax on imaging."""

entities_6 = [
    {"label": "LATERALITY",        **get_span(text_6, "Right-sided", 1)},
    {"label": "PROC_ACTION",       **get_span(text_6, "tube thoracostomy", 1)},
    {"label": "OBS_LESION",        **get_span(text_6, "pneumothorax", 1)},
    {"label": "PROC_METHOD",       **get_span(text_6, "landmark technique", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "28 Fr tube", 1)},
    {"label": "MEAS_PRESS",        **get_span(text_6, "-20cmH2O", 1)},
    {"label": "OUTCOME_PLEURAL",   **get_span(text_6, "resolution of pneumothorax", 1)}
]
BATCH_DATA.append({"id": "559103_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 559103_syn_7
# ==========================================
text_7 = """[Indication]
Right Pneumothorax.
[Anesthesia]
Local + Moderate analgesia.
[Description]
28Fr Chest Tube placed R 5th ICS. Air evacuated. Lung re-expanded.
[Plan]
Admit. Suction."""

entities_7 = [
    {"label": "LATERALITY",        **get_span(text_7, "Right", 1)},
    {"label": "OBS_LESION",        **get_span(text_7, "Pneumothorax", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "28Fr Chest Tube", 1)},
    {"label": "LATERALITY",        **get_span(text_7, "R", 1)},
    {"label": "ANAT_PLEURA",       **get_span(text_7, "5th ICS", 1)},
    {"label": "OBS_FINDING",       **get_span(text_7, "Air evacuated", 1)},
    {"label": "OUTCOME_PLEURAL",   **get_span(text_7, "Lung re-expanded", 1)}
]
BATCH_DATA.append({"id": "559103_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 559103_syn_8
# ==========================================
text_8 = """We placed a chest tube in [REDACTED] to treat his collapsed lung. We numbed the area and inserted a large tube between the ribs. A lot of air came out, and his breathing improved. The X-ray showed the lung is back up. He is admitted to the hospital."""

entities_8 = [
    {"label": "DEV_CATHETER",     **get_span(text_8, "chest tube", 1)},
    {"label": "OBS_LESION",       **get_span(text_8, "collapsed lung", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_8, "tube", 2)},
    {"label": "OBS_FINDING",      **get_span(text_8, "air came out", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "breathing improved", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_8, "lung is back up", 1)}
]
BATCH_DATA.append({"id": "559103_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 559103_syn_9
# ==========================================
text_9 = """Intervention: Tube thoracostomy.
Indication: Pneumothorax.
Technique: Surgical insertion of pleural drain.
Outcome: Re-expansion of pulmonary parenchyma."""

entities_9 = [
    {"label": "PROC_ACTION",     **get_span(text_9, "Tube thoracostomy", 1)},
    {"label": "OBS_LESION",      **get_span(text_9, "Pneumothorax", 1)},
    {"label": "DEV_CATHETER",    **get_span(text_9, "pleural drain", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_9, "Re-expansion of pulmonary parenchyma", 1)}
]
BATCH_DATA.append({"id": "559103_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 559103 (Original)
# ==========================================
text_10 = """CHEST TUBE INSERTION NOTE
Date: [REDACTED] 03:10
Patient: [REDACTED] | 27M | MRN [REDACTED]
Location: [REDACTED]
Operator: Dr. Rachel O'Connor (Interventional Pulmonology)

INDICATION: Large right spontaneous pneumothorax with dyspnea in otherwise healthy young male; failure of small-bore pigtail catheter placed at outside hospital.

PROCEDURE: Tube thoracostomy, right chest (CPT 32551)

ANESTHESIA: Local 1% lidocaine with epinephrine plus small IV fentanyl boluses (moderate analgesia; no continuous procedural sedation).

PROCEDURE SUMMARY:
Patient [REDACTED] with right arm above head. Landmark-based insertion was performed at the right 5th intercostal space, mid-axillary line. Blunt dissection was used to enter the pleural space.

A 28 Fr chest tube was inserted and directed apically. Immediate rush of air was noted with improvement in breath sounds and oxygen saturation. The tube was secured with heavy silk sutures and connected to -20 cm H2O suction.

Post-procedure portable CXR showed full re-expansion of the right lung without residual large pneumothorax.

COMPLICATIONS: None.
DISPOSITION: Admitted to pulmonary ward for ongoing management."""

entities_10 = [
    {"label": "CTX_TIME",          **get_span(text_10, "03:10", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "pneumothorax", 1)},
    {"label": "OUTCOME_SYMPTOMS",  **get_span(text_10, "dyspnea", 1)},
    {"label": "CTX_HISTORICAL",    **get_span(text_10, "failure of", 1)},
    {"label": "DEV_CATHETER",      **get_span(text_10, "pigtail catheter", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "Tube thoracostomy", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right", 2)},
    {"label": "ANAT_PLEURA",       **get_span(text_10, "chest", 1)},
    {"label": "MEDICATION",        **get_span(text_10, "lidocaine", 1)},
    {"label": "MEDICATION",        **get_span(text_10, "epinephrine", 1)},
    {"label": "MEDICATION",        **get_span(text_10, "fentanyl", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right", 3)},
    {"label": "PROC_METHOD",       **get_span(text_10, "Landmark-based", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right", 4)},
    {"label": "ANAT_PLEURA",       **get_span(text_10, "5th intercostal space", 1)},
    {"label": "PROC_METHOD",       **get_span(text_10, "Blunt dissection", 1)},
    {"label": "ANAT_PLEURA",       **get_span(text_10, "pleural space", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "28 Fr chest tube", 1)},
    {"label": "OBS_FINDING",       **get_span(text_10, "rush of air", 1)},
    {"label": "OUTCOME_SYMPTOMS",  **get_span(text_10, "improvement in breath sounds", 1)},
    {"label": "MEAS_PRESS",        **get_span(text_10, "-20 cm H2O", 1)},
    {"label": "OUTCOME_PLEURAL",   **get_span(text_10, "full re-expansion", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right", 5)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)}
]
BATCH_DATA.append({"id": "559103", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)