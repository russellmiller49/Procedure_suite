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
# 2. Helper Definition
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Case 1: 2526522
# ==========================================
id_1 = "2526522"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: David Kim, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Olympus BF-UC260F-OL8 linear EBUS bronchoscope
   - Needle: 19-gauge FNB/ProCore (Acquire)
   - STATIONS SAMPLED: 4 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 2L: 4 passes, short axis 20.2mm
     * Station 4R: 4 passes, short axis 17.2mm
     * Station 7: 3 passes, short axis 11.6mm
     * Station 11R: 3 passes, short axis 17.2mm

   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Ion Robotic Bronchoscopy System (Intuitive Surgical)
   - Registration method: CT-to-body
   - Registration accuracy: 1.9 mm
   - Navigation to peripheral lesion: LLL posterior basal (B10)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Eccentric view of 27.1mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: LLL lobe
   - Forceps biopsies obtained: 7 specimens
   - Additional TBNA: 3 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Radial EBUS
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 10:30 - 11:55 (85 minutes)
ANESTHESIA: General anesthesia (ASA 2)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

David Kim, MD
[REDACTED]"""

entities_1 = [
    # --- Procedure 1: EBUS-TBNA ---
    {"label": "PROC_METHOD",      **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION",      **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_1, "linear EBUS bronchoscope", 1)},
    {"label": "DEV_NEEDLE",       **get_span(text_1, "19-gauge", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION",  **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_SIZE",        **get_span(text_1, "20.2mm", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION",  **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "4 passes", 2)},
    {"label": "MEAS_SIZE",        **get_span(text_1, "17.2mm", 1)},
    
    # Station 7
    {"label": "ANAT_LN_STATION",  **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE",        **get_span(text_1, "11.6mm", 1)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION",  **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "3 passes", 2)},
    {"label": "MEAS_SIZE",        **get_span(text_1, "17.2mm", 2)},
    
    # --- Procedure 2: Navigation ---
    {"label": "PROC_METHOD",      **get_span(text_1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "Ion Robotic Bronchoscopy System", 1)},
    {"label": "ANAT_LUNG_LOC",    **get_span(text_1, "LLL posterior basal (B10)", 1)},
    
    # --- Procedure 3: Radial EBUS ---
    {"label": "PROC_METHOD",      **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 2)}, # Header
    {"label": "DEV_INSTRUMENT",   **get_span(text_1, "radial EBUS miniprobe", 1)},
    {"label": "MEAS_SIZE",        **get_span(text_1, "27.1mm", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "Radial EBUS", 1)},
    
    # --- Procedure 4: Biopsy ---
    {"label": "PROC_ACTION",      **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC",    **get_span(text_1, "LLL lobe", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "7 specimens", 1)},
    
    # Additional TBNA & Brushings
    {"label": "PROC_ACTION",      **get_span(text_1, "TBNA", 2)}, # From "Additional TBNA"
    {"label": "MEAS_COUNT",       **get_span(text_1, "3 passes", 3)},
    {"label": "PROC_ACTION",      **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT",       **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "Radial EBUS", 2)}, # Confirmation
    
    # --- Specimens ---
    {"label": "SPECIMEN",         **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN",         **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",         **get_span(text_1, "flow cytometry", 1)},
    {"label": "SPECIMEN",         **get_span(text_1, "Surgical pathology", 1)},
    {"label": "SPECIMEN",         **get_span(text_1, "molecular testing", 1)},
    {"label": "SPECIMEN",         **get_span(text_1, "Cytology", 2)},
    
    # --- BAL ---
    {"label": "PROC_ACTION",      **get_span(text_1, "BAL", 1)},
    {"label": "SPECIMEN",         **get_span(text_1, "cultures", 1)},
    
    # --- Meta ---
    {"label": "CTX_TIME",         **get_span(text_1, "10:30", 1)},
    {"label": "CTX_TIME",         **get_span(text_1, "11:55", 1)},
    {"label": "CTX_TIME",         **get_span(text_1, "85 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)} # Under COMPLICATIONS
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)