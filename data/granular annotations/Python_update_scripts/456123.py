import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from a subdirectory, we look two levels up
REPO_ROOT = Path(__file__).resolve().parent.parent

# Append the repository root to sys.path to enable imports
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==============================================================================
# BATCH: 456123.json (Pleural Instillation / Empyema)
# ==============================================================================

# --- 456123_syn_1 ---
t_456123_1 = """Indication: Empyema, multiloculated.
Procedure: tPA/DNase instillation Day 1.
- Cath flushed.
- 10mg tPA / 5mg DNase instilled.
- 2hr dwell.
- Unclamped to water seal."""
e_456123_1 = [
    {"label": "OBS_LESION", **get_span(t_456123_1, "Empyema", 1)},
    {"label": "OBS_FINDING", **get_span(t_456123_1, "multiloculated", 1)},
    {"label": "MEDICATION", **get_span(t_456123_1, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t_456123_1, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_1, "instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_1, "Cath", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_1, "flushed", 1)},
    {"label": "MEDICATION", **get_span(t_456123_1, "tPA", 2)},
    {"label": "MEDICATION", **get_span(t_456123_1, "DNase", 2)},
    {"label": "PROC_ACTION", **get_span(t_456123_1, "instilled", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_1, "2hr", 1)},
]
BATCH_DATA.append({"id": "456123_syn_1", "text": t_456123_1, "entities": e_456123_1})

# --- 456123_syn_2 ---
t_456123_2 = """PROCEDURE NOTE: Intrapleural administration of fibrinolytic agents.
INDICATION: A 76-year-old male with a multiloculated empyema post-pneumonia.
DESCRIPTION: The indwelling pigtail catheter was prepped. A solution containing 10 mg of tissue plasminogen activator and 5 mg of dornase alfa was instilled into the pleural cavity. The catheter was clamped for a dwell period of two hours to maximize therapeutic effect before being unclamped to water seal drainage."""
e_456123_2 = [
    {"label": "ANAT_PLEURA", **get_span(t_456123_2, "Intrapleural", 1)},
    {"label": "MEDICATION", **get_span(t_456123_2, "fibrinolytic agents", 1)},
    {"label": "OBS_FINDING", **get_span(t_456123_2, "multiloculated", 1)},
    {"label": "OBS_LESION", **get_span(t_456123_2, "empyema", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_2, "pigtail catheter", 1)},
    {"label": "MEDICATION", **get_span(t_456123_2, "tissue plasminogen activator", 1)},
    {"label": "MEDICATION", **get_span(t_456123_2, "dornase alfa", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_2, "instilled", 1)},
    {"label": "ANAT_PLEURA", **get_span(t_456123_2, "pleural cavity", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_2, "catheter", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_2, "two hours", 1)},
]
BATCH_DATA.append({"id": "456123_syn_2", "text": t_456123_2, "entities": e_456123_2})

# --- 456123_syn_3 ---
t_456123_3 = """Billing Code: 32561 (Instillation of fibrinolytic agent).
Dosage: tPA 10mg, DNase 5mg.
Route: Via existing indwelling pleural catheter.
Indication: Empyema with septations (ICD-10 J86.9).
Note: First dose of planned regimen."""
e_456123_3 = [
    {"label": "PROC_ACTION", **get_span(t_456123_3, "Instillation", 1)},
    {"label": "MEDICATION", **get_span(t_456123_3, "fibrinolytic agent", 1)},
    {"label": "MEDICATION", **get_span(t_456123_3, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t_456123_3, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_3, "pleural catheter", 1)},
    {"label": "OBS_LESION", **get_span(t_456123_3, "Empyema", 1)},
    {"label": "OBS_FINDING", **get_span(t_456123_3, "septations", 1)},
]
BATCH_DATA.append({"id": "456123_syn_3", "text": t_456123_3, "entities": e_456123_3})

# --- 456123_syn_4 ---
t_456123_4 = """Resident Procedure Note
Patient: [REDACTED]
Procedure: Fibrinolytic Instillation
Steps:
1. Time out performed.
2. Catheter hub cleaned.
3. Meds instilled (tPA/DNase).
4. Clamped x 2h.
5. Opened to drainage.
No complications."""
e_456123_4 = [
    {"label": "MEDICATION", **get_span(t_456123_4, "Fibrinolytic", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_4, "Instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_4, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_4, "instilled", 1)},
    {"label": "MEDICATION", **get_span(t_456123_4, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t_456123_4, "DNase", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_4, "2h", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_456123_4, "No complications", 1)},
]
BATCH_DATA.append({"id": "456123_syn_4", "text": t_456123_4, "entities": e_456123_4})

# --- 456123_syn_5 ---
t_456123_5 = """Harold Williams 76M with empyema we put in the lytics today tpa 10 and dnase 5 pushed through the pigtail clamped it for a couple hours draining ok now no pain fever or anything will do again tonight."""
e_456123_5 = [
    {"label": "OBS_LESION", **get_span(t_456123_5, "empyema", 1)},
    {"label": "MEDICATION", **get_span(t_456123_5, "tpa", 1)},
    {"label": "MEDICATION", **get_span(t_456123_5, "dnase", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_5, "pushed", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_5, "pigtail", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_5, "couple hours", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t_456123_5, "no pain", 1)},
]
BATCH_DATA.append({"id": "456123_syn_5", "text": t_456123_5, "entities": e_456123_5})

# --- 456123_syn_6 ---
t_456123_6 = """76M with multiloculated empyema. Instillation of fibrinolytic agents via indwelling pleural catheter Day 1. Sterile technique used. Pleural catheter flushed with 10mL saline. tPA 10mg in 30mL NS and DNase 5mg in 30mL NS instilled. Total dwell time 2 hours. Catheter unclamped to water seal. Patient stable."""
e_456123_6 = [
    {"label": "OBS_FINDING", **get_span(t_456123_6, "multiloculated", 1)},
    {"label": "OBS_LESION", **get_span(t_456123_6, "empyema", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_6, "Instillation", 1)},
    {"label": "MEDICATION", **get_span(t_456123_6, "fibrinolytic agents", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_6, "pleural catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_6, "Pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_6, "flushed", 1)},
    {"label": "MEAS_VOL", **get_span(t_456123_6, "10mL", 1)},
    {"label": "MEDICATION", **get_span(t_456123_6, "tPA", 1)},
    {"label": "MEAS_VOL", **get_span(t_456123_6, "30mL", 1)},
    {"label": "MEDICATION", **get_span(t_456123_6, "DNase", 1)},
    {"label": "MEAS_VOL", **get_span(t_456123_6, "30mL", 2)},
    {"label": "PROC_ACTION", **get_span(t_456123_6, "instilled", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_6, "2 hours", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_6, "Catheter", 1)},
]
BATCH_DATA.append({"id": "456123_syn_6", "text": t_456123_6, "entities": e_456123_6})

# --- 456123_syn_7 ---
t_456123_7 = """[Indication]
Empyema with multiple septations.
[Anesthesia]
None.
[Description]
Instilled tPA 10mg and DNase 5mg via left pigtail catheter. Dwell time 2 hours.
[Plan]
Continue q12h dosing."""
e_456123_7 = [
    {"label": "OBS_LESION", **get_span(t_456123_7, "Empyema", 1)},
    {"label": "OBS_FINDING", **get_span(t_456123_7, "septations", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_7, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(t_456123_7, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t_456123_7, "DNase", 1)},
    {"label": "LATERALITY", **get_span(t_456123_7, "left", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_7, "pigtail catheter", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_7, "2 hours", 1)},
]
BATCH_DATA.append({"id": "456123_syn_7", "text": t_456123_7, "entities": e_456123_7})

# --- 456123_syn_8 ---
t_456123_8 = """[REDACTED] a complicated empyema that isn't draining well with just the catheter. Today we started fibrinolytic therapy to break up the loculations. We injected tPA and DNase through his chest tube and let it sit for two hours. Afterward, we opened the tube back up to the water seal. He didn't have any pain or fever during the process."""
e_456123_8 = [
    {"label": "OBS_LESION", **get_span(t_456123_8, "empyema", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_8, "catheter", 1)},
    {"label": "MEDICATION", **get_span(t_456123_8, "fibrinolytic", 1)},
    {"label": "OBS_FINDING", **get_span(t_456123_8, "loculations", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_8, "injected", 1)},
    {"label": "MEDICATION", **get_span(t_456123_8, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t_456123_8, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_8, "chest tube", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_8, "two hours", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t_456123_8, "didn't have any pain", 1)},
]
BATCH_DATA.append({"id": "456123_syn_8", "text": t_456123_8, "entities": e_456123_8})

# --- 456123_syn_9 ---
t_456123_9 = """Indication: Septated empyema.
Action: Introduced fibrinolytic agents via pleural tube (Day 1).
Details: The catheter was prepped. 10mg alteplase and 5mg dornase alfa were injected. The tube was closed for 2 hours, then released to the water seal. Patient remained stable."""
e_456123_9 = [
    {"label": "OBS_FINDING", **get_span(t_456123_9, "Septated", 1)},
    {"label": "OBS_LESION", **get_span(t_456123_9, "empyema", 1)},
    {"label": "MEDICATION", **get_span(t_456123_9, "fibrinolytic agents", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_9, "pleural tube", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_9, "catheter", 1)},
    {"label": "MEDICATION", **get_span(t_456123_9, "alteplase", 1)},
    {"label": "MEDICATION", **get_span(t_456123_9, "dornase alfa", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_9, "injected", 1)},
    {"label": "CTX_TIME", **get_span(t_456123_9, "2 hours", 1)},
]
BATCH_DATA.append({"id": "456123_syn_9", "text": t_456123_9, "entities": e_456123_9})

# --- 456123 (Main) ---
t_456123_main = """Name: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (76 years old)
Date of Service: [REDACTED]
Location: [REDACTED]
Attending: Dr. Sarah Kim, MD - Interventional Pulmonology

Indication: Empyema with multiple septations, post-pneumonia

History: 76M with DM2, recent hospitalization for CAP now with empyema. Pigtail catheter placed 12/02. Minimal output despite appropriate positioning. CT shows multiloculated collection.

Procedure: Instillation of fibrinolytic via indwelling pleural catheter (Day 1)
Using sterile technique, pleural catheter flushed with 10mL saline. Then instilled:
- tPA 10mg in 30mL NS
- DNase 5mg in 30mL NS
Total dwell time: 2 hours
Catheter unclamped to water seal.

Patient [REDACTED]. No pain. No fever. Will continue q12h dosing.

S. Kim, MD"""
e_456123_main = [
    {"label": "OBS_LESION", **get_span(t_456123_main, "Empyema", 1)},
    {"label": "OBS_FINDING", **get_span(t_456123_main, "septations", 1)},
    {"label": "OBS_LESION", **get_span(t_456123_main, "empyema", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_main, "Pigtail catheter", 1)},
    {"label": "OBS_FINDING", **get_span(t_456123_main, "multiloculated", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_main, "Instillation", 1)},
    {"label": "MEDICATION", **get_span(t_456123_main, "fibrinolytic", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_main, "pleural catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_main, "pleural catheter", 2)},
    {"label": "PROC_ACTION", **get_span(t_456123_main, "flushed", 1)},
    {"label": "MEAS_VOL", **get_span(t_456123_main, "10mL", 1)},
    {"label": "PROC_ACTION", **get_span(t_456123_main, "instilled", 1)},
    {"label": "MEDICATION", **get_span(t_456123_main, "tPA", 1)},
    {"label": "MEAS_VOL", **get_span(t_456123_main, "30mL", 1)},
    {"label": "MEDICATION", **get_span(t_456123_main, "DNase", 1)},
    {"label": "MEAS_VOL", **get_span(t_456123_main, "30mL", 2)},
    {"label": "CTX_TIME", **get_span(t_456123_main, "2 hours", 1)},
    {"label": "DEV_CATHETER", **get_span(t_456123_main, "Catheter", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t_456123_main, "No pain", 1)},
]
BATCH_DATA.append({"id": "456123", "text": t_456123_main, "entities": e_456123_main})

# ==============================================================================
# BATCH: 74-8829-C.json (Microwave Ablation)
# ==============================================================================

# --- 74-8829-C_syn_1 ---
t_8829_1 = """Indication: RUL Adenocarcinoma.
Procedure: Microwave Ablation.
Probe: Neuwave 14mm.
Settings: 60W, 6 min.
Guidance: ENB + R-EBUS.
Result: Good ablation zone. No complications.
Plan: Discharge tomorrow."""
e_8829_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_1, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_1, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_1, "Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_1, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(t_8829_1, "14mm", 1)},
    {"label": "MEAS_ENERGY", **get_span(t_8829_1, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t_8829_1, "6 min", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_1, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_1, "R-EBUS", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_8829_1, "No complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_1", "text": t_8829_1, "entities": e_8829_1})

# --- 74-8829-C_syn_2 ---
t_8829_2 = """OPERATIVE REPORT: Bronchoscopic Microwave Ablation.
CLINICAL SUMMARY: Patient with medically inoperable RUL adenocarcinoma.
PROCEDURE: The target lesion in the RUL anterior segment was localized using electromagnetic navigation and confirmed via radial EBUS (contact view). A Neuwave microwave antenna was deployed. Microwave energy was delivered at 60 Watts for 6 minutes. Post-ablation imaging verified adequate coverage of the lesion. The patient tolerated the procedure well."""
e_8829_2 = [
    {"label": "PROC_METHOD", **get_span(t_8829_2, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_2, "Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_2, "adenocarcinoma", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_2, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_2, "electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_2, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_2, "Neuwave", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_2, "microwave antenna", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_2, "Microwave", 2)},
    {"label": "MEAS_ENERGY", **get_span(t_8829_2, "60 Watts", 1)},
    {"label": "MEAS_TIME", **get_span(t_8829_2, "6 minutes", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_2, "lesion", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_2", "text": t_8829_2, "entities": e_8829_2})

# --- 74-8829-C_syn_3 ---
t_8829_3 = """Service: 31641 (Destruction of tumor).
Method: Microwave Ablation.
Device: Neuwave System.
Support: 31627 (Navigation), 31654 (Radial EBUS).
Narrative: Navigated to RUL nodule. Verified tool-in-lesion. Delivered microwave energy to destroy tumor. Post-procedure check negative for pneumothorax."""
e_8829_3 = [
    {"label": "OBS_LESION", **get_span(t_8829_3, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_3, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_3, "Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_3, "Neuwave System", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_3, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_3, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_3, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_3, "microwave", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_3, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_3", "text": t_8829_3, "entities": e_8829_3})

# --- 74-8829-C_syn_4 ---
t_8829_4 = """Procedure: Microwave Ablation
Patient: [REDACTED]
Location: RUL anterior.
Steps:
1. Navigated to lesion (SuperDimension).
2. Confirmed with Radial EBUS.
3. Inserted Microwave catheter.
4. Ablated 60W for 6 mins.
5. Checked airway - clear.
Plan: Post-op CT."""
e_8829_4 = [
    {"label": "PROC_METHOD", **get_span(t_8829_4, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_4, "Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_4, "RUL anterior", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_4, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_4, "SuperDimension", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_4, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_4, "Microwave catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_4, "Ablated", 1)},
    {"label": "MEAS_ENERGY", **get_span(t_8829_4, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t_8829_4, "6 mins", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_8829_4, "airway", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_4", "text": t_8829_4, "entities": e_8829_4})

# --- 74-8829-C_syn_5 ---
t_8829_5 = """done by Dr Foster for [REDACTED] Sato. RUL cancer. used the superD to get there and radial ebus to see it. put the microwave needle in. burned it for 6 mins at 60 watts. looks like we got it all based on the scan after. patient woke up fine no pneumo."""
e_8829_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_5, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_5, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_5, "superD", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_5, "radial ebus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_5, "microwave needle", 1)},
    {"label": "MEAS_TIME", **get_span(t_8829_5, "6 mins", 1)},
    {"label": "MEAS_ENERGY", **get_span(t_8829_5, "60 watts", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_5", "text": t_8829_5, "entities": e_8829_5})

# --- 74-8829-C_syn_6 ---
t_8829_6 = """Bronchoscopic microwave ablation. Right upper lobe nodule. General anesthesia. Electromagnetic navigation to RUL anterior segment. Target confirmed in contact position with radial EBUS. Microwave probe inserted. Ablation performed at 60W for 6 minutes. Lesion coverage confirmed. Airway patent. Extubated."""
e_8829_6 = [
    {"label": "PROC_METHOD", **get_span(t_8829_6, "microwave", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_6, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_6, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_6, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_6, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_6, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_6, "Microwave probe", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_6, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(t_8829_6, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t_8829_6, "6 minutes", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_6, "Lesion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_8829_6, "Airway", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_6", "text": t_8829_6, "entities": e_8829_6})

# --- 74-8829-C_syn_7 ---
t_8829_7 = """[Indication]
RUL Adenocarcinoma.
[Anesthesia]
General.
[Description]
Navigation to RUL anterior segment. Microwave ablation (60W x 6min). Lesion destroyed. No complications.
[Plan]
[REDACTED] in 24h."""
e_8829_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_7, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_7, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_7, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_7, "ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(t_8829_7, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t_8829_7, "6min", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_7, "Lesion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_8829_7, "No complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_7", "text": t_8829_7, "entities": e_8829_7})

# --- 74-8829-C_syn_8 ---
t_8829_8 = """[REDACTED] in for ablation of his right upper lobe lung cancer. We used a microwave probe inserted through the bronchoscope. After finding the tumor with navigation and ultrasound, we applied microwave energy for 6 minutes. This heated the tumor enough to destroy it. He is recovering well."""
e_8829_8 = [
    {"label": "PROC_ACTION", **get_span(t_8829_8, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_8, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_8, "lung cancer", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_8, "microwave probe", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_8, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_8, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_8, "ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_8, "microwave", 2)},
    {"label": "MEAS_TIME", **get_span(t_8829_8, "6 minutes", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_8, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_8", "text": t_8829_8, "entities": e_8829_8})

# --- 74-8829-C_syn_9 ---
t_8829_9 = """Procedure: Bronchoscopic tumor destruction.
Modality: Microwave energy.
Action: The RUL neoplasm was targeted. The microwave antenna was positioned. Thermal energy was delivered to ablate the mass. 
Result: Therapeutic destruction of the tumor."""
e_8829_9 = [
    {"label": "OBS_LESION", **get_span(t_8829_9, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_9, "Microwave", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_9, "neoplasm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_9, "microwave antenna", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_9, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_9, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_9, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_9", "text": t_8829_9, "entities": e_8829_9})

# --- 74-8829-C (Main) ---
t_8829_main = """DATE: [REDACTED]
PATIENT: [REDACTED] || MRN: [REDACTED]
SURGEON: Dr. Amanda Foster
FACILITY: [REDACTED]

PREOP DX: RUL nodule, 2.1 cm, adenocarcinoma
POSTOP DX: Same  
OPERATION: Bronchoscopic microwave ablation

ANESTHESIA: General with ETT
EBL: <10cc
COMPLICATIONS: None

PROCEDURE NOTE:
62M with RUL adenocarcinoma, medically inoperable. Bronchoscopy performed. ENB navigation to RUL anterior segment lesion (superDimension system). R-EBUS confirmed target in contact position. Microwave probe (Neuwave, 14mm antenna) inserted. Ablation: 60W x 6 min. Good lesion coverage on post-ablation imaging. Airways inspected - no complications. Extubated, stable to PACU.

PLAN: CXR in 4h, CT in 24h, discharge tomorrow if stable, f/u 4 weeks.

A. Foster, MD
Interventional Pulmonology"""
e_8829_main = [
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_main, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_main, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t_8829_main, "2.1 cm", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_main, "adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_main, "microwave", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_main, "ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_8829_main, "None", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_main, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t_8829_main, "adenocarcinoma", 2)},
    {"label": "PROC_METHOD", **get_span(t_8829_main, "ENB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_8829_main, "RUL anterior segment", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_main, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_main, "superDimension", 1)},
    {"label": "PROC_METHOD", **get_span(t_8829_main, "R-EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_main, "Microwave probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_8829_main, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(t_8829_main, "14mm", 1)},
    {"label": "PROC_ACTION", **get_span(t_8829_main, "Ablation", 1)}, # FIXED: Occurrence 2 -> 1 (Capitalized 'Ablation' only appears once)
    {"label": "MEAS_ENERGY", **get_span(t_8829_main, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t_8829_main, "6 min", 1)},
    {"label": "OBS_LESION", **get_span(t_8829_main, "lesion", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t_8829_main, "Airways", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_8829_main, "no complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C", "text": t_8829_main, "entities": e_8829_main})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")