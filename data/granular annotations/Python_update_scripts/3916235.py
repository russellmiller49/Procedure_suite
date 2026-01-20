import sys
from pathlib import Path

# Set up the repository root assuming this script is inside a 'scripts' or 'data' subfolder
# Adjust levels=2 (e.g., repo/scripts/this_script.py -> repo)
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 3916235 (Interventional Pulmonology Report)
# ==========================================
id_3916235 = "3916235"
text_3916235 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Maria Santos, MD

CLINICAL RATIONALE
Right upper lobe mass with ipsilateral mediastinal nodes. Target lesion: 31.9mm ground-glass nodule localized to LLL anteromedial basal (B7+8).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Acquire).

Station 11L: Visualized homogeneous node (21.6x19.9mm). Executed 4 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 2L: Visualized homogeneous node (14.5x12.2mm). Executed 4 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 7: Visualized homogeneous node (21.8x25.3mm). Executed 3 aspiration passes. ROSE yielded: Adequate lymphocytes.
Station 11R: Visualized homogeneous node (15.0x14.3mm). Executed 3 aspiration passes. ROSE yielded: Malignant - small cell carcinoma.
Station 10R: Visualized heterogeneous node (21.4x18.1mm). Executed 4 aspiration passes. ROSE yielded: Adequate lymphocytes, no malignancy.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Ion robotic navigation platform (Intuitive Surgical) was initialized and calibrated. Registration accuracy measured 3.2mm. The articulating catheter was maneuvered to the LLL anteromedial basal (B7+8) target zone.

Radial ultrasound miniprobe was deployed, yielding adjacent visualization of the lesion. Instrument-within-target was verified via fluoroscopy.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 6
- Aspiration needle passes executed: 3  
- Cytology brushings harvested: 2
- Lavage fluid extracted from LLL

ROSE assessment yielded: Suspicious for malignancy

SPECIMEN DISPOSITION
- EBUS aspirates dispatched to: Cytology, cell block, flow cytometry
- Parenchymal samples dispatched to: Surgical pathology, molecular analysis
- Brushings dispatched to: Cytology
- Lavage dispatched to: Microbiology (bacterial, mycobacterial, fungal)

OUTCOME ASSESSMENT
Procedure concluded without adverse events. Hemorrhage: negligible (<10mL). Post-procedure radiograph: unremarkable, pneumothorax excluded.

DISPOSITION
Patient [REDACTED] recovery suite. Discharged to residence following observation period. Outpatient follow-up scheduled for pathology review.

SUMMARY
1. EBUS-guided mediastinal staging successfully executed (5 stations sampled)
2. Robotic navigation to peripheral target successfully accomplished
3. Tissue acquisition achieved via multiple modalities
4. Zero procedural complications documented

