import sys
from pathlib import Path

# Add the repository root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Strictly case-sensitive to ensure exact substring matching.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 12345_syn_1
# ==========================================
text_1 = """Indication: Undiagnosed right effusion.
Procedure: Medical Thoracoscopy.
- Local + MAC.
- 1.5L bloody fluid drained.
- Findings: Diffuse parietal nodules.
- Biopsy x6.
- Talc poudrage (4g).
- 24Fr chest tube.
Dx: Suspicious for Mesothelioma.
Plan: Admit."""

entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Medical Thoracoscopy", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "1.5L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bloody", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "poudrage", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
]
BATCH_DATA.append({"id": "12345_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 12345_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: Medical Thoracoscopy. The patient was positioned in the left lateral decubitus position. Following induction of MAC, a trocar was introduced into the right 5th intercostal space. Thoracoscopic inspection revealed hemorrhagic effusion (1.5L evacuated) and extensive nodularity of the parietal pleura, sparing the visceral surface. Multiple parietal pleural biopsies were obtained. To prevent recurrence, talc poudrage was performed under direct vision. A chest tube was placed. Clinical impression suggests mesothelioma."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Medical Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_2, "left", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "trocar", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "5th intercostal space", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Thoracoscopic", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "hemorrhagic", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "effusion", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "1.5L", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodularity", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "visceral surface", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_2, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
]
BATCH_DATA.append({"id": "12345_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 12345_syn_3
# ==========================================
text_3 = """Code: 32650 (Thoracoscopy, surgical; with pleurodesis).
Rationale:
- Method: Surgical thoracoscopy (VATS/Medical Thoracoscopy).
- Therapeutic Agent: Talc poudrage insufflated for pleurodesis.
- Bundling: Biopsies (32602) are typically bundled into the comprehensive pleurodesis code when performed in the same session for the same pathology."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "surgical", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleurodesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Surgical thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "VATS", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Medical Thoracoscopy", 1)},
    {"label": "MEDICATION", **get_span(text_3, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleurodesis", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleurodesis", 3)},
]
BATCH_DATA.append({"id": "12345_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 12345_syn_4
# ==========================================
text_4 = """Procedure: Pleuroscopy / Talc
Patient: [REDACTED]:
1. MAC sedation. Local.
2. Trocar in.
3. Suctioned 1.5L bloody fluid.
4. Saw nodules all over chest wall.
5. Grabbed biopsies x6.
6. Sprayed talc (4g).
7. Chest tube in.
Plan: Wait for path."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Pleuroscopy", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Talc", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Trocar", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "1.5L", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "bloody", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "chest wall", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x6", 1)},
    {"label": "MEDICATION", **get_span(text_4, "talc", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "12345_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 12345_syn_5
# ==========================================
text_5 = """Thoracoscopy note for Greg MRN [REDACTED]. Right effusion. Went in with the scope found bloody fluid and nodules everywhere on the parietal pleura. Looks like mesothelioma. Took a bunch of biopsies. Sprayed talc for pleurodesis. Put a tube in. Admitting him."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_5, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "effusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "bloody", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_5, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "tube", 1)},
]
BATCH_DATA.append({"id": "12345_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 12345_syn_6
# ==========================================
text_6 = """Medical thoracoscopy right. Patient 50M. Undiagnosed effusion. 1.5L hemorrhagic fluid drained. Diffuse parietal pleural nodules visualized. Biopsies performed. Talc poudrage pleurodesis performed. 24Fr chest tube placed. Diagnosis suspicious for mesothelioma. Disposition admission."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Medical thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_6, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "effusion", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "1.5L", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "hemorrhagic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_6, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "pleurodesis", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_6, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
]
BATCH_DATA.append({"id": "12345_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 12345_syn_7
# ==========================================
text_7 = """[Indication]
Undiagnosed right pleural effusion.
[Anesthesia]
MAC + Local.
[Description]
Trocar entry. Drainage of 1.5L bloody fluid. Parietal nodules biopsied. Talc poudrage (4g) administered. Chest tube placed.
[Plan]
Admit, Oncology consult."""

entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "pleural effusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Trocar", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "1.5L", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "bloody", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "Parietal", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsied", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "12345_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 12345_syn_8
# ==========================================
text_8 = """We performed a medical thoracoscopy on Greg to investigate his pleural effusion. After draining a large amount of bloody fluid, we saw many nodules lining the chest wall. We took several biopsies of these nodules. To stop the fluid from coming back, we sprayed sterile talc into the chest cavity. A chest tube was left in place to drain any remaining fluid."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "pleural effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "bloody", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "chest wall", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 2)},
    {"label": "MEDICATION", **get_span(text_8, "talc", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "chest cavity", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "12345_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 12345_syn_9
# ==========================================
text_9 = """Procedure: Thoracoscopic exploration with pleurodesis.
Action: The pleural space was accessed. Hemorrhagic fluid was evacuated. Nodular pathology on the parietal surface was sampled. A sclerosing agent (talc) was insufflated. A drainage catheter was sited.
Result: Tissue obtained; symphysis attempted."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "pleurodesis", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Hemorrhagic", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Nodular", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal surface", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampled", 1)},
    {"label": "MEDICATION", **get_span(text_9, "talc", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "drainage catheter", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "Tissue", 1)},
]
BATCH_DATA.append({"id": "12345_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 12345
# ==========================================
text_10 = """PROCEDURE: Medical Thoracoscopy (Right)
DATE: [REDACTED]
PHYSICIAN: Dr. House
PATIENT: [REDACTED] (MRN [REDACTED])

Indication: Undiagnosed right pleural effusion.

Local anesthesia + MAC. Pt in LLD. Trocar inserted 5th ICS. 1.5L bloody fluid removed. Inspection showed diffuse nodules on parietal pleura. Visceral pleura appeared normal. 
Biopsies taken x 6 from parietal pleura. 
Talc poudrage (4g) performed for pleurodesis. 
24Fr Chest tube placed. 

Dx: Suspicious for Mesothelioma.
Plan: Admit."""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Trocar", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "5th ICS", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "1.5L", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "bloody", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Visceral pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x 6", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 2)},
    {"label": "MEDICATION", **get_span(text_10, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "pleurodesis", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_10, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "12345", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)