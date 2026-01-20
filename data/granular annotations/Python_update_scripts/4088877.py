import sys
from pathlib import Path

# Set the root directory dynamically
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 4088877
# ==========================================
t1 = """Catherine Gray, MRN [REDACTED], a 59-year-old male underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Baptist Medical Center on [REDACTED]. The indication was lung nodule evaluation with mediastinal lymphadenopathy workup with a 27.1mm solid lesion in the RLL superior (B6), bronchus sign negative, PET SUV max 6.1. The patient was ASA class 3 with smoking history of None pack-years (never). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Olympus BF-UC190F bronchoscope with 22-gauge FNB/ProCore needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 4L (9.1mm, 3 passes, ROSE: Suspicious for malignancy); station 2R (14.9mm, 3 passes, ROSE: Malignant - NSCLC NOS); station 2L (13.2mm, 2 passes, ROSE: Adequate lymphocytes, no malignancy). Rapid on-site evaluation was available for all stations.

The Ion robotic bronchoscopy system (Intuitive Surgical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 1.8mm. The robotic catheter was advanced to the RLL superior (B6) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by augmented fluoroscopy. Transbronchial forceps biopsies (5 specimens), transbronchial needle aspiration (2 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed malignant - squamous cell carcinoma.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 108 minutes. Attending physician: Amanda Foster, MD."""

e1 = [
    # Paragraph 1
    {"label": "PROC_METHOD", **get_span(t1, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "mediastinal", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "peripheral lung biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lung nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "mediastinal", 2)},
    {"label": "OBS_LESION", **get_span(t1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "27.1mm", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL superior (B6)", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "8.0mm", 1)},
    
    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(t1, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22-gauge", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "mediastinal", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "hilar", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(t1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "9.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Suspicious for malignancy", 1)},
    
    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(t1, "station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "14.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - NSCLC NOS", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(t1, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "13.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Adequate lymphocytes, no malignancy", 1)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(t1, "Ion robotic bronchoscopy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL superior (B6)", 2)},
    {"label": "PROC_METHOD", **get_span(t1, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(t1, "augmented fluoroscopy", 1)},
    
    # Procedures / Actions
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "5 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "malignant - squamous cell carcinoma", 1)},

    # Paragraph 4
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "without complications", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(t1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cultures", 1)},
    
    # Paragraph 5
    {"label": "CTX_TIME", **get_span(t1, "108 minutes", 1)},
]

BATCH_DATA.append({"id": "4088877", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)