Electronically attested,
Maria Santos, MD
Division of Interventional Pulmonology
Memorial Hospital"""

entities_3916235 = [
    # Anatomy & Lesions
    {"label": "ANAT_LUNG_LOC", **get_span(text_3916235, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_3916235, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "31.9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_3916235, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3916235, "LLL anteromedial basal (B7+8)", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "8.0mm", 1)}, # Airway device size
    
    # EBUS Segment
    {"label": "PROC_METHOD", **get_span(text_3916235, "convex-probe ultrasound", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3916235, "22-gauge aspiration needle", 1)},
    
    # Stations
    {"label": "ANAT_LN_STATION", **get_span(text_3916235, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "21.6x19.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3916235, "4", 1)},
    {"label": "OBS_ROSE", **get_span(text_3916235, "Suspicious for malignancy", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_3916235, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "14.5x12.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3916235, "4", 2)},
    {"label": "OBS_ROSE", **get_span(text_3916235, "Suspicious for malignancy", 2)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_3916235, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "21.8x25.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3916235, "3", 1)},
    {"label": "OBS_ROSE", **get_span(text_3916235, "Adequate lymphocytes", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_3916235, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "15.0x14.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3916235, "3", 2)},
    {"label": "OBS_ROSE", **get_span(text_3916235, "Malignant - small cell carcinoma", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_3916235, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "21.4x18.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3916235, "4", 3)},
    {"label": "OBS_ROSE", **get_span(text_3916235, "Adequate lymphocytes, no malignancy", 1)},
    
    # Robotic Segment
    {"label": "PROC_METHOD", **get_span(text_3916235, "Ion robotic navigation platform", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3916235, "3.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3916235, "LLL anteromedial basal (B7+8)", 2)},
    {"label": "PROC_METHOD", **get_span(text_3916235, "Radial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_3916235, "fluoroscopy", 1)},
    
    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_3916235, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3916235, "6", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3916235, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3916235, "3", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3916235, "Cytology brushings", 1)}, 
    {"label": "MEAS_COUNT", **get_span(text_3916235, "2", 1)},
    {"label": "PROC_ACTION", **get_span(text_3916235, "Lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3916235, "LLL", 1)},
    {"label": "OBS_ROSE", **get_span(text_3916235, "Suspicious for malignancy", 3)},
    
    # Summary/Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3916235, "pneumothorax excluded", 1)},
    {"label": "PROC_METHOD", **get_span(text_3916235, "EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_3916235, "Robotic navigation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3916235, "Zero procedural complications", 1)},
]
BATCH_DATA.append({"id": id_3916235, "text": text_3916235, "entities": entities_3916235})


# ==========================================
# Case 2: 74-8829-C_syn_1
# ==========================================
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
    {"label": "PROC_ACTION", **get_span(text_syn_1, "Microwave Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_1, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(text_syn_1, "14mm", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_1, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_1, "6 min", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_1, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_1, "R-EBUS", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_1, "No complications", 1)},
]
BATCH_DATA.append({"id": id_syn_1, "text": text_syn_1, "entities": entities_syn_1})


# ==========================================
# Case 3: 74-8829-C_syn_2
# ==========================================
id_syn_2 = "74-8829-C_syn_2"
text_syn_2 = """OPERATIVE REPORT: Bronchoscopic Microwave Ablation.
CLINICAL SUMMARY: Patient with medically inoperable RUL adenocarcinoma.
PROCEDURE: The target lesion in the RUL anterior segment was localized using electromagnetic navigation and confirmed via radial EBUS (contact view). A Neuwave microwave antenna was deployed. Microwave energy was delivered at 60 Watts for 6 minutes. Post-ablation imaging verified adequate coverage of the lesion. The patient tolerated the procedure well."""

entities_syn_2 = [
    {"label": "PROC_ACTION", **get_span(text_syn_2, "Microwave Ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_2, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_2, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_2, "electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_2, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_2, "Neuwave microwave antenna", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_2, "60 Watts", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_2, "6 minutes", 1)},
]
BATCH_DATA.append({"id": id_syn_2, "text": text_syn_2, "entities": entities_syn_2})


# ==========================================
# Case 4: 74-8829-C_syn_3
# ==========================================
id_syn_3 = "74-8829-C_syn_3"
text_syn_3 = """Service: 31641 (Destruction of tumor).
Method: Microwave Ablation.
Device: Neuwave System.
Support: 31627 (Navigation), 31654 (Radial EBUS).
Narrative: Navigated to RUL nodule. Verified tool-in-lesion. Delivered microwave energy to destroy tumor. Post-procedure check negative for pneumothorax."""

entities_syn_3 = [
    {"label": "PROC_ACTION", **get_span(text_syn_3, "Microwave Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_3, "Neuwave System", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_3, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_3, "nodule", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_3, "negative for pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_syn_3, "text": text_syn_3, "entities": entities_syn_3})


# ==========================================
# Case 5: 74-8829-C_syn_4
# ==========================================
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
    {"label": "MEAS_ENERGY", **get_span(text_syn_4, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_4, "6 mins", 1)},
]
BATCH_DATA.append({"id": id_syn_4, "text": text_syn_4, "entities": entities_syn_4})


# ==========================================
# Case 6: 74-8829-C_syn_5
# ==========================================
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


# ==========================================
# Case 7: 74-8829-C_syn_6
# ==========================================
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


# ==========================================
# Case 8: 74-8829-C_syn_7
# ==========================================
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
    {"label": "PROC_METHOD", **get_span(text_syn_7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_7, "RUL anterior segment", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_7, "Microwave ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_syn_7, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_7, "6min", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_syn_7, "No complications", 1)},
]
BATCH_DATA.append({"id": id_syn_7, "text": text_syn_7, "entities": entities_syn_7})


# ==========================================
# Case 9: 74-8829-C_syn_8
# ==========================================
id_syn_8 = "74-8829-C_syn_8"
text_syn_8 = """[REDACTED] in for ablation of his right upper lobe lung cancer. We used a microwave probe inserted through the bronchoscope. After finding the tumor with navigation and ultrasound, we applied microwave energy for 6 minutes. This heated the tumor enough to destroy it. He is recovering well."""

entities_syn_8 = [
    {"label": "PROC_ACTION", **get_span(text_syn_8, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_8, "right upper lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_8, "microwave probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_8, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_syn_8, "ultrasound", 1)},
    {"label": "MEAS_TIME", **get_span(text_syn_8, "6 minutes", 1)},
]
BATCH_DATA.append({"id": id_syn_8, "text": text_syn_8, "entities": entities_syn_8})


# ==========================================
# Case 10: 74-8829-C_syn_9
# ==========================================
id_syn_9 = "74-8829-C_syn_9"
text_syn_9 = """Procedure: Bronchoscopic tumor destruction.
Modality: Microwave energy.
Action: The RUL neoplasm was targeted. The microwave antenna was positioned. Thermal energy was delivered to ablate the mass. 
Result: Therapeutic destruction of the tumor."""

entities_syn_9 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_syn_9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_9, "neoplasm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_syn_9, "microwave antenna", 1)},
    {"label": "PROC_ACTION", **get_span(text_syn_9, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(text_syn_9, "mass", 1)},
]
BATCH_DATA.append({"id": id_syn_9, "text": text_syn_9, "entities": entities_syn_9})


# ==========================================
# Case 11: 74-8829-C (Main)
# ==========================================
id_main = "74-8829-C"
text_main = """DATE: [REDACTED]
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

entities_main = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_main, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_main, "2.1 cm", 1)},
    {"label": "PROC_ACTION", **get_span(text_main, "Bronchoscopic microwave ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_main, "None", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "RUL", 2)},
    {"label": "PROC_METHOD", **get_span(text_main, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "superDimension", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "R-EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_main, "Microwave probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_main, "Neuwave", 1)},
    {"label": "MEAS_SIZE", **get_span(text_main, "14mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_main, "Ablation", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_main, "60W", 1)},
    {"label": "MEAS_TIME", **get_span(text_main, "6 min", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_main, "no complications", 1)},
]
BATCH_DATA.append({"id": id_main, "text": text_main, "entities": entities_main})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)