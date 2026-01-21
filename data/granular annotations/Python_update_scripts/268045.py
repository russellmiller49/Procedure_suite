import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add cases
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure the script is running from the correct directory structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The occurrence number (1-based).
        
    Returns:
        list: [start_index, end_index] of the term.
    
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return [start, start + len(term)]

# ==========================================
# Note 1: 268045_syn_1
# ==========================================
text_1 = """Dx: LMS NSCLC, symptomatic.
Proc: Brachy cath placement.
Findings: LMS 60% obstructed. Infiltrative.
Action: 6F afterloading cath placed 2cm distal. Fluoro verified. Rx len 3.8cm.
Plan: RadOnc for 10Gy (2/2). Remove cath post-tx."""

entities_1 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_1, "LMS", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_1, "LMS", 2)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Brachy cath", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_1, "60% obstructed", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "Infiltrative", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "6F", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "afterloading cath", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "2cm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "Fluoro", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "3.8cm", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(text_1, "10Gy", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 268045_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: The patient, with symptomatic left main stem (LMS) adenocarcinoma, underwent flexible bronchoscopy for HDR brachytherapy catheter placement. Inspection revealed an infiltrative lesion causing 60% luminal stenosis. A 6-French afterloading catheter was successfully positioned across the lesion, extending 2 cm distally. Fluoroscopic imaging confirmed appropriate seating for a planned 3.8 cm treatment length. The patient tolerated the procedure well."""

entities_2 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_2, "left main stem", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_2, "LMS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "flexible bronchoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "infiltrative lesion", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_2, "60% luminal stenosis", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_2, "6-French", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "afterloading catheter", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "lesion", 2)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_2, "2 cm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "Fluoroscopic", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_2, "3.8 cm", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 268045_syn_3
# ==========================================
text_3 = """CPT Code: 31643 (Bronchoscopy w/ catheter placement).
Target: Left Main Stem (LMS).
Equipment: 6F Afterloading Catheter.
Imaging: Fluoroscopy (7 mins) utilized for confirmation.
Details: Catheter advanced through working channel past 1.8cm tumor. Secured for HDR delivery (10 Gy).
Outcome: Successful placement for palliation."""

entities_3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Bronchoscopy", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_3, "Left Main Stem", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_3, "LMS", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_3, "6F", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "Afterloading Catheter", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "Fluoroscopy", 1)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_3, "7 mins", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "Catheter", 2)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_3, "1.8cm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_3, "tumor", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(text_3, "10 Gy", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 268045_syn_4
# ==========================================
text_4 = """Procedure: Bronchoscopy + Brachy Cath
Patient: W. Rodriguez
Steps:
1. Sedation (Mod).
2. Scope to LMS.
3. Visualize tumor (60% occlusion).
4. Insert 6F catheter.
5. Fluoro check.
6. Mark and tape.
Plan: Session 2/2 today."""

entities_4 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Bronchoscopy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Brachy Cath", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_4, "LMS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_4, "tumor", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_4, "60% occlusion", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_4, "6F", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "catheter", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_4, "Fluoro", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 268045_syn_5
# ==========================================
text_5 = """dr stevens note for mr [REDACTED] he has that left main stem tumor causing stridor we did the brachy cath placement today using mod sedation scope went down saw the tumor its about 60 percent blocked put the 6f catheter in checked it on fluoro taped it up he went to radiation for his 10gy treatment no issues during the procedure"""

entities_5 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_5, "left main stem", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "tumor", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "brachy cath", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "tumor", 2)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_5, "60 percent blocked", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_5, "6f", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "catheter", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_5, "fluoro", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(text_5, "10gy", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 268045_syn_6
# ==========================================
text_6 = """Evaluation of a 63-year-old male with symptomatic LMS adenocarcinoma for brachytherapy. Flexible bronchoscopy was performed under moderate sedation. The endobronchial tumor at the LMS was visualized. A 6F afterloading catheter was advanced through the scope beyond the tumor margin. Fluoroscopy confirmed position. The catheter was secured for the second fraction of HDR brachytherapy (10.0 Gy)."""

entities_6 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_6, "LMS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "Flexible bronchoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "endobronchial tumor", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_6, "LMS", 2)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_6, "6F", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "afterloading catheter", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "tumor", 2)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "Fluoroscopy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "catheter", 2)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(text_6, "10.0 Gy", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 268045_syn_7
# ==========================================
text_7 = """[Indication]
Symptomatic LMS NSCLC, stridor.
[Anesthesia]
Moderate sedation.
[Description]
LMS tumor id[REDACTED]. 6F catheter placed 2 cm distal to lesion. Position verified with fluoroscopy. Treatment length defined as 3.8 cm. Catheter secured.
[Plan]
RadOnc for 10 Gy. Remove cath after."""

entities_7 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_7, "LMS", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_7, "LMS", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "tumor", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_7, "6F", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "catheter", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_7, "2 cm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "lesion", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "fluoroscopy", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_7, "3.8 cm", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "Catheter", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(text_7, "10 Gy", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 268045_syn_8
# ==========================================
text_8 = """[REDACTED] severe dyspnea due to his left main stem tumor. We performed a bronchoscopy to place a catheter for his final brachytherapy session. The tumor was visible in the LMS. We threaded a 6F catheter past the obstruction and checked its position on the fluoroscope. It looked good, so we taped it in place. He went directly to radiation oncology to receive his 10 Gy dose."""

entities_8 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_8, "left main stem", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "tumor", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "bronchoscopy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "catheter", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "tumor", 2)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_8, "LMS", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_8, "6F", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "catheter", 2)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "fluoroscope", 1)))},
    {"label": "MEAS_ENERGY", **dict(zip(["start", "end"], get_span(text_8, "10 Gy", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 268045_syn_9
# ==========================================
text_9 = """Diagnosis: Symptomatic LMS malignancy.
Intervention: Scope with positioning of brachytherapy tube.
Findings: 1.8 cm mass in LMS. 6F device inserted through the channel. Guidance via fluoroscopy used to validate location. Treatment span set to 3.8 cm. Patient conveyed to Radiation unit for dosing."""

entities_9 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_9, "LMS", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "brachytherapy tube", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_9, "1.8 cm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "mass", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_9, "LMS", 2)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_9, "6F", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "device", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "fluoroscopy", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_9, "3.8 cm", 1)))},
]
BATCH_DATA.append({"id": "268045_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")