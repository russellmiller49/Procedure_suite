import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' indices, or None if not found/error.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
            
    if start != -1:
        return {'start': start, 'end': start + len(term)}
    else:
        print(f"Warning: Term '{term}' (occurrence {occurrence}) not found.")
        return None

# ==========================================
# Note 1: 3847592
# ==========================================
id_1 = "3847592"
text_1 = """**INTERVENTIONAL PULMONOLOGY CONSULT & PROCEDURE NOTE**

REQUESTING SERVICE: Medical Oncology (Dr. Stevens)
PATIENT: [REDACTED] | 74F | MRN: [REDACTED]
PROCEDURE DATE: [REDACTED]
IP TEAM: Dr. Kevin Murphy (Attending), Dr. Lisa Chang (Fellow)

**CONSULT QUESTION:**
"Patient with known metastatic breast cancer, now with new RLL nodule. Concern for lung metastasis vs new primary. Please evaluate and biopsy if appropriate. Also noted to have enlarged subcarinal node."

**HISTORY:**
74F with PMH of Stage II ER+/HER2- invasive ductal breast carcinoma diagnosed 2017, treated with lumpectomy + radiation + endocrine therapy. Developed bone and liver metastases 2023, currently on palbociclib + letrozole with stable disease.

Recent surveillance CT shows new 2.8cm RLL nodule (not present on prior CT 6 months ago). Also new subcarinal lymphadenopathy 2.1cm. PET/CT: RLL nodule SUV 6.4, subcarinal node SUV 5.9.

Clinical question: Progression of breast cancer to lung vs. new primary lung cancer (would change management significantly).

**RECOMMENDATION:**
Combined EBUS-TBNA + EMN bronchoscopy for tissue diagnosis with appropriate immunohistochemistry to differentiate breast metastasis vs primary lung cancer.

Patient [REDACTED]or procedure same day given oncologic urgency.
**PROCEDURE PERFORMED:**

**EBUS-TBNA + EMN Bronchoscopy + Transbronchial Biopsy**

Consent obtained. Anesthesia: MAC (Dr. Roberts). ETT 7.5.

**PHASE 1 - EBUS:**

Surveyed mediastinum systematically.

Station 7 (subcarinal):
- 21 x 18mm, hypoechoic, round
- 22G needle, 5 passes
- ROSE (Dr. Williams): "Positive for malignancy. Adenocarcinoma cells. CK7+/CK20- pattern on rapid IHC. Cannot definitively distinguish breast met vs lung primary on cytology alone - recommend tissue biopsy with full IHC panel."

Other stations surveyed - no other enlarged nodes.

**PHASE 2 - EMN to RLL nodule:**

SuperDimension system. CT from [REDACTED] loaded.
Target: RLL lateral basal segment nodule.

Registration: Auto, 8 points, good accuracy.

Navigated to target - distance 0.7cm per system.

Radial EBUS: Concentric pattern, 26mm heterogeneous lesion.

Sampling:
- TBBx x 8 (formalin - **REQUEST FULL IHC PANEL: TTF-1, Napsin-A, CK7, CK20, ER, PR, HER2, GATA-3, Mammaglobin**)
- Brushings x 3
- BAL

ROSE: "Adenocarcinoma. Morphology could represent either primary lung or breast metastasis. IHC panel will be definitive."

No complications. CXR: no PTX.

**IMPRESSION:**
Adenocarcinoma in both subcarinal node and RLL nodule. Awaiting IHC to determine if breast metastasis vs primary lung cancer.

If breast metastasis → continue systemic breast cancer therapy
If primary lung cancer → separate staging/treatment approach needed

**PLAN:**
- IHC panel expedited (results expected 05/09)
- Contact patient with results
- Tumor board if lung primary confirmed
- Close communication with medical oncology

K. Murphy MD
**BRONCHOSCOPY REPORT - COMBINED MODALITY**

Institution: [REDACTED]
Date of Service: [REDACTED]

**PATIENT:** Nguyen, Linh T., Female, Age 56
**MRN:** 2938475
**ATTENDING:** Dr. Patricia Lee, MD, FCCP
**FELLOW:** Dr. Michael Torres, MD
**ANESTHESIA:** Dr. David Chen, MD

**INDICATION:**
- RML nodule 2.2cm (increased from 1.6cm over 6 months)
- Mediastinal lymphadenopathy: Station 4R 2.0cm, Station 7 1.6cm
- Never-smoker
- PET: RML nodule SUV 5.2, Station 4R SUV 4.1, Station 7 SUV 3.4

**PROCEDURES:**
1. EBUS with TBNA
2. Ion robotic bronchoscopy
3. Radial EBUS
4. Transbronchial biopsy with cryobiopsy

**CONSENT:** Standard risks discussed (PTX 1-3%, bleeding 1-5%, higher with cryo 5-10%, infection, anesthesia risks, etc.). Patient consented.

**ANESTHESIA:** General/ETT, ETT 7.5 at 21cm

**VENTILATOR SETTINGS:**
- Mode: Pressure Control
- Inspiratory Pressure: 17 cmH2O
- RR: 14
- PEEP: 5
- FiO2: 50%

**TIME-OUT:** Performed per protocol
**PROCEDURE DETAILS:**

**EBUS Phase:**

Using Olympus EBUS scope, performed systematic mediastinal survey.

**Station 2R:** 8mm - not sampled
**Station 2L:** Not enlarged

**Station 4R (Right paratracheal):**
- Size: 19 x 15mm
- Echo: Hypoechoic, heterogeneous
- Shape: Oval, margins discrete
- Elastography: Intermediate stiffness (strain ratio 5.4)
- **Sampling:** 22G needle, 5 passes
- ROSE (Dr. Kumar): "Adequate. Atypical epithelial cells. Glandular features. Favor adenocarcinoma. Recommend core tissue for molecular."

**Station 7 (Subcarinal):**
- Size: 15 x 13mm
- Echo: Hypoechoic, homogeneous
- Appears reactive
- **Sampling:** 22G needle, 3 passes
- ROSE: "Negative for malignancy. Reactive lymphocytes only."

**Stations 10R, 11R:** Normal size, not sampled
**Ion Robotic Bronchoscopy Phase:**

CT from [REDACTED] loaded to Ion platform.
Target: RML medial segment nodule.

**Registration:**
- Automatic method
- Fiducial error: 1.4mm
- Quality: Excellent
- Landmarks: Carina, RUL/RML/RLL bifurcation, RML segmental anatomy

**Navigation:**
Ion catheter advanced to RML medial segment.
Tool-to-target: 0.8cm

**Radial EBUS:**
- Pattern: Concentric
- Size: 20mm
- Echo: Heterogeneous, irregular margins
- No large vessels

**CBCT Confirmation:**
Cone-beam CT acquired. NaviLink fusion confirmed catheter within lesion, 3mm from center.

**Sampling:**

**Conventional:**
- Forceps biopsies x 6
- Brushings x 3
- Washing

ROSE: "Adenocarcinoma, similar to node"

**Cryobiopsy:**
Given need for molecular testing and never-smoker status:

Arndt blocker (7Fr) positioned in RML ostium.

Cryoprobe 1.9mm advanced through Ion catheter.
- 2 cryobiopsies obtained (4 sec freeze each)
- Blocker inflated between samples
- Minimal bleeding, resolved with blocker + iced saline
**COMPLETION:**

Procedure time: 69 minutes
No complications
Extubated successfully
Post-procedure vitals stable

**EBL:** ~20mL

**SPECIMENS:**
1. Station 4R TBNA x5 (cell block)
2. Station 7 TBNA x3 (cell block)
3. RML forceps biopsy x6 (formalin)
4. RML cryobiopsy x2 (formalin) - **REQUEST: EGFR, ALK, ROS1, PD-L1, comprehensive NGS**
5. RML brushings x3 (cytology)
6. RML washing (cytology + micro)

**Post-op CXR:** No pneumothorax. Small subsegmental atelectasis RML (expected post-cryobiopsy). No intervention needed.
**FINDINGS (based on ROSE):**
- Station 4R: Positive for adenocarcinoma (N2)
- Station 7: Negative (N0)
- RML nodule: Adenocarcinoma (primary)

**Preliminary Stage:** IIIA (T1cN2M0)

**ASSESSMENT:**
Stage IIIA adenocarcinoma. Never-smoker with N2 disease. Will require neoadjuvant therapy vs definitive chemoradiation. Molecular results critical given never-smoker status - high likelihood of targetable mutation.

**PLAN:**
- Complete staging: Brain MRI
- Await molecular testing (7-14 days)
- Tumor board presentation
- Medical oncology consult
- Thoracic surgery consult
- If EGFR/ALK+ → neoadjuvant targeted therapy consideration
- F/u IP clinic 1 week

Dr. Patricia Lee - Attending, present throughout procedure

**Electronically signed: [REDACTED] 16:33**
**PROCEDURE: EBUS-TBNA + ELECTROMAGNETIC NAVIGATION BRONCHOSCOPY**

Valley Medical Center | IP Service

**PT:** Davis, Harold K. | 72M | MRN [REDACTED]
**DATE:** [REDACTED]
**PHYSICIANS:** Dr. Jennifer Walsh (Attending), Dr. Christopher Brown (Fellow), Dr. Amanda Stevens (Anesthesia)

**INDICATION:**

72M with 60 pack-year smoking history presents with concerning imaging:

Primary lesion:
- LUL mass 4.3cm, cavitary with thick irregular walls
- PET SUV 9.8

Lymphadenopathy:
- Station 4L: 2.4cm, SUV 7.1
- Station 5: 2.2cm, SUV 6.8
- Station 7: 1.9cm, SUV 5.4
- Station 10L: 1.7cm, SUV 4.9

Patient [REDACTED] weight loss (20 lbs / 3 months), new hemoptysis (scant blood-streaking). Requires diagnosis and staging.

**PROCEDURES PERFORMED:**
- EBUS-TBNA (multiple stations)
- EMN bronchoscopy
- Radial EBUS
- Transbronchial biopsy
- Endobronchial biopsy (visible tumor in LUL)

**CONSENT:** Obtained. Comprehensive risk discussion including higher bleeding risk given hemoptysis history. Patient understood and agreed.

**ANESTHESIA:**
General with ETT (8.0 at 23cm)
VC mode: TV 500, RR 12, PEEP 5, FiO2 55%, Pmean 13
**PROCEDURE:**

**Part 1: EBUS-TBNA**

EBUS bronchoscope inserted through ETT.

**Mediastinal Survey:**

**Station 4R:** 11mm - appears reactive, not sampled

**Station 4L:**
- 23 x 19mm
- Hypoechoic, heterogeneous, round (loss of oval shape)
- 22G needle, 5 passes
- ROSE (Dr. Martinez): \"POSITIVE - Squamous cell carcinoma\"

**Station 5 (AP window):**
- 21 x 18mm
- Hypoechoic, irregular borders
- 22G needle, 5 passes
- ROSE: \"POSITIVE - Squamous cell carcinoma\"

**Station 7:**
- 18 x 16mm
- Hypoechoic
- 22G needle, 4 passes
- ROSE: \"POSITIVE - Squamous cell carcinoma\"

**Station 10L:**
- 16 x 14mm
- Hypoechoic
- 22G needle, 3 passes
- ROSE: \"POSITIVE - Squamous cell carcinoma\"

**Nodal Staging Summary:** Extensive disease - N1, N2, and N3 all involved
**Part 2: Standard Airway Survey**

EBUS scope removed. Therapeutic bronchoscope (Olympus BF-1TH190) inserted.

**Finding:** LUL orifice shows exophytic endobronchial tumor - fungating mass with areas of necrosis, nearly occluding lingual ostium.

**Endobronchial Biopsy:**

Given visible endobronchial component, obtained direct biopsies before proceeding to EMN:
- 6 forceps biopsies from endobronchial tumor
- Friable tissue, moderate bleeding
- Managed with epinephrine 1:10,000 5mL + wedging scope
- Hemostasis achieved

ROSE: \"Squamous cell carcinoma - consistent with nodal samples\"
**Part 3: EMN to Cavitary Component**

Despite endobronchial biopsy being diagnostic, proceeded with EMN to sample cavitary/necrotic component given potential for different biology/infectious etiology.

SuperDimension system. CT from [REDACTED].

Registration: Automatic, 7 points confirmed.

Target: LUL apical-posterior segment (cavitary portion of mass).

Navigation: Challenging due to tumor distortion of anatomy. Unable to reach planned depth (tumor blocking). Achieved position ~12mm from target per system.

Radial EBUS: Eccentric pattern, visualizing mass edge/cavity wall.

Sampling through guide sheath:
- Forceps biopsies x 5 (from cavity wall)
- Brushings x 2
- BAL x 100cc (sent for bacterial/fungal/AFB cultures + cytology)

ROSE: \"Squamous cell carcinoma, areas of necrosis\"
**COMPLETION:**

Total time: 64 minutes
Moderate bleeding from endobronchial site - resolved
Patient [REDACTED]

**EBL:** ~40mL

**SPECIMENS:**
1. Station 4L TBNA x5
2. Station 5 TBNA x5
3. Station 7 TBNA x4
4. Station 10L TBNA x3
5. LUL endobronchial biopsies x6
6. LUL cavity wall biopsies (EMN) x5
7. LUL brushings x2
8. LUL BAL (cultures + cytology)

**REQUEST PD-L1 testing on tumor specimens**

**COMPLICATIONS:** Moderate endobronchial bleeding - controlled

**POST-OP CXR:** No pneumothorax. Known LUL cavitary mass unchanged.
**FINDINGS:**

**Diagnosis:** Squamous cell carcinoma of LUL with extensive nodal metastases

**Staging:**
- T: T3 (4.3cm with cavitation)
- N: N3 (contralateral mediastinal node station 4L positive)
- M: M0 (pending complete staging)
- **Stage: IIIB (T3N3M0)**

**Characteristics:**
- Cavitary lesion (concerning - DDx includes post-obstructive pneumonia, tumor necrosis)
- Endobronchial extension with near-obstruction
- Extensive nodal disease

**NOT A SURGICAL CANDIDATE** - Stage IIIB with N3 disease
**PLAN:**

**Immediate:**
- Monitor for post-procedure bleeding (patient with prior hemoptysis)
- Continue observation overnight given bleeding during procedure
- F/u CXR in AM

**Staging:**
- Brain MRI
- Complete PET/CT review (ensure no distant mets)

**Infectious Work-up:**
- Culture results pending (bacterial/fungal/AFB from BAL)
- Consider CT-guided drainage if abscess component id[REDACTED]
- Empiric antibiotics if clinical signs of post-obstructive pneumonia

**Oncologic:**
- Medical oncology urgent consult
- Radiation oncology consult
- Definitive concurrent chemoradiation (platinum-doublet + RT)
- PD-L1 results will guide immunotherapy consideration
- Hemoptysis precautions - may need palliative RT if worsens

**Follow-up:**
- IP clinic 1 week
- Earlier if concerning symptoms (increased hemoptysis, fever, dyspnea)

**Prognosis Discussion:**
- Stage IIIB - locally advanced
- Not curable with surgery
- Chemoradiation can provide long-term control in some patients
- Will need frank discussion of prognosis and goals of care

Dr. Jennifer Walsh, Attending Physician
Procedure performed and supervised in entirety

**Signed: [REDACTED] 17:55**"""

