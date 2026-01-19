import sys
from pathlib import Path

# Set the root directory (assuming this script is in a subdirectory like 'scripts/')
# Adjust .parent count if the script is deeper or shallower in the repo
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure REPO_ROOT is correct.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 3592324
# ==========================================
id_1 = "3592324"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Adam Turner
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 41 years)
Biological Sex: Male
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 41-year-old male patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed peripheral lung nodule with suspicious mediastinal nodes. Preprocedural imaging demonstrated a 24.3 mm solid pulmonary parenchymal lesion localized to the LUL superior lingula (B4), with negative bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 12.7.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 4. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 4L demonstrated a homogeneous lymph node measuring 21.5 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed malignant - nsclc nos. Station 10L demonstrated a homogeneous lymph node measuring 21.1 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed malignant - nsclc nos. Station 11L demonstrated a homogeneous lymph node measuring 8.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed malignant - squamous cell carcinoma.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Ion robotic bronchoscopy platform (Intuitive Surgical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 1.5 mm. The robotic catheter was successfully advanced to the target lesion in the LUL superior lingula (B4).

Radial endobronchial ultrasonography demonstrated eccentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via augmented fluoroscopy.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (4 specimens), transbronchial needle aspiration (2 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed adequate lymphocytes.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 3 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of LUL pulmonary lesion
3. Cytological evaluation suggestive of malignant - nsclc nos
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 108 minutes

Electronically Signed,
Robert Patel, MD
Division of Interventional Pulmonology
Memorial Hospital"""

entities_1 = [
    # Indication / Anatomy
    {"label": "OBS_LESION", **get_span(text_1, "peripheral lung nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.3 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid pulmonary parenchymal lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL superior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B4", 1)},

    # Anesthetic / Devices
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},

    # Component I: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.5 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.1 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 2)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - squamous cell carcinoma", 1)},

    # Component II: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL superior lingula", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B4", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},

    # Tissue Acquisition (Robotic)
    # "transbronchial forceps biopsy" -> Split into Instrument (forceps) and Action (biopsy) per guide instructions
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)}, 
    {"label": "MEAS_COUNT", **get_span(text_1, "4 specimens", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # lowercase in this section
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 3)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # ROSE
    {"label": "OBS_ROSE", **get_span(text_1, "lymphocytes", 1)},

    # Outcomes
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no evidence of pneumothorax", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "108 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)