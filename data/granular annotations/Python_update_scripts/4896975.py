import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 74-8829-C_syn_1
# ==========================================
t1 = """Indication: RUL Adenocarcinoma.
Procedure: Microwave Ablation.
Probe: Neuwave 14mm.
Settings: 60W, 6 min.
Guidance: ENB + R-EBUS.
Result: Good ablation zone. No complications.
Plan: Discharge tomorrow."""

e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Adenocarcinoma", 1)},
    # "Microwave Ablation" - Ablation is the action, Microwave is the technology/modality implied
    {"label": "PROC_ACTION", **get_span(t1, "Ablation", 1)}, 
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "14mm", 1)},
    {"label": "MEAS_ENERGY", **get_span(t1, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "6 min", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "R-EBUS", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 74-8829-C_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Bronchoscopic Microwave Ablation.
CLINICAL SUMMARY: Patient with medically inoperable RUL adenocarcinoma.
PROCEDURE: The target lesion in the RUL anterior segment was localized using electromagnetic navigation and confirmed via radial EBUS (contact view). A Neuwave microwave antenna was deployed. Microwave energy was delivered at 60 Watts for 6 minutes. Post-ablation imaging verified adequate coverage of the lesion. The patient tolerated the procedure well."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "adenocarcinoma", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Neuwave", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "microwave antenna", 1)},
    {"label": "MEAS_ENERGY", **get_span(t2, "60 Watts", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "6 minutes", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 74-8829-C_syn_3
# ==========================================
t3 = """Service: 31641 (Destruction of tumor).
Method: Microwave Ablation.
Device: Neuwave System.
Support: 31627 (Navigation), 31654 (Radial EBUS).
Narrative: Navigated to RUL nodule. Verified tool-in-lesion. Delivered microwave energy to destroy tumor. Post-procedure check negative for pneumothorax."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Destruction", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Neuwave System", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(t3, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "destroy", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t3, "negative for pneumothorax", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 74-8829-C_syn_4
# ==========================================
t4 = """Procedure: Microwave Ablation
Patient: [REDACTED]
Location: RUL anterior.
Steps:
1. Navigated to lesion (SuperDimension).
2. Confirmed with Radial EBUS.
3. Inserted Microwave catheter.
4. Ablated 60W for 6 mins.
5. Checked airway - clear.
Plan: Post-op CT."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL anterior", 1)},
    {"label": "OBS_LESION", **get_span(t4, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "SuperDimension", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Microwave catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Ablated", 1)},
    {"label": "MEAS_ENERGY", **get_span(t4, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t4, "6 mins", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 74-8829-C_syn_5
# ==========================================
t5 = """done by Dr Foster for [REDACTED] Sato. RUL cancer. used the superD to get there and radial ebus to see it. put the microwave needle in. burned it for 6 mins at 60 watts. looks like we got it all based on the scan after. patient woke up fine no pneumo."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "superD", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "radial ebus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "microwave needle", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "6 mins", 1)},
    {"label": "MEAS_ENERGY", **get_span(t5, "60 watts", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no pneumo", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 74-8829-C_syn_6
# ==========================================
t6 = """Bronchoscopic microwave ablation. Right upper lobe nodule. General anesthesia. Electromagnetic navigation to RUL anterior segment. Target confirmed in contact position with radial EBUS. Microwave probe inserted. Ablation performed at 60W for 6 minutes. Lesion coverage confirmed. Airway patent. Extubated."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Microwave probe", 1)},
    # ERROR FIX: 'Ablation' (Title Case) only appears once in the text (at the start of a sentence), though the word 'ablation' (lowercase) appeared earlier.
    {"label": "PROC_ACTION", **get_span(t6, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(t6, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t6, "6 minutes", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Lesion", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 74-8829-C_syn_7
# ==========================================
t7 = """[Indication]
RUL Adenocarcinoma.
[Anesthesia]
General.
[Description]
Navigation to RUL anterior segment. Microwave ablation (60W x 6min). Lesion destroyed. No complications.
[Plan]
[REDACTED] in 24h."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL anterior segment", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(t7, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t7, "6min", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Lesion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "No complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 74-8829-C_syn_8
# ==========================================
t8 = """[REDACTED] in for ablation of his right upper lobe lung cancer. We used a microwave probe inserted through the bronchoscope. After finding the tumor with navigation and ultrasound, we applied microwave energy for 6 minutes. This heated the tumor enough to destroy it. He is recovering well."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lung cancer", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "microwave probe", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "ultrasound", 1)},
    {"label": "MEAS_TIME", **get_span(t8, "6 minutes", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 74-8829-C_syn_9
# ==========================================
t9 = """Procedure: Bronchoscopic tumor destruction.
Modality: Microwave energy.
Action: The RUL neoplasm was targeted. The microwave antenna was positioned. Thermal energy was delivered to ablate the mass. 
Result: Therapeutic destruction of the tumor."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "neoplasm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "microwave antenna", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "destruction", 2)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 74-8829-C
# ==========================================
t10 = """DATE: [REDACTED]
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

e10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.1 cm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "adenocarcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "None", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t10, "adenocarcinoma", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL anterior segment", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "superDimension system", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "R-EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Microwave probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "antenna", 1)},
    # ERROR FIX: 'Ablation' (Title Case) only appears once (Line 16), though 'ablation' (lowercase) appeared earlier (Line 9).
    {"label": "PROC_ACTION", **get_span(t10, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(t10, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "6 min", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no complications", 1)},
]
BATCH_DATA.append({"id": "74-8829-C", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)