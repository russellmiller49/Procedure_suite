import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
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
# Note 1: 1904505_syn_1
# ==========================================
t1 = """Indication: RUL mass, 4R node.
Anesthesia: Moderate.
Procedure: Flex bronch.
- Airway normal.
- Station 4R targeted w/ 21G Wang needle.
- 3 passes.
- ROSE: NSCLC.
Complications: Minimal bleeding.
Plan: Tumor board."""

e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R node", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Flex bronch", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Airway", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "NSCLC", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Minimal bleeding", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1904505_syn_2
# ==========================================
t2 = """HISTORY: [REDACTED] a right upper lobe mass and ipsilateral mediastinal adenopathy.
PROCEDURE: Under moderate sedation, flexible bronchoscopy was performed. Conventional TBNA of the right lower paratracheal (Station 4R) lymph node was executed using a 21-gauge Wang needle and anatomic landmarks. Three passes yielded diagnostic material. ROSE confirmed non-small cell lung carcinoma.
IMPRESSION: N2 positive NSCLC."""

e2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mediastinal adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "21-gauge Wang needle", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "anatomic landmarks", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "non-small cell lung carcinoma", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1904505_syn_3
# ==========================================
t3 = """Procedure: Bronchoscopy with Transbronchial Needle Aspiration (31629).
Site: Right Lower Paratracheal Node (Station 4R).
Device: 21-gauge Wang Needle.
Technique: Blind aspiration using anatomic landmarks (No EBUS).
Specimen: 3 passes for cytology/molecular. ROSE positive for NSCLC.
Justification: Staging of lung cancer."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Transbronchial Needle Aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Right Lower Paratracheal Node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "21-gauge Wang Needle", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Blind", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "anatomic landmarks", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "NSCLC", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1904505_syn_4
# ==========================================
t4 = """Procedure Note
Patient: [REDACTED]
Attending: Dr. Moore
Procedure: TBNA Station 4R

Steps:
1. Moderate sedation.
2. Scope inserted.
3. 4R node id[REDACTED].
4. Wang needle used for 3 passes.
5. ROSE: Positive for NSCLC.
6. No complications.

