import sys
from pathlib import Path

# Set up the repository root path
# This assumes the script is running within the standard directory structure
# Adjust REPO_ROOT as necessary for your specific environment
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback or placeholder if the module isn't strictly available in this context
    # In a real pipeline, this import is required.
    def add_case(case_id, text, entities, root_path):
        print(f"Processing Case: {case_id} ({len(entities)} entities)")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 5225684
# ==========================================
id_1 = "5225684"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Joyce Lopez
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 78 years)
Biological Sex: Female
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 78-year-old female patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed right upper lobe mass with ipsilateral mediastinal nodes. Preprocedural imaging demonstrated a 20.2 mm solid pulmonary parenchymal lesion localized to the LUL inferior lingula (B5), with positive bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 16.9.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 3. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 4L demonstrated a homogeneous lymph node measuring 24.4 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed adequate lymphocytes, no malignancy. Station 7 demonstrated a homogeneous lymph node measuring 20.3 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed adequate lymphocytes, no malignancy. Station 10R demonstrated a homogeneous lymph node measuring 20.4 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 21-gauge Standard FNA needle. Rapid on-site cytological evaluation revealed atypical cells.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Galaxy robotic bronchoscopy platform (Noah Medical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 2.3 mm. The robotic catheter was successfully advanced to the target lesion in the LUL inferior lingula (B5).

Radial endobronchial ultrasonography demonstrated concentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via radial ebus.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (7 specimens), transbronchial needle aspiration (4 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed malignant - small cell carcinoma.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 3 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of LUL pulmonary lesion
3. Cytological evaluation suggestive of adequate lymphocytes, no malignancy
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 113 minutes

Electronically Signed,
Rachel Goldman, MD
Division of Interventional Pulmonology
Community Hospital"""

entities_1 = [
    # Indication / Hx
    {"label": "CTX_HISTORICAL", **get_span(text_1, "oncologic history", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "LATERALITY", **get_span(text_1, "ipsilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.2 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},

    # Anesthesia
    {"label": "PROC_METHOD", **get_span(text_1, "General endotracheal anesthesia", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "intubation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},

    # Component I: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe endobronchial ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheobronchial tree", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "lymph node", 2)}, # Generic ref

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous lymph node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.4 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous lymph node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.3 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 2)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous lymph node", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.4 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Standard FNA needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},

    # Component II: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy robotic bronchoscopy platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Noah Medical", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.3 mm", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    
    # Biopsies
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    # FIXED: Changed occurrence from 4 to 1 because this is the first occurrence of the lowercase string "transbronchial needle aspiration"
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # Outcomes
    {"label": "OBS_ROSE", **get_span(text_1, "malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "small cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemostasis was achieved", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no evidence of pneumothorax", 1)},
    
    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 lymph node stations", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic-assisted bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 3)},
    
    # Time
    {"label": "CTX_TIME", **get_span(text_1, "113 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)