import sys
from pathlib import Path

# Set up path to import utility functions
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the add_case utility
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure you are running this from the correct repository structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text: {text[:50]}...")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 219775_syn_1
# ==========================================
t1 = """Indication: Hilar adenopathy.
Procedure: EBUS-TBNA.
Stations: 4R (2 passes), 7 (2 passes), 11L (1 pass).
ROSE: 4R/7 reactive, 11L non-diagnostic.
Complications: None.
Plan: Follow-up CT."""

e1 = [
    # Indication
    {"label": "ANAT_LN_STATION", **get_span(t1, "Hilar", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "adenopathy", 1)},
    
    # Procedure
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    
    # Stations / Counts
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "1 pass", 1)},
    
    # ROSE
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "reactive", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11L", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "non-diagnostic", 1)},
    
    # Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)},
]
BATCH_DATA.append({"id": "219775_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 219775_syn_2
# ==========================================
t2 = """PROCEDURE: Endobronchial Ultrasound-Guided Transbronchial Needle Aspiration.
CLINICAL HISTORY: Patient with PET-avid right paratracheal and subcarinal lymphadenopathy.
DESCRIPTION: The airway was inspected. No endobronchial lesions. EBUS performed. Station 4R (15mm) and Station 7 (20mm) sampled with 22G needle. ROSE confirmed lymphocytes. Station 11L sampled, scanty cellularity. No immediate complications."""

e2 = [
    # Header
    {"label": "PROC_METHOD", **get_span(t2, "Endobronchial Ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Transbronchial Needle Aspiration", 1)},
    
    # History
    {"label": "ANAT_LN_STATION", **get_span(t2, "right paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "subcarinal", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "lymphadenopathy", 1)},
    
    # Description
    {"label": "ANAT_AIRWAY", **get_span(t2, "airway", 1)},
    {"label": "OBS_LESION", **get_span(t2, "endobronchial lesions", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "15mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "20mm", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "sampled", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "22G needle", 1)},
    
    # Results
    {"label": "OBS_ROSE", **get_span(t2, "lymphocytes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "Station 11L", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "sampled", 2)},
    {"label": "OBS_ROSE", **get_span(t2, "scanty cellularity", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": "219775_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 219775_syn_3
# ==========================================
t3 = """Service: 31652 (EBUS sampling 1-2 stations), 31653 (3+ stations).
Technique: EBUS-TBNA.
Targets: Mediastinal and Hilar nodes.
Details: 
- Station 4R: 2 passes, benign.
- Station 7: 2 passes, benign.
- Station 11L: 1 pass, insufficient.
Device: 22 gauge Olympus needle."""

e3 = [
    # Service/Technique
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "sampling", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    
    # Targets
    {"label": "ANAT_LN_STATION", **get_span(t3, "Mediastinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Hilar", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodes", 1)},
    
    # Details
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 4R", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "benign", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "2 passes", 2)},
    {"label": "OBS_ROSE", **get_span(t3, "benign", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "1 pass", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "insufficient", 1)},
    
    # Device
    {"label": "DEV_NEEDLE", **get_span(t3, "22 gauge Olympus needle", 1)},
]
BATCH_DATA.append({"id": "219775_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 219775_syn_4
# ==========================================
t4 = """Procedure: EBUS
Indication: Staging lung cancer.
Nodes sampled:
1. 4R - >1cm node. 22ga needle. 2 passes. ROSE: Negative.
2. Subcarinal (7) - Large node. 2 passes. ROSE: Negative.
3. 11L - Small node. 1 pass. ROSE: N/A.
Result: Likely reactive nodes."""

e4 = [
    # Header
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t4, "lung cancer", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "sampled", 1)},
    
    # Node 1
    {"label": "ANAT_LN_STATION", **get_span(t4, "4R", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, ">1cm", 1)},
    {"label": "OBS_LESION", **get_span(t4, "node", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "22ga needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Negative", 1)},
    
    # Node 2
    {"label": "ANAT_LN_STATION", **get_span(t4, "Subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "7", 1)},
    {"label": "OBS_LESION", **get_span(t4, "node", 2)},
    {"label": "MEAS_COUNT", **get_span(t4, "2 passes", 2)},
    {"label": "OBS_ROSE", **get_span(t4, "Negative", 2)},
    
    # Node 3
    {"label": "ANAT_LN_STATION", **get_span(t4, "11L", 1)},
    {"label": "OBS_LESION", **get_span(t4, "node", 3)},
    {"label": "MEAS_COUNT", **get_span(t4, "1 pass", 1)},
    
    # Result
    {"label": "OBS_ROSE", **get_span(t4, "reactive", 1)},
    # FIXED: "nodes" appears twice but only once in lowercase. First occurrence is "Nodes sampled" (uppercase).
    # "Likely reactive nodes" contains the first lowercase instance.
    {"label": "OBS_LESION", **get_span(t4, "nodes", 1)},
]
BATCH_DATA.append({"id": "219775_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 219775_syn_5
# ==========================================
t5 = """Dr. Lee performed EBUS for [REDACTED]. We looked at the lymph nodes. Poked station 4R twice and station 7 twice using the 22 gauge needle. Both looked like just reactive tissue on the rapid stain. Tried to get 11L but it was too small, only one pass, didn't get much. Patient tolerated well."""

e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t5, "lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "22 gauge needle", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "reactive", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "one pass", 1)},
]
BATCH_DATA.append({"id": "219775_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 219775_syn_6
# ==========================================
t6 = """EBUS-TBNA performed under moderate sedation. Inspection revealed normal mucosa. Ultrasound localization of lymph node stations 4R, 7, and 11L. TBNA performed using 22G Vizishot needle. 
- 4R: 2 aspirates, lymphocytes present.
- 7: 2 aspirates, lymphocytes present.
- 11L: 1 aspirate, blood only.
Impression: Negative for malignancy by ROSE in 4R/7."""

e6 = [
    # Header/Desc
    {"label": "PROC_METHOD", **get_span(t6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Ultrasound", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "lymph node stations", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "11L", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 2)},
    {"label": "DEV_NEEDLE", **get_span(t6, "22G Vizishot needle", 1)},
    
    # 4R
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 2)},
    {"label": "MEAS_COUNT", **get_span(t6, "2 aspirates", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "lymphocytes", 1)},
    
    # 7
    {"label": "ANAT_LN_STATION", **get_span(t6, "7", 2)},
    {"label": "MEAS_COUNT", **get_span(t6, "2 aspirates", 2)},
    {"label": "OBS_ROSE", **get_span(t6, "lymphocytes", 2)},
    
    # 11L
    {"label": "ANAT_LN_STATION", **get_span(t6, "11L", 2)},
    {"label": "MEAS_COUNT", **get_span(t6, "1 aspirate", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "blood", 1)},
    
    # Impression
    {"label": "OBS_ROSE", **get_span(t6, "Negative for malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "7", 3)},
]
BATCH_DATA.append({"id": "219775_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 219775_syn_7
# ==========================================
t7 = """[Indication]
Mediastinal adenopathy.
[Procedure]
EBUS-TBNA.
[Findings]
- Stn 4R: Enlarged. 2 passes (22G). ROSE neg.
- Stn 7: Enlarged. 2 passes (22G). ROSE neg.
- Stn 11L: 1 pass. Insufficient.
[Outcome]
Stable."""

e7 = [
    # Indication
    {"label": "ANAT_LN_STATION", **get_span(t7, "Mediastinal", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "adenopathy", 1)},
    
    # Procedure
    {"label": "PROC_METHOD", **get_span(t7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    
    # Findings - 4R
    {"label": "ANAT_LN_STATION", **get_span(t7, "Stn 4R", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Enlarged", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "22G", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "neg", 1)},
    
    # Findings - 7
    {"label": "ANAT_LN_STATION", **get_span(t7, "Stn 7", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Enlarged", 2)},
    {"label": "MEAS_COUNT", **get_span(t7, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(t7, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(t7, "neg", 2)},
    
    # Findings - 11L
    {"label": "ANAT_LN_STATION", **get_span(t7, "Stn 11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "1 pass", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "Insufficient", 1)},
]
BATCH_DATA.append({"id": "219775_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 219775_syn_8
# ==========================================
t8 = """[REDACTED] for staging of his lung cancer. We used the ultrasound bronchoscope to see the glands in the chest. We took samples from the right paratracheal area (4R) and under the main airway split (Station 7). We also tried the left hilar area (11L). The pathologist in the room said the first two spots just showed inflammation cells, no cancer seen yet."""

e8 = [
    {"label": "OBS_LESION", **get_span(t8, "lung cancer", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "ultrasound bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "took samples", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "right paratracheal area", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "left hilar area", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "11L", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "inflammation cells", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "no cancer", 1)},
]
BATCH_DATA.append({"id": "219775_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 219775_syn_9
# ==========================================
t9 = """Procedure: EBUS-guided needle aspiration.
Indication: Lymphadenopathy.
Action: Nodes 4R, 7, 11L localized. Aspiration performed with 22G needle. 
Specimen: Cytology sent for cell block.
Result: Preliminary negative for malignancy."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "needle aspiration", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "11L", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "22G needle", 1)},
    {"label": "SPECIMEN", **get_span(t9, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(t9, "cell block", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "negative for malignancy", 1)},
]
BATCH_DATA.append({"id": "219775_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 219775 (Original)
# ==========================================
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
DATE: [REDACTED]
PHYSICIAN: Dr. S. Lee

PREOPERATIVE DIAGNOSIS: Right upper lobe lung mass with mediastinal lymphadenopathy (suspected N2 disease).
POSTOPERATIVE DIAGNOSIS: Same. Successful sampling of stations 4R, 7, 11L.

PROCEDURE: Flexible Bronchoscopy with EBUS-TBNA

ANESTHESIA: Laryngeal Mask Airway (LMA), Propofol TIVA.

DESCRIPTION:
The patient was brought to the endoscopy suite. Time out performed. LMA placed. 

White light bronchoscopy: Normal vocal cords. Trachea patent. Carina sharp. Right and Left bronchial trees inspected to subsegmental level. No endobronchial lesions visualized. 

EBUS Procedure:
The EBUS scope was introduced. Systematic evaluation of mediastinum performed.

1. Station 4R (Right Paratracheal): 1.2 cm short axis. Heterogeneous. 
    - Action: 2 passes with 22G Olympus ViziShot needle. 
    - ROSE: Heavily lymphoid, no malignant cells seen.

2. Station 7 (Subcarinal): 1.8 cm short axis. Triangular shape.
    - Action: 2 passes with 22G needle.
    - ROSE: Reactive lymphocytes.

3. Station 11L (Left Interlobar): 0.8 cm node.
    - Action: 1 pass. Technical difficulty due to angle.
    - ROSE: Non-diagnostic/paucicellular.

COMPLICATIONS: Minimal bleeding at puncture sites, self-limiting. No pneumothorax.

PLAN:
- Discharge home when alert.
- Final pathology pending (3-5 days).
- If benign, consider mediastinoscopy vs surveillance.
- Oncology follow-up [REDACTED].

S. Lee, MD
Pulmonary & Critical Care"""

e10 = [
    # Diagnosis
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lung mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "mediastinal", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "lymphadenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "sampling", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "stations 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "11L", 1)},
    
    # Procedure Header
    {"label": "PROC_ACTION", **get_span(t10, "Flexible Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 1)},
    
    # Desc
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right and Left bronchial trees", 1)},
    {"label": "OBS_LESION", **get_span(t10, "endobronchial lesions", 1)},
    
    # EBUS Desc
    {"label": "DEV_INSTRUMENT", **get_span(t10, "EBUS scope", 1)},
    
    # Stn 4R
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Right Paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.2 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22G Olympus ViziShot needle", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Heavily lymphoid", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "no malignant cells", 1)},
    
    # Stn 7
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Subcarinal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.8 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22G needle", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Reactive lymphocytes", 1)},
    
    # Stn 11L
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 11L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Left Interlobar", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "0.8 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "1 pass", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Non-diagnostic", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "paucicellular", 1)},
    
    # Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Minimal bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No pneumothorax", 1)},
]
BATCH_DATA.append({"id": "219775", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)