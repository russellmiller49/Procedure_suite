import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Note 1: 1528559
# ------------------------------------------
id_1 = "1528559"
text_1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Dorothy Price, a 53-year-old female patient, presented to Community Hospital [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Andrew Nakamura, MD, with Jessica Martinez assisting.

The clinical indication for this procedure was combined staging and peripheral nodule diagnosis. Preprocedural imaging had demonstrated a 16.3 millimeter ground-glass pulmonary nodule located in the RLL lobe, specifically within the superior (B6) segment. The lesion exhibited a positive bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 6.9. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 23 pack-years as a former smoker. The American Society of Anesthesiologists physical status classification was 2.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 08:15.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC190F bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 11L, a heterogeneous lymph node was id[REDACTED] measuring 14.4 millimeters in short axis and 23.4 millimeters in long axis. The node appeared round in shape. Using the 22-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported granuloma. At station 4L, a homogeneous lymph node was id[REDACTED] measuring 21.7 millimeters in short axis and 20.3 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 10L, a homogeneous lymph node was id[REDACTED] measuring 19.2 millimeters in short axis and 34.4 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Galaxy robotic bronchoscopy system, manufactured by Noah Medical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 3.4 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RLL superior (B6). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a adjacent view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using radial ebus.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 6 specimens. Transbronchial needle aspiration was performed with 4 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported malignant - squamous cell carcinoma. Finally, bronchoalveolar lavage was performed from the RLL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 09:49, for a total procedure time of 94 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Andrew Nakamura, MD
Interventional Pulmonology"""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.3 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "superior (B6) segment", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 3)},
    {"label": "CTX_HISTORICAL", **get_span(text_1, "former smoker", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 millimeter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "08:15", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.4 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.4 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.7 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.3 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.2 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "34.4 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - squamous cell carcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lobe", 2)},
    {"label": "CTX_TIME", **get_span(text_1, "09:49", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "94 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)