import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure you are running from the correct directory structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4082732
# ==========================================
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Michael Rodriguez, MD

CLINICAL RATIONALE
Right upper lobe mass with ipsilateral mediastinal nodes. Target lesion: 28.6mm ground-glass nodule localized to RLL lateral basal (B9).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Olympus BF-UC260F-OL8) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 21-gauge aspiration needle (Standard FNA).

Station 10R: Visualized heterogeneous node (17.1x25.9mm). Executed 2 aspiration passes. ROSE yielded: Atypical cells.
Station 11R: Visualized homogeneous node (8.4x34.2mm). Executed 2 aspiration passes. ROSE yielded: Granuloma.
Station 11L: Visualized homogeneous node (22.2x34.6mm). Executed 4 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.
Station 2R: Visualized heterogeneous node (21.9x28.9mm). Executed 4 aspiration passes. ROSE yielded: Atypical cells.
Station 4L: Visualized homogeneous node (18.5x22.0mm). Executed 4 aspiration passes. ROSE yielded: Granuloma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Ion robotic navigation platform (Intuitive Surgical) was initialized and calibrated. Registration accuracy measured 2.6mm. The articulating catheter was maneuvered to the RLL lateral basal (B9) target zone.

Radial ultrasound miniprobe was deployed, yielding adjacent visualization of the lesion. Instrument-within-target was verified via augmented fluoroscopy.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 5
- Aspiration needle passes executed: 4  
- Cytology brushings harvested: 2
- Lavage fluid extracted from RLL

ROSE assessment yielded: Malignant - adenocarcinoma

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
Michael Rodriguez, MD
Division of Interventional Pulmonology
Memorial Hospital"""

entities_1 = [
    # Clinical Rationale
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.6mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 1)},

    # Sedation
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "airway device", 1)},

    # Segment 1: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC260F-OL8", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal conduit", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "aspiration needle", 1)},
    
    # EBUS Stations
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.1x25.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.4x34.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.2x34.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.9x28.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 2)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.5x22.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 2)},

    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.6mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},

    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 1)}, # 5 specimens
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 4)}, # 4 passes
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # 2 brushings
    {"label": "PROC_ACTION", **get_span(text_1, "Lavage", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    
    # Post-nav ROSE
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 2)},

    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 2)},

    # Outcome
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax excluded", 1)},

    # Summary
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)},
]

BATCH_DATA.append({"id": "4082732", "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)