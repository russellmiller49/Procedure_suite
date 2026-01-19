import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from a subdirectory, we look for the root
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return start, start + len(term)

# ==========================================
# Note 1: 4351628_syn_1
# ==========================================
text_1 = """Indication: LUL Emphysema.
Procedure: Valve Placement (4 valves).
- 31647: LB1+2 (Initial).
- 31651: LB3 (Add'l).
- 31651: LB4 (Add'l).
- 31651: LB5 (Add'l).
Result: Total occlusion LUL."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_1, "LUL", 1)))},
    {"label": "OBS_FINDING",              **dict(zip(["start", "end"], get_span(text_1, "Emphysema", 1)))},
    {"label": "PROC_ACTION",              **dict(zip(["start", "end"], get_span(text_1, "Valve Placement", 1)))},
    {"label": "MEAS_COUNT",               **dict(zip(["start", "end"], get_span(text_1, "4", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_1, "valves", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_1, "LB1+2", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_1, "LB3", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_1, "LB4", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_1, "LB5", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_1, "Total occlusion", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_1, "LUL", 2)))},
]
BATCH_DATA.append({"id": "4351628_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4351628_syn_2
# ==========================================
text_2 = """PROCEDURE: Bronchoscopic Lung Volume Reduction.
TARGET: Left Upper Lobe.
DETAILS: The airway was sized. The first valve (Zephyr 5.5) was deployed in the apicoposterior segment (Initial Lobe, 31647). Subsequently, valves were deployed in the Anterior, Superior Lingula, and Inferior Lingula segments (Each additional bronchus, 31651 x3). Complete lobar occlusion was verified visually."""

entities_2 = [
    {"label": "PROC_ACTION",              **dict(zip(["start", "end"], get_span(text_2, "Bronchoscopic Lung Volume Reduction", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_2, "Left Upper Lobe", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_2, "valve", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_2, "Zephyr 5.5", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_2, "apicoposterior segment", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_2, "valves", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_2, "Anterior", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_2, "Superior Lingula", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_2, "Inferior Lingula", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_2, "Complete lobar occlusion", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4351628_syn_3
# ==========================================
text_3 = """Billing Codes:
- 31647 (1 unit): Initial bronchus valve placement (LB1+2).
- 31651 (3 units): Additional bronchus valve placements (LB3, LB4, LB5).
Note: Procedure performed in LUL. Four distinct segmental bronchi treated."""

entities_3 = [
    {"label": "PROC_ACTION",              **dict(zip(["start", "end"], get_span(text_3, "valve placement", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_3, "LB1+2", 1)))},
    {"label": "PROC_ACTION",              **dict(zip(["start", "end"], get_span(text_3, "valve placements", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_3, "LB3", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_3, "LB4", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_3, "LB5", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_3, "LUL", 1)))},
    {"label": "MEAS_COUNT",               **dict(zip(["start", "end"], get_span(text_3, "Four", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4351628_syn_4
# ==========================================
text_4 = """Procedure: BLVR LUL
Steps:
1. Chartis negative.
2. Placed valve in LB1+2 (First).
3. Placed valve in LB3 (Add-on).
4. Placed valve in LB4 (Add-on).
5. Placed valve in LB5 (Add-on).
All valves look good."""

entities_4 = [
    {"label": "PROC_ACTION",              **dict(zip(["start", "end"], get_span(text_4, "BLVR", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_4, "LUL", 1)))},
    {"label": "PROC_METHOD",              **dict(zip(["start", "end"], get_span(text_4, "Chartis", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_4, "valve", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_4, "LB1+2", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_4, "valve", 2)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_4, "LB3", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_4, "valve", 3)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_4, "LB4", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_4, "valve", 4)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_4, "LB5", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_4, "valves", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4351628_syn_5
# ==========================================
text_5 = """harold johnson here for valve placement lul. chartis was good. put the first valve in the top segment. then put three more in the other segments to block the whole lobe. four valves total. patient woke up fine."""

entities_5 = [
    {"label": "PROC_ACTION",              **dict(zip(["start", "end"], get_span(text_5, "valve placement", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_5, "lul", 1)))},
    {"label": "PROC_METHOD",              **dict(zip(["start", "end"], get_span(text_5, "chartis", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_5, "valve", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_5, "top segment", 1)))},
    {"label": "MEAS_COUNT",               **dict(zip(["start", "end"], get_span(text_5, "three", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_5, "lobe", 1)))},
    {"label": "MEAS_COUNT",               **dict(zip(["start", "end"], get_span(text_5, "four", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_5, "valves", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4351628_syn_6
# ==========================================
text_6 = """Bronchoscopic lung volume reduction performed on Left Upper Lobe. Initial valve placed in LB1+2. Additional valves placed in LB3, LB4, and LB5. Total of 4 Zephyr valves deployed. Complete occlusion achieved."""

entities_6 = [
    {"label": "PROC_ACTION",              **dict(zip(["start", "end"], get_span(text_6, "Bronchoscopic lung volume reduction", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_6, "Left Upper Lobe", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_6, "valve", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_6, "LB1+2", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_6, "valves", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_6, "LB3", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_6, "LB4", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_6, "LB5", 1)))},
    {"label": "MEAS_COUNT",               **dict(zip(["start", "end"], get_span(text_6, "4", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_6, "Zephyr valves", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_6, "Complete occlusion", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4351628_syn_7
# ==========================================
text_7 = """[Indication]
Severe Emphysema, LUL target.
[Anesthesia]
General.
[Description]
Valves placed:
1. LB1+2 (31647)
2. LB3 (31651)
3. LB4 (31651)
4. LB5 (31651)
[Plan]
Admit for obs."""

entities_7 = [
    {"label": "OBS_FINDING",              **dict(zip(["start", "end"], get_span(text_7, "Emphysema", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_7, "LUL", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_7, "Valves", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_7, "LB1+2", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_7, "LB3", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_7, "LB4", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_7, "LB5", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4351628_syn_8
# ==========================================
text_8 = """We treated [REDACTED] blocking off the diseased upper left part of his lung. We placed a total of four one-way valves. The first one went into the top segment, and then we placed three more in the remaining segments of that lobe to make sure no air could get in. This should help the healthier parts of his lung work better."""

entities_8 = [
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_8, "upper left part of his lung", 1)))},
    {"label": "MEAS_COUNT",               **dict(zip(["start", "end"], get_span(text_8, "four", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_8, "one-way valves", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_8, "top segment", 1)))},
    {"label": "MEAS_COUNT",               **dict(zip(["start", "end"], get_span(text_8, "three", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_8, "lobe", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4351628_syn_9
# ==========================================
text_9 = """Procedure: Deployment of bronchial flow-control devices.
Target: LUL.
Action: Primary device anchored in LB1+2. Supplemental devices anchored in LB3, LB4, and LB5.
Outcome: Lobar isolation."""

entities_9 = [
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_9, "bronchial flow-control devices", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_9, "LUL", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_9, "device", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_9, "LB1+2", 1)))},
    {"label": "DEV_VALVE",                **dict(zip(["start", "end"], get_span(text_9, "devices", 2)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_9, "LB3", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_9, "LB4", 1)))},
    {"label": "ANAT_LUNG_LOC",            **dict(zip(["start", "end"], get_span(text_9, "LB5", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_9, "Lobar isolation", 1)))},
]
BATCH_DATA.append({"id": "4351628_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)