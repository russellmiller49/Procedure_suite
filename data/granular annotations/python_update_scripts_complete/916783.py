import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add cases
# Ensure the 'scripts' module is in the python path or adjust relative import as needed for your environment
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

# List to hold all processed case data
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
        
    Returns:
        tuple: (start_index, end_index)
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return start, start + len(term)

# ==========================================
# Note 1: 916783_syn_1
# ==========================================
id_1 = "916783_syn_1"
text_1 = """Target: 34mm RUL mass.
Actions:
- Monarch nav to RB2.
- rEBUS: Concentric.
- TBNA (21G), Forceps x8, Brush.
- BAL (RB2).
- Fiducial placed.
ROSE: Suspicious for NSCC.
Plan: SBRT planning/Onc referral."""

entities_1 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "34mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RUL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "mass", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "Monarch", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RB2", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "TBNA", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_1, "21G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Forceps", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_1, "x8", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "BAL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_1, "RB2", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "Fiducial placed", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_1, "Suspicious for NSCC", 1)))},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 916783_syn_2
# ==========================================
id_2 = "916783_syn_2"
text_2 = """OPERATIVE REPORT: [REDACTED] a suspicious 34mm RUL mass. Following induction of general anesthesia, the Monarch robotic system was introduced. Navigation to the Posterior Segment of the RUL was successful (Registration error 4.0mm). Radial EBUS demonstrated a concentric view. We performed extensive sampling including TBNA (21G), forceps biopsy, and protected brushing. A bronchoalveolar lavage was performed at the target segment. Finally, a gold fiducial marker was deployed for future radiation planning. ROSE was suspicious for non-small cell carcinoma."""

entities_2 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_2, "34mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_2, "RUL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "mass", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "Monarch robotic system", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_2, "Posterior Segment", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_2, "RUL", 2)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "Radial EBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "TBNA", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_2, "21G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "biopsy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "brushing", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "bronchoalveolar lavage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "fiducial marker was deployed", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_2, "suspicious for non-small cell carcinoma", 1)))},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 916783_syn_3
# ==========================================
id_3 = "916783_syn_3"
text_3 = """Billing Summary:
- 31629 (TBNA)
- 31628 (Forceps Bx)
- 31623 (Brush)
- 31624 (BAL)
- 31626 (Fiducial)
- 31627 (Nav)
- 31654 (EBUS)
Justification: Multimodal sampling of 34mm RUL lesion plus marker placement for SBRT. All distinct techniques used."""

entities_3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "Forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Bx", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "Brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "BAL", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Fiducial", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "Nav", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "EBUS", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_3, "34mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_3, "RUL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_3, "lesion", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "marker placement", 1)))},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 916783_syn_4
# ==========================================
id_4 = "916783_syn_4"
text_4 = """Resident Note
Pt: [REDACTED].
Indication: Lung mass RUL.
Steps:
1. GA, ETT.
2. Nav to RUL Posterior.
3. rEBUS concentric.
4. TBNA x5, Bx x8, Brush.
5. BAL performed.
6. Fiducial dropped.
ROSE: Suspicious for NSCC.
Complications: None."""

entities_4 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_4, "mass", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_4, "RUL", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_4, "Nav", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_4, "RUL Posterior", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_4, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "TBNA", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_4, "x5", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Bx", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_4, "x8", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "BAL", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Fiducial dropped", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_4, "Suspicious for NSCC", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_4, "None", 1)))},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 916783_syn_5
# ==========================================
id_5 = "916783_syn_5"
text_5 = """Procedure note for Steven Rodriguez big nodule 34mm in the RUL. We used the monarch system navigated to RB2. EBUS was concentric so good hit. Did the works needle 21g forceps brush and a lavage. Also put in a gold marker for radiation. Pathology says suspicious for non small cell. No bleeding patient woke up fine."""

entities_5 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "nodule", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_5, "34mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_5, "RUL", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_5, "monarch system", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_5, "RB2", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_5, "EBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_5, "needle", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_5, "21g", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_5, "lavage", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_5, "suspicious for non small cell", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_5, "No bleeding", 1)))},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 916783_syn_6
# ==========================================
id_6 = "916783_syn_6"
text_6 = """Robotic bronchoscopy targeting a 34mm RUL mass was performed under GA. Navigation to the posterior segment (RB2) was achieved. rEBUS showed a concentric view. Samples were obtained via 21G TBNA, forceps biopsy, and brush. Bronchoalveolar lavage was performed. A gold fiducial marker was placed under fluoroscopic guidance. ROSE reported suspicion of non-small cell carcinoma. The patient tolerated the procedure well."""

