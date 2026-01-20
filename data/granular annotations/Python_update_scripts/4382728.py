import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact substring to find.
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary containing 'text', 'start', and 'end'.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Case 1: 4382728
# ==========================================
id_4382728 = "4382728"
text_4382728 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Ashley Sanders, a 68-year-old male patient, presented to Northwestern Memorial Hospital [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Brian O'Connor, MD, with Kevin Chang assisting.

The clinical indication for this procedure was right upper lobe mass with ipsilateral mediastinal nodes. Preprocedural imaging had demonstrated a 29.4 millimeter part-solid pulmonary nodule located in the LLL lobe, specifically within the lateral basal (B9) segment. The lesion exhibited a negative bronchus sign on computed tomography. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 43 pack-years as a current smoker. The American Society of Anesthesiologists physical status classification was 3.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 10:15.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Pentax EB-1990i bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 10R, a homogeneous lymph node was id[REDACTED] measuring 15.5 millimeters in short axis and 31.6 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy. At station 10L, a heterogeneous lymph node was id[REDACTED] measuring 21.7 millimeters in short axis and 14.6 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes. At station 11R, a homogeneous lymph node was id[REDACTED] measuring 20.5 millimeters in short axis and 29.9 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Ion robotic bronchoscopy system, manufactured by Intuitive Surgical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.8 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the LLL lateral basal (B9). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a adjacent view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using fluoroscopy.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 6 specimens. Transbronchial needle aspiration was performed with 2 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported malignant - squamous cell carcinoma. Finally, bronchoalveolar lavage was performed from the LLL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 11:36, for a total procedure time of 81 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Brian O'Connor, MD
Interventional Pulmonology"""

entities_4382728 = [
    # Indications & Diagnosis
    {"label": "ANAT_LUNG_LOC", **get_span(text_4382728, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_4382728, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4382728, "mediastinal nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4382728, "29.4 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_4382728, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4382728, "LLL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4382728, "lateral basal (B9) segment", 1)},
    {"label": "OBS_FINDING", **get_span(text_4382728, "negative bronchus sign", 1)},

    # Procedure Info
    {"label": "PROC_METHOD", **get_span(text_4382728, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_4382728, "mediastinal staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_4382728, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4382728, "peripheral lung biopsy", 1)},
    {"label": "CTX_TIME", **get_span(text_4382728, "10:15", 1)},
    
    # EBUS Component
    {"label": "PROC_ACTION", **get_span(text_4382728, "systematic mediastinal lymph node evaluation", 1)},
    {"label": "PROC_METHOD", **get_span(text_4382728, "linear endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4382728, "Pentax EB-1990i bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_4382728, "airway inspection", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_4382728, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4382728, "15.5 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4382728, "31.6 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4382728, "22-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4382728, "3 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4382728, "suspicious for malignancy", 1)},
    
    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_4382728, "station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4382728, "21.7 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4382728, "14.6 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4382728, "22-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_4382728, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4382728, "adequate lymphocytes", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_4382728, "station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4382728, "20.5 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4382728, "29.9 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4382728, "22-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_4382728, "3 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_4382728, "malignant - nsclc nos", 1)},

    # Robotic Component
    {"label": "PROC_METHOD", **get_span(text_4382728, "robotic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(text_4382728, "peripheral lesion sampling", 1)},
    {"label": "PROC_METHOD", **get_span(text_4382728, "Ion robotic bronchoscopy system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4382728, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4382728, "LLL lateral basal (B9)", 1)},
    {"label": "PROC_METHOD", **get_span(text_4382728, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_4382728, "fluoroscopy", 1)},

    # Peripheral Sampling
    {"label": "DEV_INSTRUMENT", **get_span(text_4382728, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_4382728, "biopsies", 1)}, # Context: Transbronchial forceps biopsies
    {"label": "MEAS_COUNT", **get_span(text_4382728, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_4382728, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4382728, "2 passes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4382728, "Two", 1)}, # Context: Two bronchial brushing specimens
    {"label": "PROC_ACTION", **get_span(text_4382728, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_4382728, "malignant - squamous cell carcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_4382728, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4382728, "LLL lobe", 2)},

    # Completion / Outcomes
    {"label": "CTX_TIME", **get_span(text_4382728, "11:36", 1)},
    {"label": "CTX_TIME", **get_span(text_4382728, "81 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4382728, "No complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4382728, "hemostasis was achieved", 1)},
    {"label": "MEAS_VOL", **get_span(text_4382728, "less than ten milliliters", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4382728, "no evidence of pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_4382728, "text": text_4382728, "entities": entities_4382728})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)