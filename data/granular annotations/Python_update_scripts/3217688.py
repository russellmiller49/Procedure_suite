import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3217688_syn_1
# ==========================================
text_1 = """Proc: Rt Med Thoracoscopy w/ Biopsy.
Findings: Inflammatory changes. No nodules.
Actions:
- 12 biopsies from parietal pleura.
- Diaphragmatic biopsies taken.
- Fluid evacuated.
- Chest tube placed.
- No pleurodesis performed.
Status: Stable."""

entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "Rt", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Med Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Inflammatory changes", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "pleurodesis", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 3217688_syn_2
# ==========================================
text_2 = """PROCEDURE RECORD: Right-sided medical thoracoscopy was initiated for exudative effusion. Visual inspection demonstrated significant inflammatory changes lacking distinct nodularity. Extensive sampling was conducted, with twelve biopsies harvested from the parietal pleura and additional tissue from the diaphragm for immunohistochemistry. Fluid was fully evacuated. No chemical pleurodesis was undertaken. A thoracostomy tube was positioned."""

entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "Right-sided", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "medical thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "exudative effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Visual inspection", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "inflammatory changes", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "harvested", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleura", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "tissue", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "diaphragm", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "evacuated", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "chemical pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "thoracostomy tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "positioned", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 3217688_syn_3
# ==========================================
text_3 = """Billing: 32609 (Thoracoscopy with pleura biopsy).
Technique: Right 6th ICS entry. Visual inspection showed inflammation. Biopsy forceps utilized to obtain 12 specimens from parietal pleura and additional from diaphragm to rule out malignancy. No therapeutic pleurodesis (32650) performed. Chest tube inserted."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "LATERALITY", **get_span(text_3, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "6th ICS", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Visual inspection", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "inflammation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Biopsy forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "12", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "specimens", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "therapeutic pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "inserted", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 3217688_syn_4
# ==========================================
text_4 = """Resident Note: Right Medical Thoracoscopy
Steps:
1. Moderate sedation.
2. Trocar placement right chest.
3. Visualization: Inflammatory changes, no masses.
4. Biopsy: 12 parietal specimens + diaphragm samples.
5. Fluid drainage complete.
6. Chest tube secured. No air leak."""

entities_4 = [
    {"label": "LATERALITY", **get_span(text_4, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Medical Thoracoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Trocar", 1)},
    {"label": "LATERALITY", **get_span(text_4, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "chest", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Inflammatory changes", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "masses", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "parietal", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "specimens", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "diaphragm", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "samples", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "drainage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_4, "No air leak", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 3217688_syn_5
# ==========================================
text_5 = """right side thoracoscopy done for effusion looked mostly inflammatory didn't see nodules but we took a lot of biopsies anyway 12 from the parietal pleura and some from diaphragm just to be sure drained the fluid put the chest tube in no talc used today"""

entities_5 = [
    {"label": "LATERALITY", **get_span(text_5, "right side", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "inflammatory", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drained", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
    {"label": "MEDICATION", **get_span(text_5, "talc", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 3217688_syn_6
# ==========================================
text_6 = """Right medical thoracoscopy was performed under local anesthesia and sedation. The pleural space revealed inflammatory changes without obvious nodularity. Twelve biopsies were taken from the parietal pleura, along with diaphragmatic biopsies. The specimens were sent for pathology. Fluid was drained and a chest tube was placed. The patient tolerated the procedure well."""

entities_6 = [
    {"label": "LATERALITY", **get_span(text_6, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "inflammatory changes", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 2)},
    {"label": "SPECIMEN", **get_span(text_6, "specimens", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "placed", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 3217688_syn_7
# ==========================================
text_7 = """[Indication] Cytology-negative effusion.
[Anesthesia] Moderate.
[Description] Right thoracoscopy. Findings: Inflammatory changes. Interventions: 12 biopsies parietal pleura, plus diaphragmatic samples. Fluid drained. Chest tube placed.
[Plan] Path review, oncology consult if positive."""

entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "diaphragmatic", 1)},
    {"label": "SPECIMEN", **get_span(text_7, "samples", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "placed", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 3217688_syn_8
# ==========================================
text_8 = """[REDACTED] a right medical thoracoscopy. The inspection revealed inflammatory changes but no distinct nodularity. We obtained twelve biopsies from the parietal pleura and additional samples from the diaphragm to ensure a comprehensive evaluation. All fluid was evacuated, and a chest tube was placed. No pleurodesis was performed."""

entities_8 = [
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "inflammatory changes", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal pleura", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "diaphragm", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "placed", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "pleurodesis", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 3217688_syn_9
# ==========================================
text_9 = """Right pleuroscopy executed. Visual assessment showed inflammatory alterations without nodularity. Twelve tissue samples harvested from the parietal pleura, with further sampling of the diaphragm. Effusion drained. Catheter deployed. No sclerosing agent utilized."""

entities_9 = [
    {"label": "LATERALITY", **get_span(text_9, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "pleuroscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "inflammatory alterations", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Twelve", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "tissue samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "harvested", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "diaphragm", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "deployed", 1)},
    {"label": "MEDICATION", **get_span(text_9, "sclerosing agent", 1)}
]
BATCH_DATA.append({"id": "3217688_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# Note 10: 3217688
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams
Fellow: Dr. Maria Santos (PGY-6)

Indication: Cytology-negative exudative effusion
Side: Right

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Inflammatory changes without nodularity
Multiple biopsies obtained from parietal pleura (12 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Williams, MD"""

entities_10 = [
    {"label": "OBS_FINDING", **get_span(text_10, "exudative effusion", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Pleural Biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "pleuroscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "inserted", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "inspected", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Inflammatory changes", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "nodularity", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "12", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "diaphragmatic pleura", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Specimens", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placed", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "No air leak", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 2)}
]
BATCH_DATA.append({"id": "3217688", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)