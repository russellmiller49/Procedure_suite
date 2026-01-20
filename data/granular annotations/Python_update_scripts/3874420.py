import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 3874420
# ==========================================
id_1 = "3874420"
text_1 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

Patient: [REDACTED]
Medical Record: [REDACTED]
Service Date: [REDACTED]
Operator: Brian O'Connor, MD

CLINICAL RATIONALE
Lung nodule evaluation with mediastinal lymphadenopathy workup. Target lesion: 31.2mm solid nodule localized to LUL inferior lingula (B5).

SEDATION DETAILS
General endotracheal sedation administered. 8.0mm airway device deployed orally.

OPERATIVE NARRATIVE

SEGMENT 1: LINEAR EBUS MEDIASTINAL ASSESSMENT

The convex-probe ultrasound bronchoscope (Olympus BF-UC180F) was advanced through the endotracheal conduit. Systematic mediastinal survey was executed. Lymph nodes were visualized at multiple stations and sampled utilizing 22-gauge aspiration needle (Acquire).

Station 10R: Visualized homogeneous node (16.6x13.8mm). Executed 4 aspiration passes. ROSE yielded: Malignant - NSCLC NOS.
Station 4R: Visualized heterogeneous node (13.5x29.3mm). Executed 2 aspiration passes. ROSE yielded: Malignant - small cell carcinoma.
Station 2L: Visualized homogeneous node (11.0x19.3mm). Executed 4 aspiration passes. ROSE yielded: Adequate lymphocytes, no malignancy.
Station 2R: Visualized heterogeneous node (21.8x17.2mm). Executed 4 aspiration passes. ROSE yielded: Adequate lymphocytes, no malignancy.
Station 4L: Visualized heterogeneous node (22.9x29.8mm). Executed 3 aspiration passes. ROSE yielded: Atypical cells.

SEGMENT 2: ROBOTIC-ASSISTED PERIPHERAL NAVIGATION

The Monarch robotic navigation platform (Auris Health (J&J)) was initialized and calibrated. Registration accuracy measured 2.2mm. The articulating catheter was maneuvered to the LUL inferior lingula (B5) target zone.

Radial ultrasound miniprobe was deployed, yielding concentric visualization of the lesion. Instrument-within-target was verified via cbct.

TISSUE ACQUISITION:
- Grasping forceps specimens acquired: 6
- Aspiration needle passes executed: 2  
- Cytology brushings harvested: 2
- Lavage fluid extracted from LUL

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
1. EBUS-guided mediastinal staging successfully executed (5 stations sampled)
2. Robotic navigation to peripheral target successfully accomplished
3. Tissue acquisition achieved via multiple modalities
4. Zero procedural complications documented

Electronically attested,
Brian O'Connor, MD
Division of Interventional Pulmonology
Cleveland Clinic"""

entities_1 = [
    # Clinical Rationale
    {"label": "MEAS_SIZE", **get_span(text_1, "31.2mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},
    
    # Sedation/Devices
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "airway device", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "convex-probe ultrasound bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC180F", 1)},
    
    # EBUS Segment
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "aspiration needle", 1)}, # Lowercase in Seg 1
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.6x13.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 2)}, # "Executed 4..." (Occ 2 of 4)
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.5x29.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 4)}, # "Executed 2..." (Occ 4 of 2)
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.0x19.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 4)}, # "Executed 4..." (Occ 4 of 4)
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    
    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.8x17.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 5)}, # "Executed 4..." (Occ 5 of 4)
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 2)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.9x29.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 5)}, # "Executed 3..." (Occ 5 of 3)
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    
    # Segment 2 - Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic navigation platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "articulating catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial ultrasound miniprobe", 1)},
    
    # Tissue Acquisition
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Grasping forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 3)}, # "acquired: 6" (Occ 3 of 6)
    {"label": "DEV_NEEDLE", **get_span(text_1, "Aspiration needle", 1)}, # Capitalized in Seg 2
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 14)}, # "passes executed: 2" (Occ 14 of 2)
    {"label": "SPECIMEN", **get_span(text_1, "Cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 15)}, # "harvested: 2" (Occ 15 of 2)
    {"label": "SPECIMEN", **get_span(text_1, "Lavage fluid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)}, # In "Lavage fluid extracted from LUL"
    
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},
    
    # Specimen Disposition
    {"label": "SPECIMEN", **get_span(text_1, "EBUS aspirates", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Parenchymal samples", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Lavage", 1)}, # In "Lavage dispatched to..."
    
    # Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemorrhage", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 1)},
    
    # Summary
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Tissue acquisition", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)