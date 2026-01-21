import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 700001_syn_1
# ==========================================
text_1 = """Proc: EBUS-TBNA mediastinal/hilar nodes.
Anesthesia: GA, 8.5 ETT.
Details:
- Airway inspection neg.
- EBUS scope introduced.
- Sampled 4R (3 passes, ROSE malig), 4L (3 passes, benign), 7 (4 passes, susp), 10L (2 passes, benign).
- Total 12 passes.
Comp: None. <5mL EBL.
Plan: Extubated. PACU. F/U 1-2 wks."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal/hilar nodes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.5", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airway", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "EBUS scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malig", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "benign", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "susp", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "benign", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "12 passes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<5mL", 1)},
]

BATCH_DATA.append({"id": "700001_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 700001_syn_2
# ==========================================
text_2 = """OPERATIVE NARRATIVE: The patient, [REDACTED], presented for staging of a PET-avid left upper lobe mass. Following induction of general anesthesia and placement of an 8.5 mm endotracheal tube, a systematic endobronchial ultrasound examination was conducted. We id[REDACTED] and sampled stations 4R, 4L, 7, and 10L. Rapid On-Site Evaluation (ROSE) indicated malignancy in stations 4R and 7, while stations 4L and 10L yielded adequate lymphocytes without definitive malignant cells. The procedure concluded without complication, and the patient was transferred to the PACU in stable condition."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "8.5 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "endotracheal tube", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "stations 4R, 4L, 7, and 10L", 1)}, # Capturing phrase to avoid ambiguity or single tokens
    {"label": "OBS_ROSE", **get_span(text_2, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "10L", 2)},
    {"label": "OBS_ROSE", **get_span(text_2, "lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "malignant cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "without complication", 1)},
]

