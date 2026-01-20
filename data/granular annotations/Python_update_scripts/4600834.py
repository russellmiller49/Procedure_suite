import sys
from pathlib import Path

# Set the repository root directory (assuming script is run from a subdir)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the add_case utility
try:
    from scripts.add_training_case import add_case
except ImportError:
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
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4600834
# ==========================================
id_1 = "4600834"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Mark Howard
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 48 years)
Biological Sex: Female
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 48-year-old female patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed right upper lobe mass with ipsilateral mediastinal nodes. Preprocedural imaging demonstrated a 28.6 mm ground-glass pulmonary parenchymal lesion localized to the RLL lateral basal (B9), with negative bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 8.9.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 4. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Olympus BF-UC260F-OL8) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 10R demonstrated a heterogeneous lymph node measuring 17.1 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed atypical cells. Station 11R demonstrated a homogeneous lymph node measuring 8.4 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed granuloma. Station 11L demonstrated a homogeneous lymph node measuring 22.2 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma. Station 2R demonstrated a heterogeneous lymph node measuring 21.9 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed atypical cells. Station 4L demonstrated a homogeneous lymph node measuring 18.5 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed granuloma.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Ion robotic bronchoscopy platform (Intuitive Surgical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 2.6 mm. The robotic catheter was successfully advanced to the target lesion in the RLL lateral basal (B9).

Radial endobronchial ultrasonography demonstrated adjacent visualization of the target lesion. Tool-in-lesion confirmation was achieved via augmented fluoroscopy.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (5 specimens), transbronchial needle aspiration (4 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed malignant - adenocarcinoma.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 5 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of RLL pulmonary lesion
3. Cytological evaluation suggestive of atypical cells
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 92 minutes

Electronically Signed,
Michael Rodriguez, MD
Division of Interventional Pulmonology
Memorial Hospital"""

entities_1 = [
    # Anatomy & Locations
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "right upper lobe", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal nodes", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},  # In Impression

    # Observations (Lesions/Findings)
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)}, # parenchymal lesion
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)}, # target lesion
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 3)}, # adjacent visualization of target lesion
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 4)}, # RLL pulmonary lesion

    # Measurements (Size)
    {"label": "MEAS_SIZE", **get_span(text_1, "28.6 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.1 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.4 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.2 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.9 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.5 mm", 1)},

    # Component I: EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},

    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 2)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 5)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 2)},

    # Component II: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    
    # Tissue Acquisition
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 specimens", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # lowercase t
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 4)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # Final ROSE & Impression
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic-assisted", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 3)},
    {"label": "CTX_TIME", **get_span(text_1, "92 minutes", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)