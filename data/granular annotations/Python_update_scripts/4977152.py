import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} time(s) in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 4977152
# ==========================================
id_1 = "4977152"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Brian O'Connor, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Fujifilm EB-580S linear EBUS bronchoscope
   - Needle: 19-gauge FNB/ProCore (Standard FNA)
   - STATIONS SAMPLED: 3 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 11L: 4 passes, short axis 13.3mm
     * Station 7: 2 passes, short axis 10.0mm
     * Station 2L: 3 passes, short axis 24.9mm


   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Monarch Robotic Bronchoscopy System (Auris Health (J&J))
   - Registration method: CT-to-body
   - Registration accuracy: 3.2 mm
   - Navigation to peripheral lesion: RUL anterior (B3)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Concentric view of 14.5mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RUL lobe
   - Forceps biopsies obtained: 7 specimens
   - Additional TBNA: 4 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Radial EBUS
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 09:15 - 11:31 (136 minutes)
ANESTHESIA: General anesthesia (ASA 3)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Brian O'Connor, MD
[REDACTED]"""

entities_1 = [
    # Procedure 1: EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 1)},
    
    # Stations
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.3mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10.0mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.9mm", 1)},

    # Procedure 2: Navigation
    {"label": "PROC_METHOD", **get_span(text_1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch Robotic Bronchoscopy System", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3.2 mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "electromagnetic navigation", 1)},

    # Procedure 3: Peripheral EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)}, # miniprobe
    {"label": "MEAS_SIZE", **get_span(text_1, "14.5mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)}, # In code justification

    # Procedure 4: TBBx
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # "Additional TBNA"
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)}, # Tool-in-lesion confirmed via

    # Specimen & Outcomes
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "136 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)