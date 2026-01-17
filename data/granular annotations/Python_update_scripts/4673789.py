import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return start, start + len(term)

# ==========================================
# Note 1: 4673789_syn_1
# ==========================================
text_1 = """Indication: Iatrogenic Pneumothorax.
Procedure: Chest Tube (Right).
Size: 24Fr.
Findings: Air rush. Tube fogging.
Plan: ICU. Suction."""

entities_1 = [
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_1, "Pneumothorax", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_1, "Chest Tube", 1)))},
    {"label": "LATERALITY",        **dict(zip(["start", "end"], get_span(text_1, "Right", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_1, "24Fr", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_1, "Air rush", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_1, "Tube fogging", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4673789_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: Emergent Tube Thoracostomy.
[REDACTED] iatrogenic pneumothorax post-procedure. A 24Fr chest tube was inserted into the right 5th intercostal space using blunt dissection. A significant rush of air was appreciated upon pleural entry, and the tube demonstrated fogging with respiration. The tube was secured and placed to suction."""

entities_2 = [
    {"label": "PROC_ACTION",       **dict(zip(["start", "end"], get_span(text_2, "Tube Thoracostomy", 1)))},
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_2, "pneumothorax", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_2, "24Fr", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_2, "chest tube", 1)))},
    {"label": "LATERALITY",        **dict(zip(["start", "end"], get_span(text_2, "right", 1)))},
    {"label": "ANAT_PLEURA",       **dict(zip(["start", "end"], get_span(text_2, "5th intercostal space", 1)))},
    {"label": "PROC_METHOD",       **dict(zip(["start", "end"], get_span(text_2, "blunt dissection", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_2, "rush of air", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_2, "tube", 2)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_2, "fogging", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4673789_syn_3
# ==========================================
text_3 = """CPT 32551: Tube thoracostomy.
Indication: Pneumothorax (Air).
Technique: Blunt dissection.
Verification: Air rush, condensation, CXR confirmation.
Location: [REDACTED]"""

entities_3 = [
    {"label": "PROC_ACTION",       **dict(zip(["start", "end"], get_span(text_3, "Tube thoracostomy", 1)))},
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_3, "Pneumothorax", 1)))},
    {"label": "PROC_METHOD",       **dict(zip(["start", "end"], get_span(text_3, "Blunt dissection", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_3, "Air rush", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_3, "condensation", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4673789_syn_4
# ==========================================
text_4 = """Procedure: Chest Tube for PTX
Patient: [REDACTED]
Steps:
1. Stat prep.
2. 5th ICS anterior axillary.
3. Dissection.
4. 24Fr tube in.
5. Air rush confirmed.
Plan: ICU."""

entities_4 = [
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_4, "Chest Tube", 1)))},
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_4, "PTX", 1)))},
    {"label": "ANAT_PLEURA",       **dict(zip(["start", "end"], get_span(text_4, "5th ICS", 1)))},
    {"label": "ANAT_PLEURA",       **dict(zip(["start", "end"], get_span(text_4, "anterior axillary", 1)))},
    {"label": "PROC_METHOD",       **dict(zip(["start", "end"], get_span(text_4, "Dissection", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_4, "24Fr", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_4, "tube", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_4, "Air rush", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4673789_syn_5
# ==========================================
text_5 = """stat chest tube for mr [REDACTED] he had a pneumo after the procedure put a 24 french in the right side heard the air whoosh out hooked it up to the atrium box patient stable now going to icu."""

entities_5 = [
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_5, "chest tube", 1)))},
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_5, "pneumo", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_5, "24 french", 1)))},
    {"label": "LATERALITY",        **dict(zip(["start", "end"], get_span(text_5, "right", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_5, "air whoosh", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_5, "atrium box", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4673789_syn_6
# ==========================================
text_6 = """Tube thoracostomy was performed for right pneumothorax. The chest wall was prepped. A 24Fr tube was inserted via blunt dissection. Air release was noted. The tube was connected to a drainage system at -20cmH2O."""

entities_6 = [
    {"label": "PROC_ACTION",       **dict(zip(["start", "end"], get_span(text_6, "Tube thoracostomy", 1)))},
    {"label": "LATERALITY",        **dict(zip(["start", "end"], get_span(text_6, "right", 1)))},
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_6, "pneumothorax", 1)))},
    {"label": "ANAT_PLEURA",       **dict(zip(["start", "end"], get_span(text_6, "chest wall", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_6, "24Fr", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_6, "tube", 1)))},
    {"label": "PROC_METHOD",       **dict(zip(["start", "end"], get_span(text_6, "blunt dissection", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_6, "Air release", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_6, "tube", 2)))},
    {"label": "MEAS_PRESS",        **dict(zip(["start", "end"], get_span(text_6, "-20cmH2O", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4673789_syn_7
# ==========================================
text_7 = """[Indication]
Iatrogenic PTX.
[Anesthesia]
Local.
[Description]
Right tube thoracostomy (24Fr). Air rush noted.
[Plan]
ICU admission."""

entities_7 = [
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_7, "PTX", 1)))},
    {"label": "LATERALITY",        **dict(zip(["start", "end"], get_span(text_7, "Right", 1)))},
    {"label": "PROC_ACTION",       **dict(zip(["start", "end"], get_span(text_7, "tube thoracostomy", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_7, "24Fr", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_7, "Air rush", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4673789_syn_8
# ==========================================
text_8 = """[REDACTED] a collapsed lung after his earlier procedure. We immediately placed a chest tube on his right side to re-expand the lung. We heard the air escape as we put the tube in. He is now being monitored in the ICU with the tube on suction."""

entities_8 = [
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_8, "collapsed lung", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_8, "chest tube", 1)))},
    {"label": "LATERALITY",        **dict(zip(["start", "end"], get_span(text_8, "right", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_8, "air escape", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_8, "tube", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_8, "tube", 2)))},
]
BATCH_DATA.append({"id": "4673789_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4673789_syn_9
# ==========================================
text_9 = """Procedure: Thoracostomy for pneumothorax.
Etiology: Iatrogenic.
Confirmation: Auditory air escape and tube condensation.
Device: 24Fr catheter.
Disposition: Intensive care monitoring."""

entities_9 = [
    {"label": "PROC_ACTION",       **dict(zip(["start", "end"], get_span(text_9, "Thoracostomy", 1)))},
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_9, "pneumothorax", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_9, "Auditory air escape", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_9, "tube condensation", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_9, "24Fr", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_9, "catheter", 1)))},
]
BATCH_DATA.append({"id": "4673789_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4673789
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Amanda Garcia

Indication: Iatrogenic pneumothorax post-procedure
Side: Right

PROCEDURE: Tube Thoracostomy
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide accessible.
Site: 5th intercostal space, anterior to mid-axillary line.
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Blunt dissection technique. 24Fr chest tube inserted.
Rush of air upon entry. Tube fogging noted.
Tube secured with sutures. Connected to Pleur-evac at -20cmH2O.
CXR obtained - tube in good position.

DISPOSITION: ICU admission.
Plan: Daily CXR, assess for tube removal criteria.

Garcia, MD"""

entities_10 = [
    {"label": "OBS_LESION",        **dict(zip(["start", "end"], get_span(text_10, "pneumothorax", 1)))},
    {"label": "LATERALITY",        **dict(zip(["start", "end"], get_span(text_10, "Right", 1)))},
    {"label": "PROC_ACTION",       **dict(zip(["start", "end"], get_span(text_10, "Tube Thoracostomy", 1)))},
    {"label": "ANAT_PLEURA",       **dict(zip(["start", "end"], get_span(text_10, "5th intercostal space", 1)))},
    {"label": "ANAT_PLEURA",       **dict(zip(["start", "end"], get_span(text_10, "anterior to mid-axillary line", 1)))},
    {"label": "MEDICATION",        **dict(zip(["start", "end"], get_span(text_10, "lidocaine", 1)))},
    {"label": "PROC_METHOD",       **dict(zip(["start", "end"], get_span(text_10, "Blunt dissection", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_10, "24Fr", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_10, "chest tube", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_10, "Rush of air", 1)))},
    {"label": "OBS_FINDING",       **dict(zip(["start", "end"], get_span(text_10, "Tube fogging", 1)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_10, "Tube", 3)))},
    {"label": "DEV_CATHETER",      **dict(zip(["start", "end"], get_span(text_10, "Pleur-evac", 1)))},
    {"label": "MEAS_PRESS",        **dict(zip(["start", "end"], get_span(text_10, "-20cmH2O", 1)))},
]
BATCH_DATA.append({"id": "4673789", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)