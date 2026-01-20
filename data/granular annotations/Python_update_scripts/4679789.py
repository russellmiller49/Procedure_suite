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
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# -------------------------------------------------------------------------
# Case 1: 4679789
# -------------------------------------------------------------------------
text_4679789 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Nancy Gray, a 72-year-old female patient, presented to Veterans Affairs Medical Center [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Brian O'Connor, MD, with Jessica Martinez assisting.

The clinical indication for this procedure was mediastinal staging for biopsy-proven lung adenocarcinoma. Preprocedural imaging had demonstrated a 22.6 millimeter solid pulmonary nodule located in the RUL lobe, specifically within the apical (B1) segment. The lesion exhibited a negative bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 9.7. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a negative smoking history. The American Society of Anesthesiologists physical status classification was 3.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 07:45.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC190F bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 11R, a homogeneous lymph node was id[REDACTED] measuring 24.9 millimeters in short axis and 17.4 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma. At station 2L, a heterogeneous lymph node was id[REDACTED] measuring 14.7 millimeters in short axis and 16.9 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 4R, a heterogeneous lymph node was id[REDACTED] measuring 13.0 millimeters in short axis and 24.5 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - small cell carcinoma. At station 11L, a heterogeneous lymph node was id[REDACTED] measuring 19.1 millimeters in short axis and 15.5 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Galaxy robotic bronchoscopy system, manufactured by Noah Medical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.8 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RUL apical (B1). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a concentric view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using cbct.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 4 specimens. Transbronchial needle aspiration was performed with 4 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported suspicious for malignancy. Finally, bronchoalveolar lavage was performed from the RUL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 09:56, for a total procedure time of 131 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Brian O'Connor, MD
Interventional Pulmonology"""

entities_4679789 = [
    # Para 1
    {"label": "PROC_METHOD", **get_span(text_4679789, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_4679789, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4679789, "peripheral lung biopsy", 1)},

    # Para 2
    {"label": "MEAS_SIZE", **get_span(text_4679789, "22.6 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_4679789, "pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4679789, "RUL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4679789, "apical (B1) segment", 1)},
    {"label": "OBS_LESION", **get_span(text_4679789, "mediastinal lymphadenopathy", 1)},

    # Para 4
    {"label": "MEAS_SIZE", **get_span(text_4679789, "8.0 millimeter", 1)},
    {"label": "CTX_TIME", **get_span(text_4679789, "07:45", 1)},

    # Para 5
    {"label": "PROC_METHOD", **get_span(text_4679789, "linear endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4679789, "bronchoscope", 1)}, # Olympus BF-UC190F

    # Para 6 - Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_4679789, "station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "24.9 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "17.4 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4679789, "22-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4679789, "3 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4679789, "malignant - adenocarcinoma", 1)},

    # Para 6 - Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_4679789, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "14.7 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "16.9 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4679789, "22-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_4679789, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4679789, "malignant - nsclc nos", 1)},

    # Para 6 - Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_4679789, "station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "13.0 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "24.5 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4679789, "22-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_4679789, "3 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_4679789, "malignant - small cell carcinoma", 1)},

    # Para 6 - Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_4679789, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "19.1 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "15.5 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4679789, "22-gauge needle", 4)},
    {"label": "MEAS_COUNT", **get_span(text_4679789, "3 aspiration passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_4679789, "suspicious for malignancy", 1)},

    # Para 7
    {"label": "PROC_METHOD", **get_span(text_4679789, "robotic bronchoscopy", 2)},
    {"label": "MEAS_SIZE", **get_span(text_4679789, "1.8 millimeters", 1)},

    # Para 8
    {"label": "ANAT_LUNG_LOC", **get_span(text_4679789, "RUL apical (B1)", 1)},
    {"label": "PROC_METHOD", **get_span(text_4679789, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_4679789, "cbct", 1)},

    # Para 9
    {"label": "DEV_INSTRUMENT", **get_span(text_4679789, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_4679789, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4679789, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_4679789, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4679789, "4 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_4679789, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_4679789, "suspicious for malignancy", 2)},
    {"label": "PROC_ACTION", **get_span(text_4679789, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4679789, "RUL lobe", 2)},

    # Para 10
    {"label": "CTX_TIME", **get_span(text_4679789, "09:56", 1)},
    {"label": "CTX_TIME", **get_span(text_4679789, "131 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4679789, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_4679789, "ten milliliters", 1)},
]

BATCH_DATA.append({"id": "4679789", "text": text_4679789, "entities": entities_4679789})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)