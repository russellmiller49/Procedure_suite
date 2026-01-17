import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is running from inside the 'scripts' or similar directory,
# we traverse up to find the root. Adjust as necessary for your specific environment.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts.add_training_case.py")
    sys.exit(1)

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
# Note 1: 1800685
# ==========================================
id_1 = "1800685"
text_1 = """Larry Gray, MRN [REDACTED], a 61-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Methodist Hospital on [REDACTED]. The indication was lung cancer staging - suspected nsclc with mediastinal lymphadenopathy with a 14.5mm ground-glass lesion in the RUL anterior (B3), bronchus sign positive. The patient was ASA class 3 with smoking history of 50 pack-years (former). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Fujifilm EB-580S bronchoscope with 19-gauge FNB/ProCore needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 11L (13.3mm, 4 passes, ROSE: Malignant - NSCLC NOS); station 7 (10.0mm, 2 passes, ROSE: Adequate lymphocytes); station 2L (24.9mm, 3 passes, ROSE: Malignant - small cell carcinoma). Rapid on-site evaluation was available for all stations.

The Monarch robotic bronchoscopy system (Auris Health (J&J)) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 3.2mm. The robotic catheter was advanced to the RUL anterior (B3) and radial EBUS probe deployment revealed concentric view of the lesion. Tool-in-lesion was confirmed by radial ebus. Transbronchial forceps biopsies (7 specimens), transbronchial needle aspiration (4 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed atypical cells.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 136 minutes. Attending physician: Brian O'Connor, MD."""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)}, # Context: peripheral lung biopsy
    {"label": "OBS_LESION", **get_span(text_1, "lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nsclc", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.5mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign positive", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},

    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fujifilm EB-580S bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic bronchoscopy system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric view", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 3)}, # Context: concentric view of the lesion
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # (2) in brushings (2)
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},

    # Paragraph 4 & 5
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "136 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)