import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

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

# ------------------------------------------
# Case: 4507663
# ------------------------------------------
text_4507663 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Lisa Thompson, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Pentax EB-1990i linear EBUS bronchoscope
   - Needle: 22-gauge Standard FNA (Standard FNA)
   - STATIONS SAMPLED: 4 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 4R: 2 passes, short axis 23.5mm
     * Station 4L: 4 passes, short axis 14.3mm
     * Station 10R: 2 passes, short axis 11.1mm
     * Station 2L: 2 passes, short axis 20.1mm

   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Monarch Robotic Bronchoscopy System (Auris Health (J&J))
   - Registration method: CT-to-body
   - Registration accuracy: 3.2 mm
   - Navigation to peripheral lesion: RML medial (B5)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Adjacent view of 31.5mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RML lobe
   - Forceps biopsies obtained: 5 specimens
   - Additional TBNA: 4 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Augmented fluoroscopy
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 08:30 - 10:15 (105 minutes)
ANESTHESIA: General anesthesia (ASA 4)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Lisa Thompson, MD
[REDACTED]"""

entities_4507663 = [
    # Procedure Methods & Actions
    {"label": "PROC_METHOD", **get_span(text_4507663, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_4507663, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_4507663, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_4507663, "Monarch Robotic Bronchoscopy System", 1)},
    {"label": "PROC_METHOD", **get_span(text_4507663, "ENDOBRONCHIAL ULTRASOUND", 2)},
    {"label": "PROC_METHOD", **get_span(text_4507663, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4507663, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "PROC_ACTION", **get_span(text_4507663, "TBNA", 2)}, # "Additional TBNA"
    {"label": "PROC_ACTION", **get_span(text_4507663, "Brushings", 1)},
    {"label": "PROC_METHOD", **get_span(text_4507663, "Augmented fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4507663, "BAL", 1)},
    {"label": "PROC_ACTION", **get_span(text_4507663, "ROSE", 1)},

    # Devices
    {"label": "DEV_INSTRUMENT", **get_span(text_4507663, "Pentax EB-1990i linear EBUS bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4507663, "22-gauge", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4507663, "miniprobe", 1)},

    # Anatomy
    {"label": "ANAT_LN_STATION", **get_span(text_4507663, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4507663, "Station 4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4507663, "Station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4507663, "Station 2L", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4507663, "RML medial (B5)", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4507663, "RML lobe", 1)},

    # Measurements & Counts
    {"label": "MEAS_COUNT", **get_span(text_4507663, "2 passes", 1)}, # 4R
    {"label": "MEAS_SIZE", **get_span(text_4507663, "23.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4507663, "4 passes", 1)}, # 4L
    {"label": "MEAS_SIZE", **get_span(text_4507663, "14.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4507663, "2 passes", 2)}, # 10R
    {"label": "MEAS_SIZE", **get_span(text_4507663, "11.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4507663, "2 passes", 3)}, # 2L
    {"label": "MEAS_SIZE", **get_span(text_4507663, "20.1mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4507663, "31.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4507663, "5 specimens", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4507663, "4 passes", 2)}, # Additional TBNA
    {"label": "MEAS_COUNT", **get_span(text_4507663, "2 specimens", 1)},

    # Observations & Lesions
    {"label": "OBS_LESION", **get_span(text_4507663, "peripheral lesion", 1)},
    {"label": "OBS_LESION", **get_span(text_4507663, "peripheral lung lesion", 1)},
    {"label": "OBS_LESION", **get_span(text_4507663, "PERIPHERAL LESION", 1)},
    {"label": "OBS_LESION", **get_span(text_4507663, "peripheral pulmonary lesion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4507663, "None", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_4507663, "EBUS-TBNA specimens", 1)},
    {"label": "SPECIMEN", **get_span(text_4507663, "Transbronchial biopsies", 1)},
    {"label": "SPECIMEN", **get_span(text_4507663, "Brushings", 2)},

    # Context
    {"label": "CTX_TIME", **get_span(text_4507663, "08:30", 1)},
    {"label": "CTX_TIME", **get_span(text_4507663, "10:15", 1)},
    {"label": "CTX_TIME", **get_span(text_4507663, "105 minutes", 1)},
]

BATCH_DATA.append({"id": "4507663", "text": text_4507663, "entities": entities_4507663})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)