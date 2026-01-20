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
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3833354
# ==========================================
id_1 = "3833354"
text_1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Thomas Henderson, a 45-year-old male patient, presented to Academic Health System [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Sarah Chen, MD, with Emily Chen assisting.

The clinical indication for this procedure was lung nodule evaluation with mediastinal lymphadenopathy workup. Preprocedural imaging had demonstrated a 30.2 millimeter ground-glass pulmonary nodule located in the LUL lobe, specifically within the inferior lingula (B5) segment. The lesion exhibited a positive bronchus sign on computed tomography. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 34 pack-years as a former smoker. The American Society of Anesthesiologists physical status classification was 4.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 08:30.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC190F bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 4R, a heterogeneous lymph node was id[REDACTED] measuring 22.1 millimeters in short axis and 22.1 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported atypical cells. At station 2R, a heterogeneous lymph node was id[REDACTED] measuring 14.8 millimeters in short axis and 16.0 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy. At station 2L, a homogeneous lymph node was id[REDACTED] measuring 15.4 millimeters in short axis and 34.5 millimeters in long axis. The node appeared round in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported granuloma. At station 10L, a homogeneous lymph node was id[REDACTED] measuring 10.7 millimeters in short axis and 16.3 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Monarch robotic bronchoscopy system, manufactured by Auris Health (J&J), was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 2.2 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the LUL inferior lingula (B5). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a eccentric view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using cbct.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 8 specimens. Transbronchial needle aspiration was performed with 4 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported malignant - small cell carcinoma. Finally, bronchoalveolar lavage was performed from the LUL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 10:08, for a total procedure time of 98 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Sarah Chen, MD
Interventional Pulmonology"""

entities_1 = [
    # --- Procedures ---
    {"label": "PROC_METHOD", **get_span(text_1, "combined bronchoscopic procedure", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided mediastinal staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "bronchial brushing", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "bronchoalveolar lavage", 1)},

    # --- Anatomy ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "inferior lingula (B5) segment", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10L", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL lobe", 2)},

    # --- Findings ---
    {"label": "OBS_FINDING", **get_span(text_1, "lung nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "mediastinal lymphadenopathy", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass pulmonary nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "positive bronchus sign", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "no endobronchial abnormalities", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous lymph node", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "atypical cells", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous lymph node", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "suspicious for malignancy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous lymph node", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "granuloma", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous lymph node", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "malignant - adenocarcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "eccentric view", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "malignant - small cell carcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "No complications", 1)},

    # --- Measurements ---
    {"label": "MEAS_SIZE", **get_span(text_1, "30.2 millimeter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 millimeter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.1 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.1 millimeters", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.0 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.4 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "34.5 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10.7 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.3 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.2 millimeters", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "08:30", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "10:08", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "98 minutes", 1)},

    # --- Devices ---
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 4)},

    # --- Specimens ---
    {"label": "SPECIMEN", **get_span(text_1, "specimens", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "specimens", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "specimens", 3)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)