BATCH_DATA.append({"id": "700001_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 700001_syn_3
# ==========================================
text_3 = """Procedure Code: 31653 (EBUS sampling 3+ stations).
Guidance: Convex linear EBUS (Olympus BF-UC180F).
Site[REDACTED]
1. Station 4R (Initial): 22G needle, 3 passes.
2. Station 4L (Add-on): 22G needle, 3 passes.
3. Station 7 (Add-on): 22G needle, 4 passes.
4. Station 10L (Add-on): 22G needle, 2 passes.
Medical Necessity: Staging for lung cancer (LUL mass). General anesthesia utilized. Cytology and molecular profiling ordered."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "sampling", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Convex linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Olympus BF-UC180F", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 4R", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "22G needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "3 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 4L", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "22G needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_3, "3 passes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "22G needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_3, "4 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 10L", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "22G needle", 4)},
    {"label": "MEAS_COUNT", **get_span(text_3, "2 passes", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "mass", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "Cytology", 1)},
]

BATCH_DATA.append({"id": "700001_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 700001_syn_4
# ==========================================
text_4 = """Procedure: EBUS-TBNA
Attending: Dr. Kim
Steps:
1. Time-out performed.
2. ETT placed by Anesthesia.
3. White light bronchoscopy: normal anatomy.
4. EBUS TBNA performed at stations 4R, 4L, 7, and 10L using 22G needle.
5. ROSE confirmed adequacy/malignancy at 4R/7.
6. Scope removed. Patient extubated.
Complications: None."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "White light bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "10L", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "22G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "None", 1)},
]

BATCH_DATA.append({"id": "700001_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 700001_syn_5
# ==========================================
text_5 = """We did the bronch on Mr [REDACTED] today for his lung mass staging used the ebus scope under GA tube size 8.5. Looked at the nodes sampled 4R 4L 7 and 10L got good samples rose said cancer in 4R and 7 so thats likely stage 3. 4L and 10L looked okay just lymphocytes. No bleeding or issues patient woke up fine sending to pacu will follow up path."""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "bronch", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "lung mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "ebus scope", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "8.5", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "10L", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "10L", 2)},
    {"label": "OBS_ROSE", **get_span(text_5, "lymphocytes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "No bleeding", 1)},
]

BATCH_DATA.append({"id": "700001_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 700001_syn_6
# ==========================================
text_6 = """68-year-old male with LUL mass. Flexible bronchoscopy with EBUS-TBNA performed under general anesthesia. Airway inspected; no endobronchial lesions. EBUS id[REDACTED] target nodes. Needle aspiration performed at stations 4R, 4L, 7, and 10L. ROSE positive for malignancy at 4R and 7. Samples sent for final path and moleculars. Patient tolerated well, no complications."""

entities_6 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Airway", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lesions", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "Needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "10L", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no complications", 1)},
]

BATCH_DATA.append({"id": "700001_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 700001_syn_7
# ==========================================
text_7 = """[Indication]
Lung cancer staging; LUL mass with PET-avid adenopathy.
[Anesthesia]
General anesthesia, 8.5 mm ETT.
[Description]
Systematic EBUS-TBNA performed. Stations 4R, 4L, 7, and 10L sampled with 22G needle. ROSE confirmed malignant cells at 4R and 7. 4L and 10L benign.
[Plan]
Extubate, PACU, outpatient follow-up for molecular results."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "adenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "8.5 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Stations 4R, 4L, 7, and 10L", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "sampled", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "22G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "malignant cells", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "10L", 2)},
    {"label": "OBS_ROSE", **get_span(text_7, "benign", 1)},
]

BATCH_DATA.append({"id": "700001_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 700001_syn_8
# ==========================================
text_8 = """The patient was brought to the bronchoscopy suite for EBUS-TBNA to stage a left upper lobe mass. We utilized general anesthesia and an 8.5 mm ETT. After verifying the airway was clear, we switched to the EBUS scope. We methodically sampled stations 4R, 4L, 7, and 10L. The preliminary onsite evaluation suggested malignancy in the 4R and subcarinal nodes, which alters the staging. The left-sided nodes appeared benign. There were no complications, and the patient was extubated successfully."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "TBNA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "8.5 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "ETT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "EBUS scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "stations 4R, 4L, 7, and 10L", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "subcarinal", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "benign", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "no complications", 1)},
]

BATCH_DATA.append({"id": "700001_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 700001_syn_9
# ==========================================
text_9 = """Procedure: Flexible bronchoscopy with ultrasound-guided aspiration of mediastinal nodes.
Operator: Dr. Kim.
Actions: The airway was surveyed. The diagnostic scope was swapped for the linear EBUS. Target stations 4R, 4L, 7, and 10L were localized and aspirated. ROSE verified malignant cells in 4R and 7. Specimens were submitted for analysis. The patient was extubated and transferred."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "mediastinal nodes", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "airway", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "linear EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "10L", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspirated", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "malignant cells", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 2)},
    {"label": "SPECIMEN", **get_span(text_9, "Specimens", 1)},
]

BATCH_DATA.append({"id": "700001_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 700001
# ==========================================
text_10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (68 years)
DATE OF PROCEDURE: [REDACTED]
LOCATION: [REDACTED]

PROCEDURE: Flexible bronchoscopy with linear endobronchial ultrasound–guided transbronchial needle aspiration (EBUS-TBNA) of mediastinal and hilar lymph nodes.
OPERATORS:
  Primary Operator: David Kim, MD – Interventional Pulmonology (Attending)
  Assistant: Maria Lopez, MD – Pulmonary Fellow (PGY-5)
  Bronchoscopy RN: Jonathan Johnson, RN
  RT: Erica White, RRT

INDICATION:
68-year-old male with 3.2 cm left upper lobe mass and PET-avid mediastinal/hilar adenopathy (stations 4R, 4L, 7, 10L) requiring tissue for lung cancer staging and diagnosis.

ANESTHESIA / AIRWAY:
General anesthesia provided by Anesthesia service. Orotracheal intubation with 8.5 mm ETT. Patient positioned supine. Continuous cardiac monitoring, pulse oximetry, NIBP.

PROCEDURE DESCRIPTION:
Time-out was performed confirming patient, procedure, and site. The bronchoscope was advanced through the ETT under direct visualization. Trachea and bilateral bronchial tree were inspected to subsegmental level. No endobronchial tumor, secretions, or active bleeding was seen.

EBUS TECHNIQUE:
The diagnostic scope was exchanged for a convex linear EBUS bronchoscope (Olympus BF-UC180F). Complete systematic nodal survey was performed. Target stations were id[REDACTED] by ultrasound and measured.

STATIONS SAMPLED:
• Station 4R: 1.5 x 1.3 cm oval node, heterogeneous with distinct margins. Three passes with 22G EBUS needle; ROSE adequate with malignant cells.
• Station 4L: 1.2 x 1.0 cm node, mildly enlarged. Three passes with 22G needle; ROSE adequate lymphocytes, no definite malignancy.
• Station 7 (subcarinal): 2.0 x 1.6 cm node, heterogeneous with central necrosis. Four passes; ROSE suspicious for malignancy.
• Station 10L: 1.0 x 0.8 cm node. Two passes; ROSE adequate lymphocytes.

A total of 12 needle passes were performed. Specimens were sent for cytology, cell block, and molecular profiling (EGFR/ALK/ROS1/BRAF, PD-L1) per lung cancer protocol.

COMPLICATIONS:
No significant bleeding, hypoxia, or arrhythmia occurred. Estimated blood loss < 5 mL. No immediate complications were observed.

DISPOSITION / PLAN:
Patient [REDACTED] in the procedure room and transferred to PACU in stable condition on 2 L/min nasal cannula. Planned outpatient follow-up in IP clinic in 1–2 weeks to review final pathology and staging. CT chest with contrast and brain MRI are already scheduled.

PRELIMINARY IMPRESSION:
Successful systematic EBUS-TBNA of mediastinal and hilar lymph nodes (stations 4R, 4L, 7, 10L) for lung cancer staging. ROSE suggests malignant involvement at 4R and 7; final cytology and molecular testing pending.

SIGNED:
David Kim, MD
Interventional Pulmonology"""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal and hilar lymph nodes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "3.2 cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "adenopathy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "stations 4R, 4L, 7, 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "8.5 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "ETT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretions", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "active bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "convex linear EBUS bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Olympus BF-UC180F", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.5 x 1.3 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Three passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G EBUS needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "adequate with malignant cells", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.2 x 1.0 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Three passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.0 x 1.6 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Four passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "suspicious for malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.0 x 0.8 cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Two passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "adequate lymphocytes", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "12 needle passes", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "cell block", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant bleeding", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "< 5 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No immediate complications", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "mediastinal and hilar lymph nodes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "stations 4R, 4L, 7, 10L", 2)},
]

BATCH_DATA.append({"id": "700001", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)