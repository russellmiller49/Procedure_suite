import sys
from pathlib import Path

# Set up the repository root path
# Path: data/granular annotations/Python_update_scripts/660219.py -> 4 levels down from proc_suite
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 660219_syn_1
# ==========================================
text_1 = """Indication: Pleural effusion (HF).
Proc: US Thoracentesis.
Site: [REDACTED]
Amount: 1.3L clear fluid.
Labs: Sent.
Complication: None."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "US", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Thoracentesis", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "1.3L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "clear", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": "660219_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 660219_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: Ultrasound-Guided Left Thoracentesis.
INDICATION: Symptomatic pleural effusion refractory to diuretic therapy.
DESCRIPTION: The largest fluid pocket was localized via bedside ultrasound. Under local anesthesia, a catheter was introduced using Seldinger technique. 1300 mL of serous fluid was drained for symptomatic relief and diagnostic analysis. Post-procedure ultrasound ruled out pneumothorax."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Ultrasound-Guided", 1)},
    {"label": "LATERALITY", **get_span(text_2, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Thoracentesis", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "bedside ultrasound", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "1300 mL", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "fluid", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "serous", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_2, "symptomatic relief", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "ultrasound", 2)},
]
BATCH_DATA.append({"id": "660219_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 660219_syn_3
# ==========================================
text_3 = """Code: 32555 (Thoracentesis with imaging guidance).
Specifics: Ultrasound used for localization and real-time guidance (documented). 1.3L removed. No chest tube placed."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Thoracentesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "imaging guidance", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ultrasound", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "1.3L", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "chest tube", 1)},
]
BATCH_DATA.append({"id": "660219_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 660219_syn_4
# ==========================================
text_4 = """Procedure: Thoracentesis
Patient: [REDACTED]
1. Sitting up.
2. US check: Left effusion.
3. Prepped/numbed 8th ICS.
4. Needle in -> fluid -> catheter in.
5. Drained 1.3L straw fluid.
6. Pulled catheter.
7. Bandaged."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Thoracentesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "US", 1)},
    {"label": "LATERALITY", **get_span(text_4, "Left", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "effusion", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "8th ICS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Needle", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "1.3L", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "straw", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "fluid", 2)},
    {"label": "DEV_CATHETER", **get_span(text_4, "catheter", 2)},
]
BATCH_DATA.append({"id": "660219_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 660219_syn_5
# ==========================================
text_5 = """[REDACTED] on the left lung heart failure. did a tap at the bedside used the ultrasound to find a good spot. drained 1.3 liters of yellow fluid he feels better breathing now. sent fluid to lab no complications."""

entities_5 = [
    {"label": "LATERALITY", **get_span(text_5, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "tap", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "1.3 liters", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "yellow", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_5, "feels better breathing", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no complications", 1)},
]
BATCH_DATA.append({"id": "660219_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 660219_syn_6
# ==========================================
text_6 = """Diagnostic and therapeutic thoracentesis performed on the left hemithorax. Ultrasound guidance utilized. 1300 mL of clear straw-colored fluid evacuated. Catheter removed. Patient tolerated well with improvement in dyspnea."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "thoracentesis", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "hemithorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Ultrasound", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "1300 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "clear", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "straw-colored", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Catheter", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_6, "improvement in dyspnea", 1)},
]
BATCH_DATA.append({"id": "660219_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 660219_syn_7
# ==========================================
text_7 = """[Indication]
Left pleural effusion, symptomatic.
[Anesthesia]
Local (Lidocaine).
[Description]
US-guided thoracentesis. 1.3L removed. Samples sent.
[Plan]
Monitor O2. Diuretics."""

entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "Left", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "pleural effusion", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "US-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "thoracentesis", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "1.3L", 1)},
]
BATCH_DATA.append({"id": "660219_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 660219_syn_8
# ==========================================
text_8 = """Dr. Simmons performed a procedure to drain fluid from around [REDACTED]. Using ultrasound to guide the needle, we removed 1.3 liters of fluid. This helped his breathing immediately. We sent the fluid to the lab to make sure there is no infection."""

entities_8 = [
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "needle", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "1.3 liters", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 2)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "helped his breathing", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 3)},
]
BATCH_DATA.append({"id": "660219_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 660219_syn_9
# ==========================================
text_9 = """Procedure: Ultrasound-guided pleural drainage.
Indication: Pleural effusion causing dyspnea.
Action: Percutaneous catheter insertion. Evacuation of 1300mL effusate.
Outcome: Symptomatic improvement."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "pleural drainage", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Pleural effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "1300mL", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "effusate", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_9, "Symptomatic improvement", 1)},
]
BATCH_DATA.append({"id": "660219_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 660219
# ==========================================
text_10 = """THORACENTESIS PROCEDURE NOTE
Date: [REDACTED]
Patient: [REDACTED] | 73M | MRN [REDACTED]
Location: [REDACTED]
Attending: Dr. Laura Simmons

INDICATION: Symptomatic recurrent left pleural effusion in the setting of heart failure and chronic kidney disease.

PROCEDURE: Ultrasound-guided diagnostic and therapeutic left thoracentesis (CPT 32555)

ANESTHESIA: Local anesthesia with 1% lidocaine only; no IV sedation administered.

TECHNIQUE:
Patient [REDACTED] upright leaning forward. Bedside ultrasound was used to id[REDACTED] the largest fluid pocket in the left posterior axillary line at the 8th intercostal space. The skin was prepped and draped in sterile fashion.

A 5 Fr thoracentesis catheter was advanced over a needle into the pleural space using the Seldinger technique under real-time ultrasound guidance. A total of 1.3 L of clear straw-colored fluid was removed, with drainage halted for mild cough.

Pleural fluid was sent for cell count, chemistries, microbiology and cytology.

Post-procedure ultrasound demonstrated a small residual effusion and good lung sliding. No chest tube was placed.

COMPLICATIONS: None.
DISPOSITION: Returned to the medical ward with improved dyspnea."""

entities_10 = [
    {"label": "LATERALITY", **get_span(text_10, "left", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound-guided", 1)},
    {"label": "LATERALITY", **get_span(text_10, "left", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "thoracentesis", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Bedside ultrasound", 1)},
    {"label": "LATERALITY", **get_span(text_10, "left", 3)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "posterior axillary line", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "8th intercostal space", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_10, "5 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "thoracentesis catheter", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "needle", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ultrasound", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "1.3 L", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "clear", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "straw-colored", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "fluid", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "Pleural fluid", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ultrasound", 3)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 2)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "improved dyspnea", 1)},
]
BATCH_DATA.append({"id": "660219", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)