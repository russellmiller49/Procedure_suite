import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for local testing if not in the exact structure
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 678234_syn_1
# ==========================================
text_1 = """Indication: Post-CABG effusion.
Proc: Catheter insertion.
- 14Fr pigtail.
- Landmark guidance.
- Drained 2350mL serous.
- Manometry: Normal elastance.
- Left to bulb suction."""

entities_1 = [
    {"label": "OBS_LESION",        **get_span(text_1, "effusion", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "Catheter insertion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14Fr pigtail", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "Landmark", 1)},
    {"label": "MEAS_VOL",          **get_span(text_1, "2350mL", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "Manometry", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "bulb suction", 1)},
]

BATCH_DATA.append({"id": "678234_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 678234_syn_2
# ==========================================
text_2 = """PROCEDURE: Insertion of pleural drainage catheter with manometry.
INDICATION: Large symptomatic effusion post-CABG.
DESCRIPTION: A 14Fr pigtail catheter was inserted into the right pleural space without imaging. Manometry was performed, showing normal pleural elastance. A total of 2350 mL of serous fluid was drained. The catheter was left in place and connected to a bulb drain."""

entities_2 = [
    {"label": "PROC_ACTION",       **get_span(text_2, "Insertion", 1)},
    {"label": "DEV_CATHETER",      **get_span(text_2, "pleural drainage catheter", 1)},
    {"label": "PROC_ACTION",       **get_span(text_2, "manometry", 1)},
    {"label": "OBS_LESION",        **get_span(text_2, "effusion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "14Fr pigtail catheter", 1)},
    {"label": "LATERALITY",        **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA",       **get_span(text_2, "pleural space", 1)},
    {"label": "PROC_ACTION",       **get_span(text_2, "Manometry", 1)},
    {"label": "MEAS_VOL",          **get_span(text_2, "2350 mL", 1)},
    {"label": "SPECIMEN",          **get_span(text_2, "fluid", 1)},
    {"label": "DEV_CATHETER",      **get_span(text_2, "catheter", 2)},
]

BATCH_DATA.append({"id": "678234_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 678234_syn_3
# ==========================================
text_3 = """CPT 32556: Pleural drainage w/ catheter.
Add-on: Manometry performed.
Output: 2350mL.
Device: 14Fr pigtail connected to bulb.
Guidance: None."""

entities_3 = [
    {"label": "PROC_ACTION",       **get_span(text_3, "Pleural drainage", 1)},
    {"label": "DEV_CATHETER",      **get_span(text_3, "catheter", 1)},
    {"label": "PROC_ACTION",       **get_span(text_3, "Manometry", 1)},
    {"label": "MEAS_VOL",          **get_span(text_3, "2350mL", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "14Fr pigtail", 1)},
]

BATCH_DATA.append({"id": "678234_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 678234_syn_4
# ==========================================
text_4 = """Procedure: Pigtail + Manometry
1. Landmark.
2. 14Fr pigtail.
3. Manometry checked (normal).
4. Drained 2350mL.
5. Bulb suction."""

entities_4 = [
    {"label": "DEV_CATHETER",      **get_span(text_4, "Pigtail", 1)},
    {"label": "PROC_ACTION",       **get_span(text_4, "Manometry", 1)},
    {"label": "PROC_METHOD",       **get_span(text_4, "Landmark", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "14Fr pigtail", 1)},
    {"label": "PROC_ACTION",       **get_span(text_4, "Manometry", 2)},
    {"label": "MEAS_VOL",          **get_span(text_4, "2350mL", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_4, "Bulb suction", 1)},
]

BATCH_DATA.append({"id": "678234_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 678234_syn_5
# ==========================================
text_5 = """Richard Hernandez post cabg effusion drained it with a pigtail 14fr checked pressures lung expanded fine got out over 2 liters 2350 total left it to bulb suction."""

entities_5 = [
    {"label": "OBS_LESION",         **get_span(text_5, "effusion", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_5, "pigtail", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_5, "14fr", 1)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_5, "lung expanded fine", 1)},
    {"label": "MEAS_VOL",           **get_span(text_5, "2 liters", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_5, "bulb suction", 1)},
]

BATCH_DATA.append({"id": "678234_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 678234_syn_6
# ==========================================
text_6 = """Thoracentesis with catheter insertion. Post-cardiac surgery pleural effusion right. Without ultrasound 14Fr pigtail catheter inserted using standard technique. Serous yellow fluid encountered. Total 2350mL drained over 50 minutes with serial manometry demonstrating pleural elastance 12 cm H2O/L. Catheter left in place attached to bulb suction."""

entities_6 = [
    {"label": "PROC_ACTION",       **get_span(text_6, "Thoracentesis", 1)},
    {"label": "PROC_ACTION",       **get_span(text_6, "catheter insertion", 1)},
    {"label": "OBS_LESION",        **get_span(text_6, "pleural effusion", 1)},
    {"label": "LATERALITY",        **get_span(text_6, "right", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "14Fr pigtail catheter", 1)},
    {"label": "SPECIMEN",          **get_span(text_6, "fluid", 1)},
    {"label": "MEAS_VOL",          **get_span(text_6, "2350mL", 1)},
    {"label": "MEAS_TIME",         **get_span(text_6, "50 minutes", 1)},
    {"label": "PROC_ACTION",       **get_span(text_6, "manometry", 1)},
    {"label": "MEAS_PRESS",        **get_span(text_6, "12 cm H2O/L", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_6, "bulb suction", 1)},
]

BATCH_DATA.append({"id": "678234_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 678234_syn_7
# ==========================================
text_7 = """[Indication]
Post-CABG effusion.
[Anesthesia]
Local.
[Description]
14Fr pigtail. Manometry normal. Drained 2350mL. Bulb suction.
[Plan]
Reassess tomorrow."""

entities_7 = [
    {"label": "OBS_LESION",        **get_span(text_7, "effusion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "14Fr pigtail", 1)},
    {"label": "PROC_ACTION",       **get_span(text_7, "Manometry", 1)},
    {"label": "MEAS_VOL",          **get_span(text_7, "2350mL", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_7, "Bulb suction", 1)},
]

BATCH_DATA.append({"id": "678234_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 678234_syn_8
# ==========================================
text_8 = """[REDACTED] a large fluid collection after his heart surgery. We placed a pigtail catheter to drain it. We checked the pressures in his chest while draining, which showed his lung was expanding well. We drained over 2 liters of fluid and left the tube in with a suction bulb to get the rest out."""

entities_8 = [
    {"label": "DEV_CATHETER",    **get_span(text_8, "pigtail catheter", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_8, "lung was expanding well", 1)},
    {"label": "MEAS_VOL",        **get_span(text_8, "2 liters", 1)},
    {"label": "SPECIMEN",        **get_span(text_8, "fluid", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_8, "suction bulb", 1)},
]

BATCH_DATA.append({"id": "678234_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 678234_syn_9
# ==========================================
text_9 = """Diagnosis: Post-surgical pleural effusion.
Action: Insertion of pleural catheter with manometry.
Details: 14Fr catheter placed. 2350mL drained. Elastance normal. Bulb suction applied."""

entities_9 = [
    {"label": "OBS_LESION",         **get_span(text_9, "pleural effusion", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "Insertion", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_9, "pleural catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "manometry", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_9, "14Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_9, "catheter", 2)},
    {"label": "MEAS_VOL",           **get_span(text_9, "2350mL", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_9, "Bulb suction", 1)},
]

BATCH_DATA.append({"id": "678234_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 678234
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Amanda Foster

Dx: Post-cardiac surgery pleural effusion, right
Procedure: Thoracentesis with catheter insertion

Hx: 59M s/p CABG 3 weeks ago, now with large right pleural effusion causing dyspnea. Effusion confirmed transudate on prior tap. Persistent accumulation.

Procedure:
Patient [REDACTED]. Right chest, 7th ICS at mid-axillary line. Sterile prep. Lidocaine local anesthesia.

Without ultrasound (not available), 14Fr pigtail catheter inserted using standard technique. Serous yellow fluid encountered. Total 2350mL drained over 50 minutes with serial manometry demonstrating pleural elastance 12 cm H2O/L (no trapped lung).

No complications. Patient much improved. CXR confirms lung expansion, no PTX.

Catheter left in place attached to bulb suction for ongoing drainage. Reassess tomorrow for removal.

A. Foster MD"""

entities_10 = [
    {"label": "OBS_LESION",        **get_span(text_10, "pleural effusion", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "Thoracentesis", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "catheter insertion", 1)},
    {"label": "LATERALITY",        **get_span(text_10, "right", 2)},
    {"label": "OBS_LESION",        **get_span(text_10, "pleural effusion", 2)},
    {"label": "LATERALITY",        **get_span(text_10, "Right", 1)},
    {"label": "MEDICATION",        **get_span(text_10, "Lidocaine", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "14Fr pigtail catheter", 1)},
    {"label": "SPECIMEN",          **get_span(text_10, "fluid", 1)},
    {"label": "MEAS_VOL",          **get_span(text_10, "2350mL", 1)},
    {"label": "MEAS_TIME",         **get_span(text_10, "50 minutes", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "manometry", 1)},
    {"label": "MEAS_PRESS",        **get_span(text_10, "12 cm H2O/L", 1)},
    {"label": "OUTCOME_PLEURAL",   **get_span(text_10, "no trapped lung", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
    {"label": "OUTCOME_PLEURAL",   **get_span(text_10, "lung expansion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no PTX", 1)},
    {"label": "DEV_CATHETER",      **get_span(text_10, "Catheter", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "bulb suction", 1)},
]

BATCH_DATA.append({"id": "678234", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)