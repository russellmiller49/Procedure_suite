import sys
from pathlib import Path

# Set up the repository root (assumes this script is in a subdirectory of the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent
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
# Note 1: 1763427
# ==========================================
id_1 = "1763427"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Maria Santos, MD

CLINICAL RATIONALE
Combined staging and peripheral nodule diagnosis. Target lesion: 16.3mm part-solid nodule localized to RUL anterior (B3).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Olympus BF-UC180F) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 21-gauge aspiration needle (Standard FNA).

Station 2L: Visualized homogeneous node (19.0x23.5mm). Executed 2 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.
Station 10L: Visualized heterogeneous node (22.7x13.9mm). Executed 4 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.
Station 7: Visualized heterogeneous node (16.8x24.0mm). Executed 4 aspiration passes. ROSE yielded: Adequate lymphocytes, no malignancy.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Monarch robotic navigation platform (Auris Health (J&J)) was initialized and calibrated. Registration accuracy measured 3.0mm. The articulating catheter was maneuvered to the RUL anterior (B3) target zone.

Radial ultrasound miniprobe was deployed, yielding eccentric visualization of the lesion. Instrument-within-target was verified via augmented fluoroscopy.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 6
- Aspiration needle passes executed: 2  
- Cytology brushings harvested: 2
- Lavage fluid extracted from RUL

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
1. EBUS-guided mediastinal staging successfully executed (3 stations sampled)
2. Robotic navigation to peripheral target successfully accomplished
3. Tissue acquisition achieved via multiple modalities
4. Zero procedural complications documented

Electronically attested,
Maria Santos, MD
Division of Interventional Pulmonology
Memorial Hospital"""

entities_1 = [
    # Clinical Rationale
    {"label": "MEAS_SIZE", **get_span(text_1, "16.3mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    
    # Sedation Details
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},

    # Segment 1: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.0x23.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},

    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.7x13.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 2)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.8x24.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},

    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic navigation platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},

    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 1)}, # forceps count
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)}, # Corrected occurrence: Only 1 capitalized instance exists
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # needle passes (note: check occurrence in full text carefully)
                                                         # occ 1: Station 2L "2 aspiration passes"
                                                         # occ 2: Station 10L "...22.7..." no "2"
                                                         # occ 3: Tissue Acquisition "2"
    {"label": "SPECIMEN", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 4)}, # brushings count
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)}, # "extracted from RUL"
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 3)},

    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 1)},

    # Outcome
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax excluded", 1)},

    # Summary
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Zero procedural complications", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)