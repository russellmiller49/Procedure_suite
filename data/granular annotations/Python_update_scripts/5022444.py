import sys
from pathlib import Path

# 1. Setup Repo Root (adjust depth as needed for your file structure)
# Assuming this script runs from a folder like `experiments/data_prep/` 
# and the repo root is 2 levels up.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))

# 2. Import the Utility Function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Could not import 'add_case'. Ensure you are running from the correct repository context.")
    sys.exit(1)

# 3. Helper for Span Extraction
def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term),
        "text": term
    }

BATCH_DATA = []

# ==========================================
# FILE: 5022444.json
# ==========================================

# --- Note 5022444 ---
id_5022444 = "5022444"
text_5022444 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Lisa Thompson, MD
Fellow: N/A
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 85 years
Sex: Male
ASA Class: 4

PRE-PROCEDURE:
1. Patient id[REDACTED] confirmed with two id[REDACTED]
2. Informed consent verified on chart
3. NPO status confirmed (>8 hours)
4. Anticoagulation status reviewed - not on anticoagulation
5. Allergies reviewed - NKDA
6. Time-out performed with all team members

INDICATION:
Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy
Target lesion: 31.5mm part-solid nodule, RML medial (B5)
Bronchus sign: Positive

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: 22G Standard FNA
- Robotic platform: Monarch (Auris Health (J&J))
- Radial EBUS: 20 MHz miniprobe
- Biopsy forceps: Standard
- Cytology brushes: Standard

PROCEDURE STEPS:

PART A - LINEAR EBUS FOR STAGING:
1. Bronchoscope inserted through ETT
2. Standard airway inspection performed - airways patent, no endobronchial lesions
3. Linear EBUS scope exchanged
4. Systematic lymph node survey performed
5. Following stations id[REDACTED] and sampled:
   - Station 4R: 23.5mm, 2 passes
   - Station 4L: 14.3mm, 4 passes
   - Station 10R: 11.1mm, 2 passes
   - Station 2L: 20.1mm, 2 passes
6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - squamous cell carcinoma

PART B - ROBOTIC NAVIGATION:
1. Monarch system prepared and registered
2. Registration error: 3.2mm (acceptable)
3. Robotic catheter advanced to RML medial (B5)
4. Radial EBUS deployed - Adjacent view obtained
5. Tool-in-lesion confirmed with Augmented fluoroscopy
6. Sampling performed:
   - Forceps biopsies: 5
   - TBNA passes: 4
   - Brushings: 2
7. ROSE performed - Malignant - squamous cell carcinoma
8. BAL obtained from RML

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 4R, 4L, 10R, 2L) → Cytology, cell block
2. TBBx RML → Surgical pathology
3. Brushings → Cytology
4. BAL → Cultures (bacterial, fungal, AFB)

COMPLICATIONS: None
ESTIMATED BLOOD LOSS: <10 mL

IMPRESSION:
1. Completed EBUS-TBNA mediastinal staging
2. Completed robotic bronchoscopy with peripheral lung biopsy
3. No immediate complications

PLAN:
1. Monitor in recovery x 2 hours
2. Discharge home if stable
3. Follow-up in clinic for pathology results
4. Results to be discussed at tumor board

Procedure performed under direct supervision of Lisa Thompson, MD

