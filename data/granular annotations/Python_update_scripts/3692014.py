import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3692014_syn_1
# ==========================================
text_1 = """Procedure: Navigational Bronchoscopy, Radial EBUS, Cryobiopsy RLL.
Indication: 2.8cm RLL nodule.
Actions:
- 8.0 ETT placed.
- SuperDimension nav to RLL lateral basal.
- Radial EBUS: concentric view, 27mm lesion.
- Cryoprobe 1.9mm used. 4 samples taken (6 sec freeze).
- Arndt blocker used for hemostasis. Minimal bleeding.
- No pneumothorax on post-op check."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "SuperDimension", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lateral basal", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cryoprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "samples", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "6 sec", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Arndt blocker", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Minimal bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 3692014_syn_2
# ==========================================
text_2 = """HISTORY: [REDACTED], a 67-year-old male, presented with a 2.8 cm spiculated nodule in the right lower lobe. The metabolic activity on PET scan (SUV 4.5) raised concern for malignancy.
PROCEDURE NARRATIVE: Following the induction of general anesthesia and orotracheal intubation, a systematic navigational bronchoscopy was undertaken utilizing the SuperDimension system. We achieved excellent registration error (4.2mm). The catheter was navigated to the lateral basal segment of the right lower lobe. Radial endobronchial ultrasound confirmed a concentric, heterogeneous lesion measuring 27 mm. Subsequently, transbronchial cryobiopsy was performed. Four specimens were obtained with a 1.9 mm probe using a 6-second freeze cycle. Prophylactic placement of an Arndt endobronchial blocker ensured adequate hemostasis."""

entities_2 = [
    {"label": "MEAS_SIZE", **get_span(text_2, "2.8 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right lower lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "SuperDimension system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "4.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "lateral basal segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right lower lobe", 2)},
    {"label": "PROC_METHOD", **get_span(text_2, "Radial endobronchial ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "concentric", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "heterogeneous", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "27 mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "transbronchial cryobiopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Four", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "specimens", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "1.9 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "probe", 1)},
    {"label": "MEAS_TIME", **get_span(text_2, "6-second", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Arndt endobronchial blocker", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 3692014_syn_3
# ==========================================
text_3 = """CPT Coding Justification:
31627 (Navigational Bronchoscopy): Electromagnetic navigation system loaded with CT data; catheter navigated to RLL target.
31654 (Radial EBUS): Peripheral lesion id[REDACTED] via radial probe ultrasound (concentric view) prior to biopsy.
31628 (Transbronchial Biopsy): 1.9mm cryoprobe utilized to obtain parenchymal samples from the RLL lateral basal segment.
Note: Endobronchial blocker used for control, not separately billable as therapeutic tamponade unless bleeding was excessive (it was minimal)."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "radial probe ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Transbronchial Biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "cryoprobe", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "samples", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "lateral basal segment", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Endobronchial blocker", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 3692014_syn_4
# ==========================================
text_4 = """Procedure Note - Pulmonary Service
Attending: Dr. Williams
Resident: Dr. Lee
Procedure: EMN Bronchoscopy w/ Cryobiopsy
Steps:
1. Time out. GA induced. 8.0 ETT.
2. Registration with SuperDimension (Auto).
3. Navigated to RLL nodule (Target 0.8cm away).
4. Radial EBUS confirmation (Concentric).
5. Biopsy: Cryoprobe x4 passes.
6. Hemostasis: Balloon blocker used prophylactically.
7. Extubation stable."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EMN Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "SuperDimension", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "0.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x4", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Balloon blocker", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 3692014_syn_5
# ==========================================
text_5 = """patient [REDACTED] here for the lung nodule biopsy right lower side. we put him asleep general anesthesia tube size 8. used the superdimension navigation thing it worked good got us right to the spot in the rll. radial ebus showed the nodule perfectly concentric view. did the cryo biopsy took 4 pieces froze for 6 seconds each. [REDACTED] put the blocker up so no bleeding really. patient woke up fine sent to recovery check xray for pneumo."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "lung nodule", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "right lower side", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "8", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "superdimension navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "radial ebus", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 2)},
    {"label": "OBS_FINDING", **get_span(text_5, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "cryo biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "4", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "pieces", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "6 seconds", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "blocker", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "pneumo", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 3692014_syn_6
# ==========================================
text_6 = """[REDACTED] navigation bronchoscopy for a right lower lobe nodule. Under general anesthesia with an 8.0 ETT, the SuperDimension system was registered with a fiducial error of 4.2mm. We navigated to the lateral basal segment. Radial EBUS confirmed the lesion location with a concentric view. We performed transbronchial cryobiopsy using a 1.9mm probe for 4 samples. An Arndt blocker was used to manage the airway and prevent bleeding. The patient tolerated the procedure well with no immediate complications."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "navigation bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "SuperDimension system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "4.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "lateral basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "transbronchial cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "probe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "4", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Arndt blocker", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 3692014_syn_7
# ==========================================
text_7 = """[Indication]
2.8cm spiculated RLL nodule, PET avid.
[Anesthesia]
General, 8.0 ETT.
[Description]
Navigated to RLL lateral basal segment (SuperDimension). Radial EBUS confirmed concentric lesion (27mm). Performed transbronchial cryobiopsy x4 samples (1.9mm probe). Arndt blocker used for hemostasis.
[Plan]
Pathology pending. Clinic follow-up 1 week."""

entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "ETT", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "lateral basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "SuperDimension", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "concentric", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "27mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "transbronchial cryobiopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x4", 1)},
    {"label": "SPECIMEN", **get_span(text_7, "samples", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Arndt blocker", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 3692014_syn_8
# ==========================================
text_8 = """The patient, [REDACTED], was brought to the bronchoscopy suite for evaluation of a right lower lobe nodule. After induction of general anesthesia, we proceeded with electromagnetic navigation. The target in the lateral basal segment was reached successfully. We utilized radial EBUS to visualize the lesion, noting a distinct concentric pattern. With the target confirmed, we used a cryoprobe to obtain four biopsies, freezing for six seconds each time. An endobronchial blocker was employed to ensure hemostasis between passes. The procedure concluded without complications, and the patient was extubated."""

entities_8 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lateral basal segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "concentric", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "four", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "MEAS_TIME", **get_span(text_8, "six seconds", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "endobronchial blocker", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 3692014_syn_9
# ==========================================
text_9 = """PROCEDURE: Electromagnetic guidance bronchoscopy (CPT 31627), Radial sonography (CPT 31654), Transbronchial freeze-sampling (CPT 31628).
DETAILS: Navigation established to the RLL target. Sonographic verification revealed a concentric mass. Four tissue samples were harvested using the cryoprobe. An airway occluder was deployed for bleeding control. Hemostasis was secured."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Electromagnetic guidance bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Radial sonography", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Transbronchial freeze-sampling", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "concentric", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "mass", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Four", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "tissue samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "cryoprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "airway occluder", 1)},
]

