import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from within the repository structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts module
# This assumes a structure like:
# repo_root/
#   scripts/
#     add_training_case.py (contains add_case function)
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for local testing if strict structure isn't present
    print("Warning: Could not import 'add_case'. Creating mock function for display.")
    def add_case(case_id, text, entities, root):
        print(f"Would process case: {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
        
    Returns:
        dict: {'start': start_index, 'end': end_index}
        
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
            
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 4691776
# ==========================================
t1 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Joyce Sullivan, a 77-year-old female patient, presented to Baptist Medical Center [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by Jennifer Walsh, MD, with Marcus Williams assisting.

The clinical indication for this procedure was lung cancer staging - suspected nsclc with mediastinal lymphadenopathy. Preprocedural imaging had demonstrated a 23.2 millimeter ground-glass pulmonary nodule located in the LLL lobe, specifically within the lateral basal (B9) segment. The lesion exhibited a positive bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 16.0. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 55 pack-years as a current smoker. The American Society of Anesthesiologists physical status classification was 3.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 08:45.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC180F bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 11R, a homogeneous lymph node was id[REDACTED] measuring 13.7 millimeters in short axis and 15.8 millimeters in long axis. The node appeared irregular in shape. Using the 19-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported suspicious for malignancy. At station 2L, a heterogeneous lymph node was id[REDACTED] measuring 8.4 millimeters in short axis and 22.4 millimeters in long axis. The node appeared irregular in shape. Using the 19-gauge needle, 2 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - nsclc nos. At station 4L, a heterogeneous lymph node was id[REDACTED] measuring 19.6 millimeters in short axis and 18.4 millimeters in long axis. The node appeared irregular in shape. Using the 19-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Galaxy robotic bronchoscopy system, manufactured by Noah Medical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 2.8 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the LLL lateral basal (B9). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a eccentric view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using radial ebus.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 7 specimens. Transbronchial needle aspiration was performed with 2 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported suspicious for malignancy. Finally, bronchoalveolar lavage was performed from the LLL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 10:30, for a total procedure time of 105 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

Jennifer Walsh, MD
Interventional Pulmonology"""

e1 = [
    # --- Introduction & Indications ---
    {"label": "PROC_METHOD", **get_span(t1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nsclc", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "23.2 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(t1, "pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LLL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "lateral basal (B9) segment", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "positive bronchus sign", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "hypermetabolic activity", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 2)}, # "peripheral nodule" in last sentence of paragraph
    {"label": "OBS_LESION", **get_span(t1, "mediastinal lymphadenopathy", 2)},

    # --- History ---
    {"label": "CTX_HISTORICAL", **get_span(t1, "smoking history", 1)},

    # --- Procedure Start & Airway ---
    {"label": "PROC_ACTION", **get_span(t1, "intubated", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "8.0 millimeter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "endotracheal tube", 1)},
    {"label": "CTX_TIME", **get_span(t1, "08:45", 1)},

    # --- EBUS Component ---
    {"label": "PROC_METHOD", **get_span(t1, "linear endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Olympus BF-UC180F bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "airway inspection", 1)},

    # --- Station 11R ---
    {"label": "ANAT_LN_STATION", **get_span(t1, "station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "13.7 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "15.8 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "19-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "suspicious for malignancy", 1)},

    # --- Station 2L ---
    {"label": "ANAT_LN_STATION", **get_span(t1, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "8.4 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "22.4 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "19-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "malignant - nsclc nos", 1)},

    # --- Station 4L ---
    {"label": "ANAT_LN_STATION", **get_span(t1, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "19.6 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "18.4 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "19-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(t1, "4 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "malignant - adenocarcinoma", 1)},

    # --- Robotic Component ---
    {"label": "PROC_METHOD", **get_span(t1, "robotic bronchoscopy", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LLL lateral basal (B9)", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "twenty-megahertz radial endobronchial ultrasound probe", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 5)}, # "eccentric view of the target lesion"
    {"label": "PROC_METHOD", **get_span(t1, "radial ebus", 1)},

    # --- Sampling & Lavage ---
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "suspicious for malignancy", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LLL lobe", 2)},

    # --- Outcomes ---
    {"label": "CTX_TIME", **get_span(t1, "10:30", 1)},
    {"label": "CTX_TIME", **get_span(t1, "105 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "ten milliliters", 1)},
]
BATCH_DATA.append({"id": "4691776", "text": t1, "entities": e1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)