import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# Assuming saved in: data/granular_annotations/Python_update_scripts/
# REPO_ROOT is 3 levels up.
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
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact substring to find.
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary containing 'text', 'start', and 'end'.
    
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
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

# ------------------------------------------
# Case 1: 1102811
# ------------------------------------------
id_1 = "1102811"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Amy Wood
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 54 years)
Biological Sex: Female
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 54-year-old female patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed peripheral lung nodule with suspicious mediastinal nodes. Preprocedural imaging demonstrated a 19.4 mm solid pulmonary parenchymal lesion localized to the RUL anterior (B3), with positive bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 6.7.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 2. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Olympus BF-UC180F) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 10R demonstrated a heterogeneous lymph node measuring 21.2 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 19-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma. Station 2L demonstrated a homogeneous lymph node measuring 8.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 19-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed atypical cells. Station 11L demonstrated a heterogeneous lymph node measuring 13.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 19-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed adequate lymphocytes, no malignancy.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy platform (Auris Health (J&J)) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 1.5 mm. The robotic catheter was successfully advanced to the target lesion in the RUL anterior (B3).

Radial endobronchial ultrasonography demonstrated concentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via augmented fluoroscopy.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (6 specimens), transbronchial needle aspiration (3 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed granuloma.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 3 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of RUL pulmonary lesion
3. Cytological evaluation suggestive of malignant - adenocarcinoma
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 131 minutes

Electronically Signed,
Eric Johnson, MD
Division of Interventional Pulmonology
Regional Medical Center"""

entities_1 = [
    # --- Anatomy & Indications ---
    {"label": "OBS_LESION", **get_span(text_1, "peripheral lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "suspicious mediastinal nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid pulmonary parenchymal lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    
    # --- Component I: EBUS ---
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.2 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},
    
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 1)},
    
    # --- Component II: Robotic ---
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    
    # Biopsies
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # Corrected: lowercase text appears 1st time here (previous were Title Case)
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)}, # Note: 2nd occurrence of "3 passes"
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    
    # ROSE & Outcomes
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no evidence of pneumothorax", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "131 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        try:
            add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
            print(f"Successfully processed: {case['id']}")
        except Exception as e:
            print(f"Failed to process {case['id']}: {e}")