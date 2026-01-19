import sys
from pathlib import Path

# Set the repository root (assuming script is running from within the repo structure)
# Adjust this logic if the script location differs in your specific environment
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function for adding cases
# Ensure 'scripts/add_training_case.py' exists in your path or adjust import
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is running in the correct environment.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Case 1: 44521901
# ==========================================
id_1 = "44521901"
text_1 = """Date of Service: [REDACTED] 0930 Patient: Henderson, Mark (MRN [REDACTED]) Attending Physician: Van Dyke, Dick, MD Service: Pulmonary / Critical Care 

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT 1 Happy Street Dr, Hollywood, CA92110
INDICATION FOR OPERATION: Mark Henderson is a 62 year-old male who presents with Complicated Parapneumonic Effusion. The nature, purpose, risks, benefits and alternatives to Chest Ultrasound and Instillation of agents for fibrinolysis (initial) were discussed with the patient in detail. Patient indicated a wish to proceed with procedure and informed consent was signed. 

PREOPERATIVE DIAGNOSIS: Complicated Parapneumonic Effusion POSTOPERATIVE DIAGNOSIS: Same as preoperative diagnosis - see above. 
PROCEDURE:

76604 Ultrasound, chest (includes mediastinum), real time with image documentation 

32561 Instillation(s), via chest tube/catheter, agent for fibrinolysis (eg, fibrinolytic agent for break up of multiloculated effusion); initial day 

ASSISTANT: Sarah Chen MD RN: bedside RN David Miller MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure. 
PROCEDURE IN DETAIL: PATIENT POSITION: ☐ Supine ☑ Sitting ☐ Lateral Decubitus: ☐ Right ☐ Left 
CHEST ULTRASOUND FINDINGS: Hemithorax: ☑ Right ☐ Left Pleural Effusion: ☑ Volume: ☐ None ☐ Minimal ☐ Small ☑ Moderate ☐ Large ☑ Echogenicity: ☐ Anechoic ☐ Hypoechoic ☑ Isoechoic ☐ Hyperechoic ☑ Loculations: ☐ None ☐ Thin ☑ Thick ☑ Diaphragmatic Motion: ☑ Normal ☐ Diminished ☐ Absen
Lung: Lung sliding before procedure: ☑ Present ☐ Absent Lung consolidation/atelectasis: ☑ Present ☐ Absent Pleura: ☐ Normal ☑ Thick ☐ Nodular
Date of chest tube insertion: [REDACTED] Side: Right ☑ 10 mg/5 mg tPA/Dnase 
COMPLICATIONS: ☑ None 
IMPRESSION/PLAN: Mark Henderson is a 62 year-old male who presents for Chest Ultrasound and Instillation of agents for fibrinolysis (initial).  The patient tolerated the procedure well. There were no immediate complications. DISPOSITION: Nursing Unit [] dwell for 1 hour [] chest tube to suction"""

entities_1 = [
    # "Complicated Parapneumonic Effusion"
    {"label": "OBS_FINDING", **get_span(text_1, "Effusion", 1)},
    
    # "Chest Ultrasound" (Indication)
    {"label": "PROC_METHOD", **get_span(text_1, "Chest Ultrasound", 1)},
    
    # "Instillation" (Indication)
    {"label": "PROC_ACTION", **get_span(text_1, "Instillation", 1)},
    
    # "Ultrasound, chest" (Procedure list)
    {"label": "PROC_METHOD", **get_span(text_1, "Ultrasound, chest", 1)},
    
    # "Instillation" (Procedure list)
    {"label": "PROC_ACTION", **get_span(text_1, "Instillation", 2)},
    
    # "chest tube" (Procedure list - "via chest tube/catheter")
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    
    # "catheter" (Procedure list - "via chest tube/catheter")
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 1)},
    
    # "Right" (Hemithorax: ☑ Right)
    # Note: 1st "Right" is in 'Lateral Decubitus: Right' (unchecked). 2nd is 'Hemithorax: Right'.
    {"label": "LATERALITY", **get_span(text_1, "Right", 2)},
    
    # "Pleural Effusion" (Findings)
    {"label": "ANAT_PLEURA", **get_span(text_1, "Pleural", 1)},
    # Note: 1: Indication, 2: Preop, 3: Findings. The 'effusion' in procedure list is lowercase.
    {"label": "OBS_FINDING", **get_span(text_1, "Effusion", 3)}, 
    
    # "Isoechoic" (Echogenicity)
    {"label": "OBS_FINDING", **get_span(text_1, "Isoechoic", 1)},
    
    # "Loculations"
    {"label": "OBS_FINDING", **get_span(text_1, "Loculations", 1)},
    
    # "Thick" (Loculations)
    {"label": "OBS_FINDING", **get_span(text_1, "Thick", 1)},
    
    # "Lung" (Header)
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Lung", 1)},
    
    # "Lung" (Lung sliding) - Contextual, usually skip strictly unless target, but 'Lung' is ANAT_LUNG_LOC
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Lung", 2)},
    
    # "consolidation"
    {"label": "OBS_FINDING", **get_span(text_1, "consolidation", 1)},
    
    # "atelectasis"
    {"label": "OBS_FINDING", **get_span(text_1, "atelectasis", 1)},
    
    # "Pleura"
    {"label": "ANAT_PLEURA", **get_span(text_1, "Pleura", 1)},
    
    # "Thick" (Pleura)
    {"label": "OBS_FINDING", **get_span(text_1, "Thick", 2)},
    
    # "chest tube" (Date of insertion)
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 2)},
    
    # "Right" (Side: Right)
    # Note: 1: Patient pos, 2: Hemithorax, 3: Side
    {"label": "LATERALITY", **get_span(text_1, "Right", 3)},
    
    # "tPA"
    {"label": "MEDICATION", **get_span(text_1, "tPA", 1)},
    
    # "Dnase"
    {"label": "MEDICATION", **get_span(text_1, "Dnase", 1)},
    
    # "None" (Complications)
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 3)}, # 1: Volume None, 2: Loculations None, 3: Complications None
    
    # "Chest Ultrasound" (Impression)
    {"label": "PROC_METHOD", **get_span(text_1, "Chest Ultrasound", 2)},
    
    # "Instillation" (Impression)
    {"label": "PROC_ACTION", **get_span(text_1, "Instillation", 3)},
    
    # "chest tube" (Disposition)
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 3)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)