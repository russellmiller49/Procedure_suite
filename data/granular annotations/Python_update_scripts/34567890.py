import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
# Expected location: <repo>/data/granular annotations/Python_update_scripts/<id>.py
# parents[3] => <repo>
REPO_ROOT = Path(__file__).resolve().parents[3]

# Import the utility function to add cases
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback to sys.path hack if not running as module
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to find.
        occurrence (int): Which occurrence to return (1-based).
        
    Returns:
        dict: A dictionary with 'start' and 'end' keys.
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
# Note 1: 34567890_syn_1
# ==========================================
text_1 = """Procedure: Bronchoscopic Thermal Vapor Ablation (BTVA).
Target: RUL (RB3, RB1).
Action: InterVapor catheter placed. 14 calories total delivered.
Result: Good vapor delivery. No complications.
Plan: ICU admission, prophylactic antibiotics."""

entities_1 = [
    {"label": "PROC_ACTION",    **get_span(text_1, "Bronchoscopic Thermal Vapor Ablation", 1)}, # [cite: 10]
    {"label": "PROC_ACTION",    **get_span(text_1, "BTVA", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "RUL", 1)}, # [cite: 2]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "RB3", 1)}, # [cite: 2]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_1, "RB1", 1)}, # [cite: 2]
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "InterVapor catheter", 1)}, # [cite: 7]
    {"label": "MEAS_ENERGY",    **get_span(text_1, "14 calories", 1)}, # [cite: 24]
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)}, # [cite: 16]
]
BATCH_DATA.append({"id": "34567890_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 34567890_syn_2
# ==========================================
text_2 = """OPERATIVE NARRATIVE: The patient with severe emphysema underwent bronchoscopic thermal vapor ablation. The Right Upper Lobe was selected based on collateral ventilation status. The InterVapor catheter was navigated to the anterior (RB3) and apical (RB1) segments. A total of 14 calories of thermal energy were delivered (8 cal to RB3, 6 cal to RB1). Fluoroscopy confirmed accurate catheter placement and vapor containment. The patient tolerated the procedure without adverse events."""

entities_2 = [
    {"label": "PROC_ACTION",    **get_span(text_2, "bronchoscopic thermal vapor ablation", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "Right Upper Lobe", 1)}, # [cite: 2]
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "InterVapor catheter", 1)}, # [cite: 7]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "RB3", 1)}, # [cite: 2]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "RB1", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_2, "14 calories", 1)}, # [cite: 24]
    {"label": "MEAS_ENERGY",    **get_span(text_2, "8 cal", 1)}, # [cite: 24]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "RB3", 2)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_2, "6 cal", 1)}, # [cite: 24]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_2, "RB1", 2)}, # [cite: 2]
    {"label": "PROC_METHOD",    **get_span(text_2, "Fluoroscopy", 1)}, # [cite: 10]
]
BATCH_DATA.append({"id": "34567890_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 34567890_syn_3
# ==========================================
text_3 = """Code: 31641 (Destruction of tumor/tissue, bronchoscopic).
Technique: Thermal vapor ablation of emphysematous tissue.
Target: Right Upper Lobe.
Dosage: 14 Calories total.
Note: This is a distinct modality from valve placement."""

entities_3 = [
    {"label": "PROC_ACTION",    **get_span(text_3, "Thermal vapor ablation", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_3, "Right Upper Lobe", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_3, "14 Calories", 1)}, # [cite: 24]
    {"label": "DEV_VALVE",      **get_span(text_3, "valve", 1)}, # [cite: 4]
]
BATCH_DATA.append({"id": "34567890_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 34567890_syn_4
# ==========================================
text_4 = """Procedure: Vapor Ablation (InterVapor)
Attending: Dr. Chen
Steps:
1. Navigated to RUL.
2. Treated RB3 with 8 calories.
3. Treated RB1 with 6 calories.
4. Verified with fluoro.
5. No bleeding.
Plan: Watch for inflammatory response/fever."""

entities_4 = [
    {"label": "PROC_ACTION",    **get_span(text_4, "Vapor Ablation", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "RUL", 1)}, # [cite: 2]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "RB3", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_4, "8 calories", 1)}, # [cite: 24]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_4, "RB1", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_4, "6 calories", 1)}, # [cite: 24]
    {"label": "PROC_METHOD",    **get_span(text_4, "fluoro", 1)}, # [cite: 10]
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No bleeding", 1)}, # [cite: 16]
]
BATCH_DATA.append({"id": "34567890_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 34567890_syn_5
# ==========================================
text_5 = """George Martinez here for the vapor treatment for his COPD. We did the RUL today. Used the steam catheter put 8 calories in the front segment and 6 in the top one. Vapor went in good seen on xray. Patient is stable. He needs antibiotics and prednisone for the inflammation coming up."""

entities_5 = [
    {"label": "PROC_ACTION",    **get_span(text_5, "vapor treatment", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_5, "RUL", 1)}, # [cite: 2]
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "steam catheter", 1)}, # [cite: 7]
    {"label": "MEAS_ENERGY",    **get_span(text_5, "8 calories", 1)}, # [cite: 24]
    {"label": "MEDICATION",     **get_span(text_5, "prednisone", 1)}, # [cite: 20]
]
BATCH_DATA.append({"id": "34567890_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 34567890_syn_6
# ==========================================
text_6 = """Bronchoscopic thermal vapor ablation. The right upper lobe was targeted for lung volume reduction. The vapor catheter was positioned in the RUL anterior and apical segments. Thermal energy was delivered as calculated. Fluoroscopy confirmed appropriate vapor delivery. The procedure was uncomplicated."""

entities_6 = [
    {"label": "PROC_ACTION",    **get_span(text_6, "Bronchoscopic thermal vapor ablation", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_6, "right upper lobe", 1)}, # [cite: 2]
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "vapor catheter", 1)}, # [cite: 7]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_6, "RUL", 1)}, # [cite: 2]
    {"label": "PROC_METHOD",    **get_span(text_6, "Fluoroscopy", 1)}, # [cite: 10]
]
BATCH_DATA.append({"id": "34567890_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 34567890_syn_7
# ==========================================
text_7 = """[Indication]
Severe Emphysema, RUL target (CV+).
[Anesthesia]
MAC/LMA.
[Description]
BTVA to RUL. RB3: 8 cal. RB1: 6 cal. Vapor delivery confirmed.
[Plan]
ICU, Prednisone, Antibiotics."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "RUL", 1)}, # [cite: 2]
    {"label": "PROC_ACTION",    **get_span(text_7, "BTVA", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "RUL", 2)}, # [cite: 2]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "RB3", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_7, "8 cal", 1)}, # [cite: 24]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_7, "RB1", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_7, "6 cal", 1)}, # [cite: 24]
    {"label": "MEDICATION",     **get_span(text_7, "Prednisone", 1)}, # [cite: 20]
]
BATCH_DATA.append({"id": "34567890_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 34567890_syn_8
# ==========================================
text_8 = """[REDACTED] a steam treatment for his emphysema today. Since his lung anatomy wasn't right for valves, we used thermal vapor to treat the diseased parts of his right upper lung. We delivered the vapor to two specific segments. This will cause that tissue to scar down and shrink over the next few months, which should help him breathe better. He needs to stay in the hospital for monitoring as this causes a deliberate inflammation."""

entities_8 = [
    {"label": "PROC_ACTION",    **get_span(text_8, "steam treatment", 1)}, # [cite: 10]
    {"label": "DEV_VALVE",      **get_span(text_8, "valves", 1)}, # [cite: 4]
    {"label": "PROC_ACTION",    **get_span(text_8, "thermal vapor", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_8, "right upper lung", 1)}, # [cite: 2]
]
BATCH_DATA.append({"id": "34567890_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 34567890_syn_9
# ==========================================
text_9 = """Procedure: Endobronchial thermal therapy.
Target: Emphysematous lung tissue.
Action: Vapor energy was administered to the RUL segments. 
Result: Tissue ablation initiated.
Post-op: Inflammatory modulation protocol."""

entities_9 = [
    {"label": "PROC_ACTION",    **get_span(text_9, "Endobronchial thermal therapy", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_9, "RUL", 1)}, # [cite: 2]
]
BATCH_DATA.append({"id": "34567890_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 34567890
# ==========================================
text_10 = """BRONCHOSCOPIC THERMAL VAPOR ABLATION PROCEDURE NOTE

Patient: [REDACTED] | DOB: [REDACTED] | Age: 65 | MRN: [REDACTED]
Institution: [REDACTED]
Date: [REDACTED]
Procedure: Bronchoscopic Lung Volume Reduction via Thermal Vapor Ablation
Operator: Lisa Chen, MD | Assistant: RN Jennifer Thompson
Anesthesia: Dr. Michael Roberts, MD

BACKGROUND:
Patient [REDACTED] upper lobe predominant emphysema, failed prior medical management. CT shows 80% destruction of RUL with moderate collateral ventilation present (not ideal for valves).

PREPARATION:
- Pre-medication: Dexamethasone 8mg IV, acetaminophen 1000mg PO
- Sedation: Propofol infusion (monitored anesthesia care)
- Airway: Laryngeal mask airway placed

PROCEDURE:
Rigid bronchoscopy initially performed for airway assessment and measurement. Subsequently transitioned to flexible bronchoscopy with therapeutic bronchoscope.

InterVapor catheter advanced to RUL under direct visualization and fluoroscopic guidance. Vapor generator calibrated for target tissue volume of 10g.

TREATMENT ADMINISTERED:
- RUL anterior segment (RB3): 8 calories delivered
- Temperature achieved: 72°C at tissue interface
- Vapor penetration confirmed with fluoroscopy
- Treatment duration: 10 seconds
- Post-treatment bronchoscopy: Expected mucosal erythema, no bleeding

Second treatment site:
- RUL apical segment (RB1): 6 calories delivered  
- Similar technical success

TOTAL VAPOR ENERGY: 14 calories
TARGET TISSUE VOLUME: 10g

IMMEDIATE ASSESSMENT:
Patient [REDACTED] throughout. Mild bronchospasm treated with inhaled albuterol. No significant hemorrhage or pneumothorax.

POST-PROCEDURE ORDERS:
- ICU admission for monitoring (24-48 hours expected)
- Prednisone 40mg daily x 5 days
- Prophylactic antibiotics: Levofloxacin 750mg daily x 5 days
- Aggressive pulmonary toilet
- Serial chest radiographs
- Expected inflammatory response with infiltrate development

COMPLICATIONS: None intra-procedurally

The patient and family were counseled on expected post-procedure course including inflammatory reaction, potential for COPD exacerbation, and gradual symptom improvement over 3-6 months."""

entities_10 = [
    {"label": "PROC_ACTION",    **get_span(text_10, "BRONCHOSCOPIC THERMAL VAPOR ABLATION", 1)}, # [cite: 10]
    {"label": "PROC_ACTION",    **get_span(text_10, "Bronchoscopic Lung Volume Reduction", 1)}, # [cite: 10]
    {"label": "PROC_ACTION",    **get_span(text_10, "Thermal Vapor Ablation", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "RUL", 1)}, # [cite: 2]
    {"label": "DEV_VALVE",      **get_span(text_10, "valves", 1)}, # [cite: 4]
    {"label": "MEDICATION",     **get_span(text_10, "Dexamethasone", 1)}, # [cite: 20]
    {"label": "MEDICATION",     **get_span(text_10, "acetaminophen", 1)}, # [cite: 20]
    {"label": "MEDICATION",     **get_span(text_10, "Propofol", 1)}, # [cite: 20]
    {"label": "PROC_METHOD",    **get_span(text_10, "Rigid bronchoscopy", 1)}, # [cite: 10]
    {"label": "PROC_METHOD",    **get_span(text_10, "flexible bronchoscopy", 1)}, # [cite: 10]
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "therapeutic bronchoscope", 1)}, # [cite: 7]
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "InterVapor catheter", 1)}, # [cite: 7]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "RUL", 2)}, # [cite: 2]
    {"label": "PROC_METHOD",    **get_span(text_10, "fluoroscopic", 1)}, # [cite: 10]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "RUL", 3)}, # [cite: 2]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "RB3", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_10, "8 calories", 1)}, # [cite: 24]
    {"label": "MEAS_TEMP",      **get_span(text_10, "72°C", 1)}, # [cite: 23]
    {"label": "PROC_METHOD",    **get_span(text_10, "fluoroscopy", 1)}, # [cite: 10]
    {"label": "MEAS_TIME",      **get_span(text_10, "10 seconds", 1)}, # [cite: 22]
    {"label": "OBS_FINDING",    **get_span(text_10, "erythema", 1)}, # [cite: 20]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "RUL", 4)}, # [cite: 2]
    {"label": "ANAT_LUNG_LOC",  **get_span(text_10, "RB1", 1)}, # [cite: 2]
    {"label": "MEAS_ENERGY",    **get_span(text_10, "6 calories", 1)}, # [cite: 24]
    {"label": "MEAS_ENERGY",    **get_span(text_10, "14 calories", 1)}, # [cite: 24]
    {"label": "MEDICATION",     **get_span(text_10, "albuterol", 1)}, # [cite: 20]
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant hemorrhage", 1)}, # [cite: 16]
    {"label": "MEDICATION",     **get_span(text_10, "Prednisone", 1)}, # [cite: 20]
    {"label": "MEDICATION",     **get_span(text_10, "Levofloxacin", 1)}, # [cite: 20]
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)}, # [cite: 16]
]
BATCH_DATA.append({"id": "34567890", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)