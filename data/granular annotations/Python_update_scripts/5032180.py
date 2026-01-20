import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
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
# Case 1: 5032180
# ==========================================
text_5032180 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: LCDR John Park, MD

Indication: Empyema
Side: Right

PROCEDURE: Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 12Fr pigtail catheter inserted.
895mL turbid fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Park, MD"""

entities_5032180 = [
    {"label": "OBS_LESION", **get_span(text_5032180, "Empyema")},
    {"label": "LATERALITY", **get_span(text_5032180, "Right")},
    {"label": "ANAT_PLEURA", **get_span(text_5032180, "Pleural")},
    {"label": "DEV_CATHETER", **get_span(text_5032180, "Drainage Catheter")},
    {"label": "MEDICATION", **get_span(text_5032180, "lidocaine")},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5032180, "12Fr")},
    {"label": "DEV_CATHETER", **get_span(text_5032180, "pigtail catheter")},
    {"label": "MEAS_VOL", **get_span(text_5032180, "895mL")},
    {"label": "OBS_FINDING", **get_span(text_5032180, "turbid")},
    {"label": "SPECIMEN", **get_span(text_5032180, "fluid")},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5032180, "no PTX")},
]
BATCH_DATA.append({"id": "5032180", "text": text_5032180, "entities": entities_5032180})

# ==========================================
# Case 2: 74-8829-C_syn_1
# ==========================================
text_syn_1 = """Indication: RUL Adenocarcinoma.
Procedure: Microwave Ablation.
Probe: Neuwave 14mm.
Settings: 60W, 6 min.
Guidance: ENB + R-EBUS.
Result: Good ablation zone. No complications.
Plan: Discharge tomorrow."""

entities_syn_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_1, "RUL")},
    {"label": "OBS_LESION", **get_span(text_syn_1, "Adenocarcinoma")},
    {"label": "PROC_ACTION", **get_span(text_syn_1, "Ablation")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_1, "Neuwave")},
    {"label": "MEAS_SIZE", **get_span(text_syn_1, "14mm")},
    {"label": "MEAS_ENERGY", **get_span(text_syn_1, "60W")},
    {"label": "MEAS_TIME", **get_span(text_syn_1, "6 min")},
    {"label": "PROC_METHOD", **get_span(text_syn_1, "ENB")},
    {"label": "PROC_METHOD", **get_span(text_syn_1, "R-EBUS")},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_1, "No complications")},
]
BATCH_DATA.append({"id": "74-8829-C_syn_1", "text": text_syn_1, "entities": entities_syn_1})

# ==========================================
# Case 3: 74-8829-C_syn_2
# ==========================================
text_syn_2 = """OPERATIVE REPORT: Bronchoscopic Microwave Ablation.
CLINICAL SUMMARY: Patient with medically inoperable RUL adenocarcinoma.
PROCEDURE: The target lesion in the RUL anterior segment was localized using electromagnetic navigation and confirmed via radial EBUS (contact view). A Neuwave microwave antenna was deployed. Microwave energy was delivered at 60 Watts for 6 minutes. Post-ablation imaging verified adequate coverage of the lesion. The patient tolerated the procedure well."""

entities_syn_2 = [
    {"label": "PROC_ACTION", **get_span(text_syn_2, "Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_2, "adenocarcinoma")},
    {"label": "OBS_LESION", **get_span(text_syn_2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_2, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_2, "anterior segment")},
    {"label": "PROC_METHOD", **get_span(text_syn_2, "electromagnetic navigation")},
    {"label": "PROC_METHOD", **get_span(text_syn_2, "radial EBUS")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_2, "Neuwave microwave antenna")},
    {"label": "MEAS_ENERGY", **get_span(text_syn_2, "60 Watts")},
    {"label": "MEAS_TIME", **get_span(text_syn_2, "6 minutes")},
    {"label": "OBS_LESION", **get_span(text_syn_2, "lesion", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_2", "text": text_syn_2, "entities": entities_syn_2})

# ==========================================
# Case 4: 74-8829-C_syn_3
# ==========================================
text_syn_3 = """Service: 31641 (Destruction of tumor).
Method: Microwave Ablation.
Device: Neuwave System.
Support: 31627 (Navigation), 31654 (Radial EBUS).
Narrative: Navigated to RUL nodule. Verified tool-in-lesion. Delivered microwave energy to destroy tumor. Post-procedure check negative for pneumothorax."""

entities_syn_3 = [
    {"label": "PROC_ACTION", **get_span(text_syn_3, "Destruction")},
    {"label": "OBS_LESION", **get_span(text_syn_3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_3, "Ablation")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_3, "Neuwave System")},
    {"label": "PROC_METHOD", **get_span(text_syn_3, "Navigation")},
    {"label": "PROC_METHOD", **get_span(text_syn_3, "Radial EBUS")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_3, "RUL")},
    {"label": "OBS_LESION", **get_span(text_syn_3, "nodule")},
    {"label": "OBS_LESION", **get_span(text_syn_3, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_3, "negative for pneumothorax")},
]
BATCH_DATA.append({"id": "74-8829-C_syn_3", "text": text_syn_3, "entities": entities_syn_3})

# ==========================================
# Case 5: 74-8829-C_syn_4
# ==========================================
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
    {"label": "PROC_ACTION", **get_span(text_syn_4, "Ablation")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_4, "RUL")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_4, "anterior")},
    {"label": "OBS_LESION", **get_span(text_syn_4, "lesion")},
    {"label": "PROC_METHOD", **get_span(text_syn_4, "SuperDimension")},
    {"label": "PROC_METHOD", **get_span(text_syn_4, "Radial EBUS")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_4, "Microwave catheter")},
    {"label": "PROC_ACTION", **get_span(text_syn_4, "Ablated")},
    {"label": "MEAS_ENERGY", **get_span(text_syn_4, "60W")},
    {"label": "MEAS_TIME", **get_span(text_syn_4, "6 mins")},
]
BATCH_DATA.append({"id": "74-8829-C_syn_4", "text": text_syn_4, "entities": entities_syn_4})

# ==========================================
# Case 6: 74-8829-C_syn_5
# ==========================================
text_syn_5 = """done by Dr Foster for [REDACTED] Sato. RUL cancer. used the superD to get there and radial ebus to see it. put the microwave needle in. burned it for 6 mins at 60 watts. looks like we got it all based on the scan after. patient woke up fine no pneumo."""

entities_syn_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_5, "RUL")},
    {"label": "OBS_LESION", **get_span(text_syn_5, "cancer")},
    {"label": "PROC_METHOD", **get_span(text_syn_5, "superD")},
    {"label": "PROC_METHOD", **get_span(text_syn_5, "radial ebus")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_5, "microwave needle")},
    {"label": "MEAS_TIME", **get_span(text_syn_5, "6 mins")},
    {"label": "MEAS_ENERGY", **get_span(text_syn_5, "60 watts")},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_5, "no pneumo")},
]
BATCH_DATA.append({"id": "74-8829-C_syn_5", "text": text_syn_5, "entities": entities_syn_5})

# ==========================================
# Case 7: 74-8829-C_syn_6
# ==========================================
text_syn_6 = """Bronchoscopic microwave ablation. Right upper lobe nodule. General anesthesia. Electromagnetic navigation to RUL anterior segment. Target confirmed in contact position with radial EBUS. Microwave probe inserted. Ablation performed at 60W for 6 minutes. Lesion coverage confirmed. Airway patent. Extubated."""

entities_syn_6 = [
    {"label": "PROC_ACTION", **get_span(text_syn_6, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_6, "Right upper lobe")},
    {"label": "OBS_LESION", **get_span(text_syn_6, "nodule")},
    {"label": "PROC_METHOD", **get_span(text_syn_6, "Electromagnetic navigation")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_6, "RUL")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_6, "anterior segment")},
    {"label": "PROC_METHOD", **get_span(text_syn_6, "radial EBUS")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_6, "Microwave probe")},
    {"label": "PROC_ACTION", **get_span(text_syn_6, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_6, "60W")},
    {"label": "MEAS_TIME", **get_span(text_syn_6, "6 minutes")},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_syn_6, "Airway patent")},
]
BATCH_DATA.append({"id": "74-8829-C_syn_6", "text": text_syn_6, "entities": entities_syn_6})

# ==========================================
# Case 8: 74-8829-C_syn_7
# ==========================================
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
    {"label": "OBS_LESION", **get_span(text_syn_7, "Adenocarcinoma")},
    {"label": "PROC_METHOD", **get_span(text_syn_7, "Navigation")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_7, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_7, "anterior segment")},
    {"label": "PROC_ACTION", **get_span(text_syn_7, "ablation")},
    {"label": "MEAS_ENERGY", **get_span(text_syn_7, "60W")},
    {"label": "MEAS_TIME", **get_span(text_syn_7, "6min")},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_7, "No complications")},
]
BATCH_DATA.append({"id": "74-8829-C_syn_7", "text": text_syn_7, "entities": entities_syn_7})

# ==========================================
# Case 9: 74-8829-C_syn_8
# ==========================================
text_syn_8 = """[REDACTED] in for ablation of his right upper lobe lung cancer. We used a microwave probe inserted through the bronchoscope. After finding the tumor with navigation and ultrasound, we applied microwave energy for 6 minutes. This heated the tumor enough to destroy it. He is recovering well."""

entities_syn_8 = [
    {"label": "PROC_ACTION", **get_span(text_syn_8, "ablation")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_8, "right upper lobe")},
    {"label": "OBS_LESION", **get_span(text_syn_8, "lung cancer")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_8, "microwave probe")},
    {"label": "OBS_LESION", **get_span(text_syn_8, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_8, "navigation")},
    {"label": "PROC_METHOD", **get_span(text_syn_8, "ultrasound")},
    {"label": "MEAS_TIME", **get_span(text_syn_8, "6 minutes")},
    {"label": "OBS_LESION", **get_span(text_syn_8, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_8", "text": text_syn_8, "entities": entities_syn_8})

# ==========================================
# Case 10: 74-8829-C_syn_9
# ==========================================
text_syn_9 = """Procedure: Bronchoscopic tumor destruction.
Modality: Microwave energy.
Action: The RUL neoplasm was targeted. The microwave antenna was positioned. Thermal energy was delivered to ablate the mass. 
Result: Therapeutic destruction of the tumor."""

entities_syn_9 = [
    {"label": "OBS_LESION", **get_span(text_syn_9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_9, "destruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_9, "RUL")},
    {"label": "OBS_LESION", **get_span(text_syn_9, "neoplasm")},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_9, "microwave antenna")},
    {"label": "PROC_ACTION", **get_span(text_syn_9, "ablate")},
    {"label": "OBS_LESION", **get_span(text_syn_9, "mass")},
    {"label": "PROC_ACTION", **get_span(text_syn_9, "destruction", 2)},
    {"label": "OBS_LESION", **get_span(text_syn_9, "tumor", 2)},
]
BATCH_DATA.append({"id": "74-8829-C_syn_9", "text": text_syn_9, "entities": entities_syn_9})

# ==========================================
# Case 11: 74-8829-C
# ==========================================
text_74_8829_C = """DATE: [REDACTED]
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

