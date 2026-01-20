import sys
from pathlib import Path

# Set up the repository root path
# (Assuming this script is running two levels deep, e.g., in a 'scripts/generated' folder)
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Could not import 'add_case'. Ensure you are running this from the correct repository structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3673622
# ==========================================
id_1 = "3673622"
text_1 = """Brandon Morris, MRN [REDACTED], a 47-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at St. Luke's Medical Center on [REDACTED]. The indication was lung cancer staging - suspected nsclc with mediastinal lymphadenopathy with a 19.5mm solid lesion in the RLL posterior basal (B10), bronchus sign positive, PET SUV max 5.4. The patient was ASA class 3 with smoking history of None pack-years (never). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Fujifilm EB-580S bronchoscope with 19-gauge FNB/ProCore needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 10R (11.4mm, 3 passes, ROSE: Malignant - adenocarcinoma); station 7 (8.1mm, 3 passes, ROSE: Adequate lymphocytes, no malignancy); station 2R (13.6mm, 2 passes, ROSE: Adequate lymphocytes); station 4R (22.2mm, 3 passes, ROSE: Malignant - small cell carcinoma). Rapid on-site evaluation was available for all stations.

The Ion robotic bronchoscopy system (Intuitive Surgical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 3.2mm. The robotic catheter was advanced to the RLL posterior basal (B10) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by fluoroscopy. Transbronchial forceps biopsies (7 specimens), transbronchial needle aspiration (3 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed malignant - nsclc nos.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 91 minutes. Attending physician: Eric Johnson, MD."""

entities_1 = [
    # Procedures and Methods
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # Anatomy
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL posterior basal (B10)", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4R", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL posterior basal (B10)", 2)},

    # Observations and Findings
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign positive", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 2)}, # Using 2nd instance of phrase "Adequate lymphocytes"
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Devices
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fujifilm EB-580S bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    
    # Measurements
    {"label": "MEAS_SIZE", **get_span(text_1, "19.5mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 4)},
    {"label": "MEAS_VOL", **get_span(text_1, "less than 10mL", 1)},

    # Context & Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "91 minutes", 1)},
    
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