BATCH_DATA.append({"id": "3692014_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 3692014
# ==========================================
text_10 = """PATIENT: [REDACTED], 67-year-old Male
MRN: [REDACTED]
INDICATION FOR OPERATION: Mr. [REDACTED] is a 67-year-old male with a 2.8cm spiculated right lower lobe nodule discovered on screening CT. PET-avid with SUV 4.5. The nature, purpose, risks, benefits and alternatives to navigational bronchoscopy with cryobiopsy were discussed with the patient in detail. Patient indicated a wish to proceed and informed consent was signed.
PREOPERATIVE DIAGNOSIS: Right lower lobe pulmonary nodule
POSTOPERATIVE DIAGNOSIS: Same
PROCEDURE: Electromagnetic Navigation Bronchoscopy (CPT 31627), Radial EBUS (CPT 31654), Transbronchial Cryobiopsy (CPT 31632), Endobronchial Blocker Placement
ATTENDING: Dr. Patricia Williams
ASSISTANT: Dr. David Lee, Fellow
Support Staff:

RN: Jessica Brown
RT: Anthony Garcia

ANESTHESIA: General anesthesia with endotracheal intubation
MONITORING: Standard ASA monitoring
INSTRUMENT: SuperDimension Navigation System, Olympus BF-1TH190 bronchoscope, 1.9mm cryoprobe, 7Fr Arndt endobronchial blocker
ESTIMATED BLOOD LOSS: 30 mL
COMPLICATIONS: None
PROCEDURE IN DETAIL:
After induction of general anesthesia and intubation with 8.0 ETT, a timeout was performed. All procedure related images were saved and archived.
PATIENT [REDACTED]: Supine
Ventilation Parameters:

Mode: Volume Control
RR: 12
TV: 500mL
PEEP: 5 cmH2O
FiO2: 40%
Flow Rate: 50 L/min
Pmean: 15 cmH2O

Electromagnetic navigation bronchoscopy was performed using the SuperDimension system. CT scan from [REDACTED] was loaded onto the planning station to generate 3D rendering. The navigational plan was reviewed and verified, then loaded into the navigation platform.
EMN Registration: Automatic registration was used. Adequate airway landmark matching achieved at carina, right main carina, and RLL subsegmental bifurcations. Mean fiducial error: 4.2mm. Global alignment quality: excellent.
The EMN catheter was advanced under navigational guidance to the target lesion in the lateral basal segment of the right lower lobe (RB9). Target lesion measured 2.8cm in diameter. Under navigational guidance, the catheter was advanced to 0.8cm from the planned target.
Radial EBUS Survey: Performed to confirm nodule location. The following features were noted: Concentric pattern, heterogeneous echogenicity, lesion size 27mm, no large vessels visualized in the biopsy path.
Transbronchial Cryobiopsy: After confirming absence of significant vessels at the biopsy site with radial EBUS, transbronchial cryobiopsy was performed using a 1.9mm cryoprobe. Freeze-thaw cycle: 6 seconds freeze, passive thaw. After each sample was obtained, the Arndt endobronchial blocker was positioned at the RLL ostium and inflated with 6cc of air for hemostasis. Total 4 samples were collected.
After each biopsy, the blocker was maintained for 2 minutes, then deflated. Inspection showed minimal bleeding, which resolved spontaneously. Final inspection showed patent airways with no active bleeding.
The patient tolerated the procedure well. There were no immediate complications. The attending, Dr. Williams, was present throughout the entire procedure.
SPECIMEN(S):

RLL cryobiopsy x4 (histology)
Additional tissue for molecular testing

IMPRESSION/PLAN: Mr. [REDACTED] underwent successful navigational bronchoscopy with cryobiopsy of RLL nodule. Preliminary frozen section showed atypical cells, final pathology pending. Post-procedure CXR shows no pneumothorax. Patient to follow up in clinic in 1 week for pathology results."""

entities_10 = [
    {"label": "MEAS_SIZE", **get_span(text_10, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "navigational bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Electromagnetic Navigation Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial Cryobiopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Endobronchial Blocker", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "SuperDimension Navigation System", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Olympus BF-1TH190 bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.9mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cryoprobe", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "7Fr", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Arndt endobronchial blocker", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "ETT", 1)},
    {"label": "MEAS_PRESS", **get_span(text_10, "5 cmH2O", 1)},
    {"label": "MEAS_PRESS", **get_span(text_10, "15 cmH2O", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "SuperDimension system", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right main carina", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "4.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lateral basal segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lower lobe", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB9", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.8cm", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "0.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 3)},
    {"label": "OBS_FINDING", **get_span(text_10, "Concentric pattern", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "heterogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "27mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial Cryobiopsy", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.9mm", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cryoprobe", 2)},
    {"label": "MEAS_TIME", **get_span(text_10, "6 seconds", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Arndt endobronchial blocker", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "6cc", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "samples", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsy", 2)},
    {"label": "MEAS_TIME", **get_span(text_10, "2 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "minimal bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no active bleeding", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "cryobiopsy", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x4", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "tissue", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "navigational bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "cryobiopsy", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 4)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 4)},
    {"label": "OBS_FINDING", **get_span(text_10, "atypical cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": "3692014", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)