entities_1 = [
    # --- Case 1: Murphy (RLL/Subcarinal) ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "subcarinal", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_1, "PMH", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "subcarinal", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EMN bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 2)}, # Transbronchial Biopsy header
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 2)}, # PHASE 1 - EBUS
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "subcarinal", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21 x 18mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Positive for malignancy", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma cells", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EMN", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 5)},
    {"label": "PROC_METHOD", **get_span(text_1, "SuperDimension system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal segment", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Registration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8 points", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "26mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Sampling", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "no PTX", 1)},

    # --- Case 2: Lee (RML/Robotic) ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.2cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.0cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.6cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "cryobiopsy", 1)},
    {"label": "MEAS_PRESS", **get_span(text_1, "17 cmH2O", 1)},
    {"label": "MEAS_PRESS", **get_span(text_1, "5", 1)}, # PEEP
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "EBUS scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19 x 15mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical epithelial cells", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15 x 13mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 3)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Negative for malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Stations 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Ion catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial segment", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Cone-beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Washing", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Cryobiopsy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Arndt blocker", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "RML ostium", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cryoprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "4 sec", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "69 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 2)},
    {"label": "MEAS_VOL", **get_span(text_1, "20mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "atelectasis", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "16:33", 1)},

    # --- Case 3: Walsh (LUL/Squamous) ---
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "4.3cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.4cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 5", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.2cm", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 5)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.7cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Transbronchial biopsy", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Endobronchial biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23 x 19mm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "POSITIVE - Squamous cell carcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 5", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21 x 18mm", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 6)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18 x 16mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16 x 14mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "LUL orifice", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "endobronchial tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "necrosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "lingual ostium", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Endobronchial Biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Friable tissue", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "moderate bleeding", 1)},
    {"label": "MEDICATION", **get_span(text_1, "epinephrine", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL apical-posterior segment", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "100cc", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "64 minutes", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "40mL", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "17:55", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)