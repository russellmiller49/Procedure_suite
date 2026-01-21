import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 456890_syn_1
# ==========================================
id_1 = "456890_syn_1"
text_1 = """Indication: Complicated parapneumonic effusion.
Proc: Catheter drainage.
- 14Fr pigtail.
- No imaging.
- Drained 900mL turbid.
- Connected to water seal."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Complicated parapneumonic effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Catheter drainage", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "turbid", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "water seal", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 456890_syn_2
# ==========================================
id_2 = "456890_syn_2"
text_2 = """PROCEDURE: Placement of pleural drainage catheter.
INDICATION: Complicated parapneumonic effusion/empyema.
DESCRIPTION: A 14Fr pigtail catheter was inserted into the right pleural space using the Seldinger technique without imaging guidance. Purulent fluid was encountered, and 900 mL was drained. The catheter was secured and attached to a water seal system for continuous drainage."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Placement", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "pleural drainage catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "Complicated parapneumonic effusion/empyema", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "pigtail catheter", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Seldinger technique", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Purulent", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "900 mL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "water seal system", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 456890_syn_3
# ==========================================
id_3 = "456890_syn_3"
text_3 = """CPT 32556: Pleural drainage with catheter insertion.
Type: 14Fr Pigtail.
Guidance: None.
Output: 900mL purulent.
Plan: Continuous drainage."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Pleural drainage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "catheter", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "purulent", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 456890_syn_4
# ==========================================
id_4 = "456890_syn_4"
text_4 = """Procedure: Pigtail Placement
1. Landmark.
2. 14Fr pigtail in.
3. Drained 900mL turbid fluid.
4. Sutured in place.
5. Water seal."""
entities_4 = [
    {"label": "DEV_CATHETER", **get_span(text_4, "Pigtail", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Placement", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Landmark", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "turbid", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Water seal", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 456890_syn_5
# ==========================================
id_5 = "456890_syn_5"
text_5 = """James Morrison with the empyema put in a pigtail 14fr right side landmark guided drained 900cc pus hooked it up to atrium for drainage."""
entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "empyema", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "pigtail", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5, "14fr", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right side", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "landmark guided", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "900cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "pus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "atrium", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 456890_syn_6
# ==========================================
id_6 = "456890_syn_6"
text_6 = """Thoracentesis with catheter drainage. Right parapneumonic effusion. Without imaging guidance 14Fr pigtail catheter placed using Seldinger technique. Immediate return of turbid yellow-green fluid. 900mL drained during procedure. Catheter sutured and connected to underwater seal drainage."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Thoracentesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "drainage", 1)},
    {"label": "LATERALITY", **get_span(text_6, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "parapneumonic effusion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Seldinger technique", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "turbid yellow-green", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "900mL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "underwater seal drainage", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 456890_syn_7
# ==========================================
id_7 = "456890_syn_7"
text_7 = """[Indication]
Complicated parapneumonic effusion.
[Anesthesia]
Local.
[Description]
14Fr pigtail inserted. 900mL drained. Secured to water seal.
[Plan]
Admit."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Complicated parapneumonic effusion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "900mL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "water seal", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 456890_syn_8
# ==========================================
id_8 = "456890_syn_8"
text_8 = """[REDACTED] infected fluid collection around his lung. We placed a pigtail catheter to drain it continuously. We drained 900mL of cloudy fluid initially and hooked the tube up to a drainage system to keep the lung clear."""
entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "infected fluid collection", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "cloudy", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 456890_syn_9
# ==========================================
id_9 = "456890_syn_9"
text_9 = """Diagnosis: Complicated pleural effusion.
Action: Insertion of pleural drain.
Details: 14Fr catheter placed. 900mL turbid output. Connected to drainage system."""
entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "Complicated pleural effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Insertion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "pleural drain", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_9, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "turbid", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 456890
# ==========================================
id_10 = "456890"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Patricia Lee

Dx: Right parapneumonic effusion
Procedure: Thoracentesis with catheter drainage

Hx: 67M admitted with CAP complicated by moderate right pleural effusion. Initial thoracentesis 2 days ago showed complicated parapneumonic effusion. Persistent effusion with fever, decision made for catheter drainage.

Procedure:
Patient [REDACTED] at bedside. Right posterolateral chest, 7th ICS posterior axillary line. Standard sterile prep. Local anesthesia with lidocaine.

Without imaging guidance, 14Fr pigtail catheter placed using Seldinger technique. Immediate return of turbid yellow-green fluid. 900mL drained during procedure. Catheter sutured and connected to underwater seal drainage.

Fluid analysis: pH 7.15, glucose 35, LDH 1250 - consistent with complicated parapneumonic/early empyema.

No pneumothorax on bedside ultrasound. Patient comfortable.

Plan: Continuous drainage. If inadequate, will consider fibrinolytics vs thoracoscopy.

P. Lee MD"""
entities_10 = [
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "parapneumonic effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Thoracentesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "drainage", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "parapneumonic effusion", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "catheter drainage", 2)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "chest", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Seldinger technique", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "turbid yellow-green", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "900mL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "underwater seal drainage", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "empyema", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)