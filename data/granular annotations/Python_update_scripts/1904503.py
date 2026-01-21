import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the training case
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a tuple (start, end).
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return start, start + len(term)

# ==========================================
# Case 1: 1904503_syn_1
# ==========================================
id_1 = "1904503_syn_1"
text_1 = """Indication: 4L adenopathy, r/o sarcoid vs lymphoma.
Anesthesia: Moderate.
Procedure: Flex bronch.
- Airway normal.
- Station 4L targeted w/ 21G Wang needle.
- 4 passes.
- ROSE: Granulomas (benign).
Complications: None.
Plan: Rheumatology referral."""

entities_1 = [
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "4L", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "adenopathy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "Flex bronch", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_1, "Airway", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_1, "Station 4L", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "21G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Wang needle", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "4 passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "Granulomas", 1)))},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 1904503_syn_2
# ==========================================
id_2 = "1904503_syn_2"
text_2 = """HISTORY: [REDACTED] isolated left lower paratracheal lymphadenopathy for tissue diagnosis.
PROCEDURE: Under moderate sedation, flexible bronchoscopy was performed. The airway examination was unremarkable. Conventional transbronchial needle aspiration (TBNA) of the Station 4L lymph node was executed using a 21-gauge Wang needle based on anatomic landmarks. Four passes were obtained. Rapid on-site evaluation revealed non-necrotizing granulomas consistent with sarcoidosis, ruling out lymphoma.
IMPRESSION: TBNA consistent with granulomatous inflammation."""

entities_2 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "lymphadenopathy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "flexible bronchoscopy", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_2, "airway", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "Conventional", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "transbronchial needle aspiration", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "TBNA", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_2, "Station 4L", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_2, "21-gauge", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "Wang needle", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_2, "Four passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_2, "granulomas", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "TBNA", 2)))},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 1904503_syn_3
# ==========================================
id_3 = "1904503_syn_3"
text_3 = """Procedure: Bronchoscopy with Transbronchial Needle Aspiration (31629).
Site: Left Lower Paratracheal Node (Station 4L).
Device: 21-gauge Wang Needle.
Technique: Conventional blind aspiration using anatomic landmarks. No EBUS utilized.
Specimen: 4 passes for cytology, cell block, and culture. ROSE showed granulomas.
Diagnosis: Sarcoidosis suspected."""

entities_3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Transbronchial Needle Aspiration", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_3, "Station 4L", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_3, "21-gauge", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "Wang Needle", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "Conventional", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "blind", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "EBUS", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_3, "4 passes", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_3, "cytology", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_3, "cell block", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_3, "culture", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_3, "granulomas", 1)))},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 1904503_syn_4
# ==========================================
id_4 = "1904503_syn_4"
text_4 = """Procedure Note
Patient: [REDACTED]
Attending: Dr. Grant
Procedure: Bronchoscopy, TBNA 4L

Steps:
1. Time out.
2. Sedation (Versed/Fentanyl).
3. Scope inserted.
4. Exam normal.
5. Wang needle used for 4L node.
6. 4 passes.
7. ROSE: Granulomas.
8. Cultures sent.

Plan: Discharge, Rheum consult."""

entities_4 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "TBNA", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_4, "4L", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_4, "Versed", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_4, "Fentanyl", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Scope", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Wang needle", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_4, "4L", 2)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_4, "4 passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_4, "Granulomas", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_4, "Cultures", 1)))},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 1904503_syn_5
# ==========================================
id_5 = "1904503_syn_5"
text_5 = """bronch note for omar rahman 59m indx adenopathy rule out sarcoid sedation moderate scope in airway clear except for some compression on the left used wang needle on 4l node did 4 passes rose showed granulomas no cancer seen minimal bleeding patient did well discharge home"""

entities_5 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_5, "bronch", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "adenopathy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "scope", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_5, "airway", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "wang needle", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_5, "4l", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_5, "4 passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_5, "granulomas", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_5, "minimal bleeding", 1)))},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 1904503_syn_6
# ==========================================
id_6 = "1904503_syn_6"
text_6 = """The patient, a 59-year-old male, underwent flexible bronchoscopy for evaluation of mediastinal lymphadenopathy. Moderate sedation was administered. A flexible bronchoscope was inserted. The airway was patent. A 21-gauge Wang needle was used to perform conventional TBNA of the left lower paratracheal lymph node (Station 4L). Four passes were obtained. On-site cytology revealed non-necrotizing granulomas. There were no complications. The patient was discharged home."""

entities_6 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "flexible bronchoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "lymphadenopathy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "flexible bronchoscope", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_6, "airway", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_6, "21-gauge", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "Wang needle", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "conventional", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "TBNA", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_6, "Station 4L", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_6, "Four passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_6, "granulomas", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_6, "no complications", 1)))},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 1904503_syn_7
# ==========================================
id_7 = "1904503_syn_7"
text_7 = """[Indication]
Isolated 4L adenopathy, r/o sarcoidosis vs lymphoma.
[Anesthesia]
Moderate sedation.
[Description]
Flexible bronchoscopy performed. Conventional TBNA of Station 4L using 21G Wang needle (4 passes). ROSE showed granulomas. Cultures sent.
[Plan]
Discharge. Rheumatology referral."""

