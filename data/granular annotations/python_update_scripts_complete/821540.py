import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is running from standard location, adjust strictly as requested
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Import the utility function
try:
    from scripts.add_training_case import add_case
    REPO_ROOT = root
except ImportError:
    # Fallback for manual testing contexts if needed, though strictly we use the import above
    print("WARNING: Could not import add_case. Ensure script is run within repo structure.")
    REPO_ROOT = Path(".")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    Returns a dictionary suitable for the entity list: {'start': int, 'end': int}.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 821540_syn_1
# ==========================================
id_1 = "821540_syn_1"
text_1 = """Indication: 2 nodules (RUL, RLL).
Proc: Robotic Nav + REBUS + TBBx.
Targets: RUL post (1.6cm), RLL sup (2.1cm).
Action: Navigated, confirmed REBUS. Biopsied both.
Result: Samples obtained.
Plan: D/C."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL post", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.6cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL sup", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "REBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsied", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 821540_syn_2
# ==========================================
id_2 = "821540_syn_2"
text_2 = """OPERATIVE NOTE: Robotic Navigational Bronchoscopy.
INDICATION: Bilateral pulmonary nodules.
PROCEDURE: A pre-operative CT was utilized for path planning. Using the robotic platform, the bronchoscope was navigated sequentially to the RUL posterior and RLL superior segments. Radial EBUS confirmed lesion location at both sites. Transbronchial biopsies were obtained from both targets without complication."""
entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Robotic Navigational Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "pulmonary nodules", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "robotic platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL posterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL superior", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "without complication", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 821540_syn_3
# ==========================================
id_3 = "821540_syn_3"
text_3 = """Codes: 31627 (Navigational Bronch), 31654 (REBUS), 31628 (TBBx 1st lobe), 31632 (TBBx addl lobe).
Details: Navigation used. REBUS used. Biopsies taken from RUL and RLL (2 separate lobes)."""
entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Navigational Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBBx", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBBx", 2)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "REBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 821540_syn_4
# ==========================================
id_4 = "821540_syn_4"
text_4 = """Procedure: Robotic Bronch
Patient: [REDACTED]
1. Navigated to RUL nodule -> REBUS confirm -> Biopsy x3.
2. Navigated to RLL nodule -> REBUS confirm -> Biopsy x4.
3. Fluoroscopy used.
4. No pneumo.
5. Good samples."""
entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Robotic Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x3", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodule", 2)},
    {"label": "PROC_METHOD", **get_span(text_4, "REBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 2)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x4", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Fluoroscopy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No pneumo", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 821540_syn_5
# ==========================================
id_5 = "821540_syn_5"
text_5 = """teresa johnson two spots on the lung right side. used the robot to get out there. found the top one with the ultrasound took some bites. then went to the bottom one found that too took more bites. everything went smooth no bleeding patient went home."""
entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "spots", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lung right side", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "bites", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "bites", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 821540_syn_6
# ==========================================
id_6 = "821540_syn_6"
text_6 = """Robotic assisted navigational bronchoscopy performed for peripheral pulmonary nodules. Targets in RUL and RLL localized using digital path planning and radial EBUS confirmation. Transbronchial forceps biopsies obtained from both sites. No complications."""
entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Robotic assisted navigational bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "pulmonary nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "digital path planning", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 821540_syn_7
# ==========================================
id_7 = "821540_syn_7"
text_7 = """[Indication]
Lung nodules RUL/RLL.
[Anesthesia]
General.
[Description]
Robotic Nav to RUL & RLL. REBUS confirmation. Transbronchial biopsies performed x2 lobes.
[Plan]
Discharge. CT f/u."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Robotic Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 2)},
    {"label": "PROC_METHOD", **get_span(text_7, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Transbronchial biopsies", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 821540_syn_8
# ==========================================
id_8 = "821540_syn_8"
text_8 = """[REDACTED] a robotic bronchoscopy today to biopsy two spots in her right lung. We used the robot to steer the camera deep into the lung to reach the spots in the upper and lower lobes. We confirmed we were in the right place with ultrasound and took biopsies from both. She did very well."""
entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "spots", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right lung", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "robot", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "spots", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "upper and lower lobes", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 821540_syn_9
# ==========================================
id_9 = "821540_syn_9"
text_9 = """Procedure: Computer-assisted navigational bronchoscopy.
Targets: RUL and RLL peripheral lesions.
Verification: Radial endobronchial ultrasound.
Intervention: Transbronchial biopsy of multiple lobes.
Outcome: Tissue acquisition successful."""
entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Computer-assisted navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesions", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Radial endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Transbronchial biopsy", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 821540
# ==========================================
id_10 = "821540"
text_10 = """ROBOTIC NAVIGATIONAL BRONCHOSCOPY NOTE
Patient: [REDACTED] | 59F | MRN [REDACTED]
Date: [REDACTED]
Institution: [REDACTED]
Attending: Dr. Kevin Li
Fellow: Dr. Nora Steele

INDICATION:
Two enlarging peripheral pulmonary nodules (right upper lobe posterior segment 1.6 cm; right lower lobe superior segment 2.1 cm) in a 30-pack-year former smoker with COPD. PET shows both nodules mildly FDG-avid without clear nodal disease.

PROCEDURES PERFORMED:
- Robotic navigational bronchoscopy with computer-assisted image-guided navigation (CPT 31627)
- Radial EBUS for peripheral lesion localization (CPT 31654)
- Transbronchial lung biopsy, first lobe (CPT 31628)
- Transbronchial lung biopsy, additional lobe (add-on CPT +31632)

ANESTHESIA: General anesthesia with 8.0 ETT

PROCEDURE SUMMARY:
Pre-procedure planning CT was loaded into the robotic platform and pathways were created to the RUL posterior segment and RLL superior segment targets.

After induction, the robotic bronchoscope was navigated to the RUL target. Radial EBUS demonstrated a concentric hypoechoic lesion. Three transbronchial forceps biopsies and one cytology brush were obtained from the RUL posterior segment.

The robot was then redirected to the RLL superior segment. Radial EBUS again confirmed an eccentric lesion abutting an airway. Four forceps biopsies were obtained from the RLL.

No linear EBUS was performed and no fiducial markers or ablation were placed. Fluoroscopy showed no immediate pneumothorax.

COMPLICATIONS: None; estimated blood loss ~15 mL.
DISPOSITION: Extubated in the OR, recovered in PACU and discharged home the same day with clinic and CT follow up arranged."""
entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "ROBOTIC NAVIGATIONAL BRONCHOSCOPY", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "peripheral pulmonary nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right upper lobe posterior segment", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.6 cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lower lobe superior segment", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.1 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Robotic navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "computer-assisted image-guided navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial lung biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial lung biopsy", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "robotic platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL posterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL superior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "robotic bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Three", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cytology brush", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL posterior segment", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL superior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 3)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 3)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Four", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Fluoroscopy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no immediate pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")