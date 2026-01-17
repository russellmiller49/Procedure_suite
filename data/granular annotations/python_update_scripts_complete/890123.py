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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 891234_syn_1
# ------------------------------------------
t1 = """Indication: Organized hemothorax.
Proc: tPA/DNase instillation.
- 10mg tPA / 5mg DNase.
- 2hr dwell.
- Output: 200mL bloody fluid.
- Stable."""
e1 = [
    {"label": "OBS_LESION",   **get_span(t1, "Organized hemothorax", 1)},
    {"label": "MEDICATION",   **get_span(t1, "tPA", 1)},
    {"label": "MEDICATION",   **get_span(t1, "DNase", 1)},
    {"label": "PROC_ACTION",  **get_span(t1, "instillation", 1)},
    {"label": "MEDICATION",   **get_span(t1, "tPA", 2)},
    {"label": "MEDICATION",   **get_span(t1, "DNase", 2)},
    {"label": "MEAS_TIME",    **get_span(t1, "2hr", 1)},
    {"label": "MEAS_VOL",     **get_span(t1, "200mL", 1)},
    {"label": "OBS_FINDING",  **get_span(t1, "bloody fluid", 1)},
]
BATCH_DATA.append({"id": "891234_syn_1", "text": t1, "entities": e1})

# ------------------------------------------
# Case 2: 891234_syn_2
# ------------------------------------------
t2 = """PROCEDURE REPORT: Intrapleural fibrinolytic therapy for organized hemothorax.
CLINICAL CONTEXT: 54-year-old male post-trauma with retained hemothorax.
INTERVENTION: To facilitate drainage of the organized collection, sequential instillation of alteplase (10 mg) and dornase alfa (5 mg) was performed via the chest tube. Following a two-hour clamp period, suction was reapplied, yielding 200 mL of dark sanguineous fluid."""
e2 = [
    {"label": "ANAT_PLEURA",  **get_span(t2, "Intrapleural", 1)},
    {"label": "PROC_ACTION",  **get_span(t2, "fibrinolytic therapy", 1)},
    {"label": "OBS_LESION",   **get_span(t2, "organized hemothorax", 1)},
    {"label": "OBS_LESION",   **get_span(t2, "retained hemothorax", 1)},
    {"label": "OBS_LESION",   **get_span(t2, "organized collection", 1)},
    {"label": "PROC_ACTION",  **get_span(t2, "instillation", 1)},
    {"label": "MEDICATION",   **get_span(t2, "alteplase", 1)},
    {"label": "MEDICATION",   **get_span(t2, "dornase alfa", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest tube", 1)},
    {"label": "MEAS_TIME",    **get_span(t2, "two-hour", 1)},
    {"label": "MEAS_VOL",     **get_span(t2, "200 mL", 1)},
    {"label": "OBS_FINDING",  **get_span(t2, "dark sanguineous fluid", 1)},
]
BATCH_DATA.append({"id": "891234_syn_2", "text": t2, "entities": e2})

# ------------------------------------------
# Case 3: 891234_syn_3
# ------------------------------------------
t3 = """Code 32561: Instillation of fibrinolytic agent.
Agents: Alteplase 10mg, Dornase 5mg.
Site: [REDACTED]
Indication: Retained hemothorax (Traumatic).
Output: 200mL post-instillation."""
e3 = [
    {"label": "PROC_ACTION",  **get_span(t3, "Instillation", 1)},
    {"label": "MEDICATION",   **get_span(t3, "Alteplase", 1)},
    {"label": "MEDICATION",   **get_span(t3, "Dornase", 1)},
    {"label": "OBS_LESION",   **get_span(t3, "Retained hemothorax", 1)},
    {"label": "MEAS_VOL",     **get_span(t3, "200mL", 1)},
]
BATCH_DATA.append({"id": "891234_syn_3", "text": t3, "entities": e3})

# ------------------------------------------
# Case 4: 891234_syn_4
# ------------------------------------------
t4 = """Procedure: Lytic Instillation
Indication: Hemothorax
Steps:
1. Flushed tube.
2. Instilled tPA then DNase.
3. Clamped 2 hours.
4. Suction -20cmH2O.
Output 200mL. Patient stable."""
e4 = [
    {"label": "PROC_ACTION",  **get_span(t4, "Instillation", 1)},
    {"label": "OBS_LESION",   **get_span(t4, "Hemothorax", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "tube", 1)},
    {"label": "PROC_ACTION",  **get_span(t4, "Instilled", 1)},
    {"label": "MEDICATION",   **get_span(t4, "tPA", 1)},
    {"label": "MEDICATION",   **get_span(t4, "DNase", 1)},
    {"label": "MEAS_TIME",    **get_span(t4, "2 hours", 1)},
    {"label": "MEAS_PRESS",   **get_span(t4, "-20cmH2O", 1)},
    {"label": "MEAS_VOL",     **get_span(t4, "200mL", 1)},
]
BATCH_DATA.append({"id": "891234_syn_4", "text": t4, "entities": e4})

# ------------------------------------------
# Case 5: 891234_syn_5
# ------------------------------------------
t5 = """Trauma patient with the stuck hemothorax we did the lytics tpa dnase put it in clamped for two hours got out about 200 cc dark blood patient is fine sats good on 2L plan for bid dosing."""
e5 = [
    {"label": "OBS_LESION",   **get_span(t5, "hemothorax", 1)},
    {"label": "MEDICATION",   **get_span(t5, "tpa", 1)},
    {"label": "MEDICATION",   **get_span(t5, "dnase", 1)},
    {"label": "MEAS_TIME",    **get_span(t5, "two hours", 1)},
    {"label": "MEAS_VOL",     **get_span(t5, "200 cc", 1)},
    {"label": "OBS_FINDING",  **get_span(t5, "dark blood", 1)},
]
BATCH_DATA.append({"id": "891234_syn_5", "text": t5, "entities": e5})

# ------------------------------------------
# Case 6: 891234_syn_6
# ------------------------------------------
t6 = """Intrapleural fibrinolytic administration Day 1. Organized hemothorax post-trauma. Confirmed tube patency. Instilled Alteplase 10mg and Dornase alfa 5mg. Sequential instillation. Catheter clamped for 2 hours total dwell. Opened to -20cmH2O suction. Immediate output 200mL dark bloody fluid. Patient hemodynamically stable."""
e6 = [
    {"label": "ANAT_PLEURA",  **get_span(t6, "Intrapleural", 1)},
    {"label": "PROC_ACTION",  **get_span(t6, "fibrinolytic administration", 1)},
    {"label": "OBS_LESION",   **get_span(t6, "Organized hemothorax", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "tube", 1)},
    {"label": "PROC_ACTION",  **get_span(t6, "Instilled", 1)},
    {"label": "MEDICATION",   **get_span(t6, "Alteplase", 1)},
    {"label": "MEDICATION",   **get_span(t6, "Dornase alfa", 1)},
    {"label": "PROC_ACTION",  **get_span(t6, "instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "Catheter", 1)},
    {"label": "MEAS_TIME",    **get_span(t6, "2 hours", 1)},
    {"label": "MEAS_PRESS",   **get_span(t6, "-20cmH2O", 1)},
    {"label": "MEAS_VOL",     **get_span(t6, "200mL", 1)},
    {"label": "OBS_FINDING",  **get_span(t6, "dark bloody fluid", 1)},
]
BATCH_DATA.append({"id": "891234_syn_6", "text": t6, "entities": e6})

# ------------------------------------------
# Case 7: 891234_syn_7
# ------------------------------------------
t7 = """[Indication]
Organized traumatic hemothorax.
[Anesthesia]
None.
[Description]
Instilled tPA 10mg/DNase 5mg via chest tube. 2 hour dwell. 200mL output.
[Plan]
BID dosing x 3 days."""
e7 = [
    {"label": "OBS_LESION",   **get_span(t7, "Organized traumatic hemothorax", 1)},
    {"label": "PROC_ACTION",  **get_span(t7, "Instilled", 1)},
    {"label": "MEDICATION",   **get_span(t7, "tPA", 1)},
    {"label": "MEDICATION",   **get_span(t7, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "chest tube", 1)},
    {"label": "MEAS_TIME",    **get_span(t7, "2 hour", 1)},
    {"label": "MEAS_VOL",     **get_span(t7, "200mL", 1)},
]
BATCH_DATA.append({"id": "891234_syn_7", "text": t7, "entities": e7})

# ------------------------------------------
# Case 8: 891234_syn_8
# ------------------------------------------
t8 = """Mr. O'Brien is dealing with a retained hemothorax from his car accident. To help clear the blood clots, we administered tPA and DNase through his chest tube today. We let the medication sit for two hours before turning the suction back on. This resulted in the drainage of 200mL of dark, bloody fluid, indicating it's breaking up the clot."""
e8 = [
    {"label": "OBS_LESION",   **get_span(t8, "retained hemothorax", 1)},
    {"label": "MEDICATION",   **get_span(t8, "tPA", 1)},
    {"label": "MEDICATION",   **get_span(t8, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
    {"label": "MEAS_TIME",    **get_span(t8, "two hours", 1)},
    {"label": "MEAS_VOL",     **get_span(t8, "200mL", 1)},
    {"label": "OBS_FINDING",  **get_span(t8, "dark, bloody fluid", 1)},
]
BATCH_DATA.append({"id": "891234_syn_8", "text": t8, "entities": e8})

# ------------------------------------------
# Case 9: 891234_syn_9
# ------------------------------------------
t9 = """Indication: Retained blood collection.
Action: Injected fibrinolytic agents via pleural drain.
Details: 10mg alteplase and 5mg dornase alfa administered. Drain closed for 2 hours. Re-opened to suction, yielding 200mL bloody output. Vitals stable."""
e9 = [
    {"label": "OBS_LESION",   **get_span(t9, "Retained blood collection", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "pleural drain", 1)},
    {"label": "MEDICATION",   **get_span(t9, "alteplase", 1)},
    {"label": "MEDICATION",   **get_span(t9, "dornase alfa", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "Drain", 1)},
    {"label": "MEAS_TIME",    **get_span(t9, "2 hours", 1)},
    {"label": "MEAS_VOL",     **get_span(t9, "200mL", 1)},
    {"label": "OBS_FINDING",  **get_span(t9, "bloody", 1)},
]
BATCH_DATA.append({"id": "891234_syn_9", "text": t9, "entities": e9})

# ------------------------------------------
# Case 10: 891234 (Original)
# ------------------------------------------
t10 = """PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Location: [REDACTED]
Physician: Dr. Amanda Foster, Interventional Pulmonology
Fellow: Dr. Kevin Park, PGY-5

Indication: Organized hemothorax post-trauma, inadequate drainage

Background: 54M s/p MVC with traumatic hemothorax. Chest tube placed at OSH 5 days ago. Transfer for IP evaluation due to persistent opacity. CT shows organized hemothorax with extensive fibrin stranding.

Procedure: Intrapleural fibrinolytic administration - Day 1
After confirming tube patency with 20mL saline flush, we instilled:
- Alteplase (tPA) 10mg in 30mL NS
- Dornase alfa (DNase) 5mg in 30mL NS
Sequential instillation with 30-minute interval.
Catheter clamped for 2 hours total dwell.
Opened to -20cmH2O suction.

Immediate output: 200mL dark bloody fluid within first hour.
Patient [REDACTED]. O2 sat 96% on 2L NC.

Plan: BID dosing x 3 days, then reassess with CT.

A. Foster, MD / K. Park, MD"""
e10 = [
    {"label": "OBS_LESION",   **get_span(t10, "Organized hemothorax", 1)},
    {"label": "OBS_LESION",   **get_span(t10, "traumatic hemothorax", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 1)},
    {"label": "OBS_LESION",   **get_span(t10, "organized hemothorax", 1)},
    {"label": "OBS_FINDING",  **get_span(t10, "fibrin stranding", 1)},
    {"label": "ANAT_PLEURA",  **get_span(t10, "Intrapleural", 1)},
    {"label": "PROC_ACTION",  **get_span(t10, "fibrinolytic administration", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "tube", 1)},
    {"label": "PROC_ACTION",  **get_span(t10, "instilled", 1)},
    {"label": "MEDICATION",   **get_span(t10, "Alteplase", 1)},
    {"label": "MEDICATION",   **get_span(t10, "tPA", 1)},
    {"label": "MEDICATION",   **get_span(t10, "Dornase alfa", 1)},
    {"label": "MEDICATION",   **get_span(t10, "DNase", 1)},
    {"label": "PROC_ACTION",  **get_span(t10, "instillation", 1)},
    {"label": "MEAS_TIME",    **get_span(t10, "30-minute", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Catheter", 1)},
    {"label": "MEAS_TIME",    **get_span(t10, "2 hours", 1)},
    {"label": "MEAS_PRESS",   **get_span(t10, "-20cmH2O", 1)},
    {"label": "MEAS_VOL",     **get_span(t10, "200mL", 1)},
    {"label": "OBS_FINDING",  **get_span(t10, "dark bloody fluid", 1)},
]
BATCH_DATA.append({"id": "891234", "text": t10, "entities": e10})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)