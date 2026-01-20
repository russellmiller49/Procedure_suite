import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case: 4848028
# ==========================================
id_1 = "4848028"
text_1 = """Andrew Jones, MRN [REDACTED], a 72-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Community Hospital on [REDACTED]. The indication was right upper lobe mass with ipsilateral mediastinal nodes with a 20.2mm solid lesion in the LUL inferior lingula (B5), bronchus sign positive, PET SUV max 16.9. The patient was ASA class 3 with smoking history of 43 pack-years (current). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Pentax EB-1990i bronchoscope with 21-gauge Standard FNA needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 4L (24.4mm, 2 passes, ROSE: Adequate lymphocytes, no malignancy); station 7 (20.3mm, 3 passes, ROSE: Adequate lymphocytes, no malignancy); station 10R (20.4mm, 4 passes, ROSE: Atypical cells). Rapid on-site evaluation was available for all stations.

The Galaxy robotic bronchoscopy system (Noah Medical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 2.3mm. The robotic catheter was advanced to the LUL inferior lingula (B5) and radial EBUS probe deployment revealed concentric view of the lesion. Tool-in-lesion was confirmed by radial ebus. Transbronchial forceps biopsies (7 specimens), transbronchial needle aspiration (4 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed malignant - small cell carcinoma.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 113 minutes. Attending physician: Rachel Goldman, MD."""

entities_1 = [
    # Paragraph 1
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)}, # mediastinal staging
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)}, # mediastinal nodes
    {"label": "OBS_LESION", **get_span(text_1, "nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.2mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign positive", 1)},
    
    # Paragraph 2
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 3)}, # mediastinal and hilar
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # Paragraph 3
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy robotic bronchoscopy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric view", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 2)}, # in '7 specimens'
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 4)}, # in 'brushings (2)'
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - small cell carcinoma", 1)},

    # Paragraph 4
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
    
    # Paragraph 5
    {"label": "CTX_TIME", **get_span(text_1, "113 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)