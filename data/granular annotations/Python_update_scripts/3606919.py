#!/usr/bin/env python3
"""Blank patient update script (auto-generated).

Source JSON: data/knowledge/patient_note_texts/3606919.json
"""


def main() -> None:
    # TODO: implement per-patient updates here
    pass


if __name__ == "__main__":
    main()
import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3606919
# ==========================================
id_1 = "3606919"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Peter Gray
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 55 years)
Biological Sex: Female
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 55-year-old female patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed lung nodule evaluation with mediastinal lymphadenopathy workup. Preprocedural imaging demonstrated a 31.2 mm solid pulmonary parenchymal lesion localized to the LUL inferior lingula (B5), with positive bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 5.0.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 2. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Olympus BF-UC180F) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 10R demonstrated a homogeneous lymph node measuring 16.6 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed malignant - nsclc nos. Station 4R demonstrated a heterogeneous lymph node measuring 13.5 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed malignant - small cell carcinoma. Station 2L demonstrated a homogeneous lymph node measuring 11.0 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed adequate lymphocytes, no malignancy. Station 2R demonstrated a heterogeneous lymph node measuring 21.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed adequate lymphocytes, no malignancy. Station 4L demonstrated a heterogeneous lymph node measuring 22.9 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed atypical cells.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy platform (Auris Health (J&J)) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 2.2 mm. The robotic catheter was successfully advanced to the target lesion in the LUL inferior lingula (B5).

Radial endobronchial ultrasonography demonstrated concentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via cbct.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (6 specimens), transbronchial needle aspiration (2 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed malignant - squamous cell carcinoma.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 5 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of LUL pulmonary lesion
3. Cytological evaluation suggestive of malignant - nsclc nos
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 78 minutes

Electronically Signed,
Brian O'Connor, MD
Division of Interventional Pulmonology
Cleveland Clinic"""

entities_1 = [
    # --- Clinical Presentation ---
    {"label": "OBS_LESION", **get_span(text_1, "lung nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)}, # mediastinal lymphadenopathy
    {"label": "MEAS_SIZE", **get_span(text_1, "31.2 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid pulmonary parenchymal lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "positive bronchus sign", 1)},
    
    # --- Component I ---
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)}, # title
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 2)}, # convex-probe...
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)}, # Systematic mediastinal
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.6 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.5 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - small cell carcinoma", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.0 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 1)},
    
    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 4)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire needle", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 2)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.9 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 5)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 5)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire needle", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},

    # --- Component II ---
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 3)}, # mediastinal staging
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Electromagnetic navigation", 1)},
    # Note: 2.2 mm is reg error, skipping
    {"label": "OBS_LESION", **get_span(text_1, "target lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 2)},
    
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "target lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "cbct", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # Lowercase t
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    
    # --- ROSE ---
    {"label": "OBS_LESION", **get_span(text_1, "peripheral lesion", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - squamous cell carcinoma", 1)},
    
    # --- Outcomes ---
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 1)},
    
    # --- Impression ---
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "robotic-assisted bronchoscopic biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 3)}, # "LUL pulmonary lesion"
    {"label": "OBS_LESION", **get_span(text_1, "pulmonary lesion", 1)}, # Corrected occurrence count from 2 to 1
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 2)},
    
    {"label": "MEAS_TIME", **get_span(text_1, "78 minutes", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)