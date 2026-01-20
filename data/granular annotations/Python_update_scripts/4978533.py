import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from inside the 'scripts' or 'data' directory
# and the repo root is one or two levels up. Adjust if necessary.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports from 'scripts'
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the add_case utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Please ensure you are running this script from the correct location within the repository.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
            
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 74-8829-C_syn_1
# ==========================================
text_1 = """Indication: RUL Adenocarcinoma.
Procedure: Microwave Ablation.
Probe: Neuwave 14mm.
Settings: 60W, 6 min.
Guidance: ENB + R-EBUS.
Result: Good ablation zone. No complications.
Plan: Discharge tomorrow."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14mm", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_1, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "6 min", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "R-EBUS", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 74-8829-C_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: Bronchoscopic Microwave Ablation.
CLINICAL SUMMARY: Patient with medically inoperable RUL adenocarcinoma.
PROCEDURE: The target lesion in the RUL anterior segment was localized using electromagnetic navigation and confirmed via radial EBUS (contact view). A Neuwave microwave antenna was deployed. Microwave energy was delivered at 60 Watts for 6 minutes. Post-ablation imaging verified adequate coverage of the lesion. The patient tolerated the procedure well."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Neuwave", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "microwave antenna", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_2, "60 Watts", 1)},
    {"label": "MEAS_TIME", **get_span(text_2, "6 minutes", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 74-8829-C_syn_3
# ==========================================
text_3 = """Service: 31641 (Destruction of tumor).
Method: Microwave Ablation.
Device: Neuwave System.
Support: 31627 (Navigation), 31654 (Radial EBUS).
Narrative: Navigated to RUL nodule. Verified tool-in-lesion. Delivered microwave energy to destroy tumor. Post-procedure check negative for pneumothorax."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Neuwave System", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodule", 1)},
    # Fixed: "Microwave" (line 2) vs "microwave" (line 5). Lowercase "microwave" is the 1st occurrence of that exact string.
    {"label": "PROC_METHOD", **get_span(text_3, "microwave", 1)}, 
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3, "negative for pneumothorax", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 74-8829-C_syn_4
# ==========================================
text_4 = """Procedure: Microwave Ablation
Patient: [REDACTED]
Location: RUL anterior.
Steps:
1. Navigated to lesion (SuperDimension).
2. Confirmed with Radial EBUS.
3. Inserted Microwave catheter.
4. Ablated 60W for 6 mins.
5. Checked airway - clear.
Plan: Post-op CT."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL anterior", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "SuperDimension", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Microwave catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Ablated", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_4, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_4, "6 mins", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 74-8829-C_syn_5
# ==========================================
text_5 = """done by Dr Foster for [REDACTED] Sato. RUL cancer. used the superD to get there and radial ebus to see it. put the microwave needle in. burned it for 6 mins at 60 watts. looks like we got it all based on the scan after. patient woke up fine no pneumo."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "superD", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "radial ebus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "microwave needle", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "6 mins", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_5, "60 watts", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no pneumo", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 74-8829-C_syn_6
# ==========================================
text_6 = """Bronchoscopic microwave ablation. Right upper lobe nodule. General anesthesia. Electromagnetic navigation to RUL anterior segment. Target confirmed in contact position with radial EBUS. Microwave probe inserted. Ablation performed at 60W for 6 minutes. Lesion coverage confirmed. Airway patent. Extubated."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "microwave", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Microwave probe", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_6, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_6, "6 minutes", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "Airway patent", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 74-8829-C_syn_7
# ==========================================
text_7 = """[Indication]
RUL Adenocarcinoma.
[Anesthesia]
General.
[Description]
Navigation to RUL anterior segment. Microwave ablation (60W x 6min). Lesion destroyed. No complications.
[Plan]
[REDACTED] in 24h."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Microwave", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_7, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "6min", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Lesion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "No complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 74-8829-C_syn_8
# ==========================================
text_8 = """[REDACTED] in for ablation of his right upper lobe lung cancer. We used a microwave probe inserted through the bronchoscope. After finding the tumor with navigation and ultrasound, we applied microwave energy for 6 minutes. This heated the tumor enough to destroy it. He is recovering well."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lung cancer", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "microwave probe", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "microwave", 2)}, # "microwave energy" is 2nd mention
    {"label": "MEAS_TIME", **get_span(text_8, "6 minutes", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 74-8829-C_syn_9
# ==========================================
text_9 = """Procedure: Bronchoscopic tumor destruction.
Modality: Microwave energy.
Action: The RUL neoplasm was targeted. The microwave antenna was positioned. Thermal energy was delivered to ablate the mass. 
Result: Therapeutic destruction of the tumor."""

entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "destruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Microwave", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "neoplasm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "microwave antenna", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "destruction", 2)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 74-8829-C
# ==========================================
text_10 = """DATE: [REDACTED]
PATIENT: [REDACTED] || MRN: [REDACTED]
SURGEON: Dr. Amanda Foster
FACILITY: [REDACTED]

PREOP DX: RUL nodule, 2.1 cm, adenocarcinoma
POSTOP DX: Same  
OPERATION: Bronchoscopic microwave ablation

ANESTHESIA: General with ETT
EBL: <10cc
COMPLICATIONS: None

PROCEDURE NOTE:
62M with RUL adenocarcinoma, medically inoperable. Bronchoscopy performed. ENB navigation to RUL anterior segment lesion (superDimension system). R-EBUS confirmed target in contact position. Microwave probe (Neuwave, 14mm antenna) inserted. Ablation: 60W x 6 min. Good lesion coverage on post-ablation imaging. Airways inspected - no complications. Extubated, stable to PACU.

PLAN: CXR in 4h, CT in 24h, discharge tomorrow if stable, f/u 4 weeks.

A. Foster, MD
Interventional Pulmonology"""

entities_10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.1 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "microwave", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)}, # In "COMPLICATIONS: None"
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "adenocarcinoma", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "ENB navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL anterior segment", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "superDimension system", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "R-EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Microwave probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "antenna", 1)},
    # Fixed: "ablation" (line 7) vs "Ablation" (line 15). "Ablation" is the 1st occurrence of that exact capitalized string.
    {"label": "PROC_ACTION", **get_span(text_10, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_10, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "6 min", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)