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
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Raises ValueError if the term is not found the specified number of times.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# 3. Data Definitions (Batch)
# ==========================================

# ------------------------------------------
# Note 1: 234567_syn_1
# ------------------------------------------
t1 = """Indication: Recurrent L effusion (Hepatic hydrothorax).
Proc: Thoracentesis w/ catheter.
- 12Fr pigtail.
- No imaging.
- Drained 2100mL clear yellow.
- Catheter removed."""

e1 = [
    {"label": "LATERALITY",          **get_span(t1, "L", 1)},
    {"label": "OBS_FINDING",         **get_span(t1, "effusion", 1)},
    {"label": "OBS_FINDING",         **get_span(t1, "Hepatic hydrothorax", 1)},
    {"label": "PROC_ACTION",         **get_span(t1, "Thoracentesis", 1)},
    {"label": "DEV_CATHETER",        **get_span(t1, "catheter", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t1, "12Fr pigtail", 1)},
    {"label": "MEAS_VOL",            **get_span(t1, "2100mL", 1)},
    {"label": "OBS_FINDING",         **get_span(t1, "clear yellow", 1)},
    {"label": "DEV_CATHETER",        **get_span(t1, "Catheter", 1)}, # Case sensitive: 'Catheter'
]
BATCH_DATA.append({"id": "234567_syn_1", "text": t1, "entities": e1})


# ------------------------------------------
# Note 2: 234567_syn_2
# ------------------------------------------
t2 = """PROCEDURE NOTE: Large volume thoracentesis via catheter.
INDICATION: Recurrent hepatic hydrothorax causing dyspnea.
DETAILS: Without imaging guidance, a 12Fr pigtail catheter was introduced into the left pleural space. Approximately 2.1 liters of transudative fluid were evacuated. The procedure was terminated due to patient cough, and the catheter was removed."""

e2 = [
    {"label": "PROC_ACTION",         **get_span(t2, "thoracentesis", 1)},
    {"label": "DEV_CATHETER",        **get_span(t2, "catheter", 1)},
    {"label": "OBS_FINDING",         **get_span(t2, "hepatic hydrothorax", 1)},
    {"label": "OBS_FINDING",         **get_span(t2, "dyspnea", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t2, "12Fr pigtail catheter", 1)},
    {"label": "LATERALITY",          **get_span(t2, "left", 1)},
    {"label": "ANAT_PLEURA",         **get_span(t2, "pleural space", 1)},
    {"label": "MEAS_VOL",            **get_span(t2, "2.1 liters", 1)},
    {"label": "OBS_FINDING",         **get_span(t2, "transudative", 1)},
    {"label": "SPECIMEN",            **get_span(t2, "fluid", 1)},
    {"label": "PROC_ACTION",         **get_span(t2, "evacuated", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "cough", 1)},
    {"label": "DEV_CATHETER",        **get_span(t2, "catheter", 3)}, # 1st: via catheter, 2nd: pigtail catheter, 3rd: catheter was removed
]
BATCH_DATA.append({"id": "234567_syn_2", "text": t2, "entities": e2})


# ------------------------------------------
# Note 3: 234567_syn_3
# ------------------------------------------
t3 = """CPT 32556: Pleural drainage via indwelling catheter.
Note: Catheter removed at end of case (still 32556 per CPT definition if catheter used for drainage).
Volume: 2100mL.
Guidance: None."""

e3 = [
    {"label": "PROC_ACTION",         **get_span(t3, "Pleural drainage", 1)},
    {"label": "DEV_CATHETER",        **get_span(t3, "indwelling catheter", 1)},
    {"label": "DEV_CATHETER",        **get_span(t3, "Catheter", 1)},
    {"label": "DEV_CATHETER",        **get_span(t3, "catheter", 2)}, # FIXED: occurrence 3 -> 2 (lowercase 'catheter' appears twice)
    {"label": "MEAS_VOL",            **get_span(t3, "2100mL", 1)},
]
BATCH_DATA.append({"id": "234567_syn_3", "text": t3, "entities": e3})


# ------------------------------------------
# Note 4: 234567_syn_4
# ------------------------------------------
t4 = """Procedure: Thoracentesis
1. Landmark guidance.
2. 12Fr pigtail inserted.
3. Drained 2100mL.
4. Pulled catheter.
Breathing improved."""

e4 = [
    {"label": "PROC_ACTION",         **get_span(t4, "Thoracentesis", 1)},
    {"label": "PROC_METHOD",         **get_span(t4, "Landmark guidance", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t4, "12Fr pigtail", 1)},
    {"label": "MEAS_VOL",            **get_span(t4, "2100mL", 1)},
    {"label": "DEV_CATHETER",        **get_span(t4, "catheter", 1)},
    {"label": "OUTCOME_SYMPTOMS",    **get_span(t4, "Breathing improved", 1)},
]
BATCH_DATA.append({"id": "234567_syn_4", "text": t4, "entities": e4})


