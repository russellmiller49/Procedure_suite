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
# 2. Helper Definition
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: S31640-022_syn_1
# ==========================================
t1 = """Indication: Tracheal tumor, dyspnea.
Approach: Rigid bronchoscopy.
Action: Coring and forceps debulking of proximal tracheal mass. Snare used for pedunculated portion. No ablation.
Result: Lumen patency improved from 30% to patent.
EBL: 15mL.
Plan: D/C to home."""
e1 = [
    {"label": "ANAT_AIRWAY", **get_span(t1, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t1, "tumor", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t1, "dyspnea", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "debulking", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Snare", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "30%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "patent", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "15mL", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: S31640-022_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Mr. James Anderson, presenting with stridor secondary to a proximal tracheal neoplasm, underwent rigid bronchoscopy. The airway was secured, and the lesion—a sessile mass occluding 70% of the lumen—was visualized. Mechanical resection was executed utilizing the rigid bronchoscope barrel for coring, supplemented by forceps extraction and snare resection of pedunculated elements. Thermal modalities were strictly avoided. Hemostasis was spontaneous or assisted by cold saline lavage."""
e2 = [
    {"label": "OUTCOME_SYMPTOMS", **get_span(t2, "stridor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t2, "neoplasm", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "rigid bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "airway", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 1)},
    {"label": "OBS_LESION", **get_span(t2, "sessile mass", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "70%", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "resection", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "extraction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "snare", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "resection", 2)},
    {"label": "PROC_ACTION", **get_span(t2, "lavage", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: S31640-022_syn_3
# ==========================================
t3 = """CPT: 31640 (Excision of Tumor).
Technique: Rigid Bronchoscopy with Mechanical Debulking.
Tools: Rigid scope (coring), Forceps, Snare.
Site: Proximal Trachea.
Narrative: The patient was anesthetized. Rigid scope inserted. Tumor mechanically cored and removed with forceps. Snare used for polypoid component. No laser or cryotherapy utilized. Pathologic specimen collected."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Excision", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Snare", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Proximal Trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Rigid scope", 2)},
    {"label": "OBS_LESION", **get_span(t3, "Tumor", 2)},
    {"label": "PROC_ACTION", **get_span(t3, "cored", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "removed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Snare", 2)},
]
BATCH_DATA.append({"id": "S31640-022_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: S31640-022_syn_4
# ==========================================
t4 = """Resident Note: Tracheal Debulking
Patient: [REDACTED], 55M
Staff: Dr. Shah
1. General Anesthesia induced.
2. Rigid bronchoscope inserted.
3. Proximal tracheal tumor id[REDACTED] (70% stenosis).
4. Performed mechanical debulking using rigid coring technique and forceps.
5. Snare used for one piece.
6. No complications. Minimal bleeding.
Plan: Extubate, PACU, Home."""
e4 = [
    {"label": "ANAT_AIRWAY", **get_span(t4, "Tracheal", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t4, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t4, "70%", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Snare", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No complications", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: S31640-022_syn_5
# ==========================================
t5 = """Procedure note for William Taylor he has that tracheal tumor causing noisy breathing we took him to the OR for rigid bronchoscopy did the mechanical debulking used the rigid scope to core it out and forceps to grab the pieces also used a snare for a hanging part no balloons or burning used just mechanical removal bleeding was minimal 15ml he did fine extubated sent to pacu then home later"""
e5 = [
    {"label": "ANAT_AIRWAY", **get_span(t5, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t5, "noisy breathing", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "core", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "snare", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "removal", 1)},
    {"label": "MEAS_VOL", **get_span(t5, "15ml", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: S31640-022_syn_6
# ==========================================
t6 = """BRONCHOSCOPY PROCEDURE NOTE MECHANICAL DEBULKING OF TRACHEAL TUMOR Patient David Thomas 56-year-old male Date [REDACTED] Location Capital Regional Hospital Indication Proximal tracheal tumor with noisy breathing and exertional dyspnea Procedure Rigid bronchoscopy with mechanical debulking excision of proximal tracheal mass CPT 31640 Anesthesia General anesthesia with rigid tracheoscope ASA class III Findings Sessile tumor on anterior proximal tracheal wall narrowing lumen to 70% Interventions Rigid coring and forceps debulking removed most of the lesion Snare resection used to excise a pedunculated portion No ablation or balloon used Hemostasis Minimal controlled with cold saline EBL 15 mL."""
e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "DEBULKING", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "TRACHEAL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "TUMOR", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "Proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t6, "noisy breathing", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t6, "exertional dyspnea", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "excision", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "proximal tracheal", 2)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "rigid tracheoscope", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Sessile tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "anterior proximal tracheal wall", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "70%", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "debulking", 2)},
    {"label": "OBS_LESION", **get_span(t6, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Snare", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "resection", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "15 mL", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: S31640-022_syn_7
# ==========================================
t7 = """[Indication]
Proximal tracheal tumor, stridor, exertional dyspnea.
[Anesthesia]
General Anesthesia, Rigid Bronchoscopy.
[Description]
Rigid scope inserted. 70% occlusion of proximal trachea noted. Mechanical debulking performed via rigid coring, forceps excision, and snare resection. No thermal ablation. Hemostasis secured with cold saline.
[Plan]
Extubate. Discharge home after recovery."""
e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "Proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t7, "stridor", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t7, "exertional dyspnea", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Rigid Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Rigid scope", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "70% occlusion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "proximal trachea", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "excision", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "snare", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "resection", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: S31640-022_syn_8
# ==========================================
t8 = """[REDACTED] rigid bronchoscopy to treat a tumor in his windpipe. Once he was asleep, we inserted the rigid scope and saw the mass blocking about 70% of the airway. We used the sharp edge of the scope to core through the tumor and forceps to pull the pieces out. We also used a snare to cut off a hanging piece. We didn't use any heat or balloons. The bleeding was very light and stopped with some cold saltwater. He went home the same day."""
e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "windpipe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "rigid scope", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "70%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "core", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "snare", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: S31640-022_syn_9
# ==========================================
t9 = """Indication: Proximal tracheal tumor with noisy respiration and exertional breathlessness.
Procedure: Rigid bronchoscopy with physical reduction/extraction of proximal tracheal mass.
Interventions: Rigid coring and forceps removal eliminated most of the lesion. Snare excision utilized to remove a pedunculated segment. No destruction or balloon employed.
Hemostasis: Minimal; managed with chilled saline."""
e9 = [
    {"label": "ANAT_AIRWAY", **get_span(t9, "Proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t9, "noisy respiration", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t9, "exertional breathlessness", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "extraction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "removal", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "Snare", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "excision", 1)},
]
BATCH_DATA.append({"id": "S31640-022_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: S31640-022
# ==========================================
t10 = """BRONCHOSCOPY PROCEDURE NOTE – MECHANICAL DEBULKING OF TRACHEAL TUMOR

Patient: [REDACTED], 55-year-old male
MRN: [REDACTED]
Date: [REDACTED]
Location: [REDACTED]
Attending: Dr. Monica Shah

Indication:
Proximal tracheal tumor with noisy breathing and exertional dyspnea.

Procedure:
Rigid bronchoscopy with mechanical debulking/excision of proximal tracheal mass (CPT 31640).

Anesthesia:
General anesthesia with rigid tracheoscope. ASA class III.

Findings:
Sessile tumor on anterior proximal tracheal wall narrowing lumen to ~70%.

Interventions:
Rigid coring and forceps debulking removed most of the lesion. Snare resection used to excise a pedunculated portion. No ablation or balloon used.

Hemostasis:
Minimal; controlled with cold saline.

EBL:
15 mL.

Complications:
None.

Disposition:
Extubated and discharged to PACU, then home later the same day."""
e10 = [
    {"label": "PROC_ACTION", **get_span(t10, "DEBULKING", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "TRACHEAL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "TUMOR", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Proximal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "noisy breathing", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "exertional dyspnea", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "excision", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "proximal tracheal", 2)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid tracheoscope", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Sessile tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "anterior proximal tracheal wall", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "~70%", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "debulking", 2)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Snare", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "resection", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "15 mL", 1)},
]
BATCH_DATA.append({"id": "S31640-022", "text": t10, "entities": e10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)