Fellow, PGY-None
Lisa Thompson, MD (Attending - present for entire procedure)"""

entities_5022444 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_5022444, "Lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(text_5022444, "NSCLC", 1)},
    {"label": "OBS_LESION", **get_span(text_5022444, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5022444, "31.5mm", 1)},
    {"label": "OBS_LESION", **get_span(text_5022444, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5022444, "RML medial (B5)", 1)},
    
    # Equipment
    {"label": "PROC_METHOD", **get_span(text_5022444, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5022444, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5022444, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_5022444, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_5022444, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_5022444, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5022444, "20 MHz miniprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5022444, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5022444, "Cytology brushes", 1)},
    
    # Part A
    {"label": "PROC_METHOD", **get_span(text_5022444, "Linear EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_5022444, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5022444, "23.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5022444, "2 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5022444, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5022444, "14.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5022444, "4 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5022444, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5022444, "11.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5022444, "2 passes", 2)}, # 2nd occurrence of "2 passes" in the list
    {"label": "ANAT_LN_STATION", **get_span(text_5022444, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5022444, "20.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5022444, "2 passes", 3)}, # 3rd occurrence
    {"label": "OBS_ROSE", **get_span(text_5022444, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_5022444, "squamous cell carcinoma", 1)},
    
    # Part B
    {"label": "PROC_METHOD", **get_span(text_5022444, "Monarch", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5022444, "RML medial (B5)", 2)},
    {"label": "PROC_METHOD", **get_span(text_5022444, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_5022444, "Augmented fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5022444, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_5022444, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5022444, "5", 2)}, 
    {"label": "PROC_ACTION", **get_span(text_5022444, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5022444, "4", 6)}, 
    
    {"label": "PROC_ACTION", **get_span(text_5022444, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5022444, "2", 8)},

    {"label": "OBS_ROSE", **get_span(text_5022444, "Malignant", 2)},
    {"label": "OBS_ROSE", **get_span(text_5022444, "squamous cell carcinoma", 2)},
    {"label": "PROC_ACTION", **get_span(text_5022444, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5022444, "RML", 4)}, 

    # Post/Specimens
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5022444, "no pneumothorax", 1)},
    {"label": "MEAS_VOL", **get_span(text_5022444, "10 mL", 1)},
    
    # Impression
    {"label": "PROC_ACTION", **get_span(text_5022444, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_5022444, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_5022444, "biopsy", 1)}, 
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5022444, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": id_5022444, "text": text_5022444, "entities": entities_5022444})

# ==========================================
# FILE: 74-8829-C.json
# ==========================================

# --- Note 74-8829-C_syn_1 ---
id_syn_1 = "74-8829-C_syn_1"
text_syn_1 = """Indication: RUL Adenocarcinoma.
Procedure: Microwave Ablation.
Probe: Neuwave 14mm.
Settings: 60W, 6 min.
Guidance: ENB + R-EBUS.
Result: Good ablation zone. No complications.
Plan: Discharge tomorrow."""

entities_syn_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_1, "Adenocarcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_1, "Microwave Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_1, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(text_syn_1, "14mm", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_1, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_1, "6 min", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_1, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_1, "R-EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_syn_1, "ablation zone", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_1, "No complications", 1)},
]
BATCH_DATA.append({"id": id_syn_1, "text": text_syn_1, "entities": entities_syn_1})

# --- Note 74-8829-C_syn_2 ---
id_syn_2 = "74-8829-C_syn_2"
text_syn_2 = """OPERATIVE REPORT: Bronchoscopic Microwave Ablation.
CLINICAL SUMMARY: Patient with medically inoperable RUL adenocarcinoma.
PROCEDURE: The target lesion in the RUL anterior segment was localized using electromagnetic navigation and confirmed via radial EBUS (contact view). A Neuwave microwave antenna was deployed. Microwave energy was delivered at 60 Watts for 6 minutes. Post-ablation imaging verified adequate coverage of the lesion. The patient tolerated the procedure well."""

entities_syn_2 = [
    {"label": "PROC_ACTION", **get_span(text_syn_2, "Microwave Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_2, "adenocarcinoma", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_2, "target lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_2, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_2, "electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_2, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_2, "Neuwave microwave antenna", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_2, "60 Watts", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_2, "6 minutes", 1)},
]
BATCH_DATA.append({"id": id_syn_2, "text": text_syn_2, "entities": entities_syn_2})

# --- Note 74-8829-C_syn_3 ---
id_syn_3 = "74-8829-C_syn_3"
text_syn_3 = """Service: 31641 (Destruction of tumor).
Method: Microwave Ablation.
Device: Neuwave System.
Support: 31627 (Navigation), 31654 (Radial EBUS).
Narrative: Navigated to RUL nodule. Verified tool-in-lesion. Delivered microwave energy to destroy tumor. Post-procedure check negative for pneumothorax."""

entities_syn_3 = [
    {"label": "PROC_ACTION", **get_span(text_syn_3, "Destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_3, "Microwave Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_3, "Neuwave System", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_3, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_3, "nodule", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_3, "microwave energy", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_3, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_3, "negative for pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_syn_3, "text": text_syn_3, "entities": entities_syn_3})

# --- Note 74-8829-C_syn_4 ---
id_syn_4 = "74-8829-C_syn_4"
text_syn_4 = """Procedure: Microwave Ablation
Patient: [REDACTED]
Location: RUL anterior.
Steps:
1. Navigated to lesion (SuperDimension).
2. Confirmed with Radial EBUS.
3. Inserted Microwave catheter.
4. Ablated 60W for 6 mins.
5. Checked airway - clear.
Plan: Post-op CT."""

entities_syn_4 = [
    {"label": "PROC_ACTION", **get_span(text_syn_4, "Microwave Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_4, "RUL anterior", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_4, "SuperDimension", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_4, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_4, "Microwave catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_4, "Ablated", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_4, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_4, "6 mins", 1)},
]
BATCH_DATA.append({"id": id_syn_4, "text": text_syn_4, "entities": entities_syn_4})

# --- Note 74-8829-C_syn_5 ---
id_syn_5 = "74-8829-C_syn_5"
text_syn_5 = """done by Dr Foster for [REDACTED] Sato. RUL cancer. used the superD to get there and radial ebus to see it. put the microwave needle in. burned it for 6 mins at 60 watts. looks like we got it all based on the scan after. patient woke up fine no pneumo."""

entities_syn_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_5, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_5, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_5, "superD", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_5, "radial ebus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_5, "microwave needle", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_5, "6 mins", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_5, "60 watts", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_5, "no pneumo", 1)},
]
BATCH_DATA.append({"id": id_syn_5, "text": text_syn_5, "entities": entities_syn_5})

# --- Note 74-8829-C_syn_6 ---
id_syn_6 = "74-8829-C_syn_6"
text_syn_6 = """Bronchoscopic microwave ablation. Right upper lobe nodule. General anesthesia. Electromagnetic navigation to RUL anterior segment. Target confirmed in contact position with radial EBUS. Microwave probe inserted. Ablation performed at 60W for 6 minutes. Lesion coverage confirmed. Airway patent. Extubated."""

entities_syn_6 = [
    {"label": "PROC_ACTION", **get_span(text_syn_6, "microwave ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_6, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_6, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_6, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_6, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_6, "Microwave probe", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_6, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_6, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_6, "6 minutes", 1)},
]
BATCH_DATA.append({"id": id_syn_6, "text": text_syn_6, "entities": entities_syn_6})

# --- Note 74-8829-C_syn_7 ---
id_syn_7 = "74-8829-C_syn_7"
text_syn_7 = """[Indication]
RUL Adenocarcinoma.
[Anesthesia]
General.
[Description]
Navigation to RUL anterior segment. Microwave ablation (60W x 6min). Lesion destroyed. No complications.
[Plan]
[REDACTED] in 24h."""

entities_syn_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_7, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_7, "RUL anterior segment", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_7, "Microwave ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_7, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_7, "6min", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_7, "No complications", 1)},
]
BATCH_DATA.append({"id": id_syn_7, "text": text_syn_7, "entities": entities_syn_7})

# --- Note 74-8829-C_syn_8 ---
id_syn_8 = "74-8829-C_syn_8"
text_syn_8 = """[REDACTED] in for ablation of his right upper lobe lung cancer. We used a microwave probe inserted through the bronchoscope. After finding the tumor with navigation and ultrasound, we applied microwave energy for 6 minutes. This heated the tumor enough to destroy it. He is recovering well."""

entities_syn_8 = [
    {"label": "PROC_ACTION", **get_span(text_syn_8, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_8, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_8, "lung cancer", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_8, "microwave probe", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_8, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_8, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_8, "ultrasound", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_8, "microwave energy", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_8, "6 minutes", 1)},
]
BATCH_DATA.append({"id": id_syn_8, "text": text_syn_8, "entities": entities_syn_8})

# --- Note 74-8829-C_syn_9 ---
id_syn_9 = "74-8829-C_syn_9"
text_syn_9 = """Procedure: Bronchoscopic tumor destruction.
Modality: Microwave energy.
Action: The RUL neoplasm was targeted. The microwave antenna was positioned. Thermal energy was delivered to ablate the mass. 
Result: Therapeutic destruction of the tumor."""

entities_syn_9 = [
    {"label": "PROC_ACTION", **get_span(text_syn_9, "tumor destruction", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_9, "Microwave energy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_9, "neoplasm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_9, "microwave antenna", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_9, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_9, "mass", 1)},
]
BATCH_DATA.append({"id": id_syn_9, "text": text_syn_9, "entities": entities_syn_9})

# --- Note 74-8829-C ---
id_base = "74-8829-C"
text_base = """DATE: [REDACTED]
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

entities_base = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_base, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_base, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_base, "2.1 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_base, "adenocarcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_base, "Bronchoscopic microwave ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_base, "None", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_base, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(text_base, "adenocarcinoma", 2)},
    {"label": "PROC_METHOD", **get_span(text_base, "ENB navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_base, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_base, "superDimension system", 1)},
    {"label": "PROC_METHOD", **get_span(text_base, "R-EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_base, "Microwave probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_base, "Neuwave", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_base, "14mm antenna", 1)},
    {"label": "PROC_ACTION", **get_span(text_base, "Ablation", 1)}, # Corrected from 2 to 1 because 'Ablation' (capitalized) is distinct from 'ablation' (lowercase)
    {"label": "MEAS_ENERGY", **get_span(text_base, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_base, "6 min", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_base, "no complications", 1)},
]
BATCH_DATA.append({"id": id_base, "text": text_base, "entities": entities_base})


# 4. Main Execution Loop
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")