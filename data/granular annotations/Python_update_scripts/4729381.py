import sys
from pathlib import Path

# Set the repository root (assuming script is running from within the repo)
# If the script is in 'scripts/', REPO_ROOT is one level up.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 4729381
# ==========================================
id_1 = "4729381"
text_1 = """Patient Name: [REDACTED] MRN: [REDACTED] DOB: [REDACTED] Date: [REDACTED]
Attending: Dr. Patel, Nina MD Fellow: Dr. Jackson, Marcus MD
PROCEDURE: Robotic-assisted bronchoscopy with Intuitive Ion system
INDICATION: RUL nodule 2.8cm, ground-glass component on CT, PET SUV 3.2, intermediate suspicion for malignancy
CONSENT: Obtained, documented
ANESTHESIA: General anesthesia (Dr. Wilson), ETT 8.0
PRE-PROCEDURE PLANNING: CT chest from [REDACTED] loaded into Ion planning station. 3D reconstruction completed. Pathway to RUL posterior segment target generated. Target coordinates confirmed.
VENTILATION PARAMETERS: Mode: Volume Control RR: 12 TV: 500mL PEEP: 5cmH2O FiO2: 40% Flow: 50L/min Pmean: 14cmH2O
ION REGISTRATION: Automatic registration performed. Adequate airway landmark matching achieved at carina, right and left main carina, RUL apical subsegmental bifurcations. Mean fiducial error: 3.2mm. Global alignment: Excellent. No registration drift observed.
NAVIGATION: Ion catheter advanced through planned pathway under robotic control to RUL posterior segment. Distance to target: 0.8cm from pleura.
RADIAL EBUS CONFIRMATION: Radial probe advanced through Ion working channel. Ultrasound pattern: Concentric (lesion surrounds probe). Lesion size by REBUS: 28mm. Position confirmed within target.
CONE BEAM CT: CBCT spin performed. NaviLink 3D fusion confirmed catheter position within lesion with 2mm margin from lesion center. Excellent alignment.
SAMPLING:
•\tBrush cytology x2 samples (via guide sheath)
•\tForceps biopsy x4 samples (via guide sheath)
•\tNeedle aspiration x2 samples (21G)
ROSE: Not available
COMPLICATIONS: None No pneumothorax on post-CBCT imaging
ESTIMATED BLOOD LOSS: <5mL
SPECIMENS: Cytology, histology sent to pathology
IMPRESSION: Successful robotic navigation and sampling of RUL nodule. Awaiting final pathology.
PLAN: Pathology results in 3-5 days, follow-up in IP clinic
Nina Patel, MD [REDACTED] 1440hrs
**PATIENT:** Martinez, Sofia J.
**MRN:** 8847293
**DOB:** [REDACTED]
**DATE OF SERVICE:** [REDACTED]
**ATTENDING:** Dr. Kenneth Patel, MD
**FELLOW:** Dr. Lisa Chen, MD

**PROCEDURE:** Robotic Navigational Bronchoscopy with Transbronchial Biopsy

**INDICATION:** 2.3 cm right upper lobe nodule, PET avid (SUV 4.2)

**CONSENT:** Obtained. Risks including bleeding, pneumothorax, infection, and need for further intervention discussed. Patient verbalized understanding.

**ANESTHESIA:** General anesthesia with endotracheal intubation performed by Dr. Amanda Rodriguez

**VENT SETTINGS:**
- Mode: Volume Control
- RR: 12
- TV: 450 mL
- PEEP: 5 cm H2O
- FiO2: 60%
- Flow: 50 L/min
- Pmean: 12 cm H2O

**PROCEDURE DETAILS:**
Pre-procedure CT from [REDACTED] was loaded onto the Ion planning station. 3D pathway created targeting RUL anterior segment nodule. Plan reviewed and approved.

Registration performed using automatic method. Excellent landmark correlation at carina, right upper lobe carina, and tertiary bifurcations. Mean fiducial error 1.2 mm. No drift noted during procedure.

Ion catheter advanced along planned pathway under navigational guidance. Radial EBUS performed showing concentric pattern, lesion measuring 22 mm. CBCT spin obtained - overlay confirmed tool-in-lesion position with catheter tip 3 mm from lesion center.

**SAMPLING:**
- Transbronchial forceps biopsy x 6 samples (to pathology)
- Cytology brushings x 2 (to cytology)
- Bronchial washing (to microbiology and cytology)

ROSE preliminary: adequate cellularity, atypical cells present, favor adenocarcinoma (final pending)

Hemostasis confirmed. No complications. Patient extubated in OR, transferred to PACU in stable condition.

**EBL:** <5 mL
**SPECIMENS:** As above
**COMPLICATIONS:** None

**IMPRESSION:** Successful robotic bronchoscopy with biopsy of RUL nodule. ROSE suggestive of malignancy. Final pathology pending. Follow up in IP clinic in 2 weeks with results."""

entities_1 = [
    # Report 1
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "posterior segment", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "main carina", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 4)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "posterior segment", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "0.8cm", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "pleura", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "RADIAL EBUS", 1)}, # Corrected casing to match Report 1
    {"label": "MEAS_SIZE", **get_span(text_1, "28mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "guide sheath", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "guide sheath", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "histology", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 5)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    {"label": "CTX_TIME", **get_span(text_1, "1440hrs", 1)},

    # Report 2 (starts after 1440hrs)
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Navigational Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.3 cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 6)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior segment", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 4)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "carina", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion catheter", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)}, # Corrected occurrence (unique casing for this report)
    {"label": "MEAS_SIZE", **get_span(text_1, "22 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchial washing", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate cellularity", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "atypical cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 7)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignancy", 2)} 
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)