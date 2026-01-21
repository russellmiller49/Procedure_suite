import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
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
# Note 1: 1904502_syn_1
# ==========================================
id_1 = "1904502_syn_1"
text_1 = """Dx: LUL mass, subcarinal adenopathy.
Anesthesia: GA, 8.0 ETT.
Procedure: Bronchoscopy with TBNA.
- Scope via ETT.
- Normal airway inspection.
- Station 7 targeted w/ 22G Wang needle (conventional).
- 3 passes.
- ROSE: Malignant.
Complications: None.
Disposition: PACU."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "subcarinal", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Wang needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "conventional", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1904502_syn_2
# ==========================================
id_2 = "1904502_syn_2"
text_2 = """INDICATION: [REDACTED], a 62-year-old female with a central left upper lobe mass, underwent mediastinal staging.
PROCEDURE: The patient was placed under general anesthesia with endotracheal intubation. A flexible bronchoscope was advanced. The tracheobronchial tree was patent. Conventional transbronchial needle aspiration (TBNA) of the subcarinal lymph node (Station 7) was performed using a 22-gauge Wang needle and anatomic landmarks. Three passes yielded diagnostic material confirmed by rapid on-site evaluation to be metastatic non-small cell lung carcinoma.
CONCLUSION: Positive mediastinal staging (N2 disease)."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "tracheobronchial tree", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "Station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "metastatic non-small cell lung carcinoma", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1904502_syn_3
# ==========================================
id_3 = "1904502_syn_3"
text_3 = """Service: Bronchoscopy with TBNA (31629).
Target: Subcarinal Lymph Node (Station 7).
Method: Conventional TBNA using 22-gauge Wang needle. Anatomic landmarks used for guidance (EBUS not utilized).
Specimen: 3 passes obtained for cytology and cell block. ROSE confirmed malignancy.
Anesthesia: General anesthesia with ETT."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Subcarinal Lymph Node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "Station 7", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_3, "malignancy", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1904502_syn_4
# ==========================================
id_4 = "1904502_syn_4"
text_4 = """Resident Procedure Note
Patient: [REDACTED]
Procedure: Conventional TBNA Station 7
Staff: Dr. Romero

1. Pt intubated/GA.
2. Scope passed through ETT.
3. Airway exam: Normal.
4. Needle (Wang 22G) used to sample Station 7.
5. 3 passes completed.
6. ROSE: Positive for malignancy.
7. Tolerated well.

