import sys
from pathlib import Path

# Set up the repository root (assuming script is run from a subfolder or root)
# Adjust this logic based on actual repo structure if needed
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running standalone for testing
    print("Warning: Could not import 'add_case'. Ensure you are in the correct repo structure.")
    def add_case(case_id, text, entities, root):
        print(f"Would process {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 1812736_syn_1
# ==========================================
t1 = """Procedure: Bedside Pleurodesis.
- Access: Existing chest tube.
- Agent: 4g Talc slurry + 200mg Lidocaine.
- Method: Instill -> Clamp -> Rotate.
- Result: Tolerated well.
- Plan: Suction, remove tube in 48h."""

e1 = [
    {"label": "PROC_ACTION", **get_span(t1, "Pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "chest tube", 1)},
    {"label": "MEDICATION", **get_span(t1, "Talc", 1)},
    {"label": "MEDICATION", **get_span(t1, "Lidocaine", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Instill", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Clamp", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Rotate", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t1, "Tolerated well", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Suction", 1)},
    {"label": "CTX_TIME", **get_span(t1, "48h", 1)},
]
BATCH_DATA.append({"id": "1812736_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1812736_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: Chemical pleurodesis was performed via the existing right-sided chest tube. After confirmation of lung re-expansion and lidocaine premedication, a slurry containing 4 grams of sterile talc was instilled. The patient was rotated through standard positions to ensure distribution. The tube was unclamped after 60 minutes."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "Chemical pleurodesis", 1)},
    {"label": "LATERALITY", **get_span(t2, "right-sided", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t2, "lung re-expansion", 1)},
    {"label": "MEDICATION", **get_span(t2, "lidocaine", 1)},
    {"label": "MEDICATION", **get_span(t2, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "instilled", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "rotated", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "unclamped", 1)},
    {"label": "CTX_TIME", **get_span(t2, "60 minutes", 1)},
]
BATCH_DATA.append({"id": "1812736_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1812736_syn_3
# ==========================================
t3 = """Code: 32560 (Pleurodesis instillation). Agent: Talc. Route: Chest tube. Pre-medication: Lidocaine intrapleural. Indication: Malignant effusion."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Pleurodesis instillation", 1)},
    {"label": "MEDICATION", **get_span(t3, "Talc", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "Chest tube", 1)},
    {"label": "MEDICATION", **get_span(t3, "Lidocaine", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Malignant effusion", 1)},
]
BATCH_DATA.append({"id": "1812736_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1812736_syn_4
# ==========================================
t4 = """Procedure: Talc Pleurodesis
1. Checked CXR - lung up.
2. Pushed lidocaine into chest tube.
3. Pushed talc slurry (4g).
4. Clamped and rotated patient x 1 hour.
5. Back to suction.
Plan: Watch drainage."""

e4 = [
    {"label": "MEDICATION", **get_span(t4, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Pleurodesis", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t4, "lung up", 1)},
    {"label": "MEDICATION", **get_span(t4, "lidocaine", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "chest tube", 1)},
    {"label": "MEDICATION", **get_span(t4, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Clamped", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "rotated", 1)},
    {"label": "CTX_TIME", **get_span(t4, "1 hour", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "suction", 1)},
]
BATCH_DATA.append({"id": "1812736_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1812736_syn_5
# ==========================================
t5 = """bedside pleurodesis for rebecca martinez. she has that cancer effusion. lung was up so we put in lidocaine then the talc slurry. rolled her around for an hour. put the tube back on suction. she had some pain but morphine helped."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "bedside pleurodesis", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 1)},
    {"label": "OBS_LESION", **get_span(t5, "effusion", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t5, "lung was up", 1)},
    {"label": "MEDICATION", **get_span(t5, "lidocaine", 1)},
    {"label": "MEDICATION", **get_span(t5, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "rolled", 1)},
    {"label": "CTX_TIME", **get_span(t5, "an hour", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "tube", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "suction", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t5, "pain", 1)},
    {"label": "MEDICATION", **get_span(t5, "morphine", 1)},
]
BATCH_DATA.append({"id": "1812736_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1812736_syn_6
# ==========================================
t6 = """Chemical pleurodesis with talc slurry via chest tube was performed. The patient has a recurrent malignant pleural effusion. Lidocaine was administered followed by 4 grams of talc slurry. The patient was repositioned for distribution. The tube was unclamped after 60 minutes. The patient tolerated the procedure reasonably well."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Chemical pleurodesis", 1)},
    {"label": "MEDICATION", **get_span(t6, "talc", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "chest tube", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t6, "recurrent", 1)},
    {"label": "OBS_LESION", **get_span(t6, "malignant pleural effusion", 1)},
    {"label": "MEDICATION", **get_span(t6, "Lidocaine", 1)},
    {"label": "MEDICATION", **get_span(t6, "talc", 2)},
    {"label": "PROC_ACTION", **get_span(t6, "repositioned", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "tube", 2)},
    {"label": "PROC_ACTION", **get_span(t6, "unclamped", 1)},
    {"label": "CTX_TIME", **get_span(t6, "60 minutes", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t6, "tolerated the procedure reasonably well", 1)},
]
BATCH_DATA.append({"id": "1812736_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1812736_syn_7
# ==========================================
t7 = """[Indication]
Malignant Pleural Effusion.
[Anesthesia]
Local/Intrapleural Lidocaine.
[Description]
4g Talc slurry instilled via chest tube. Patient rotated. Suction resumed.
[Plan]
Remove tube when drainage decreases."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Malignant Pleural Effusion", 1)},
    {"label": "MEDICATION", **get_span(t7, "Lidocaine", 1)},
    {"label": "MEDICATION", **get_span(t7, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "instilled", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "rotated", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Suction", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Remove", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "tube", 2)},
]
BATCH_DATA.append({"id": "1812736_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1812736_syn_8
# ==========================================
t8 = """[REDACTED] a bedside pleurodesis to treat her recurring pleural fluid. Since her lung was fully expanded, we injected a mixture of talc and saline through her chest tube. We had her change positions for an hour to coat the lining of the lung. She experienced some discomfort but is comfortable now. We'll leave the tube in for a couple of days to make sure the lung sticks."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "bedside pleurodesis", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t8, "recurring", 1)},
    {"label": "OBS_LESION", **get_span(t8, "pleural fluid", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t8, "lung was fully expanded", 1)},
    {"label": "MEDICATION", **get_span(t8, "talc", 1)},
    {"label": "MEDICATION", **get_span(t8, "saline", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "change positions", 1)},
    {"label": "CTX_TIME", **get_span(t8, "an hour", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t8, "discomfort", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t8, "comfortable", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "tube", 2)},
]
BATCH_DATA.append({"id": "1812736_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1812736_syn_9
# ==========================================
t9 = """Procedure: Chemical sclerosis of pleural space.
Agent: Talc suspension.
Method: Instillation via thoracostomy tube with positional rotation.
Goal: Pleural symphysis."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Chemical sclerosis", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "pleural space", 1)},
    {"label": "MEDICATION", **get_span(t9, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Instillation", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "thoracostomy tube", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "rotation", 1)},
]
BATCH_DATA.append({"id": "1812736_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1812736
# ==========================================
t10 = """Name: [REDACTED]
Age/Sex: 68/Female
MRN: [REDACTED]
Date: [REDACTED]
Location: [REDACTED]
Attending Physician: Dr. Thomas Anderson
Indication: Recurrent malignant pleural effusion (metastatic ovarian cancer), right-sided, despite optimal drainage via chest tube
Background: Patient has had 28Fr chest tube in place for 5 days. Initial drainage was 1400mL, then decreased to <100mL/day for the past 48 hours. CXR today shows good lung expansion with only minimal residual pleural fluid. No air leak present. Patient is appropriate candidate for pleurodesis.
Consent: Obtained from patient. Risks discussed include chest pain/discomfort, fever, respiratory distress (rare), failure of pleurodesis requiring repeat procedure.
Premedication:

Morphine 4mg IV given 30 minutes prior
Acetaminophen 1000mg PO given 1 hour prior
Ondansetron 4mg IV given for nausea prophylaxis


PROCEDURE STEPS:
Step 1 - Verification (Time: 14:00)

Verified chest tube patency by flushing with 10mL sterile saline
Confirmed no air leak on water seal
Reviewed most recent CXR with radiologist - confirmed adequate lung expansion

Step 2 - Lidocaine Administration (Time: 14:05)

Drew up 20mL of 1% lidocaine (200mg total)
Administered through chest tube slowly over 2 minutes
Clamped tube for 5 minutes to allow lidocaine to distribute
Released clamp, allowed to drain

Step 3 - Talc Slurry Preparation (Time: 14:15)

Prepared sterile talc slurry: 4 grams talc powder in 50mL normal saline
Mixed thoroughly in sterile cup until uniform suspension achieved
Drew up into 60mL catheter tip syringe

Step 4 - Talc Administration (Time: 14:20)

Slowly instilled talc slurry through chest tube over 5 minutes
Followed with 20mL normal saline flush to ensure complete delivery
Immediately clamped chest tube

Step 5 - Position Changes (Time: 14:25 - 15:25)
Patient [REDACTED] positions every 15 minutes to distribute talc:

Position 1 (14:25): Supine - 15 minutes
Position 2 (14:40): Right lateral decubitus - 15 minutes
Position 3 (14:55): Prone (as tolerated) - 10 minutes
Position 4 (15:05): Left lateral decubitus - 15 minutes
Position 5 (15:20): Return to supine - 5 minutes

Total dwell time: 60 minutes
Step 6 - Resumption of Drainage (Time: 15:25)

Released clamp on chest tube
Connected back to suction at -20 cmH2O
Immediate return of approximately 30mL serosanguineous fluid


PATIENT [REDACTED]:
During procedure:

Vital signs stable throughout
Complained of moderate chest discomfort (5/10) during position changes
Received additional morphine 2mg IV at 14:50
No respiratory distress
Oxygen saturation maintained >94% on 2L NC

Post-procedure (2 hours observation):

Chest discomfort decreased to 3/10
No fever (temp 37.2°C)
No dyspnea
Chest tube draining serosanguineous fluid, approximately 50mL total since unclamping

SPECIMENS: None
COMPLICATIONS: None
POST-PROCEDURE ORDERS:

Continue chest tube to suction -20 cmH2O
Monitor drainage every 4 hours
Pain control: Morphine 2-4mg IV q4h PRN, acetaminophen 650mg PO q6h scheduled
Chest X-ray in AM
If drainage <150mL over next 24 hours AND CXR shows no reaccumulation, consider chest tube removal in 48-72 hours

ASSESSMENT: Chemical pleurodesis with talc slurry via chest tube completed successfully without complications. Patient tolerated procedure reasonably well with adequate pain control. Will monitor for pleurodesis efficacy over next several days.
Follow-up Plan:

Daily CXR while chest tube in place
Remove chest tube when drainage criteria met (typically 2-3 days)
Follow-up CXR 1 week after chest tube removal
If recurrent effusion develops, may consider PleurX catheter placement"""

e10 = [
    {"label": "CTX_HISTORICAL", **get_span(t10, "Recurrent", 1)},
    {"label": "OBS_LESION", **get_span(t10, "malignant pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(t10, "metastatic ovarian cancer", 1)},
    {"label": "LATERALITY", **get_span(t10, "right-sided", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t10, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 2)},
    {"label": "CTX_TIME", **get_span(t10, "5 days", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "1400mL", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "100mL", 1)},
    {"label": "CTX_TIME", **get_span(t10, "48 hours", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t10, "good lung expansion", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "pleural fluid", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "air leak", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "pleurodesis", 1)},
    {"label": "MEDICATION", **get_span(t10, "Morphine", 1)},
    {"label": "MEDICATION", **get_span(t10, "Acetaminophen", 1)},
    {"label": "MEDICATION", **get_span(t10, "Ondansetron", 1)},
    {"label": "CTX_TIME", **get_span(t10, "14:00", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 3)},
    {"label": "MEAS_VOL", **get_span(t10, "10mL", 1)},
    {"label": "MEDICATION", **get_span(t10, "sterile saline", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "air leak", 2)},
    {"label": "OUTCOME_PLEURAL", **get_span(t10, "adequate lung expansion", 1)},
    {"label": "CTX_TIME", **get_span(t10, "14:05", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "20mL", 1)},
    {"label": "MEDICATION", **get_span(t10, "lidocaine", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 4)},
    {"label": "MEAS_TIME", **get_span(t10, "2 minutes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Clamped", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "tube", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "5 minutes", 1)},
    {"label": "MEDICATION", **get_span(t10, "lidocaine", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "Released", 1)},
    {"label": "CTX_TIME", **get_span(t10, "14:15", 1)},
    {"label": "MEDICATION", **get_span(t10, "talc", 1)},
    {"label": "MEDICATION", **get_span(t10, "talc", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "50mL", 1)},
    {"label": "MEDICATION", **get_span(t10, "normal saline", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "catheter tip syringe", 1)},
    {"label": "CTX_TIME", **get_span(t10, "14:20", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "instilled", 1)},
    {"label": "MEDICATION", **get_span(t10, "talc", 3)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 5)},
    {"label": "MEAS_TIME", **get_span(t10, "5 minutes", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "20mL", 2)},
    {"label": "MEDICATION", **get_span(t10, "normal saline", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "clamped", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 6)},
    {"label": "CTX_TIME", **get_span(t10, "14:25 - 15:25", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "15 minutes", 1)},
    {"label": "MEDICATION", **get_span(t10, "talc", 4)},
    {"label": "CTX_TIME", **get_span(t10, "14:25", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "15 minutes", 2)},
    {"label": "CTX_TIME", **get_span(t10, "14:40", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "15 minutes", 3)},
    {"label": "CTX_TIME", **get_span(t10, "14:55", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "10 minutes", 1)},
    {"label": "CTX_TIME", **get_span(t10, "15:05", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "15 minutes", 4)},
    {"label": "CTX_TIME", **get_span(t10, "15:20", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "5 minutes", 3)},
    {"label": "CTX_TIME", **get_span(t10, "60 minutes", 1)},
    {"label": "CTX_TIME", **get_span(t10, "15:25", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Released", 2)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 7)},
    {"label": "PROC_ACTION", **get_span(t10, "suction", 1)},
    {"label": "MEAS_PRESS", **get_span(t10, "-20 cmH2O", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "30mL", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "serosanguineous fluid", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "chest discomfort", 1)},
    {"label": "MEDICATION", **get_span(t10, "morphine", 1)},
    {"label": "CTX_TIME", **get_span(t10, "14:50", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "respiratory distress", 2)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "Chest discomfort", 1)},
    {"label": "MEAS_TEMP", **get_span(t10, "37.2°C", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "dyspnea", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "serosanguineous fluid", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "50mL", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "unclamping", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 8)},
    {"label": "PROC_ACTION", **get_span(t10, "suction", 2)},
    {"label": "MEAS_PRESS", **get_span(t10, "-20 cmH2O", 2)},
    {"label": "MEDICATION", **get_span(t10, "Morphine", 2)},
    {"label": "MEDICATION", **get_span(t10, "acetaminophen", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "150mL", 1)},
    {"label": "CTX_TIME", **get_span(t10, "24 hours", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 9)},
    {"label": "PROC_ACTION", **get_span(t10, "removal", 1)},
    {"label": "CTX_TIME", **get_span(t10, "48-72 hours", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Chemical pleurodesis", 1)},
    {"label": "MEDICATION", **get_span(t10, "talc", 5)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 10)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "tolerated procedure reasonably well", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 11)},
    {"label": "PROC_ACTION", **get_span(t10, "Remove", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 12)},
    {"label": "CTX_TIME", **get_span(t10, "2-3 days", 1)},
    {"label": "CTX_TIME", **get_span(t10, "1 week", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 13)},
    {"label": "OBS_LESION", **get_span(t10, "recurrent effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "PleurX catheter", 1)},
]
BATCH_DATA.append({"id": "1812736", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)