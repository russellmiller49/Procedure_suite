import sys
from pathlib import Path

# Set up the repository root path (assuming script is running from within the repo)
# Adjust this logic as needed for the actual deployment environment.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure 'scripts' is a module in the python path
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback to appending path if module is not found directly
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a substring.
    
    Args:
        text (str): The text to search within.
        term (str): The substring to search for.
        occurrence (int): The specific occurrence to find (1-based index).
        
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Occurrence not found
            
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3983760
# ==========================================
id_1 = "3983760"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Date: [REDACTED]
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (62 years old)

Attending: Dr. Robert Chen, MD
Cytopathologist: Dr. Elizabeth Taylor, MD (ROSE)
Location: [REDACTED]

INDICATION: 62-year-old female non-smoker with 2.8cm RUL spiculated nodule (PET avid, SUVmax 8.2) and enlarged mediastinal lymph nodes on CT (Station 4R 1.8cm, Station 7 2.1cm, Station 4L 1.2cm). Referred for EBUS-TBNA staging prior to planned surgical resection if N2/N3 negative.

PREOPERATIVE DIAGNOSIS: Right upper lobe lung mass concerning for primary lung malignancy; mediastinal lymphadenopathy for staging

POSTOPERATIVE DIAGNOSIS: Same; mediastinal lymph nodes sampled - ROSE benign at all stations

PROCEDURE: Linear EBUS bronchoscopy with transbronchial needle aspiration of mediastinal and hilar lymph nodes (5 stations)

ANESTHESIA: General anesthesia with LMA

PROCEDURE NARRATIVE:
The EBUS bronchoscope (Olympus BF-UC180F) was introduced through the LMA. Systematic mediastinal staging was performed.

STATION-BY-STATION SAMPLING:

Station 7 (Subcarinal):
- Size: 22mm short axis, oval, heterogeneous, no CHS
- Elastography: Score 4 (suspicious)
- Sampling: 22G FNA needle, 4 passes
- ROSE: Abundant lymphocytes, no malignant cells, ADEQUATE - BENIGN

Station 4R (Right lower paratracheal):
- Size: 18mm short axis, round, heterogeneous
- Elastography: Score 3 (indeterminate)
- Sampling: 22G FNA needle, 4 passes  
- ROSE: Lymphocytes with scattered histiocytes, no malignant cells, ADEQUATE - BENIGN

Station 4L (Left lower paratracheal):
- Size: 12mm short axis, oval, homogeneous, CHS present
- Elastography: Score 2 (benign-appearing)
- Sampling: 22G FNA needle, 3 passes
- ROSE: Reactive lymphocytes, ADEQUATE - BENIGN

Station 10R (Right hilar):
- Size: 14mm short axis
- Sampling: 22G FNA needle, 3 passes
- ROSE: Lymphocytes and bronchial cells, ADEQUATE - BENIGN

Station 11R (Right interlobar):
- Size: 11mm short axis
- Sampling: 22G FNA needle, 3 passes
- ROSE: Lymphocytes, ADEQUATE - BENIGN

All samples sent for cell block and final cytopathology.

No complications. Airways examined and appeared normal. No endobronchial lesion at RUL orifice.

ROSE SUMMARY (Dr. Taylor):
"5 stations sampled with adequate lymphocyte material at all stations. No malignant cells id[REDACTED] at any station. Recommend final pathology confirmation. If staging remains N0 on final path, patient may proceed with planned surgical resection. If clinical suspicion remains high despite negative EBUS, recommend surgical staging (mediastinoscopy) given substantial adenopathy and risk of sampling error."

SPECIMENS:
- Station 7: Cytology, cell block
- Station 4R: Cytology, cell block
- Station 4L: Cytology, cell block
- Station 10R: Cytology, cell block
- Station 11R: Cytology, cell block

COMPLICATIONS: None

EBL: <5mL

IMPRESSION:
1. EBUS-TBNA of 5 mediastinal/hilar stations performed for lung cancer staging
2. ROSE negative for malignancy at all stations
3. Pending final cytopathology confirmation

PLAN:
1. Await final pathology (3-5 days)
2. Discussed with patient: If final pathology benign at all stations, will recommend surgical mediastinoscopy given size of station 7 and 4R nodes and high suspicion for malignancy based on primary lesion PET characteristics
3. Thoracic surgery consultation placed for mediastinoscopy
4. If mediastinoscopy also negative, patient will proceed with lobectomy + lymph node dissection

Dr. Robert Chen, MD
Interventional Pulmonology"""

entities_1 = [
    # Indication
    {"label": "MEAS_SIZE", **get_span(text_1, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.1cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.2cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "surgical resection", 1)},
    
    # Preop Diagnosis
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)},
    
    # Postop Diagnosis
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal lymph nodes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "benign", 1)},
    
    # Procedure Header
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 4)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    
    # Anesthesia
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "LMA", 1)},
    
    # Narrative
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC180F", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "LMA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 5)},
    
    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Subcarinal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNA needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "BENIGN", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Right lower paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNA needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "histiocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignant cells", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "BENIGN", 2)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Left lower paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNA needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Reactive lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "BENIGN", 3)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Right hilar", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 4)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNA needle", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Lymphocytes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "bronchial cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "BENIGN", 4)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Right interlobar", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 5)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNA needle", 5)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Lymphocytes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "BENIGN", 5)},

    # Samples / End of procedure
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airways", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "orifice", 1)},
    
    # ROSE Summary
    {"label": "OBS_ROSE", **get_span(text_1, "lymphocyte material", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "No malignant cells", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "surgical resection", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "surgical staging", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinoscopy", 1)},
    
    # Specimens List
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 4)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 4)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 5)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 5)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 6)},
    
    # Complications / EBL
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<5mL", 1)},
    
    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 5)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 6)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "lung cancer", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "negative", 2)},
    
    # Plan
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinoscopy", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 7", 1)}, # lowercase in plan? "station 7"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)}, # just 4R in plan
    {"label": "OBS_LESION", **get_span(text_1, "malignancy", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinoscopy", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinoscopy", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "lobectomy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "lymph node dissection", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)