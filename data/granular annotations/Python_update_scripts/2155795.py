import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
# Ensure this script is run from a location where 'scripts.add_training_case' is accessible
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for dictionary unpacking.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 2155795_syn_1
# ==========================================
id_1 = "2155795_syn_1"
text_1 = """Proc: Rt Thoracoscopy w/ Biopsy & Talc.
Findings: Malignant nodules.
Actions:
- 10 biopsies parietal pleura.
- Diaphragmatic biopsies.
- Talc poudrage.
- Tube placed.
Status: No leak."""

entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "Rt", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Talc", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "10", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 2)},
    {"label": "MEDICATION", **get_span(text_1, "Talc", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "No leak", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2155795_syn_2
# ==========================================
id_2 = "2155795_syn_2"
text_2 = """OPERATIVE REPORT: Right medical thoracoscopy was performed for persistent effusion. Multiple nodules with a malignant appearance were id[REDACTED] on the parietal pleura. Ten biopsies were harvested from the parietal surface, with additional sampling of the diaphragm. Talc poudrage was performed for pleurodesis. The chest was drained and a tube placed."""

entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "medical thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Ten", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_2, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "tube", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2155795_syn_3
# ==========================================
id_3 = "2155795_syn_3"
text_3 = """Codes: 32609 (Biopsy) + 32650 (Pleurodesis).
Site: [REDACTED]
Tech: 10 specimens taken from parietal pleura. Diaphragm sampled. Talc insufflated. Chest tube inserted."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Pleurodesis", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "10", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "specimens", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "Diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_3, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "insufflated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Chest tube", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2155795_syn_4
# ==========================================
id_4 = "2155795_syn_4"
text_4 = """Procedure: Right Thoracoscopy
Steps:
1. Sedation.
2. Scope inserted right 6th ICS.
3. Findings: Malignant nodules.
4. Biopsies: 10 parietal + diaphragm.
5. Talc poudrage.
6. Chest tube placed.
Plan: Oncology consult."""

entities_4 = [
    {"label": "LATERALITY", **get_span(text_4, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Thoracoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "LATERALITY", **get_span(text_4, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "6th ICS", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "10", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2155795_syn_5
# ==========================================
id_5 = "2155795_syn_5"
text_5 = """right thoracoscopy for elizabeth saw nodules looked malignant took 10 biopsies from the wall plus some from diaphragm did the talc poudrage too drained it all chest tube in place"""

entities_5 = [
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "10", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "wall", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_5, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2155795_syn_6
# ==========================================
id_6 = "2155795_syn_6"
text_6 = """Right medical thoracoscopy was performed. Multiple malignant-appearing nodules were noted. Ten biopsies were obtained from the parietal pleura, along with diaphragmatic biopsies. Talc poudrage was performed for pleurodesis. Fluid was evacuated and a chest tube was placed."""

entities_6 = [
    {"label": "LATERALITY", **get_span(text_6, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "medical thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Ten", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 2)},
    {"label": "MEDICATION", **get_span(text_6, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2155795_syn_7
# ==========================================
id_7 = "2155795_syn_7"
text_7 = """[Indication] Persistent effusion.
[Anesthesia] Moderate.
[Description] Right thoracoscopy. Malignant nodules. 10 parietal biopsies. Diaphragmatic biopsies. Talc poudrage.
[Plan] Path results."""

entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "10", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "parietal", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "Diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 2)},
    {"label": "MEDICATION", **get_span(text_7, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "poudrage", 1)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2155795_syn_8
# ==========================================
id_8 = "2155795_syn_8"
text_8 = """We performed a right medical thoracoscopy on [REDACTED]. The pleura showed multiple malignant-appearing nodules. We collected ten biopsies from the parietal pleura and additional samples from the diaphragm. We then performed talc poudrage for pleurodesis and placed a chest tube."""

entities_8 = [
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "ten", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_8, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2155795_syn_9
# ==========================================
id_9 = "2155795_syn_9"
text_9 = """Right pleuroscopy performed. Malignant nodules observed. Ten tissue samples harvested from parietal pleura; diaphragm also sampled. Talc insufflation executed. Fluid drained and catheter deployed."""

entities_9 = [
    {"label": "LATERALITY", **get_span(text_9, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "pleuroscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Ten", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "tissue samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_9, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "insufflation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "catheter", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 2155795
# ==========================================
id_10 = "2155795"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: LCDR John Park, MD
Fellow: Dr. Maria Santos (PGY-6)

Indication: Persistent effusion despite thoracentesis
Side: Right

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Multiple pleural nodules - malignant appearing
Multiple biopsies obtained from parietal pleura (10 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
Given findings, talc poudrage performed for pleurodesis.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Park, MD"""

entities_10 = [
    {"label": "OBS_FINDING", **get_span(text_10, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Pleural Biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "mid-axillary line", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "pleuroscope", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "10", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "diaphragmatic pleura", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Specimens", 1)},
    {"label": "MEDICATION", **get_span(text_10, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "No air leak", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 2)}
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)