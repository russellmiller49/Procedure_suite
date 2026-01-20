import sys
from pathlib import Path

# Add the repository root to the python path to import the utility
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 4025945
# ==========================================
id_1 = "4025945"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: [REDACTED]
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 76 years)
Biological Sex: Female
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 76-year-old female patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed mediastinal staging for biopsy-proven lung adenocarcinoma. Preprocedural imaging demonstrated a 22.6 mm solid pulmonary parenchymal lesion localized to the RUL apical (B1), with negative bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 9.7.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 3. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Olympus BF-UC190F) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 11R demonstrated a homogeneous lymph node measuring 24.9 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma. Station 2L demonstrated a heterogeneous lymph node measuring 14.7 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed malignant - nsclc nos. Station 4R demonstrated a heterogeneous lymph node measuring 13.0 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed malignant - small cell carcinoma. Station 11L demonstrated a heterogeneous lymph node measuring 19.1 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed suspicious for malignancy.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Galaxy robotic bronchoscopy platform (Noah Medical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 1.8 mm. The robotic catheter was successfully advanced to the target lesion in the RUL apical (B1).

Radial endobronchial ultrasonography demonstrated concentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via cbct.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (4 specimens), transbronchial needle aspiration (4 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed suspicious for malignancy.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 4 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of RUL pulmonary lesion
3. Cytological evaluation suggestive of malignant - adenocarcinoma
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 131 minutes

Electronically Signed,
Brian O'Connor, MD
Division of Interventional Pulmonology
Veterans Affairs Medical Center"""

entities_1 = [
    # Clinical Presentation
    {"label": "OBS_LESION", **get_span(text_1, "lung adenocarcinoma", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.6 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid pulmonary parenchymal lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL apical (B1)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "negative bronchus sign", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "metabolic hyperactivity", 1)},

    # Anesthetic
    {"label": "PROC_METHOD", **get_span(text_1, "General endotracheal anesthesia", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "orotracheal intubation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "8.0 mm endotracheal tube", 1)}, # Transient tool

    # Component I: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND-GUIDED", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe endobronchial ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheobronchial tree", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal and hilar lymph node", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.9 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.7 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.0 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - small cell carcinoma", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.1 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 4)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},

    # Component II: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy robotic bronchoscopy platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL apical (B1)", 2)},

    # Confirmation & Tools
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "cbct", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # Lowercase variant in Comp II
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # Outcome
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "minimal blood loss", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    
    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)}, # Fixed occurrence
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal staging", 2)}, 
    {"label": "PROC_METHOD", **get_span(text_1, "robotic-assisted bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 2)},
    
    # Duration
    {"label": "CTX_TIME", **get_span(text_1, "131 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)