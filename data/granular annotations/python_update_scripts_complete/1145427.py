import sys
from pathlib import Path

# 1. Dynamic Repo Root Calculation
#    (Assumes this script is running from inside the repo or similar structure)
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# 2. Import the Utility Function
#    (Adjust 'scripts.add_training_case' to your actual module path if different)
from scripts.add_training_case import add_case

BATCH_DATA = []

# Helper Function for safe span extraction
def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of 'term' in 'text'.
    Returns a dictionary: { "start": int, "end": int }.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note: 1145427
# ==========================================
id_1 = "1145427"
text_1 = """Michael Gomez, MRN [REDACTED], a 48-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Community Hospital on [REDACTED]. The indication was combined staging and peripheral nodule diagnosis with a 16.3mm ground-glass lesion in the RLL superior (B6), bronchus sign positive, PET SUV max 6.9. The patient was ASA class 2 with smoking history of 23 pack-years (former). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Olympus BF-UC190F bronchoscope with 22-gauge Standard FNA needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 11L (14.4mm, 4 passes, ROSE: Granuloma); station 4L (21.7mm, 3 passes, ROSE: Malignant - NSCLC NOS); station 10L (19.2mm, 2 passes, ROSE: Malignant - adenocarcinoma). Rapid on-site evaluation was available for all stations.

The Galaxy robotic bronchoscopy system (Noah Medical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 3.4mm. The robotic catheter was advanced to the RLL superior (B6) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by radial ebus. Transbronchial forceps biopsies (6 specimens), transbronchial needle aspiration (4 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed malignant - squamous cell carcinoma.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 94 minutes. Attending physician: Andrew Nakamura, MD."""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.3mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},

    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "robotic", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "probe", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # (2) in brushings context
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - squamous cell carcinoma", 1)},

    # Paragraph 4
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "94 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)