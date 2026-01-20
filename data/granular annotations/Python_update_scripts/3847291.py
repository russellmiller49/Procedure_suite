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
# 3. Batch Data Definitions
# ==========================================
BATCH_DATA = []

# --- Note 1: 3847291_syn_1 ---
text_1 = """Pre-op: Post-intubation subglottic stenosis.
Anesthesia: GA, Jet ventilation.
Action: Flex bronch. Web-like stenosis 2cm below cords (70%). CRE Balloon dilation: 10mm -> 12mm -> 14mm (8 ATM x 60s). 
Result: Lumen 90% patent. Minimal bleeding.
Plan: D/C. Re-scope 6-8 wks."""

entities_1 = [
    {"label": "ANAT_AIRWAY", **get_span(text_1, "subglottic", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Jet ventilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Flex bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Flex bronch", 1)}, # Implied procedure
    {"label": "OBS_LESION", **get_span(text_1, "Web-like stenosis", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "cords", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "70%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "CRE Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14mm", 1)},
    {"label": "MEAS_PRESS", **get_span(text_1, "8 ATM", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "60s", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "Lumen 90% patent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Minimal bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Re-scope", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_1", "text": text_1, "entities": entities_1})


# --- Note 2: 3847291_syn_2 ---
text_2 = """INDICATION: The patient, a 68-year-old female, presented with stridor following prolonged intubation. Radiographic evaluation demonstrated critical subglottic stenosis.
PROCEDURE: General anesthesia utilizing jet ventilation was induced. Bronchoscopic inspection revealed a fibrous circumferential stricture 2 cm subglottically, compromising 70% of the lumen. Intervention proceeded with sequential hydrostatic balloon dilation utilizing a CRE catheter graduated to 14mm at 8 atmospheres. Post-procedural assessment confirmed restoration of airway caliber to approximately 90% of expected diameter. Hemostasis was maintained.
DISPOSITION: The patient was transferred to the PACU in stable condition."""

entities_2 = [
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_2, "stridor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "subglottic", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "jet ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Bronchoscopic", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "fibrous circumferential stricture", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "2 cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "subglottically", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "70% of the lumen", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "balloon dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "CRE catheter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "14mm", 1)},
    {"label": "MEAS_PRESS", **get_span(text_2, "8 atmospheres", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "90% of expected diameter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "Hemostasis was maintained", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_2", "text": text_2, "entities": entities_2})


# --- Note 3: 3847291_syn_3 ---
text_3 = """Procedure: Bronchoscopy with Balloon Dilation (CPT 31630).
Technique: Flexible bronchoscope introduced via oral route under general anesthesia (Jet Ventilation).
Findings: 70% stenosis id[REDACTED] in subglottic trachea.
Intervention: Controlled Radial Expansion (CRE) balloon dilator utilized. Sequential inflations performed at 10mm, 12mm, and 14mm diameters. Pressure maintained at 8 ATM for 60 seconds per cycle.
Outcome: Successful dilation to 14mm; >90% patency achieved. Medical necessity supported by symptomatic stenosis."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Balloon Dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Flexible bronchoscope", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Jet Ventilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "70% stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "subglottic trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Controlled Radial Expansion (CRE) balloon dilator", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "10mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "12mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "14mm", 1)}, # First occurrence
    {"label": "MEAS_PRESS", **get_span(text_3, "8 ATM", 1)},
    {"label": "MEAS_TIME", **get_span(text_3, "60 seconds", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "14mm", 2)}, # Second occurrence in Outcome
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, ">90% patency", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "stenosis", 2)},
]
BATCH_DATA.append({"id": "3847291_syn_3", "text": text_3, "entities": entities_3})


# --- Note 4: 3847291_syn_4 ---
text_4 = """Resident Procedure Note
Patient: [REDACTED] Wilson
Attending: Dr. Rodriguez
Diagnosis: Subglottic stenosis
Steps:
1. Time out. GA/Jet vent.
2. Scope inserted. Saw 70% stenosis subglottic.
3. Dilation performed: Used CRE balloon. Sizes 10, 12, 14mm.
4. Held for 60s at 8atm.
5. Checked airway: Looks good, 90% open.
Plan: PPIs, follow up 2 months."""

entities_4 = [
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Subglottic", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Jet vent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_4, "70% stenosis", 1)},
    # Fixed: changed occurrence from 2 to 1 because "subglottic" (lowercase) appears only once. The first one is "Subglottic" (uppercase).
    {"label": "ANAT_AIRWAY", **get_span(text_4, "subglottic", 1)}, 
    {"label": "PROC_ACTION", **get_span(text_4, "Dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "10", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "12", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "14mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_4, "60s", 1)},
    {"label": "MEAS_PRESS", **get_span(text_4, "8atm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "90% open", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_4", "text": text_4, "entities": entities_4})


# --- Note 5: 3847291_syn_5 ---
text_5 = """Procedure note for Dorothy Evans for the tracheal stenosis dilation used jet ventilation patient asleep. Went in with the flexible scope saw the narrowing about 70 percent block. Did the balloon dilation started at 10 went up to 14 millimeters held it for a minute each time at 8 atmospheres. Opened up nice to about 90 percent no tearing really just a little blood. Woke up fine sending to recovery plan for repeat scope later."""

entities_5 = [
    {"label": "ANAT_AIRWAY", **get_span(text_5, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "dilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "jet ventilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "flexible scope", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "narrowing", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "70 percent block", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "balloon dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "10", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "14 millimeters", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "minute", 1)},
    {"label": "MEAS_PRESS", **get_span(text_5, "8 atmospheres", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "90 percent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no tearing", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "repeat scope", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_5", "text": text_5, "entities": entities_5})


# --- Note 6: 3847291_syn_6 ---
text_6 = """The patient was brought to the operating room and placed under general anesthesia with jet ventilation. Flexible bronchoscopy revealed circumferential web-like stenosis 2cm below vocal cords with 65-70% luminal obstruction. Sequential balloon dilation performed using CRE balloon dilator, starting at 10mm, progressed to 12mm, then 14mm over three cycles. Each inflation held for 60 seconds at 8 ATM. Post-dilation exam showed adequate lumen restored to approximately 90% patency. No mucosal tears. Minimal bleeding controlled with observation."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "jet ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Flexible bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "stenosis", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "2cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "vocal cords", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "65-70% luminal obstruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "balloon dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "CRE balloon dilator", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "10mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "12mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "14mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_6, "60 seconds", 1)},
    {"label": "MEAS_PRESS", **get_span(text_6, "8 ATM", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "90% patency", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No mucosal tears", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "Minimal bleeding controlled", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_6", "text": text_6, "entities": entities_6})


# --- Note 7: 3847291_syn_7 ---
text_7 = """[Indication]
Post-intubation subglottic stenosis, symptomatic with stridor.
[Anesthesia]
General anesthesia, Jet ventilation.
[Description]
Circumferential stenosis 2cm below cords (70%). Sequential CRE balloon dilation performed (10, 12, 14mm) at 8 ATM x 60s. Lumen restored to 90% patency. Minimal bleeding.
[Plan]
Discharge today. PPI. Repeat bronchoscopy 6-8 weeks."""

entities_7 = [
    {"label": "ANAT_AIRWAY", **get_span(text_7, "subglottic", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "stenosis", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_7, "stridor", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Jet ventilation", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "stenosis", 2)},
    {"label": "MEAS_SIZE", **get_span(text_7, "2cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "cords", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "70%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "10", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "12", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "14mm", 1)},
    {"label": "MEAS_PRESS", **get_span(text_7, "8 ATM", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "60s", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "90% patency", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "Minimal bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Repeat bronchoscopy", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_7", "text": text_7, "entities": entities_7})


# --- Note 8: 3847291_syn_8 ---
text_8 = """[REDACTED] brought to the suite for management of her subglottic stenosis. Under general anesthesia with jet ventilation, we advanced the bronchoscope and visualized the stricture, which was narrowing the airway by about 70%. We used a CRE balloon to dilate the area, sequentially increasing the size from 10mm to 14mm. We held the inflations for 60 seconds at 8 atmospheres. The airway opened up significantly to about 90% patency. There was only minimal bleeding which stopped on its own."""

entities_8 = [
    {"label": "ANAT_AIRWAY", **get_span(text_8, "subglottic", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "jet ventilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "bronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "stricture", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "narrowing the airway by about 70%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dilate", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "10mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "14mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_8, "60 seconds", 1)},
    {"label": "MEAS_PRESS", **get_span(text_8, "8 atmospheres", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "90% patency", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "minimal bleeding", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_8", "text": text_8, "entities": entities_8})


# --- Note 9: 3847291_syn_9 ---
text_9 = """PRE-OP DX: Post-intubation tracheal constriction
PROCEDURE: Bronchoscopy with pneumatic expansion of tracheal constriction
DETAILS: Patient anesthetized via jet ventilation. Scope revealed circumferential web-like constriction 2cm below vocal cords with 70% blockage. Sequential pneumatic expansion executed using CRE dilator, starting at 10mm, progressed to 14mm. Each inflation maintained for 60 seconds. Post-expansion exam showed adequate airway restored to 90% openness. No mucosal lacerations."""

entities_9 = [
    {"label": "ANAT_AIRWAY", **get_span(text_9, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "constriction", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "pneumatic expansion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "tracheal", 2)},
    {"label": "OBS_LESION", **get_span(text_9, "constriction", 2)},
    {"label": "PROC_METHOD", **get_span(text_9, "jet ventilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Scope", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "constriction", 3)},
    {"label": "MEAS_SIZE", **get_span(text_9, "2cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "vocal cords", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_9, "70% blockage", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "pneumatic expansion", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "CRE dilator", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "10mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "14mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_9, "60 seconds", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "90% openness", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "No mucosal lacerations", 1)},
]
BATCH_DATA.append({"id": "3847291_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)