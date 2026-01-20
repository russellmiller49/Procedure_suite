import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
# Adjust this logic if the directory structure differs in your environment.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts directory
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure the script is located correctly relative to the 'scripts' folder.")
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
# Note 1: 3900786
# ==========================================
id_1 = "3900786"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Sarah Chen, MD

CLINICAL RATIONALE
Lung nodule evaluation with mediastinal lymphadenopathy workup. Target lesion: 30.2mm ground-glass nodule localized to LUL inferior lingula (B5).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Olympus BF-UC190F) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Acquire).

Station 4R: Visualized heterogeneous node (22.1x22.1mm). Executed 4 aspiration passes. ROSE yielded: Atypical cells.
Station 2R: Visualized heterogeneous node (14.8x16.0mm). Executed 4 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 2L: Visualized homogeneous node (15.4x34.5mm). Executed 2 aspiration passes. ROSE yielded: Granuloma.
Station 10L: Visualized homogeneous node (10.7x16.3mm). Executed 3 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Monarch robotic navigation platform (Auris Health (J&J)) was initialized and calibrated. Registration accuracy measured 2.2mm. The articulating catheter was maneuvered to the LUL inferior lingula (B5) target zone.

Radial ultrasound miniprobe was deployed, yielding eccentric visualization of the lesion. Instrument-within-target was verified via cbct.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 8
- Aspiration needle passes executed: 4  
- Cytology brushings harvested: 2
- Lavage fluid extracted from LUL

ROSE assessment yielded: Malignant - small cell carcinoma

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
Sarah Chen, MD
Division of Interventional Pulmonology
Academic Health System"""

entities_1 = [
    # Clinical Rationale
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.2mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},
    
    # Sedation/Airway
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    
    # Segment 1: EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "LINEAR EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.1x22.1mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    
    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "heterogeneous node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8x16.0mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.4x34.5mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    
    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10.7x16.3mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    
    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    
    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    # Correction: 'Aspiration needle' (Capitalized) appears only once in the text (in the list under TISSUE ACQUISITION).
    # The previous occurrence was 'aspiration needle' (lowercase). Since get_span is case-sensitive, we must use occurrence=1.
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Aspiration needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 3)},
    
    # ROSE & Disposition
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 1)},
    
    # Outcome
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Zero procedural complications", 1)},
    
    # Summary
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)