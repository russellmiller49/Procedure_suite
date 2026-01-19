import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from within the repository structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the python path to import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 3722419
# ==========================================
id_1 = "3722419"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: [REDACTED]
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 57 years)
Biological Sex: Male
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 57-year-old male patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed pet-avid lung mass and mediastinal lymphadenopathy. Preprocedural imaging demonstrated a 30.9 mm ground-glass pulmonary parenchymal lesion localized to the RUL anterior (B3), with negative bronchus sign on computed tomographic assessment. 

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 3. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 4L demonstrated a homogeneous lymph node measuring 18.3 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - nsclc nos. Station 10R demonstrated a heterogeneous lymph node measuring 14.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed suspicious for malignancy. Station 4R demonstrated a homogeneous lymph node measuring 20.9 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma. Station 7 demonstrated a homogeneous lymph node measuring 24.0 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy platform (Auris Health (J&J)) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 2.0 mm. The robotic catheter was successfully advanced to the target lesion in the RUL anterior (B3).

Radial endobronchial ultrasonography demonstrated adjacent visualization of the target lesion. Tool-in-lesion confirmation was achieved via fluoroscopy.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (6 specimens), transbronchial needle aspiration (4 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed granuloma.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 4 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of RUL pulmonary lesion
3. Cytological evaluation suggestive of malignant - nsclc nos
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 77 minutes

Electronically Signed,
Steven Park, MD
Division of Interventional Pulmonology
Regional Medical Center"""

entities_1 = [
    # Indications / Lesions
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.9 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "negative bronchus sign", 1)},

    # Component I: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "convex-probe endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "bronchoscope", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.3 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.9 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.0 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 2)},

    # Component II: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},

    # Tissue Acquisition
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # Lower case variant
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    
    # ROSE & Outcomes
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "77 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)