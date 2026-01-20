import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 3459527
# ==========================================
id_1 = "3459527"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Rachel Goldman, MD

CLINICAL RATIONALE
Peripheral nodule and bilateral hilar adenopathy. Target lesion: 14.0mm ground-glass nodule localized to LUL apicoposterior (B1+2).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Pentax EB-1990i) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (FNB/ProCore).

Station 2L: Visualized homogeneous node (14.8x28.3mm). Executed 3 aspiration passes. ROSE yielded: Atypical cells.
Station 4L: Visualized homogeneous node (24.3x25.6mm). Executed 2 aspiration passes. ROSE yielded: Malignant - squamous cell carcinoma.
Station 10R: Visualized heterogeneous node (12.9x30.7mm). Executed 2 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 10L: Visualized heterogeneous node (18.8x34.6mm). Executed 3 aspiration passes. ROSE yielded: Suspicious for malignancy.
Station 11L: Visualized heterogeneous node (18.7x20.8mm). Executed 2 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Ion robotic navigation platform (Intuitive Surgical) was initialized and calibrated. Registration accuracy measured 1.5mm. The articulating catheter was maneuvered to the LUL apicoposterior (B1+2) target zone.

Radial ultrasound miniprobe was deployed, yielding concentric visualization of the lesion. Instrument-within-target was verified via fluoroscopy.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 7
- Aspiration needle passes executed: 2  
- Cytology brushings harvested: 2
- Lavage fluid extracted from LUL

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
1. EBUS-guided mediastinal staging successfully executed (5 stations sampled)
2. Robotic navigation to peripheral target successfully accomplished
3. Tissue acquisition achieved via multiple modalities
4. Zero procedural complications documented

Electronically attested,
Rachel Goldman, MD
Division of Interventional Pulmonology
Academic Health System"""

entities_1 = [
    # Clinical Rationale
    {"label": "OBS_LESION",         **get_span(text_1, "Peripheral nodule", 1)},
    {"label": "OBS_FINDING",        **get_span(text_1, "bilateral hilar adenopathy", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "14.0mm", 1)},
    {"label": "OBS_LESION",         **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "LUL apicoposterior (B1+2)", 1)},
    
    # Sedation
    {"label": "MEAS_SIZE",          **get_span(text_1, "8.0mm", 1)},

    # Segment 1: EBUS
    {"label": "PROC_METHOD",        **get_span(text_1, "EBUS", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_1, "aspiration needle", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "14.8x28.3mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "3", 1)},
    {"label": "OBS_ROSE",           **get_span(text_1, "Atypical cells", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "24.3x25.6mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "2", 1)},
    {"label": "OBS_ROSE",           **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "12.9x30.7mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "2", 2)}, # Second occurrence of "2" in this block
    {"label": "OBS_ROSE",           **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Station 10L
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "18.8x34.6mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "3", 2)},
    {"label": "OBS_ROSE",           **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Station 11L
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE",          **get_span(text_1, "18.7x20.8mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "2", 3)},
    {"label": "OBS_ROSE",           **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    
    # Segment 2: Robotic
    {"label": "PROC_METHOD",        **get_span(text_1, "Robotic", 1)}, # In "ROBOTIC-ASSISTED"
    {"label": "PROC_METHOD",        **get_span(text_1, "Ion robotic navigation platform", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "LUL apicoposterior (B1+2)", 2)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "fluoroscopy", 1)},
    
    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "7", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_1, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "2", 4)}, # Fourth occurrence of single digit "2" (check context lines)
    {"label": "SPECIMEN",           **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "2", 5)},
    {"label": "SPECIMEN",           **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "LUL", 3)},
    {"label": "OBS_ROSE",           **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    
    # Specimen Disposition
    {"label": "SPECIMEN",           **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "Lavage", 1)},
    
    # Outcome
    {"label": "MEAS_VOL",               **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION",   **get_span(text_1, "pneumothorax excluded", 1)},
    
    # Summary
    {"label": "PROC_METHOD",            **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD",            **get_span(text_1, "Robotic navigation", 1)},
    {"label": "OUTCOME_COMPLICATION",   **get_span(text_1, "Zero procedural complications", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)