entities_74_8829_C = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_74_8829_C, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_74_8829_C, "nodule")},
    {"label": "MEAS_SIZE", **get_span(text_74_8829_C, "2.1 cm")},
    {"label": "OBS_LESION", **get_span(text_74_8829_C, "adenocarcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_74_8829_C, "ablation")},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_74_8829_C, "None")},
    {"label": "ANAT_LUNG_LOC", **get_span(text_74_8829_C, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(text_74_8829_C, "adenocarcinoma", 2)},
    {"label": "PROC_METHOD", **get_span(text_74_8829_C, "ENB")},
    {"label": "PROC_METHOD", **get_span(text_74_8829_C, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_74_8829_C, "RUL", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_74_8829_C, "anterior segment")},
    {"label": "OBS_LESION", **get_span(text_74_8829_C, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_74_8829_C, "superDimension system")},
    {"label": "PROC_METHOD", **get_span(text_74_8829_C, "R-EBUS")},
    {"label": "DEV_INSTRUMENT", **get_span(text_74_8829_C, "Microwave probe")},
    {"label": "DEV_INSTRUMENT", **get_span(text_74_8829_C, "Neuwave")},
    {"label": "MEAS_SIZE", **get_span(text_74_8829_C, "14mm")},
    {"label": "DEV_INSTRUMENT", **get_span(text_74_8829_C, "antenna")},
    {"label": "PROC_ACTION", **get_span(text_74_8829_C, "Ablation")},
    {"label": "MEAS_ENERGY", **get_span(text_74_8829_C, "60W")},
    {"label": "MEAS_TIME", **get_span(text_74_8829_C, "6 min")},
    {"label": "OBS_LESION", **get_span(text_74_8829_C, "lesion", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_74_8829_C, "no complications")},
]
BATCH_DATA.append({"id": "74-8829-C", "text": text_74_8829_C, "entities": entities_74_8829_C})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)