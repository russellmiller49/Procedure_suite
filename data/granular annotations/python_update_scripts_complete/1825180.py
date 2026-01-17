import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
# Ensure 'scripts.add_training_case' is in your python path or adjust imports as necessary
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Warning: Could not import 'add_case'. Please ensure the script is run from the correct context.")
    # Mocking the function for standalone testing purposes if import fails
    def add_case(case_id, text, entities, root):
        print(f"Processing Case: {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The full text content.
        term (str): The substring to find.
        occurrence (int): The 1-based index of the occurrence (e.g., 1 for first).
    
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1825180
# ==========================================
id_1 = "1825180"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Rebecca Stewart
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 79 years)
Biological Sex: Male
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 79-year-old male patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed peripheral nodule and bilateral hilar adenopathy. Preprocedural imaging demonstrated a 14.0 mm ground-glass pulmonary parenchymal lesion localized to the LUL apicoposterior (B1+2), with negative bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 17.6.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 2. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 2L demonstrated a homogeneous lymph node measuring 14.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed atypical cells. Station 4L demonstrated a homogeneous lymph node measuring 24.3 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - squamous cell carcinoma. Station 10R demonstrated a heterogeneous lymph node measuring 12.9 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - nsclc nos. Station 10L demonstrated a heterogeneous lymph node measuring 18.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed suspicious for malignancy. Station 11L demonstrated a heterogeneous lymph node measuring 18.7 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Ion robotic bronchoscopy platform (Intuitive Surgical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 1.5 mm. The robotic catheter was successfully advanced to the target lesion in the LUL apicoposterior (B1+2).

Radial endobronchial ultrasonography demonstrated concentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via fluoroscopy.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (7 specimens), transbronchial needle aspiration (2 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed adequate lymphocytes, no malignancy.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 5 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of LUL pulmonary lesion
3. Cytological evaluation suggestive of atypical cells
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 114 minutes

Electronically Signed,
Rachel Goldman, MD
Division of Interventional Pulmonology
Academic Health System"""

entities_1 = [
    # Clinical Presentation
    {"label": "OBS_LESION", **get_span(text_1, "peripheral nodule", 1)},
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "adenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.0 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass pulmonary parenchymal lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "apicoposterior (B1+2)", 1)},

    # Anesthetic
    {"label": "PROC_METHOD", **get_span(text_1, "General endotracheal anesthesia", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "orotracheal intubation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},

    # Component I (EBUS)
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe endobronchial ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheobronchial tree", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 2)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.3 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - squamous cell carcinoma", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.9 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 4)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore needle", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.7 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 5)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 5)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore needle", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},

    # Component II (Robotic)
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion robotic bronchoscopy platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Intuitive Surgical", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "target lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "apicoposterior (B1+2)", 2)},

    # Navigation/Biopsy
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "target lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # ROSE
    {"label": "OBS_LESION", **get_span(text_1, "peripheral lesion", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 1)},

    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    
    # Impression
    # ERROR FIX: Changed 'endobronchial ultrasound-guided' occurrence 2 to 1.
    # The header is UPPERCASE. The text in the Impression section is the 1st lowercase occurrence.
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic-assisted", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 3)},
    {"label": "OBS_LESION", **get_span(text_1, "pulmonary lesion", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 2)},
    {"label": "MEAS_TIME", **get_span(text_1, "114 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)