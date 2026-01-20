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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions
# ==========================================
BATCH_DATA = []

# -------------------------------------------------------------------------
# Case 1: 4765883
# -------------------------------------------------------------------------
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Eric Johnson, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Fujifilm EB-580S linear EBUS bronchoscope
   - Needle: 19-gauge FNB/ProCore (FNB/ProCore)
   - STATIONS SAMPLED: 4 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 10R: 3 passes, short axis 11.4mm
     * Station 7: 3 passes, short axis 8.1mm
     * Station 2R: 2 passes, short axis 13.6mm
     * Station 4R: 3 passes, short axis 22.2mm

   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Ion Robotic Bronchoscopy System (Intuitive Surgical)
   - Registration method: CT-to-body
   - Registration accuracy: 3.2 mm
   - Navigation to peripheral lesion: RLL posterior basal (B10)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Adjacent view of 19.5mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RLL lobe
   - Forceps biopsies obtained: 7 specimens
   - Additional TBNA: 3 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Fluoroscopy
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 09:15 - 10:46 (91 minutes)
ANESTHESIA: General anesthesia (ASA 3)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Eric Johnson, MD
[REDACTED]"""

entities_1 = [
    # --- 1. EBUS-TBNA ---
    {"label": "PROC_METHOD",       **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "Fujifilm EB-580S linear EBUS bronchoscope", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_1, "19-gauge", 1)},
    
    # Stations
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "11.4mm", 1)},
    
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "3 passes", 2)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "8.1mm", 1)},
    
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "13.6mm", 1)},
    
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "3 passes", 3)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "22.2mm", 1)},

    # --- 2. Navigation ---
    {"label": "PROC_METHOD",       **get_span(text_1, "Computer-assisted electromagnetic navigation", 1)}, # from Title
    {"label": "PROC_METHOD",       **get_span(text_1, "Ion Robotic Bronchoscopy System", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "RLL posterior basal (B10)", 1)},
    
    # --- 3. Radial EBUS ---
    {"label": "PROC_METHOD",       **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "20 MHz radial EBUS miniprobe", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "19.5mm", 1)},

    # --- 4. TBB ---
    {"label": "PROC_ACTION",       **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "RLL lobe", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "7 specimens", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "3 passes", 4)}, # Additional TBNA
    {"label": "MEAS_COUNT",        **get_span(text_1, "2 specimens", 1)}, # Brushings
    {"label": "PROC_METHOD",       **get_span(text_1, "Fluoroscopy", 1)},

    # --- Specimens / Misc ---
    {"label": "SPECIMEN",          **get_span(text_1, "cell block", 1)},
    {"label": "CTX_TIME",          **get_span(text_1, "09:15", 1)},
    {"label": "CTX_TIME",          **get_span(text_1, "10:46", 1)},
    {"label": "CTX_TIME",          **get_span(text_1, "91 minutes", 1)},
]

BATCH_DATA.append({"id": "4765883", "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)