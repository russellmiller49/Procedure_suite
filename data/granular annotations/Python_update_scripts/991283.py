import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Case 1: 991283_syn_1
# ==========================================
text_1 = """Proc: EBUS-TBNA + Attempted Nav Bronch.
LN Sampling:
- Stn 7 (12mm): 3 passes, benign.
- Stn 4R (10mm): 3 passes, benign.
- Stn 4L (8mm): 2 passes, benign.
Navigation: Veran system. RUL nodule target. Reg error 5mm. Target NOT reached/visualized despite multiple attempts. Radial EBUS negative.
Outcome: Mediastinum staged. Peripheral biopsy aborted."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Nav Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Sampling", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Stn 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "benign", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Stn 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "10mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "benign", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Stn 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "benign", 3)},
    {"label": "PROC_METHOD", **get_span(text_1, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Veran system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "5mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Mediastinum", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "staged", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
]
BATCH_DATA.append({"id": "991283_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 991283_syn_2
# ==========================================
text_2 = """PROCEDURE SUMMARY: The patient underwent combined EBUS-TBNA and attempted electromagnetic navigation bronchoscopy. Systematic mediastinal staging was performed first. EBUS-guided transbronchial needle aspiration was conducted at stations 7, 4R, and 4L; rapid on-site evaluation indicated benign lymphocytes for all stations. Following this, the scope was exchanged for navigation to the 1.8cm RUL apical nodule. Despite minimizing registration error to 5mm and utilizing radial EBUS, the lesion could not be eccentrically or concentrically visualized. Consequently, the peripheral biopsy component was aborted to avoid non-diagnostic sampling of normal parenchyma."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "electromagnetic navigation bronchoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "mediastinal", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "EBUS-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "benign lymphocytes", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "1.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "apical", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "5mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sampling", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "parenchyma", 1)},
]
BATCH_DATA.append({"id": "991283_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 991283_syn_3
# ==========================================
text_3 = """Billing Codes: 31653 (EBUS-TBNA 3+ stations), 31627 (Navigational Bronchoscopy).
- EBUS: Stations 7, 4R, 4L sampled with needle aspiration. Cytology obtained.
- Navigation: Planning and registration performed. Catheter advanced to RUL target zone. Lesion not confirmed via Radial EBUS (31654 not billed/bundled as no specific image obtained). Biopsy (31628) not performed."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4L", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "sampled", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsy", 1)},
]
BATCH_DATA.append({"id": "991283_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 991283_syn_4
# ==========================================
text_4 = """Resident Note
Pt: [REDACTED]
Proc: EBUS + ENB
1. EBUS scope in. Sampled 7, 4R, 4L. ROSE: Benign.
2. Switched to therapeutic scope.
3. Loaded Veran map. Navigated to RUL.
4. Could not confirm target with REBUS.
5. Stopped procedure without biopsy of nodule.
Plan: Follow up or alternative biopsy method."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "ENB", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "EBUS scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Benign", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "therapeutic scope", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Veran map", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "biopsy", 2)},
]
BATCH_DATA.append({"id": "991283_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 991283_syn_5
# ==========================================
text_5 = """Procedure note for leo spaceman doing the ebus and navigation today. Ebus went fine we hit station 7 and 4r and 4l all looked benign on the slides. Switched to the nav scope for that RUL nodule. Tried to get there with the veran system but just couldnt see it on the radial probe. tried a few times but no luck so we didnt stick a needle in it. biopsy aborted just the lymph nodes done today."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "ebus", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "Ebus", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4r", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4l", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "benign", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "nav scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "veran system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "radial probe", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "lymph nodes", 1)},
]
BATCH_DATA.append({"id": "991283_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 991283_syn_6
# ==========================================
text_6 = """Electromagnetic Navigation Bronchoscopy and EBUS-TBNA were performed. Linear EBUS was used to sample lymph node stations 7, 4R, and 4L; all were benign on ROSE. Electromagnetic navigation was then attempted for a 1.8cm RUL nodule. Despite registration, the target was not localized with radial EBUS. The decision was made to abort the peripheral biopsy due to lack of target confirmation. The procedure was concluded without complications."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Electromagnetic Navigation Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS-TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "sample", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "lymph node stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "benign", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Electromagnetic navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "without complications", 1)},
]
BATCH_DATA.append({"id": "991283_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 991283_syn_7
# ==========================================
text_7 = """[Indication]
1.8cm RUL nodule, mediastinal staging.
[Anesthesia]
Moderate Sedation.
[Description]
EBUS-TBNA performed at stations 7, 4R, 4L. ROSE negative for malignancy. ENB attempted to RUL nodule. Lesion not visualized on Radial EBUS. Biopsy aborted.
[Plan]
Outpatient follow-up."""

entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "1.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "mediastinal", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "negative for malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "ENB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "Lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsy", 1)},
]
BATCH_DATA.append({"id": "991283_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 991283_syn_8
# ==========================================
text_8 = """We began the procedure with mediastinal staging using the linear EBUS scope. We successfully sampled lymph nodes at stations 7, 4R, and 4L, all of which showed benign lymphocytes on site. We then transitioned to the electromagnetic navigation phase to biopsy the RUL nodule. Although we navigated to the anatomical region, we could not confirm the lesion's location with radial EBUS. Therefore, we decided to abort the biopsy of the lung nodule to ensure patient safety."""

entities_8 = [
    {"label": "ANAT_PLEURA", **get_span(text_8, "mediastinal", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "staging", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "linear EBUS scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "benign lymphocytes", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "electromagnetic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 2)},
]
BATCH_DATA.append({"id": "991283_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 991283_syn_9
# ==========================================
text_9 = """Procedure: Endobronchial Ultrasound and Guided Navigation.
Details: Nodal stations 7, 4R, and 4L were aspirated; onsite analysis showed benign cells. The instruments were exchanged for the electromagnetic guidance system. We navigated to the RUL apex but failed to localize the target lesion with ultrasound. The tissue sampling of the parenchymal nodule was cancelled."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Endobronchial Ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Guided Navigation", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Nodal stations 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4L", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspirated", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "benign cells", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "electromagnetic guidance system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "apex", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "tissue sampling", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "parenchymal", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodule", 1)},
]
BATCH_DATA.append({"id": "991283_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 991283
# ==========================================
text_10 = """PROCEDURE: Electromagnetic Navigation Bronchoscopy & EBUS
PATIENT: [REDACTED] | MRN: [REDACTED]
DATE: [REDACTED]

**Plan:** Biopsy of 1.8cm RUL nodule and mediastinal staging.

**EBUS-TBNA:**
Linear EBUS scope inserted. 
- Station 7 (Subcarinal): 12mm node. Sampled x 3 passes. ROSE: Benign lymphocytes.
- Station 4R (Right Paratracheal): 10mm node. Sampled x 3 passes. ROSE: Benign lymphocytes.
- Station 4L: 8mm node. Sampled x 2 passes. ROSE: Benign lymphocytes.

**Navigation:**
Scope exchanged for therapeutic bronchoscope. Electromagnetic navigation (Veran) attempted to RUL apical segment nodule. Registration error 5mm. 
Despite multiple attempts and catheter adjustments, the target could not be successfully localized. Radial EBUS probe passed but no distinct lesion visualized (only normal lung parenchyma). 

**Decision:** Biopsy of the peripheral nodule was ABORTED due to lack of confirmation. No samples taken from RUL.

**Procedure concluded.**"""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Electromagnetic Navigation Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "mediastinal", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "staging", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS-TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Linear EBUS scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Subcarinal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "12mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Sampled", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Benign lymphocytes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Right Paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "10mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Sampled", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "Benign lymphocytes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "8mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Sampled", 3)},
    {"label": "MEAS_COUNT", **get_span(text_10, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Benign lymphocytes", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "therapeutic bronchoscope", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Veran", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "apical segment", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "5mm", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Radial EBUS probe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lung parenchyma", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Biopsy", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 3)},
]
BATCH_DATA.append({"id": "991283", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)