Plan: Extubate, PACU."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "Station 7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Wang", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "22G", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "Station 7", 2)},
    {"label": "MEAS_COUNT", **get_span(text_4, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Positive for malignancy", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1904502_syn_5
# ==========================================
id_5 = "1904502_syn_5"
text_5 = """note for laura benson 62f procedure bronchoscopy with tbna indication lung mass subcarinal node anesthesia general with ett tube scope went in fine airway normal used 22g wang needle on station 7 did 3 passes rose showed cancer cells no bleeding patient stable extubated in or sent to recovery"""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "tbna", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "lung mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "subcarinal node", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "22g", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1904502_syn_6
# ==========================================
id_6 = "1904502_syn_6"
text_6 = """Laura Benson, a 62-year-old female, underwent flexible bronchoscopy with conventional TBNA for mediastinal staging of a central lung mass. General anesthesia was used. A bronchoscope was passed through the endotracheal tube. The airway was inspected and found to be normal. A 22-gauge Wang needle was used to aspirate the subcarinal lymph node (Station 7) using anatomic landmarks. Three passes were performed. Rapid on-site evaluation showed malignant cells. No complications occurred. The patient was extubated and transferred to the PACU."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lung mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "Wang needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "malignant cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1904502_syn_7
# ==========================================
id_7 = "1904502_syn_7"
text_7 = """[Indication]
Mediastinal staging, LUL mass, Station 7 adenopathy.
[Anesthesia]
General anesthesia (ETT).
[Description]
Flexible bronchoscopy via ETT. Conventional TBNA of Station 7 performed using 22G Wang needle (3 passes). ROSE confirmed malignancy. No EBUS used.
[Plan]
Extubate. Oncology follow-up."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Station 7", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "Station 7", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "Wang needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "malignancy", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1904502_syn_8
# ==========================================
id_8 = "1904502_syn_8"
text_8 = """The patient was brought to the operating room and placed under general anesthesia with an endotracheal tube. A flexible bronchoscope was introduced through the tube. We inspected the airways and noted no endobronchial lesions. Using a 22-gauge Wang needle, we performed conventional transbronchial needle aspiration of the subcarinal lymph node (Station 7). Three passes were made, and on-site cytology confirmed metastatic carcinoma. The procedure concluded without complications, and the patient was extubated."""

entities_8 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airways", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesions", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "Wang needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "Three passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "metastatic carcinoma", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1904502_syn_9
# ==========================================
id_9 = "1904502_syn_9"
text_9 = """PROCEDURE: Bronchoscopy with blind needle aspiration of subcarinal node.
REASON: Central lung mass with nodal involvement.
TECHNIQUE: Under general anesthesia, the scope was introduced. The Station 7 node was sampled using a Wang needle via conventional landmarks. Three samples were obtained. Rapid analysis showed carcinoma. The patient was awakened and extubated."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "blind", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "subcarinal node", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lung mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "Wang needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "conventional", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Three samples", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "carcinoma", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1904502
# ==========================================
id_10 = "1904502"
text_10 = """PATIENT: [REDACTED], 62-year-old Female
MRN: [REDACTED]
DATE: [REDACTED]
ATTENDING: Dr. Daniel Romero
FELLOW: Dr. Hannah Nguyen
PROCEDURE: Flexible bronchoscopy with conventional transbronchial needle aspiration (TBNA) of subcarinal lymph node (station 7) using Wang needle (CPT 31629)
INDICATION: Centrally located left upper lobe mass with enlarged subcarinal lymph node on PET-CT, mediastinal staging prior to definitive therapy.

ANESTHESIA/SEDATION: General anesthesia with endotracheal intubation provided by Anesthesiology. Size 8.0 ETT secured. The patient was ventilated mechanically throughout the procedure.

PROCEDURE DESCRIPTION:
After standard pre-procedure checks and a surgical time-out, a flexible adult bronchoscope was introduced through the endotracheal tube. The vocal cords and proximal trachea were normal. The main carina was sharp with mild external impression posteriorly. No intraluminal tumor was seen in either mainstem bronchus. Segmental bronchi in both lungs were free of obstructing lesions.

CONVENTIONAL TBNA (WANG NEEDLE):
A 22-gauge Wang TBNA needle was advanced through the bronchoscope working channel. Using anatomic landmarks only (no EBUS system available in the OR), the subcarinal (station 7) lymph node was targeted by puncturing the bronchial wall just proximal and slightly posterior to the main carina. Three needle passes were performed with suction. Each pass yielded blood-tinged material with visible tissue cores.

ROSE: On-site cytology was available. Rapid evaluation demonstrated cellular samples with lymphocytes and malignant epithelial cells compatible with metastatic non-small cell lung carcinoma. Adequacy was confirmed after the second pass; a third pass was obtained for additional cell block material.

SPECIMENS:
Station 7 conventional TBNA x3 passes submitted for cytology, cell block, and PD-L1/molecular profiling as indicated.

COMPLICATIONS: No significant bleeding, hypoxia, or arrhythmia. No EBUS, radial probe, or navigational bronchoscopy was used; this was a purely conventional blind Wang needle TBNA.

DISPOSITION/PLAN:
The patient was extubated in the OR and transferred to the PACU in stable condition. She will follow up in thoracic oncology clinic within 1 week to review final pathology and discuss resection versus combined-modality therapy."""

entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang needle", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal lymph node", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible adult bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "vocal cords", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "proximal trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "mainstem bronchus", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Segmental bronchi", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesions", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "CONVENTIONAL", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "WANG NEEDLE", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang TBNA needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "anatomic landmarks", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal (station 7) lymph node", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "Three needle passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignant epithelial cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "metastatic non-small cell lung carcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 4)},
    {"label": "MEAS_COUNT", **get_span(text_10, "3 passes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No significant bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "conventional", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "blind", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "Wang needle", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 5)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)