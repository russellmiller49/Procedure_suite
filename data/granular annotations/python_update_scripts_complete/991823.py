import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure 'scripts.add_training_case' is in your python path
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is run from the correct directory context.")
    sys.exit(1)

# Container for all batch data
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 991823_syn_1
# ==========================================
id_1 = "991823_syn_1"
text_1 = """Indication: Empyema suspected.
Procedure: US guided access. 6F catheter placed -> frank pus. Converted to 14F chest tube via Seldinger. 450cc purulent drainage. tPA/DNase instilled. Tube clamped.
Complications: None."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Empyema", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "US", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "6F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "frank pus", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "450cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "purulent drainage", 1)},
    {"label": "MEDICATION", **get_span(text_1, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_1, "DNase", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 991823_syn_2
# ==========================================
id_2 = "991823_syn_2"
text_2 = """OPERATIVE REPORT: PLEURAL INTERVENTION
The patient presented with signs of pleural sepsis. Ultrasound interrogation of the right hemithorax revealed a complex, loculated effusion. Initial diagnostic thoracentesis yielded frank purulence, necessitating immediate escalation to tube thoracostomy. A 14 French Wayne catheter was sited using the Seldinger technique, draining 450 mL of purulent fluid. To address the loculations, intrapleural fibrinolytic therapy (tPA/DNase) was administered."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "PLEURAL INTERVENTION", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Ultrasound", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "hemithorax", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "thoracentesis", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "frank purulence", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "tube thoracostomy", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "14 French", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "Wayne catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "450 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "purulent fluid", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "loculations", 1)},
    {"label": "MEDICATION", **get_span(text_2, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_2, "DNase", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 991823_syn_3
# ==========================================
id_3 = "991823_syn_3"
text_3 = """Primary Service: Tube Thoracostomy (32551).
Secondary Service: Fibrinolytic Instillation (32561).
Sequence: Diagnostic aspiration (bundled) -> Conversion to therapeutic drainage (billable). 
Site: [REDACTED]
Device: 14Fr Pigtail.
Output: 450cc purulent fluid.
Note: 32555 not billed as it converted to 32551 at same site."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Tube Thoracostomy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Fibrinolytic Instillation", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Diagnostic aspiration", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "450cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "purulent fluid", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 991823_syn_4
# ==========================================
id_4 = "991823_syn_4"
text_4 = """Procedure: Chest Tube Placement
Resident: Dr. X
Steps:
1. US check: Loculated fluid.
2. Local lidocaine.
3. Needle access -> Pus.
4. Wire placed.
5. Dilated.
6. 14Fr chest tube placed.
7. 10mg tPA / 5mg DNase instilled.
8. Clamped."""
entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Chest Tube Placement", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "US", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Loculated", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "fluid", 1)},
    {"label": "MEDICATION", **get_span(text_4, "lidocaine", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Needle", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Pus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Wire", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "chest tube", 1)},
    {"label": "MEDICATION", **get_span(text_4, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_4, "DNase", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 991823_syn_5
# ==========================================
id_5 = "991823_syn_5"
text_5 = """Dr Xavier here seeing Mr [REDACTED] for the empyema right side. Started as a tap put in the small catheter got straight pus out so we switched to a chest tube right there. 14 french wayne. Drained about 450 pus. Because of the loculations on the ultrasound we put in tPA and DNase right away. Clamped it. Admitting him."""
entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "empyema", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "pus", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5, "14 french", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "wayne", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "pus", 2)},
    {"label": "OBS_FINDING", **get_span(text_5, "loculations", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "MEDICATION", **get_span(text_5, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_5, "DNase", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 991823_syn_6
# ==========================================
id_6 = "991823_syn_6"
text_6 = """Ultrasound-guided pleural intervention. Initial aspiration yielded frank purulence. Procedure converted to tube thoracostomy. 14 Fr catheter inserted via Seldinger technique. 450 cc purulent fluid evacuated. 10mg tPA and 5mg DNase instilled intrapleurally for loculation management. Tube clamped. Patient stable."""
entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "pleural intervention", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "aspiration", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "frank purulence", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "tube thoracostomy", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "14 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "450 cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "purulent fluid", 1)},
    {"label": "MEDICATION", **get_span(text_6, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_6, "DNase", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 991823_syn_7
# ==========================================
id_7 = "991823_syn_7"
text_7 = """[Indication]
Fevers, loculated right pleural effusion, empyema concern.
[Anesthesia]
Local (Lidocaine).
[Description]
Diagnostic thoracentesis revealed pus. Converted to 14Fr chest tube placement. 450cc purulent drainage. Instillation of tPA/DNase.
[Plan]
Admit for empyema protocol."""
entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "loculated", 1)},
    {"label": "LATERALITY", **get_span(text_7, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "empyema", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Lidocaine", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Diagnostic thoracentesis", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "pus", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "chest tube", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "450cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "purulent drainage", 1)},
    {"label": "MEDICATION", **get_span(text_7, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_7, "DNase", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 991823_syn_8
# ==========================================
id_8 = "991823_syn_8"
text_8 = """We performed a pleural intervention on [REDACTED]. Initially, we inserted a small catheter for diagnostic purposes, which revealed frank pus. Consequently, we immediately proceeded to place a 14 French chest tube in the same location to establish drainage. We drained 450cc of fluid. Given the loculations seen on ultrasound, we instilled fibrinolytics (tPA and DNase) directly into the tube before clamping it."""
entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "pleural intervention", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "frank pus", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_8, "14 French", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "450cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "loculations", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "MEDICATION", **get_span(text_8, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_8, "DNase", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 991823_syn_9
# ==========================================
id_9 = "991823_syn_9"
text_9 = """Procedure: Thoracostomy conversion.
Action: The pleural space was accessed. Purulence was aspirated. A drainage catheter was deployed. Effusion was evacuated. Fibrinolytics were administered.
Outcome: Tube in situ."""
entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Thoracostomy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Purulence", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "drainage catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Effusion", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 991823
# ==========================================
id_10 = "991823"
text_10 = """PROCEDURE NOTE: PLEURAL INTERVENTION CONVERSION

**Patient:** James Howlett (MRN: [REDACTED])
**Date:** [REDACTED]
**Provider:** Dr. C. Xavier

**Indication:** 55M with fevers and large right pleural effusion. Concern for empyema.

**Procedure Details:**
Timeout performed. Right posterior chest prepped. 
Ultrasound id[REDACTED] a loculated fluid collection. Local anesthesia (20cc Lidocaine). 

1. **Diagnostic Thoracentesis:** A 6Fr catheter was inserted. 60cc of frank purulent fluid (pus) was aspirated. 
   *Decision made to escalate to tube thoracostomy immediately given gross empyema.*

2. **Chest Tube Placement:** Using the same site (tract dilated), a 14Fr Wayne pigtail catheter was inserted using Seldinger technique. 
   Return: 450cc purulent fluid. 
   Tube sutured in place and connected to atrium.

3. **Fibrinolytics:** Given loculations seen on US, 10mg tPA and 5mg DNase were instilled through the new chest tube at the end of the case. Tube clamped.

**Complications:** None.
**Disposition:** Admitted for empyema management."""
entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "PLEURAL INTERVENTION CONVERSION", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "empyema", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "chest", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "loculated", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Lidocaine", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Diagnostic Thoracentesis", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "6Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "60cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "frank purulent fluid", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "pus", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "tube thoracostomy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "empyema", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Chest Tube Placement", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Wayne pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "450cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "purulent fluid", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "loculations", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "US", 1)},
    {"label": "MEDICATION", **get_span(text_10, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_10, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)