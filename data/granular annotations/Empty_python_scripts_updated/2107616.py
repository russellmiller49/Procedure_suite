import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 2107616
# ==========================================
id_1 = "2107616"
text_1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], [REDACTED], a 60-year-old male patient, presented to Presbyterian Hospital [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Brian O'Connor, MD.

The clinical indication for this procedure was lung cancer staging - suspected nsclc with mediastinal lymphadenopathy. Preprocedural imaging had demonstrated a 15.4 millimeter ground-glass pulmonary nodule located in the RML lobe, specifically within the lateral (B4) segment. The lesion exhibited a positive bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 4.3. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 47 pack-years as a former smoker. The American Society of Anesthesiologists physical status classification was 2.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 09:00.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Fujifilm EB-580S bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 10R, a homogeneous lymph node was id[REDACTED] measuring 15.1 millimeters in short axis and 29.1 millimeters in long axis. The node appeared irregular in shape. Using the 21-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes. At station 4L, a homogeneous lymph node was id[REDACTED] measuring 21.5 millimeters in short axis and 25.6 millimeters in long axis. The node appeared oval in shape. Using the 21-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes, no malignancy. At station 4R, a heterogeneous lymph node was id[REDACTED] measuring 12.6 millimeters in short axis and 19.0 millimeters in long axis. The node appeared round in shape. Using the 21-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy. At station 11L, a heterogeneous lymph node was id[REDACTED] measuring 22.8 millimeters in short axis and 27.5 millimeters in long axis. The node appeared irregular in shape. Using the 21-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes, no malignancy.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Monarch robotic bronchoscopy system, manufactured by Auris Health (J&J), was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 2.5 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RML lateral (B4). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a adjacent view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using radial ebus.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 7 specimens. Transbronchial needle aspiration was performed with 4 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported atypical cells. Finally, bronchoalveolar lavage was performed from the RML lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 10:45, for a total procedure time of 105 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Brian O'Connor, MD
Interventional Pulmonology"""

entities_1 = [
    # Indication / Findings
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lateral (B4) segment", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.4 millimeter", 1)},
    
    # Procedure Methods
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear endobronchial ultrasound", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.1 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.1 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # "3 aspiration passes"
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes", 1)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.5 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "25.6 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # "2 aspiration passes"
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.6 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.0 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 4)}, # "2 aspiration passes"
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.8 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.5 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)}, # "4 aspiration passes"
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 2)},

    # Robotic / Peripheral
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML lateral (B4)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},

    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 1)}, # "7 specimens"
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 4)}, # "4 passes"
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML lobe", 2)},

    # Outcomes
    {"label": "CTX_TIME", **get_span(text_1, "105 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "less than ten milliliters", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no evidence of pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)