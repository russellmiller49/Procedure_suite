import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
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

BATCH_DATA = []

# ==========================================
# Note 1: 917337_syn_1
# ==========================================
id_1 = "917337_syn_1"
text_1 = """Proc: Rt Med Thoracoscopy w/ Biopsy & Talc.
Findings: Diffuse pleural nodularity.
Actions:
- 7 biopsies taken from parietal pleura.
- Diaphragmatic biopsies taken.
- Talc poudrage performed.
- Fluid evacuated.
- Chest tube placed.
Status: Hemostasis achieved. No leak."""
ent_1 = [
    {"label": "LATERALITY", **get_span(text_1, "Rt", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Med Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Talc", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Talc poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Fluid evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": ent_1})

# ==========================================
# Note 2: 917337_syn_2
# ==========================================
id_2 = "917337_syn_2"
text_2 = """OPERATIVE NARRATIVE: The patient underwent a right-sided medical thoracoscopy under moderate sedation. Inspection of the pleural cavity revealed diffuse nodularity involving the parietal surface. Histological sampling was performed, yielding seven distinct specimens from the parietal pleura, alongside diaphragmatic sampling. Following biopsy, chemical pleurodesis was achieved via talc insufflation (poudrage) to address the malignant effusion. A chest tube was secured post-evacuation."""
ent_2 = [
    {"label": "LATERALITY", **get_span(text_2, "right-sided", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural cavity", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "nodularity", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal surface", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sampling", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "seven", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "specimens", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sampling", 2)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "chemical pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "talc insufflation", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": ent_2})

# ==========================================
# Note 3: 917337_syn_3
# ==========================================
id_3 = "917337_syn_3"
text_3 = """Code Justification:
- 32609 (Thoracoscopy with biopsy): Right pleural space accessed. Diffuse nodules visualized. Biopsy forceps used to obtain 7 specimens from parietal pleura.
- 32650 (Thoracoscopy with pleurodesis): Talc poudrage insufflated under direct visualization for pleurodesis.
Device: Semi-rigid pleuroscope. Outcome: Fluid drained, tube placed."""
ent_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Thoracoscopy with biopsy", 1)},
    {"label": "LATERALITY", **get_span(text_3, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleural space", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodules", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Biopsy forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "7", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Thoracoscopy with pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Talc poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleurodesis", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Semi-rigid pleuroscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Fluid drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "tube", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": ent_3})

# ==========================================
# Note 4: 917337_syn_4
# ==========================================
id_4 = "917337_syn_4"
text_4 = """Procedure Note: Right Thoracoscopy
Steps:
1. Time out/Sedation.
2. Port created 6th ICS mid-axillary.
3. Scope inserted; diffuse nodules seen.
4. Biopsies x7 taken from parietal pleura; additional from diaphragm.
5. Talc poudrage performed for pleurodesis.
6. Chest tube placed to suction.
Complications: None."""
ent_4 = [
    {"label": "LATERALITY", **get_span(text_4, "Right", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "6th ICS mid-axillary", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "7", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Talc poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": ent_4})

# ==========================================
# Note 5: 917337_syn_5
# ==========================================
id_5 = "917337_syn_5"
text_5 = """did a right thoracoscopy on mr [REDACTED] saw a lot of nodules on the pleura took about 7 biopsies from the wall and some from the diaphragm sent for path then we did talc poudrage to stop the fluid chest tube is in place no air leak patient fine"""
ent_5 = [
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "wall", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "talc poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "air leak", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": ent_5})

# ==========================================
# Note 6: 917337_syn_6
# ==========================================
id_6 = "917337_syn_6"
text_6 = """Under moderate sedation, a right-sided single-port thoracoscopy was performed. The pleural space demonstrated diffuse nodularity. Seven biopsies were obtained from the parietal pleura, with additional samples from the diaphragm. Given the findings, talc poudrage was performed for pleurodesis. All fluid was evacuated and a chest tube was placed. Hemostasis was confirmed."""
ent_6 = [
    {"label": "LATERALITY", **get_span(text_6, "right-sided", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "single-port thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Seven", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "talc poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": ent_6})

# ==========================================
# Note 7: 917337_syn_7
# ==========================================
id_7 = "917337_syn_7"
text_7 = """[Indication] Suspected mesothelioma.
[Anesthesia] Moderate sedation, local.
[Description] Right thoracoscopy performed. Findings: Diffuse pleural nodularity. Actions: 7 biopsies parietal pleura, plus diaphragmatic biopsies. Talc poudrage performed.
[Plan] Admit, chest tube to suction, path pending."""
ent_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "mesothelioma", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Right", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "pleural", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 2)},
    {"label": "PROC_ACTION", **get_span(text_7, "Talc poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": ent_7})

# ==========================================
# Note 8: 917337_syn_8
# ==========================================
id_8 = "917337_syn_8"
text_8 = """We performed a right medical thoracoscopy on [REDACTED]. Upon entering the pleural space, we observed diffuse nodularity throughout. We proceeded to obtain seven biopsies from the parietal pleura and additional samples from the diaphragm. Following the biopsies, we performed talc poudrage for pleurodesis. The fluid was evacuated and a chest tube was inserted."""
ent_8 = [
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "seven", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 2)},
    {"label": "PROC_ACTION", **get_span(text_8, "talc poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": ent_8})

# ==========================================
# Note 9: 917337_syn_9
# ==========================================
id_9 = "917337_syn_9"
text_9 = """Right pleuroscopy performed. Pleura demonstrated diffuse nodularity. Seven tissue samples harvested from the parietal wall, with additional sampling of the diaphragm. Talc insufflation executed for symphysis. Fluid drained and catheter inserted. Hemostasis secured."""
ent_9 = [
    {"label": "LATERALITY", **get_span(text_9, "Right", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "Pleura", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "nodularity", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Seven", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "tissue samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal wall", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Talc insufflation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Fluid drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "catheter", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": ent_9})

# ==========================================
# Note 10: 917337
# ==========================================
id_10 = "917337"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: LCDR John Park, MD
Fellow: Dr. Kevin Patel (PGY-5)

Indication: Suspected mesothelioma
Side: Right

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Diffuse pleural nodularity
Multiple biopsies obtained from parietal pleura (7 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
Given findings, talc poudrage performed for pleurodesis.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Park, MD"""
ent_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "mesothelioma", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Pleural Biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th intercostal space, mid-axillary line", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Semi-rigid pleuroscope", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "nodularity", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "7", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "diaphragmatic pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "talc poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "fluid evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 2)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": ent_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)