import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2323422_syn_1
# ==========================================
t1 = """Indication: Complex septated effusion L.
Proc: US Chest + Lytic Instillation.
US: Left side, large volume, isoechoic, thick loculations.
Intervention: 10mg tPA / 5mg DNase via L chest tube.
Result: Tolerated well."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "effusion", 1)},
    {"label": "LATERALITY", **get_span(t1, "L", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "US", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Instillation", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "US", 2)},
    {"label": "LATERALITY", **get_span(t1, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "isoechoic", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "thick loculations", 1)},
    {"label": "MEDICATION", **get_span(t1, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t1, "DNase", 1)},
    {"label": "LATERALITY", **get_span(t1, "L", 2)},
    {"label": "DEV_CATHETER", **get_span(t1, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Tolerated well", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2323422_syn_2
# ==========================================
t2 = """PROCEDURE: Intrapleural administration of fibrinolytic agents with ultrasound guidance.
PATIENT: [REDACTED], 50M.
CLINICAL SUMMARY: The patient presents with a complex septated effusion. Thoracic ultrasound of the left hemithorax demonstrated a large, isoechoic effusion with thick internal septations and diminished diaphragmatic excursion. To address the multiloculated nature of the effusion, 10 mg tPA and 5 mg DNase were instilled via the existing left chest catheter."""

e2 = [
    {"label": "ANAT_PLEURA", **get_span(t2, "Intrapleural", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(t2, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "ultrasound", 2)},
    {"label": "LATERALITY", **get_span(t2, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "hemithorax", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "isoechoic", 1)},
    {"label": "OBS_LESION", **get_span(t2, "effusion", 2)},
    {"label": "OBS_FINDING", **get_span(t2, "thick internal septations", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "diaphragmatic", 1)},
    {"label": "OBS_LESION", **get_span(t2, "effusion", 3)},
    {"label": "MEDICATION", **get_span(t2, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t2, "DNase", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "instilled", 1)},
    {"label": "LATERALITY", **get_span(t2, "left", 2)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest catheter", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2323422_syn_3
# ==========================================
t3 = """Billing Record:
- CPT 76604-26 (US Chest): Left hemithorax scanned. Findings: Large, isoechoic, thick loculations. Image stored.
- CPT 32561 (Fibrinolysis): Instillation of 10mg tPA/5mg DNase via chest tube for complex effusion.
Note: Initial day of therapy."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "US", 1)},
    {"label": "LATERALITY", **get_span(t3, "Left", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "hemithorax", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "isoechoic", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "thick loculations", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Instillation", 1)},
    {"label": "MEDICATION", **get_span(t3, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t3, "DNase", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "chest tube", 1)},
    {"label": "OBS_LESION", **get_span(t3, "effusion", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2323422_syn_4
# ==========================================
t4 = """Resident Note
Patient: [REDACTED]
Procedure: US & Lytic instillation.
Findings:
- Left chest US: Large effusion, really thick septations, isoechoic.
- Diaphragm not moving much.
Action: Put tPA 10 and DNase 5 into the left tube.
Plan: Clamp 1hr."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "US", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "instillation", 1)},
    {"label": "LATERALITY", **get_span(t4, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "US", 2)},
    {"label": "OBS_LESION", **get_span(t4, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "thick septations", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "isoechoic", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "Diaphragm", 1)},
    {"label": "MEDICATION", **get_span(t4, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t4, "DNase", 1)},
    {"label": "LATERALITY", **get_span(t4, "left", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "tube", 1)},
    {"label": "MEAS_TIME", **get_span(t4, "1hr", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2323422_syn_5
# ==========================================
t5 = """sean omalley 50 year old male complex effusion left side. ultrasound showed large fluid collection thick loculations isoechoic. we put the meds in the tube 10 tpa 5 dnase. no issues patient is fine. check him in an hour."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "effusion", 1)},
    {"label": "LATERALITY", **get_span(t5, "left", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "thick loculations", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "isoechoic", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "tube", 1)},
    {"label": "MEDICATION", **get_span(t5, "tpa", 1)},
    {"label": "MEDICATION", **get_span(t5, "dnase", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no issues", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "hour", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2323422_syn_6
# ==========================================
t6 = """[REDACTED] 50M with complex septated left effusion. Ultrasound chest performed left side showing large isoechoic effusion with thick loculations and diminished diaphragmatic motion. Instilled 10 mg tPA and 5 mg DNase via left chest tube. No complications. Dwell time 1 hour."""

e6 = [
    {"label": "LATERALITY", **get_span(t6, "left", 1)},
    {"label": "OBS_LESION", **get_span(t6, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Ultrasound", 1)},
    {"label": "LATERALITY", **get_span(t6, "left", 2)},
    {"label": "OBS_FINDING", **get_span(t6, "isoechoic", 1)},
    {"label": "OBS_LESION", **get_span(t6, "effusion", 2)},
    {"label": "OBS_FINDING", **get_span(t6, "thick loculations", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Instilled", 1)},
    {"label": "MEDICATION", **get_span(t6, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t6, "DNase", 1)},
    {"label": "LATERALITY", **get_span(t6, "left", 3)},
    {"label": "DEV_CATHETER", **get_span(t6, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)},
    {"label": "MEAS_TIME", **get_span(t6, "1 hour", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2323422_syn_7
# ==========================================
t7 = """[Indication]
Complex Septated Effusion (Left).
[Imaging]
US Left Chest: Large, isoechoic, thick loculations.
[Description]
Instillation of 10mg tPA and 5mg DNase via left chest tube.
[Plan]
Suction after 1 hour dwell."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Effusion", 1)},
    {"label": "LATERALITY", **get_span(t7, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "US", 1)},
    {"label": "LATERALITY", **get_span(t7, "Left", 2)},
    {"label": "OBS_FINDING", **get_span(t7, "isoechoic", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "thick loculations", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Instillation", 1)},
    {"label": "MEDICATION", **get_span(t7, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t7, "DNase", 1)},
    {"label": "LATERALITY", **get_span(t7, "left", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "chest tube", 1)},
    {"label": "MEAS_TIME", **get_span(t7, "1 hour", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2323422_syn_8
# ==========================================
t8 = """We evaluated Mr. O'Malley for his complex left-sided effusion. Bedside ultrasound of the left chest was significant for a large volume effusion that was isoechoic with thick loculations, indicating a complex process. We then instilled 10 mg of tPA and 5 mg of DNase into the left chest tube to facilitate drainage. The patient tolerated the procedure without any adverse events."""

e8 = [
    {"label": "LATERALITY", **get_span(t8, "left", 1)},
    {"label": "OBS_LESION", **get_span(t8, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "ultrasound", 1)},
    {"label": "LATERALITY", **get_span(t8, "left", 2)},
    {"label": "OBS_LESION", **get_span(t8, "effusion", 2)},
    {"label": "OBS_FINDING", **get_span(t8, "isoechoic", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "thick loculations", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "instilled", 1)},
    {"label": "MEDICATION", **get_span(t8, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t8, "DNase", 1)},
    {"label": "LATERALITY", **get_span(t8, "left", 3)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "without any adverse events", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2323422_syn_9
# ==========================================
t9 = """Indication: Multiloculated Effusion.
Visualization: Ultrasonic assessment of the left thorax showed a large, septated collection.
Treatment: Administered 10mg tPA and 5mg DNase through the left pleural drain.
Outcome: Completed without incident."""

e9 = [
    {"label": "OBS_LESION", **get_span(t9, "Effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Ultrasonic", 1)},
    {"label": "LATERALITY", **get_span(t9, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "thorax", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "septated", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Administered", 1)},
    {"label": "MEDICATION", **get_span(t9, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t9, "DNase", 1)},
    {"label": "LATERALITY", **get_span(t9, "left", 2)},
    {"label": "DEV_CATHETER", **get_span(t9, "pleural drain", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "without incident", 1)},
]
BATCH_DATA.append({"id": "2323422_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2323422
# ==========================================
t10 = """Date of Service: [REDACTED] 0845 Patient: O'Malley, Sean (MRN [REDACTED]) Attending Physician: Miller, Russell J, MD Service: Pulmonary / Critical Care 
INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT 1 Happy Street Dr, Hollywood, CA92110
INDICATION FOR OPERATION: Sean O'Malley is a 50 year-old male who presents with Complex Septated Effusion. The nature, purpose, risks, benefits and alternatives to Chest Ultrasound and Instillation of agents for fibrinolysis (initial) were discussed with the patient in detail. Patient indicated a wish to proceed with procedure and informed consent was signed. 
PREOPERATIVE DIAGNOSIS: Complex Septated Effusion POSTOPERATIVE DIAGNOSIS: Same as preoperative diagnosis - see above. 
PROCEDURE:
• 76604 Ultrasound, chest (includes mediastinum), real time with image documentation 
• 32561 Instillation(s), via chest tube/catheter, agent for fibrinolysis (eg, fibrinolytic agent for break up of multiloculated effusion); initial day 
ASSISTANT: Rebecca Lin MD RN: bedside RN Thomas Anderson MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure. 
PROCEDURE IN DETAIL: PATIENT POSITION: ☑ Supine ☐ Sitting ☐ Lateral Decubitus: ☐ Right ☐ Left 
CHEST ULTRASOUND FINDINGS: Hemithorax: ☐ Right ☑ Left Pleural Effusion: ☑ Volume: ☐ None ☐ Minimal ☐ Small ☐ Moderate ☑ Large ☑ Echogenicity: ☐ Anechoic ☐ Hypoechoic ☑ Isoechoic ☐ Hyperechoic ☑ Loculations: ☐ None ☐ Thin ☑ Thick ☑ Diaphragmatic Motion: ☐ Normal ☑ Diminished ☐ Absent 
Lung: Lung sliding before procedure: ☑ Present ☐ Absent Lung consolidation/atelectasis: ☑ Present ☐ Absent Pleura: ☐ Normal ☑ Thick ☐ Nodular 
Date of chest tube insertion: [REDACTED] Side: Left ☑ 10 mg/5 mg tPA/Dnase 
COMPLICATIONS: ☑ None 
IMPRESSION/PLAN: Sean O'Malley is a 50 year-old male who presents for Chest Ultrasound and Instillation of agents for fibrinolysis (initial). The patient tolerated the procedure well. There were no immediate complications. DISPOSITION: Nursing Unit [] dwell for 1 hour [] chest tube to suction"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Effusion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Chest", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Instillation", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Effusion", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "Instillation", 2)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "OBS_LESION", **get_span(t10, "effusion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Hemithorax", 1)},
    {"label": "LATERALITY", **get_span(t10, "Left", 2)},
    {"label": "OBS_LESION", **get_span(t10, "Pleural Effusion", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Isoechoic", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Loculations", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Thick", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Diaphragmatic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lung", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Pleura", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 2)},
    {"label": "LATERALITY", **get_span(t10, "Left", 3)},
    {"label": "MEDICATION", **get_span(t10, "tPA", 1)},
    {"label": "MEDICATION", **get_span(t10, "Dnase", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "None", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "Instillation", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no immediate complications", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "1 hour", 1)},
]
BATCH_DATA.append({"id": "2323422", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)