import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the system path to allow imports
sys.path.append(str(REPO_ROOT))

# Import the utility function from the provided script
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The term to search for.
        occurrence (int): The specific occurrence to find (1-based index).
        
    Returns:
        tuple: (start_index, end_index)
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
    
    if start != -1:
        return start, start + len(term)
    else:
        # Fallback to prevent silent errors, though strict offset protocol should be followed
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")

# ==========================================
# Note 1: 1269056_syn_1
# ==========================================
t1 = """Proc: Lt Thoracoscopy w/ Biopsy & Talc.
Findings: Visceral tumor implants.
Actions:
- 11 biopsies parietal pleura.
- Diaphragmatic biopsies.
- Talc poudrage.
- Tube placed.
Status: No leak."""

e1 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t1, "Lt", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "Thoracoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "Biopsy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "Talc", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t1, "Visceral", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t1, "tumor implants", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t1, "11", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t1, "parietal pleura", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t1, "Diaphragmatic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "biopsies", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "Talc poudrage", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t1, "Tube", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "placed", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t1, "No leak", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1269056_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: Left-sided medical thoracoscopy revealed tumor implants on the visceral pleura. Eleven biopsies were obtained from the parietal pleura, along with diaphragmatic sampling. Talc poudrage was utilized for pleurodesis. Fluid was evacuated and a chest tube positioned."""

e2 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t2, "Left-sided", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "medical thoracoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t2, "tumor implants", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t2, "visceral pleura", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t2, "Eleven", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t2, "parietal pleura", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t2, "diaphragmatic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "sampling", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "Talc poudrage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "pleurodesis", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t2, "Fluid", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "evacuated", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t2, "chest tube", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "positioned", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1269056_syn_3
# ==========================================
t3 = """Billing: 32609 (Biopsy) & 32650 (Talc).
Site: [REDACTED]
Details: Visceral implants seen. 11 parietal biopsies taken. Diaphragmatic biopsies taken. Talc poudrage performed. Chest tube placed."""

e3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "Biopsy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "Talc", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t3, "Visceral", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t3, "implants", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t3, "11", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t3, "parietal", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t3, "Diaphragmatic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "biopsies", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "Talc poudrage", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t3, "Chest tube", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "placed", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1269056_syn_4
# ==========================================
t4 = """Resident Note: Left Thoracoscopy
Steps:
1. Sedation.
2. Entry left 6th ICS.
3. Findings: Tumor implants.
4. Biopsies: 11 parietal + diaphragm.
5. Talc poudrage.
6. Chest tube placed.
Plan: Admit."""

e4 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t4, "Left", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "Thoracoscopy", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t4, "left 6th ICS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t4, "Tumor implants", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "Biopsies", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t4, "11", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t4, "parietal", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t4, "diaphragm", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "Talc poudrage", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t4, "Chest tube", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "placed", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1269056_syn_5
# ==========================================
t5 = """left thoracoscopy on kathleen saw tumor implants took 11 biopsies from parietal pleura and some from diaphragm did talc poudrage drained the fluid put the chest tube in"""

e5 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t5, "left", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "thoracoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t5, "tumor implants", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t5, "11", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t5, "parietal pleura", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t5, "diaphragm", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "talc poudrage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "drained", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t5, "fluid", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t5, "chest tube", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1269056_syn_6
# ==========================================
t6 = """Left medical thoracoscopy was performed. Visceral pleural tumor implants were visualized. Eleven biopsies were obtained from the parietal pleura, along with diaphragmatic biopsies. Talc poudrage was performed for pleurodesis. Fluid was evacuated and a chest tube was placed."""

e6 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t6, "Left", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "medical thoracoscopy", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t6, "Visceral pleural", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t6, "tumor implants", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t6, "Eleven", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t6, "parietal pleura", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t6, "diaphragmatic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "biopsies", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "Talc poudrage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "pleurodesis", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t6, "Fluid", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "evacuated", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t6, "chest tube", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "placed", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1269056_syn_7
# ==========================================
t7 = """[Indication] Persistent effusion.
[Anesthesia] Moderate.
[Description] Left thoracoscopy. Visceral tumor implants. 11 parietal biopsies. Diaphragmatic biopsies. Talc poudrage.
[Plan] Path results."""

e7 = [
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t7, "Persistent effusion", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t7, "Left", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "thoracoscopy", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t7, "Visceral", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t7, "tumor implants", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t7, "11", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t7, "parietal", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t7, "Diaphragmatic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "biopsies", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "Talc poudrage", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1269056_syn_8
# ==========================================
t8 = """We performed a left medical thoracoscopy on [REDACTED]. We observed visceral pleural tumor implants. We collected eleven biopsies from the parietal pleura and additional samples from the diaphragm. We then performed talc poudrage for pleurodesis and placed a chest tube."""

e8 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t8, "left", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "medical thoracoscopy", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t8, "visceral pleural", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t8, "tumor implants", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t8, "eleven", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t8, "parietal pleura", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "samples", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t8, "diaphragm", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "talc poudrage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "pleurodesis", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "placed", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t8, "chest tube", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1269056_syn_9
# ==========================================
t9 = """Left pleuroscopy performed. Visceral tumor implants observed. Eleven tissue samples harvested from parietal pleura; diaphragm also sampled. Talc insufflation executed. Fluid drained and catheter deployed."""

e9 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t9, "Left", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "pleuroscopy", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t9, "Visceral", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t9, "tumor implants", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t9, "Eleven", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t9, "tissue samples", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "harvested", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t9, "parietal pleura", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t9, "diaphragm", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "sampled", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "Talc insufflation", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t9, "Fluid", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "drained", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t9, "catheter", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "deployed", 1)))},
]
BATCH_DATA.append({"id": "1269056_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1269056
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams

Indication: Persistent effusion despite thoracentesis
Side: Left

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Visceral pleural tumor implants
Multiple biopsies obtained from parietal pleura (11 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
Given findings, talc poudrage performed for pleurodesis.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Williams, MD"""

e10 = [
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "Persistent effusion", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "thoracentesis", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(t10, "Left", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "Medical Thoracoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "Pleural Biopsy", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t10, "Single", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t10, "6th intercostal space", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t10, "mid-axillary line", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "Semi-rigid pleuroscope", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "inserted", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t10, "Pleural space", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "inspected", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t10, "Visceral pleural", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "tumor implants", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "biopsies", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t10, "parietal pleura", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t10, "11", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t10, "specimens", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "biopsies", 2)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(t10, "diaphragmatic pleura", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t10, "Specimens", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "talc poudrage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "pleurodesis", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(t10, "fluid", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "evacuated", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t10, "Chest tube", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "placed", 1)))},
    {"label": "OBS_FINDING", **dict(zip(["start", "end"], get_span(t10, "No air leak", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(t10, "Chest tube", 2)))},
]
BATCH_DATA.append({"id": "1269056", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)