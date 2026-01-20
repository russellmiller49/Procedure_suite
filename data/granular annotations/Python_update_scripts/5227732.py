import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 5227732_syn_1
# ==========================================
t1 = """Target: 13mm Lingula nodule.
Tech: Monarch robot. rEBUS Concentric.
Bx: 22G TBNA x5. Brush.
No BAL.
ROSE: Suspicious."""
e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "13mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Monarch robot", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22G", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Suspicious", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 5227732_syn_2
# ==========================================
t2 = """NARRATIVE: The patient underwent robotic bronchoscopy for a 13mm incidental nodule in the Superior Lingula. Electromagnetic navigation was precise (2.0mm error). Navigation to LB4 was achieved. Radial EBUS revealed a concentric view, confirming the target. We proceeded with Transbronchial Needle Aspiration using a 22G needle (5 passes) and protected specimen brushing. No lavage was performed. On-site pathology was suspicious for malignancy."""
e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "robotic bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "13mm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Superior Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Electromagnetic navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "2.0mm", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Transbronchial Needle Aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "5 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "protected specimen brushing", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "suspicious", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 5227732_syn_3
# ==========================================
t3 = """Coding: 31629 (TBNA), 31623 (Brush), 31627 (Nav), 31654 (EBUS). Note: No BAL performed. Navigated to Lingula (LB4). rEBUS concentric view confirmed target. 22G needle used."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "needle", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 5227732_syn_4
# ==========================================
t4 = """Steps:
1. GA/ETT.
2. Robot to Lingula.
3. rEBUS: Concentric.
4. 22G Needle x 5.
5. Brush.
ROSE: Suspicious.
Plan: CXR."""
e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "Needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x 5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Suspicious", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 5227732_syn_5
# ==========================================
t5 = """rivera kenneth lingula nodule 13mm robotic bronchoscopy navigation was good 2mm error went to lb4 rebus concentric 22g needle 5 passes brush too rose says suspicious no bal done bleeding minimal."""
e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lingula", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "13mm", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lb4", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rebus", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "suspicious", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "bal", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "bleeding minimal", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 5227732_syn_6
# ==========================================
t6 = """The patient was intubated. Monarch robotic system used. Navigated to Superior Lingula LB4. Registration error 2.0mm. rEBUS showed concentric view. 22G TBNA performed 5 times. Protected brushings obtained. ROSE reported atypical cells suspicious for malignancy. No complications."""
e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Monarch robotic system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "Superior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LB4", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "2.0mm", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "22G", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "5 times", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Protected brushings", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "atypical cells", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "suspicious", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 5227732_syn_7
# ==========================================
t7 = """[Indication] 13mm Lingula nodule.
[Anesthesia] General.
[Description] Nav to Lingula. rEBUS concentric. 22G TBNA x5. Brush. No BAL.
[Plan] Recovery."""
e7 = [
    {"label": "MEAS_SIZE", **get_span(t7, "13mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Lingula", 2)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "22G", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "BAL", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 5227732_syn_8
# ==========================================
t8 = """We guided the robotic bronchoscope to the superior segment of the Lingula. The electromagnetic registration was excellent. We confirmed the lesion location with a concentric view on radial EBUS. We then took five samples using a 22-gauge needle and obtained additional cells with a cytology brush. The on-site pathologist id[REDACTED] cells suspicious for cancer."""
e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "robotic bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "superior segment of the Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "electromagnetic registration", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "five samples", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "cytology brush", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "suspicious", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 5227732_syn_9
# ==========================================
t9 = """The robotic probe was steered to the Lingula. Registration variance was 2.0mm. The scope was parked at LB4. Sonographic assessment showed a concentric target. Needle aspiration was performed with a 22G device for 5 cycles. Brushing was also executed. Early pathology indicated malignancy."""
e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "robotic probe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Lingula", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "2.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LB4", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "22G", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "5 cycles", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Brushing", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "malignancy", 1)},
]
BATCH_DATA.append({"id": "5227732_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 5227732
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Emily Thompson
Fellow: Dr. Kevin Patel (PGY-5)

Indication: Incidental pulmonary nodule requiring tissue diagnosis
Target: 13mm nodule in Lingula

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PRVC\t12\t321\t18\t80\t8\t24

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 2.0mm.

The device was navigated to the Lingula. The outer sheath was parked and locked at the ostium of the segmental airway (LB4) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Superior Lingula.

Radial EBUS performed via the working channel. rEBUS view: Concentric. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 22G aspiration needle under direct endoscopic and fluoroscopic guidance. 5 passes performed. Samples sent for Cytology and Cell block.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

ROSE Result: Atypical cells present, suspicious for malignancy

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Thompson, MD"""
e10 = [
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "13mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "normal caliber", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Monarch robotic endoscope", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Electromagnetic registration", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Superior Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22G", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Protected cytology brushings", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Atypical cells present", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "suspicious", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": "5227732", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)