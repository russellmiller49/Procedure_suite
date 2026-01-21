import sys
from pathlib import Path

# Set up the repository root path
# This assumes the script is running within the structure: repo_root/scripts/add_case_script.py
# Adjust parents reference if the script depth changes.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1232915_syn_1
# ==========================================
text_1 = """Dx: Pleural nodularity.
Proc: Right Thoracoscopy + Biopsy + Talc.
- Inflammatory changes seen.
- 6 biopsies parietal pleura + diaphragm.
- Talc poudrage done.
- Chest tube to suction."""

entities_1 = [
    {"label": "ANAT_PLEURA",   **get_span(text_1, "Pleural", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "nodularity", 1)},
    {"label": "LATERALITY",    **get_span(text_1, "Right", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "Biopsy", 1)},
    {"label": "MEDICATION",    **get_span(text_1, "Talc", 1)},
    {"label": "OBS_FINDING",   **get_span(text_1, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_1, "6", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "biopsies", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_1, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_1, "diaphragm", 1)},
    {"label": "MEDICATION",    **get_span(text_1, "Talc", 2)},
    {"label": "PROC_ACTION",   **get_span(text_1, "poudrage", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_1, "Chest tube", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1232915_syn_2
# ==========================================
text_2 = """PROCEDURE RECORD: [REDACTED] a right-sided medical thoracoscopy. The indication was radiographic pleural nodularity. Intraoperative inspection revealed inflammatory changes lacking distinct nodularity, contrary to imaging. Nevertheless, six biopsies were harvested from the parietal pleura and additional tissue from the diaphragm to rule out occult disease. Talc poudrage was instilled to achieve pleurodesis. A chest tube was inserted."""

entities_2 = [
    {"label": "LATERALITY",    **get_span(text_2, "right-sided", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_2, "pleural", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "nodularity", 1)},
    {"label": "OBS_FINDING",   **get_span(text_2, "inflammatory changes", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "nodularity", 2)},
    {"label": "MEAS_COUNT",    **get_span(text_2, "six", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "biopsies", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_2, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_2, "diaphragm", 1)},
    {"label": "MEDICATION",    **get_span(text_2, "Talc", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "poudrage", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "pleurodesis", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_2, "chest tube", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1232915_syn_3
# ==========================================
text_3 = """CPT Justification:
- 32609: Thoracoscopy with biopsy (6 parietal samples obtained).
- 32650: Thoracoscopy with pleurodesis (Talc poudrage).
Site: [REDACTED]
Findings: Inflammatory changes.
Disposition: Inpatient."""

entities_3 = [
    {"label": "PROC_ACTION",   **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3, "biopsy", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_3, "6", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_3, "parietal", 1)},
    {"label": "SPECIMEN",      **get_span(text_3, "samples", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3, "Thoracoscopy", 2)},
    {"label": "PROC_ACTION",   **get_span(text_3, "pleurodesis", 1)},
    {"label": "MEDICATION",    **get_span(text_3, "Talc", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3, "poudrage", 1)},
    {"label": "OBS_FINDING",   **get_span(text_3, "Inflammatory changes", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1232915_syn_4
# ==========================================
text_4 = """Steps:
1. Right side prep.
2. Scope in 6th ICS.
3. Looked around: Inflammatory changes, no obvious nodules.
4. Took 6 biopsies anyway (parietal) + diaphragm.
5. Puffed Talc.
6. Chest tube in.
Res: Dr. Walsh."""

entities_4 = [
    {"label": "LATERALITY",    **get_span(text_4, "Right", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_4, "Scope", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_4, "6th ICS", 1)},
    {"label": "OBS_FINDING",   **get_span(text_4, "Inflammatory changes", 1)},
    {"label": "OBS_LESION",    **get_span(text_4, "nodules", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_4, "6", 2)},
    {"label": "PROC_ACTION",   **get_span(text_4, "biopsies", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_4, "parietal", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_4, "diaphragm", 1)},
    {"label": "MEDICATION",    **get_span(text_4, "Talc", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_4, "Chest tube", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1232915_syn_5
# ==========================================
text_5 = """[REDACTED] right thoracoscopy. indications were nodules on ct but inside it just looked inflammatory. we took biopsies anyway 6 from the wall and some from diaphragm. did the talc procedure just in case. chest tube placed to suction. no air leak hemostasis good."""

entities_5 = [
    {"label": "LATERALITY",    **get_span(text_5, "right", 1)},
    {"label": "PROC_ACTION",   **get_span(text_5, "thoracoscopy", 1)},
    {"label": "OBS_LESION",    **get_span(text_5, "nodules", 1)},
    {"label": "OBS_FINDING",   **get_span(text_5, "inflammatory", 1)},
    {"label": "PROC_ACTION",   **get_span(text_5, "biopsies", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_5, "6", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_5, "wall", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_5, "diaphragm", 1)},
    {"label": "MEDICATION",    **get_span(text_5, "talc", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_5, "chest tube", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1232915_syn_6
# ==========================================
text_6 = """Medical Thoracoscopy with Pleural Biopsy. Under moderate sedation, single-port entry at 6th intercostal space. Semi-rigid pleuroscope inserted. Findings: Inflammatory changes without nodularity. Multiple biopsies obtained from parietal pleura (6 specimens). Additional biopsies from diaphragmatic pleura. Given findings, talc poudrage performed for pleurodesis. Chest tube placed."""

entities_6 = [
    {"label": "PROC_ACTION",   **get_span(text_6, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_6, "Pleural", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "Biopsy", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_6, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_6, "Semi-rigid pleuroscope", 1)},
    {"label": "OBS_FINDING",   **get_span(text_6, "Inflammatory changes", 1)},
    {"label": "OBS_LESION",    **get_span(text_6, "nodularity", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_6, "parietal pleura", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_6, "6", 1)},
    {"label": "SPECIMEN",      **get_span(text_6, "specimens", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "biopsies", 2)},
    {"label": "ANAT_PLEURA",   **get_span(text_6, "diaphragmatic pleura", 1)},
    {"label": "MEDICATION",    **get_span(text_6, "talc", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "poudrage", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "pleurodesis", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_6, "Chest tube", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1232915_syn_7
# ==========================================
text_7 = """[Indication]
Pleural nodularity on imaging.
[Anesthesia]
Moderate.
[Description]
Right side. Findings: Inflammatory changes. Action: 6 parietal biopsies, diaphragm biopsy, Talc poudrage. Fluid evacuated.
[Plan]
Admit to floor. Suction."""

entities_7 = [
    {"label": "ANAT_PLEURA",   **get_span(text_7, "Pleural", 1)},
    {"label": "OBS_LESION",    **get_span(text_7, "nodularity", 1)},
    {"label": "LATERALITY",    **get_span(text_7, "Right", 1)},
    {"label": "OBS_FINDING",   **get_span(text_7, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_7, "6", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_7, "parietal", 1)},
    {"label": "PROC_ACTION",   **get_span(text_7, "biopsies", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_7, "diaphragm", 1)},
    {"label": "PROC_ACTION",   **get_span(text_7, "biopsy", 1)},
    {"label": "MEDICATION",    **get_span(text_7, "Talc", 1)},
    {"label": "PROC_ACTION",   **get_span(text_7, "poudrage", 1)},
    {"label": "SPECIMEN",      **get_span(text_7, "Fluid", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1232915_syn_8
# ==========================================
text_8 = """We carried out a right medical thoracoscopy on [REDACTED]. Although imaging suggested nodules, direct visualization showed mostly inflammatory changes. We proceeded to biopsy the parietal pleura six times and sampled the diaphragm as well. To manage the effusion, we performed talc poudrage. The chest tube was placed without complication, and the lung expanded well."""

entities_8 = [
    {"label": "LATERALITY",    **get_span(text_8, "right", 1)},
    {"label": "PROC_ACTION",   **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "nodules", 1)},
    {"label": "OBS_FINDING",   **get_span(text_8, "inflammatory changes", 1)},
    {"label": "PROC_ACTION",   **get_span(text_8, "biopsy", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_8, "parietal pleura", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_8, "six", 1)},
    {"label": "PROC_ACTION",   **get_span(text_8, "sampled", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_8, "diaphragm", 1)},
    {"label": "OBS_FINDING",   **get_span(text_8, "effusion", 1)},
    {"label": "MEDICATION",    **get_span(text_8, "talc", 1)},
    {"label": "PROC_ACTION",   **get_span(text_8, "poudrage", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_8, "chest tube", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1232915_syn_9
# ==========================================
text_9 = """Procedure: Pleuroscopy with Tissue Sampling and Sclerosant Administration.
Side: Right.
Findings: Phlegmonous/inflammatory changes.
Action: Acquired 6 parietal specimens. Instilled talc for pleurodesis. Drained effusion and sited chest catheter."""

entities_9 = [
    {"label": "PROC_ACTION",   **get_span(text_9, "Pleuroscopy", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "Tissue Sampling", 1)},
    {"label": "LATERALITY",    **get_span(text_9, "Right", 1)},
    {"label": "OBS_FINDING",   **get_span(text_9, "Phlegmonous", 1)},
    {"label": "OBS_FINDING",   **get_span(text_9, "inflammatory changes", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_9, "6", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_9, "parietal", 1)},
    {"label": "SPECIMEN",      **get_span(text_9, "specimens", 1)},
    {"label": "MEDICATION",    **get_span(text_9, "talc", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "pleurodesis", 1)},
    {"label": "OBS_FINDING",   **get_span(text_9, "effusion", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_9, "chest catheter", 1)},
]

BATCH_DATA.append({"id": "1232915_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1232915
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Mark Taylor
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Pleural nodularity on imaging
Side: Right

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Inflammatory changes without nodularity
Multiple biopsies obtained from parietal pleura (6 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
Given findings, talc poudrage performed for pleurodesis.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Taylor, MD"""

entities_10 = [
    {"label": "ANAT_PLEURA",   **get_span(text_10, "Pleural", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "nodularity", 1)},
    {"label": "LATERALITY",    **get_span(text_10, "Right", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_10, "Pleural", 2)},
    {"label": "PROC_ACTION",   **get_span(text_10, "Biopsy", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_10, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "Semi-rigid pleuroscope", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_10, "Pleural space", 1)},
    {"label": "OBS_FINDING",   **get_span(text_10, "Inflammatory changes", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "nodularity", 2)},
    {"label": "PROC_ACTION",   **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_PLEURA",   **get_span(text_10, "parietal pleura", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_10, "6", 2)},
    {"label": "SPECIMEN",      **get_span(text_10, "specimens", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_PLEURA",   **get_span(text_10, "diaphragmatic pleura", 1)},
    {"label": "MEDICATION",    **get_span(text_10, "talc", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "poudrage", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "pleurodesis", 1)},
    {"label": "SPECIMEN",      **get_span(text_10, "fluid", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_10, "Chest tube", 1)},
    {"label": "DEV_CATHETER",  **get_span(text_10, "Chest tube", 2)},
]

BATCH_DATA.append({"id": "1232915", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)