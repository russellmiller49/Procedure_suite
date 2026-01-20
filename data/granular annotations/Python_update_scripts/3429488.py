import sys
from pathlib import Path

# Set up the repository root (assuming this script is inside a subdirectory like 'scripts/')
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 3429488_syn_1
# ==========================================
id_1 = "3429488_syn_1"
text_1 = """Pre-op: Lung Ca staging. Right side.
Proc: Thoracoscopy + Biopsy + Talc.
- 6th ICS entry.
- Findings: Thickened parietal pleura, nodules.
- Action: 6 biopsies taken. Talc poudrage performed.
- Chest tube placed.
Plan: Admit. Path pending."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Lung Ca", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Right side", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Talc", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "6th ICS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Talc", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 3429488_syn_2
# ==========================================
id_2 = "3429488_syn_2"
text_2 = """OPERATIVE NARRATIVE: The patient was brought to the endoscopy suite for right-sided medical thoracoscopy to assess for pleural carcinomatosis. Under moderate sedation, the pleural space was accessed via the 6th intercostal space. Inspection revealed significant parietal pleural thickening with distinct nodularity. Extensive biopsies were harvested from the parietal surface (six specimens) and the diaphragm. Given the macroscopic appearance suggestive of malignancy, talc poudrage was instigated for pleurodesis. The procedure concluded with chest tube placement; hemostasis was secured."""
entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "right-sided", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "medical thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "pleural carcinomatosis", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleural", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "thickening", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodularity", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal surface", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "six", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "diaphragm", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignancy", 1)},
    {"label": "MEDICATION", **get_span(text_2, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "hemostasis was secured", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 3429488_syn_3
# ==========================================
id_3 = "3429488_syn_3"
text_3 = """Procedure: Thoracoscopy, surgical; with biopsy of pleura (32609) and with pleurodesis (32650).
Site: [REDACTED]
Technique: Single port access. Semi-rigid pleuroscope utilized.
Intervention: Directed biopsy of thickened parietal pleura (6 samples) and diaphragmatic pleura. Talc insufflation performed for chemical pleurodesis based on findings.
Device: 24Fr chest tube placed."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleurodesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Single port access", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Semi-rigid pleuroscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 2)},
    {"label": "OBS_FINDING", **get_span(text_3, "thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "6", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "diaphragmatic pleura", 1)},
    {"label": "MEDICATION", **get_span(text_3, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "insufflation", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleurodesis", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "24Fr chest tube", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 3429488_syn_4
# ==========================================
id_4 = "3429488_syn_4"
text_4 = """Procedure Note
Patient: 79F
Procedure: Right Medical Thoracoscopy w/ Biopsy & Talc
Attending: Dr. Williams
Steps:
1. Timeout.
2. Local + Moderate Sedation.
3. Trocar entry 6th ICS.
4. Survey: Nodules on parietal pleura.
5. Biopsied parietal (x6) and diaphragm.
6. Talc poudrage.
7. Chest tube secured."""
entities_4 = [
    {"label": "LATERALITY", **get_span(text_4, "Right", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Talc", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Trocar", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "6th ICS", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "parietal", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "6", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Talc", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 3429488_syn_5
# ==========================================
id_5 = "3429488_syn_5"
text_5 = """pt [REDACTED] for staging lung ca right side. we did the thoracoscopy under sedation entered at the 6th rib space. saw thickened pleura and nodules took about 6 biopsies from the wall and some from the diaphragm. looked malignant so we did the talc poudrage right then. put a chest tube in no air leak. admitting to floor for pain control and tube management."""
entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "lung ca", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right side", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "6th rib space", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "wall", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "diaphragm", 1)},
    {"label": "MEDICATION", **get_span(text_5, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no air leak", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 3429488_syn_6
# ==========================================
id_6 = "3429488_syn_6"
text_6 = """Medical Thoracoscopy with Pleural Biopsy and Talc Poudrage. Under moderate sedation with local anesthesia, a single-port entry was made at the 6th intercostal space, mid-axillary line. The semi-rigid pleuroscope was inserted. Inspection revealed thickened parietal pleura with nodules. Multiple biopsies were obtained from the parietal pleura (6 specimens) and diaphragmatic pleura. Specimens were sent for histopathology. Talc poudrage was performed for pleurodesis. All fluid was evacuated and a chest tube was placed."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "Pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Biopsy", 1)},
    {"label": "MEDICATION", **get_span(text_6, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Poudrage", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "single-port entry", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "semi-rigid pleuroscope", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 2)},
    {"label": "MEAS_COUNT", **get_span(text_6, "6", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "diaphragmatic pleura", 1)},
    {"label": "MEDICATION", **get_span(text_6, "Talc", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 3429488_syn_7
# ==========================================
id_7 = "3429488_syn_7"
text_7 = """[Indication]
Staging for lung cancer pleural involvement.
[Anesthesia]
Moderate sedation, local anesthesia.
[Description]
Right-sided entry (6th ICS). Findings: Thickened parietal pleura with nodules. Interventions: Parietal biopsies (6), diaphragmatic biopsies, Talc poudrage pleurodesis. Chest tube placed.
[Plan]
Admit. Oncology consult if pos."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "lung cancer", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "pleural", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Right-sided", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "6th ICS", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "Parietal", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "6", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 2)},
    {"label": "MEDICATION", **get_span(text_7, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 3429488_syn_8
# ==========================================
id_8 = "3429488_syn_8"
text_8 = """The patient underwent a right-sided medical thoracoscopy for staging purposes. Upon entering the pleural space through the sixth intercostal space, we observed thickened parietal pleura studded with nodules. We proceeded to take multiple biopsies, specifically six from the parietal pleura and additional samples from the diaphragm. Due to the high suspicion of malignancy, we performed a talc poudrage to prevent fluid recurrence. The lung was re-expanded, and a chest tube was secured."""
entities_8 = [
    {"label": "LATERALITY", **get_span(text_8, "right-sided", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "sixth intercostal space", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "six", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal pleura", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "diaphragm", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "malignancy", 1)},
    {"label": "MEDICATION", **get_span(text_8, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "poudrage", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_8, "lung was re-expanded", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 3429488_syn_9
# ==========================================
id_9 = "3429488_syn_9"
text_9 = """Procedure: Medical Thoracoscopy with Pleural Sampling and Pleurodesis.
Site: [REDACTED]
Findings: Indurated parietal pleura with nodularity.
Actions: Sampled parietal pleura (6 fragments) and diaphragmatic surface. Administered talc poudrage for symphysis. Evacuated effusion. Anchored chest drain."""
entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "Pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Sampling", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Pleurodesis", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Indurated", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodularity", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Sampled", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal pleura", 2)},
    {"label": "MEAS_COUNT", **get_span(text_9, "6", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "diaphragmatic surface", 1)},
    {"label": "MEDICATION", **get_span(text_9, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "chest drain", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 3429488
# ==========================================
id_10 = "3429488"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams
Fellow: LT Michelle Torres, MD (PGY-5)

Indication: Staging for lung cancer pleural involvement
Side: Right

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Thickened parietal pleura with nodules
Multiple biopsies obtained from parietal pleura (6 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
Given findings, talc poudrage performed for pleurodesis.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Williams, MD"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "lung cancer", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Single-port entry", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Semi-rigid pleuroscope", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "diaphragmatic pleura", 1)},
    {"label": "MEDICATION", **get_span(text_10, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No air leak", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 2)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)