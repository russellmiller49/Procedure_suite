import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Case 1: 700009_syn_1
# ==========================================
id_1 = "700009_syn_1"
text_1 = """Proc: EBUS (4R, 7, 11R) + EM Nav (RLL mass).
Findings:
- EBUS: 4R/7 malignant.
- Nav: Tool in lesion, fluoroscopy confirmed.
- Bx: 5 samples RLL mass.
Comp: None.
Plan: Oncology referral."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EM Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Tool", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 samples", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 700009_syn_2
# ==========================================
id_2 = "700009_syn_2"
text_2 = """OPERATIVE REPORT: Combined EBUS-TBNA and electromagnetic navigational bronchoscopy. 
INDICATION: Staging and diagnosis for 71F with RLL mass and adenopathy.
EBUS: Stations 4R, 7, and 11R sampled. Malignancy confirmed at 4R/7.
NAVIGATION: The superDimension system was used to navigate to the RLL basilar segment lesion. Transbronchial biopsies were obtained under fluoroscopic guidance. 
CONCLUSION: Stage IIIA/B lung cancer (N2 disease)."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "electromagnetic navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "11R", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sampled", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "Malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 2)},
    {"label": "PROC_METHOD", **get_span(text_2, "superDimension", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL basilar segment", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial biopsies", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "fluoroscopic guidance", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 700009_syn_3
# ==========================================
id_3 = "700009_syn_3"
text_3 = """Codes:
- 31653: EBUS 3+ stations (4R, 7, 11R).
- 31627: Navigational bronchoscopy.
- 31628: TBLB single lobe (RLL).
Rational: EBUS for staging, Nav/TBLB for primary lesion diagnosis. Distinct services."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "11R", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigational bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBLB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBLB", 2)},
    {"label": "OBS_LESION", **get_span(text_3, "lesion", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 700009_syn_4
# ==========================================
id_4 = "700009_syn_4"
text_4 = """Procedure: EBUS + Nav Bronch
Patient: [REDACTED]
Steps:
1. EBUS: 4R, 7, 11R sampled.
2. Nav: Registered CT. Navigated to RLL mass.
3. TBLB: 5 passes.
4. Fluoro confirmed position.
Events: Minor bleeding, stopped w/ saline."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Nav Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "11R", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "sampled", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBLB", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "5 passes", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Fluoro", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "Minor bleeding", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 700009_syn_5
# ==========================================
id_5 = "700009_syn_5"
text_5 = """Double procedure for [REDACTED] and diagnosis. Started with EBUS hit 4R 7 and 11R rose said cancer in the mediastinum. Then switched to the nav scope for the RLL mass. Got right to it with the superD. Took 5 biopsies looks diagnostic. Patient did fine."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "mediastinum", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "nav", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "superD", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "5", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 700009_syn_6
# ==========================================
id_6 = "700009_syn_6"
text_6 = """Combined EBUS-TBNA and electromagnetic navigational bronchoscopy. Stations 4R, 7, 11R sampled; malignancy at 4R/7. Navigational bronchoscopy to RLL mass performed with fluoroscopic confirmation. Transbronchial biopsies obtained. No complications."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "electromagnetic navigational bronchoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "11R", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "sampled", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 2)},
    {"label": "PROC_METHOD", **get_span(text_6, "Navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "fluoroscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Transbronchial biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 700009_syn_7
# ==========================================
id_7 = "700009_syn_7"
text_7 = """[Indication]
RLL mass, mediastinal adenopathy.
[Anesthesia]
General.
[Description]
1. EBUS-TBNA stations 4R, 7, 11R.
2. EM Navigation to RLL mass.
3. Transbronchial biopsy RLL.
[Plan]
Oncology follow-up."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mediastinal adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "11R", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EM Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 2)},
    {"label": "PROC_ACTION", **get_span(text_7, "Transbronchial biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 3)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 700009_syn_8
# ==========================================
id_8 = "700009_syn_8"
text_8 = """We performed a combined staging and diagnostic procedure for [REDACTED]. First, we used EBUS to sample nodes at stations 4R, 7, and 11R, confirming malignancy in the mediastinum. Then, using electromagnetic navigation, we guided a scope to her RLL mass and obtained several biopsies. This provides both the diagnosis and the stage in one session."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "sample", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "11R", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "mediastinum", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 700009_syn_9
# ==========================================
id_9 = "700009_syn_9"
text_9 = """Procedure: Ultrasound-guided nodal aspiration and computer-assisted parenchymal biopsy.
Target: Mediastinal nodes and RLL tumor.
Action: EBUS-TBNA was performed on 3 stations. The RLL lesion was localized via EM guidance and sampled.
Result: Diagnosis and staging completed."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "computer-assisted", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "parenchymal biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Mediastinal nodes", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "TBNA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "EM guidance", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampled", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 700009
# ==========================================
id_10 = "700009"
text_10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (71 years)
DATE OF SERVICE: [REDACTED]
LOCATION: Bronchoscopy Suite

PROCEDURES:
1. Flexible bronchoscopy with linear EBUS-TBNA of mediastinal/hilar lymph nodes.
2. Electromagnetic navigational bronchoscopy to right lower lobe lesion.
3. Transbronchial lung biopsies of right lower lobe lesion.

OPERATOR: Jason Miller, MD (Interventional Pulmonology)
FELLOW: Priya Shah, MD (PGY-6)

INDICATION:
71-year-old female with a 2.5 cm right lower lobe mass and enlarged PET-avid subcarinal and right paratracheal nodes. Referred for combined mediastinal staging and bronchoscopic diagnosis of the parenchymal lesion.

ANESTHESIA/AIRWAY:
General anesthesia with ETT. Patient in supine position.

EBUS-TBNA:
A convex probe EBUS bronchoscope was used for systematic mediastinal staging. Nodes were id[REDACTED] and sampled as follows:
• Station 4R: 1.4 cm, oval; 3 passes with 22G needle.
• Station 7: 2.0 cm, heterogeneous; 4 passes with 22G needle.
• Station 11R: 1.1 cm; 3 passes with 22G needle.
ROSE was adequate at all stations, with malignant cells seen at 4R and 7.

NAVIGATIONAL BRONCHOSCOPY/TBLB:
After completing EBUS, an electromagnetic navigation system (superDimension) was used. The pre-procedure CT was registered and the right lower lobe lesion target planned. Navigation error was approximately 2.5 mm.

A thin bronchoscope was advanced along the projected path to a subsegmental bronchus in the basilar segment of the RLL. The target lesion was reached and confirmed by fluoroscopy. Multiple transbronchial biopsies (5 forceps samples) and cytology brushings (2) were obtained from the lesion.

COMPLICATIONS:
Minor bleeding controlled with cold saline and suction. No significant hypoxia or pneumothorax observed. Estimated blood loss < 10 mL.

DISPOSITION:
The patient was extubated and transferred to PACU in stable condition, with a post-procedure CXR ordered. She will follow up in IP clinic in 1–2 weeks.

IMPRESSION:
Combined EBUS-TBNA of 4R, 7, and 11R nodes and navigational bronchoscopy with fluoroscopic confirmation and transbronchial biopsies of an RLL mass."""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "linear EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal/hilar lymph nodes", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Electromagnetic navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial lung biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lower lobe", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.5 cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lower lobe", 3)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "right paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "diagnosis", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "convex probe EBUS bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Nodes", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.4 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.0 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G needle", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.1 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignant cells", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "NAVIGATIONAL BRONCHOSCOPY", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBLB", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "electromagnetic navigation system", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "superDimension", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lower lobe", 4)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 4)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "thin bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "subsegmental bronchus", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "basilar segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 5)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cytology brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "2", 4)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 6)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Minor bleeding", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "< 10 mL", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 4)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "11R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "nodes", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic confirmation", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial biopsies", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 2)}
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)