# ------------------------------------------
# Note 5: 234567_syn_5
# ------------------------------------------
t5 = """Dorothy Williams recurrent hydrothorax drained it again today put in a 12fr pigtail got out 2.1 liters she started coughing so we stopped pulled the tube fluid clear."""

e5 = [
    {"label": "OBS_FINDING",         **get_span(t5, "hydrothorax", 1)},
    {"label": "PROC_ACTION",         **get_span(t5, "drained", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t5, "12fr pigtail", 1)},
    {"label": "MEAS_VOL",            **get_span(t5, "2.1 liters", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "coughing", 1)},
    {"label": "DEV_CATHETER",        **get_span(t5, "tube", 1)},
    {"label": "SPECIMEN",            **get_span(t5, "fluid", 1)},
    {"label": "OBS_FINDING",         **get_span(t5, "clear", 1)},
]
BATCH_DATA.append({"id": "234567_syn_5", "text": t5, "entities": e5})


# ------------------------------------------
# Note 6: 234567_syn_6
# ------------------------------------------
t6 = """Thoracentesis with catheter aspiration. 78F with CHF and cirrhosis presenting with recurrent left pleural effusion. Using Seldinger technique without imaging guidance 12Fr pigtail catheter inserted into pleural space. Total of 2100mL drained over 45 minutes. Catheter removed. Post-procedure SpO2 96% on RA."""

e6 = [
    {"label": "PROC_ACTION",         **get_span(t6, "Thoracentesis", 1)},
    {"label": "PROC_ACTION",         **get_span(t6, "catheter aspiration", 1)},
    {"label": "OBS_FINDING",         **get_span(t6, "CHF", 1)},
    {"label": "LATERALITY",          **get_span(t6, "left", 1)},
    {"label": "OBS_FINDING",         **get_span(t6, "pleural effusion", 1)},
    {"label": "PROC_METHOD",         **get_span(t6, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t6, "12Fr pigtail catheter", 1)},
    {"label": "ANAT_PLEURA",         **get_span(t6, "pleural space", 1)},
    {"label": "MEAS_VOL",            **get_span(t6, "2100mL", 1)},
    {"label": "CTX_TIME",            **get_span(t6, "45 minutes", 1)},
    {"label": "DEV_CATHETER",        **get_span(t6, "Catheter", 1)},
]
BATCH_DATA.append({"id": "234567_syn_6", "text": t6, "entities": e6})


# ------------------------------------------
# Note 7: 234567_syn_7
# ------------------------------------------
t7 = """[Indication]
Recurrent L hepatic hydrothorax.
[Anesthesia]
Local.
[Description]
12Fr pigtail placed. Drained 2100mL. Removed.
[Plan]
Discharge."""

e7 = [
    {"label": "LATERALITY",          **get_span(t7, "L", 1)},
    {"label": "OBS_FINDING",         **get_span(t7, "hepatic hydrothorax", 1)},
    {"label": "MEDICATION",          **get_span(t7, "Local", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t7, "12Fr pigtail", 1)},
    {"label": "PROC_ACTION",         **get_span(t7, "Drained", 1)},
    {"label": "MEAS_VOL",            **get_span(t7, "2100mL", 1)},
]
BATCH_DATA.append({"id": "234567_syn_7", "text": t7, "entities": e7})


# ------------------------------------------
# Note 8: 234567_syn_8
# ------------------------------------------
t8 = """[REDACTED] fluid buildup due to her liver condition. She needed another drainage today. We inserted a small pigtail catheter into her left chest and drained over 2 liters of fluid. We removed the catheter right after the procedure. She felt much better afterward."""

e8 = [
    {"label": "OBS_FINDING",         **get_span(t8, "fluid buildup", 1)},
    {"label": "PROC_ACTION",         **get_span(t8, "drainage", 1)},
    {"label": "DEV_CATHETER",        **get_span(t8, "pigtail catheter", 1)},
    {"label": "LATERALITY",          **get_span(t8, "left", 1)},
    {"label": "ANAT_PLEURA",         **get_span(t8, "chest", 1)},
    {"label": "PROC_ACTION",         **get_span(t8, "drained", 1)},
    {"label": "MEAS_VOL",            **get_span(t8, "2 liters", 1)},
    {"label": "SPECIMEN",            **get_span(t8, "fluid", 2)}, # "of fluid"
    {"label": "DEV_CATHETER",        **get_span(t8, "catheter", 2)}, # 1: pigtail catheter, 2: removed the catheter
    {"label": "OUTCOME_SYMPTOMS",    **get_span(t8, "felt much better", 1)},
]
BATCH_DATA.append({"id": "234567_syn_8", "text": t8, "entities": e8})


