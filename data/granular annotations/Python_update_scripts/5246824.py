import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note: 5246824
# ==========================================
id_1 = "5246824"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Mark Cox
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 45 years)
Biological Sex: Male
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 45-year-old male patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed lung nodule evaluation with mediastinal lymphadenopathy workup. Preprocedural imaging demonstrated a 30.2 mm ground-glass pulmonary parenchymal lesion localized to the LUL inferior lingula (B5), with positive bronchus sign on computed tomographic assessment. 

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 4. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Olympus BF-UC190F) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 4R demonstrated a heterogeneous lymph node measuring 22.1 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed atypical cells. Station 2R demonstrated a heterogeneous lymph node measuring 14.8 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed suspicious for malignancy. Station 2L demonstrated a homogeneous lymph node measuring 15.4 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed granuloma. Station 10L demonstrated a homogeneous lymph node measuring 10.7 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 3 passes with a 22-gauge Acquire needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy platform (Auris Health (J&J)) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 2.2 mm. The robotic catheter was successfully advanced to the target lesion in the LUL inferior lingula (B5).

Radial endobronchial ultrasonography demonstrated eccentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via cbct.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (8 specimens), transbronchial needle aspiration (4 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed malignant - small cell carcinoma.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 4 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of LUL pulmonary lesion
3. Cytological evaluation suggestive of atypical cells
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 98 minutes

Electronically Signed,
Sarah Chen, MD
Division of Interventional Pulmonology
Academic Health System"""

entities_1 = [
    # Clinical Presentation
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.2 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)}, # pulmonary parenchymal lesion
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "positive bronchus sign", 1)},
    
    # Anesthetic (Endotracheal tube skipped as per guidelines - transient tool usually usually excluded unless explicit intervention target, focusing on procedure devices)
    
    # Component I: EBUS
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe endobronchial ultrasound bronchoscope", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.1 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},
    
    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.4 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},
    
    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10.7 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 4)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},
    
    # Component II: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic bronchoscopy platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)}, # target lesion
    {"label": "PROC_METHOD", **get_span(text_1, "cbct", 1)},
    
    # Tissue Acquisition
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)}, # Action containing tool
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8 specimens", 1)},
    # Fixed: "transbronchial needle aspiration" (lowercase) is occurrence 1 (previous 4 were Capitalized)
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, 
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)}, # 4R, 2R, Robotic
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    
    # ROSE
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 3)}, # peripheral lesion
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - small cell carcinoma", 1)},
    
    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemostasis was achieved spontaneously", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "minimal blood loss", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no evidence of pneumothorax", 1)},
    
    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic-assisted", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 2)}, # 1st was inside transbronchial forceps biopsy
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 3)}, # 3rd unique LUL span (1=Pres, 2=Robotic, 3=Impression)
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 4)}, # pulmonary lesion
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 2)},
    {"label": "CTX_TIME", **get_span(text_1, "98 minutes", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)