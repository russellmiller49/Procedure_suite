import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts folder
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2126665
# ==========================================
id_1 = "2126665"
text_1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], [REDACTED], a 54-year-old female patient, presented to Regional Medical Center [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by David Kim, MD, with Jessica Martinez assisting.

The clinical indication for this procedure was pet-avid lung mass and mediastinal lymphadenopathy. Preprocedural imaging had demonstrated a 23.3 millimeter solid pulmonary nodule located in the RLL lobe, specifically within the medial basal (B7) segment. The lesion exhibited a negative bronchus sign on computed tomography. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a negative smoking history. The American Society of Anesthesiologists physical status classification was 3.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 10:30.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Fujifilm EB-580S bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 2R, a heterogeneous lymph node was id[REDACTED] measuring 12.0 millimeters in short axis and 33.3 millimeters in long axis. The node appeared round in shape. Using the 22-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 10R, a heterogeneous lymph node was id[REDACTED] measuring 12.9 millimeters in short axis and 26.6 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy. At station 2L, a heterogeneous lymph node was id[REDACTED] measuring 13.9 millimeters in short axis and 22.9 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported granuloma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Galaxy robotic bronchoscopy system, manufactured by Noah Medical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.9 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RLL medial basal (B7). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a adjacent view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using radial ebus.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 5 specimens. Transbronchial needle aspiration was performed with 4 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported adequate lymphocytes, no malignancy. Finally, bronchoalveolar lavage was performed from the RLL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 12:49, for a total procedure time of 139 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

David Kim, MD
Interventional Pulmonology"""

entities_1 = [
    # Indications / Findings
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "solid pulmonary nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "peripheral nodule", 1)},
    
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "medial basal (B7)", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "medial basal (B7)", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "bronchial tree", 1)},
    
    # LN Stations
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    
    # Procedure Methods
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    
    # Procedure Actions
    {"label": "PROC_ACTION", **get_span(text_1, "staging", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "lung biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "intubated", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushing", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoalveolar lavage", 1)},

    # Devices
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},

    # Measurements
    {"label": "MEAS_SIZE", **get_span(text_1, "23.3 millimeter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 millimeter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.0 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "33.3 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.9 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "26.6 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.9 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.9 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9 millimeters", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "ten milliliters", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)}, # 4 aspiration passes
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # 3 aspiration passes
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # 2 aspiration passes
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 1)}, # 5 specimens
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)}, # 4 passes
    {"label": "MEAS_COUNT", **get_span(text_1, "Two", 1)}, # Two bronchial brushing

    # ROSE / Pathology / Observations
    {"label": "OBS_FINDING", **get_span(text_1, "no endobronchial abnormalities", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 1)},

    # Time
    {"label": "CTX_TIME", **get_span(text_1, "10:30", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "12:49", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "139 minutes", 1)},

    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no evidence of pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)