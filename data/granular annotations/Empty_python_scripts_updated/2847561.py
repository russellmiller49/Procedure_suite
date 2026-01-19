import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 2847561_syn_1
# ------------------------------------------
id_1 = "2847561_syn_1"
text_1 = """Procedure: Bronchoscopic Cryoablation LUL.
Target: 1.8cm nodule.
Technique: ENB + r-EBUS to localize. Cryoprobe inserted.
Ablation: 2 cycles (5 min freeze / 3 min thaw).
Result: Ice ball visualized. No bleeding.
Plan: D/C home."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8cm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "r-EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cryoprobe", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Ablation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "5 min", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "freeze", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "3 min", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "thaw", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Ice ball", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No bleeding", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 2847561_syn_2
# ------------------------------------------
id_2 = "2847561_syn_2"
text_2 = """OPERATIVE REPORT: The patient presented for bronchoscopic ablation of a biopsy-proven Stage IA1 adenocarcinoma in the LUL. Electromagnetic navigation (SPiN system) was utilized to navigate to the anterior segment. Radial EBUS confirmed concentric probe placement. A 2.4mm cryoprobe was deployed. Therapeutic cryoablation was administered via two freeze-thaw cycles (5 minutes each). Fluoroscopic imaging confirmed the formation of an ice ball encompassing the lesion margin. Post-procedure inspection revealed no hemorrhage."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "SPiN system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Radial EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "2.4mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "cryoprobe", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "cryoablation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "two", 1)},
    {"label": "MEAS_TIME", **get_span(text_2, "5 minutes", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Fluoroscopic imaging", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "ice ball", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "no hemorrhage", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 2847561_syn_3
# ------------------------------------------
id_3 = "2847561_syn_3"
text_3 = """Billing Record:
- 31641 (Destruction of tumor, bronchoscopic): Cryoablation of LUL nodule.
- 31627 (Navigational Bronchoscopy): Used for localization.
- 31654 (Radial EBUS): Used for verification of target.
Device: Erbe Cryo 2 system.
Time: Ablation duration 300s x 2."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Erbe Cryo 2 system", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Ablation", 1)},
    {"label": "MEAS_TIME", **get_span(text_3, "300s", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "2", 2)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 2847561_syn_4
# ------------------------------------------
id_4 = "2847561_syn_4"
text_4 = """Procedure: Cryoablation LUL
Staff: Dr. Patterson
Steps:
1. Navigated to LUL nodule with ENB.
2. Checked with rEBUS - concentric view.
3. Put cryo probe in.
4. Freezing x 2 cycles.
5. Saw ice ball on fluoro.
No complications."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 2)},
    {"label": "OBS_LESION", **get_span(text_4, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "cryo probe", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Freezing", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "2", 2)},
    {"label": "OBS_FINDING", **get_span(text_4, "ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "fluoro", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No complications", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 2847561_syn_5
# ------------------------------------------
id_5 = "2847561_syn_5"
text_5 = """[REDACTED] here for the freezing procedure cryoablation. She has that small cancer in the LUL. We used the navigation system to get there and the ultrasound probe to make sure we were in the middle. Put the freezing probe in and froze it for 5 minutes then let it thaw then froze it again. Ice ball looked good on the xray screen. Patient did great no bleeding."""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "freezing", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "cryoablation", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "cancer", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "navigation system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "ultrasound probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "freezing probe", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "froze", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "5 minutes", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "thaw", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "froze", 2)},
    {"label": "OBS_FINDING", **get_span(text_5, "Ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "xray screen", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 2847561_syn_6
# ------------------------------------------
id_6 = "2847561_syn_6"
text_6 = """Bronchoscopic cryoablation of left upper lobe nodule. Patient is a 63-year-old female with stage IA1 adenocarcinoma. Under general anesthesia, electromagnetic navigation was used to reach the LUL target. Radial EBUS confirmed lesion position. A cryoprobe was advanced and two freeze-thaw cycles were performed to ablate the tumor. An ice ball was visualized fluoroscopically. There were no immediate complications."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "two", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "fluoroscopically", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no immediate complications", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 2847561_syn_7
# ------------------------------------------
id_7 = "2847561_syn_7"
text_7 = """[Indication]
LUL Nodule, Stage IA1 NSCLC, non-surgical candidate.
[Anesthesia]
General, ETT.
[Description]
Navigation to LUL. r-EBUS confirmation. Cryoablation performed (2 cycles). Ice ball confirmed. Airways intact.
[Plan]
Discharge. CT chest 4 weeks."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "NSCLC", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 2)},
    {"label": "PROC_METHOD", **get_span(text_7, "r-EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Cryoablation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "2", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Ice ball", 1)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 2847561_syn_8
# ------------------------------------------
id_8 = "2847561_syn_8"
text_8 = """Because [REDACTED]'t a candidate for surgery, we proceeded with cryoablation of her lung nodule. We navigated a bronchoscope to the small tumor in her left upper lobe and confirmed its location with ultrasound. We then inserted a specialized freezing probe and performed two freezing cycles to destroy the tumor tissue. We could see the ice ball forming on the x-ray monitor, ensuring we treated the whole area."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "navigated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "bronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left upper lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "freezing probe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "two", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "freezing", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 2)},
    {"label": "OBS_FINDING", **get_span(text_8, "ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "x-ray monitor", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 2847561_syn_9
# ------------------------------------------
id_9 = "2847561_syn_9"
text_9 = """Procedure: Endobronchial cryotherapy.
Target: Peripheral pulmonary lesion.
Action: The instrument was steered to the LUL using electromagnetic guidance. The position was authenticated via radial ultrasound. A cryo-tip was inserted, and thermal ablation was executed via freezing cycles.
Outcome: Lesion destruction visually confirmed via fluoroscopy."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Endobronchial", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "cryotherapy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "pulmonary", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "electromagnetic guidance", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "radial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "cryo-tip", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "thermal ablation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "freezing", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "destruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "fluoroscopy", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ------------------------------------------
# Case 10: 2847561
# ------------------------------------------
id_10 = "2847561"
text_10 = """Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Facility: [REDACTED]
Physician: Dr. James Patterson, MD

PRE-OP DX: LUL nodule, 1.8cm, PET-avid, biopsy proven NSCLC
POST-OP DX: Same
PROCEDURE: Bronchoscopic cryoablation of LUL peripheral nodule

Patient is a 63 y/o female with stage IA1 adenocarcinoma, poor surgical candidate. Bronchoscopy performed under general anesthesia with 8.0 ETT. ENB navigation to LUL anterior segment lesion using SPiN thoracic navigation system. Target confirmed with r-EBUS and fluoroscopy. Cryoprobe (erbecryo 2, 2.4mm) advanced to lesion center. Two freeze-thaw cycles performed: 5 min freeze, 3 min passive thaw, 5 min freeze, 5 min passive thaw. Ice ball formation visualized on fluoroscopy. Post-procedure inspection showed intact airways, no bleeding. Patient tolerated well, extubated, to PACU stable.

COMPLICATIONS: None
EBL: <5 mL

PLAN: Observation, CXR at 4 hours, discharge if stable, CT chest in 4 weeks, f/u clinic 1 week.

Dr. James Patterson, MD"""

entities_10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.8cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "NSCLC", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "cryoablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ENB navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "anterior segment", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "SPiN thoracic navigation system", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "r-EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Cryoprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "erbecryo 2", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Two", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "5 min", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "freeze", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "3 min", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "thaw", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "5 min", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "freeze", 2)},
    {"label": "MEAS_TIME", **get_span(text_10, "5 min", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "thaw", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "Ice ball", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopy", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)}
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)