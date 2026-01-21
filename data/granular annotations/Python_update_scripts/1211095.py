import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is located in 'scripts/' or similar, and we need the root.
# Adjust REPO_ROOT calculation if the script location differs in your pipeline.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure your project structure is correct and the script is running from the right location.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search.
        term (str): The exact term to find (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            return None
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 1211095_syn_1
# ==========================================
id_1 = "1211095_syn_1"
text_1 = """Indication: Malignant effusion.
Procedure: Tunneled Pleural Catheter (Right).
Tech: Seldinger. Subcutaneous tunnel created.
Drainage: 2300mL turbid fluid.
Plan: Home drainage education."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Malignant effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Tunneled Pleural Catheter", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Seldinger", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Subcutaneous tunnel", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "2300mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "turbid", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "fluid", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1211095_syn_2
# ==========================================
id_2 = "1211095_syn_2"
text_2 = """OPERATIVE REPORT: Insertion of Tunneled Indwelling Pleural Catheter.
[REDACTED] catheter placement for a recurrent malignant effusion. Following ultrasound localization, a subcutaneous tunnel was created on the right chest wall. The Aspira catheter was introduced into the pleural cavity via a separate counter-incision. 2.3L of turbid fluid was evacuated. The cuff was positioned appropriately within the tunnel."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Insertion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "Tunneled Indwelling Pleural Catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignant effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "ultrasound", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "subcutaneous tunnel", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "chest wall", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "Aspira", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural cavity", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "2.3L", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "turbid", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "fluid", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "tunnel", 2)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1211095_syn_3
# ==========================================
id_3 = "1211095_syn_3"
text_3 = """Code: 32550 (Insertion of tunneled pleural catheter with cuff).
Kit: Aspira.
Guidance: Ultrasound (bundled).
Drainage: 2300 mL.
Confirmation: CXR showed lung re-expansion."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Insertion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "tunneled pleural catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Aspira", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ultrasound", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "2300 mL", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_3, "lung re-expansion", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1211095_syn_4
# ==========================================
id_4 = "1211095_syn_4"
text_4 = """Procedure: IPC Placement
Patient: [REDACTED]
Steps:
1. US marked site (5th ICS).
2. Local/Sedation.
3. Tunnel made.
4. Catheter inserted over wire.
5. Drained 2.3L.
Plan: Discharge with supplies."""

entities_4 = [
    {"label": "DEV_CATHETER", **get_span(text_4, "IPC", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "US", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "Tunnel", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "2.3L", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1211095_syn_5
# ==========================================
id_5 = "1211095_syn_5"
text_5 = """put in a tunneled catheter for mr [REDACTED] right side malignant effusion used the aspira kit made the tunnel under the skin put the tube in drained a lot of fluid 2300 ml patient feels better going home with instructions."""

entities_5 = [
    {"label": "DEV_CATHETER", **get_span(text_5, "tunneled catheter", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right side", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "malignant effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "aspira", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "tunnel", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "tube", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "2300 ml", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1211095_syn_6
# ==========================================
id_6 = "1211095_syn_6"
text_6 = """A tunneled pleural catheter was inserted for management of malignant effusion. The procedure was performed under ultrasound guidance. A subcutaneous tunnel was created. The catheter was advanced into the right pleural space. 2300mL of turbid fluid was drained. The catheter was secured."""

entities_6 = [
    {"label": "DEV_CATHETER", **get_span(text_6, "tunneled pleural catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "malignant effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "ultrasound", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "subcutaneous tunnel", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 1)},
    {"label": "LATERALITY", **get_span(text_6, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "pleural space", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "2300mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "turbid", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 2)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1211095_syn_7
# ==========================================
id_7 = "1211095_syn_7"
text_7 = """[Indication]
Malignant effusion, unknown primary.
[Anesthesia]
Moderate sedation.
[Description]
Right-sided IPC placed via tunneling technique. 2300mL drained.
[Plan]
Clinic f/u 1-2 weeks."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Malignant effusion", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Right-sided", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "IPC", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "2300mL", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1211095_syn_8
# ==========================================
id_8 = "1211095_syn_8"
text_8 = """We placed a permanent drainage catheter for [REDACTED] help manage his fluid buildup. We created a small tunnel under the skin to lower infection risk and inserted the tube into the pleural space. We drained over 2 liters of fluid immediately. He will learn how to drain this at home."""

entities_8 = [
    {"label": "DEV_CATHETER", **get_span(text_8, "drainage catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "fluid buildup", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "tunnel", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "tube", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleural space", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "2 liters", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 2)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1211095_syn_9
# ==========================================
id_9 = "1211095_syn_9"
text_9 = """Procedure: Implantation of indwelling pleural conduit.
Device: Tunneled catheter (Aspira).
Volume: 2300mL turbid effusion.
Guidance: Sonography.
Disposition: Ambulatory management."""

entities_9 = [
    {"label": "DEV_CATHETER", **get_span(text_9, "indwelling pleural conduit", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Tunneled catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Aspira", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "2300mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "turbid", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Sonography", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1211095
# ==========================================
id_10 = "1211095"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Rachel Kim

Indication: Malignant pleural effusion - unknown primary
Side: Right

PROCEDURE: Tunneled Pleural Catheter Insertion
Informed consent obtained. Timeout performed.
Patient positioned lateral decubitus, Right side up.
Preprocedure ultrasound confirmed large free-flowing effusion.
Site [REDACTED]
Sterile prep and drape. Local anesthesia with 1% lidocaine.
Aspira tunneled pleural catheter kit used.
Subcutaneous tunnel created. Pleural space entered with Seldinger technique.
Catheter advanced and position confirmed. 2300mL turbid fluid drained.
Catheter secured with sutures. Sterile dressing applied.
CXR obtained - catheter in good position, lung re-expanded.

DISPOSITION: Home with drainage supplies. Teaching provided.
F/U: Clinic 1-2 weeks, drain PRN for symptoms.

Kim, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Malignant pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Tunneled Pleural Catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 2)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Aspira", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "tunneled pleural catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Subcutaneous tunnel", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Seldinger", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "2300mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "turbid", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter", 3)},
    {"label": "DEV_CATHETER", **get_span(text_10, "catheter", 2)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "lung re-expanded", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)