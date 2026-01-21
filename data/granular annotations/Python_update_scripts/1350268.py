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
# 3. Data Definitions
# ==========================================
BATCH_DATA = []

# -------------------------------------------------------------------------
# Note: 1350268
# -------------------------------------------------------------------------
id_1350268 = "1350268"
text_1350268 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Jonathan Wood, a 54-year-old female patient, presented to Memorial Hospital [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Michael Rodriguez, MD.

The clinical indication for this procedure was right upper lobe mass with ipsilateral mediastinal nodes. Preprocedural imaging had demonstrated a 28.6 millimeter ground-glass pulmonary nodule located in the RLL lobe, specifically within the lateral basal (B9) segment. The lesion exhibited a negative bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 8.9. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 36 pack-years as a former smoker. The American Society of Anesthesiologists physical status classification was 4.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 09:30.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC260F-OL8 bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 10R, a heterogeneous lymph node was id[REDACTED] measuring 17.1 millimeters in short axis and 25.9 millimeters in long axis. The node appeared oval in shape. Using the 21-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported atypical cells. At station 11R, a homogeneous lymph node was id[REDACTED] measuring 8.4 millimeters in short axis and 34.2 millimeters in long axis. The node appeared round in shape. Using the 21-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported granuloma. At station 11L, a homogeneous lymph node was id[REDACTED] measuring 22.2 millimeters in short axis and 34.6 millimeters in long axis. The node appeared irregular in shape. Using the 21-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma. At station 2R, a heterogeneous lymph node was id[REDACTED] measuring 21.9 millimeters in short axis and 28.9 millimeters in long axis. The node appeared round in shape. Using the 21-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported atypical cells. At station 4L, a homogeneous lymph node was id[REDACTED] measuring 18.5 millimeters in short axis and 22.0 millimeters in long axis. The node appeared irregular in shape. Using the 21-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported granuloma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Ion robotic bronchoscopy system, manufactured by Intuitive Surgical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 2.6 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RLL lateral basal (B9). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a adjacent view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using augmented fluoroscopy.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 5 specimens. Transbronchial needle aspiration was performed with 4 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported malignant - adenocarcinoma. Finally, bronchoalveolar lavage was performed from the RLL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 11:02, for a total procedure time of 92 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Michael Rodriguez, MD
Interventional Pulmonology"""

entities_1350268 = [
    # Indication / Findings
    {"label": "PROC_METHOD", **get_span(text_1350268, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1350268, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1350268, "peripheral lung biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1350268, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1350268, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1350268, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1350268, "lateral basal (B9) segment", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "28.6 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_1350268, "pulmonary nodule", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1350268, "bronchus", 1)}, # negative bronchus sign
    {"label": "OBS_LESION", **get_span(text_1350268, "nodule", 2)}, # peripheral nodule

    # Procedure Start / EBUS
    {"label": "MEAS_SIZE", **get_span(text_1350268, "8.0 millimeter", 1)},
    {"label": "CTX_TIME", **get_span(text_1350268, "09:30", 1)},
    {"label": "PROC_METHOD", **get_span(text_1350268, "linear endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1350268, "Olympus BF-UC260F-OL8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1350268, "bronchoscope", 1)}, # Fixed: Only 1 occurrence found in text

    # EBUS Stations
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1350268, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "17.1 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "25.9 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1350268, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1350268, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "2", 5)}, # "2 aspiration passes"
    {"label": "PROC_ACTION", **get_span(text_1350268, "aspiration", 1)},
    {"label": "OBS_ROSE", **get_span(text_1350268, "atypical cells", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1350268, "station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "8.4 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "34.2 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1350268, "21-gauge", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "2", 6)}, # Next "2" in "2 aspiration passes"
    {"label": "PROC_ACTION", **get_span(text_1350268, "aspiration", 2)},
    {"label": "OBS_ROSE", **get_span(text_1350268, "granuloma", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1350268, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "22.2 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "34.6 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1350268, "21-gauge", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "4", 3)},
    {"label": "PROC_ACTION", **get_span(text_1350268, "aspiration", 3)},
    {"label": "OBS_ROSE", **get_span(text_1350268, "malignant - adenocarcinoma", 1)},

    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1350268, "station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "21.9 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "28.9 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1350268, "21-gauge", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "4", 4)},
    {"label": "PROC_ACTION", **get_span(text_1350268, "aspiration", 4)},
    {"label": "OBS_ROSE", **get_span(text_1350268, "atypical cells", 2)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1350268, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "18.5 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1350268, "22.0 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1350268, "21-gauge", 5)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "4", 5)},
    {"label": "PROC_ACTION", **get_span(text_1350268, "aspiration", 5)},
    {"label": "OBS_ROSE", **get_span(text_1350268, "granuloma", 2)},

    # Robotic Phase
    {"label": "PROC_METHOD", **get_span(text_1350268, "robotic bronchoscopy", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1350268, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1350268, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1350268, "lateral basal (B9)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1350268, "radial endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1350268, "probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1350268, "augmented fluoroscopy", 1)},

    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1350268, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1350268, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "5", 3)},
    {"label": "SPECIMEN", **get_span(text_1350268, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1350268, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "4", 6)},
    {"label": "MEAS_COUNT", **get_span(text_1350268, "Two", 1)},
    {"label": "PROC_ACTION", **get_span(text_1350268, "bronchial brushing", 1)},
    {"label": "SPECIMEN", **get_span(text_1350268, "specimens", 2)},
    {"label": "OBS_ROSE", **get_span(text_1350268, "malignant - adenocarcinoma", 2)},
    {"label": "PROC_ACTION", **get_span(text_1350268, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1350268, "RLL", 3)},

    # Outcome
    {"label": "CTX_TIME", **get_span(text_1350268, "11:02", 1)},
    {"label": "CTX_TIME", **get_span(text_1350268, "92 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1350268, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_1350268, "ten milliliters", 1)},
]

BATCH_DATA.append({"id": id_1350268, "text": text_1350268, "entities": entities_1350268})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)