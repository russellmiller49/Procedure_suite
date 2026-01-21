import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from inside a subdirectory of the repo
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the add_case utility
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback to appending path if module resolution fails
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 1377952
# ==========================================
text_1377952 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], [REDACTED], a 41-year-old male patient, presented to Memorial Hospital [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Robert Patel, MD, with Priya Sharma assisting.

The clinical indication for this procedure was peripheral lung nodule with suspicious mediastinal nodes. Preprocedural imaging had demonstrated a 24.3 millimeter solid pulmonary nodule located in the LUL lobe, specifically within the superior lingula (B4) segment. The lesion exhibited a negative bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 12.7. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 49 pack-years as a current smoker. The American Society of Anesthesiologists physical status classification was 4.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 08:30.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Pentax EB-1990i bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 4L, a homogeneous lymph node was id[REDACTED] measuring 21.5 millimeters in short axis and 32.3 millimeters in long axis. The node appeared round in shape. Using the 21-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 10L, a homogeneous lymph node was id[REDACTED] measuring 21.1 millimeters in short axis and 12.4 millimeters in long axis. The node appeared irregular in shape. Using the 21-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 11L, a homogeneous lymph node was id[REDACTED] measuring 8.8 millimeters in short axis and 15.4 millimeters in long axis. The node appeared oval in shape. Using the 21-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - squamous cell carcinoma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Ion robotic bronchoscopy system, manufactured by Intuitive Surgical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.5 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the LUL superior lingula (B4). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a eccentric view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using augmented fluoroscopy.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 4 specimens. Transbronchial needle aspiration was performed with 2 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported adequate lymphocytes. Finally, bronchoalveolar lavage was performed from the LUL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 10:18, for a total procedure time of 108 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Robert Patel, MD
Interventional Pulmonology"""

entities_1377952 = [
    # Procedure/Method/Action
    {"label": "PROC_METHOD", **get_span(text_1377952, "bronchoscopic procedure", 1)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1377952, "mediastinal staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1377952, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "linear endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "robotic bronchoscopy", 2)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "CT-to-body", 1)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1377952, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1377952, "Transbronchial forceps biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1377952, "Transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1377952, "bronchial brushing", 1)},
    {"label": "PROC_ACTION", **get_span(text_1377952, "bronchoalveolar lavage", 1)},
    
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_1377952, "LUL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1377952, "superior lingula (B4)", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1377952, "bronchial tree", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1377952, "station 4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1377952, "station 10L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1377952, "station 11L", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1377952, "LUL superior lingula (B4)", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1377952, "LUL lobe", 2)},

    # Devices
    {"label": "DEV_INSTRUMENT", **get_span(text_1377952, "endotracheal tube", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1377952, "Pentax EB-1990i bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1377952, "21-gauge needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1377952, "21-gauge needle", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1377952, "21-gauge needle", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1377952, "Ion robotic bronchoscopy system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1377952, "robotic catheter", 1)},
    
    # Observations / Findings / Lesions
    {"label": "OBS_LESION", **get_span(text_1377952, "peripheral lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1377952, "suspicious mediastinal nodes", 1)},
    {"label": "OBS_LESION", **get_span(text_1377952, "solid pulmonary nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1377952, "negative bronchus sign", 1)},
    {"label": "OBS_FINDING", **get_span(text_1377952, "hypermetabolic activity", 1)},
    {"label": "OBS_FINDING", **get_span(text_1377952, "no endobronchial abnormalities", 1)},
    {"label": "OBS_ROSE", **get_span(text_1377952, "malignant - nsclc nos", 1)},
    {"label": "OBS_ROSE", **get_span(text_1377952, "malignant - nsclc nos", 2)},
    {"label": "OBS_ROSE", **get_span(text_1377952, "malignant - squamous cell carcinoma", 1)},
    {"label": "OBS_ROSE", **get_span(text_1377952, "adequate lymphocytes", 1)},

    # Measurements
    {"label": "MEAS_SIZE", **get_span(text_1377952, "24.3 millimeter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1377952, "8.0 millimeter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1377952, "21.5 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1377952, "32.3 millimeters", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1377952, "2", 1)}, # 2 aspiration passes
    {"label": "MEAS_SIZE", **get_span(text_1377952, "21.1 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1377952, "12.4 millimeters", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1377952, "2", 2)}, # 2 aspiration passes
    {"label": "MEAS_SIZE", **get_span(text_1377952, "8.8 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1377952, "15.4 millimeters", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1377952, "3", 1)}, # 3 aspiration passes
    {"label": "MEAS_SIZE", **get_span(text_1377952, "1.5 millimeters", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1377952, "4", 3)}, # 4 specimens (Skip 4L, ASA 4)
    {"label": "MEAS_COUNT", **get_span(text_1377952, "2", 3)}, # 2 passes TBNA
    {"label": "MEAS_TIME", **get_span(text_1377952, "108 minutes", 1)},
    {"label": "MEAS_VOL", **get_span(text_1377952, "ten milliliters", 1)},

    # Context / Outcomes
    {"label": "CTX_TIME", **get_span(text_1377952, "08:30", 1)},
    {"label": "CTX_TIME", **get_span(text_1377952, "10:18", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1377952, "No complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1377952, "no significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1377952, "no evidence of pneumothorax", 1)},
]

BATCH_DATA.append({"id": "1377952", "text": text_1377952, "entities": entities_1377952})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)