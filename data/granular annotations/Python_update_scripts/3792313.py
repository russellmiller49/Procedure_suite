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
# 2. Helper Function
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
# Case 1: 3792313
# ==========================================
id_1 = "3792313"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED] Baker
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Robert Patel, MD

CLINICAL RATIONALE
Peripheral nodule and bilateral hilar adenopathy. Target lesion: 21.6mm ground-glass nodule localized to RUL anterior (B3).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Fujifilm EB-580S) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Standard FNA).

Station 10L: Visualized heterogeneous node (13.0x14.3mm). Executed 3 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 4L: Visualized homogeneous node (15.7x23.7mm). Executed 2 aspiration passes. ROSE yielded: Adequate lymphocytes.
Station 11L: Visualized heterogeneous node (19.4x27.5mm). Executed 2 aspiration passes. ROSE yielded: Malignant - small cell carcinoma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Ion robotic navigation platform (Intuitive Surgical) was initialized and calibrated. Registration accuracy measured 1.8mm. The articulating catheter was maneuvered to the RUL anterior (B3) target zone.

Radial ultrasound miniprobe was deployed, yielding eccentric visualization of the lesion. Instrument-within-target was verified via cbct.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 8
- Aspiration needle passes executed: 4  
- Cytology brushings harvested: 2
- Lavage fluid extracted from RUL

ROSE assessment yielded: Granuloma

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
1. EBUS-guided mediastinal staging successfully executed (3 stations sampled)
2. Robotic navigation to peripheral target successfully accomplished
3. Tissue acquisition achieved via multiple modalities
4. Zero procedural complications documented

Electronically attested,
Robert Patel, MD
Division of Interventional Pulmonology
Presbyterian Hospital"""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Peripheral nodule", 1)},
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "adenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.6mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "ground-glass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.0x14.3mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.7x23.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4x27.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic navigation platform", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8", 4)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 4)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 9)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemorrhage", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax excluded", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided mediastinal staging", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 stations", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Zero procedural complications", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)