# ------------------------------------------
# Note 9: 234567_syn_9
# ------------------------------------------
t9 = """Diagnosis: Hepatic hydrothorax.
Action: Catheter drainage of pleural fluid.
Details: 12Fr catheter inserted. 2100mL evacuated. Catheter removed."""

e9 = [
    {"label": "OBS_FINDING",         **get_span(t9, "Hepatic hydrothorax", 1)},
    {"label": "DEV_CATHETER",        **get_span(t9, "Catheter", 1)},
    {"label": "PROC_ACTION",         **get_span(t9, "drainage", 1)},
    {"label": "SPECIMEN",            **get_span(t9, "pleural fluid", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t9, "12Fr catheter", 1)},
    {"label": "MEAS_VOL",            **get_span(t9, "2100mL", 1)},
    {"label": "DEV_CATHETER",        **get_span(t9, "Catheter", 2)}, # 2nd occurrence
]
BATCH_DATA.append({"id": "234567_syn_9", "text": t9, "entities": e9})


# ------------------------------------------
# Note 10: 234567 (Original)
# ------------------------------------------
t10 = """PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (78 years old)
Date: [REDACTED]
Location: [REDACTED]

Attending: Dr. Robert Kim, MD - Pulmonary/Critical Care
Resident: Dr. Emily Chen, MD - PGY-3

Indication: Recurrent large left pleural effusion, CHF with hepatic hydrothorax

Procedure: Thoracentesis with catheter aspiration

Details:
78F with CHF and cirrhosis presenting with recurrent left pleural effusion causing dyspnea. This is her 4th thoracentesis in 3 months. Not a candidate for TIPS.

Patient [REDACTED]. Left posterolateral chest, 7th ICS id[REDACTED]. Sterile prep and drape. Local anesthesia with 10mL 1% lidocaine.

Using Seldinger technique without imaging guidance, 12Fr pigtail catheter inserted into pleural space. Immediate return of transudative-appearing clear yellow fluid. Total of 2100mL drained over 45 minutes. Patient asked to stop due to chest tightness and cough.

Post-procedure SpO2 96% on RA (baseline 91% on 2L). Marked improvement in dyspnea. CXR shows lung re-expansion, no pneumothorax.

Fluid: Transudate per Light's criteria.

Plan: Discuss IPC placement at next recurrence.

R. Kim, MD / E. Chen, MD"""

e10 = [
    {"label": "LATERALITY",          **get_span(t10, "left", 1)},
    {"label": "OBS_FINDING",         **get_span(t10, "pleural effusion", 1)},
    {"label": "OBS_FINDING",         **get_span(t10, "CHF", 1)},
    {"label": "OBS_FINDING",         **get_span(t10, "hepatic hydrothorax", 1)},
    {"label": "PROC_ACTION",         **get_span(t10, "Thoracentesis", 1)},
    {"label": "PROC_ACTION",         **get_span(t10, "catheter aspiration", 1)},
    {"label": "OBS_FINDING",         **get_span(t10, "CHF", 2)},
    {"label": "LATERALITY",          **get_span(t10, "left", 2)},
    {"label": "OBS_FINDING",         **get_span(t10, "pleural effusion", 2)},
    {"label": "OBS_FINDING",         **get_span(t10, "dyspnea", 1)},
    {"label": "PROC_ACTION",         **get_span(t10, "thoracentesis", 1)}, # FIXED: occurrence 2 -> 1 (lowercase 'thoracentesis' only appears once)
    {"label": "LATERALITY",          **get_span(t10, "Left", 1)}, # Capitalized "Left posterolateral..."
    {"label": "ANAT_PLEURA",         **get_span(t10, "chest", 1)},
    {"label": "MEDICATION",          **get_span(t10, "lidocaine", 1)},
    {"label": "PROC_METHOD",         **get_span(t10, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER_SIZE",   **get_span(t10, "12Fr pigtail catheter", 1)},
    {"label": "ANAT_PLEURA",         **get_span(t10, "pleural space", 1)},
    {"label": "OBS_FINDING",         **get_span(t10, "transudative", 1)},
    {"label": "OBS_FINDING",         **get_span(t10, "clear yellow", 1)},
    {"label": "SPECIMEN",            **get_span(t10, "fluid", 1)},
    {"label": "MEAS_VOL",            **get_span(t10, "2100mL", 1)},
    {"label": "CTX_TIME",            **get_span(t10, "45 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "chest tightness", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "cough", 1)},
    {"label": "OUTCOME_SYMPTOMS",    **get_span(t10, "Marked improvement in dyspnea", 1)},
    {"label": "OUTCOME_PLEURAL",     **get_span(t10, "lung re-expansion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no pneumothorax", 1)},
    {"label": "OBS_FINDING",         **get_span(t10, "Transudate", 1)},
]
BATCH_DATA.append({"id": "234567", "text": t10, "entities": e10})


# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)