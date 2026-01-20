import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from a subdir)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts module
# Ensure your environment has the 'scripts' package available in python path
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly without package context, just to prevent immediate crash if testing
    print("Warning: Could not import 'add_case' from 'scripts.add_training_case'.")
    def add_case(id, text, entities, root):
        print(f"Would add case: {id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact string to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            return None  # Occurrence not found
            
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note: 4818600
# ==========================================
id_1 = "4818600"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Amanda Foster, MD

CLINICAL RATIONALE
Lung nodule evaluation with mediastinal lymphadenopathy workup. Target lesion: 27.1mm solid nodule localized to RLL superior (B6).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Olympus BF-UC190F) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (FNB/ProCore).

Station 4L: Visualized heterogeneous node (9.1x13.1mm). Executed 3 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 2R: Visualized heterogeneous node (14.9x15.8mm). Executed 3 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 2L: Visualized homogeneous node (13.2x25.8mm). Executed 2 aspiration passes. ROSE yielded: Adequate lymphocytes, no malignancy.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Ion robotic navigation platform (Intuitive Surgical) was initialized and calibrated. Registration accuracy measured 1.8mm. The articulating catheter was maneuvered to the RLL superior (B6) target zone.

Radial ultrasound miniprobe was deployed, yielding adjacent visualization of the lesion. Instrument-within-target was verified via augmented fluoroscopy.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 5
- Aspiration needle passes executed: 2  
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
Amanda Foster, MD
Division of Interventional Pulmonology
Baptist Medical Center"""

entities_1 = [
    # Rationale
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.1mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)}, # "solid nodule"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 1)},
    
    # Sedation
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    
    # Segment 1: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "aspiration needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "9.1x13.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)}, # passes
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.9x15.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # passes
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.2x25.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 1)}, # passes
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    
    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC-ASSISTED", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion robotic navigation platform", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior (B6)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    
    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},
    
    # Disposition
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 1)},
    
    # Outcome
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
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