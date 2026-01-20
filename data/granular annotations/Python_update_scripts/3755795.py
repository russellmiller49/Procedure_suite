import sys
from pathlib import Path

# Adjust path to find the utility script
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Case: 3755795
# ==========================================
id_3755795 = "3755795"
text_3755795 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Steven Park, MD

CLINICAL RATIONALE
PET-avid lung mass and mediastinal lymphadenopathy. Target lesion: 30.9mm ground-glass nodule localized to RUL anterior (B3).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (FNB/ProCore).

Station 4L: Visualized homogeneous node (18.3x28.3mm). Executed 2 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 10R: Visualized heterogeneous node (14.8x23.9mm). Executed 4 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 4R: Visualized homogeneous node (20.9x20.6mm). Executed 4 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.
Station 7: Visualized homogeneous node (24.0x28.4mm). Executed 2 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Monarch robotic navigation platform (Auris Health (J&J)) was initialized and calibrated. Registration accuracy measured 2.0mm. The articulating catheter was maneuvered to the RUL anterior (B3) target zone.

Radial ultrasound miniprobe was deployed, yielding adjacent visualization of the lesion. Instrument-within-target was verified via fluoroscopy.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 6
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
1. EBUS-guided mediastinal staging successfully executed (4 stations sampled)
2. Robotic navigation to peripheral target successfully accomplished
3. Tissue acquisition achieved via multiple modalities
4. Zero procedural complications documented

Electronically attested,
[REDACTED], MD
Division of Interventional Pulmonology
Regional Medical Center"""

entities_3755795 = [
    # Clinical Rationale
    {"label": "OBS_LESION", **get_span(text_3755795, "lung mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3755795, "30.9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_3755795, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3755795, "RUL anterior (B3)", 1)},

    # Sedation
    {"label": "MEAS_SIZE", **get_span(text_3755795, "8.0mm", 1)},

    # Segment 1: EBUS
    {"label": "DEV_INSTRUMENT", **get_span(text_3755795, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3755795, "22-gauge aspiration needle", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_3755795, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3755795, "18.3x28.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3755795, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_3755795, "Malignant - NSCLC NOS", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_3755795, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3755795, "14.8x23.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3755795, "4 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_3755795, "Suspicious for malignancy", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_3755795, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3755795, "20.9x20.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3755795, "4 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_3755795, "Malignant - adenocarcinoma", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_3755795, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3755795, "24.0x28.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3755795, "2 aspiration passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_3755795, "Malignant - adenocarcinoma", 2)},

    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_3755795, "ROBOTIC-ASSISTED", 1)},
    {"label": "PROC_METHOD", **get_span(text_3755795, "robotic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3755795, "RUL anterior (B3)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3755795, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_3755795, "fluoroscopy", 1)},

    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_3755795, "Grasping forceps", 1)},
    # Fixed: Occurrence changed from 2 to 1 because "Aspiration needle" (Title Case) appears only once. 
    # The lowercase "aspiration needle" in Segment 1 is a separate string.
    {"label": "DEV_NEEDLE", **get_span(text_3755795, "Aspiration needle", 1)}, 
    {"label": "SPECIMEN", **get_span(text_3755795, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3755795, "RUL", 3)}, 
    {"label": "OBS_ROSE", **get_span(text_3755795, "Granuloma", 1)},

    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_3755795, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_3755795, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_3755795, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_3755795, "Lavage", 2)}, 

    # Outcome
    {"label": "MEAS_VOL", **get_span(text_3755795, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3755795, "pneumothorax excluded", 1)},

    # Summary
    {"label": "PROC_METHOD", **get_span(text_3755795, "EBUS-guided", 1)},
    # Fixed: Occurrence changed from 2 to 1. "Robotic navigation" (Title Case) appears only once in the Summary.
    # The earlier instance is "robotic navigation" (lowercase) or "ROBOTIC-ASSISTED" (all caps).
    {"label": "PROC_METHOD", **get_span(text_3755795, "Robotic navigation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3755795, "Zero procedural complications", 1)},
]
BATCH_DATA.append({"id": id_3755795, "text": text_3755795, "entities": entities_3755795})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)