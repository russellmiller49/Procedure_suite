import sys
from pathlib import Path

# Set up the repository root (assuming script is run from within the repo structure)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure you are running from the correct repository context.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns: {'start': int, 'end': int} or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 555123_syn_1
# ==========================================
t1 = "EBUS-TBNA 7, 4R. Radial EBUS RUL nodule. TBBx x5. Brush x1."
e1 = [
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBBx", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "1", 1)},
]
BATCH_DATA.append({"id": "555123_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 555123_syn_2
# ==========================================
t2 = "Mr. [REDACTED] underwent a combined EBUS-TBNA and navigational bronchoscopy. Mediastinal staging involved sampling stations 7 and 4R. The peripheral RUL nodule was localized via radial EBUS (eccentric view) and sampled with transbronchial biopsy and brushing."
e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "navigational bronchoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "4R", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "transbronchial biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "brushing", 1)},
]
BATCH_DATA.append({"id": "555123_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 555123_syn_3
# ==========================================
t3 = "CPT 31652 (EBUS-TBNA 2 stations), 31654 (Radial EBUS peripheral), 31628 (TBBx), 31623 (Brush). RUL nodule and mediastinal nodes sampled."
e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "2", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBBx", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Brush", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "mediastinal nodes", 1)},
]
BATCH_DATA.append({"id": "555123_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 555123_syn_4
# ==========================================
t4 = "Procedure: EBUS and Nav Bronch. Steps: 1. EBUS stations 7, 4R. 2. Radial EBUS to RUL lesion. 3. Biopsy x5. 4. Brush x1."
e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Nav Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "4R", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "1", 2)}, # "Brush x1" is the second "1" in the text
]
BATCH_DATA.append({"id": "555123_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 555123_syn_5
# ==========================================
t5 = "bronch for john doe did ebus first hit 7 and 4r then switched scopes for the nodule in the rul used the radar probe found it eccentric took 5 biopsies and a brush rose said inflammation."
e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ebus", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "4r", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rul", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "radar probe", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "eccentric", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "rose", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "inflammation", 1)},
]
BATCH_DATA.append({"id": "555123_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 555123_syn_6
# ==========================================
t6 = "Bronchoscopy performed for mediastinal adenopathy and RUL nodule. EBUS-TBNA of stations 7 and 4R was completed. The RUL nodule was located with radial EBUS and sampled via biopsy and brush."
e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mediastinal adenopathy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 2)},
    {"label": "PROC_METHOD", **get_span(t6, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "brush", 1)},
]
BATCH_DATA.append({"id": "555123_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 555123_syn_7
# ==========================================
t7 = "[Indication] Adenopathy/Nodule. [Anesthesia] Moderate. [Description] EBUS 7/4R. Radial EBUS RUL. TBBx/Brush. [Plan] Path pending."
e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Adenopathy", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4R", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBBx", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Brush", 1)},
]
BATCH_DATA.append({"id": "555123_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 555123_syn_8
# ==========================================
t8 = "We started with the EBUS scope to sample the lymph nodes at stations 7 and 4R. Then we switched to the thin scope and used the radial probe to find the nodule in the right upper lobe. We took biopsies and a brush sample."
e8 = [
    {"label": "DEV_INSTRUMENT", **get_span(t8, "EBUS scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "4R", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "thin scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "radial probe", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right upper lobe", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "brush", 1)},
]
BATCH_DATA.append({"id": "555123_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 555123_syn_9
# ==========================================
t9 = "Endobronchial ultrasound-guided needle aspiration of mediastinal nodes. Peripheral lesion localization via radial probe. Transbronchial sampling and brushing performed."
e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "mediastinal nodes", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "radial probe", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Transbronchial sampling", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "brushing", 1)},
]
BATCH_DATA.append({"id": "555123_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 555123
# ==========================================
t10 = """Fellow Procedure Note

Patient: [REDACTED] (MRN: [REDACTED])
Attending: Dr. Z. Smith
Date: [REDACTED]

Performed standard bronchoscopy via oral route (moderate sedation). Vocal cords normal. 

**EBUS-TBNA:**
Used linear scope. Sampled station 7 (subcarinal) and 4R (right paratracheal). Both small (<1cm) but PET avid. 
- 7: 3 passes, ROSE negative.
- 4R: 3 passes, ROSE negative.

**Peripheral Nodule Assessment:**
Exchanged for thin bronchoscope (P190). Advanced to RUL apical segment. Inserted **Radial EBUS** probe. Visualized lesion - eccentric view (not concentric). Adjusted scope, still eccentric but tool-in-lesion confirmed. 

Performed **transbronchial biopsies** (fluoroscopy guidance) x 5. 
Performed **brushing** x 1.

ROSE: Non-diagnostic / inflammation.

Plan: Await final path. If negative, consider TTNA."""

e10 = [
    {"label": "PROC_ACTION", **get_span(t10, "bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Vocal cords", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "normal", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "linear scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "right paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "<1cm", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "PET avid", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "negative", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "negative", 2)},
    {"label": "OBS_LESION", **get_span(t10, "Nodule", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "thin bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "P190", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "apical segment", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "probe", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "eccentric", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "eccentric", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "transbronchial biopsies", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "fluoroscopy", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "brushing", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "1", 2)}, # "1" appears in "<1cm", then "x 1"
    {"label": "OBS_ROSE", **get_span(t10, "Non-diagnostic", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "inflammation", 1)},
]
BATCH_DATA.append({"id": "555123", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)