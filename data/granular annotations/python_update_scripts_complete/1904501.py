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
# 3. Data Definitions (Batch)
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 1904501_syn_1
# ------------------------------------------
text_1 = """Indication: RLL mass, mediastinal staging.
Anesthesia: Moderate (Versed/Fentanyl).
Procedure:
- Scope passed orally.
- Normal vocal cords/trachea.
- Station 7 subcarinal node id[REDACTED].
- 21G Wang needle used for conventional TBNA (no EBUS).
- 4 passes complete.
- ROSE: Malignant cells present.
Complications: Minimal bleeding.
Plan: Discharge. Tumor board."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Versed", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Fentanyl", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "vocal cords", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "trachea", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "subcarinal node", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Wang needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)}, # Context is 'no EBUS', usually captured to indicate method discussion
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant cells", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_1", "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 1904501_syn_2
# ------------------------------------------
text_2 = """HISTORY: [REDACTED], a 68-year-old male with a right lower lobe mass and PET-avid subcarinal adenopathy, presented for diagnostic bronchoscopy.
PROCEDURE: Under moderate sedation, a flexible bronchoscope was introduced. Inspection of the tracheobronchial tree revealed no endobronchial lesions. Utilizing conventional transbronchial needle aspiration (TBNA) techniques based on anatomic landmarks, the subcarinal lymph node (Station 7) was sampled with a 21-gauge Wang needle. Four passes were obtained. Rapid on-site evaluation (ROSE) confirmed the presence of malignant epithelial cells consistent with metastatic carcinoma.
IMPRESSION: Successful staging bronchoscopy confirming N2 disease."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "subcarinal", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "tracheobronchial tree", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "anatomic landmarks", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "Station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Four passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "malignant epithelial cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "metastatic carcinoma", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_2", "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 1904501_syn_3
# ------------------------------------------
text_3 = """Procedure: Bronchoscopy with Transbronchial Needle Aspiration (CPT 31629).
Device: 21-gauge Wang Needle.
Site: Subcarinal Lymph Node (Station 7).
Technique: Conventional TBNA using anatomic landmarks (blind aspiration); no endobronchial ultrasound (EBUS) utilized. Four passes were performed to ensure adequate cellularity.
Specimen: Cytology and cell block. ROSE confirmed malignancy.
Justification: Mediastinal staging for lung cancer."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Transbronchial Needle Aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "Wang Needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Subcarinal Lymph Node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 7", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "anatomic landmarks", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "blind aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "Four passes", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "cell block", 1)},
    {"label": "OBS_ROSE", **get_span(text_3, "malignancy", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_3", "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 1904501_syn_4
# ------------------------------------------
text_4 = """Procedure Note
Patient: [REDACTED]
Attending: Dr. Desai
Procedure: Flex Bronch, Conventional TBNA

Steps:
1. Time out performed.
2. Moderate sedation administered.
3. Scope inserted; airway inspection normal.
4. Wang needle passed to Station 7 (subcarinal).
5. 4 passes performed using landmark guidance.
6. ROSE positive for carcinoma.
7. Scope withdrawn.

