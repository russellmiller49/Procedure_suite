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
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 2222456
# ==========================================
id_1 = "2222456"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (62 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Steven Park
Fellow: Dr. Emily Chen (PGY-5)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Peripheral nodule and bilateral hilar adenopathy

PREOPERATIVE DIAGNOSIS
1. Lung nodule/mass requiring tissue diagnosis
2. Mediastinal lymphadenopathy requiring staging

POSTOPERATIVE DIAGNOSIS
Same as preoperative, pending final pathology

PROCEDURES PERFORMED
1. Linear endobronchial ultrasound with transbronchial needle aspiration (EBUS-TBNA) for mediastinal staging
2. Robotic-assisted bronchoscopy (Ion platform) with peripheral lung biopsy
3. Radial EBUS for peripheral lesion localization
4. Transbronchial lung biopsy

ANESTHESIA
Type: General anesthesia with endotracheal intubation
ASA Class: 3

PROCEDURE START TIME: 07:00
PROCEDURE END TIME: 09:02
TOTAL PROCEDURE TIME: 122 minutes

EQUIPMENT
- Linear EBUS scope: Fujifilm EB-580S
- EBUS needle: Olympus NA-201SX-4021 (21G Standard FNA)
- Robotic platform: Ion (Intuitive Surgical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 7: Id[REDACTED] homogeneous lymph node measuring 8.3mm (short axis) x 24.2mm (long axis). 2 passes performed with 21G needle. ROSE: Atypical cells.
Station 11R: Id[REDACTED] homogeneous lymph node measuring 19.4mm (short axis) x 15.1mm (long axis). 4 passes performed with 21G needle. ROSE: Adequate lymphocytes, no malignancy.
Station 11L: Id[REDACTED] homogeneous lymph node measuring 14.1mm (short axis) x 15.1mm (long axis). 4 passes performed with 21G needle. ROSE: Granuloma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Ion robotic bronchoscopy system was deployed.

Target lesion: LUL superior lingula (B4)
Lesion characteristics:
- Size: 34.7 mm
- Distance from pleura: 9.5 mm
- CT appearance: Part-solid
- Bronchus sign: Positive
- PET SUV max: 12.7

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming adjacent view of the lesion.

Tool-in-lesion confirmation: Radial EBUS

Sampling performed:
- Transbronchial forceps biopsies: 5 specimens
- TBNA: 3 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Suspicious for malignancy

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 7, 11R, 11L - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from LUL - sent for surgical pathology
3. Brushings from LUL - sent for cytology
4. BAL from LUL - sent for cultures (bacterial, fungal, AFB)

COMPLICATIONS
None. No significant bleeding. No pneumothorax noted on post-procedure imaging.

ESTIMATED BLOOD LOSS
Minimal (<10 mL)

IMPRESSION
1. Successful EBUS-TBNA mediastinal staging with sampling of 3 lymph node stations
2. Successful robotic bronchoscopy with peripheral nodule biopsy
3. ROSE adequate at all sampled sites
4. Await final pathology and molecular testing if indicated

PLAN
1. Monitor in recovery for 2 hours
2. Post-procedure chest X-ray - completed, no pneumothorax
3. Discharge to home if stable with standard post-bronchoscopy precautions
4. Results conference scheduled
5. Final pathology will determine staging and treatment planning

Steven Park
Interventional Pulmonology
University Medical Center

CPT CODES: 31653, 31627, 31654, 31628"""

entities_1 = [
    # --- Indications & Diagnosis ---
    {"label": "OBS_LESION",      **get_span(text_1, "nodule", 1)},            # "Peripheral nodule"
    {"label": "LATERALITY",      **get_span(text_1, "bilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "adenopathy", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "nodule", 2)},            # "Lung nodule/mass"
    {"label": "OBS_LESION",      **get_span(text_1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Mediastinal", 1)},       # "Mediastinal lymphadenopathy"
    {"label": "OBS_LESION",      **get_span(text_1, "lymphadenopathy", 1)},

    # --- Procedures Performed (Header) ---
    {"label": "PROC_METHOD",     **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "EBUS", 1)},             # In "EBUS-TBNA"
    {"label": "PROC_ACTION",     **get_span(text_1, "TBNA", 1)},             # In "EBUS-TBNA"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},       # "for mediastinal staging"
    {"label": "PROC_METHOD",     **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "Radial EBUS", 1)},       # "Radial EBUS for..."
    {"label": "PROC_ACTION",     **get_span(text_1, "Transbronchial lung biopsy", 1)},

    # --- Vitals & Equipment ---
    {"label": "CTX_TIME",        **get_span(text_1, "07:00", 1)},
    {"label": "CTX_TIME",        **get_span(text_1, "09:02", 1)},
    {"label": "MEAS_TIME",       **get_span(text_1, "122 minutes", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Fujifilm EB-580S", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "Olympus NA-201SX-4021", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "21G", 1)},              # In "21G Standard FNA"
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "20 MHz miniprobe", 1)},

    # --- Procedure Part 1 (EBUS) ---
    {"label": "PROC_METHOD",     **get_span(text_1, "LINEAR EBUS", 1)},       # Header
    {"label": "ANAT_LN_STATION", **get_span(text_1, "MEDIASTINAL", 1)},       # Header
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "ETT", 1)},               # "8.0 mm ETT"
    {"label": "MEAS_SIZE",       **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "linear EBUS bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)},       # "Systematic mediastinal..."

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "8.3mm", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "24.2mm", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "21G needle", 1)},
    {"label": "OBS_ROSE",        **get_span(text_1, "Atypical cells", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "19.4mm", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "15.1mm", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "4 passes", 1)},        # First "4 passes"
    {"label": "DEV_NEEDLE",      **get_span(text_1, "21G needle", 2)},
    {"label": "OBS_ROSE",        **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "14.1mm", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "15.1mm", 2)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "4 passes", 2)},        # Second "4 passes"
    {"label": "DEV_NEEDLE",      **get_span(text_1, "21G needle", 3)},
    {"label": "OBS_ROSE",        **get_span(text_1, "Granuloma", 1)},

    # --- Procedure Part 2 (Robotic) ---
    {"label": "PROC_METHOD",     **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 3)},       # "completion of mediastinal..."
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "LUL superior lingula (B4)", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "34.7 mm", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Radial EBUS probe", 2)}, # Second occurrence
    {"label": "PROC_METHOD",     **get_span(text_1, "Radial EBUS", 4)},       # "Tool-in-lesion confirmation: Radial EBUS" (4th occ of EBUS phrase roughly)
    
    # Sampling
    {"label": "PROC_ACTION",     **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "5 specimens", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "TBNA", 2)},              # "TBNA: 3 passes"
    {"label": "MEAS_COUNT",      **get_span(text_1, "3 passes", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "Brushings", 1)},         # Action of brushing
    {"label": "MEAS_COUNT",      **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE",        **get_span(text_1, "Suspicious for malignancy", 1)},

    # --- Specimens ---
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 2)},              # In "stations 7, 11R, 11L"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 2)},              # In "stations 7, 11R, 11L"
    {"label": "SPECIMEN",        **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "LUL", 2)},              # "biopsies from LUL"
    {"label": "SPECIMEN",        **get_span(text_1, "Brushings", 2)},         # "Brushings from LUL" (Specimen)
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "LUL", 3)},              # "Brushings from LUL"
    {"label": "PROC_ACTION",     **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "LUL", 4)},              # "BAL from LUL"

    # --- Complications / Impression / Plan ---
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
    {"label": "MEAS_VOL",             **get_span(text_1, "<10 mL", 1)},
    {"label": "ANAT_LN_STATION",      **get_span(text_1, "mediastinal", 4)}, # "EBUS-TBNA mediastinal staging"
    {"label": "PROC_METHOD",          **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "OBS_LESION",           **get_span(text_1, "nodule", 3)},       # "peripheral nodule biopsy"
    {"label": "PROC_ACTION",          **get_span(text_1, "biopsy", 3)},       # "nodule biopsy" (3rd 'biopsy' word)
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)