entities_7 = [
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_7, "4L", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "adenopathy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "Flexible bronchoscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "Conventional", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "TBNA", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_7, "Station 4L", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_7, "21G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "Wang needle", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_7, "4 passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_7, "granulomas", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_7, "Cultures", 1)))},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 1904503_syn_8
# ==========================================
id_8 = "1904503_syn_8"
text_8 = """Following consent, the patient was sedated with midazolam and fentanyl. We introduced the bronchoscope and inspected the tracheobronchial tree, which appeared normal. We then directed our attention to the left lower paratracheal station (4L) and performed conventional TBNA using a 21-gauge Wang needle. Four passes were completed. Rapid on-site evaluation demonstrated granulomas, suggesting sarcoidosis. The procedure was well-tolerated."""

entities_8 = [
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_8, "midazolam", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_8, "fentanyl", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "bronchoscope", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_8, "tracheobronchial tree", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_8, "4L", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "conventional", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "TBNA", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_8, "21-gauge", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "Wang needle", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_8, "Four passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_8, "granulomas", 1)))},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 1904503_syn_9
# ==========================================
id_9 = "1904503_syn_9"
text_9 = """OPERATION: Endoscopy with needle sampling of left paratracheal node.
REASON: Lymphadenopathy, check for sarcoid.
DETAILS: Under sedation, the scope was passed. The Station 4L node was accessed using a Wang needle via landmarks. Four samples were taken. Rapid testing showed granulomas. The instrument was removed. Patient stable."""

entities_9 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "Endoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "needle sampling", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "Lymphadenopathy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "scope", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_9, "Station 4L", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "Wang needle", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_9, "Four samples", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_9, "granulomas", 1)))},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 1904503
# ==========================================
id_10 = "1904503"
text_10 = """PATIENT: [REDACTED], 59-year-old Male
MRN: [REDACTED]
DATE: [REDACTED]
ATTENDING: Dr. Melissa Grant
FELLOW: Dr. Ravi Kulkarni
PROCEDURE: Flexible bronchoscopy with conventional transbronchial needle aspiration (TBNA) of left lower paratracheal lymph node (station 4L) using Wang needle (CPT 31629)
INDICATION: Isolated mediastinal lymphadenopathy (station 4L, 1.6 cm short axis) in a patient with progressive dyspnea and bilateral hilar fullness; evaluation for sarcoidosis versus lymphoma.

ANESTHESIA/SEDATION: Moderate sedation with intravenous midazolam and fentanyl. Topical 1% lidocaine to nasopharynx, vocal cords, and trachea. The patient breathed spontaneously via native airway with supplemental oxygen.

PROCEDURE DESCRIPTION:
After informed consent and a procedural time-out, a flexible adult bronchoscope was introduced orally. The upper airway, vocal cords, and trachea were normal. The main carina was sharp. The right bronchial tree was normal. On the left, there was mild extrinsic impression on the distal left mainstem corresponding to the paratracheal lymph node but no mucosal lesion.

CONVENTIONAL TBNA (WANG NEEDLE):
A 21-gauge Wang TBNA needle was advanced through the bronchoscope. Using anatomic landmarks without EBUS guidance, the left lower paratracheal (station 4L) lymph node was targeted via the medial wall of the distal trachea just above the left mainstem origin. Four needle passes were performed with suction. Aspirates contained blood-tinged material with small whitish tissue fragments.

ROSE: Cytotechnologist present for on-site evaluation. ROSE demonstrated abundant benign lymphocytes with well-formed non-necrotizing granulomas. No malignant cells were seen. Adequacy was confirmed after the second pass; two additional passes were obtained for culture and cell block.

SPECIMENS:
Station 4L conventional TBNA x4 passes submitted for cytology, cell block, AFB/fungal cultures, and flow cytometry.

COMPLICATIONS: No significant bleeding, hypoxia, or hemodynamic instability. No linear or radial EBUS, navigation, or fluoroscopy was used; this was a blind conventional Wang needle TBNA.

DISPOSITION/PLAN:
The patient recovered uneventfully in the bronchoscopy suite and was discharged home. If final pathology confirms non-necrotizing granulomatous inflammation, findings will be discussed with rheumatology for sarcoidosis management; if lymphoma is id[REDACTED], oncology referral will be arranged."""

entities_10 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Flexible bronchoscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "conventional", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "transbronchial needle aspiration", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "TBNA", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_10, "station 4L", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "Wang needle", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "lymphadenopathy", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_10, "station 4L", 2)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_10, "1.6 cm", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_10, "midazolam", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_10, "fentanyl", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_10, "lidocaine", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "vocal cords", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "trachea", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "flexible adult bronchoscope", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "upper airway", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "vocal cords", 2)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "trachea", 2)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "main carina", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "right bronchial tree", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "left mainstem", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "CONVENTIONAL", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "TBNA", 2)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "WANG NEEDLE", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_10, "21-gauge", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "Wang TBNA needle", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "bronchoscope", 2)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "EBUS", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_10, "station 4L", 3)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "distal trachea", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "left mainstem", 2)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_10, "Four needle passes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_10, "lymphocytes", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_10, "granulomas", 1)))},
    {"label": "ANAT_LN_STATION", **dict(zip(["start", "end"], get_span(text_10, "Station 4L", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "conventional", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "TBNA", 4)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_10, "x4 passes", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "cytology", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "cell block", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "cultures", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "flow cytometry", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "EBUS", 2)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "navigation", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "fluoroscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "blind", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "conventional", 3)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "Wang needle", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "TBNA", 5)))},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)