Complications: None.
Plan: Discharge home."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Flex Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "airway", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "subcarinal", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "4 passes", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "landmark guidance", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "positive", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "None", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_4", "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 1904501_syn_5
# ------------------------------------------
text_5 = """procedure note for samuel ortiz 68m we did a bronchoscopy today for staging of that lung mass sedation was fine used midazolam and fentanyl scope went down easy airway looked clear except for some compression near the carina used the wang needle 21 gauge on station 7 subcarinal node did 4 passes got good samples rose said it was cancer so we stopped bleeding was minimal patient tolerating well plan is oncology referral"""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "lung mass", 1)},
    {"label": "MEDICATION", **get_span(text_5, "midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_5, "fentanyl", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "airway", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "compression", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "carina", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "wang needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "21 gauge", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "subcarinal node", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "bleeding was minimal", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_5", "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 1904501_syn_6
# ------------------------------------------
text_6 = """The patient, a 68-year-old male, underwent flexible bronchoscopy with conventional TBNA for mediastinal staging. Moderate sedation was provided. A flexible bronchoscope was introduced orally. The airway inspection was unremarkable. A 21-gauge Wang needle was used to aspirate the subcarinal lymph node (Station 7) utilizing anatomic landmarks without ultrasound guidance. Four passes were performed. On-site cytology confirmed metastatic carcinoma. There were no complications. The patient was discharged in stable condition."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "airway", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "Wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Station 7", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "anatomic landmarks", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "ultrasound", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Four passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "metastatic carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no complications", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_6", "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 1904501_syn_7
# ------------------------------------------
text_7 = """[Indication]
Mediastinal staging for suspected NSCLC, RLL mass, Station 7 adenopathy.
[Anesthesia]
Moderate sedation (Midazolam/Fentanyl).
[Description]
Flexible bronchoscopy performed. Normal airway anatomy. Conventional TBNA of Station 7 performed using 21G Wang needle (4 passes). ROSE confirmed malignancy.
[Plan]
Discharge. Tumor board review."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Station 7", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "adenopathy", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Fentanyl", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Flexible bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "airway", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Station 7", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "malignancy", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_7", "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 1904501_syn_8
# ------------------------------------------
text_8 = """After obtaining informed consent, the patient was brought to the bronchoscopy suite and placed under moderate sedation. A flexible bronchoscope was introduced through the mouth. We inspected the airway and found no endobronchial abnormalities. We then targeted the subcarinal lymph node (Station 7) for staging using a conventional 21-gauge Wang needle. Four needle passes were performed based on anatomic landmarks. The on-site pathologist confirmed the presence of malignant cells. The procedure was completed without any significant complications."""

entities_8 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "Station 7", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "conventional", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "Four needle passes", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "anatomic landmarks", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "malignant cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "without any significant complications", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_8", "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 1904501_syn_9
# ------------------------------------------
text_9 = """OPERATION: Flexible endoscopy with needle sampling of mediastinal node.
INDICATION: Lung mass with enlarged lymph node.
DETAILS: Under sedation, the scope was inserted. The subcarinal node (Station 7) was accessed using a Wang needle via conventional technique. Four samples were extracted. Rapid analysis indicated malignancy. The instrument was removed. The patient recovered well."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Flexible endoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "needle sampling", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Lung mass", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "enlarged", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "subcarinal node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "Wang needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "conventional technique", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Four samples", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "malignancy", 1)},
]
BATCH_DATA.append({"id": "1904501_syn_9", "text": text_9, "entities": entities_9})

# ------------------------------------------
# Case 10: 1904501
# ------------------------------------------
text_10 = """PATIENT: [REDACTED], 68-year-old Male
MRN: [REDACTED]
DATE: [REDACTED]
ATTENDING: Dr. Priya Desai
FELLOW: Dr. Michael Anders
PROCEDURE: Flexible bronchoscopy with conventional transbronchial needle aspiration (TBNA) of subcarinal lymph node (station 7) using Wang needle (CPT 31629)
INDICATION: Right lower lobe lung mass with PET-avid subcarinal lymphadenopathy, mediastinal staging for suspected non-small cell lung cancer.

ANESTHESIA/SEDATION: Moderate sedation with intravenous midazolam and fentanyl administered by the bronchoscopy team. Topical 1% lidocaine applied to the oropharynx and vocal cords. The patient maintained spontaneous ventilation via native airway with supplemental oxygen by nasal cannula.

PROCEDURE DESCRIPTION:
After a time-out and confirmation of consent, a flexible adult bronchoscope was introduced orally with a bite block. The vocal cords were mobile and normal in appearance. The trachea and main carina were normal with mild extrinsic impression at the subcarinal region but no endobronchial tumor. The right and left bronchial trees were inspected to the subsegmental level without obstructing lesions.

CONVENTIONAL TBNA (WANG NEEDLE):
A 21-gauge Wang transbronchial aspiration needle was passed through the working channel. Using anatomic landmarks only (no EBUS or ultrasound), multiple passes were made through the bronchial wall just proximal to the main carina targeting the subcarinal (station 7) lymph node seen on imaging (short-axis 15 mm). Four needle passes were performed with suction applied on each pass, yielding blood-tinged material with visible tissue fragments.

ROSE: An on-site cytotechnologist was present. Rapid on-site evaluation showed abundant lymphocytes with clusters of malignant epithelial cells, consistent with metastatic carcinoma. Adequacy was confirmed after the third pass; a fourth pass was performed for cell block and ancillary studies.

SPECIMENS:
Station 7 conventional TBNA x4 passes, submitted for cytology, cell block, and flow cytometry with reflex molecular studies if malignant.

COMPLICATIONS: Minimal oozing at the puncture site resolved with suction and cold saline. No significant bleeding, hypoxia, or hemodynamic instability. No linear EBUS, radial EBUS, or navigational bronchoscopy was used at any point; this was a purely conventional blind Wang needle TBNA.

DISPOSITION/PLAN:
The patient was monitored in the bronchoscopy recovery area and discharged home in stable condition. Final cytology, cell block, and molecular profiling from station 7 will be reviewed at multidisciplinary tumor board. Further management (surgical resection versus chemoradiation or systemic therapy) will be based on complete staging results."""

entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang needle", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lung mass", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "subcarinal lymphadenopathy", 1)},
    {"label": "MEDICATION", **get_span(text_10, "midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_10, "fentanyl", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "vocal cords", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible adult bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "vocal cords", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "extrinsic impression", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "CONVENTIONAL", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "WANG NEEDLE", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang transbronchial aspiration needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "anatomic landmarks", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ultrasound", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "lymph node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "15 mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Four needle passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignant epithelial cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "metastatic carcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 3)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 passes", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "cell block", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "Minimal oozing", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "linear EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "blind", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang needle", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 4)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 7", 3)},
]
BATCH_DATA.append({"id": "1904501", "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)