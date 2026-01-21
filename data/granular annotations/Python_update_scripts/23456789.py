import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# Assuming saved in: data/granular_annotations/Python_update_scripts/
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 23456789_syn_1
# ------------------------------------------
id_1 = "23456789_syn_1"
text_1 = """Indication: RML Emphysema.
Proc: BLVR RML.
Action:
- Chartis: CV Negative.
- Valves: 2 Zephyr (RB4, RB5).
Result: RML occluded."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "Emphysema", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "BLVR", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 2)},
    {"label": "DEV_INSTRUMENT",**get_span(text_1, "Chartis", 1)},
    {"label": "DEV_VALVE",     **get_span(text_1, "Valves", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_1, "2", 1)},
    {"label": "DEV_VALVE",     **get_span(text_1, "Zephyr", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RB5", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 3)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 23456789_syn_2
# ------------------------------------------
id_2 = "23456789_syn_2"
text_2 = """PROCEDURE NOTE: Elective bronchoscopy for RML lung volume reduction. The right middle lobe was isolated. Chartis assessment confirmed absence of collateral ventilation. Two Zephyr valves were deployed in the medial (RB5) and lateral (RB4) segments. Complete lobar isolation was confirmed."""

entities_2 = [
    {"label": "PROC_ACTION",   **get_span(text_2, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right middle lobe", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_2, "Chartis", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_2, "Two", 1)},
    {"label": "DEV_VALVE",     **get_span(text_2, "Zephyr", 1)},
    {"label": "DEV_VALVE",     **get_span(text_2, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "medial", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RB5", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "lateral", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RB4", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 23456789_syn_3
# ------------------------------------------
id_3 = "23456789_syn_3"
text_3 = """CPT: 31647 (Valve placement initial lobe).
Target: Right Middle Lobe.
Valves: 2 (RB4, RB5).
Chartis: Negative for CV.
Outcome: Procedure successful."""

entities_3 = [
    {"label": "PROC_ACTION",   **get_span(text_3, "Valve placement", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Right Middle Lobe", 1)},
    {"label": "DEV_VALVE",     **get_span(text_3, "Valves", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_3, "2", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RB5", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_3, "Chartis", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 23456789_syn_4
# ------------------------------------------
id_4 = "23456789_syn_4"
text_4 = """Resident Note
Pt: [REDACTED]
Proc: RML Valves
Steps:
1. Insp RML.
2. Chartis negative.
3. Placed 2 valves (RB4, RB5).
4. No leaks.
Plan: Discharge."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RML", 1)},
    {"label": "DEV_VALVE",     **get_span(text_4, "Valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RML", 2)},
    {"label": "DEV_INSTRUMENT",**get_span(text_4, "Chartis", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_4, "2", 1)},
    {"label": "DEV_VALVE",     **get_span(text_4, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RB5", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 23456789_syn_5
# ------------------------------------------
id_5 = "23456789_syn_5"
text_5 = """RML valve case. Chartis said no collateral ventilation so we proceeded. Put in two valves one for lateral one for medial. RML collapsed nicely. No pneumo on xray. Sending home."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RML", 1)},
    {"label": "DEV_VALVE",     **get_span(text_5, "valve", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_5, "Chartis", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_5, "two", 1)},
    {"label": "DEV_VALVE",     **get_span(text_5, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lateral", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "medial", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RML", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "pneumo", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 23456789_syn_6
# ------------------------------------------
id_6 = "23456789_syn_6"
text_6 = """Bronchoscopic Lung Volume Reduction, Right Middle Lobe. Chartis CV negative. Two Zephyr valves deployed (RB4, RB5). Complete occlusion. Discharged home."""

entities_6 = [
    {"label": "PROC_ACTION",   **get_span(text_6, "Bronchoscopic Lung Volume Reduction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "Right Middle Lobe", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_6, "Chartis", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_6, "Two", 1)},
    {"label": "DEV_VALVE",     **get_span(text_6, "Zephyr", 1)},
    {"label": "DEV_VALVE",     **get_span(text_6, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RB5", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 23456789_syn_7
# ------------------------------------------
id_7 = "23456789_syn_7"
text_7 = """[Indication]
Severe emphysema RML.
[Anesthesia]
Moderate.
[Description]
Chartis negative. 2 valves placed RML. Good seal.
[Plan]
Discharge."""

entities_7 = [
    {"label": "OBS_LESION",    **get_span(text_7, "emphysema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RML", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_7, "Chartis", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_7, "2", 1)},
    {"label": "DEV_VALVE",     **get_span(text_7, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RML", 2)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 23456789_syn_8
# ------------------------------------------
id_8 = "23456789_syn_8"
text_8 = """[REDACTED] valve placement. After confirming no collateral ventilation with Chartis, we placed valves in the medial and lateral segments. The lobe was fully occluded, and she was discharged the same day."""

entities_8 = [
    {"label": "PROC_ACTION",   **get_span(text_8, "valve placement", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_8, "Chartis", 1)},
    {"label": "DEV_VALVE",     **get_span(text_8, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "medial", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lateral", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 23456789_syn_9
# ------------------------------------------
id_9 = "23456789_syn_9"
text_9 = """Procedure: BLVR with valve implantation.
Target: Right Middle Lobe.
Action: Chartis confirmed eligibility. Two valves implanted.
Result: Lobe occluded."""

entities_9 = [
    {"label": "PROC_ACTION",   **get_span(text_9, "BLVR", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "valve implantation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Right Middle Lobe", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_9, "Chartis", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_9, "Two", 1)},
    {"label": "DEV_VALVE",     **get_span(text_9, "valves", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ------------------------------------------
# Case 10: 23456789 (Main)
# ------------------------------------------
id_10 = "23456789"
text_10 = """BRONCHOSCOPY - EBV PLACEMENT RML
[REDACTED]

Patient: [REDACTED] | DOB: [REDACTED] | Age: 65 | MRN: [REDACTED]
Institution: [REDACTED]
Physician: Ahmed Hassan, MD | RN: Rebecca Chen, RN

Pt: 65F w/ heterogeneous emphysema
Target: RML (CT destruction 75%, fissure 90%)

Sedation: ✓ Moderate
Scope: Flexible video bronchoscope
Path:
• Oropharynx → larynx (nl)
• Trachea → carina (nl) 
• RML inspected - severe emphysema

Chartis: Negative CV (RML)

Valves placed:
• RB4 (lateral): 4.0mm EBV ✓
• RB5 (medial): 4.0mm EBV ✓

Result: Complete RML occlusion
CXR: Valves in place, no PTX
Dispo: Home same day

Ahmed Hassan, MD
Johns Hopkins Interventional Pulmonology"""

entities_10 = [
    {"label": "PROC_ACTION",   **get_span(text_10, "BRONCHOSCOPY", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "EBV PLACEMENT", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "emphysema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 2)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "Flexible video bronchoscope", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "carina", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 3)},
    {"label": "OBS_LESION",    **get_span(text_10, "emphysema", 2)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "Chartis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 4)},
    {"label": "DEV_VALVE",     **get_span(text_10, "Valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lateral", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_10, "4.0mm", 1)},
    {"label": "DEV_VALVE",     **get_span(text_10, "EBV", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB5", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "medial", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_10, "4.0mm", 2)},
    {"label": "DEV_VALVE",     **get_span(text_10, "EBV", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 5)},
    {"label": "DEV_VALVE",     **get_span(text_10, "Valves", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "PTX", 1)}
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)