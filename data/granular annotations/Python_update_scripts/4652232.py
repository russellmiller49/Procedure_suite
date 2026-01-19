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
# 2. Helper Definition
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
# Case 1: 4652232_syn_1
# ==========================================
text_1 = """Indication: Hepatic hydrothorax.
Procedure: Pleural Catheter (Left).
Method: Seldinger (Landmark).
Size: 14Fr.
Drainage: 996mL serosanguinous.
Plan: Monitor output."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Hepatic hydrothorax", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Pleural Catheter", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Seldinger", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Landmark", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14Fr", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "996mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "serosanguinous", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 4652232_syn_2
# ==========================================
text_2 = """PROCEDURE: Placement of Pleural Drainage Catheter.
Mr. [REDACTED] required drainage of a left-sided hepatic hydrothorax. The 5th intercostal space was id[REDACTED] by anatomic landmarks. A 14Fr pigtail catheter was placed using the Seldinger technique without real-time imaging. 996 mL of fluid was evacuated. Complications: None."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Placement", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "Pleural Drainage Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "drainage", 1)},
    {"label": "LATERALITY", **get_span(text_2, "left-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "hepatic hydrothorax", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "5th intercostal space", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "anatomic landmarks", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Seldinger technique", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "996 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "None", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 4652232_syn_3
# ==========================================
text_3 = """Code: 32556 (Pleural drainage, percutaneous, without imaging).
Device: 14Fr Pigtail.
Technique: Seldinger.
Volume: 996 mL.
Location: [REDACTED]"""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Pleural drainage", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "percutaneous", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Pigtail", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Seldinger", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "996 mL", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 4652232_syn_4
# ==========================================
text_4 = """Procedure: Pigtail Placement
Patient: [REDACTED]
Steps:
1. Landmarks id[REDACTED].
2. Prep/Drape/Local.
3. Needle entry.
4. 14Fr catheter over wire.
5. Drained ~1L.
Plan: Reassess 48h."""

entities_4 = [
    {"label": "DEV_CATHETER", **get_span(text_4, "Pigtail", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Placement", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Landmarks", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Needle", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "wire", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "~1L", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 4652232_syn_5
# ==========================================
text_5 = """put a pigtail in mr [REDACTED] left side for the hydrothorax just used landmarks didnt use ultrasound 14 french tube drained about a liter serosanguinous fluid securement device applied."""

entities_5 = [
    {"label": "DEV_CATHETER", **get_span(text_5, "pigtail", 1)},
    {"label": "LATERALITY", **get_span(text_5, "left side", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "hydrothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "landmarks", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5, "14 french", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "tube", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "about a liter", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "serosanguinous", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 4652232_syn_6
# ==========================================
text_6 = """A pleural drainage catheter was inserted on the left side. Landmarks were used to id[REDACTED] the insertion site. A 14Fr catheter was placed. 996mL of fluid was drained. Post-procedure x-ray confirmed position."""

entities_6 = [
    {"label": "DEV_CATHETER", **get_span(text_6, "pleural drainage catheter", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left side", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Landmarks", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 2)},
    {"label": "MEAS_VOL", **get_span(text_6, "996mL", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 4652232_syn_7
# ==========================================
text_7 = """[Indication]
Hepatic hydrothorax.
[Anesthesia]
Local.
[Description]
Left 14Fr pigtail placed (Landmark guidance). 996mL drained.
[Plan]
Floor care."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Hepatic hydrothorax", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Left", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "pigtail", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Landmark guidance", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "996mL", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 4652232_syn_8
# ==========================================
text_8 = """We inserted a small drainage tube into [REDACTED] to treat his liver-related fluid buildup. We found the spot by feeling the ribs and placed the tube using a guide wire. It drained just under a liter of fluid. We'll watch the output over the next few days."""

entities_8 = [
    {"label": "DEV_CATHETER", **get_span(text_8, "drainage tube", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "fluid buildup", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "feeling the ribs", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "tube", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "guide wire", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "just under a liter", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 4652232_syn_9
# ==========================================
text_9 = """Procedure: Percutaneous pleural catheterization (blind).
Indication: Transdiaphragmatic fluid accumulation.
Device: 14Fr pigtail.
Yield: 996mL.
Guidance: Anatomic landmarks."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "pleural catheterization", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Percutaneous", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "blind", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Transdiaphragmatic fluid accumulation", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_9, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "996mL", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Anatomic landmarks", 1)},
]
BATCH_DATA.append({"id": "4652232_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 4652232
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Rachel Kim

Indication: Hepatic hydrothorax
Side: Left

PROCEDURE: Pleural Drainage Catheter Placement
Informed consent obtained. Timeout performed.
Patient [REDACTED]ide up.
Site: [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Seldinger technique used. 14Fr pigtail catheter inserted.
996mL serosanguinous fluid drained.
Catheter secured. Connected to drainage system.
Post-procedure CXR: catheter in appropriate position, no PTX.

DISPOSITION: Floor admission for continued drainage.
Plan: Daily output monitoring, reassess in 48-72h.

Kim, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Hepatic hydrothorax", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Left", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Pleural Drainage Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Placement", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Seldinger technique", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "996mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "serosanguinous", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no PTX", 1)},
]
BATCH_DATA.append({"id": "4652232", "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)