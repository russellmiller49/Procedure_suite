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
# Note 1: 1145039_syn_1
# ==========================================
id_1 = "1145039_syn_1"
text_1 = """Procedure: Robotic Bronchoscopy (Ion), LLL nodule.
- Nav: Ion system, 3.8mm error.
- Confirmation: Radial EBUS (concentric) + Cone Beam CT.
- Sampling: Forceps x6, Brush x2.
- Complications: None.
- Plan: D/C, path follow-up."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3.8mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Cone Beam CT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1145039_syn_2
# ==========================================
id_2 = "1145039_syn_2"
text_2 = """OPERATIVE REPORT: The patient underwent robotic-assisted bronchoscopy utilizing the Intuitive Ion platform for a peripheral LLL lesion. Navigation was aided by shape-sensing technology. Target verification was achieved via radial EBUS (concentric view) and intraoperative Cone-Beam CT, confirming tool-in-lesion. Transbronchial biopsies and brushings were obtained. The patient remained stable."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Intuitive Ion platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "peripheral", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "shape-sensing technology", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "concentric view", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Cone-Beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "brushings", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1145039_syn_3
# ==========================================
id_3 = "1145039_syn_3"
text_3 = """Codes: 31627 (Nav), 31628 (Biopsy), 31623 (Brush), 31654 (REBUS).
Target: Left Lower Lobe (LB9).
Tech: Robotic platform, Fluoroscopy, CBCT, Radial EBUS.
Samples: Histology and Cytology obtained.
Complications: None."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "REBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Left Lower Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "CBCT", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3, "None", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1145039_syn_4
# ==========================================
id_4 = "1145039_syn_4"
text_4 = """Procedure: Robotic Bronch LLL
Steps:
1. GA/ETT.
2. Registered Ion robot.
3. Navigated to LLL target.
4. REBUS check: Concentric.
5. CBCT spin: Tool in lesion.
6. Biopsied (forceps/brush).
7. No bleeding.
Plan: Extubate, recover."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Robotic Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Ion robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 2)},
    {"label": "PROC_METHOD", **get_span(text_4, "REBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Concentric", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "CBCT spin", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "brush", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No bleeding", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1145039_syn_5
# ==========================================
id_5 = "1145039_syn_5"
text_5 = """robotic bronch for michael chang lll nodule. ion system used. registration good. drove out to the lb9 segment. rebus showed the lesion concentric view. did a spin with the c-arm to be sure. took 6 bites and 2 brushes. no bleeding. woke up fine."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "robotic bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ion system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lb9 segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "rebus", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "concentric view", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "c-arm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "6", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "2", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brushes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1145039_syn_6
# ==========================================
id_6 = "1145039_syn_6"
text_6 = """Robotic Navigational Bronchoscopy using Intuitive Ion System was performed for a 1.8cm left lower lobe nodule. Navigation planning and registration were completed. The catheter was advanced to the target in LB9. Radial EBUS and Cone-Beam CT confirmed lesion location. Transbronchial biopsy and brushing were performed. No complications occurred."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Robotic Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Intuitive Ion System", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Cone-Beam CT", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Transbronchial biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "brushing", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1145039_syn_7
# ==========================================
id_7 = "1145039_syn_7"
text_7 = """[Indication]
1.8cm LLL Nodule.
[Anesthesia]
General, ETT.
[Description]
Ion Robotic Navigation. REBUS/CBCT confirmation. Transbronchial biopsy x6. Brushing x2. No pneumothorax.
[Plan]
Pathology pending."""

entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "1.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Ion Robotic Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "REBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Transbronchial biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Brushing", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x2", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "No pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1145039_syn_8
# ==========================================
id_8 = "1145039_syn_8"
text_8 = """We performed a robotic bronchoscopy to biopsy a nodule in [REDACTED] lobe. Using the Ion platform, we navigated to the lateral basal segment. We confirmed our position with both radial EBUS and a cone-beam CT spin, ensuring the tool was right in the lesion. We then took multiple biopsies and brushings. The procedure went smoothly with no complications."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Ion platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lateral basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "cone-beam CT spin", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "brushings", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "no complications", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1145039_syn_9
# ==========================================
id_9 = "1145039_syn_9"
text_9 = """Procedure: Robotic-assisted transbronchial sampling.
Target: Peripheral pulmonary nodule, LLL.
Guidance: Electromagnetic/Shape-sensing navigation, Radial Ultrasound, Cone-Beam Tomography.
Action: Acquired tissue via forceps and brush.
Result: No adverse events."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic-assisted", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "transbronchial sampling", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Peripheral", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Electromagnetic/Shape-sensing navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Radial Ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Cone-Beam Tomography", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "brush", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "No adverse events", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1145039
# ==========================================
id_10 = "1145039"
text_10 = """PATIENT: [REDACTED], 55-year-old Male
MRN: [REDACTED]
INDICATION FOR OPERATION: Mr. [REDACTED] is a 55-year-old male with a 1.8cm spiculated left lower lobe nodule discovered on low-dose CT screening. PET shows SUV 3.2. Nodule location is peripheral in the lateral basal segment. The nature, purpose, risks, benefits and alternatives to robotic navigational bronchoscopy were discussed with the patient in detail. Patient indicated a wish to proceed and informed consent was signed.
PREOPERATIVE DIAGNOSIS: Left lower lobe pulmonary nodule
POSTOPERATIVE DIAGNOSIS: Same
PROCEDURE: Robotic Navigational Bronchoscopy using Intuitive Ion System (CPT 31627), Radial EBUS (CPT 31654), Transbronchial Biopsy (CPT 31628), Transbronchial Brushing (CPT 31623)
ATTENDING: Dr. Amanda Roberts
ASSISTANT: Dr. Jason Kim, Fellow
Support Staff:

RN: Laura Martinez
RT: Thomas Wilson
Anesthesia: Dr. Susan Park

ANESTHESIA: General anesthesia with endotracheal intubation
MONITORING: Standard ASA monitoring
INSTRUMENT: Intuitive Ion Robotic Platform, radial EBUS probe, biopsy forceps, cytology brush
ESTIMATED BLOOD LOSS: <10 mL
COMPLICATIONS: None
PROCEDURE IN DETAIL:
After induction of general anesthesia and intubation with 8.0 ETT, a timeout was performed. All procedure related images were saved and archived.
PATIENT [REDACTED]: Supine
Ventilation Parameters:

Mode: Volume Control
RR: 12
TV: 500mL
PEEP: 5 cmH₂O
FiO₂: 40%
Flow Rate: 50 L/min
Pmean: 14 cmH₂O

Navigation Planning:
CT Chest scan from [REDACTED] was placed on the separate planning station (Synapse Lung) to generate 3D rendering of the pathway to target nodule in the lateral basal segment of the left lower lobe (LB9). The navigational plan was reviewed, verified, and loaded into the Ion robotic bronchoscopy platform.
Target lesion characteristics:

Location: LLL, lateral basal segment (LB9)
Size: 1.8cm
Distance from pleura: 1.2cm
Bronchus sign: Present
Ion Registration - Complete:
Registration to the pre-procedure CT was completed using automatic methods. Adequate airway landmark matching achieved at:

Main carina
Left main carina
LLL segmental carinas
Tertiary bifurcations in LB9

Mean fiducial error: 3.8mm
Global alignment quality: Excellent
No registration drift observed during the case
A confidence sweep confirmed stable targeting throughout the planned trajectory with virtual-to-live alignment within acceptable parameters.
Navigation:
The Ion catheter was advanced under navigational guidance through the left mainstem bronchus, into the LLL, and subsequently into the LB9 segment. The robotic system provided real-time feedback with shape sensing technology.
Target reached notification appeared when catheter tip was 0.6cm from the planned target center.
Radial EBUS Confirmation:
Radial EBUS probe (1.4mm) was passed through the Ion extended working channel to confirm lesion location. The following features were noted:

Pattern: Concentric
Echogenicity: Heterogeneous
Lesion size by REBUS: 19mm
Distance to pleura: 11mm
Vessel proximity: No large vessels within 5mm

Cone-Beam CT Verification:
Mobile C-arm CBCT spin was performed with the Ion catheter in [REDACTED]. Three-dimensional reconstruction confirmed:

Catheter tip within lesion margins
Distance from lesion center: 4mm
Trajectory angle: Optimal for sampling
No pleural transgression

Sampling:
With confirmed tool-in-lesion [REDACTED]:

Transbronchial Biopsy: Forceps biopsies obtained through Ion extended working channel. Total 6 samples collected with visible tissue in each specimen.
Bronchial Brushings: Cytology brush advanced to lesion site. Total 2 brush samples obtained.
Aspiration: Catheter aspiration performed for cytology.

All samples appeared adequate with visible tissue/cellular material. No ROSE available.
Post-Sampling Inspection:
The Ion catheter was withdrawn. Final bronchoscopic inspection showed:

No active bleeding from biopsy site
Patent LLL airways
No complications id[REDACTED]

The patient tolerated the procedure well. There were no immediate complications. The attending, Dr. Roberts, was present throughout the entire procedure.
SPECIMEN(S):

LLL nodule forceps biopsies x6 (histology, molecular if malignant)
Bronchial brushings x2 (cytology)
Catheter aspiration (cytology)

IMPRESSION/PLAN: Mr. [REDACTED] underwent successful robotic navigational bronchoscopy with sampling of LLL nodule. Procedure completed without complications. Post-procedure CXR shows no pneumothorax. Patient discharged home same day with instructions to follow up in 1 week for pathology results. If benign, will need CT follow-up in 3-6 months per Fleischner criteria. If malignant, will be discussed at multidisciplinary tumor board for treatment planning."""

entities_10 = [
    {"label": "MEAS_SIZE", **get_span(text_10, "1.8cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "spiculated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "peripheral", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lateral basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "robotic navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pulmonary nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Robotic Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Intuitive Ion System", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial Brushing", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Intuitive Ion Robotic Platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cytology brush", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "<10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "500mL", 1)},
    {"label": "MEAS_PRESS", **get_span(text_10, "5 cmH₂O", 1)},
    {"label": "MEAS_PRESS", **get_span(text_10, "14 cmH₂O", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lateral basal segment", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "left lower lobe", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB9", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion robotic bronchoscopy platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lateral basal segment", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB9", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.8cm", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.2cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Bronchus sign", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Left main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LLL segmental carinas", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Tertiary bifurcations", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB9", 3)},
    {"label": "MEAS_SIZE", **get_span(text_10, "3.8mm", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Ion catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem bronchus", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB9", 4)},
    {"label": "PROC_METHOD", **get_span(text_10, "shape sensing technology", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "0.6cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Radial EBUS probe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.4mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Ion extended working channel", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Concentric", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Heterogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "19mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "11mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Mobile C-arm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "CBCT spin", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Ion catheter", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "4mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial Biopsy", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Ion extended working channel", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6 samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchial Brushings", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Cytology brush", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "2 brush samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Aspiration", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter aspiration", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Ion catheter", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No active bleeding", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "Patent LLL airways", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 3)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 4)},
    {"label": "PROC_ACTION", **get_span(text_10, "forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchial brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x2", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Catheter aspiration", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "robotic navigational bronchoscopy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 4)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 5)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "without complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)