import sys
from pathlib import Path

# Set up path to allow importing from scripts directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Case 1: 4266178
# ==========================================
id_1 = "4266178"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Ronald James
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 51 years)
Biological Sex: Male
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 51-year-old male patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed right upper lobe mass with ipsilateral mediastinal nodes. Preprocedural imaging demonstrated a 31.9 mm ground-glass pulmonary parenchymal lesion localized to the LLL anteromedial basal (B7+8), with negative bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 13.4.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 3. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 11L demonstrated a homogeneous lymph node measuring 21.6 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed suspicious for malignancy. Station 2L demonstrated a homogeneous lymph node measuring 14.5 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed suspicious for malignancy. Station 7 demonstrated a homogeneous lymph node measuring 21.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed adequate lymphocytes. Station 11R demonstrated a homogeneous lymph node measuring 15.0 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed malignant - small cell carcinoma. Station 10R demonstrated a heterogeneous lymph node measuring 21.4 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed adequate lymphocytes, no malignancy.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Ion robotic bronchoscopy platform (Intuitive Surgical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 3.2 mm. The robotic catheter was successfully advanced to the target lesion in the LLL anteromedial basal (B7+8).

Radial endobronchial ultrasonography demonstrated adjacent visualization of the target lesion. Tool-in-lesion confirmation was achieved via fluoroscopy.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (6 specimens), transbronchial needle aspiration (3 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed suspicious for malignancy.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 5 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of LLL pulmonary lesion
3. Cytological evaluation suggestive of suspicious for malignancy
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 119 minutes

Electronically Signed,
Maria Santos, MD
Division of Interventional Pulmonology
Memorial Hospital"""

entities_1 = [
    # --- Indication & History ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.9 mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL anteromedial basal (B7+8)", 1)},
    
    # --- Anesthesia ---
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    
    # --- EBUS Technique ---
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe endobronchial ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheobronchial tree", 1)},
    
    # --- Station 11L ---
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.6 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},
    
    # --- Station 2L ---
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.5 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 2)},
    
    # --- Station 7 ---
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes", 1)},
    
    # --- Station 11R ---
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.0 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - small cell carcinoma", 1)},
    
    # --- Station 10R ---
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.4 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 5)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge Acquire needle", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate lymphocytes, no malignancy", 1)},
    
    # --- Robotic Navigation ---
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 3)}, # "target lesion"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL anteromedial basal (B7+8)", 2)},
    
    # --- Robotic Verification ---
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    
    # --- Robotic Acquisition ---
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    
    # --- Post-Op / Outcomes ---
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no evidence of pneumothorax", 1)},
    
    # --- Impression ---
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    # Fixed: "robotic-assisted bronchoscopic" appears in lowercase only once (in the Impression).
    # The header has it in UPPERCASE, which find() misses.
    {"label": "PROC_METHOD", **get_span(text_1, "robotic-assisted bronchoscopic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 3)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 4)},
    {"label": "CTX_TIME", **get_span(text_1, "119 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)