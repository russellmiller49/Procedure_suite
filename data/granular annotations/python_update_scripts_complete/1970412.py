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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1970412
# ==========================================
text_1970412 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Susan Rodriguez, a 46-year-old male patient, presented to Baptist Medical Center [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Lisa Thompson, MD, with Jason Park assisting.

The clinical indication for this procedure was lung nodule evaluation with mediastinal lymphadenopathy workup. Preprocedural imaging had demonstrated a 30.4 millimeter solid pulmonary nodule located in the RML lobe, specifically within the lateral (B4) segment. The lesion exhibited a negative bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 13.0. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 46 pack-years as a former smoker. The American Society of Anesthesiologists physical status classification was 2.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 09:30.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC260F-OL8 bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 2R, a heterogeneous lymph node was id[REDACTED] measuring 15.3 millimeters in short axis and 24.4 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes. At station 11R, a heterogeneous lymph node was id[REDACTED] measuring 23.0 millimeters in short axis and 31.5 millimeters in long axis. The node appeared round in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes, no malignancy. At station 4R, a heterogeneous lymph node was id[REDACTED] measuring 15.0 millimeters in short axis and 25.3 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 7, a heterogeneous lymph node was id[REDACTED] measuring 13.7 millimeters in short axis and 16.2 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Monarch robotic bronchoscopy system, manufactured by Auris Health (J&J), was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 2.6 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RML lateral (B4). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a adjacent view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using radial ebus.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 4 specimens. Transbronchial needle aspiration was performed with 2 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported suspicious for malignancy. Finally, bronchoalveolar lavage was performed from the RML lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 10:49, for a total procedure time of 79 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Lisa Thompson, MD
Interventional Pulmonology"""

entities_1970412 = [
    # Indications & Findings
    {"label": "OBS_LESION", **get_span(text_1970412, "lung nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1970412, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "30.4 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_1970412, "pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1970412, "RML lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1970412, "lateral (B4) segment", 1)},
    
    # Procedure Methods & Tools
    {"label": "PROC_METHOD", **get_span(text_1970412, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1970412, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1970412, "peripheral lung biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "8.0 millimeter", 1)},
    {"label": "CTX_TIME", **get_span(text_1970412, "09:30", 1)},
    {"label": "PROC_METHOD", **get_span(text_1970412, "linear endobronchial ultrasound", 1)},
    
    # EBUS Staging - Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1970412, "station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "15.3 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "24.4 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1970412, "22-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1970412, "3 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1970412, "lymphocytes", 1)},
    
    # EBUS Staging - Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1970412, "station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "23.0 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "31.5 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1970412, "22-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1970412, "3 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1970412, "lymphocytes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1970412, "no malignancy", 1)},
    
    # EBUS Staging - Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1970412, "station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "15.0 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "25.3 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1970412, "22-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1970412, "3 aspiration passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1970412, "malignant - nsclc nos", 1)},
    
    # EBUS Staging - Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1970412, "station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "13.7 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "16.2 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1970412, "22-gauge needle", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1970412, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1970412, "lymphocytes", 3)},

    # Robotic Phase
    {"label": "PROC_METHOD", **get_span(text_1970412, "robotic bronchoscopy", 2)},
    {"label": "PROC_METHOD", **get_span(text_1970412, "Monarch robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_1970412, "CT-to-body", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1970412, "2.6 millimeters", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1970412, "RML lateral (B4)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1970412, "radial endobronchial ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_1970412, "target lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_1970412, "radial ebus", 1)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1970412, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1970412, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1970412, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1970412, "2 passes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1970412, "Two", 1)}, # context: Two bronchial brushing specimens
    {"label": "PROC_ACTION", **get_span(text_1970412, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_1970412, "suspicious for malignancy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1970412, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1970412, "RML lobe", 2)},

    # Outcomes
    {"label": "CTX_TIME", **get_span(text_1970412, "10:49", 1)},
    {"label": "CTX_TIME", **get_span(text_1970412, "79 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1970412, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_1970412, "ten milliliters", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1970412, "no evidence of pneumothorax", 1)},
]

BATCH_DATA.append({"id": "1970412", "text": text_1970412, "entities": entities_1970412})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)