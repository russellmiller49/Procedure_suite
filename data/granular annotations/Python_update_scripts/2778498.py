import sys
from pathlib import Path

# Set up the repository root directory
# (Assuming this script is run from a subdirectory like 'scripts' or 'notebooks')
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports from the 'scripts' package
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function to add the case
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to find (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 2778498
# ==========================================
id_1 = "2778498"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Donna Vasquez
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 53 years)
Biological Sex: Male
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 53-year-old male patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed pet-avid lung mass and mediastinal lymphadenopathy. Preprocedural imaging demonstrated a 20.0 mm solid pulmonary parenchymal lesion localized to the RML medial (B5), with negative bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 6.5.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 4. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Olympus BF-UC190F) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 2L demonstrated a homogeneous lymph node measuring 13.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed malignant - small cell carcinoma. Station 4R demonstrated a heterogeneous lymph node measuring 23.9 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma. Station 11R demonstrated a heterogeneous lymph node measuring 19.6 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed atypical cells. Station 11L demonstrated a heterogeneous lymph node measuring 17.4 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Ion robotic bronchoscopy platform (Intuitive Surgical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 2.5 mm. The robotic catheter was successfully advanced to the target lesion in the RML medial (B5).

Radial endobronchial ultrasonography demonstrated adjacent visualization of the target lesion. Tool-in-lesion confirmation was achieved via augmented fluoroscopy.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (7 specimens), transbronchial needle aspiration (2 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed malignant - nsclc nos.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 4 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of RML pulmonary lesion
3. Cytological evaluation suggestive of malignant - small cell carcinoma
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 87 minutes

Electronically Signed,
David Kim, MD
Division of Interventional Pulmonology
Regional Medical Center"""

entities_1 = [
    # Clinical Presentation
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.0 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid pulmonary parenchymal lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 1)},
    
    # Anesthetic
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},

    # Component I
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe endobronchial ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheobronchial tree", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - small cell carcinoma", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.9 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.6 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.4 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 2)},

    # Component II
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    
    # Biopsies
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # lowercase in component II
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # ROSE
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},

    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 lymph node stations", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic-assisted bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 2)}, # 1 in 'transbronchial forceps biopsy', 2 here? text: "biopsy of RML"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 2)}, # 1 in 'RML medial', 2 in impression 'RML pulmonary'
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - small cell carcinoma", 2)},
    {"label": "CTX_TIME", **get_span(text_1, "87 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)