Plan: Discharge, Tumor Board."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "4R node", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "NSCLC", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No complications", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1904505_syn_5
# ==========================================
t5 = """bronch note victor lin 64m lung mass 4r node sedation moderate scope down airway ok used wang needle 21g on station 4r did 3 passes rose showed nsclc minimal bleeding stopped on its own patient stable discharge home"""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lung", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "4r node", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "airway", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "wang needle 21g", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "station 4r", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "nsclc", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "minimal bleeding", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1904505_syn_6
# ==========================================
t6 = """Victor Lin, a 64-year-old male, underwent flexible bronchoscopy with conventional TBNA for staging of a right upper lobe mass. Moderate sedation was administered. The bronchoscope was inserted orally. A 21-gauge Wang needle was used to sample the right lower paratracheal node (Station 4R) using anatomic landmarks. Three passes were obtained. On-site cytology confirmed non-small cell lung carcinoma. The procedure was uncomplicated."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "21-gauge Wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "right lower paratracheal node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "Station 4R", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "anatomic landmarks", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "On-site cytology", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "non-small cell lung carcinoma", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1904505_syn_7
# ==========================================
t7 = """[Indication]
RUL mass, 4R adenopathy, staging.
[Anesthesia]
Moderate sedation.
[Description]
Flexible bronchoscopy performed. Conventional TBNA of Station 4R using 21G Wang needle (3 passes). ROSE confirmed NSCLC. Molecular testing sent.
[Plan]
Discharge. Tumor board."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4R", 1)},
    {"label": "OBS_LESION", **get_span(t7, "adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "21G Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "NSCLC", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1904505_syn_8
# ==========================================
t8 = """After informed consent, the patient was sedated and the bronchoscope was introduced. We inspected the airway and then targeted the right lower paratracheal node (Station 4R) for staging. Using a 21-gauge Wang needle and conventional technique, we performed three passes. Rapid on-site evaluation confirmed malignant cells compatible with NSCLC. The patient tolerated the procedure well."""

e8 = [
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "right lower paratracheal node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "21-gauge Wang needle", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "conventional technique", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "three passes", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "Rapid on-site evaluation", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "NSCLC", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1904505_syn_9
# ==========================================
t9 = """OPERATION: Endoscopy with needle sampling of right paratracheal node.
REASON: Lung cancer staging.
DETAILS: Under sedation, the scope was passed. The Station 4R node was accessed with a Wang needle. Three samples were extracted. Rapid testing showed cancer. The instrument was removed."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Endoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "needle sampling", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "right paratracheal node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "Three samples", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "Rapid testing", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "cancer", 1)}
]
BATCH_DATA.append({"id": "1904505_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1904505
# ==========================================
t10 = """PATIENT: [REDACTED], 64-year-old Male
MRN: [REDACTED]
DATE: [REDACTED]
ATTENDING: Dr. Angela Moore
FELLOW: Dr. David Shah
PROCEDURE: Flexible bronchoscopy with conventional transbronchial needle aspiration (TBNA) of right lower paratracheal lymph node (station 4R) using Wang needle (CPT 31629)
INDICATION: Right upper lobe lung mass with PET-avid right lower paratracheal (4R) lymph node; mediastinal staging for suspected non-small cell lung cancer.

ANESTHESIA/SEDATION: Moderate sedation with IV midazolam and fentanyl. Topical lidocaine applied to upper airway. The patient breathed spontaneously via native airway with supplemental oxygen.

PROCEDURE DESCRIPTION:
After time-out and confirmation of consent, a flexible bronchoscope was advanced orally. The larynx and trachea were normal. The main carina was sharp. The right mainstem bronchus showed mild external impression along its medial wall consistent with the known 4R node; mucosa was intact. The remainder of the bronchial tree was free of obstructing lesions.

CONVENTIONAL TBNA (WANG NEEDLE):
A 21-gauge Wang TBNA needle was introduced through the bronchoscope. Using anatomic landmarks (no EBUS), the right lower paratracheal (station 4R) node was targeted from the distal trachea and proximal right mainstem bronchus. Three passes were made with suction applied. Aspirates contained blood-tinged material with visible tissue fragments.

ROSE: On-site cytology was available. ROSE demonstrated malignant epithelial cells compatible with non-small cell lung carcinoma in a lymphoid background, confirming adequacy after the second pass. A third pass was obtained for cell block.

SPECIMENS:
Station 4R conventional TBNA x3 passes submitted for cytology and cell block with reflex molecular studies.

COMPLICATIONS: Minimal self-limited bleeding from the puncture site; no hypoxia or arrhythmia. No linear EBUS, radial EBUS, or navigation was performed; this was conventional blind Wang needle TBNA.

DISPOSITION/PLAN:
The patient recovered uneventfully in the bronchoscopy recovery area and was discharged home. Staging will be finalized once cytology and imaging are integrated; case to be presented at lung tumor board for definitive treatment planning."""

e10 = [
    {"label": "PROC_ACTION", **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "right lower paratracheal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "Wang needle", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lung mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "right lower paratracheal (4R) lymph node", 1)},
    {"label": "MEDICATION", **get_span(t10, "midazolam", 1)},
    {"label": "MEDICATION", **get_span(t10, "fentanyl", 1)},
    {"label": "MEDICATION", **get_span(t10, "lidocaine", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airway", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "right mainstem bronchus", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "4R node", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "21-gauge Wang TBNA needle", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "anatomic landmarks", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "right lower paratracheal (station 4R) node", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "right mainstem bronchus", 2)},
    {"label": "MEAS_COUNT", **get_span(t10, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "On-site cytology", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "malignant epithelial cells", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "non-small cell lung carcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "conventional", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 3)},
    {"label": "MEAS_COUNT", **get_span(t10, "x3 passes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Minimal self-limited bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "conventional", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "blind", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "Wang needle", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 4)}
]
BATCH_DATA.append({"id": "1904505", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)