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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a term in the text.
    Ensures strict case-sensitive matching as per protocol.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# 3. Data Definitions
# ==========================================

# --- Case: 3071562_syn_1 ---
text_3071562_syn_1 = """Proc: Rt Thoracoscopy, Biopsy, Pleurodesis.
Findings: Mass on diaphragmatic pleura.
Actions:
- 12 biopsies parietal pleura.
- Diaphragmatic biopsies.
- Talc poudrage.
- Tube placed.
Status: Hemostasis confirmed."""
entities_3071562_syn_1 = [
    {"label": "LATERALITY", **get_span(text_3071562_syn_1, "Rt", 1)},
    {"label": "PROC_METHOD", **get_span(text_3071562_syn_1, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_1, "Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_1, "Pleurodesis", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_1, "Mass", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_1, "diaphragmatic pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_1, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_1, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_1, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_1, "biopsies", 2)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_1, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_1, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_1, "Tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_1, "placed", 1)},
    {"label": "OBS_FINDING", **get_span(text_3071562_syn_1, "Hemostasis", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_1", "text": text_3071562_syn_1, "entities": entities_3071562_syn_1})

# --- Case: 3071562_syn_2 ---
text_3071562_syn_2 = """OPERATIVE REPORT: The patient underwent a right medical thoracoscopy for staging. A distinct mass lesion was id[REDACTED] on the diaphragmatic pleura. Twelve biopsies were excised from the parietal pleura, with additional targeted sampling of the diaphragmatic mass. Given the findings, palliative pleurodesis was induced via talc poudrage. The hemithorax was drained and a chest tube inserted."""
entities_3071562_syn_2 = [
    {"label": "PROC_METHOD", **get_span(text_3071562_syn_2, "medical thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "staging", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_2, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_2, "lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_2, "diaphragmatic pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_2, "Twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "excised", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_2, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "sampling", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_2, "mass", 2)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "pleurodesis", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_2, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_2, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_2, "inserted", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_2", "text": text_3071562_syn_2, "entities": entities_3071562_syn_2})

# --- Case: 3071562_syn_3 ---
text_3071562_syn_3 = """Coding: 32609 (Biopsy) & 32650 (Talc Pleurodesis).
Site: [REDACTED]
Details: Mass visualized. 12 parietal biopsies obtained. Diaphragmatic biopsies obtained. Talc insufflated for pleurodesis due to malignant appearance. Chest tube placed for drainage."""
entities_3071562_syn_3 = [
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_3, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "Pleurodesis", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_3, "Mass", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_3, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "obtained", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "biopsies", 2)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "obtained", 2)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_3, "Talc", 2)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "insufflated", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "pleurodesis", 1)}, # Corrected from 2 to 1 (case sensitive: 'Pleurodesis' vs 'pleurodesis')
    {"label": "OBS_ROSE", **get_span(text_3071562_syn_3, "malignant", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_3, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_3, "placed", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_3", "text": text_3071562_syn_3, "entities": entities_3071562_syn_3})

# --- Case: 3071562_syn_4 ---
text_3071562_syn_4 = """Procedure: Right Thoracoscopy + Biopsy + Talc
Steps:
1. Sedation start.
2. Entry right 6th ICS.
3. Findings: Diaphragmatic mass.
4. Biopsies: 12 parietal + diaphragm.
5. Intervention: Talc poudrage.
6. Tube placed.
Plan: Admit."""
entities_3071562_syn_4 = [
    {"label": "LATERALITY", **get_span(text_3071562_syn_4, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_3071562_syn_4, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_4, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_4, "Talc", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_4, "Sedation", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_4, "6th ICS", 1)}, 
    {"label": "OBS_LESION", **get_span(text_3071562_syn_4, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_4, "Biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_4, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_4, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_4, "Talc", 2)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_4, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_4, "Tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_4, "placed", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_4", "text": text_3071562_syn_4, "entities": entities_3071562_syn_4})

# --- Case: 3071562_syn_5 ---
text_3071562_syn_5 = """S: 65yo M with pleural effusion.
O: Right Medical Thoracoscopy.
- Pleura: Nodular diaphragmatic disease.
- Sampling: 12 bites parietal pleura.
- Interventions: Talc slurry insufflation. 24Fr chest tube placed.
A: Successful dx/therapeutic procedure.
P: Recover."""
entities_3071562_syn_5 = [
    {"label": "OBS_FINDING", **get_span(text_3071562_syn_5, "pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(text_3071562_syn_5, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_3071562_syn_5, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_5, "Pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_5, "Sampling", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_5, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_5, "parietal pleura", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_5, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_5, "insufflation", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3071562_syn_5, "24Fr chest tube", 1)}, 
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_5, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_5, "placed", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_5", "text": text_3071562_syn_5, "entities": entities_3071562_syn_5})

# --- Case: 3071562_syn_6 ---
text_3071562_syn_6 = """PREOPERATIVE DIAGNOSIS: Right pleural effusion, suspicious for malignancy.
PROCEDURE: Right medical thoracoscopy, parietal pleural biopsy x12, talc pleurodesis.
FINDINGS: The right lung was collapsed. A large mass was noted on the diaphragm.
The parietal pleura appeared relatively normal but was biopsied 12 times for staging.
Talc was administered. A chest drain was secured."""
entities_3071562_syn_6 = [
    {"label": "LATERALITY", **get_span(text_3071562_syn_6, "Right", 1)},
    {"label": "OBS_FINDING", **get_span(text_3071562_syn_6, "pleural effusion", 1)},
    {"label": "OBS_ROSE", **get_span(text_3071562_syn_6, "malignancy", 1)},
    {"label": "LATERALITY", **get_span(text_3071562_syn_6, "Right", 2)},
    {"label": "PROC_METHOD", **get_span(text_3071562_syn_6, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_6, "parietal pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_6, "biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_6, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_6, "pleurodesis", 1)},
    {"label": "LATERALITY", **get_span(text_3071562_syn_6, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3071562_syn_6, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_6, "mass", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_6, "diaphragm", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_6, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_6, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_6, "staging", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_6, "Talc", 1)}, 
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_6, "chest drain", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_6", "text": text_3071562_syn_6, "entities": entities_3071562_syn_6})

# --- Case: 3071562_syn_7 ---
text_3071562_syn_7 = """Dr. Martinez performed a right medical thoracoscopy on [REDACTED]. We visualized a mass on the diaphragmatic pleura. To ensure accurate staging, we took twelve biopsies from the parietal pleura and additional samples from the diaphragm. Given the appearance, we proceeded with talc poudrage for pleurodesis before placing the chest tube."""
entities_3071562_syn_7 = [
    {"label": "LATERALITY", **get_span(text_3071562_syn_7, "right", 1)},
    {"label": "PROC_METHOD", **get_span(text_3071562_syn_7, "medical thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_7, "mass", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_7, "diaphragmatic pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_7, "staging", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_7, "twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_7, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_7, "parietal pleura", 1)},
    {"label": "SPECIMEN", **get_span(text_3071562_syn_7, "samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_7, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_7, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_7, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_7, "pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_7, "placing", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_7, "chest tube", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_7", "text": text_3071562_syn_7, "entities": entities_3071562_syn_7})

# --- Case: 3071562_syn_8 ---
text_3071562_syn_8 = """Right pleuroscopy completed. Diaphragmatic mass observed. Twelve tissue samples harvested from parietal pleura; diaphragm also sampled. Talc insufflation executed for symphysis. Fluid drained and catheter deployed."""
entities_3071562_syn_8 = [
    {"label": "LATERALITY", **get_span(text_3071562_syn_8, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_3071562_syn_8, "pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_8, "Diaphragmatic", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562_syn_8, "mass", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562_syn_8, "Twelve", 1)},
    {"label": "SPECIMEN", **get_span(text_3071562_syn_8, "tissue samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_8, "harvested", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_8, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562_syn_8, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_8, "sampled", 1)},
    {"label": "MEDICATION", **get_span(text_3071562_syn_8, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_8, "insufflation", 1)},
    {"label": "OBS_FINDING", **get_span(text_3071562_syn_8, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_8, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562_syn_8, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562_syn_8, "deployed", 1)},
]
BATCH_DATA.append({"id": "3071562_syn_8", "text": text_3071562_syn_8, "entities": entities_3071562_syn_8})

# --- Case: 3071562 ---
text_3071562 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Robert Martinez

Indication: Staging for lung cancer pleural involvement
Side: Right

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Mass lesion on diaphragmatic pleura
Multiple biopsies obtained from parietal pleura (12 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
Given findings, talc poudrage performed for pleurodesis.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant."""
entities_3071562 = [
    {"label": "PROC_ACTION", **get_span(text_3071562, "Staging", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3071562, "lung", 1)},
    {"label": "LATERALITY", **get_span(text_3071562, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_3071562, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562, "Pleural", 2)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_3071562, "sedation", 1)},
    {"label": "MEDICATION", **get_span(text_3071562, "local anesthesia", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562, "mid-axillary line", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3071562, "pleuroscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "inserted", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562, "Pleural space", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562, "Mass", 1)},
    {"label": "OBS_LESION", **get_span(text_3071562, "lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562, "diaphragmatic pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "obtained", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3071562, "12", 1)},
    {"label": "SPECIMEN", **get_span(text_3071562, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_3071562, "diaphragmatic pleura", 2)},
    {"label": "SPECIMEN", **get_span(text_3071562, "Specimens", 1)},
    {"label": "MEDICATION", **get_span(text_3071562, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "pleurodesis", 1)},
    {"label": "OBS_FINDING", **get_span(text_3071562, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "placed", 1)},
    {"label": "OBS_FINDING", **get_span(text_3071562, "Hemostasis", 1)},
    {"label": "OBS_FINDING", **get_span(text_3071562, "air leak", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3071562, "Chest tube", 2)},
    {"label": "PROC_ACTION", **get_span(text_3071562, "suction", 1)},
    {"label": "CTX_TIME", **get_span(text_3071562, "5-7 days", 1)},
    {"label": "OBS_ROSE", **get_span(text_3071562, "malignant", 1)},
]
BATCH_DATA.append({"id": "3071562", "text": text_3071562, "entities": entities_3071562})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)