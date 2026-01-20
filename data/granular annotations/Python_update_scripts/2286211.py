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

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2286211
# ==========================================
id_1 = "2286211"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Steven Park, MD

CLINICAL RATIONALE
Combined staging and peripheral nodule diagnosis. Target lesion: 27.5mm ground-glass nodule localized to RLL superior (B6).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Fujifilm EB-580S) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Acquire).

Station 11R: Visualized homogeneous node (22.0x13.6mm). Executed 2 aspiration passes. ROSE yielded: Malignant - small cell carcinoma.
Station 4R: Visualized heterogeneous node (13.7x29.3mm). Executed 4 aspiration passes. ROSE yielded: Atypical cells.
Station 11L: Visualized homogeneous node (18.9x31.0mm). Executed 3 aspiration passes. ROSE yielded: Malignant - small cell carcinoma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Galaxy robotic navigation platform (Noah Medical) was initialized and calibrated. Registration accuracy measured 2.8mm. The articulating catheter was maneuvered to the RLL superior (B6) target zone.

Radial ultrasound miniprobe was deployed, yielding eccentric visualization of the lesion. Instrument-within-target was verified via cbct.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 4
- Aspiration needle passes executed: 3  
- Cytology brushings harvested: 2
- Lavage fluid extracted from RLL

ROSE assessment yielded: Adequate lymphocytes, no malignancy

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
[REDACTED], MD
Division of Interventional Pulmonology
Baptist Medical Center"""

entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "27.5mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fujifilm EB-580S", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "aspiration needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.0x13.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 6)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.7x29.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.9x31.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic navigation platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Noah Medical", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "cbct", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 6)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 10)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemorrhage", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)