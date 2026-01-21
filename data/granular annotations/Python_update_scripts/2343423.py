import sys
from pathlib import Path

# Set up the repository root directory
# (Assuming this script is run from a subdirectory, e.g., /scripts/ or /data/)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports from specific modules
sys.path.append(str(REPO_ROOT))

# Import the utility function to add a case
# Ensure 'scripts.add_training_case' exists in your project structure
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for standalone testing or different structure
    print("Warning: Could not import 'add_case'. Defining a mock function for display.")
    def add_case(case_id, text, entities, repo_root):
        print(f"Added Case: {case_id} ({len(entities)} entities)")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact string to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
        
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
            
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2343423_syn_1
# ==========================================
id_1 = "2343423_syn_1"
text_1 = """Pre-op: Empyema L hemithorax.
Proc: Bedside US + tPA/DNase instillation.
Findings: US chest left showed moderate complex effusion, thick septations. Hyperechoic. Tube in place.
Action: Instilled 10mg tPA / 5mg DNase via existing L chest tube. Clamped.
Plan: Dwell 1 hr then suction."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Empyema", 1)},
    {"label": "LATERALITY", **get_span(text_1, "L", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "hemithorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "US", 1)},
    {"label": "MEDICATION", **get_span(text_1, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_1, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "instillation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "US", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "chest", 1)},
    {"label": "LATERALITY", **get_span(text_1, "left", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "moderate", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "thick", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "septations", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Hyperechoic", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_1, "tPA", 2)},
    {"label": "MEDICATION", **get_span(text_1, "DNase", 2)},
    {"label": "LATERALITY", **get_span(text_1, "L", 2)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Clamped", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Dwell", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "1 hr", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "suction", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2343423_syn_2
# ==========================================
id_2 = "2343423_syn_2"
text_2 = """PROCEDURE NOTE: INTRA-PLEURAL FIBRINOLYTIC THERAPY
INDICATION: [REDACTED], a 38-year-old male with a loculated left-sided empyema, required therapeutic instillation of fibrinolytic agents to facilitate drainage.
IMAGING: Real-time thoracic ultrasonography of the left hemithorax demonstrated a moderate volume pleural effusion characterized by hyperechogenicity and thickened septations, consistent with the diagnosis of empyema.
INTERVENTION: Through the pre-existing left chest tube, a solution containing 10 mg of tissue plasminogen activator (tPA) and 5 mg of deoxyribonuclease (DNase) was instilled using aseptic technique.
PLAN: The catheter will remain clamped for 60 minutes to maximize therapeutic effect before returning to suction."""
entities_2 = [
    {"label": "OBS_FINDING", **get_span(text_2, "loculated", 1)},
    {"label": "LATERALITY", **get_span(text_2, "left", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "empyema", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "instillation", 1)},
    {"label": "MEDICATION", **get_span(text_2, "fibrinolytic agents", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "drainage", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "ultrasonography", 1)},
    {"label": "LATERALITY", **get_span(text_2, "left", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "hemithorax", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "moderate", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "pleural effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "hyperechogenicity", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "thickened", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "septations", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "empyema", 2)},
    {"label": "LATERALITY", **get_span(text_2, "left", 3)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
    {"label": "MEDICATION", **get_span(text_2, "tissue plasminogen activator", 1)},
    {"label": "MEDICATION", **get_span(text_2, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_2, "deoxyribonuclease", 1)},
    {"label": "MEDICATION", **get_span(text_2, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "instilled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "clamped", 1)},
    {"label": "MEAS_TIME", **get_span(text_2, "60 minutes", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "suction", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2343423_syn_3
# ==========================================
id_3 = "2343423_syn_3"
text_3 = """Service: Intrapleural Instillation (CPT 32561) & Chest Ultrasound (CPT 76604-26)
Diagnosis: Empyema (J86.9).
Technique:
1. Ultrasound Assessment: Real-time scanning of the left chest was performed. Findings documented: Moderate effusion, hyperechoic with thick loculations. Images saved.
2. Instillation: Using the indwelling left chest catheter, the initial dose of fibrinolytic agents (10mg tPA/5mg DNase) was administered to break up loculations.
Outcome: Tolerance good. No immediate complications."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Instillation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Chest", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Empyema", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ultrasound", 2)},
    {"label": "PROC_METHOD", **get_span(text_3, "scanning", 1)},
    {"label": "LATERALITY", **get_span(text_3, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "chest", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "Moderate", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "hyperechoic", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "thick", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "loculations", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Instillation", 2)},
    {"label": "LATERALITY", **get_span(text_3, "left", 2)},
    {"label": "DEV_CATHETER", **get_span(text_3, "chest catheter", 1)},
    {"label": "MEDICATION", **get_span(text_3, "fibrinolytic agents", 1)},
    {"label": "MEDICATION", **get_span(text_3, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_3, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "administered", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "loculations", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2343423_syn_4
# ==========================================
id_4 = "2343423_syn_4"
text_4 = """Resident Procedure Note
Patient: [REDACTED]
Procedure: Chest US and tPA/DNase instillation (Day 1).
Staff: Dr. Van Dyke.
Steps:
1. Timeout performed.
2. Bedside US of left chest: Saw moderate effusion, very septated/thick.
3. Existing chest tube checked.
4. Instilled tPA 10mg and DNase 5mg.
5. Clamped tube.
Plan: Unclamp in 1 hour."""
entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "Chest", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "US", 1)},
    {"label": "MEDICATION", **get_span(text_4, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_4, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "instillation", 1)},
    {"label": "CTX_TIME", **get_span(text_4, "Day 1", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "US", 2)},
    {"label": "LATERALITY", **get_span(text_4, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "chest", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "moderate", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "septated", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "thick", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(text_4, "tPA", 2)},
    {"label": "MEDICATION", **get_span(text_4, "DNase", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "Clamped", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Unclamp", 1)},
    {"label": "MEAS_TIME", **get_span(text_4, "1 hour", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2343423_syn_5
# ==========================================
id_5 = "2343423_syn_5"
text_5 = """procedure note for jamal washington he has an empyema on the left side we did the ultrasound first it showed a lot of loculations thick stuff hyperechoic moderate size. so we went ahead and put in the tpa and dnase 10 and 5 mg into the chest tube on the left. patient tolerated it fine no issues clamped it for an hour chest tube to suction after."""
entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "empyema", 1)},
    {"label": "LATERALITY", **get_span(text_5, "left", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "loculations", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "thick", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "hyperechoic", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "moderate", 1)},
    {"label": "MEDICATION", **get_span(text_5, "tpa", 1)},
    {"label": "MEDICATION", **get_span(text_5, "dnase", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
    {"label": "LATERALITY", **get_span(text_5, "left", 2)},
    {"label": "PROC_ACTION", **get_span(text_5, "clamped", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "an hour", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 2)},
    {"label": "PROC_ACTION", **get_span(text_5, "suction", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2343423_syn_6
# ==========================================
id_6 = "2343423_syn_6"
text_6 = """Jamal Washington 38M with empyema presented for fibrinolytic therapy. Ultrasound of the left chest was performed revealing a moderate hyperechoic effusion with thick loculations. Through the existing left chest tube, 10 mg tPA and 5 mg DNase were instilled for the initial treatment. There were no complications. The tube was clamped for a dwell time of one hour."""
entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "empyema", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Ultrasound", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "chest", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "moderate", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "hyperechoic", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "thick", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "loculations", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left", 2)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
    {"label": "MEDICATION", **get_span(text_6, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_6, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "instilled", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no complications", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "clamped", 1)},
    {"label": "MEAS_TIME", **get_span(text_6, "one hour", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2343423_syn_7
# ==========================================
id_7 = "2343423_syn_7"
text_7 = """[Indication]
Left-sided Empyema requiring fibrinolysis.
[Imaging]
Bedside US Left Chest: Moderate volume, hyperechoic, thick loculations confirmed.
[Description]
Instillation of 10mg tPA and 5mg DNase via existing left chest tube (Initial day).
[Plan]
Clamped for 1 hour, then suction."""
entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "Left", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Empyema", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "US", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Left", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "Chest", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Moderate", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "hyperechoic", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "thick", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "loculations", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Instillation", 1)},
    {"label": "MEDICATION", **get_span(text_7, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_7, "DNase", 1)},
    {"label": "LATERALITY", **get_span(text_7, "left", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Clamped", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "1 hour", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "suction", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2343423_syn_8
# ==========================================
id_8 = "2343423_syn_8"
text_8 = """[REDACTED] ultrasound and fibrinolytic instillation for his left-sided empyema today. The ultrasound examination of the left hemithorax revealed a moderate-sized effusion that appeared hyperechoic with thick internal loculations, confirming the need for therapy. Subsequently, we instilled 10 mg of tPA and 5 mg of DNase through his existing left chest tube without difficulty. He tolerated the procedure well, and the tube was clamped to allow the medication to dwell."""
entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "instillation", 1)},
    {"label": "LATERALITY", **get_span(text_8, "left", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "empyema", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 2)},
    {"label": "LATERALITY", **get_span(text_8, "left", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "hemithorax", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "moderate", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "hyperechoic", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "thick", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "loculations", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "instilled", 1)},
    {"label": "MEDICATION", **get_span(text_8, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_8, "DNase", 1)},
    {"label": "LATERALITY", **get_span(text_8, "left", 3)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "clamped", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dwell", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2343423_syn_9
# ==========================================
id_9 = "2343423_syn_9"
text_9 = """Indication: Empyema.
Scan: Sonographic evaluation of the left thorax displayed a moderate collection with dense septations.
Treatment: Administered 10mg tPA and 5mg DNase through the indwelling left pleural catheter to dissolve loculations.
Outcome: Procedure completed successfully. No adverse events."""
entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "Empyema", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Sonographic", 1)},
    {"label": "LATERALITY", **get_span(text_9, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "thorax", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "moderate", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "collection", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "septations", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Administered", 1)},
    {"label": "MEDICATION", **get_span(text_9, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_9, "DNase", 1)},
    {"label": "LATERALITY", **get_span(text_9, "left", 2)},
    {"label": "DEV_CATHETER", **get_span(text_9, "pleural catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "loculations", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "No adverse events", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 2343423
# ==========================================
id_10 = "2343423"
text_10 = """Date of Service: [REDACTED] 1600 Patient: Washington, Jamal (MRN [REDACTED]) Attending Physician: Van Dyke, Dick, MD Service: Pulmonary / Critical Care 
INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT 1 Happy Street Dr, Hollywood, CA92110
INDICATION FOR OPERATION: Jamal Washington is a 38 year-old male who presents with Empyema. The nature, purpose, risks, benefits and alternatives to Chest Ultrasound and Instillation of agents for fibrinolysis (initial) were discussed with the patient in detail. Patient indicated a wish to proceed with procedure and informed consent was signed. 
PREOPERATIVE DIAGNOSIS: Empyema POSTOPERATIVE DIAGNOSIS: Same as preoperative diagnosis - see above. 
PROCEDURE:
•	76604 Ultrasound, chest (includes mediastinum), real time with image documentation 
•	32561 Instillation(s), via chest tube/catheter, agent for fibrinolysis (eg, fibrinolytic agent for break up of multiloculated effusion); initial day 
ASSISTANT: Emily Torres MD RN: bedside RN Mark O'Conner MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure. 
PROCEDURE IN DETAIL: PATIENT POSITION: ☐ Supine ☑ Sitting ☐ Lateral Decubitus: ☐ Right ☐ Left 
CHEST ULTRASOUND FINDINGS: Hemithorax: ☐ Right ☑ Left Pleural Effusion: ☑ Volume: ☐ None ☐ Minimal ☐ Small ☑ Moderate ☐ Large ☑ Echogenicity: ☐ Anechoic ☐ Hypoechoic ☐ Isoechoic ☑ Hyperechoic ☑ Loculations: ☐ None ☐ Thin ☑ Thick ☑ Diaphragmatic Motion: ☑ Normal ☐ Diminished ☐ Absent 
Lung: Lung sliding before procedure: ☑ Present ☐ Absent Lung consolidation/atelectasis: ☑ Present ☐ Absent Pleura: ☐ Normal ☑ Thick ☐ Nodular 
Date of chest tube insertion: [REDACTED] Side: Left ☑ 10 mg/5 mg tPA/Dnase 
COMPLICATIONS: ☑ None 
IMPRESSION/PLAN: Jamal Washington is a 38 year-old male who presents for Chest Ultrasound and Instillation of agents for fibrinolysis (initial). The patient tolerated the procedure well. There were no immediate complications. DISPOSITION: Nursing Unit [] dwell for 1 hour [] chest tube to suction"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Empyema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Chest", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Instillation", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Empyema", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "chest", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Instillation(s)", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "catheter", 1)},
    {"label": "MEDICATION", **get_span(text_10, "fibrinolytic agent", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "multiloculated", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "CHEST ULTRASOUND", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Hemithorax", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Left", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "Pleural Effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Moderate", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Hyperechoic", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Loculations", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Thick", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lung", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Lung sliding", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "consolidation", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "atelectasis", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleura", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Thick", 2)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 2)},
    {"label": "LATERALITY", **get_span(text_10, "Left", 3)},
    {"label": "MEDICATION", **get_span(text_10, "tPA", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Dnase", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Chest", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "Instillation", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no immediate complications", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "dwell", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "1 hour", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "suction", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)