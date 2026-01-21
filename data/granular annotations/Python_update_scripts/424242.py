import sys
from pathlib import Path

# 1. Dynamic Repo Root Setup
#    Assumes this script is run from inside the repository structure
#    (e.g., /repo/scripts/add_case_424242.py)
try:
    REPO_ROOT = Path(__file__).resolve().parents[1]
except NameError:
    REPO_ROOT = Path(".").resolve()

# 2. Add scripts directory to path to import utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 424242_syn_1
# ==========================================
id_1 = "424242_syn_1"
text_1 = "BLVR LUL. Chartis negative (CV-). 4 Zephyr valves placed. Good occlusion."
entities_1 = [
    {"label": "PROC_ACTION", **get_span(text_1, "BLVR", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "negative", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "CV-", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)},
    {"label": "DEV_VALVE", **get_span(text_1, "Zephyr", 1)},
    {"label": "DEV_VALVE", **get_span(text_1, "valves", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "Good occlusion", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 424242_syn_2
# ==========================================
id_2 = "424242_syn_2"
text_2 = "[REDACTED] lung volume reduction targeting the left upper lobe. Chartis assessment confirmed the absence of collateral ventilation. Four Zephyr endobronchial valves were sequentially deployed, achieving complete lobar atelectasis."
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "lung volume reduction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left upper lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "absence of collateral ventilation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Four", 1)},
    {"label": "DEV_VALVE", **get_span(text_2, "Zephyr", 1)},
    {"label": "DEV_VALVE", **get_span(text_2, "endobronchial valves", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "deployed", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_2, "complete lobar atelectasis", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 424242_syn_3
# ==========================================
id_3 = "424242_syn_3"
text_3 = "CPT 31647: Bronchoscopy with placement of valves, initial lobe. LUL treated. Chartis assessment (31634 bundled) confirmed no collateral ventilation. 4 valves placed."
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "placement", 1)},
    {"label": "DEV_VALVE", **get_span(text_3, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "no collateral ventilation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "4", 1)},
    {"label": "DEV_VALVE", **get_span(text_3, "valves", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "placed", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 424242_syn_4
# ==========================================
id_4 = "424242_syn_4"
text_4 = "Procedure: BLVR LUL. Steps: 1. GA/ETT. 2. Chartis check: No CV. 3. 4 valves deployed in LUL. 4. Occlusion confirmed."
entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "BLVR", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "GA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "ETT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "No CV", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "4", 2)}, # Occurrence 2 because '4' is also in '4. Occlusion'
    {"label": "DEV_VALVE", **get_span(text_4, "valves", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "deployed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "Occlusion confirmed", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 424242_syn_5
# ==========================================
id_5 = "424242_syn_5"
text_5 = "blvr for arthur dent lul emphysema chartis showed no cv so we put in 4 valves they sealed up good no pneumo seen right away admit for obs."
entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "blvr", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lul", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "emphysema", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "chartis", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "no cv", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "4", 1)},
    {"label": "DEV_VALVE", **get_span(text_5, "valves", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_5, "sealed up good", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no pneumo", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 424242_syn_6
# ==========================================
id_6 = "424242_syn_6"
text_6 = "Patient [REDACTED] LUL emphysema underwent valve placement. Chartis assessment showed no collateral ventilation. Four Zephyr valves were placed in the LUL segments. Lobar occlusion was confirmed."
entities_6 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "emphysema", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "valve placement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "no collateral ventilation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Four", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "Zephyr", 1)},
    {"label": "DEV_VALVE", **get_span(text_6, "valves", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "placed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "Lobar occlusion", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 424242_syn_7
# ==========================================
id_7 = "424242_syn_7"
text_7 = "[Indication] LUL Emphysema. [Anesthesia] General. [Description] Chartis neg. 4 valves to LUL. [Plan] Admit."
entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Emphysema", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "General", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "neg", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "4", 1)},
    {"label": "DEV_VALVE", **get_span(text_7, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 2)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 424242_syn_8
# ==========================================
id_8 = "424242_syn_8"
text_8 = "[REDACTED] for his valve procedure. We checked the LUL with the Chartis balloon and found no collateral ventilation. We then placed four valves to block off the lobe completely. He did well and went to recovery."
entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "valve procedure", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "LUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "Chartis balloon", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "no collateral ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "placed", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "four", 1)},
    {"label": "DEV_VALVE", **get_span(text_8, "valves", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "block off the lobe completely", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 424242_syn_9
# ==========================================
id_9 = "424242_syn_9"
text_9 = "Endobronchial valve implantation for lung volume reduction. The LUL was isolated. Four occlusion devices were inserted."
entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Endobronchial valve implantation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "lung volume reduction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LUL", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Four", 1)},
    {"label": "DEV_VALVE", **get_span(text_9, "occlusion devices", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "inserted", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 424242
# ==========================================
id_10 = "424242"
text_10 = """OPERATIVE REPORT: BRONCHOSCOPIC LUNG VOLUME REDUCTION

PATIENT: [REDACTED]
MRN: [REDACTED]
DATE: [REDACTED]

INDICATION: Severe heterogeneous emphysema, LUL predominant. PFTs: FEV1 28%, RV 210%. CT shows intact fissures. Presented for valve placement.

PROCEDURE:
Flexible bronchoscopy via ETT/General Anesthesia. 

1. CHARTIS ASSESSMENT:
   The Chartis balloon catheter was advanced to the LUL bronchus. Balloon inflated. 
   Result: CV Negative (Flow dropped to zero, pressure separation maintained). Fissure integrity confirmed.

2. VALVE DEPLOYMENT (Zephyr):
   Target: Left Upper Lobe.
   - LB 1+2 (Apical-Posterior): Zephyr 4.0 deployed. Good seal.
   - LB 3 (Anterior): Zephyr 4.0 deployed. Good seal.
   - LB 4 (Lingula Superior): Zephyr 5.5-LP deployed. Good seal.
   - LB 5 (Lingula Inferior): Zephyr 5.5 deployed. Good seal.

Total 4 valves placed. Lobar occlusion confirmed. No complications.

IMPRESSION: Successful BLVR of LUL."""
entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "BRONCHOSCOPIC LUNG VOLUME REDUCTION", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "emphysema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "valve placement", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "General Anesthesia", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Chartis balloon catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Balloon", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "CV Negative", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "VALVE DEPLOYMENT", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "Zephyr", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Left Upper Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB 1+2", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Apical-Posterior", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "Zephyr 4.0", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "deployed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB 3", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Anterior", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "Zephyr 4.0", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "deployed", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB 4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lingula Superior", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "Zephyr 5.5-LP", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "deployed", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB 5", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lingula Inferior", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "Zephyr 5.5", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "deployed", 4)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4", 1)},
    {"label": "DEV_VALVE", **get_span(text_10, "valves", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "Lobar occlusion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "BLVR", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 3)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)