import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function to add cases
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
            break
            
    if start == -1:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
        
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1904504_syn_1
# ==========================================
id_1 = "1904504_syn_1"
text_1 = """Indication: Breast ca hx, 4L node.
Anesthesia: GA, 7.5 ETT.
Procedure: Bronch w/ TBNA.
- Scope via ETT.
- 4L node sampled w/ 22G Wang needle.
- 3 passes.
- ROSE: Malignant (likely metastatic breast).
Complications: None.
Plan: Oncology f/u."""
entities_1 = [
    {"label": "CTX_HISTORICAL", **get_span(text_1, "Breast ca hx", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "7.5", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L node", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1904504_syn_2
# ==========================================
id_2 = "1904504_syn_2"
text_2 = """HISTORY: Ms. [REDACTED], 71, with a history of breast cancer, presented with new 4L lymphadenopathy.
PROCEDURE: Under general anesthesia, a flexible bronchoscope was introduced via endotracheal tube. The airway was inspected. Conventional TBNA of the left lower paratracheal (Station 4L) node was performed using a 22-gauge Wang needle. Three passes were obtained. ROSE confirmed atypical cells suspicious for metastatic carcinoma. Material was sent for immunohistochemistry.
IMPRESSION: TBNA Station 4L positive for malignancy."""
entities_2 = [
    {"label": "CTX_HISTORICAL", **get_span(text_2, "history of breast cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4L", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lymphadenopathy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "airway", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "left lower paratracheal (Station 4L) node", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "atypical cells suspicious for metastatic carcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "Station 4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "malignancy", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1904504_syn_3
# ==========================================
id_3 = "1904504_syn_3"
text_3 = """Service: Bronchoscopy with TBNA (31629).
Target: Station 4L (Left Lower Paratracheal).
Device: 22-gauge Wang Needle.
Method: Conventional aspiration via anatomic landmarks (No EBUS).
Specimen: 3 passes for cytology/IHC. ROSE positive for malignancy.
Indication: Staging of mediastinal recurrence."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 4L (Left Lower Paratracheal)", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "Wang Needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "anatomic landmarks", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_3, "malignancy", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1904504_syn_4
# ==========================================
id_4 = "1904504_syn_4"
text_4 = """Resident Note
Patient: [REDACTED]
Procedure: TBNA Station 4L
Staff: Dr. Li

1. GA/Intubation.
2. Scope passed.
3. 4L node id[REDACTED] via landmarks.
4. Wang needle used for 3 passes.
5. ROSE: Malignant cells.
6. Scope removed.

Plan: Extubate, PACU, Onc f/u."""
entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "Station 4L", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4L node", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "landmarks", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Malignant cells", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 2)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1904504_syn_5
# ==========================================
id_5 = "1904504_syn_5"
text_5 = """proc note [REDACTED] howard 71f hx breast cancer now has 4l node went in with general anesthesia ett tube scope looks good airway normal used 22g wang needle on 4l did 3 passes rose said cancer cells suspicious for breast met no bleeding extubated fine plan oncology"""
entities_5 = [
    {"label": "CTX_HISTORICAL", **get_span(text_5, "hx breast cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4l node", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "airway", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4l", 2)},
    {"label": "MEAS_COUNT", **get_span(text_5, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1904504_syn_6
# ==========================================
id_6 = "1904504_syn_6"
text_6 = """Brenda Howard underwent flexible bronchoscopy with conventional TBNA to evaluate a PET-avid 4L node. General anesthesia was used. The bronchoscope was introduced through the ETT. A 22-gauge Wang needle was used to sample the left lower paratracheal node (Station 4L) using anatomic landmarks. Three passes were performed. On-site cytology showed malignant cells. No complications occurred. The patient was transferred to the PACU."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4L node", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "Wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "left lower paratracheal node (Station 4L)", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "anatomic landmarks", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "malignant cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1904504_syn_7
# ==========================================
id_7 = "1904504_syn_7"
text_7 = """[Indication]
Breast cancer hx, PET-avid 4L node.
[Anesthesia]
General anesthesia (ETT).
[Description]
Flexible bronchoscopy via ETT. Conventional TBNA of Station 4L using 22G Wang needle (3 passes). ROSE confirmed malignancy. IHC pending.
[Plan]
Extubate. Oncology referral."""
entities_7 = [
    {"label": "CTX_HISTORICAL", **get_span(text_7, "Breast cancer hx", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4L node", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Station 4L", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "malignancy", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1904504_syn_8
# ==========================================
id_8 = "1904504_syn_8"
text_8 = """The patient was placed under general anesthesia. We advanced the bronchoscope through the endotracheal tube and surveyed the airway. Using anatomic landmarks, we id[REDACTED] the location of the left lower paratracheal node (Station 4L). We performed conventional TBNA using a 22-gauge Wang needle, obtaining three passes. On-site evaluation was consistent with metastatic disease. The procedure ended without incident."""
entities_8 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "anatomic landmarks", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "left lower paratracheal node (Station 4L)", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "three passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "consistent with metastatic disease", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1904504_syn_9
# ==========================================
id_9 = "1904504_syn_9"
text_9 = """PROCEDURE: Bronchoscopy with blind needle biopsy of paratracheal node.
REASON: Possible metastatic breast cancer.
TECHNIQUE: Under general anesthesia, the scope was inserted. The Station 4L node was sampled with a Wang needle. Three samples were taken. Rapid analysis confirmed malignancy. The patient was awakened."""
entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "blind", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "needle biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "paratracheal node", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Station 4L node", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Three samples", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "malignancy", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1904504
# ==========================================
id_10 = "1904504"
text_10 = """PATIENT: [REDACTED], 71-year-old Female
MRN: [REDACTED]
DATE: [REDACTED]
ATTENDING: Dr. Jason Li
FELLOW: Dr. Sofia Martinez
PROCEDURE: Flexible bronchoscopy with conventional transbronchial needle aspiration (TBNA) of left lower paratracheal lymph node (station 4L) using Wang needle (CPT 31629)
INDICATION: History of breast cancer with new PET-avid 4L mediastinal lymphadenopathy; tissue diagnosis requested to distinguish metastatic disease from granulomatous inflammation.

ANESTHESIA/SEDATION: General anesthesia with endotracheal intubation (7.5 ETT). Anesthesiology provided induction with propofol and rocuronium; patient mechanically ventilated throughout.

PROCEDURE DESCRIPTION:
After pre-procedural verification and a time-out, a flexible bronchoscope was advanced through the endotracheal tube. The trachea and main carina were normal. The right bronchial tree was normal. On the left, there was subtle extrinsic narrowing of the distal trachea just above the carina and mild impression on the proximal left mainstem bronchus; mucosa was intact.

CONVENTIONAL TBNA (WANG NEEDLE):
A 22-gauge Wang TBNA needle was introduced via the bronchoscope. Using anatomic landmarks (no EBUS available in this OR), the left lower paratracheal (4L) node was sampled by puncturing the medial wall of the distal trachea above the left mainstem origin. Three passes were performed with suction. Aspirates contained blood-tinged material with tissue fragments.

ROSE: Rapid on-site cytology was available. ROSE revealed lymphoid tissue with atypical epithelial cells; findings were suspicious for metastatic carcinoma and deemed adequate for diagnosis. Additional material was set aside for cell block and immunohistochemistry.

SPECIMENS:
Station 4L conventional TBNA x3 passes submitted for cytology, cell block, and immunohistochemical staining.

COMPLICATIONS: No significant bleeding, airway compromise, or hemodynamic instability. No linear EBUS, radial EBUS, or navigational bronchoscopy was performed; this was purely a blind Wang needle TBNA.

DISPOSITION/PLAN:
The patient was extubated in the OR and transferred to PACU in stable condition. Final pathology will be correlated with prior breast cancer histology. If metastatic disease is confirmed, systemic therapy options will be discussed with oncology; if benign, further workup for granulomatous disease will be considered."""
entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "left lower paratracheal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 4L", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang needle", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_10, "History of breast cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4L", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "7.5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right bronchial tree", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "extrinsic narrowing", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "distal trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "proximal left mainstem bronchus", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "CONVENTIONAL", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "WANG NEEDLE", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang TBNA needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "bronchoscope", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "anatomic landmarks", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "left lower paratracheal (4L) node", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "distal trachea", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "lymphoid tissue", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "atypical epithelial cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "suspicious for metastatic carcinoma", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "cell block", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4L", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 3)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x3 passes", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "cytology", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "cell block", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "blind", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)