import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts directory
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT / 'scripts'}. Make sure the environment is set up correctly.")
    sys.exit(1)

# List to hold all processed cases
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text string.
    
    Args:
        text (str): The text to search within.
        term (str): The term to search for (case-sensitive).
        occurrence (int): The specific occurrence to find (1-based index).
        
    Returns:
        dict: {'start': start_index, 'end': end_index} or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4830228
# ==========================================
id_1 = "4830228"
text_1 = """Ronald Bell, MRN [REDACTED], a 82-year-old male underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Academic Health System on [REDACTED]. The indication was peripheral nodule and bilateral hilar adenopathy with a 14.0mm ground-glass lesion in the LUL apicoposterior (B1+2), bronchus sign negative, PET SUV max 17.6. The patient was ASA class 2 with smoking history of 34 pack-years (current). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Pentax EB-1990i bronchoscope with 22-gauge FNB/ProCore needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 2L (14.8mm, 3 passes, ROSE: Atypical cells); station 4L (24.3mm, 2 passes, ROSE: Malignant - squamous cell carcinoma); station 10R (12.9mm, 2 passes, ROSE: Malignant - NSCLC NOS); station 10L (18.8mm, 3 passes, ROSE: Suspicious for malignancy); station 11L (18.7mm, 2 passes, ROSE: Malignant - adenocarcinoma). Rapid on-site evaluation was available for all stations.

The Ion robotic bronchoscopy system (Intuitive Surgical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 1.5mm. The robotic catheter was advanced to the LUL apicoposterior (B1+2) and radial EBUS probe deployment revealed concentric view of the lesion. Tool-in-lesion was confirmed by fluoroscopy. Transbronchial forceps biopsies (7 specimens), transbronchial needle aspiration (2 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed adequate lymphocytes, no malignancy.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 114 minutes. Attending physician: Rachel Goldman, MD."""

entities_1 = [
    # Procedure Methods
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},

    # Procedure Actions
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # Anatomy & Findings
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "adenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL apicoposterior (B1+2)", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL apicoposterior (B1+2)", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},

    # Measurements (Size, Count)
    {"label": "MEAS_SIZE", **get_span(text_1, "14.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 4)},

    # Devices
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},

    # Observations (ROSE)
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 1)},

    # Context & Outcomes
    {"label": "CTX_HISTORICAL", **get_span(text_1, "smoking history of", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "114 minutes", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)