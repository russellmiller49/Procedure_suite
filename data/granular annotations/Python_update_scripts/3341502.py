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
# 2. Helper Functions
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
# Note 1: 3341502_syn_1
# ==========================================
id_1 = "3341502_syn_1"
text_1 = """Loc: LUL (LB3).
Size: 27mm.
Nav: Monarch (4.2mm error).
rEBUS: Adjacent.
Bx: 19G TBNA (4x), Forceps (6x).
ROSE: Granuloma."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB3", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "27mm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "Monarch", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "4.2mm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "rEBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_1, "19G", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_1, "4x", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_1, "6x", 1)},
    {"label": "OBS_ROSE",      **get_span(text_1, "Granuloma", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 3341502_syn_2
# ==========================================
id_2 = "3341502_syn_2"
text_2 = """PROCEDURE: Robotic bronchoscopy for a growing 27mm LUL nodule. Navigation to the Anterior Segment (LB3) was completed. Radial EBUS id[REDACTED] the lesion with an adjacent orientation. We obtained diagnostic tissue via 19G Transbronchial Needle Aspiration (4 passes) and Transbronchial Forceps Biopsy (6 specimens). No lavage was performed. On-site pathology indicated granulomatous inflammation."""

entities_2 = [
    {"label": "PROC_METHOD",   **get_span(text_2, "Robotic bronchoscopy", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_2, "27mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB3", 1)},
    {"label": "PROC_METHOD",   **get_span(text_2, "Radial EBUS", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "lesion", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_2, "19G", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "Transbronchial Needle Aspiration", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_2, "4 passes", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_2, "Forceps", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "Biopsy", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_2, "6 specimens", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "lavage", 1)},
    {"label": "OBS_ROSE",      **get_span(text_2, "granulomatous inflammation", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 3341502_syn_3
# ==========================================
id_3 = "3341502_syn_3"
text_3 = """Billing 31629, 31628, 31627, 31654. Note: No BAL. 19G TBNA x4 and Forceps x6 in LUL. rEBUS used for confirmation. Continuous guidance maintained."""

entities_3 = [
    {"label": "PROC_ACTION",   **get_span(text_3, "BAL", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_3, "19G", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3, "TBNA", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_3, "x4", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_3, "Forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_3, "x6", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "rEBUS", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 3341502_syn_4
# ==========================================
id_4 = "3341502_syn_4"
text_4 = """Procedure: Monarch LUL Biopsy.
Target: 27mm nodule.
1. Nav to LB3.
2. rEBUS: Adjacent.
3. 19G TBNA x 4.
4. Forceps x 6.
ROSE: Granulomatous.
No BAL."""

entities_4 = [
    {"label": "PROC_METHOD",   **get_span(text_4, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 1)},
    {"label": "PROC_ACTION",   **get_span(text_4, "Biopsy", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_4, "27mm", 1)},
    {"label": "OBS_LESION",    **get_span(text_4, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB3", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "rEBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_4, "19G", 1)},
    {"label": "PROC_ACTION",   **get_span(text_4, "TBNA", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_4, "x 4", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_4, "Forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_4, "x 6", 1)},
    {"label": "OBS_ROSE",      **get_span(text_4, "Granulomatous", 1)},
    {"label": "PROC_ACTION",   **get_span(text_4, "BAL", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 3341502_syn_5
# ==========================================
id_5 = "3341502_syn_5"
text_5 = """[REDACTED] lul nodule 27mm monarch robot used registration 4.2mm error navigated to lb3 rebus adjacent 19g needle 4 times forceps 6 times rose says granuloma no bal bleeding stopped easily."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lul", 1)},
    {"label": "OBS_LESION",    **get_span(text_5, "nodule", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_5, "27mm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_5, "monarch robot", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_5, "4.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lb3", 1)},
    {"label": "PROC_METHOD",   **get_span(text_5, "rebus", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_5, "19g", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_5, "4 times", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_5, "forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_5, "6 times", 1)},
    {"label": "OBS_ROSE",      **get_span(text_5, "granuloma", 1)},
    {"label": "PROC_ACTION",   **get_span(text_5, "bal", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "bleeding stopped easily", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 3341502_syn_6
# ==========================================
id_6 = "3341502_syn_6"
text_6 = """Anesthesia induced. Monarch robot navigated to LUL Anterior Segment. Registration error 4.2mm. rEBUS adjacent. 19G TBNA performed 4 times. Forceps biopsy performed 6 times. ROSE showed granulomatous inflammation. No BAL performed. Patient stable."""

entities_6 = [
    {"label": "PROC_METHOD",   **get_span(text_6, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "Anterior Segment", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_6, "4.2mm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_6, "rEBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_6, "19G", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "TBNA", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_6, "4 times", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_6, "Forceps", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "biopsy", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_6, "6 times", 1)},
    {"label": "OBS_ROSE",      **get_span(text_6, "granulomatous inflammation", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "BAL", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 3341502_syn_7
# ==========================================
id_7 = "3341502_syn_7"
text_7 = """[Indication] 27mm LUL nodule.
[Anesthesia] General.
[Description] Nav to LB3. rEBUS adjacent. 19G TBNA x4. Forceps x6. ROSE granuloma.
[Plan] Follow up."""

entities_7 = [
    {"label": "MEAS_SIZE",     **get_span(text_7, "27mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_7, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB3", 1)},
    {"label": "PROC_METHOD",   **get_span(text_7, "rEBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_7, "19G", 1)},
    {"label": "PROC_ACTION",   **get_span(text_7, "TBNA", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_7, "x4", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_7, "Forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_7, "x6", 1)},
    {"label": "OBS_ROSE",      **get_span(text_7, "granuloma", 1)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 3341502_syn_8
# ==========================================
id_8 = "3341502_syn_8"
text_8 = """We utilized the Monarch robot to navigate to the anterior segment of the left upper lobe. After confirming the target with adjacent radial EBUS views, we sampled the 27mm nodule. We used a 19-gauge needle for four passes and forceps for six bites. The on-site evaluation suggested granulomatous inflammation, so no further sampling was needed."""

entities_8 = [
    {"label": "PROC_METHOD",   **get_span(text_8, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "anterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left upper lobe", 1)},
    {"label": "PROC_METHOD",   **get_span(text_8, "radial EBUS", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_8, "27mm", 1)},
    {"label": "OBS_LESION",    **get_span(text_8, "nodule", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_8, "19-gauge", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_8, "four passes", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_8, "forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_8, "six bites", 1)},
    {"label": "OBS_ROSE",      **get_span(text_8, "granulomatous inflammation", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 3341502_syn_9
# ==========================================
id_9 = "3341502_syn_9"
text_9 = """The robotic instrument was guided to the LUL. Registration variance was 4.2mm. The scope reached LB3. Sonography indicated an adjacent mass. Aspiration with a 19G needle was done 4 times. Tissue extraction via forceps occurred 6 times. Initial pathology revealed granuloma."""

entities_9 = [
    {"label": "PROC_METHOD",   **get_span(text_9, "robotic", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_9, "instrument", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LUL", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_9, "4.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LB3", 1)},
    {"label": "OBS_LESION",    **get_span(text_9, "mass", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "Aspiration", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_9, "19G", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_9, "4 times", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "Tissue extraction", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_9, "forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_9, "6 times", 1)},
    {"label": "OBS_ROSE",      **get_span(text_9, "granuloma", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})


# ==========================================
# Note 10: 3341502
# ==========================================
id_10 = "3341502"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Rachel Kim
Fellow: Dr. Kevin Patel (PGY-5)

Indication: Growing lung nodule on surveillance
Target: 27mm nodule in LUL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PRVC\t13\t286\t13\t100\t6\t23

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 4.2mm.

The device was navigated to the LUL. The outer sheath was parked and locked at the ostium of the segmental airway (LB3) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Anterior Segment of LUL.

Radial EBUS performed via the working channel. rEBUS view: Adjacent. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 19G aspiration needle under direct endoscopic and fluoroscopic guidance. 4 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 6 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

ROSE Result: Granulomatous inflammation

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Kim, MD"""

entities_10 = [
    {"label": "OBS_LESION",    **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_10, "27mm", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "carina", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "lesions", 1)},
    {"label": "OBS_FINDING",   **get_span(text_10, "secretions", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "suction", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "Monarch", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "robotic endoscope", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "Electromagnetic registration", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "main carina", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "right", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "left mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "lobar carinas", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_10, "4.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 2)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "outer sheath", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB3", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "inner scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 3)},
    {"label": "PROC_METHOD",   **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "rEBUS", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(text_10, "bronchial wall", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE",    **get_span(text_10, "19G", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "fluoroscopic", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_10, "4 passes", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "forceps", 1)},
    {"label": "MEAS_COUNT",    **get_span(text_10, "6 specimens", 1)},
    {"label": "OBS_ROSE",      **get_span(text_10, "Granulomatous inflammation", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "robotic system", 1)}
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)