import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function from the scripts module
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Case 1: 4392820
# ==========================================
id_1 = "4392820"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE DOCUMENTATION

Patient [REDACTED]: Brandon Morales
Medical Record [REDACTED]: [REDACTED]
Date of Birth: [REDACTED] (Age: 77 years)
Biological Sex: Female
Date of Procedure: [REDACTED]
Institution: [REDACTED]

CLINICAL PRESENTATION AND PROCEDURAL INDICATION

This 77-year-old female patient with a pertinent oncologic history presented for comprehensive bronchoscopic evaluation. The primary indication for this procedure encompassed lung cancer staging - suspected nsclc with mediastinal lymphadenopathy. Preprocedural imaging demonstrated a 23.2 mm ground-glass pulmonary parenchymal lesion localized to the LLL lateral basal (B9), with positive bronchus sign on computed tomographic assessment. Positron emission tomography demonstrated metabolic hyperactivity with standardized uptake value maximum of 16.0.

ANESTHETIC CONSIDERATIONS

The patient was classified as American Society of Anesthesiologists physical status 3. General endotracheal anesthesia was administered, with successful orotracheal intubation utilizing a 8.0 mm endotracheal tube.

PROCEDURAL TECHNIQUE

COMPONENT I: ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION

The convex-probe endobronchial ultrasound bronchoscope (Olympus BF-UC180F) was advanced through the endotracheal tube into the tracheobronchial tree. Systematic mediastinal and hilar lymph node evaluation was performed according to established staging protocols.

Station 11R demonstrated a homogeneous lymph node measuring 13.7 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 19-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed suspicious for malignancy. Station 2L demonstrated a heterogeneous lymph node measuring 8.4 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 2 passes with a 19-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - nsclc nos. Station 4L demonstrated a heterogeneous lymph node measuring 19.6 mm in short axis diameter. Transbronchial needle aspiration was performed utilizing 4 passes with a 19-gauge FNB/ProCore needle. Rapid on-site cytological evaluation revealed malignant - adenocarcinoma.

COMPONENT II: ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION

Following completion of mediastinal staging, the Galaxy robotic bronchoscopy platform (Noah Medical) was deployed. Electromagnetic navigation registration achieved acceptable accuracy with registration error of 2.8 mm. The robotic catheter was successfully advanced to the target lesion in the LLL lateral basal (B9).

Radial endobronchial ultrasonography demonstrated eccentric visualization of the target lesion. Tool-in-lesion confirmation was achieved via radial ebus.

Tissue acquisition was performed utilizing multiple modalities: transbronchial forceps biopsy (7 specimens), transbronchial needle aspiration (2 passes), and bronchial brushings (2 specimens). Bronchoalveolar lavage was obtained for microbiological analysis.

RAPID ON-SITE CYTOLOGICAL EVALUATION

On-site cytopathological assessment of the peripheral lesion specimens revealed suspicious for malignancy.

PROCEDURAL OUTCOMES AND COMPLICATIONS

The procedure was completed without complication. Hemostasis was achieved spontaneously with minimal blood loss (<10 mL). Post-procedural chest radiography demonstrated no evidence of pneumothorax or other acute pulmonary parenchymal abnormality.

IMPRESSION AND RECOMMENDATIONS

1. Successful endobronchial ultrasound-guided mediastinal staging with sampling of 3 lymph node stations
2. Successful robotic-assisted bronchoscopic biopsy of LLL pulmonary lesion
3. Cytological evaluation suggestive of suspicious for malignancy
4. Recommend correlation with final surgical pathology and consideration of molecular profiling if malignancy confirmed

Total Procedure Duration: 105 minutes

Electronically Signed,
Jennifer Walsh, MD
Division of Interventional Pulmonology
Baptist Medical Center"""

entities_1 = [
    # Clinical Presentation & Anatomy
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.2 mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL lateral basal (B9)", 1)},
    
    # Anesthesia/Airway
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)}, # Tube size
    
    # Component I: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe endobronchial ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC180F", 1)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymph node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.7 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymph node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.4 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - nsclc nos", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymph node", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.6 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial needle aspiration", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant - adenocarcinoma", 1)},
    
    # Component II: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED BRONCHOSCOPIC NAVIGATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy robotic bronchoscopy platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Noah Medical", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.8 mm", 1)}, # Registration error
    {"label": "DEV_CATHETER", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL lateral basal (B9)", 2)},
    
    # Navigation/Confirmation
    {"label": "PROC_METHOD", **get_span(text_1, "Radial endobronchial ultrasonography", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)}, # Corrected occurrence (lowercase match)
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    
    # ROSE & Outcomes
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "without complication", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "105 minutes", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)