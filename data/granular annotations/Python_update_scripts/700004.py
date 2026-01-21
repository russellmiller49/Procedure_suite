import sys
from pathlib import Path

# Set up the repository root assuming this script is inside 'scripts/'
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 700004_syn_1
# ==========================================
t1 = """Dx: R empyema.
Proc: US Thora + Chest Tube.
Steps:
- US loculated fluid.
- 40mL asp for labs.
- 28Fr chest tube placed 6th ICS.
- 900mL purulent output.
Plan: ICU, antibiotics, consider TPA/DNAse."""
e1 = [
    {"label": "LATERALITY", **get_span(t1, "R", 1)},
    {"label": "OBS_LESION", **get_span(t1, "empyema", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "US", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Thora", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Chest Tube", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "US", 2)},
    {"label": "OBS_FINDING", **get_span(t1, "loculated", 1)},
    {"label": "SPECIMEN", **get_span(t1, "fluid", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "40mL", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "asp", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t1, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "chest tube", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "6th ICS", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "purulent", 1)}
]
BATCH_DATA.append({"id": "700004_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 700004_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: Ultrasound-guided thoracentesis and large-bore chest tube insertion.
PATIENT: [REDACTED], 56M, with complex parapneumonic effusion.
DETAILS: Under real-time ultrasound guidance, diagnostic aspiration confirmed turbid fluid. Subsequently, a 28 Fr tube thoracostomy was performed using the Seldinger technique via a separate incision. Immediate return of 900 mL of purulent fluid confirmed the diagnosis of empyema. Post-procedure imaging ordered."""
e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "thoracentesis", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest tube", 1)},
    {"label": "OBS_LESION", **get_span(t2, "complex parapneumonic effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "aspiration", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "turbid", 1)},
    {"label": "SPECIMEN", **get_span(t2, "fluid", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t2, "28 Fr", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "tube thoracostomy", 1)},
    {"label": "MEAS_VOL", **get_span(t2, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "purulent", 1)},
    {"label": "SPECIMEN", **get_span(t2, "fluid", 2)},
    {"label": "OBS_LESION", **get_span(t2, "empyema", 1)}
]
BATCH_DATA.append({"id": "700004_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 700004_syn_3
# ==========================================
t3 = """Codes:
- 32555: Thoracentesis with imaging guidance (diagnostic/therapeutic).
- 32551: Tube thoracostomy (separate incision/site).
Medical Necessity: Septated empyema requiring large-bore drainage. Ultrasound essential for safe localization."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Thoracentesis", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "imaging guidance", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Tube thoracostomy", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "Septated", 1)},
    {"label": "OBS_LESION", **get_span(t3, "empyema", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Ultrasound", 1)}
]
BATCH_DATA.append({"id": "700004_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 700004_syn_4
# ==========================================
t4 = """Procedure: Chest Tube Placement
Patient: [REDACTED]
Indication: Empyema
Steps:
1. US localization.
2. Diagnostic tap (19G): turbid fluid.
3. 28Fr chest tube placed (Seldinger).
4. Sutured, sterile dressing.
5. Output: 900mL purulent.
Complications: None."""
e4 = [
    {"label": "DEV_CATHETER", **get_span(t4, "Chest Tube", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Empyema", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "US", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Diagnostic tap", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "19G", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "turbid", 1)},
    {"label": "SPECIMEN", **get_span(t4, "fluid", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t4, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "chest tube", 1)},
    {"label": "MEAS_VOL", **get_span(t4, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "purulent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "None", 1)}
]
BATCH_DATA.append({"id": "700004_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 700004_syn_5
# ==========================================
t5 = """Bedside procedure for [REDACTED] ICU he has that loculated effusion right side. Used ultrasound to find a pocket. Numbed him up tapped it got pus so we went ahead and put in a chest tube. 28 french big tube. Drained about 900 cc of nasty looking fluid. Hooked to suction he tolerated it fine."""
e5 = [
    {"label": "OBS_FINDING", **get_span(t5, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(t5, "effusion", 1)},
    {"label": "LATERALITY", **get_span(t5, "right side", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "tapped", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "pus", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t5, "28 french", 1)},
    {"label": "MEAS_VOL", **get_span(t5, "900 cc", 1)},
    {"label": "SPECIMEN", **get_span(t5, "fluid", 1)}
]
BATCH_DATA.append({"id": "700004_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 700004_syn_6
# ==========================================
t6 = """Ultrasound-guided diagnostic thoracentesis followed by 28 Fr chest tube insertion for right-sided empyema. 40 mL aspirated for analysis; 900 mL purulent fluid drained via tube. No complications. Patient remains in ICU on vasopressors."""
e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "thoracentesis", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t6, "28 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "chest tube", 1)},
    {"label": "LATERALITY", **get_span(t6, "right-sided", 1)},
    {"label": "OBS_LESION", **get_span(t6, "empyema", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "40 mL", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "aspirated", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "purulent", 1)},
    {"label": "SPECIMEN", **get_span(t6, "fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)}
]
BATCH_DATA.append({"id": "700004_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 700004_syn_7
# ==========================================
t7 = """[Indication]
Right complex parapneumonic effusion/empyema.
[Anesthesia]
Local (Lidocaine).
[Description]
US-guided aspiration of pleural space. Placement of 28 Fr chest tube. Drainage of 900 mL purulent fluid.
[Plan]
Suction -20cmH2O, antibiotics, repeat imaging."""
e7 = [
    {"label": "LATERALITY", **get_span(t7, "Right", 1)},
    {"label": "OBS_LESION", **get_span(t7, "complex parapneumonic effusion", 1)},
    {"label": "OBS_LESION", **get_span(t7, "empyema", 1)},
    {"label": "MEDICATION", **get_span(t7, "Lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "US", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "aspiration", 1)},
    {"label": "ANAT_PLEURA", **get_span(t7, "pleural space", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t7, "28 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "chest tube", 1)},
    {"label": "MEAS_VOL", **get_span(t7, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "purulent", 1)},
    {"label": "SPECIMEN", **get_span(t7, "fluid", 1)},
    {"label": "MEAS_PRESS", **get_span(t7, "-20cmH2O", 1)}
]
BATCH_DATA.append({"id": "700004_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 700004_syn_8
# ==========================================
t8 = """We performed a bedside procedure for [REDACTED] his right-sided empyema. Using ultrasound, we first performed a diagnostic thoracentesis to confirm the nature of the fluid. Upon seeing turbid fluid, we proceeded to place a large-bore 28 French chest tube. This immediately drained nearly a liter of purulent fluid. The tube was secured, and a follow-up chest x-ray was ordered."""
e8 = [
    {"label": "LATERALITY", **get_span(t8, "right-sided", 1)},
    {"label": "OBS_LESION", **get_span(t8, "empyema", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "thoracentesis", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "turbid", 1)},
    {"label": "SPECIMEN", **get_span(t8, "fluid", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t8, "28 French", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "purulent", 1)},
    {"label": "SPECIMEN", **get_span(t8, "fluid", 2)}
]
BATCH_DATA.append({"id": "700004_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 700004_syn_9
# ==========================================
t9 = """Procedure: Sonographic-guided pleural aspiration and thoracostomy.
Indication: Pyothorax.
Action: The pleural space was accessed under imaging. Fluid was withdrawn for testing. A drainage catheter (28 Fr) was inserted. Purulent effusion was evacuated.
Outcome: Lung re-expansion pending imaging."""
e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Sonographic", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "pleural aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "thoracostomy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Pyothorax", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "pleural space", 1)},
    {"label": "SPECIMEN", **get_span(t9, "Fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "drainage catheter", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t9, "28 Fr", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Purulent", 1)},
    {"label": "OBS_LESION", **get_span(t9, "effusion", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t9, "Lung re-expansion", 1)}
]
BATCH_DATA.append({"id": "700004_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 700004
# ==========================================
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
AGE: 56 years
DATE OF PROCEDURE: [REDACTED]
LOCATION: [REDACTED]

PRE-OP DIAGNOSIS: Right parapneumonic effusion with suspected empyema.
POST-OP DIAGNOSIS: Same.

PROCEDURES:
1. Ultrasound-guided diagnostic and therapeutic right thoracentesis.
2. Insertion of right large-bore chest tube for ongoing drainage.

OPERATOR: Emily Rogers, MD (Pulmonary/Critical Care)
ASSISTANT: ICU Resident PGY-2

INDICATION:
56-year-old male with severe community-acquired pneumonia and enlarging right pleural effusion with loculations and fevers despite antibiotics. Ultrasound reveals complex septated effusion. Bedside thoracentesis for diagnosis followed by chest tube for continued drainage.

ULTRASOUND-GUIDED THORACENTESIS:
The patient was positioned sitting upright. Right posterolateral chest was prepped and draped in sterile fashion. Ultrasound id[REDACTED] a moderate, complex right pleural effusion with diaphragmatic excursion and no obvious lung entrapment. A safe window in the right posterior axillary line at the 8th intercostal space was chosen.

Local anesthesia with 1% lidocaine was infiltrated down to the pleura. A 19G needle with catheter was advanced above the rib under real-time ultrasound guidance into the pleural space with return of turbid, yellow fluid. Approximately 40 mL of fluid was aspirated for diagnostic studies (chemistry, cell count, Gram stain/culture, cytology, pH, LDH, glucose).

CHEST TUBE INSERTION:
Given the thick, loculated nature of the effusion and sepsis, a decision was made to place a large-bore chest tube. A 28 Fr straight chest tube was inserted via a separate incision at the mid-axillary line in the 6th intercostal space using blunt dissection and Seldinger technique into the posterolateral collection. The tube was secured with sutures and connected to -20 cm H2O suction.

Initial drainage was approximately 900 mL of turbid, malodorous fluid. The patient tolerated the procedure without hypotension or significant desaturation. Post-procedure ultrasound confirmed lung expansion, and a CXR was ordered to confirm position and evaluate for complications.

COMPLICATIONS:
No immediate pneumothorax, bleeding, or organ injury was observed.

DISPOSITION:
Patient [REDACTED] the ICU on existing vasopressor and ventilator settings. Plan for intrapleural fibrinolytics if imaging shows persistent loculations.

IMPRESSION:
Successful ultrasound-guided right thoracentesis with large-volume purulent fluid removal and placement of a large-bore right chest tube for ongoing drainage of presumed empyema."""
e10 = [
    {"label": "LATERALITY", **get_span(t10, "Right", 1)},
    {"label": "OBS_LESION", **get_span(t10, "parapneumonic effusion", 1)},
    {"label": "OBS_LESION", **get_span(t10, "empyema", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "thoracentesis", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 2)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 3)},
    {"label": "OBS_LESION", **get_span(t10, "pleural effusion", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "loculations", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "septated", 1)},
    {"label": "OBS_LESION", **get_span(t10, "effusion", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "thoracentesis", 2)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 2)},
    {"label": "LATERALITY", **get_span(t10, "Right", 2)},
    {"label": "ANAT_PLEURA", **get_span(t10, "posterolateral chest", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ultrasound", 3)},
    {"label": "LATERALITY", **get_span(t10, "right", 4)},
    {"label": "OBS_LESION", **get_span(t10, "pleural effusion", 2)},
    {"label": "ANAT_PLEURA", **get_span(t10, "diaphragmatic", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 5)},
    {"label": "ANAT_PLEURA", **get_span(t10, "posterior axillary line", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "8th intercostal space", 1)},
    {"label": "MEDICATION", **get_span(t10, "lidocaine", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleura", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "19G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "turbid", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "yellow", 1)},
    {"label": "SPECIMEN", **get_span(t10, "fluid", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "40 mL", 1)},
    {"label": "SPECIMEN", **get_span(t10, "fluid", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "loculated", 1)},
    {"label": "OBS_LESION", **get_span(t10, "effusion", 2)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 3)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t10, "28 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 4)},
    {"label": "ANAT_PLEURA", **get_span(t10, "mid-axillary line", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "6th intercostal space", 1)},
    {"label": "MEAS_PRESS", **get_span(t10, "-20 cm H2O", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "turbid", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "malodorous", 1)},
    {"label": "SPECIMEN", **get_span(t10, "fluid", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound", 2)},
    {"label": "OUTCOME_PLEURAL", **get_span(t10, "lung expansion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate pneumothorax", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "organ injury", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ultrasound", 3)},
    {"label": "LATERALITY", **get_span(t10, "right", 6)},
    {"label": "PROC_ACTION", **get_span(t10, "thoracentesis", 3)},
    {"label": "OBS_FINDING", **get_span(t10, "purulent", 1)},
    {"label": "SPECIMEN", **get_span(t10, "fluid", 4)},
    {"label": "LATERALITY", **get_span(t10, "right", 7)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 5)},
    {"label": "OBS_LESION", **get_span(t10, "empyema", 2)}
]
BATCH_DATA.append({"id": "700004", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)