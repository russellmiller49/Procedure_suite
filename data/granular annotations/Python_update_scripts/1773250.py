import sys
from pathlib import Path

# Add the repository root to sys.path to import the utility
# Assuming this script is run from a subdirectory or needs to resolve root dynamically
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1773250
# ==========================================
id_1773250 = "1773250"
text_1773250 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED] Baker
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Andrew Nakamura, MD

CLINICAL RATIONALE
Combined staging and peripheral nodule diagnosis. Target lesion: 16.3mm ground-glass nodule localized to RLL superior (B6).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Olympus BF-UC190F) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Standard FNA).

Station 11L: Visualized heterogeneous node (14.4x23.4mm). Executed 4 aspiration passes. ROSE yielded: Granuloma.
Station 4L: Visualized homogeneous node (21.7x20.3mm). Executed 3 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 10L: Visualized homogeneous node (19.2x34.4mm). Executed 2 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Galaxy robotic navigation platform (Noah Medical) was initialized and calibrated. Registration accuracy measured 3.4mm. The articulating catheter was maneuvered to the RLL superior (B6) target zone.

Radial ultrasound miniprobe was deployed, yielding adjacent visualization of the lesion. Instrument-within-target was verified via radial ebus.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 6
- Aspiration needle passes executed: 4  
- Cytology brushings harvested: 2
- Lavage fluid extracted from RLL

ROSE assessment yielded: Malignant - squamous cell carcinoma

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
Andrew Nakamura, MD
Division of Interventional Pulmonology
Community Hospital"""

entities_1773250 = [
    # Clinical Rationale
    {"label": "MEAS_SIZE", **get_span(text_1773250, "16.3mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1773250, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1773250, "RLL superior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1773250, "B6", 1)},

    # Sedation
    {"label": "MEAS_SIZE", **get_span(text_1773250, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1773250, "airway device", 1)},

    # Segment 1: EBUS
    {"label": "PROC_METHOD", **get_span(text_1773250, "LINEAR EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1773250, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1773250, "Olympus BF-UC190F", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1773250, "Lymph nodes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1773250, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1773250, "aspiration needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_1773250, "Standard FNA", 1)},

    # Stations
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1773250, "Station 11L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1773250, "heterogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1773250, "14.4x23.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1773250, "4", 1)},
    {"label": "PROC_ACTION", **get_span(text_1773250, "aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1773250, "Granuloma", 1)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1773250, "Station 4L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1773250, "homogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1773250, "21.7x20.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1773250, "3", 1)},
    {"label": "PROC_ACTION", **get_span(text_1773250, "aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1773250, "Malignant - NSCLC NOS", 1)},

    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1773250, "Station 10L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1773250, "homogeneous node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1773250, "19.2x34.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1773250, "2", 1)},
    {"label": "PROC_ACTION", **get_span(text_1773250, "aspiration passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1773250, "Malignant - adenocarcinoma", 1)},

    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1773250, "ROBOTIC-ASSISTED", 1)},
    # "robotic navigation" inside "Galaxy robotic navigation platform"
    {"label": "PROC_METHOD", **get_span(text_1773250, "robotic navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1773250, "3.4mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1773250, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1773250, "RLL superior", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1773250, "B6", 2)},

    {"label": "DEV_INSTRUMENT", **get_span(text_1773250, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1773250, "radial ebus", 1)},

    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1773250, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1773250, "6", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1773250, "Aspiration needle", 1)},
    # "4" appears in "Aspiration needle passes executed: 4" (This is 2nd occurrence of "4")
    {"label": "MEAS_COUNT", **get_span(text_1773250, "4", 2)},
    # "Cytology brushings" - labeling as SPECIMEN as they are "harvested"
    {"label": "SPECIMEN", **get_span(text_1773250, "Cytology brushings", 1)},
    # "2" appears in "Cytology brushings harvested: 2" (This is 2nd occurrence of "2")
    {"label": "MEAS_COUNT", **get_span(text_1773250, "2", 2)},
    {"label": "SPECIMEN", **get_span(text_1773250, "Lavage fluid", 1)},
    # RLL alone: 3rd occurrence of "RLL" substring (1st in RLL sup Rationale, 2nd in RLL sup Seg2, 3rd here)
    {"label": "ANAT_LUNG_LOC", **get_span(text_1773250, "RLL", 3)},
    
    {"label": "OBS_ROSE", **get_span(text_1773250, "Malignant - squamous cell carcinoma", 1)},

    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_1773250, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1773250, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1773250, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1773250, "Lavage", 1)},

    # Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1773250, "Hemorrhage", 1)},
    {"label": "MEAS_VOL", **get_span(text_1773250, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1773250, "pneumothorax excluded", 1)},

    # Summary
    {"label": "PROC_METHOD", **get_span(text_1773250, "EBUS-guided", 1)},
    # "3" appears in "(3 stations sampled)". This is the 2nd occurrence of "3".
    {"label": "MEAS_COUNT", **get_span(text_1773250, "3", 2)},
    {"label": "PROC_METHOD", **get_span(text_1773250, "Robotic navigation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1773250, "Zero procedural complications", 1)},
]

BATCH_DATA.append({"id": id_1773250, "text": text_1773250, "entities": entities_1773250})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)