entities_6 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "Robotic bronchoscopy", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_6, "34mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "RUL", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "mass", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "posterior segment", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_6, "RB2", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_6, "21G", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "biopsy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "Bronchoalveolar lavage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "placed", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "fluoroscopic guidance", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_6, "suspicion of non-small cell carcinoma", 1)))},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 916783_syn_7
# ==========================================
id_7 = "916783_syn_7"
text_7 = """[Indication]
Suspected malignancy, RUL mass (34mm).
[Anesthesia]
General, 8.0 ETT.
[Description]
Monarch nav to RB2. rEBUS: Concentric. Sampling: 21G TBNA, Forceps, Brush. BAL performed. Gold fiducial placed. ROSE: Suspicious for NSCC.
[Plan]
CXR, Discharge, Oncology follow-up."""

entities_7 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "mass", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_7, "RUL", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_7, "34mm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "Monarch", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_7, "RB2", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_7, "21G", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "Forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "Brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "BAL", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "fiducial placed", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_7, "Suspicious for NSCC", 1)))},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 916783_syn_8
# ==========================================
id_8 = "916783_syn_8"
text_8 = """[REDACTED] for biopsy of a large 34mm mass in the right upper lobe. Under general anesthesia, we used the Monarch robot to find the lesion in the posterior segment. The EBUS view was concentric, confirming we were inside the lesion. We took multiple samples with a needle, forceps, and brush, and also washed the area (BAL). Since radiation might be needed, we placed a fiducial marker. The preliminary path read was suspicious for non-small cell cancer."""

entities_8 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "biopsy", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_8, "34mm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "mass", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_8, "right upper lobe", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "Monarch robot", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "lesion", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_8, "posterior segment", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "EBUS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "lesion", 2)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_8, "needle", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "brush", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "washed", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "BAL", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "placed a fiducial marker", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_8, "suspicious for non-small cell cancer", 1)))},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 916783_syn_9
# ==========================================
id_9 = "916783_syn_9"
text_9 = """Procedure: Robotic bronchoscopy with multimodal sampling and marker implantation.
Site: RUL Posterior Segment.
Action: The robotic scope was navigated to the lesion. rEBUS confirmed concentricity. The mass was aspirated, biopsied, and brushed. Lavage was conducted. A fiducial marker was implanted.
Result: ROSE indicated suspicion of carcinoma. No complications."""

entities_9 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "Robotic bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "marker implantation", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_9, "RUL", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_9, "Posterior Segment", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "lesion", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "rEBUS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "mass", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "aspirated", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "biopsied", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "brushed", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "Lavage", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "fiducial marker was implanted", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_9, "suspicion of carcinoma", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_9, "No complications", 1)))},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 916783
# ==========================================
id_10 = "916783"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams
Fellow: Dr. James Liu (PGY-5)

Indication: Suspected lung malignancy
Target: 34mm nodule in RUL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
VCV\t11\t302\t16\t80\t8\t21

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 4.0mm.

The device was navigated to the RUL. The outer sheath was parked and locked at the ostium of the segmental airway (RB2) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Posterior Segment of RUL.

Radial EBUS performed via the working channel. rEBUS view: Concentric. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 21G aspiration needle under direct endoscopic and fluoroscopic guidance. 5 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 8 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

Bronchoalveolar lavage performed at RB2. 40mL NS instilled with 17mL return. Sent for Cell count, Culture, and Cytology.

Gold fiducial marker placed under fluoroscopic guidance for radiation therapy planning.

ROSE Result: Suspicious for non-small cell carcinoma

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Williams, MD"""

entities_10 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_10, "34mm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "nodule", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RUL", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "trachea", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "carina", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "lesions", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "Monarch robotic endoscope", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "main carina", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "right and left mainstem bronchi", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "lobar carinas", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RUL", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RB2", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "lesion", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "Posterior Segment", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RUL", 3)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "Radial EBUS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "Lesion", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_10, "needle", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Transbronchial needle aspiration", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(text_10, "21G", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "fluoroscopic guidance", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_10, "5 passes", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Transbronchial forceps biopsy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "forceps", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(text_10, "8 specimens", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Protected cytology brushings", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Bronchoalveolar lavage", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_10, "RB2", 2)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_10, "40mL", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_10, "17mL", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "marker placed", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "fluoroscopic guidance", 2)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(text_10, "Suspicious for non-small cell carcinoma", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_10, "No immediate complications", 1)))},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
