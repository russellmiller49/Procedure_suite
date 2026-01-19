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

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2100673
# ==========================================
id_1 = "2100673"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Sarah Chen, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Olympus BF-UC190F linear EBUS bronchoscope
   - Needle: 22-gauge Acquire (Acquire)
   - STATIONS SAMPLED: 4 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 4R: 4 passes, short axis 22.1mm
     * Station 2R: 4 passes, short axis 14.8mm
     * Station 2L: 2 passes, short axis 15.4mm
     * Station 10L: 3 passes, short axis 10.7mm

   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Monarch Robotic Bronchoscopy System (Auris Health (J&J))
   - Registration method: CT-to-body
   - Registration accuracy: 2.2 mm
   - Navigation to peripheral lesion: LUL inferior lingula (B5)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Eccentric view of 30.2mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: LUL lobe
   - Forceps biopsies obtained: 8 specimens
   - Additional TBNA: 4 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: CBCT
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 08:30 - 10:08 (98 minutes)
ANESTHESIA: General anesthesia (ASA 4)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Sarah Chen, MD
[REDACTED]"""

entities_1 = [
    # 1. EBUS-TBNA
    {"label": "PROC_METHOD",     **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "linear EBUS", 1)},
    {"label": "DEV_NEEDLE",      **get_span(text_1, "22-gauge", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "22.1mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "4 passes", 2)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "14.8mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "15.4mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "10.7mm", 1)},
    
    # 2. Navigation
    {"label": "PROC_METHOD",     **get_span(text_1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "Monarch Robotic Bronchoscopy System", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "lesion", 1)}, # "Navigation to peripheral lesion"
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "inferior lingula", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "B5", 1)},
    
    # 3. EBUS Peripheral
    {"label": "PROC_METHOD",     **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 2)},
    {"label": "OBS_LESION",      **get_span(text_1, "LESION", 1)}, # "PERIPHERAL LESION"
    {"label": "PROC_METHOD",     **get_span(text_1, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "miniprobe", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_1, "30.2mm", 1)},
    {"label": "OBS_LESION",      **get_span(text_1, "lesion", 3)}, # "30.2mm lesion" (occurrence 3 lowercase)
    {"label": "PROC_METHOD",     **get_span(text_1, "Radial EBUS", 1)},

    # 4. Biopsy
    {"label": "PROC_ACTION",     **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_1, "LUL", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "8 specimens", 1)},
    {"label": "PROC_ACTION",     **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "4 passes", 3)},
    {"label": "PROC_ACTION",     **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_METHOD",     **get_span(text_1, "CBCT", 1)},

    # Specimens
    {"label": "SPECIMEN",        **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "flow cytometry", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "Surgical pathology", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "molecular testing", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "Cytology", 2)},
    {"label": "PROC_ACTION",     **get_span(text_1, "BAL", 1)},
    {"label": "SPECIMEN",        **get_span(text_1, "cultures", 1)}, # matches "AFB cultures" context

    # Meta
    {"label": "CTX_TIME",             **get_span(text_1, "08:30 - 10:08", 1)},
    {"label": "MEAS_TIME",            **get_span(text_1, "98 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)