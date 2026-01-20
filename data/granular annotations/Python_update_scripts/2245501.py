import sys
from pathlib import Path

# Calculate the root of the repository to import the helper script
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 2245501_syn_1
# ==========================================
text_1 = """Indication: 18mm GGO Lingula.
Proc: Ion Nav, rEBUS (Adjacent).
Action: TBNA (23G x4). Fiducial placement (0.8x3mm gold).
ROSE: Adenocarcinoma.
Plan: SBRT planning."""

entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "18mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "GGO", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Adjacent", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Fiducial placement", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "0.8x3mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2245501_syn_2
# ==========================================
text_2 = """NARRATIVE: [REDACTED] biopsy and fiducial placement regarding an 18mm ground glass opacity in the Lingula (LB5). Using the Ion platform, we navigated to the target. Radial EBUS showed an adjacent view. Transbronchial needle aspiration confirmed adenocarcinoma on ROSE. Subsequently, a gold fiducial marker (CIVCO) was deployed under fluoroscopic guidance to facilitate future stereotactic radiotherapy."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "fiducial placement", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "18mm", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "ground glass opacity", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Ion platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "adjacent", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial needle aspiration", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "adenocarcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "fiducial marker", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "fluoroscopic", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2245501_syn_3
# ==========================================
text_3 = """Coding: 31626 (Fiducials), 31629 (TBNA), +31627 (Nav), +31654 (rEBUS).
Target: Lingula (LB5).
Justification: Biopsy confirmed malignancy (Adeno), fiducial placed for SBRT.
Tools: Ion, Fluoroscopy."""

entities_3 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Fiducials", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "rEBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LB5", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsy", 1)},
    {"label": "OBS_ROSE", **get_span(text_3, "malignancy", 1)},
    {"label": "OBS_ROSE", **get_span(text_3, "Adeno", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "fiducial", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Fluoroscopy", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2245501_syn_4
# ==========================================
text_4 = """Procedure: Ion Bronch + Fiducial
Pt: [REDACTED]

1. Nav to Lingula LB5.
2. rEBUS: Adjacent.
3. TBNA x4 (23G).
4. ROSE: Adenocarcinoma.
5. Placed 1 gold fiducial.
6. No complications."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Ion", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Bronch", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Fiducial", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Adjacent", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "4", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "23G", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Adenocarcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "fiducial", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No complications", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2245501_syn_5
# ==========================================
text_5 = """sarah martin here for biopsy and fiducial. 18mm ggo in the lingula lb5. ion robot used. radial ebus adjacent. took 4 needle samples. rose said adenocarcinoma. put in a gold fiducial marker for radiation. everything went fine."""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fiducial", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "18mm", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "ggo", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lb5", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ion robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "radial ebus", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "adjacent", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "4", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "adenocarcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fiducial marker", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2245501_syn_6
# ==========================================
text_6 = """Robotic navigation bronchoscopy (Ion) for 18mm Lingula GGO (LB5). Registration error 3.1mm. Radial EBUS: Adjacent. Sampling: TBNA (23G, 4 passes). ROSE: Adenocarcinoma. Fiducial marker placed under fluoroscopy. No complications."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Robotic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Ion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "18mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "GGO", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Adjacent", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "4", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "Adenocarcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Fiducial marker", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "fluoroscopy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2245501_syn_7
# ==========================================
text_7 = """[Indication]
GGO Lingula, 18mm.
[Anesthesia]
General.
[Description]
Ion nav to Inferior Lingula (LB5). rEBUS: Adjacent. 
- TBNA (23G)
- Fiducial placement
ROSE: Adenocarcinoma.
[Plan]
Radiation Oncology referral."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "GGO", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "Lingula", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "18mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Ion nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Adjacent", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "23G", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Fiducial placement", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2245501_syn_8
# ==========================================
text_8 = """[REDACTED] bronchoscopy for an 18mm nodule in the Lingula. After navigating with the Ion system and confirming location with adjacent radial EBUS, we performed needle aspiration which confirmed adenocarcinoma. We then placed a gold fiducial marker to aid in future radiation treatment."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "18mm", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Ion system", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "adjacent", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "needle aspiration", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "adenocarcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "fiducial marker", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2245501_syn_9
# ==========================================
text_9 = """Procedure: Robotic-assisted endoscopy with marker implantation.
Site: Inferior Lingula (LB5).
Sampling: Needle aspiration (TBNA) confirmed adenocarcinoma.
Intervention: A fiducial marker was deployed for radiotherapy guidance."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic-assisted", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "endoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "marker implantation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LB5", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "TBNA", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "adenocarcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "fiducial marker", 1)},
]
BATCH_DATA.append({"id": "2245501_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 2245501
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Rachel Kim

Indication: Ground glass opacity requiring biopsy
Target: 18mm nodule in Lingula

PROCEDURE:

After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings:

The endotracheal tube is in good position. The visualized portion of the trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy are normal; there are no endobronchial lesions.

Successful therapeutic aspiration was performed to clean out the Right Mainstem, RUL Carina (RC1), Carina, LUL Lingula Carina (LC1), Left Mainstem from mucus.

CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target. The navigational plan was reviewed and verified. This was then loaded into robotic bronchoscopy platform.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t13\t361\t15\t100\t5\t16

Robotic navigation bronchoscopy was performed with Ion platform. Full registration was used. Registration error: 3.1mm. Ion robotic catheter was used to engage the Inferior Lingula (LB5). Target lesion is approximately 18mm in diameter. Under navigational guidance the Ion robotic catheter was advanced to 1.6cm away from the planned target.

Radial EBUS was performed to confirm lesion location. rEBUS view: Adjacent. Continuous margin noted.

The robotic arm was actively locked to maintain rigidity. Vision probe was unlocked and removed from the working channel, leaving the outer catheter locked in position via shape-sensing technology.

Transbronchial needle aspiration was performed with 23G Needle through the extended working channel catheter. Total 4 samples were collected. Samples sent for Cytology and Cell block.

Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.

ROSE Result: Malignant cells id[REDACTED], consistent with adenocarcinoma

Vision probe was re-inserted to inspect the airway. No significant bleeding observed. The catheter was retracted. Final airway inspection showed no complications.

The patient tolerated the procedure well without immediate complications.

DISPOSITION: Recovery, then discharge if stable. CXR to rule out pneumothorax.
Follow-up: Results conference in 5-7 days.

Kim, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Ground glass opacity", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "18mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Lingula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Right Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RUL Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RC1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Carina", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LUL Lingula Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LC1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Left Mainstem", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Robotic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchoscopy", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB5", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "18mm", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion robotic catheter", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Adjacent", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "23G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cell block", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Fiducial marker", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "0.8mm x 3mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopy", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no complications", 1)},
]
BATCH_DATA.append({"id": "2245501", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)