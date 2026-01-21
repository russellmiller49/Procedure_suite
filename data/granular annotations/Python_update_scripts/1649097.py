import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from a subdir)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the add_case utility
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure the script is running in the correct repo structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    
    Args:
        text (str): The text to search within.
        term (str): The exact substring to find.
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 1649097
# ==========================================
id_1 = "1649097"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Brian O'Connor, MD

CLINICAL RATIONALE
Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy. Target lesion: 14.5mm ground-glass nodule localized to RUL anterior (B3).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Fujifilm EB-580S) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 19-gauge aspiration needle (FNB/ProCore).

Station 11L: Visualized heterogeneous node (13.3x31.3mm). Executed 4 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 7: Visualized homogeneous node (10.0x26.5mm). Executed 2 aspiration passes. ROSE yielded: Adequate lymphocytes.
Station 2L: Visualized homogeneous node (24.9x12.2mm). Executed 3 aspiration passes. ROSE yielded: Malignant - small cell carcinoma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Monarch robotic navigation platform (Auris Health (J&J)) was initialized and calibrated. Registration accuracy measured 3.2mm. The articulating catheter was maneuvered to the RUL anterior (B3) target zone.

Radial ultrasound miniprobe was deployed, yielding concentric visualization of the lesion. Instrument-within-target was verified via radial ebus.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 7
- Aspiration needle passes executed: 4  
- Cytology brushings harvested: 2
- Lavage fluid extracted from RUL

ROSE assessment yielded: Atypical cells

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
Brian O'Connor, MD
Division of Interventional Pulmonology
Methodist Hospital"""

entities_1 = [
    # Clinical Rationale
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.5mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior (B3)", 1)},
    
    # Sedation Details
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},

    # Segment 1: Linear EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "LINEAR EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fujifilm EB-580S", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Systematic mediastinal survey", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge aspiration needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "heterogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.3x31.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "homogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10.0x26.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "homogeneous node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.9x12.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},

    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic navigation platform", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3.2mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior (B3)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial ebus", 1)},

    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 2)},  # "specimens acquired: 7"
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)}, # Fixed: Changed from 2 to 1 (case sensitive)
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)},  # "executed: 4"
    {"label": "SPECIMEN", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 5)},  # "harvested: 2"
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Procedure concluded without adverse events", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemorrhage: negligible", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax excluded", 1)},

    # Summary
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)