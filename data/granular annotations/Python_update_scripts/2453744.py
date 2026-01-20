import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add cases
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback to assume script is run from the root if module not found
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The occurrence number (1-based).
        
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
# Note 1: 2453744
# ==========================================
id_1 = "2453744"
text_1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Julie Mitchell, a 82-year-old male patient, presented to Academic Health System [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Rachel Goldman, MD.

The clinical indication for this procedure was peripheral nodule and bilateral hilar adenopathy. Preprocedural imaging had demonstrated a 14.0 millimeter ground-glass pulmonary nodule located in the LUL lobe, specifically within the apicoposterior (B1+2) segment. The lesion exhibited a negative bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 17.6. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 34 pack-years as a current smoker. The American Society of Anesthesiologists physical status classification was 2.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 08:15.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Pentax EB-1990i bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 2L, a homogeneous lymph node was id[REDACTED] measuring 14.8 millimeters in short axis and 28.3 millimeters in long axis. The node appeared round in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported atypical cells. At station 4L, a homogeneous lymph node was id[REDACTED] measuring 24.3 millimeters in short axis and 25.6 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - squamous cell carcinoma. At station 10R, a heterogeneous lymph node was id[REDACTED] measuring 12.9 millimeters in short axis and 30.7 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 10L, a heterogeneous lymph node was id[REDACTED] measuring 18.8 millimeters in short axis and 34.6 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy. At station 11L, a heterogeneous lymph node was id[REDACTED] measuring 18.7 millimeters in short axis and 20.8 millimeters in long axis. The node appeared round in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Ion robotic bronchoscopy system, manufactured by Intuitive Surgical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.5 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the LUL apicoposterior (B1+2). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a concentric view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using fluoroscopy.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 7 specimens. Transbronchial needle aspiration was performed with 2 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported adequate lymphocytes, no malignancy. Finally, bronchoalveolar lavage was performed from the LUL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 10:09, for a total procedure time of 114 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Rachel Goldman, MD
Interventional Pulmonology"""

entities_1 = [
    # Procedure Methods & Actions
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear endobronchial ultrasound", 1)},
    
    # Anatomy & Indications
    {"label": "OBS_LESION", **get_span(text_1, "peripheral nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "adenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.0 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "apicoposterior (B1+2) segment", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hypermetabolic activity", 1)},

    # EBUS Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.3 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},

    # EBUS Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.3 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "25.6 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - squamous cell carcinoma", 1)},

    # EBUS Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.9 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.7 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # EBUS Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.8 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "34.6 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},

    # EBUS Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.7 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.8 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 5)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 aspiration passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},

    # Robotic/Peripheral Phase
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL apicoposterior (B1+2)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    
    # Sampling & Results
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushing", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "Two", 1)}, # For brushing specimens
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL lobe", 2)},

    # Timeline & Outcome
    {"label": "CTX_TIME", **get_span(text_1, "114 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)