import sys
from pathlib import Path

# ==========================================
# 1. Environment Setup
# ==========================================
# Dynamically calculate the repo root (assumes this script is in specific subdirectory)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

# ==========================================
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive substring.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# 3. Data Batch Definition
# ==========================================
BATCH_DATA = []

# -------------------------------------------------------------------------
# Case 1: 901234_syn_1
# -------------------------------------------------------------------------
text_1 = """Indication: Large R effusion.
Proc: Thoracentesis w/ catheter.
- US marked.
- 14Fr catheter.
- Drained 1800mL serosanguinous.
- Catheter left in place."""

entities_1 = [
    {"label": "LATERALITY",          **get_span(text_1, "R", 1)},
    {"label": "OBS_LESION",          **get_span(text_1, "effusion", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "Thoracentesis", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_1, "catheter", 1)},
    {"label": "PROC_METHOD",         **get_span(text_1, "US", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "14Fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_1, "catheter", 2)},
    {"label": "MEAS_VOL",            **get_span(text_1, "1800mL", 1)},
    {"label": "OBS_FINDING",         **get_span(text_1, "serosanguinous", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_1, "Catheter", 1)},
]
BATCH_DATA.append({"id": "901234_syn_1", "text": text_1, "entities": entities_1})

# -------------------------------------------------------------------------
# Case 2: 901234_syn_2
# -------------------------------------------------------------------------
text_2 = """PROCEDURE NOTE: Thoracentesis with insertion of indwelling pleural drainage catheter.
INDICATION: Symptomatic pleural effusion, suspected malignancy.
DESCRIPTION: Following ultrasound marking, a 14Fr pleural catheter was inserted using the Seldinger technique. A total of 1800 mL of serosanguinous fluid was drained, providing immediate symptomatic relief. The catheter was secured for ongoing drainage."""

entities_2 = [
    {"label": "PROC_ACTION",         **get_span(text_2, "Thoracentesis", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_2, "indwelling pleural drainage catheter", 1)},
    {"label": "OBS_LESION",          **get_span(text_2, "pleural effusion", 1)},
    {"label": "PROC_METHOD",         **get_span(text_2, "ultrasound", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_2, "14Fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_2, "pleural catheter", 1)},
    {"label": "MEAS_VOL",            **get_span(text_2, "1800 mL", 1)},
    {"label": "OBS_FINDING",         **get_span(text_2, "serosanguinous fluid", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_2, "catheter", 3)},
    {"label": "OUTCOME_PLEURAL",    **get_span(text_2, "symptomatic relief", 1)},
]
BATCH_DATA.append({"id": "901234_syn_2", "text": text_2, "entities": entities_2})

# -------------------------------------------------------------------------
# Case 3: 901234_syn_3
# -------------------------------------------------------------------------
text_3 = """CPT 32556: Pleural drainage with insertion of indwelling catheter.
Guidance: Ultrasound (marking only).
Output: 1800mL.
Catheter: 14Fr."""

entities_3 = [
    {"label": "PROC_ACTION",         **get_span(text_3, "Pleural drainage", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_3, "indwelling catheter", 1)},
    {"label": "PROC_METHOD",         **get_span(text_3, "Ultrasound", 1)},
    {"label": "MEAS_VOL",            **get_span(text_3, "1800mL", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_3, "14Fr", 1)},
]
BATCH_DATA.append({"id": "901234_syn_3", "text": text_3, "entities": entities_3})

# -------------------------------------------------------------------------
# Case 4: 901234_syn_4
# -------------------------------------------------------------------------
text_4 = """Procedure: Catheter Drainage
1. US mark.
2. Local.
3. 14Fr catheter placed.
4. Drained 1800mL.
5. Secured."""

entities_4 = [
    {"label": "DEV_CATHETER",        **get_span(text_4, "Catheter", 1)},
    {"label": "PROC_ACTION",         **get_span(text_4, "Drainage", 1)},
    {"label": "PROC_METHOD",         **get_span(text_4, "US", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_4, "14Fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_4, "catheter", 1)},
    {"label": "MEAS_VOL",            **get_span(text_4, "1800mL", 1)},
]
BATCH_DATA.append({"id": "901234_syn_4", "text": text_4, "entities": entities_4})

# -------------------------------------------------------------------------
# Case 5: 901234_syn_5
# -------------------------------------------------------------------------
text_5 = """William Turner with the big right effusion put in a 14fr catheter today marked with us drained 1.8 liters fluid looks serosanguinous patient breathing better now catheter stayed in."""

entities_5 = [
    {"label": "LATERALITY",          **get_span(text_5, "right", 1)},
    {"label": "OBS_LESION",          **get_span(text_5, "effusion", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_5, "14fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_5, "catheter", 1)},
    {"label": "PROC_METHOD",         **get_span(text_5, "us", 1)},
    {"label": "MEAS_VOL",            **get_span(text_5, "1.8 liters", 1)},
    {"label": "OBS_FINDING",         **get_span(text_5, "serosanguinous", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_5, "catheter", 2)},
]
BATCH_DATA.append({"id": "901234_syn_5", "text": text_5, "entities": entities_5})

# -------------------------------------------------------------------------
# Case 6: 901234_syn_6
# -------------------------------------------------------------------------
text_6 = """Thoracentesis with insertion of indwelling pleural drainage catheter. 64M former smoker with new right-sided pleural effusion. Using Seldinger technique 14Fr pleural drainage catheter inserted. Total drainage 1800mL serosanguinous fluid over 30 minutes. Patient reported immediate relief of dyspnea. Plan admit for drainage monitoring."""

entities_6 = [
    {"label": "PROC_ACTION",         **get_span(text_6, "Thoracentesis", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_6, "indwelling pleural drainage catheter", 1)},
    {"label": "LATERALITY",          **get_span(text_6, "right", 1)},
    {"label": "OBS_LESION",          **get_span(text_6, "pleural effusion", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_6, "14Fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_6, "pleural drainage catheter", 2)},
    {"label": "MEAS_VOL",            **get_span(text_6, "1800mL", 1)},
    {"label": "OBS_FINDING",         **get_span(text_6, "serosanguinous fluid", 1)},
    {"label": "MEAS_TIME",           **get_span(text_6, "30 minutes", 1)},
    {"label": "OUTCOME_SYMPTOMS",    **get_span(text_6, "relief of dyspnea", 1)},
]
BATCH_DATA.append({"id": "901234_syn_6", "text": text_6, "entities": entities_6})

# -------------------------------------------------------------------------
# Case 7: 901234_syn_7
# -------------------------------------------------------------------------
text_7 = """[Indication]
Symptomatic R pleural effusion.
[Anesthesia]
Local.
[Description]
14Fr catheter placed (US marked). Drained 1800mL.
[Plan]
Admit."""

entities_7 = [
    {"label": "LATERALITY",          **get_span(text_7, "R", 1)},
    {"label": "OBS_LESION",          **get_span(text_7, "pleural effusion", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_7, "14Fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_7, "catheter", 1)},
    {"label": "PROC_METHOD",         **get_span(text_7, "US", 1)},
    {"label": "MEAS_VOL",            **get_span(text_7, "1800mL", 1)},
]
BATCH_DATA.append({"id": "901234_syn_7", "text": text_7, "entities": entities_7})

# -------------------------------------------------------------------------
# Case 8: 901234_syn_8
# -------------------------------------------------------------------------
text_8 = """[REDACTED] a large amount of fluid around his right lung causing shortness of breath. We used ultrasound to find the best spot, then inserted a small tube (catheter) to drain it. We removed 1800mL of fluid, which helped his breathing right away. We left the tube in to continue draining."""

entities_8 = [
    {"label": "LATERALITY",          **get_span(text_8, "right", 1)},
    {"label": "PROC_METHOD",         **get_span(text_8, "ultrasound", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_8, "tube", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_8, "catheter", 1)},
    {"label": "MEAS_VOL",            **get_span(text_8, "1800mL", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_8, "tube", 2)},
]
BATCH_DATA.append({"id": "901234_syn_8", "text": text_8, "entities": entities_8})

# -------------------------------------------------------------------------
# Case 9: 901234_syn_9
# -------------------------------------------------------------------------
text_9 = """Diagnosis: Pleural effusion.
Action: Insertion of pleural drainage catheter.
Details: 14Fr catheter placed. 1800mL drained. Catheter secured."""

entities_9 = [
    {"label": "OBS_LESION",          **get_span(text_9, "Pleural effusion", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_9, "pleural drainage catheter", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_9, "14Fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_9, "catheter", 2)},
    {"label": "MEAS_VOL",            **get_span(text_9, "1800mL", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_9, "Catheter", 1)},
]
BATCH_DATA.append({"id": "901234_syn_9", "text": text_9, "entities": entities_9})

# -------------------------------------------------------------------------
# Case 10: 901234 (Main)
# -------------------------------------------------------------------------
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Susan Phillips

Dx: Large symptomatic right pleural effusion, suspected malignancy
Procedure: Thoracentesis with insertion of indwelling pleural drainage catheter

Hx: 64M former smoker with new right-sided pleural effusion. CT shows large effusion with nodular pleural thickening. Presents with progressive dyspnea over 2 weeks.

Procedure:
Position: Seated upright leaning forward on bedside table.
Site: Right posterior chest, 8th ICS at posterior axillary line.
Anesthesia: 1% lidocaine local anesthesia.
Guidance: Ultrasound used to id[REDACTED] pocket and mark entry point.

Using Seldinger technique, 14Fr pleural drainage catheter inserted. Initial return of 200mL sanguineous fluid; catheter connected to drainage bag. Total drainage: 1800mL serosanguinous fluid over 30 minutes.

Fluid sent for: Cell count, chemistry, cytology, cultures.

Patient [REDACTED] relief of dyspnea. SpO2 improved 88% to 94% on RA. No pneumothorax on post-procedure CXR.

Plan: Admit for drainage monitoring. Consider PleurX if malignant.

S. Phillips MD"""

entities_10 = [
    {"label": "LATERALITY",          **get_span(text_10, "right", 1)},
    {"label": "OBS_LESION",          **get_span(text_10, "pleural effusion", 1)},
    {"label": "PROC_ACTION",         **get_span(text_10, "Thoracentesis", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_10, "indwelling pleural drainage catheter", 1)},
    {"label": "LATERALITY",          **get_span(text_10, "right", 2)},
    {"label": "OBS_LESION",          **get_span(text_10, "pleural effusion", 2)},
    {"label": "OBS_LESION",          **get_span(text_10, "effusion", 3)},
    {"label": "OBS_LESION",          **get_span(text_10, "nodular", 1)},
    {"label": "OBS_FINDING",         **get_span(text_10, "pleural thickening", 1)},
    # Fixed: "Right" appears capitalized only once in the text (at "Site: Right...")
    {"label": "LATERALITY",          **get_span(text_10, "Right", 1)},
    {"label": "ANAT_PLEURA",         **get_span(text_10, "posterior chest", 1)},
    {"label": "MEDICATION",          **get_span(text_10, "lidocaine", 1)},
    {"label": "PROC_METHOD",         **get_span(text_10, "Ultrasound", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_10, "14Fr", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_10, "pleural drainage catheter", 2)},
    {"label": "MEAS_VOL",            **get_span(text_10, "200mL", 1)},
    {"label": "OBS_FINDING",         **get_span(text_10, "sanguineous fluid", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_10, "catheter", 1)},
    {"label": "MEAS_VOL",            **get_span(text_10, "1800mL", 1)},
    {"label": "OBS_FINDING",         **get_span(text_10, "serosanguinous fluid", 1)},
    {"label": "MEAS_TIME",           **get_span(text_10, "30 minutes", 1)},
    {"label": "SPECIMEN",            **get_span(text_10, "Fluid", 1)},
    {"label": "OUTCOME_SYMPTOMS",    **get_span(text_10, "relief of dyspnea", 1)},
    {"label": "OUTCOME_SYMPTOMS",    **get_span(text_10, "SpO2 improved", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No pneumothorax", 1)},
    {"label": "DEV_CATHETER",        **get_span(text_10, "PleurX", 1)},
]
BATCH_DATA.append({"id": "901234", "text": text_10, "entities": entities_10})


# ==========================================
# 4. Main Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting processing of {len(BATCH_DATA)} cases...")
    for case in BATCH_DATA:
        print(f"Processing case: {case['id']}")
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")