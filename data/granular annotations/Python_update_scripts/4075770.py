import sys
from pathlib import Path

# Set the repository root (assuming script is running in a subdirectory of the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is running within the repository structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a substring.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note: 4075770
# ==========================================
id_4075770 = "4075770"
text_4075770 = """BRONCHOSCOPY PROCEDURE NARRATIVE

On [REDACTED], Ronald Henderson, a 67-year-old male patient, presented to UCLA Medical Center [REDACTED] for a combined bronchoscopic procedure consisting of endobronchial ultrasound-guided mediastinal staging and robotic bronchoscopy with peripheral lung biopsy. The procedure was performed by David Kim, MD, with Kevin Chang assisting.

The clinical indication for this procedure was right upper lobe mass with ipsilateral mediastinal nodes. Preprocedural imaging had demonstrated a 27.1 millimeter ground-glass pulmonary nodule located in the LLL lobe, specifically within the posterior basal (B10) segment. The lesion exhibited a positive bronchus sign on computed tomography. Positron emission tomography scanning revealed hypermetabolic activity with a maximum standardized uptake value of 15.4. Given the combination of peripheral nodule requiring tissue diagnosis and mediastinal lymphadenopathy necessitating staging, a combined approach was deemed appropriate.

The patient's medical history included a significant smoking history of 40 pack-years as a current smoker. The American Society of Anesthesiologists physical status classification was 2.

Following the administration of general anesthesia by the anesthesiology team, the patient was intubated with a 8.0 millimeter endotracheal tube. The procedure commenced at 10:30.

The first component of the procedure involved systematic mediastinal lymph node evaluation using linear endobronchial ultrasound. The Olympus BF-UC260F-OL8 bronchoscope was advanced through the endotracheal tube, and a thorough airway inspection was performed, revealing no endobronchial abnormalities. Mediastinal and hilar lymph node stations were then surveyed systematically.

At station 2L, a heterogeneous lymph node was id[REDACTED] measuring 20.2 millimeters in short axis and 30.4 millimeters in long axis. The node appeared oval in shape. Using the 19-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - squamous cell carcinoma. At station 4R, a homogeneous lymph node was id[REDACTED] measuring 17.2 millimeters in short axis and 31.1 millimeters in long axis. The node appeared round in shape. Using the 19-gauge needle, 4 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported malignant - adenocarcinoma. At station 7, a heterogeneous lymph node was id[REDACTED] measuring 11.6 millimeters in short axis and 19.3 millimeters in long axis. The node appeared oval in shape. Using the 19-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported adequate lymphocytes. At station 11R, a heterogeneous lymph node was id[REDACTED] measuring 17.2 millimeters in short axis and 15.1 millimeters in long axis. The node appeared round in shape. Using the 19-gauge needle, 3 aspiration passes were performed. The on-site cytopathologist evaluated the specimen and reported granuloma.

Following completion of the mediastinal staging component, the procedure transitioned to robotic bronchoscopy for peripheral lesion sampling. The Ion robotic bronchoscopy system, manufactured by Intuitive Surgical, was prepared and registered using CT-to-body methodology. The registration achieved an accuracy of 1.9 millimeters, which was within acceptable parameters for proceeding with navigation.

The robotic catheter was advanced through the bronchial tree toward the target lesion in the LLL posterior basal (B10). Navigation was successful, and the catheter reached the planned trajectory endpoint. A twenty-megahertz radial endobronchial ultrasound probe was then deployed through the working channel, revealing a eccentric view of the target lesion. This confirmed appropriate positioning relative to the lesion. Additional confirmation of tool-in-lesion was obtained using radial ebus.

Tissue sampling was then performed using multiple modalities to maximize diagnostic yield. Transbronchial forceps biopsies were obtained, totaling 7 specimens. Transbronchial needle aspiration was performed with 3 passes through the lesion. Two bronchial brushing specimens were also collected. The on-site cytopathologist evaluated the peripheral specimens and reported atypical cells. Finally, bronchoalveolar lavage was performed from the LLL lobe and sent for microbiological analysis including bacterial, fungal, and acid-fast bacilli cultures.

The procedure was completed at 11:55, for a total procedure time of 85 minutes. No complications were encountered during the procedure. There was no significant bleeding, and hemostasis was achieved spontaneously. The estimated blood loss was less than ten milliliters. A post-procedure chest radiograph was obtained and demonstrated no evidence of pneumothorax or other acute abnormality.

The patient was transferred to the recovery area in stable condition. After an uneventful observation period, the patient was discharged home with standard post-bronchoscopy precautions. Follow-up was arranged for review of final pathology results.

In summary, this was a successful combined procedure achieving both mediastinal staging and peripheral lesion tissue diagnosis. The final pathology results will guide subsequent oncologic management and will be reviewed at multidisciplinary tumor board.

David Kim, MD
Interventional Pulmonology"""

