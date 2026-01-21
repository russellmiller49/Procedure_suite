import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function to add the case
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the entity list.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term),
        "text": term
    }

# ==========================================
# Note 1: 567123_syn_1
# ==========================================
id_1 = "567123_syn_1"
text_1 = """Indication: Malignant effusion (Mesothelioma).
Proc: Catheter aspiration.
- 12Fr catheter.
- Landmark guidance.
- Drained 1500mL bloody.
- Catheter removed."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Malignant effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Mesothelioma", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Catheter aspiration", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Landmark guidance", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "1500mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bloody", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "removed", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 567123_syn_2
# ==========================================
id_2 = "567123_syn_2"
text_2 = """PROCEDURE NOTE: Therapeutic thoracentesis via catheter.
INDICATION: Symptomatic malignant pleural effusion.
DETAILS: A 12Fr drainage catheter was introduced into the left pleural space using anatomical landmarks. Approximately 1.5 liters of serosanguinous fluid were drained, resulting in symptomatic relief. The catheter was removed at the conclusion of the procedure."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Therapeutic thoracentesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignant pleural effusion", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_2, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "drainage catheter", 1)},
    {"label": "LATERALITY", **get_span(text_2, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "anatomical landmarks", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "1.5 liters", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "serosanguinous", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "drained", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_2, "symptomatic relief", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 3)},
    {"label": "PROC_ACTION", **get_span(text_2, "removed", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 567123_syn_3
# ==========================================
id_3 = "567123_syn_3"
text_3 = """CPT 32556: Pleural drainage w/ catheter.
Volume: 1500mL.
Guidance: None.
Indication: Malignant effusion.
Status: Catheter removed."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Pleural drainage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "1500mL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Malignant effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "removed", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 567123_syn_4
# ==========================================
id_4 = "567123_syn_4"
text_4 = """Procedure: Thoracentesis
1. Landmark.
2. 12Fr catheter.
3. Drained 1500mL bloody fluid.
4. Catheter out.
Patient [REDACTED]."""
entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Thoracentesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Landmark", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_4, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "1500mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "bloody", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Catheter", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 567123_syn_5
# ==========================================
id_5 = "567123_syn_5"
text_5 = """Catherine Brown mesothelioma patient large effusion drained 1.5L today using a 12fr kit catheter fluid bloody patient coughed so we stopped pulled line."""
entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "mesothelioma", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "1.5L", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_5, "12fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "kit catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "bloody", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "pulled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "line", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 567123_syn_6
# ==========================================
id_6 = "567123_syn_6"
text_6 = """Thoracentesis with catheter aspiration. Large left-sided malignant pleural effusion mesothelioma. With patient sitting at bedside left posterolateral chest prepped. Using Seldinger technique 12Fr drainage catheter placed. Bloody fluid immediately returned. 1500mL serosanguinous fluid removed over 40 minutes. Catheter removed at completion of procedure."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Thoracentesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "catheter aspiration", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "malignant pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mesothelioma", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "chest", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Seldinger technique", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_6, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "drainage catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Bloody", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "1500mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "serosanguinous", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "removed", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "removed", 2)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 567123_syn_7
# ==========================================
id_7 = "567123_syn_7"
text_7 = """[Indication]
Malignant pleural effusion.
[Anesthesia]
Local.
[Description]
12Fr catheter. Drained 1500mL. Removed.
[Plan]
Discharge."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Malignant pleural effusion", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Local", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_7, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "1500mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Removed", 1)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 567123_syn_8
# ==========================================
id_8 = "567123_syn_8"
text_8 = """[REDACTED] and a large fluid buildup. We drained it today using a temporary catheter. We removed 1.5 liters of bloody fluid, which helped her breathing a lot. We took the catheter out once we were done."""
entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "fluid buildup", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "temporary catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "removed", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "1.5 liters", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "bloody", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "helped her breathing a lot", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_8, "took", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 567123_syn_9
# ==========================================
id_9 = "567123_syn_9"
text_9 = """Diagnosis: Malignant pleural effusion.
Action: Catheter drainage.
Details: 12Fr catheter used. 1500mL drained. Catheter removed."""
entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "Malignant pleural effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Catheter drainage", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_9, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "1500mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_9, "removed", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 567123
# ==========================================
id_10 = "567123"
text_10 = """PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Location: [REDACTED]

Physician: Dr. Michael Wang, MD
Fellow: Dr. Sarah Thompson, MD - Pulmonary Fellow

Indication: Large left-sided malignant pleural effusion, mesothelioma

Procedure: Thoracentesis with catheter aspiration

Details:
71-year-old female with known epithelioid mesothelioma, presenting with increasing dyspnea and large left effusion on imaging. Not candidate for IPC at this time due to ongoing chemotherapy.

With patient sitting at bedside, left posterolateral chest prepped. 8th intercostal space, posterior axillary line chosen based on percussion and prior imaging (no US available at bedside).

Local anesthesia administered. Using Seldinger technique, 12Fr drainage catheter placed. Bloody fluid immediately returned. 1500mL serosanguinous fluid removed over 40 minutes. Drainage stopped when patient developed cough.

Patient [REDACTED] improvement in breathing. Post-procedure vitals stable. Catheter removed at completion of procedure.

Fluid sent for cytology confirmation.

M. Wang, MD / S. Thompson, MD"""
entities_10 = [
    {"label": "LATERALITY", **get_span(text_10, "left-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "malignant pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mesothelioma", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Thoracentesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "catheter aspiration", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mesothelioma", 2)},
    {"label": "LATERALITY", **get_span(text_10, "left", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 2)},
    {"label": "DEV_CATHETER", **get_span(text_10, "IPC", 1)},
    {"label": "LATERALITY", **get_span(text_10, "left", 3)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "chest", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "8th intercostal space", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "percussion", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Local anesthesia", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Seldinger technique", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_10, "12Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "drainage catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Bloody", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "1500mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "serosanguinous", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "removed", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "improvement in breathing", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "removed", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "Fluid", 1)}
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)