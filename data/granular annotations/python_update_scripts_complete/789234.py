import sys
from pathlib import Path

# 1. Dynamic Repo Root Setup
# -------------------------------------------------------------------------
# Assumes this script is run from inside the repository structure.
# We look for a marker (like 'scripts' or '.git') to find the root.
# -------------------------------------------------------------------------
current_dir = Path(__file__).resolve().parent
REPO_ROOT = current_dir
for parent in current_dir.parents:
    if (parent / "scripts").exists() or (parent / ".git").exists():
        REPO_ROOT = parent
        break

sys.path.append(str(REPO_ROOT))

# 2. Import Utility
# -------------------------------------------------------------------------
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Could not import 'add_case'. Ensure you are running from the repo root.")
    sys.exit(1)

# 3. Helper Function
# -------------------------------------------------------------------------
def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start, "end": start + len(term)}

# 4. Batch Data Definition
# -------------------------------------------------------------------------
BATCH_DATA = []

# -------------------------------------------------------------------------
# Case 1: 789234_syn_1
# -------------------------------------------------------------------------
id_1 = "789234_syn_1"
text_1 = """Dx: R complex parapneumonic effusion.
Rx: Intrapleural fibrinolysis Day 1.
- 14Fr chest tube in situ.
- Instilled 10mg tPA / 5mg DNase in 50mL NS.
- Clamp 2h -> Open to drain.
- No pain/distress."""

entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "parapneumonic effusion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_1, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_1, "DNase", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "50mL", 1)},
    {"label": "MEDICATION", **get_span(text_1, "NS", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "2h", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_1, "No pain/distress", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# -------------------------------------------------------------------------
# Case 2: 789234_syn_2
# -------------------------------------------------------------------------
id_2 = "789234_syn_2"
text_2 = """CLINICAL SUMMARY: This 67-year-old female with a right-sided loculated parapneumonic effusion required intervention. The indwelling pleural catheter exhibited poor drainage secondary to loculations.
INTERVENTION: Therapeutic instillation of fibrinolytic agents. Under sterile conditions, tissue plasminogen activator (10 mg) and dornase alfa (5 mg) were administered into the pleural space via the existing catheter. The device was clamped for a dwell time of 120 minutes to facilitate fibrinolysis, then opened to gravity drainage. The patient tolerated the procedure without adverse hemodynamic sequelae."""

entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "right-sided", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "parapneumonic effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "indwelling pleural catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "loculations", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "instillation", 1)},
    {"label": "MEDICATION", **get_span(text_2, "tissue plasminogen activator", 1)},
    {"label": "MEDICATION", **get_span(text_2, "dornase alfa", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 2)},  # 'existing catheter'
    {"label": "MEAS_TIME", **get_span(text_2, "120 minutes", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# -------------------------------------------------------------------------
# Case 3: 789234_syn_3
# -------------------------------------------------------------------------
id_3 = "789234_syn_3"
text_3 = """Procedure: Instillation of fibrinolytic agent (CPT 32561).
Device: Indwelling pleural catheter (Right).
Agents: tPA 10mg + DNase 5mg.
Technique: Sterile prep, injection of agents, 2-hour clamp time.
Medical Necessity: To break down loculations in complex parapneumonic effusion."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Indwelling pleural catheter", 1)},
    {"label": "LATERALITY", **get_span(text_3, "Right", 1)},
    {"label": "MEDICATION", **get_span(text_3, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_3, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "injection", 1)},
    {"label": "MEAS_TIME", **get_span(text_3, "2-hour", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "loculations", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "parapneumonic effusion", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# -------------------------------------------------------------------------
# Case 4: 789234_syn_4
# -------------------------------------------------------------------------
id_4 = "789234_syn_4"
text_4 = """Procedure Note: Fibrinolytic Instillation
Indication: Loculated effusion
Steps:
1. Sterile prep of catheter hub.
2. Flush with NS.
3. Instilled tPA 10mg/DNase 5mg.
4. Clamped x 2 hours.
5. Unclamped.
Patient [REDACTED]."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Instillation", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "catheter", 1)},
    {"label": "MEDICATION", **get_span(text_4, "NS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_4, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_4, "DNase", 1)},
    {"label": "MEAS_TIME", **get_span(text_4, "2 hours", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# -------------------------------------------------------------------------
# Case 5: 789234_syn_5
# -------------------------------------------------------------------------
id_5 = "789234_syn_5"
text_5 = """pt [REDACTED] effusion right side we did the tpa dnase instillation today tube was flushed 10 tpa 5 dnase went in fine clamped it for two hours then opened it up no issues draining better now plan for bid dosing."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right side", 1)},
    {"label": "MEDICATION", **get_span(text_5, "tpa", 1)},
    {"label": "MEDICATION", **get_span(text_5, "dnase", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "tube", 1)},
    {"label": "MEDICATION", **get_span(text_5, "tpa", 2)},
    {"label": "MEDICATION", **get_span(text_5, "dnase", 2)},
    {"label": "MEAS_TIME", **get_span(text_5, "two hours", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_5, "draining better", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# -------------------------------------------------------------------------
# Case 6: 789234_syn_6
# -------------------------------------------------------------------------
id_6 = "789234_syn_6"
text_6 = """Right-sided complex parapneumonic effusion with loculations requiring fibrinolysis. 10mg tPA and 5mg DNase mixed in 50mL NS instilled via existing pleural catheter under sterile technique. The catheter was clamped for 2 hours and then returned to drainage. Patient tolerated the procedure well with no chest pain or distress. Plan to continue BID dosing for 3 days."""

entities_6 = [
    {"label": "LATERALITY", **get_span(text_6, "Right-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "parapneumonic effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "loculations", 1)},
    {"label": "MEDICATION", **get_span(text_6, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_6, "DNase", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "50mL", 1)},
    {"label": "MEDICATION", **get_span(text_6, "NS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "instilled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "pleural catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 2)},
    {"label": "MEAS_TIME", **get_span(text_6, "2 hours", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_6, "no chest pain or distress", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# -------------------------------------------------------------------------
# Case 7: 789234_syn_7
# -------------------------------------------------------------------------
id_7 = "789234_syn_7"
text_7 = """[Indication]
Right complex parapneumonic effusion with loculations.
[Anesthesia]
None (Local catheter access).
[Description]
Instilled 10mg tPA and 5mg DNase via 14Fr chest tube. Dwell time 2 hours.
[Plan]
BID dosing x 6 doses."""

entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "parapneumonic effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "loculations", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_7, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_7, "DNase", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "chest tube", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "2 hours", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# -------------------------------------------------------------------------
# Case 8: 789234_syn_8
# -------------------------------------------------------------------------
id_8 = "789234_syn_8"
text_8 = """[REDACTED] a 67-year-old female suffering from a right-sided pneumonia that has developed into a complex, loculated effusion. Today, we proceeded with the first day of intrapleural fibrinolytic therapy. Using her existing 14Fr chest tube, we instilled a mixture of 10mg tPA and 5mg DNase. We clamped the tube for two hours to allow the medication to work, then opened it back up for drainage. She handled it very well."""

entities_8 = [
    {"label": "LATERALITY", **get_span(text_8, "right-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "pneumonia", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "effusion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_8, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "instilled", 1)},
    {"label": "MEDICATION", **get_span(text_8, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_8, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "tube", 2)}, # 'clamped the tube'
    {"label": "MEAS_TIME", **get_span(text_8, "two hours", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# -------------------------------------------------------------------------
# Case 9: 789234_syn_9
# -------------------------------------------------------------------------
id_9 = "789234_syn_9"
text_9 = """Diagnosis: Right-sided complex parapneumonic collection.
Action: Administered fibrinolytic therapy via pleural catheter - Day 1.
Details: 10mg alteplase and 5mg dornase alfa were injected via the existing tube. The tube was occluded for 2 hours, then released for output. No discomfort noted."""

entities_9 = [
    {"label": "LATERALITY", **get_span(text_9, "Right-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "parapneumonic collection", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "pleural catheter", 1)},
    {"label": "MEDICATION", **get_span(text_9, "alteplase", 1)},
    {"label": "MEDICATION", **get_span(text_9, "dornase alfa", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "injected", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "tube", 1)}, # 'existing tube'
    {"label": "DEV_CATHETER", **get_span(text_9, "tube", 2)}, # 'tube was occluded'
    {"label": "MEAS_TIME", **get_span(text_9, "2 hours", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_9, "No discomfort", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# -------------------------------------------------------------------------
# Case 10: 789234
# -------------------------------------------------------------------------
id_10 = "789234"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. James Rodriguez

Dx: Right-sided complex parapneumonic effusion with loculations
Procedure: Intrapleural fibrinolytic instillation via indwelling pleural catheter - Day 1

Hx: 67F with right-sided pneumonia complicated by loculated parapneumonic effusion. 14Fr chest tube placed [REDACTED], draining poorly with persistent loculations on CT. Decision made to initiate intrapleural fibrinolytic therapy.

Procedure: Under sterile technique, 10mg tPA and 5mg DNase mixed in 50mL NS instilled via existing pleural catheter. Catheter clamped for 2 hours, then opened to drainage. Patient tolerated well. No chest pain, no respiratory distress.

Plan: Continue tPA/DNase BID x 3 days. Repeat imaging in 48hrs. Monitor drainage output.

J. Rodriguez MD"""

entities_10 = [
    {"label": "LATERALITY", **get_span(text_10, "Right-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "parapneumonic effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "loculations", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "indwelling pleural catheter", 1)},
    # ERROR FIX: 'right-sided' only appears once as lowercase (the other is Title Case 'Right-sided'). Changed occurrence to 1.
    {"label": "LATERALITY", **get_span(text_10, "right-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pneumonia", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "parapneumonic effusion", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "loculations", 2)},
    {"label": "MEDICATION", **get_span(text_10, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_10, "DNase", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "50mL", 1)},
    {"label": "MEDICATION", **get_span(text_10, "NS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "instilled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "pleural catheter", 2)}, # 'existing pleural catheter'
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "2 hours", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "No chest pain", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "no respiratory distress", 1)},
    {"label": "MEDICATION", **get_span(text_10, "tPA", 2)},
    {"label": "MEDICATION", **get_span(text_10, "DNase", 2)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})


# 5. Execution Loop
# -------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)