entities_4075770 = [
    # --- Introduction ---
    {"label": "PROC_METHOD", **get_span(text_4075770, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_4075770, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4075770, "lung biopsy", 1)},
    
    # --- Clinical Indication ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_4075770, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_4075770, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "27.1 millimeter", 1)},
    {"label": "OBS_LESION", **get_span(text_4075770, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4075770, "LLL lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4075770, "posterior basal (B10) segment", 1)},
    {"label": "OBS_LESION", **get_span(text_4075770, "lesion", 1)}, # The lesion exhibited
    {"label": "OBS_FINDING", **get_span(text_4075770, "positive bronchus sign", 1)},
    {"label": "OBS_FINDING", **get_span(text_4075770, "hypermetabolic", 1)},
    {"label": "OBS_LESION", **get_span(text_4075770, "nodule", 2)},
    {"label": "OBS_LESION", **get_span(text_4075770, "lymphadenopathy", 1)},

    # --- History/Vitals ---
    {"label": "CTX_HISTORICAL", **get_span(text_4075770, "history of", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "8.0 millimeter", 1)},
    {"label": "CTX_TIME", **get_span(text_4075770, "10:30", 1)},

    # --- EBUS / Mediastinal Staging ---
    {"label": "PROC_METHOD", **get_span(text_4075770, "endobronchial ultrasound", 2)}, # linear ebus
    {"label": "PROC_ACTION", **get_span(text_4075770, "airway inspection", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_4075770, "station 2L", 1)},
    {"label": "OBS_FINDING", **get_span(text_4075770, "heterogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "20.2 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "30.4 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4075770, "19-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4075770, "4 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4075770, "malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_4075770, "squamous cell carcinoma", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_4075770, "station 4R", 1)},
    {"label": "OBS_FINDING", **get_span(text_4075770, "homogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "17.2 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "31.1 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4075770, "19-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_4075770, "4 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_4075770, "malignant", 2)},
    {"label": "OBS_ROSE", **get_span(text_4075770, "adenocarcinoma", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_4075770, "station 7", 1)},
    {"label": "OBS_FINDING", **get_span(text_4075770, "heterogeneous", 2)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "11.6 millimeters", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "19.3 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4075770, "19-gauge needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_4075770, "3 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4075770, "lymphocytes", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_4075770, "station 11R", 1)},
    {"label": "OBS_FINDING", **get_span(text_4075770, "heterogeneous", 3)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "17.2 millimeters", 2)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "15.1 millimeters", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4075770, "19-gauge needle", 4)},
    {"label": "MEAS_COUNT", **get_span(text_4075770, "3 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_4075770, "granuloma", 1)},

    # --- Robotic / Peripheral ---
    {"label": "PROC_METHOD", **get_span(text_4075770, "robotic bronchoscopy", 2)},
    {"label": "PROC_METHOD", **get_span(text_4075770, "Ion robotic bronchoscopy system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4075770, "1.9 millimeters", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4075770, "LLL", 2)}, # "LLL posterior basal"
    {"label": "ANAT_LUNG_LOC", **get_span(text_4075770, "posterior basal (B10)", 2)},
    {"label": "PROC_METHOD", **get_span(text_4075770, "radial endobronchial ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_4075770, "eccentric view", 1)},
    {"label": "PROC_METHOD", **get_span(text_4075770, "radial ebus", 1)},
    
    # --- Sampling ---
    {"label": "PROC_ACTION", **get_span(text_4075770, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4075770, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_4075770, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4075770, "3 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_4075770, "bronchial brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_4075770, "atypical cells", 1)},
    {"label": "PROC_ACTION", **get_span(text_4075770, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4075770, "LLL lobe", 2)},

    # --- Outcome ---
    {"label": "CTX_TIME", **get_span(text_4075770, "11:55", 1)},
    {"label": "CTX_TIME", **get_span(text_4075770, "85 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4075770, "No complications", 1)},
    {"label": "MEAS_VOL", **get_span(text_4075770, "ten milliliters", 1)}, # "less than ten milliliters" -> capture "ten milliliters" or phrase.
]

BATCH_DATA.append({"id": id_4075770, "text": text_4075770, "entities": entities_4075770})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)