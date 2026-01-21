import sys
from pathlib import Path

# Calculate the path to the repository root (assumes this script is in a subdirectory)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow importing from scripts
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The term to search for.
        occurrence (int): The occurrence number (1-based).
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 1904506_syn_1
# ==========================================
text_1 = """Indication: RUL adenocarcinoma, confirm N2 (4R).
Anesthesia: GA, 8.0 ETT.
Procedure: Bronch w/ TBNA.
- Scope via ETT.
- Station 4R sampled w/ 22G Wang needle.
- 4 passes.
- ROSE: Adenocarcinoma.
Complications: None.
Plan: Multimodality therapy."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    # Fixed: "Adenocarcinoma" appears only once with this capitalization (in ROSE line). 
    # The first mention is "adenocarcinoma" (lowercase).
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1904506_syn_2
# ==========================================
text_2 = """HISTORY: Ms. [REDACTED], with known RUL adenocarcinoma, presented for confirmation of mediastinal involvement.
PROCEDURE: Under general anesthesia, flexible bronchoscopy was performed via ETT. Conventional TBNA of the Station 4R lymph node was conducted using a 22-gauge Wang needle. Four passes were obtained. ROSE confirmed metastatic adenocarcinoma, establishing N2 disease.
IMPRESSION: Stage IIIA NSCLC."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "adenocarcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Conventional TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "Station 4R lymph node", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "22-gauge Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Four passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "metastatic adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1904506_syn_3
# ==========================================
text_3 = """Service: Bronchoscopy with TBNA (31629).
Target: Station 4R (Right Lower Paratracheal).
Device: 22-gauge Wang Needle.
Method: Conventional aspiration via anatomic landmarks (No EBUS).
Specimen: 4 passes for cytology/molecular. ROSE confirmed malignancy.
Indication: Confirmation of N2 disease."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Right Lower Paratracheal", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "22-gauge Wang Needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_3, "malignancy", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1904506_syn_4
# ==========================================
text_4 = """Resident Note
Patient: [REDACTED]
Procedure: TBNA Station 4R
Staff: Dr. Cole

1. GA/Intubation.
2. Scope passed.
3. 4R node targeted.
4. Wang needle used for 4 passes.
5. ROSE: Adenocarcinoma.
6. Scope removed.

