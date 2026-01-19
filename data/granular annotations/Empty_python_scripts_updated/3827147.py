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
# Note 1: 3827147
# ==========================================
t_3827147 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Katherine Lee, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Pentax EB-1990i linear EBUS bronchoscope
   - Needle: 21-gauge Standard FNA (FNB/ProCore)
   - STATIONS SAMPLED: 3 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 10R: 4 passes, short axis 8.4mm
     * Station 10L: 3 passes, short axis 13.7mm
     * Station 2L: 3 passes, short axis 11.1mm


   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Ion Robotic Bronchoscopy System (Intuitive Surgical)
   - Registration method: CT-to-body
   - Registration accuracy: 1.8 mm
   - Navigation to peripheral lesion: LUL anterior (B3)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Adjacent view of 29.8mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: LUL lobe
   - Forceps biopsies obtained: 8 specimens
   - Additional TBNA: 2 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: CBCT
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 10:15 - 11:58 (103 minutes)
ANESTHESIA: General anesthesia (ASA 2)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Katherine Lee, MD
[REDACTED]"""

e_3827147 = [
    # --- Section 1: EBUS-TBNA ---
    {"label": "PROC_METHOD", **get_span(t_3827147, "ENDOBRONCHIAL ULTRASOUND-GUIDED", 1)},
    {"label": "PROC_ACTION", **get_span(t_3827147, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_NEEDLE", **get_span(t_3827147, "21-gauge", 1)},
    
    # Stations
    {"label": "ANAT_LN_STATION", **get_span(t_3827147, "Station 10R", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3827147, "4 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t_3827147, "8.4mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(t_3827147, "Station 10L", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3827147, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t_3827147, "13.7mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(t_3827147, "Station 2L", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3827147, "3 passes", 2)}, # 2nd occurrence of '3 passes'
    {"label": "MEAS_SIZE", **get_span(t_3827147, "11.1mm", 1)},
    
    # --- Section 2: Navigation ---
    {"label": "PROC_METHOD", **get_span(t_3827147, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(t_3827147, "Ion Robotic Bronchoscopy System", 1)},
    {"label": "MEAS_SIZE", **get_span(t_3827147, "1.8 mm", 1)},
    {"label": "OBS_LESION", **get_span(t_3827147, "peripheral lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3827147, "LUL anterior (B3)", 1)},
    {"label": "OBS_LESION", **get_span(t_3827147, "peripheral lung lesion", 1)},

    # --- Section 3: Peripheral EBUS ---
    {"label": "PROC_METHOD", **get_span(t_3827147, "ENDOBRONCHIAL ULTRASOUND", 2)}, # 2nd occurrence (1st was in title 1)
    {"label": "PROC_METHOD", **get_span(t_3827147, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_3827147, "miniprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(t_3827147, "29.8mm", 1)},
    {"label": "OBS_LESION", **get_span(t_3827147, "lesion", 3)}, # Context: '29.8mm lesion'
    {"label": "OBS_LESION", **get_span(t_3827147, "peripheral pulmonary lesion", 1)},

    # --- Section 4: Biopsy ---
    {"label": "PROC_ACTION", **get_span(t_3827147, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_3827147, "LUL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_3827147, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3827147, "8 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t_3827147, "TBNA", 1)}, # In 'Additional TBNA'
    {"label": "MEAS_COUNT", **get_span(t_3827147, "2 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t_3827147, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(t_3827147, "2 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(t_3827147, "CBCT", 1)},

    # --- Specimens & Footer ---
    {"label": "SPECIMEN", **get_span(t_3827147, "cell block", 1)},
    {"label": "CTX_TIME", **get_span(t_3827147, "10:15", 1)},
    {"label": "CTX_TIME", **get_span(t_3827147, "11:58", 1)},
    {"label": "MEAS_TIME", **get_span(t_3827147, "103 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3827147, "None", 1)},
]
BATCH_DATA.append({"id": "3827147", "text": t_3827147, "entities": e_3827147})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)