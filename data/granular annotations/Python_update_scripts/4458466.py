import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4458466
# ==========================================
id_1 = "4458466"
text_1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Brandon Reed, a 56-year-old male patient, presented to Baptist Medical Center [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Amanda Foster, MD.

The clinical indication for this procedure was lung nodule evaluation with mediastinal lymphadenopathy workup. Preprocedural imaging had demonstrated a 27.1 millimeter solid pulmonary nodule located in the RLL lobe, specifically within the superior (B6) segment. The lesion exhibited a negative bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 6.1. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a negative smoking history. The American Society of Anesthesiologists physical status classification was 3.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 09:15.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC190F bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 4L, a heterogeneous lymph node was id[REDACTED] measuring 9.1 millimeters in short axis and 13.1 millimeters in long axis. The node appeared oval in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy. At station 2R, a heterogeneous lymph node was id[REDACTED] measuring 14.9 millimeters in short axis and 15.8 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 2L, a homogeneous lymph node was id[REDACTED] measuring 13.2 millimeters in short axis and 25.8 millimeters in long axis. The node appeared irregular in shape. Using the 22-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes, no malignancy.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Ion robotic bronchoscopy system, manufactured by Intuitive Surgical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.8 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the RLL superior (B6). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a adjacent view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using augmented fluoroscopy.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 5 specimens. Transbronchial needle aspiration was performed with 2 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported malignant - squamous cell carcinoma. Finally, bronchoalveolar lavage was performed from the RLL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 11:03, for a total procedure time of 108 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Amanda Foster, MD
Interventional Pulmonology"""

entities_1 = [
    # Indications & Lesions
    {"label": "OBS_LESION", **get_span(text_1, "lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.1 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "superior (B6) segment", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "negative bronchus sign", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hypermetabolic activity", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "peripheral nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 2)},

    # Procedure Start & Airway
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinal staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "intubated", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 millimeter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "09:15", 1)},

    # EBUS & Staging
    {"label": "PROC_ACTION", **get_span(text_1, "mediastinal lymph node evaluation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "airway inspection", 1)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 4L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "heterogeneous lymph node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "9.1 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.1 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)},  # '3' aspiration passes
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},

    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "heterogeneous lymph node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.9 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.8 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "homogeneous lymph node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.2 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "25.8 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 1)},

    # Robotic Phase
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lesion sampling", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CT-to-body", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8 millimeters", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "radial endobronchial ultrasound probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "augmented fluoroscopy", 1)},

    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - squamous cell carcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lobe", 2)},

    # Completion & Outcomes
    {"label": "CTX_TIME", **get_span(text_1, "11:03", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "108 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "ten milliliters", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "pneumothorax", 1)}, # In context of "no evidence of"
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)