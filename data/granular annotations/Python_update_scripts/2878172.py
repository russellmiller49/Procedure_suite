import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from a subdirectory)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly without package structure
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Case-sensitive.
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
# Note 1: 2878172
# ==========================================
id_1 = "2878172"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: David Kim, MD

CLINICAL RATIONALE
PET-avid lung mass and mediastinal lymphadenopathy. Target lesion: 23.3mm solid nodule localized to RLL medial basal (B7).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Fujifilm EB-580S) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Standard FNA).

Station 2R: Visualized heterogeneous node (12.0x33.3mm). Executed 4 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 10R: Visualized heterogeneous node (12.9x26.6mm). Executed 3 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 2L: Visualized heterogeneous node (13.9x22.9mm). Executed 2 aspiration passes. ROSE yielded: Granuloma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Galaxy robotic navigation platform (Noah Medical) was initialized and calibrated. Registration accuracy measured 1.9mm. The articulating catheter was maneuvered to the RLL medial basal (B7) target zone.

Radial ultrasound miniprobe was deployed, yielding adjacent visualization of the lesion. Instrument-within-target was verified via radial ebus.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 5
- Aspiration needle passes executed: 4  
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
David Kim, MD
Division of Interventional Pulmonology
Regional Medical Center"""

entities_1 = [
    # Clinical Rationale
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.3mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL medial basal (B7)", 1)},

    # Sedation/Airway (8.0mm likely ETT size, strictly MEAS_SIZE)
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},

    # Segment 1: EBUS
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "aspiration needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},

    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.0x33.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)}, # In "4 aspiration passes"
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.9x26.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)}, # In "3 aspiration passes"
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.9x22.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, # Occ 3: "Executed 2" (Occ 1 in 2R, Occ 2 in 2L)
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},

    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "robotic navigation", 1)}, # lowercase in "Galaxy robotic..."
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL medial basal (B7)", 2)},
    
    # Tools/Navigation
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    
    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 1)},
    
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Aspiration needle", 1)}, # Capitalized "Aspiration"
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)}, # Occ 2: "executed: 4"
    
    {"label": "SPECIMEN", **get_span(text_1, "Cytology brushings", 1)}, # Mapped to Specimen or Instrument? "harvested" -> Specimen
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 4)}, # Occ 4: "harvested: 2"
    
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)}, # "extracted from RLL"
    
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},

    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 1)}, # "Lavage dispatched"

    # Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemorrhage: negligible", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax excluded", 1)},
    
    # Summary
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)} # Title case
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)