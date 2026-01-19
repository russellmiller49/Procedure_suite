import sys
from pathlib import Path

# Set the repository root (assuming script is run from inside the repo or similar structure)
# This allows importing the 'add_case' utility
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 2458901_syn_1
# ==========================================
id_1 = "2458901_syn_1"
text_1 = """Procedure: EBUS-TBNA.
Indication: Mediastinal staging.
Nodes Sampled:
- 4R (18mm): Positive for Adeno.
- 7 (22mm): Positive for Adeno.
- 10R (14mm): Positive for Adeno.
Technique: 22G needle, 3-4 passes per station.
Result: N3 disease (Contralateral/Supraclavicular not sampled, but extensive N2 involved)."""

entities_1 = [
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adeno", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adeno", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14mm", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adeno", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "N3 disease", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "N2", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2458901_syn_2
# ==========================================
id_2 = "2458901_syn_2"
text_2 = """DIAGNOSTIC OPERATIVE NOTE: The patient underwent endobronchial ultrasound-transbronchial needle aspiration (EBUS-TBNA) for mediastinal staging. The airway was inspected and found to be patent. Systematic ultrasonic evaluation of the mediastinum revealed lymphadenopathy in stations 4R, 7, and 10R. Real-time guided aspiration was performed utilizing a 22-gauge needle. Rapid On-Site Evaluation (ROSE) confirmed the presence of malignant cells consistent with adenocarcinoma in all sampled stations, confirming multi-station N2 disease."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "EBUS-TBNA", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "airway", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "10R", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "22-gauge needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "adenocarcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "N2 disease", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2458901_syn_3
# ==========================================
id_3 = "2458901_syn_3"
text_3 = """CPT Coding Data:
- 31653 (EBUS-TBNA, first 3 stations): Biopsies taken from stations 4R, 7, and 10R.
- 31622 (Dx Bronch): Bundled.
Medical Necessity: Staging for RUL mass.
Technique: Ultrasound guidance used for needle visualization during all passes. Images archived."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "10R", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Dx Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ultrasound", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2458901_syn_4
# ==========================================
id_4 = "2458901_syn_4"
text_4 = """Procedure: EBUS
Resident: Dr. Rogers
Patient: [REDACTED]
Steps:
1. Moderate sedation.
2. Airway exam normal.
3. EBUS scope down. Found nodes at 4R, 7, 10R.
4. Biopsied all three with 22G needle.
5. ROSE said cancer (adeno).
Plan: Oncology referral."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Airway", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "10R", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "22G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "cancer", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "adeno", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2458901_syn_5
# ==========================================
id_5 = "2458901_syn_5"
text_5 = """We did the EBUS on Sarah Martinez today indication was staging. Sedation was fine versed fentanyl. Looked at the nodes 4R was big so we stuck it 4 times came back cancer. Station 7 also big stuck that one too cancer. 10R also positive. So looks like stage III disease. No bleeding patient woke up fine."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "EBUS", 1)},
    {"label": "MEDICATION", **get_span(text_5, "versed", 1)},
    {"label": "MEDICATION", **get_span(text_5, "fentanyl", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "4 times", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "Station 7", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "10R", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "positive", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "stage III disease", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2458901_syn_6
# ==========================================
id_6 = "2458901_syn_6"
text_6 = """Endobronchial ultrasound-guided transbronchial needle aspiration was performed for staging of a right upper lobe mass. The EBUS bronchoscope was introduced. Lymph node stations 4R, 7, and 10R were id[REDACTED], measured, and sampled using a 22-gauge needle under real-time ultrasound guidance. Cytopathology confirmed adenocarcinoma in all sampled stations. The procedure was well tolerated without complication."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "EBUS bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "10R", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "22-gauge needle", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "ultrasound", 2)},
    {"label": "OBS_ROSE", **get_span(text_6, "adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2458901_syn_7
# ==========================================
id_7 = "2458901_syn_7"
text_7 = """[Indication]
Mediastinal lymphadenopathy, staging for RUL mass.
[Anesthesia]
Moderate Sedation.
[Description]
EBUS performed. Nodes sampled: 4R, 7, 10R. 
Pathology: Adenocarcinoma confirmed in all stations.
[Plan]
Refer to Oncology for Stage IIIB treatment."""

entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "Mediastinal lymphadenopathy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "10R", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2458901_syn_8
# ==========================================
id_8 = "2458901_syn_8"
text_8 = """[REDACTED] EBUS procedure today to stage her lung cancer. After checking her airways, which looked clear, we used the ultrasound scope to locate enlarged lymph nodes in the middle of her chest. We took samples from the right paratracheal, subcarinal, and right hilar nodes. Unfortunately, the preliminary results from the pathologist in the room showed cancer cells in all three areas, indicating the disease has spread to the lymph nodes."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "cancer", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airways", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "ultrasound scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "right paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "right hilar", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "cancer cells", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2458901_syn_9
# ==========================================
id_9 = "2458901_syn_9"
text_9 = """Procedure: Endosonography with needle extraction.
Target: Mediastinal nodes.
Action: Stations 4R, 7, and 10R were visualized. A needle was propelled into each node to harvest cells. The specimens were analyzed immediately.
Result: Malignancy detected in all stations."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Endosonography", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "10R", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "Malignancy", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 2458901
# ==========================================
id_10 = "2458901"
text_10 = """PATIENT: [REDACTED], 58-year-old Female
MRN: [REDACTED]
INDICATION FOR OPERATION: Ms. [REDACTED] is a 58-year-old female who presents with mediastinal lymphadenopathy discovered on staging CT for newly diagnosed right upper lobe mass. PET-CT shows FDG-avid nodes in stations 4R, 7, and 10R. The nature, purpose, risks, benefits and alternatives to EBUS-TBNA were discussed with the patient in detail. Patient indicated a wish to proceed and informed consent was signed.
PREOPERATIVE DIAGNOSIS: Mediastinal lymphadenopathy; Right upper lobe mass
POSTOPERATIVE DIAGNOSIS: Same
PROCEDURE: EBUS-TBNA (CPT 31652, 31653)
ATTENDING: Dr. James Chen
ASSISTANT: Dr. Emily Rogers, Fellow
Support Staff:

RN: Karen Thompson
RT: Michael Davis

ANESTHESIA: Moderate sedation with Midazolam 2mg IV and Fentanyl 100mcg IV
MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer present throughout the entire procedure.
INSTRUMENT: Olympus BF-UC180F EBUS bronchoscope
ESTIMATED BLOOD LOSS: Minimal
COMPLICATIONS: None
PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location). All procedure related images were saved and archived.
PATIENT [REDACTED]: Supine
The endobronchial ultrasound-capable bronchoscope was introduced through the oral route. 5 cc of 2% lidocaine was instilled for topical anesthesia. Initial airway inspection revealed normal vocal cords with symmetric movement, normal trachea, and patent bilateral mainstem bronchi without endobronchial lesions.
A systematic EBUS survey was completed. The following lymph node stations were id[REDACTED] and sampled:
Station 4R (Right paratracheal):

Size: 18mm (short axis)
Number of Passes: 4
Echo Features: Heterogeneous, defined borders, round shape
Biopsy Tools: 22-gauge needle
ROSE Results: Adequate cellularity, malignant cells present consistent with adenocarcinoma

Station 7 (Subcarinal):

Size: 22mm (short axis)
Number of Passes: 4
Echo Features: Heterogeneous, irregular borders
Biopsy Tools: 22-gauge needle
ROSE Results: Adequate cellularity, malignant cells present

Station 10R (Right hilar):

Size: 14mm (short axis)
Number of Passes: 3
Echo Features: Hypoechoic, defined borders
Biopsy Tools: 22-gauge needle
ROSE Results: Adequate cellularity, malignant cells present

Overall ROSE Diagnosis: Metastatic adenocarcinoma. Prior to withdrawal of the bronchoscope, inspection demonstrated no evidence of bleeding.
The patient tolerated the procedure well. There were no immediate complications. The attending, Dr. Chen, was present at the bedside and supervised the entire procedure.
SPECIMEN(S):

Station 4R TBNA x4 (cytology)
Station 7 TBNA x4 (cytology)
Station 10R TBNA x3 (cytology)

IMPRESSION/PLAN: Ms. [REDACTED] is a 58-year-old female with newly diagnosed lung adenocarcinoma. EBUS-TBNA confirms N2 and N3 nodal involvement (Stage IIIB). Results will be discussed at multidisciplinary tumor board. Patient to follow up with medical oncology for treatment planning."""

entities_10 = [
    {"label": "OBS_FINDING", **get_span(text_10, "mediastinal lymphadenopathy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "10R", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "EBUS-TBNA", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Fentanyl", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Olympus BF-UC180F EBUS bronchoscope", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "endobronchial ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "bronchoscope", 1)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "mainstem bronchi", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Right paratracheal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "18mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "adenocarcinoma", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Subcarinal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "22mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignant cells", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Right hilar", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignant cells", 3)},
    {"label": "OBS_ROSE", **get_span(text_10, "Metastatic adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 10R", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 4)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "adenocarcinoma", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "EBUS-TBNA", 2)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)