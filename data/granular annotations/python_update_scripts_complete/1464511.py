import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 1464511
# ==========================================
text_1464511 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED] Baker
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Brian O'Connor, MD

CLINICAL RATIONALE
Mediastinal staging for biopsy-proven lung adenocarcinoma. Target lesion: 22.6mm solid nodule localized to RUL apical (B1).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Olympus BF-UC190F) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Standard FNA).

Station 11R: Visualized homogeneous node (24.9x17.4mm). Executed 3 aspiration passes. ROSE yielded: Malignant - adenocarcinoma.
Station 2L: Visualized heterogeneous node (14.7x16.9mm). Executed 2 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 4R: Visualized heterogeneous node (13.0x24.5mm). Executed 3 aspiration passes. ROSE yielded: Malignant - small cell carcinoma.
Station 11L: Visualized heterogeneous node (19.1x15.5mm). Executed 3 aspiration passes. ROSE yielded: Suspicious for malignancy.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Galaxy robotic navigation platform (Noah Medical) was initialized and calibrated. Registration accuracy measured 1.8mm. The articulating catheter was maneuvered to the RUL apical (B1) target zone.

Radial ultrasound miniprobe was deployed, yielding concentric visualization of the lesion. Instrument-within-target was verified via cbct.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 4
- Aspiration needle passes executed: 4  
- Cytology brushings harvested: 2
- Lavage fluid extracted from RUL

ROSE assessment yielded: Suspicious for malignancy

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
Brian O'Connor, MD
Division of Interventional Pulmonology
Veterans Affairs Medical Center"""

entities_1464511 = [
    # Rationale
    {"label": "OBS_LESION", **get_span(text_1464511, "solid nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1464511, "22.6mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1464511, "RUL apical (B1)", 1)},
    
    # Sedation
    {"label": "MEAS_SIZE", **get_span(text_1464511, "8.0mm", 1)},
    
    # Segment 1: EBUS
    {"label": "PROC_METHOD", **get_span(text_1464511, "EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1464511, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1464511, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1464511, "aspiration needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_1464511, "FNA", 1)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1464511, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1464511, "24.9x17.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1464511, "3", 1)},
    {"label": "OBS_ROSE", **get_span(text_1464511, "Malignant - adenocarcinoma", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1464511, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1464511, "14.7x16.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1464511, "2", 1)},
    {"label": "OBS_ROSE", **get_span(text_1464511, "Malignant - NSCLC NOS", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1464511, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1464511, "13.0x24.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1464511, "3", 2)}, # 2nd occurrence of "3" in this block
    {"label": "OBS_ROSE", **get_span(text_1464511, "Malignant - small cell carcinoma", 1)},
    
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1464511, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1464511, "19.1x15.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1464511, "3", 3)}, # 3rd occurrence
    {"label": "OBS_ROSE", **get_span(text_1464511, "Suspicious for malignancy", 1)},
    
    # Segment 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1464511, "robotic navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1464511, "1.8mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1464511, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1464511, "RUL apical (B1)", 2)},
    
    # Nav/Tools
    {"label": "DEV_INSTRUMENT", **get_span(text_1464511, "Radial ultrasound miniprobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1464511, "cbct", 1)},
    
    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1464511, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1464511, "4", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1464511, "Aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1464511, "4", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1464511, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1464511, "2", 2)},
    {"label": "SPECIMEN", **get_span(text_1464511, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1464511, "RUL", 3)},
    
    # ROSE
    {"label": "OBS_ROSE", **get_span(text_1464511, "Suspicious for malignancy", 2)},
    
    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_1464511, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1464511, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1464511, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1464511, "Lavage", 1)},
    
    # Outcome
    {"label": "MEAS_VOL", **get_span(text_1464511, "<10mL", 1)},
    
    # Summary
    {"label": "PROC_METHOD", **get_span(text_1464511, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1464511, "Robotic navigation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1464511, "Zero procedural complications", 1)},
]

BATCH_DATA.append({"id": "1464511", "text": text_1464511, "entities": entities_1464511})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)