import sys
from pathlib import Path

# Set up the repository root (assumes this script is run from inside the repo)
# Adjust if necessary based on your actual directory structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure the script is located correctly relative to the repository root.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2777264
# ==========================================
id_1 = "2777264"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Lisa Thompson, MD

CLINICAL RATIONALE
Lung nodule evaluation with mediastinal lymphadenopathy workup. Target lesion: 23.3mm solid nodule localized to RLL posterior basal (B10).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 21-gauge aspiration needle (Standard FNA).

Station 10R: Visualized homogeneous node (11.9x22.1mm). Executed 3 aspiration passes. ROSE yielded: Malignant - squamous cell carcinoma.
Station 4R: Visualized homogeneous node (21.4x27.6mm). Executed 2 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 7: Visualized heterogeneous node (16.1x28.6mm). Executed 4 aspiration passes. ROSE yielded: Granuloma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Galaxy robotic navigation platform (Noah Medical) was initialized and calibrated. Registration accuracy measured 2.4mm. The articulating catheter was maneuvered to the RLL posterior basal (B10) target zone.

Radial ultrasound miniprobe was deployed, yielding concentric visualization of the lesion. Instrument-within-target was verified via cbct.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 6
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
Lisa Thompson, MD
Division of Interventional Pulmonology
Community Hospital"""

entities_1 = [
    # Clinical Rationale
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.3mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL posterior basal (B10)", 1)},

    # Sedation
    {"label": "ANAT_AIRWAY", **get_span(text_1, "endotracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "airway device", 1)},

    # Segment 1: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "LINEAR EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "endotracheal", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "aspiration needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.9x22.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.4x27.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.1x28.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "aspiration", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},

    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy robotic navigation platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Noah Medical", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.4mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL posterior basal (B10)", 2)},

    # Miniprobe
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)},

    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "specimens", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 1)},
    
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)},

    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushings", 1)}, 
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 2)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Lavage", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},

    # ROSE 2
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},

    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_1, "aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 2)},

    # Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemorrhage", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 1)}, 

    # Summary
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Tissue acquisition", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "complications", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)