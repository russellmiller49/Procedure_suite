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
    Finds the start and end indices of the Nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Case 1: 2245091
# ==========================================
id_1 = "2245091"
text_1 = """Maria Brooks, MRN [REDACTED], a 51-year-old male underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Regional Medical Center on [REDACTED]. The indication was pet-avid lung mass and mediastinal lymphadenopathy with a 30.9mm ground-glass lesion in the RUL anterior (B3), bronchus sign negative. The patient was ASA class 3 with smoking history of 20 pack-years (current). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Pentax EB-1990i bronchoscope with 22-gauge FNB/ProCore needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 4L (18.3mm, 2 passes, ROSE: Malignant - NSCLC NOS); station 10R (14.8mm, 4 passes, ROSE: Suspicious for malignancy); station 4R (20.9mm, 4 passes, ROSE: Malignant - adenocarcinoma); station 7 (24.0mm, 2 passes, ROSE: Malignant - adenocarcinoma). Rapid on-site evaluation was available for all stations.

The Monarch robotic bronchoscopy system (Auris Health (J&J)) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 2.0mm. The robotic catheter was advanced to the RUL anterior (B3) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by fluoroscopy. Transbronchial forceps biopsies (6 specimens), transbronchial needle aspiration (4 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed granuloma.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 77 minutes. Attending physician: Steven Park, MD."""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.9mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    
    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 2)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic bronchoscopy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "(2)", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},

    # Paragraph 4
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
    
    # Footer
    {"label": "CTX_TIME", **get_span(text_1, "77 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)