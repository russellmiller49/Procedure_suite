import sys
from pathlib import Path

# Set the root directory for the repo (assumes this script is running from the root or scripts dir)
# Adjust path calculation as needed based on your actual directory structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly in a different structure
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the n-th occurrence of a term in the text.
    Returns a dictionary compatible with the entity schema.
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
# Case: 4124884
# ==========================================
id_1 = "4124884"
text_1 = """Matthew Barnes, MRN [REDACTED], a 49-year-old male underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Regional Medical Center on [REDACTED]. The indication was pet-avid lung mass and mediastinal lymphadenopathy with a 20.0mm solid lesion in the RML medial (B5), bronchus sign negative, PET SUV max 6.5. The patient was ASA class 4 with smoking history of 23 pack-years (current). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Olympus BF-UC190F bronchoscope with 22-gauge Acquire needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 2L (13.8mm, 4 passes, ROSE: Malignant - small cell carcinoma); station 4R (23.9mm, 3 passes, ROSE: Malignant - adenocarcinoma); station 11R (19.6mm, 3 passes, ROSE: Atypical cells); station 11L (17.4mm, 2 passes, ROSE: Malignant - adenocarcinoma). Rapid on-site evaluation was available for all stations.

The Ion robotic bronchoscopy system (Intuitive Surgical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 2.5mm. The robotic catheter was advanced to the RML medial (B5) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by augmented fluoroscopy. Transbronchial forceps biopsies (7 specimens), transbronchial needle aspiration (2 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed malignant - nsclc nos.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 87 minutes. Attending physician: David Kim, MD."""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.0mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 1)},
    
    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire needle", 1)},
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 2)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "augmented fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "(2)", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Paragraph 4
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},

    # Footer
    {"label": "CTX_TIME", **get_span(text_1, "87 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)