Plan: Extubate, PACU, Oncology."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R node", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1904506_syn_5
# ==========================================
text_5 = """note for evelyn carter 73f known rul cancer need to check 4r node general anesthesia tube in scope down airway normal used 22g wang needle on 4r did 4 passes rose positive for adeno no bleeding patient extubated plan chemo rads"""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rul", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4r node", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "22g wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4r", 2)},
    {"label": "MEAS_COUNT", **get_span(text_5, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "adeno", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1904506_syn_6
# ==========================================
text_6 = """[REDACTED] underwent flexible bronchoscopy with conventional TBNA to confirm N2 disease. General anesthesia was used. A 22-gauge Wang needle was used to sample the right lower paratracheal node (Station 4R) through the endotracheal tube using anatomic landmarks. Four passes were performed. On-site cytology confirmed adenocarcinoma. There were no complications. The patient was transferred to the PACU."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "conventional TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "22-gauge Wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "right lower paratracheal node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Station 4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Four passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1904506_syn_7
# ==========================================
text_7 = """[Indication]
RUL adenocarcinoma, PET-avid 4R node.
[Anesthesia]
General anesthesia (ETT).
[Description]
Flexible bronchoscopy via ETT. Conventional TBNA of Station 4R using 22G Wang needle (4 passes). ROSE confirmed adenocarcinoma.
[Plan]
Extubate. Multimodality therapy."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R node", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Conventional TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "22G Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "adenocarcinoma", 2)} # First occurrence is lesion context, second is ROSE
]
BATCH_DATA.append({"id": "1904506_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1904506_syn_8
# ==========================================
text_8 = """The patient was placed under general anesthesia. We introduced the bronchoscope through the ETT. We id[REDACTED] the landmark for the right lower paratracheal node (Station 4R) and performed conventional TBNA using a 22-gauge Wang needle. Four passes were obtained, and on-site evaluation confirmed metastatic adenocarcinoma. The procedure was completed without complications."""

entities_8 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "right lower paratracheal node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "Station 4R", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "conventional TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "22-gauge Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "Four passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "metastatic adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1904506_syn_9
# ==========================================
text_9 = """PROCEDURE: Bronchoscopy with blind needle biopsy of right paratracheal node.
REASON: Confirm cancer spread.
TECHNIQUE: Under general anesthesia, the scope was inserted. The Station 4R node was sampled with a Wang needle. Four samples were taken. Rapid analysis confirmed adenocarcinoma. The patient was awakened."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "blind needle biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "right paratracheal node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Station 4R node", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Four samples", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "1904506_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1904506
# ==========================================
text_10 = """PATIENT: [REDACTED], 73-year-old Female
MRN: [REDACTED]
DATE: [REDACTED]
ATTENDING: Dr. Nathan Cole
FELLOW: Dr. Lina Chen
PROCEDURE: Flexible bronchoscopy with conventional transbronchial needle aspiration (TBNA) of right lower paratracheal lymph node (station 4R) using Wang needle (CPT 31629)
INDICATION: PET-avid right lower paratracheal (4R) lymph node in a patient with known right upper lobe adenocarcinoma; confirmation of N2 disease prior to definitive therapy.

ANESTHESIA/SEDATION: General anesthesia with 8.0 ETT. Anesthesiology provided induction with propofol and rocuronium; patient mechanically ventilated throughout.

PROCEDURE DESCRIPTION:
Following a formal time-out, a flexible bronchoscope was advanced through the endotracheal tube. The trachea and main carina appeared normal. The right mainstem bronchus showed minimal extrinsic impression along its medial wall. No endobronchial tumor or secretions were seen in either lung.

CONVENTIONAL TBNA (WANG NEEDLE):
A 22-gauge Wang TBNA needle was passed through the bronchoscope working channel. Under anatomic landmark guidance only (no EBUS system used), the right lower paratracheal (4R) node was sampled via the distal trachea and proximal right mainstem bronchus. Four aspiration passes were performed with suction. All passes yielded blood-tinged material with tissue fragments adequate for cytology and cell block.

ROSE: Rapid on-site evaluation by cytology demonstrated metastatic adenocarcinoma in a lymphoid background, confirming N2 involvement. Adequacy was established after the second pass; additional passes were dedicated to cell block and molecular testing.

SPECIMENS:
Station 4R conventional TBNA x4 passes submitted for cytology, cell block, immunohistochemistry, and molecular profiling.

COMPLICATIONS: No significant bleeding or hypoxia. No linear EBUS, radial probe, or navigation was used; this was conventional blind Wang needle TBNA.

DISPOSITION/PLAN:
The patient was extubated in the OR and transferred to PACU in stable condition. Results will be reviewed with thoracic surgery and medical oncology; given confirmed N2 disease, multimodality therapy rather than primary surgery is anticipated."""

entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "conventional transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "right lower paratracheal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "right lower paratracheal", 2)}, # Second occurrence in Indication
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 2)}, # Second occurrence in Indication
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "adenocarcinoma", 1)},
    {"label": "MEDICATION", **get_span(text_10, "propofol", 1)},
    {"label": "MEDICATION", **get_span(text_10, "rocuronium", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right mainstem bronchus", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge Wang TBNA needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "right lower paratracheal (4R) node", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "distal trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "proximal right mainstem bronchus", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Four aspiration passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "metastatic adenocarcinoma", 1)},
    # Fixed: "station 4R" (lowercase s) appears earlier, but "Station 4R" (capital S) appears here first.
    # We are searching for "Station 4R" (Capital S), so it is occurrence 1.
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 1)} 
]
BATCH_DATA.append({"id": "1904506", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)