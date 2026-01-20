import sys
from pathlib import Path

# 1. Dynamic Repo Root
# -------------------------------------------------------------------------
# Expected location:
#   <repo>/data/granular annotations/Python_update_scripts/<id>.py
# so parents[3] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# 2. Import Utility
# -------------------------------------------------------------------------
try:
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

# 3. Helper Function
# -------------------------------------------------------------------------
def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the Nth occurrence of 'term' in 'text'.
    Returns (start, end) tuple.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return start, start + len(term)

# 4. Data Payload
# -------------------------------------------------------------------------
BATCH_DATA = []

# -------------------------------------------------------------------------
# Case 1: 4829301_syn_1
# -------------------------------------------------------------------------
text_1 = """Indication: LLL nodule.
Procedure: EMN bronchoscopy.
Guidance: SuperDimension + Radial EBUS.
Action: TBBx x6, Brush x3.
ROSE: Adenocarcinoma.
Complications: None."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(text_1, "nodule", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_1, "EMN bronchoscopy", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_1, "SuperDimension", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_1, "TBBx", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_1, "x6", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_1, "Brush", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_1, "x3", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_1, "Adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", "span": get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_1", "text": text_1, "entities": entities_1})

# -------------------------------------------------------------------------
# Case 2: 4829301_syn_2
# -------------------------------------------------------------------------
text_2 = """OPERATIVE REPORT: The patient underwent electromagnetic navigation bronchoscopy for a hypermetabolic left lower lobe nodule. The SuperDimension system facilitated navigation to the superior segment. Radial EBUS demonstrated a concentric, hypoechoic lesion. Transbronchial biopsies and brushings were obtained. Preliminary cytopathologic evaluation confirmed the presence of malignant cells consistent with adenocarcinoma."""

entities_2 = [
    {"label": "PROC_METHOD", "span": get_span(text_2, "electromagnetic navigation bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_2, "left lower lobe", 1)},
    {"label": "OBS_LESION", "span": get_span(text_2, "nodule", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_2, "SuperDimension", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_2, "superior segment", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_2, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", "span": get_span(text_2, "hypoechoic", 1)},
    {"label": "OBS_LESION", "span": get_span(text_2, "lesion", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_2, "Transbronchial biopsies", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_2, "brushings", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_2, "adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_2", "text": text_2, "entities": entities_2})

# -------------------------------------------------------------------------
# Case 3: 4829301_syn_3
# -------------------------------------------------------------------------
text_3 = """Code Selection: 31627 (Navigational bronchoscopy), 31654 (Radial EBUS), 31628 (Transbronchial lung biopsy).
Justification: Computer-assisted navigation was required to reach the peripheral LLL lesion. Radial EBUS confirmed the location. Multiple transbronchial biopsies were obtained for diagnosis."""

entities_3 = [
    {"label": "PROC_METHOD", "span": get_span(text_3, "Navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_3, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_3, "Transbronchial lung biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_3, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(text_3, "lesion", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_3, "Radial EBUS", 2)},
    {"label": "PROC_ACTION", "span": get_span(text_3, "transbronchial biopsies", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_3", "text": text_3, "entities": entities_3})

# -------------------------------------------------------------------------
# Case 4: 4829301_syn_4
# -------------------------------------------------------------------------
text_4 = """Procedure Note
Patient: [REDACTED]
Indication: LLL mass.
Steps:
1. SuperDimension registration.
2. Navigated to LLL superior segment.
3. Confirmed with REBUS (concentric view).
4. Biopsies (forceps x6) and brushings x3.
5. ROSE positive for Adeno.
6. No bleeding.
Plan: D/C if CXR clear."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_4, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(text_4, "mass", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_4, "SuperDimension", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_4, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_4, "superior segment", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_4, "REBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_4, "Biopsies", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_4, "forceps", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_4, "x6", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_4, "brushings", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_4, "x3", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_4, "Adeno", 1)},
    {"label": "OUTCOME_COMPLICATION", "span": get_span(text_4, "No bleeding", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_4", "text": text_4, "entities": entities_4})

# -------------------------------------------------------------------------
# Case 5: 4829301_syn_5
# -------------------------------------------------------------------------
text_5 = """Robert has a LLL nodule used the superdimension to get there. Radial probe showed it nicely concentric view. Took 6 biopsies and some brushes. Cytotech said it looks like adenocarcinoma. No bleeding patient did great. checking cxr before discharge."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_5, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(text_5, "nodule", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_5, "superdimension", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_5, "Radial probe", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_5, "6", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_5, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_5, "brushes", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_5, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", "span": get_span(text_5, "No bleeding", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_5", "text": text_5, "entities": entities_5})

# -------------------------------------------------------------------------
# Case 6: 4829301_syn_6
# -------------------------------------------------------------------------
text_6 = """Electromagnetic Navigation Bronchoscopy with transbronchial biopsy and radial EBUS. Patient is a 71-year-old male with LLL nodule. Virtual pathway created to LLL superior segment nodule. Extended working channel placed. Radial EBUS demonstrated concentric hypoechoic lesion. Transbronchial forceps biopsies and cytology brush specimens obtained. ROSE positive for malignancy. No complications. Discharged home."""

entities_6 = [
    {"label": "PROC_METHOD", "span": get_span(text_6, "Electromagnetic Navigation Bronchoscopy", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_6, "transbronchial biopsy", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_6, "radial EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_6, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(text_6, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_6, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_6, "superior segment", 1)},
    {"label": "OBS_LESION", "span": get_span(text_6, "nodule", 2)},
    {"label": "DEV_CATHETER", "span": get_span(text_6, "Extended working channel", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_6, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", "span": get_span(text_6, "hypoechoic", 1)},
    {"label": "OBS_LESION", "span": get_span(text_6, "lesion", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_6, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_6, "cytology brush", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_6, "malignancy", 1)},
    {"label": "OUTCOME_COMPLICATION", "span": get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_6", "text": text_6, "entities": entities_6})

# -------------------------------------------------------------------------
# Case 7: 4829301_syn_7
# -------------------------------------------------------------------------
text_7 = """[Indication]
LLL nodule, PET avid.
[Anesthesia]
Moderate sedation.
[Description]
EMN navigation to LLL. REBUS confirmation. Transbronchial biopsy and brushing performed. ROSE positive for adenocarcinoma.
[Plan]
Oncology referral."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_7, "LLL", 1)},
    {"label": "OBS_LESION", "span": get_span(text_7, "nodule", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_7, "EMN navigation", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_7, "LLL", 2)},
    {"label": "PROC_METHOD", "span": get_span(text_7, "REBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_7, "Transbronchial biopsy", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_7, "brushing", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_7, "adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_7", "text": text_7, "entities": entities_7})

# -------------------------------------------------------------------------
# Case 8: 4829301_syn_8
# -------------------------------------------------------------------------
text_8 = """We performed a navigational bronchoscopy on [REDACTED] a nodule in his left lower lung. Using the electromagnetic navigation system, we guided a catheter to the lesion and confirmed its position with ultrasound. We then took several biopsies and brush samples. The immediate analysis in the room showed cancer cells, likely adenocarcinoma. He recovered well and is being discharged."""

entities_8 = [
    {"label": "PROC_METHOD", "span": get_span(text_8, "navigational bronchoscopy", 1)},
    {"label": "OBS_LESION", "span": get_span(text_8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_8, "left lower lung", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_8, "electromagnetic navigation system", 1)},
    {"label": "DEV_CATHETER", "span": get_span(text_8, "catheter", 1)},
    {"label": "OBS_LESION", "span": get_span(text_8, "lesion", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_8, "biopsies", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_8, "adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_8", "text": text_8, "entities": entities_8})

# -------------------------------------------------------------------------
# Case 9: 4829301_syn_9
# -------------------------------------------------------------------------
text_9 = """Procedure: Electromagnetic navigational sampling.
Target: LLL superior segment lesion.
Method: SuperDimension guidance with REBUS confirmation.
Action: Forceps and brush acquisition of tissue.
Diagnosis: Adenocarcinoma confirmed via ROSE."""

entities_9 = [
    {"label": "PROC_METHOD", "span": get_span(text_9, "Electromagnetic navigational sampling", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_9, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_9, "superior segment", 1)},
    {"label": "OBS_LESION", "span": get_span(text_9, "lesion", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_9, "SuperDimension", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_9, "REBUS", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_9, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_9, "brush", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_9, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "4829301_syn_9", "text": text_9, "entities": entities_9})

# -------------------------------------------------------------------------
# Case 10: 4829301
# -------------------------------------------------------------------------
# Note: This is a large composite note. We will map entities found across the text.
text_10 = """**Procedure Documentation**
Memorial Regional Medical Center

Date: [REDACTED]
Patient: [REDACTED], 71F, MRN [REDACTED]
Providers: Attending - Dr. James Mitchell | Fellow - Dr. Rebecca Torres
Anesthesia: Dr. Andrew Kim (CRNA supervision)

**Reason for procedure:**
- RLL nodule 2.9cm, irregular margins, SUV 8.1
- Right hilar lymphadenopathy (station 10R, 2.2cm, SUV 6.3)
- Left paratracheal node (station 4L, 1.7cm, SUV 3.2)

Clinical question: Primary lung cancer with mediastinal spread vs other?

**Procedures done:**
1. EBUS with TBNA (mediastinal + hilar staging)
2. Ion robotic bronchoscopy (RLL mass biopsy)
3. Radial EBUS
4. Cryobiopsy of RLL mass

**Consent:**
Standard risks reviewed (bleeding, PTX, infection, need for more procedures, anesthesia risks). Patient understood and consented.

**Anesthesia:**
General with ETT (7.5, depth 21cm). Propofol/Sevo/Fentanyl. Pressure control ventilation: Pinsp 16, RR 14, PEEP 5, FiO2 45%.

**Time-out:** Done. Patient ID [REDACTED], procedure confirmed, imaging reviewed.

**PROCEDURE DETAILS:**

**EBUS Phase:**

Used Olympus EBUS scope. Systematic node survey:

Station 2R: Not enlarged
Station 2L: Not enlarged
Station 4R: 9mm, normal appearance

**Station 4L:**
- Size: 16 x 13 mm
- Echo features: Hypoechoic, homogeneous
- Shape: Oval
- Borders: Discrete
- Central hilar vessels: Present
- **Sampled:** 22G needle, 4 passes
- **ROSE:** "Negative for malignancy. Lymphocytes and anthracotic pigment. Appears reactive."

Station 7: 12mm, appears benign, not sampled

**Station 10R (right hilar):**
- Size: 21 x 18 mm
- Echo features: Hypoechoic, heterogeneous
- Shape: Round
- **Sampled:** 22G needle, 5 passes
- **ROSE:** "POSITIVE for malignancy. Atypical epithelial cells, favor adenocarcinoma. Recommend core biopsy for molecular testing."

Station 11R: 10mm, not sampled (10R already positive)

Stations 10L, 11L: Normal size

**Ion Robotic Bronchoscopy Phase:**

EBUS scope out, Ion scope in through ETT.

Pre-procedure CT ([REDACTED]) loaded to Ion workstation. Target id[REDACTED]: RLL superior segment mass.

**Registration:**
- Method: Automatic
- Quality: Excellent
- Landmarks: Carina, right main carina, RLL carina, superior segment bifurcation
- Fiducial error: 1.1mm
- No drift detected

**Navigation:**
Ion catheter deployed and advanced along virtual pathway. Some minor course corrections needed at superior segmental bronchus due to anatomy. Final tool-to-target distance per system: 0.6cm.

**Radial EBUS verification:**
- Inserted through Ion working channel
- Pattern: Concentric
- Lesion size: 27mm
- Appearance: Heterogeneous echo, irregular margins
- No large vessels in sampling path

**CBCT/Fusion:**
Cone-beam CT acquired. NaviLink fusion showed catheter well-positioned within lesion volume, tip 3mm from center.

**Sampling strategy:**
Given ROSE positive from node and need for molecular testing, decided to obtain both conventional and cryobiopsy specimens.

**Conventional samples:**
- Forceps biopsies x 6 through Ion catheter
- Brushings x 3
- Washing for micro + cyto

**ROSE (conventional):** "Adenocarcinoma, similar to lymph node"

**Cryobiopsy:**
Arndt blocker (7Fr) placed in RLL ostium for airway protection.

Cryoprobe (1.9mm) advanced through Ion catheter to target.
- Freeze x 4 seconds
- Withdrew probe en bloc with bronchoscope
- Blocker inflated immediately (5cc air)
- Sample obtained, thawed, to formalin
- Repeated for total of 2 cryobiopsies
- Blocker inflated 45 seconds after each

Mild bleeding after cryobiopsies. Managed with:
- Wedging scope in RLL
- Iced saline 30cc
- Blocker inflation
- Hemostasis achieved

**Final airway check:**
No active bleeding. Airways clear.

**Procedure time:** 71 minutes (EBUS 28 min, Ion 43 min)

**Extubation:** Smooth, patient to PACU stable

**EBL:** ~25mL

**Specimens sent:**
1. Station 4L TBNA x 4 (cell block)
2. Station 10R TBNA x 5 (cell block)
3. RLL mass forceps biopsy x 6 (formalin) - **REQUEST MOLECULAR: EGFR, ALK, ROS1, PD-L1, comprehensive NGS**
4. RLL mass cryobiopsies x 2 (formalin) - **MOLECULAR TESTING**
5. RLL mass brushings x 3 (cytology)
6. RLL mass washing (micro + cyto)

**Complications:** None

**ROSE Summary:**
- Station 4L: Negative (reactive)
- Station 10R: Positive for adenocarcinoma (N1 disease)
- RLL mass: Positive for adenocarcinoma (primary)

**Preliminary staging:** Stage IIIA - T1c (2.9cm) N1 (ipsilateral hilar node positive) M0

**Next steps:**
- Complete staging: Brain MRI, bone scan or review PET coverage
- Await molecular testing (critical for treatment planning)
- MDT tumor board presentation
- Likely surgical candidate after neoadjuvant therapy vs upfront surgery (thoracic surgery consult)\n- IP clinic f/u 1 week for final path + molecular results

Post-procedure CXR: No pneumothorax

Dr. James Mitchell, MD - attending present throughout procedure
**IP PROCEDURE NOTE**

**PT INFO:** Rodriguez, Carlos M. | 59M | MRN [REDACTED]
**DOS:** [REDACTED]
**TEAM:** Dr. Amanda Foster (Attending), Dr. Brian Lee (Fellow), RN Maria Santos, RT Kevin Johnson
**ANESTHESIA:** Dr. Michelle Chang - General/ETT

**INDICATION:**
LLL mass 5.1cm with endobronchial extension + extensive mediastinal/hilar adenopathy. Heavy smoker (80 py). Needs diagnosis and staging.

**PROCEDURES:**
- EBUS-TBNA
- Electromagnetic navigation bronchoscopy
- Radial EBUS
- Transbronchial biopsies
- Endobronchial biopsies

**CONSENT:** Obtained - all risks discussed

**VENT:** PC mode, Pinsp 20, RR 12, PEEP 5, FiO2 50%, Pmean 14

**PROCEDURE:**

**PART 1: EBUS-TBNA**

EBUS scope inserted through ETT (8.0, 23cm).

**Mediastinal Survey:**

**Station 2R:** 7mm - not sampled

**Station 4R:** 24mm - hypoechoic, heterogeneous
- 22G needle x 5 passes
- ROSE: "Positive - squamous cell carcinoma"

**Station 4L:** 19mm - hypoechoic
- 22G needle x 4 passes
- ROSE: "Positive - squamous cell carcinoma"

**Station 7:** 28mm - large, hypoechoic, necrotic areas visible
- 22G needle x 5 passes (some passes yielded necrotic material)
- ROSE: "Positive - squamous cell carcinoma, areas of necrosis"

**Station 10L:** 22mm - hypoechoic
- 22G needle x 4 passes
- ROSE: "Positive - squamous cell carcinoma"

**Station 11L:** 18mm - hypoechoic
- 22G needle x 3 passes
- ROSE: "Positive - squamous cell carcinoma"

**Assessment after EBUS:** Extensive N2/N3 disease. Primary still needs biopsy for confirmation.

**PART 2: AIRWAY INSPECTION**

EBUS scope removed. Standard bronchoscope inserted.

**Finding:** LLL orifice shows endobronchial tumor - exophytic mass nearly occluding orifice, friable appearance.

**Decision:** Obtain endobronchial biopsies directly (easier/safer than navigating to peripheral component).

**Endobronchial biopsies:** 6 specimens obtained from visible LLL tumor using standard forceps.

Moderate bleeding from biopsy site. Managed with:
- Wedging bronchoscope
- Epinephrine 1:10,000, 5mL instilled
- Held position x 2 minutes
- Bleeding resolved

**ROSE (endobronchial):** "Squamous cell carcinoma - consistent with nodal samples"

**PART 3: EMN TO PERIPHERAL COMPONENT**

Despite endobronchial component, decided to sample peripheral component as well for potentially better tissue for molecular testing.

SuperDimension EMN system used. CT from [REDACTED] loaded.

**Registration:** Auto-registration, 7 points, adequate accuracy.

**Navigation:** Attempted to navigate to LLL superior segment (peripheral component of mass). However, significant tumor in proximal airway made navigation difficult. Guide advanced as far as possible but unable to reach planned target (remained ~15mm away per system).

**Radial EBUS:** Probe advanced through guide - visualized mass with eccentric pattern but adequate for sampling.

**Peripheral sampling:**
- Forceps biopsies x 5
- Brushings x 2

**ROSE:** "Squamous cell carcinoma - adequate for molecular testing"

**TOTAL TIME:** 58 minutes

**EXTUBATION:** Uneventful, stable

**EBL:** ~30mL

**SPECIMENS:**
1. Station 4R TBNA x5
2. Station 4L TBNA x4
3. Station 7 TBNA x5
4. Station 10L TBNA x4
5. Station 11L TBNA x3
6. LLL endobronchial tumor biopsies x6
7. LLL peripheral component biopsies x5 (via EMN)
8. LLL brushings x2

**ALL SPECIMENS:** Request PD-L1 testing (relevant for squamous NSCLC treatment decisions)

**COMPLICATIONS:** Moderate endobronchial bleeding - resolved with epinephrine

**FINDINGS:**
- Extensive nodal disease: N2 (stations 4R, 4L, 7) and N3 (contralateral 4L) involvement
- Primary LLL squamous cell carcinoma with endobronchial extension
- Stage: At least IIIB (T3-4N3M0)

**PLAN:**
- Complete staging: Brain MRI
- Not surgical candidate due to extent of nodal disease
- Medical oncology consult - definitive chemoradiation vs clinical trial
- PD-L1 results may influence systemic therapy choice
- F/u 1 week IP clinic

Post-op CXR: No PTX
**COMBINED EBUS + ROBOTIC BRONCHOSCOPY**

City Hospital - Interventional Pulmonology Service

**Patient:** Wu, Jennifer S., Age 52, Female
**MRN:** 7739284
**Procedure Date:** [REDACTED]
**Attending:** Dr. Daniel Martinez
**Fellow:** Dr. Sarah Patel
**Anesthesia:** Dr. Christopher Lee (General anesthesia/ETT)

**Clinical History:**
Never-smoker with RUL nodule discovered on screening CT. Nodule has grown from 1.2cm to 2.4cm over 12 months. PET shows moderate FDG avidity (SUV 4.7). Right paratracheal lymph node 1.9cm, SUV 3.8. Referred for combined mediastinal staging and peripheral nodule biopsy.

**Procedures:**
1. EBUS-TBNA (mediastinal staging)
2. Ion robotic bronchoscopy
3. Radial EBUS
4. Transbronchial biopsy with cryobiopsy

**Informed Consent:** Standard procedural risks reviewed including pneumothorax (quoted 1-3% standard, 5-10% with cryobiopsy), bleeding, infection, need for intervention. Patient verbalized understanding, signed consent.

**Anesthesia Details:**
- ETT 7.5 at 21cm
- Induction: Propofol/Rocuronium/Fentanyl
- Maintenance: Sevoflurane
- Ventilation: VC mode, TV 450, RR 12, PEEP 5, FiO2 55%

**Monitoring:** Continuous pulse ox, EKG, BP, ETCO2. Dedicated RN for monitoring (Jessica Adams).

**Timeout:** Performed confirming patient, procedure, site.
**PHASE 1: EBUS-TBNA**

EBUS bronchoscope (Olympus BF-UC190F) introduced through ETT.

**Mediastinal lymph node survey:**

Systematic evaluation performed. Measured all visible nodes ≥5mm.

**Station 2R:** 6mm - not sampled
**Station 2L:** Not visualized

**Station 4R (Right paratracheal):**
- Ultrasound size: 18 x 14 mm
- Characteristics: Hypoechoic, discrete borders, oval shape
- Central vessels: Present (hilar vessel sign)
- Elastography: Mixed blue/green pattern (intermediate stiffness, strain ratio 4.2)
- **Sampling:** 22-gauge EBUS needle, 5 passes performed
  - Pass 1-2: White cores visible in needle
  - Pass 3-5: Adequate material expressed
- **ROSE (Dr. Patricia Kim, cytopathologist):** "Adequate cellularity. Atypical glandular cells present. Favor adenocarcinoma. Recommend core biopsy for confirmation and molecular studies."

**Station 4L:** 11mm - appears reactive, not sampled given positive 4R

**Station 7 (Subcarinal):** 12mm - homogeneous, likely reactive, not sampled

**Station 10R (Right hilar):** 14mm - sampled given close proximity to primary tumor
- 22-gauge needle, 3 passes
- **ROSE:** "Negative for malignancy. Anthracotic pigment and lymphocytes only."

Additional stations: 10L, 11R, 11L all <10mm, not sampled.

**EBUS Conclusions:**
- N2 disease suggested by positive station 4R
- Hilar node negative (10R)
- Requires primary tumor sampling for diagnosis confirmation
**PHASE 2: ION ROBOTIC BRONCHOSCOPY**

EBUS scope removed. Ion robotic bronchoscope inserted through ETT.

**Airway survey:**
- Trachea: Patent, no masses
- Carina: Sharp, mobile
- Right bronchial tree: All segments patent, no endobronchial lesions
- Left bronchial tree: Patent

**Ion Navigation Setup:**

CT chest with contrast from [REDACTED] uploaded to Ion planning station.

Target: RUL posterior segment nodule (2.4cm, spiculated margins, ground-glass and solid components)

3D pathway created: Trachea → RMS → RUL → posterior segment → subsegmental branches

**Registration Process:**
- Method: Automatic registration selected
- Landmarks id[REDACTED] and matched:
  * Carina
  * Right upper lobe carina
  * RUL segmental bifurcations (anterior/apical/posterior)
  * Subsegmental anatomy posterior segment
- Registration quality metrics:
  * Mean fiducial error: 1.0mm (excellent)
  * Global alignment: Green (acceptable)
  * Confidence score: 98%
- Time to complete registration: 9 minutes
- **No registration drift detected during procedure**

**Navigation to Target:**

Ion catheter advanced along planned pathway under real-time navigational guidance.

Progress checkpoints:
- At RMS: On track
- At RUL takeoff: Minor deviation, system autocorrected
- At posterior segment: On track
- At subsegmental branch: Tool-to-target distance 0.5cm (excellent)

**Radial EBUS Confirmation:**

20MHz radial probe inserted through Ion extended working channel.

Initial scan:
- Pattern: Concentric (ideal - lesion centered around probe)
- Lesion size: 22mm greatest dimension
- Echo characteristics: Mixed echogenicity (correlates with part-solid CT appearance)
- Borders: Irregular (matches spiculated margins on CT)
- Internal features: Heterogeneous
- Vessel assessment: No large vessels in immediate sampling path

**CBCT/Image Fusion:**

Cone-beam CT acquired for trajectory confirmation.

NaviLink 3D fusion performed:
- Intra-procedural CBCT fused with pre-procedure planning CT
- Overlay displayed on screen
- Catheter position verified: Tip within lesion volume, 2mm from geometric center
- Sampling trajectory confirmed optimal

**Sampling Protocol:**

**Conventional Biopsies:**
- Transbronchial forceps biopsies: 7 specimens obtained through Ion catheter
  - Adequate tissue fragments seen on each pass
  - Placed in formalin for histopathology
- Cytology brushings: 4 passes
  - Placed in CytoLyt solution
- Bronchial washing: Sent for cytology

**ROSE Checkpoint (Dr. Kim):**
"Adequate cellularity. Atypical glandular epithelial cells. Favor adenocarcinoma, morphologically similar to 4R lymph node. Recommend obtaining larger tissue sample for molecular testing - cryobiopsy suggested."

**Cryobiopsy Procedure:**

Given ROSE findings and need for comprehensive molecular testing, cryobiopsy performed for larger tissue cores.

Preparation:
- Arndt endobronchial blocker (7Fr) placed in RUL ostium under direct visualization
- Balloon test inflation with 5cc air confirmed adequate seal
- Balloon deflated

Cryobiopsy technique:
- 1.9mm cryoprobe advanced through Ion catheter to target
- Position confirmed (within lesion per most recent REBUS)
- Freeze time: 4 seconds
- Probe and bronchoscope withdrawn en bloc
- Blocker immediately inflated (5cc) for prophylactic tamponade
- Sample gently thawed in saline
- Placed in formalin
- Gross inspection: Excellent tissue core, ~8mm length

**Repeat cryobiopsy:**
- Second sample obtained using same technique
- Blocker inflated between samples x 45 seconds

**Hemostasis Management:**

After cryobiopsies, airways re-inspected:
- Mild oozing from biopsy site in RUL posterior segment
- Managed with:
  * Wedging bronchoscope in segment
  * Iced saline lavage 20cc
  * Gentle suctioning
  * Blocker re-inflated x 60 seconds
  * Complete hemostasis achieved

**Final airway inspection:**
- No active bleeding
- Airways cleared of blood and secretions
- Adequate ventilation confirmed
**PROCEDURE COMPLETION:**

Total procedure time: 82 minutes
- EBUS phase: 31 minutes
- Ion phase: 51 minutes

Bronchoscope removed. Patient emerged from anesthesia smoothly. Extubated in OR without difficulty. SpO2 97% on 2L NC. Hemodynamically stable. [REDACTED] PACU.

**Estimated Blood Loss:** 20-25mL

**SPECIMENS SUBMITTED:**

**From EBUS:**
1. Station 4R TBNA x 5 passes (cell block + cytology slides)
2. Station 10R TBNA x 3 passes (cell block + cytology slides)

**From Ion Robotic Bronchoscopy:**
3. RUL nodule forceps biopsies x 7 (formalin, surgical pathology)
4. RUL nodule cryobiopsies x 2 (formalin, surgical pathology)
   **- REQUEST COMPREHENSIVE MOLECULAR TESTING:**
   - EGFR mutation analysis
   - ALK rearrangement (IHC/FISH)
   - ROS1 rearrangement
   - BRAF V600E
   - PD-L1 IHC (22C3)
   - Broader NGS panel if tissue sufficient (KRAS, MET, RET, HER2, etc.)
5. RUL nodule brushings x 4 (cytology)
6. RUL nodule washing (cytology)

**Complications:** None

**POST-PROCEDURE ORDERS:**
1. Recovery room monitoring per protocol
2. NPO x 1 hour then advance diet as tolerated
3. Chest X-ray (PA/Lateral) at 2 hours post-procedure - STAT
4. If pneumothorax present:
   - <10% and asymptomatic: Observe, repeat CXR in 4-6 hours
   - >10% or symptomatic: Contact IP attending, consider chest tube
5. Discharge home same day if:
   - No significant pneumothorax
   - Stable vital signs
   - SpO2 >92% on RA or baseline O2
   - No respiratory distress
6. Return precautions reviewed with patient

**PRELIMINARY FINDINGS:**

**Based on ROSE:**
- Primary: RUL adenocarcinoma (probable)
- Nodal status: N2 disease (station 4R positive), N1 negative (station 10R negative)
- Preliminary stage: IIIA (T1cN2M0) - pending final pathology

**CLINICAL ASSESSMENT:**

52-year-old never-smoker female with stage IIIA adenocarcinoma of lung. N2 involvement makes this a more advanced case than initially suspected. Not straightforward surgical candidate - will likely require neoadjuvant therapy.

Favorable features:
- Never-smoker (higher likelihood of targetable mutations)
- Single N2 station involved
- Young age, good performance status

**PLAN:**

1. **Staging completion:**
   - Brain MRI with contrast (screen for brain metastases)
   - Review PET/CT coverage (confirm no distant metastases)
   - If PET not recent or incomplete coverage: consider repeat PET/CT

2. **Pathology/Molecular:**
   - Await final pathology confirmation (2-3 days)
   - Await comprehensive molecular testing (7-14 days)
   - If EGFR/ALK positive: Consider targeted therapy in neoadjuvant setting

3. **Multidisciplinary Care:**
   - Present at thoracic tumor board (next meeting [REDACTED])
   - Medical oncology consultation
   - Thoracic surgery consultation
   - Radiation oncology consultation
   - Treatment approach likely:
     * Neoadjuvant chemotherapy ± immunotherapy
     * Restaging
     * Surgery if good response and downstaging
     * Adjuvant therapy based on pathologic staging

4. **Follow-up:**
   - IP clinic appointment 1 week ([REDACTED])
   - Review final pathology and molecular testing
   - Coordinate multidisciplinary care

5. **Patient Education:**
   - Preliminary findings discussed with patient in recovery
   - Explained likely stage and treatment paradigm
   - Emphasized need for molecular testing results
   - Patient expressed understanding and appropriate questions

**POST-PROCEDURE UPDATE (2 hours):**

Chest X-ray reviewed: No pneumothorax. Small linear atelectasis RML, expected post-procedure. No other acute findings.

Patient [REDACTED]. SpO2 98% RA. No chest pain or dyspnea. Tolerating PO. Discharge home with return precautions.

**ATTENDING ATTESTATION:**

I, Dr. Daniel Martinez, was present and personally performed all critical elements of this procedure including the EBUS-TBNA and Ion robotic navigation. I supervised Dr. Sarah Patel (fellow) throughout. I reviewed all ROSE results in real-time with cytopathology. I made all clinical decisions including the decision to proceed with cryobiopsy for molecular testing. I reviewed the post-procedure chest X-ray.

Total face-to-face time: 82 minutes procedure + 15 minutes pre-procedure consent/setup + 12 minutes post-procedure discussion with patient = 109 minutes

Electronically signed: Daniel Martinez, MD, FCCP
Date/Time: [REDACTED] 15:47
**BRONCHOSCOPY PROCEDURE REPORT**

Davis Medical Center | Department of Pulmonary & Critical Care

**PATIENT:** Thompson, Robert J.
**MRN:** 5927483
**DOB:** [REDACTED]
**AGE:** 61 years
**DATE OF PROCEDURE:** [REDACTED]

**CLINICAL TEAM:**
- **Attending Physician:** Victoria Chang, MD
- **Fellow Physician:** Derek Miller, MD
- **Anesthesiologist:** Patricia Anderson, MD
- **Circulating RN:** Thomas Lee, RN
- **Monitoring RN:** Rachel Green, RN
- **Respiratory Therapist:** Michael Santos, RT

**PROCEDURE(S) PERFORMED:**
1. Endobronchial Ultrasound with Transbronchial Needle Aspiration (EBUS-TBNA)
2. Electromagnetic Navigation Bronchoscopy (SuperDimension)
3. Radial Endobronchial Ultrasound (rEBUS)
4. Transbronchial Lung Biopsy (TBBx)
5. Bronchial Brushings
6. Bronchoalveolar Lavage (BAL)

**CPT CODES:** 31652, 31653, 31627, 31654, 31628, 31623, 31624

**INDICATION FOR PROCEDURE:**

61-year-old male, former smoker (quit 8 years ago, 45 pack-year history), presents with:

Clinical findings:
- Left lower lobe mass 3.6 cm on CT chest
- FDG-PET: Primary lesion SUV max 10.4
- Mediastinal lymphadenopathy:
  - Station 5 (AP window): 2.3 cm, SUV 7.2
  - Station 7 (subcarinal): 2.1 cm, SUV 6.8
  - Station 10L (left hilar): 1.8 cm, SUV 5.9
- Constitutional symptoms: 15 lb weight loss over 3 months, night sweats
- Performance status: ECOG 1

Diagnostic needs:
- Tissue diagnosis of primary lesion
- Mediastinal nodal staging for treatment planning
- Molecular/biomarker analysis for targeted therapy consideration

**INFORMED CONSENT:**

Comprehensive discussion held with patient and wife (present in pre-op area). Topics covered:
- Rationale for combined EBUS + peripheral sampling approach
- Detailed review of procedural steps
- Risks and benefits:
  - Pneumothorax risk 1-3%
  - Bleeding risk 1-5%
  - Infection risk <1%
  - Mediastinal complications (vascular injury, pericardial puncture) <0.1%
  - False negative results requiring repeat biopsy
  - Anesthesia-related risks
- Alternatives: CT-guided biopsy, surgical biopsy, observation
- Patient and wife asked appropriate questions
- All questions answered to satisfaction
- Written consent obtained

**PRE-PROCEDURE ASSESSMENT:**
- ASA Physical Status: Class III
- Allergies: NKDA
- Current medications: Lisinopril, metformin, atorvastatin
- NPO status: Confirmed 8 hours solid food, 2 hours clear liquids
- Anticoagulation: Aspirin 81mg daily held x 7 days per protocol
- Baseline vital signs: BP 138/82, HR 76, RR 16, SpO2 94% on RA
- Recent labs: WBC 8.2, Hgb 13.1, Plt 245k, INR 1.0, Cr 0.9

**ANESTHESIA:**

Type: General endotracheal anesthesia

Medications administered:
- Induction: Propofol 180 mg IV, Fentanyl 150 mcg IV, Rocuronium 50 mg IV
- Maintenance: Sevoflurane 1.5-2.5%, intermittent propofol boluses
- Endotracheal tube: 8.0 mm inner diameter, depth 22 cm at incisors
- Ventilator settings:
  - Mode: Pressure Control
  - Inspiratory Pressure: 18 cm H2O
  - Respiratory Rate: 12 breaths/min
  - PEEP: 5 cm H2O
  - FiO2: 50% (adjusted to maintain SpO2 >94%)
  - I:E ratio: 1:2

Monitoring:
- Continuous: EKG, pulse oximetry, capnography, blood pressure
- Recorded every 3 minutes by monitoring RN
- No intraoperative complications noted

**TIME-OUT PROCEDURE:**
Performed prior to procedure initiation:
- Patient id[REDACTED] verified (name, DOB, MRN) - verbal + wristband check
- Procedure confirmed: Combined EBUS-TBNA and EMN bronchoscopy
- Site/laterality confirmed: Left lower lobe mass, multiple mediastinal stations
- All imaging reviewed and available in procedure room
- Team introductions performed
- Equipment availability confirmed
- Antibiotic prophylaxis: Not indicated per institutional protocol

**PROCEDURE NARRATIVE:**
**PART I: ENDOBRONCHIAL ULTRASOUND WITH TRANSBRONCHIAL NEEDLE ASPIRATION**

Equipment: Olympus BF-UC190F Linear EBUS Bronchoscope

The EBUS bronchoscope was introduced through the endotracheal tube and advanced into the tracheobronchial tree.

**Initial Airway Survey:**
- Vocal cords: Not visualized (approached via ETT)
- Trachea: Patent, midline, no masses or stenosis
- Carina: Sharp angle, mobile with respiration
- Right main stem: Patent
- Left main stem: Patent, no extrinsic compression

**Systematic Mediastinal Lymph Node Survey:**

All accessible mediastinal and hilar lymph node stations were systematically evaluated with ultrasound. Nodes ≥5mm were measured. Nodes with suspicious features and >5mm were sampled.

**STATION 2R (High right paratracheal):**
- Ultrasound: Not well visualized in this patient

**STATION 2L (High left paratracheal):**
- Ultrasound: 7 mm, appears benign, not sampled

**STATION 4R (Low right paratracheal):**
- Ultrasound size: 13 x 10 mm
- Echogenicity: Hypoechoic
- Shape: Oval
- Margins: Well-defined
- Vascular pattern: Hilar vessels present (reassuring feature)
- Assessment: Likely reactive, below size threshold for sampling in absence of other factors
- **Not sampled**

**STATION 4L (Low left paratracheal):**
- Ultrasound size: 15 x 12 mm
- Echogenicity: Hypoechoic
- Shape: Oval
- Assessment: Borderline size, appears reactive
- **Not sampled** (limited clinical impact given ipsilateral mediastinal nodes will be sampled)

**STATION 5 (Aortopulmonary window):**
- Ultrasound size: 22 x 19 mm (consistent with CT measurement)
- Echogenicity: Markedly hypoechoic, heterogeneous internal echo
- Shape: Round (loss of normal oval shape concerning for malignant infiltration)
- Margins: Irregular, indistinct in areas
- Vascular pattern: Absent hilar vessels
- Doppler: Increased vascularity noted
- **Elastography performed:** Predominantly "hard" pattern (blue on elastography scale), strain ratio 12.3 (highly suspicious for malignancy)

**Sampling of Station 5:**
- EBUS-TBNA needle: 22-gauge
- Number of passes: 5
- Technique: Needle advanced under real-time ultrasound guidance, position within node confirmed, suction applied, multiple to-and-fro movements per pass
- Specimen handling:
  - Passes 1-3: Expressed onto slides (air-dried and alcohol-fixed), remainder to CytoLyt
  - Passes 4-5: Entire specimen to formalin for cell block preparation
- Gross assessment: White tissue cores visible in passes 2, 4, and 5

**Rapid On-Site Evaluation (ROSE) - Station 5:**
Performed by: Dr. Lisa Chen, Cytopathologist

Preliminary findings: "ADEQUATE sample. Highly cellular aspirate. Atypical epithelial cells arranged in clusters and singly. Cells demonstrate nuclear enlargement, hyperchromasia, and prominent nucleoli. Cytomorphologic features consistent with ADENOCARCINOMA. Recommend tissue biopsy of primary lesion for confirmation and molecular testing."

**STATION 7 (Subcarinal):**
- Ultrasound size: 20 x 17 mm
- Echogenicity: Hypoechoic, heterogeneous
- Shape: Round to oval
- Margins: Somewhat irregular
- Assessment: Suspicious features

**Sampling of Station 7:**
- EBUS-TBNA needle: 22-gauge
- Number of passes: 5
- Technique: Same as above
- Specimen handling: Same protocol as Station 5
- Gross assessment: Adequate tissue cores visible

**ROSE - Station 7:**
Preliminary findings: "ADEQUATE sample. Malignant cells present, similar morphology to Station 5. Consistent with ADENOCARCINOMA."

**STATION 10L (Left hilar):**
- Ultrasound size: 17 x 14 mm
- Echogenicity: Hypoechoic
- Shape: Oval
- Margins: Discrete

**Sampling of Station 10L:**
- EBUS-TBNA needle: 22-gauge
- Number of passes: 4
- Specimen handling: Same protocol
- Gross assessment: Adequate material obtained

**ROSE - Station 10L:**
Preliminary findings: "ADEQUATE sample. POSITIVE for malignancy. Adenocarcinoma, consistent with Stations 5 and 7."

**STATION 11L (Interlobar):**
- Ultrasound: 12 mm, appears reactive
- **Not sampled** (diagnostic yield already achieved from other stations)

**EBUS Summary:**
- N3 disease documented (Station 5 - contralateral N3)
- N2 disease documented (Station 7 - ipsilateral N2)
- N1 disease documented (Station 10L - ipsilateral hilar N1)
- Extensive nodal involvement consistent with advanced disease
**PART II: ELECTROMAGNETIC NAVIGATION BRONCHOSCOPY FOR PRIMARY LESION**

After completing EBUS, the EBUS bronchoscope was removed.

A standard therapeutic bronchoscope (Olympus BF-1TH190) was introduced through the ETT for EMN bronchoscopy.

**Standard Bronchoscopy - Airway Survey:**

Detailed inspection of tracheobronchial tree:

*Right lung:*
- Right upper lobe: Anterior, apical, and posterior segments - all patent
- Right middle lobe: Medial and lateral segments - patent
- Right lower lobe: Superior, medial basal, anterior basal, lateral basal, posterior basal segments - all patent
- No endobronchial lesions id[REDACTED]

*Left lung:*
- Left upper lobe: Apical-posterior segment - patent
- Left upper lobe: Anterior segment - patent
- Lingula: Superior and inferior segments - patent
- Left lower lobe: Superior segment - patent
- **Left lower lobe: Basilar segments (medial/anterior/lateral/posterior) - mild narrowing of ostia likely from external compression by mass, but patent**
- No discrete endobronchial tumor visible (mass appears primarily parenchymal)

Secretion management: Minimal thin clear secretions throughout, suctioned clear

**Electromagnetic Navigation Setup:**

System: SuperDimension iLogic Electromagnetic Navigation Platform

**CT Planning:**
- CT chest with IV contrast dated [REDACTED] loaded onto navigation workstation
- 3D reconstruction performed
- Target id[REDACTED]: LLL posterior basal segment mass (3.6 cm, irregular/spiculated margins, approximately 2.8 cm from pleural surface)

**Virtual Pathway Planning:**
Pathway created through the following anatomic route:
- Trachea
- Left main stem bronchus
- Left lower lobe bronchus
- Posterior basal segmental bronchus
- Subsegmental branches (2 levels)

**Registration Phase:**

Registration method: Automatic registration protocol

Process:
1. Electromagnetic field generator positioned under procedure table
2. Locatable guide with position sensors inserted through bronchoscope working channel
3. Locatable guide advanced through airways while system tracks position
4. Automated landmark id[REDACTED] and matching to CT dataset

Registration landmarks confirmed:
- Carina (primary reference point)
- Left main stem bronchus takeoff
- LUL/Lingula/LLL trifurcation
- LLL segmental anatomy (superior, basilar divisions)
- Posterior basal segmental bronchus
- Subsegmental branch points (levels 1 and 2)

Registration quality metrics:
- Number of registration points: 9 confirmed
- System accuracy indicator: 93% (green/acceptable)
- Estimated target error: <6 mm per system calculations
- Visual inspection of overlay: Good concordance between virtual and live bronchoscopic views

Time to complete registration: 12 minutes

**Navigation Phase:**

The extended working channel (EWC) with locatable guide (LG) was assembled and prepared.

The EWC/LG system was advanced through the bronchoscope working channel under electromagnetic navigational guidance.

Real-time position tracking displayed on navigation monitor showing:
- Current position of catheter tip
- Planned pathway
- Distance to target
- 3D anatomic orientation

Navigation progress:
- Trachea to left main stem: On trajectory
- Left main stem to LLL: On trajectory
- LLL to posterior basal segment: On trajectory, minimal deviation
- Posterior basal to subsegmental branches: Required minor repositioning (system indicated 3mm anterior adjustment needed, performed successfully)
- Final positioning: Catheter advanced to deepest safe depth in subsegmental airways

**Final Navigation Metrics:**
- Tool-to-target distance: 0.9 cm (displayed on system)
- Navigation confidence score: High (per system algorithm)
- Time to navigate to target: 8 minutes

**Radial EBUS Confirmation:**

After achieving navigational target, radial EBUS probe (20 MHz, UM-S20-20R) was introduced through the extended working channel to confirm lesion localization.

**Initial rEBUS findings:**
- Pattern: Eccentric (lesion visualized but not centered around probe)
- Lesion characteristics: Hypoechoic mass with irregular, spiculated margins
- Size: Approximately 32 mm in maximum dimension
- Internal echo: Heterogeneous

**Catheter adjustment:**
- Based on eccentric pattern, catheter advanced 4 mm deeper and rotated slightly
- Repeat rEBUS performed

**Optimized rEBUS findings:**
- Pattern: Concentric (lesion now centered around probe - OPTIMAL for sampling)
- Confirmation of same lesion characteristics
- Distance to pleura: Estimated 2.5-3.0 cm (safe sampling distance)
- Vascular assessment: No large vessels immediately adjacent to planned sampling trajectory

**rEBUS photos captured and saved to patient record**

Radial probe removed, extended working channel/locatable guide maintained in position for sampling.

**Tissue Acquisition:**

All sampling performed through the extended working channel with guide sheath in place (maintains position after probe removal).

**Transbronchial Forceps Biopsies:**
- Forceps type: Standard cup forceps
- Number of passes: 8 biopsies obtained
- Technique: Forceps advanced through EWC to target depth (guided by most recent rEBUS position), opened, advanced 1-2cm, closed, withdrawn
- Quality assessment: Adequate tissue fragments visualized on all 8 passes
- Specimen handling: All specimens placed in formalin container for histopathology

**Cytology Brushings:**
- Brush type: Disposable cytology brush
- Number of passes: 4
- Technique: Brush advanced through EWC, extended, rotated, withdrawn
- Specimen handling:
  - Brushes 1-2: Smeared on glass slides (air-dried and alcohol-fixed)
  - Brushes 3-4: Agitated in CytoLyt solution

**Bronchoalveolar Lavage:**
- Location: LLL posterior basal segment (same segment as target lesion)
- Volume instilled: 100 mL sterile 0.9% normal saline (divided into 2 x 50mL aliquots)
- Volume returned: 48 mL
- Fluid appearance: Slightly blood-tinged (expected post-biopsy), moderate turbidity
- Specimens sent for:
  - Cytology
  - Bacterial culture
  - Fungal culture
  - Acid-fast bacilli (AFB) culture and smear

**ROSE - Primary Lesion (Dr. Chen):**

Preliminary assessment of brushing specimens:

"ADEQUATE cellular sample. Malignant epithelial cells id[REDACTED]. Cells demonstrate glandular differentiation with acinar formation. Nuclear features similar to previously sampled lymph nodes. Morphology consistent with ADENOCARCINOMA.

Recommend: Full histopathologic evaluation of tissue biopsies. Request comprehensive molecular testing including EGFR, ALK, ROS1, BRAF, PD-L1, and broader next-generation sequencing panel given never-smoker status and treatment implications."

**Hemostasis Assessment:**

After completing all sampling, airways were re-inspected:
- Mild oozing from biopsy site in LLL posterior basal segment
- Self-limited - no intervention required
- Continued observation for 2 minutes
- Complete cessation of bleeding confirmed
- Airways suctioned clear

**Final Airway Inspection:**
- All airways patent
- No active bleeding
- No mucus plugging
- Adequate ventilation confirmed
**PROCEDURE COMPLETION:**

Total procedure time: 76 minutes
- EBUS phase: 38 minutes
- EMN bronchoscopy phase: 38 minutes

Equipment removed systematically:
- Extended working channel/locatable guide removed from bronchoscope
- Bronchoscope withdrawn from ETT
- Airways suctioned one final time during withdrawal

Patient [REDACTED]:
- Anesthesia discontinued
- Neuromuscular blockade reversed (neostigmine/glycopyrrolate)
- Spontaneous respirations resumed
- Patient followed commands
- Extubation performed smoothly
- Post-extubation: SpO2 97% on 2L nasal cannula

Patient [REDACTED] PACU in stable condition:
- Alert and oriented
- No respiratory distress
- Vital signs stable
- Instructions given to PACU RN

**ESTIMATED BLOOD LOSS:** 15-20 mL

**INTRAOPERATIVE COMPLICATIONS:** None
**SPECIMENS SUBMITTED:**

**From EBUS-TBNA:**
1. **Station 5 (AP window) TBNA:**
   - 5 passes total
   - Cytology slides (passes 1-3)
   - Cell block in formalin (passes 4-5)

2. **Station 7 (Subcarinal) TBNA:**
   - 5 passes total
   - Cytology slides (passes 1-3)
   - Cell block in formalin (passes 4-5)

3. **Station 10L (Left hilar) TBNA:**
   - 4 passes total
   - Cytology slides (passes 1-2)
   - Cell block in formalin (passes 3-4)

**From EMN Bronchoscopy:**
4. **LLL mass - Transbronchial biopsies:**
   - 8 specimens in formalin for histopathology
   - **CRITICAL: Request comprehensive molecular testing:**
     - EGFR mutation analysis (exons 18-21)
     - ALK rearrangement (IHC and/or FISH)
     - ROS1 rearrangement (IHC and/or FISH)
     - BRAF V600E mutation
     - MET amplification/exon 14 skipping
     - PD-L1 immunohistochemistry (22C3 antibody)
     - Broad next-generation sequencing panel if tissue adequate
     - Consider TMB (tumor mutational burden) if NGS performed

5. **LLL mass - Cytology brushings:**
   - 4 brush specimens
   - Slides (2 specimens)
   - CytoLyt solution (2 specimens)

6. **LLL BAL:**
   - 48 mL fluid
   - Split for:
     - Cytology
     - Bacterial culture (aerobic/anaerobic)
     - Fungal culture
     - AFB smear and culture
**POST-PROCEDURE ORDERS:**

**Immediate Recovery:**
1. PACU monitoring per protocol
2. NPO x 1 hour, then advance to clear liquids as tolerated
3. Vital signs: Every 15 minutes x 1 hour, then every 30 minutes x 2 hours
4. Continuous pulse oximetry x 3 hours minimum
5. Supplemental oxygen: Titrate to maintain SpO2 ≥92% or patient's baseline

**Imaging:**
6. **Chest X-ray (PA and lateral views) at 2 hours post-procedure - STAT**
   - Primary indication: Rule out pneumothorax
   - Secondary assessment: Rule out new infiltrate, significant atelectasis

**Pneumothorax Protocol:**
7. If pneumothorax id[REDACTED] on CXR:
   - Small (<10%) and asymptomatic:
     - Continue observation
     - Repeat CXR in 4 hours
     - Maintain continuous pulse oximetry
   - Moderate (10-20%) or symptomatic:
     - STAT page IP attending (Dr. Chang)
     - Consider oxygen supplementation
     - Prepare for possible chest tube placement
   - Large (>20%):
     - STAT page IP attending
     - Prepare for chest tube placement

**Discharge Criteria** (must meet ALL):
8. Chest X-ray without clinically significant pneumothorax
9. Vital signs stable x 2 hours
10. SpO2 ≥92% on room air or baseline oxygen requirement
11. No significant respiratory distress
12. Tolerating oral intake
13. Patient ambulating without difficulty
14. Adequate pain control
15. Responsible adult available for transportation and overnight supervision

**Discharge Instructions:**
16. Return precautions to be reviewed with patient:
    - Worsening shortness of breath
    - Chest pain
    - Fever >100.4°F (38°C)
    - Hemoptysis (blood-streaked sputum is normal for 24h, frank blood is not)
    - Any concerning symptoms

**Medications:**
17. Resume home medications
18. No additional prescriptions needed
19. Aspirin 81mg may be resumed tomorrow

**Activity:**
20. Rest today, light activity tomorrow
21. No driving for 24 hours (post-anesthesia)
22. May return to work in 1-2 days as tolerated
**FINDINGS SUMMARY:**

**Based on Rapid On-Site Evaluation (ROSE):**

**Primary Tumor:**
- Left lower lobe mass: ADENOCARCINOMA confirmed

**Lymph Node Staging:**
- Station 5 (Aortopulmonary window - contralateral): POSITIVE for malignancy (N3 disease)
- Station 7 (Subcarinal - ipsilateral): POSITIVE for malignancy (N2 disease)
- Station 10L (Left hilar - ipsilateral): POSITIVE for malignancy (N1 disease)

**Preliminary Staging:**
- Primary tumor (T): T2b (3.6 cm)
- Regional lymph nodes (N): N3 (contralateral mediastinal node involvement)
- Distant metastasis (M): M0 (no distant metastases id[REDACTED] on PET/CT)
- **Overall Stage: IIIB (T2bN3M0)**

This represents locally advanced disease with contralateral mediastinal lymph node involvement.
**CLINICAL ASSESSMENT & DISCUSSION:**

**Diagnosis:** Stage IIIB Adenocarcinoma of the Left Lower Lobe

**Significance:**
- This is locally advanced lung cancer with extensive nodal involvement
- N3 disease (contralateral mediastinal node) makes this unresectable by surgical standards
- Patient is NOT a surgical candidate given extent of nodal disease
- Will require systemic therapy +/- radiation

**Prognostic Factors - FAVORABLE:**
- Former smoker (quit 8 years ago) - intermediate prognosis
- Good performance status (ECOG 1)
- Age 61 - relatively young
- Histology: Adenocarcinoma (better prognosis than squamous, more treatment options)

**Prognostic Factors - UNFAVORABLE:**
- Stage IIIB with N3 disease
- Large primary tumor (3.6 cm)
- Multilevel nodal involvement (N1, N2, N3)

**Treatment Implications:**
- Primary treatment: Concurrent chemoimmunotherapy followed by consolidation immunotherapy (PACIFIC trial paradigm)
- Alternative: Sequential chemotherapy → radiation, or clinical trial
- Role of radiation: Definitive radiation therapy to primary + involved nodal stations
- Surgical resection: Not indicated given N3 disease
- Molecular testing results will be CRITICAL:
  - If EGFR/ALK/ROS1 positive: Consider targeted therapy incorporation
  - PD-L1 status: Guides immunotherapy selection
  - Other actionable mutations: May have clinical trial options

**Awaiting:**
- Final histopathology confirmation (2-3 business days)
- Comprehensive molecular testing (7-14 days, expedite if possible)
- Formal staging completion (see below)
**PLAN & FOLLOW-UP:**

**1. Staging Completion:**
- **Brain MRI with contrast** - Order STAT (high priority in adenocarcinoma, screen for brain metastases which would upstage to Stage IV)
- Review PET/CT from [REDACTED]:
  - Confirm adequate coverage of chest/abdomen/pelvis
  - No suspicious distant lesions
  - If any concerning findings, consider dedicated imaging
- Consider bone scan if bone pain or elevated alkaline phosphatase (though PET usually adequate)

**2. Pathology & Molecular Testing:**
- Monitor for final pathology report (should be available 04/18 or 04/19)
- **EXPEDITE molecular testing** - contact pathology to prioritize
  - EGFR, ALK, ROS1 (highest priority)
  - PD-L1 (critical for immunotherapy decisions)
  - Broader NGS panel
- Call patient with preliminary results once available

**3. Multidisciplinary Tumor Board:**
- **Present case at Thoracic Oncology Tumor Board** - Next meeting [REDACTED]
- Ensure molecular testing results available before tumor board if possible
- Invitees: Medical oncology, radiation oncology, thoracic surgery (for completeness), interventional pulmonology, radiology, pathology

**4. Consultations:**
- **Medical Oncology** - Referral placed to Dr. Jennifer Martinez
  - Urgent appointment requested (within 1 week)
  - Discuss systemic therapy options
  - Clinical trial consideration
- **Radiation Oncology** - Referral placed to Dr. Robert Kim
  - For definitive radiation planning
  - Coordination with medical oncology for concurrent vs sequential approach

**5. Patient Follow-Up:**
- **Interventional Pulmonology clinic appointment: [REDACTED] at 2:00 PM**
  - Review final pathology
  - Review molecular testing (if available)
  - Discuss staging results
  - Coordinate care with oncology
  - Answer questions, provide support
- **Patient phone call in 2-3 days:**
  - Check on post-procedure recovery
  - Provide preliminary results
  - Ensure patient connected with oncology
  - Address immediate concerns

**6. Patient Education & Support:**
- Provide written materials about:
  - Lung cancer diagnosis
  - Treatment options for Stage III disease
  - What to expect with chemotherapy/immunotherapy/radiation
  - Support resources
- Smoking cessation counseling (though patient quit 8 years ago, reinforce importance)
- Referral to:
  - Social work for psychosocial support
  - Nutrition services
  - Palliative care for symptom management (NOT hospice - for quality of life optimization)

**7. Symptomatic Management:**
- Monitor weight, appetite
- Address constitutional symptoms (night sweats, fatigue)
- PRN anti-emetics if needed
- Pain management as needed (none currently)
**POST-PROCEDURE UPDATE (2.5 hours post-procedure):**

**Chest X-Ray Results** (Reviewed by Dr. Victoria Chang):

PA and Lateral Chest X-Ray performed at 1630 (2 hours post-procedure):

**Findings:**
- Lungs: No pneumothorax id[REDACTED] bilaterally
- Left lower lobe: Mass visible (corresponds to known LLL lesion), unchanged from pre-procedure imaging
- Pleural spaces: No effusion
- Mediastinum: Widened (known mediastinal adenopathy), stable
- Heart size: Normal
- Bones: No acute abnormalities
- Lines/tubes: None

**Impression:**
- No post-procedure pneumothorax
- Known LLL mass unchanged
- No other acute findings

**Patient Status:**
- Vital signs: BP 132/78, HR 72, RR 14, SpO2 97% on room air, Temp 36.8°C
- Patient alert, comfortable, no complaints
- Tolerating oral intake (had crackers and juice)
- Ambulated to bathroom without difficulty
- No respiratory distress, no chest pain
- Voice slightly hoarse (expected from bronchoscopy)

**Discharge Plan:**
- Meets all discharge criteria
- Patient lives 15 minutes from hospital with wife
- Return precautions reviewed extensively with patient and wife
- Written instructions provided
- Emergency contact numbers provided
- Follow-up appointments scheduled and confirmed
- Patient verbalizes understanding of all instructions

**Discharged to home at 1645 in stable condition.**
**BILLING INFORMATION:**

**CPT Codes:**
- 31652 - Endobronchial ultrasound (EBUS) during bronchoscopic diagnostic or therapeutic intervention(s) (List separately in addition to code for primary procedure[s])
- 31653 - Bronchoscopy with transbronchial needle aspiration biopsy, first target (concurrent with 31652)
- 31654 - Bronchoscopy with radial endobronchial ultrasound (rEBUS)
- 31627 - Bronchoscopy with computer-assisted, image-guided navigation (electromagnetic navigation)
- 31628 - Bronchoscopy with transbronchial lung biopsy
- 31623 - Bronchoscopy with brushing or protected brushings
- 31624 - Bronchoscopy with bronchoalveolar lavage

**Modifiers:** None required (all procedures performed at separate sites)

**ICD-10 Codes:**
- C34.32 - Malignant neoplasm of lower lobe, left bronchus or lung (PRELIMINARY - confirm with final pathology)
- Z12.2 - Encounter for screening for malignant neoplasm of respiratory organs (if applicable)
- F17.210 - Nicotine dependence, cigarettes, uncomplicated (history of smoking)
**ATTENDING PHYSICIAN STATEMENT:**

I, Dr. Victoria Chang, MD, FCCP, Board Certified in Pulmonary Medicine and Interventional Pulmonary, was personally present throughout the entirety of this procedure. I personally performed all critical components including:

- EBUS-TBNA of all lymph node stations
- Electromagnetic navigation setup and registration
- Navigation to target lesion
- Interpretation of radial EBUS findings
- All tissue sampling procedures
- Review of all ROSE results with cytopathology
- Assessment of hemostasis
- All clinical decision-making throughout the procedure

I supervised Dr. Derek Miller (Interventional Pulmonology Fellow) in assisting with portions of the procedure under my direct observation.

Total physician time: 76 minutes intraoperative + 22 minutes pre-procedure evaluation and consent + 15 minutes post-procedure evaluation and documentation = **113 minutes total physician time**

I have reviewed this operative report and attest to its accuracy and completeness.

**Electronically signed:**
**Victoria Chang, MD, FCCP**
**Attending Physician, Interventional Pulmonology**
**Date/Time: [REDACTED] at 17:15**
**END OF REPORT**"""

entities_10 = [
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "RLL", 1)},
    {"label": "OBS_LESION", "span": get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "2.9cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Right hilar", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "station 10R", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "2.2cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Left paratracheal", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "station 4L", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "1.7cm", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "TBNA", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Ion robotic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "RLL", 2)},
    {"label": "OBS_LESION", "span": get_span(text_10, "mass", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "biopsy", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Cryobiopsy", 1)},
    {"label": "MEDICATION", "span": get_span(text_10, "Propofol", 1)},
    {"label": "MEDICATION", "span": get_span(text_10, "Sevo", 1)},
    {"label": "MEDICATION", "span": get_span(text_10, "Fentanyl", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 2R", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 2L", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 4R", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "9mm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 4L", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "16 x 13 mm", 1)},
    {"label": "OBS_FINDING", "span": get_span(text_10, "Hypoechoic", 1)},
    {"label": "DEV_NEEDLE", "span": get_span(text_10, "22G needle", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_10, "4 passes", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_10, "Negative for malignancy", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 7", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "12mm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 10R", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "21 x 18 mm", 1)},
    {"label": "DEV_NEEDLE", "span": get_span(text_10, "22G needle", 2)},
    {"label": "MEAS_COUNT", "span": get_span(text_10, "5 passes", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_10, "POSITIVE for malignancy", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_10, "adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 11R", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Stations 10L, 11L", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Ion robotic bronchoscopy", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "RLL superior segment", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "Carina", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "right main carina", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "RLL carina", 1)},
    {"label": "DEV_CATHETER", "span": get_span(text_10, "Ion catheter", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "superior segmental bronchus", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Radial EBUS", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "27mm", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Forceps biopsies", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_10, "x 6", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Brushings", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_10, "x 3", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Washing", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_10, "Arndt blocker", 1)},
    {"label": "DEV_CATHETER_SIZE", "span": get_span(text_10, "7Fr", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "RLL ostium", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_10, "Cryoprobe", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "1.9mm", 1)},
    {"label": "MEAS_TIME", "span": get_span(text_10, "4 seconds", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "LLL", 2)},
    {"label": "OBS_LESION", "span": get_span(text_10, "mass", 3)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "5.1cm", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Radial EBUS", 3)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Transbronchial biopsies", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Endobronchial biopsies", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 2R", 2)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 4R", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "24mm", 1)},
    {"label": "DEV_NEEDLE", "span": get_span(text_10, "22G needle", 3)},
    {"label": "MEAS_COUNT", "span": get_span(text_10, "x 5 passes", 1)},
    {"label": "OBS_ROSE", "span": get_span(text_10, "Positive - squamous cell carcinoma", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 4L", 4)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "19mm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 7", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "28mm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 10L", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "22mm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 11L", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "18mm", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "LLL orifice", 1)},
    {"label": "OBS_LESION", "span": get_span(text_10, "endobronchial tumor", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_10, "forceps", 3)},
    {"label": "MEDICATION", "span": get_span(text_10, "Epinephrine", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "SuperDimension", 2)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "LLL superior segment", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "RUL", 4)},
    {"label": "OBS_LESION", "span": get_span(text_10, "nodule", 5)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "1.2cm", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "2.4cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Right paratracheal", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "1.9cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 2R", 3)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 2L", 2)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 4R", 4)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "18 x 14 mm", 1)},
    {"label": "DEV_NEEDLE", "span": get_span(text_10, "22-gauge", 1)},
    {"label": "MEAS_COUNT", "span": get_span(text_10, "5 passes", 4)},
    {"label": "OBS_ROSE", "span": get_span(text_10, "Favor adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 4L", 6)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 7", 4)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 10R", 4)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "Trachea", 2)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "Carina", 3)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "Right bronchial tree", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "RUL posterior segment", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "RMS", 2)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "RUL takeoff", 1)},
    {"label": "OBS_FINDING", "span": get_span(text_10, "Concentric", 3)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "22mm", 2)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Transbronchial forceps biopsies", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Cytology brushings", 2)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Bronchial washing", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_10, "Arndt endobronchial blocker", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_10, "cryoprobe", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "Left lower lobe", 2)},
    {"label": "OBS_LESION", "span": get_span(text_10, "mass", 6)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "3.6 cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 5", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "AP window", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "2.3 cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 7", 5)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "subcarinal", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "2.1 cm", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 10L", 3)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "left hilar", 1)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "1.8 cm", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Endobronchial Ultrasound", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Transbronchial Needle Aspiration", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Electromagnetic Navigation Bronchoscopy", 1)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "Radial Endobronchial Ultrasound", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Transbronchial Lung Biopsy", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Bronchial Brushings", 1)},
    {"label": "PROC_ACTION", "span": get_span(text_10, "Bronchoalveolar Lavage", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "Right main stem", 1)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "Left main stem", 1)},
    {"label": "ANAT_LN_STATION", "span": get_span(text_10, "Station 5", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "22 x 19 mm", 1)},
    {"label": "DEV_NEEDLE", "span": get_span(text_10, "22-gauge", 4)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "Right upper lobe", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "Left upper lobe", 1)},
    {"label": "ANAT_LUNG_LOC", "span": get_span(text_10, "Left lower lobe", 4)},
    {"label": "ANAT_AIRWAY", "span": get_span(text_10, "Posterior basal segmental bronchus", 1)},
    {"label": "DEV_CATHETER", "span": get_span(text_10, "locatable guide", 1)},
    {"label": "DEV_CATHETER", "span": get_span(text_10, "extended working channel", 2)},
    {"label": "PROC_METHOD", "span": get_span(text_10, "radial EBUS", 2)},
    {"label": "MEAS_SIZE", "span": get_span(text_10, "32 mm", 1)},
    {"label": "DEV_INSTRUMENT", "span": get_span(text_10, "cytology brush", 1)},
    {"label": "MEAS_VOL", "span": get_span(text_10, "100 mL", 1)},
    {"label": "MEAS_VOL", "span": get_span(text_10, "48 mL", 1)},
]
BATCH_DATA.append({"id": "4829301", "text": text_10, "entities": entities_10})

# 5. Execution Logic
# -------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        # This script stores spans as {"label": ..., "span": (start, end)}.
        # Normalize to the shape expected by add_case(): {"label","start","end","text"}.
        normalized_entities = []
        for ent in case.get("entities", []) or []:
            if not isinstance(ent, dict):
                continue
            label = ent.get("label")
            span = ent.get("span")
            if (
                isinstance(label, str)
                and isinstance(span, (tuple, list))
                and len(span) == 2
                and isinstance(span[0], int)
                and isinstance(span[1], int)
            ):
                start, end = int(span[0]), int(span[1])
                text = case["text"][start:end]
                normalized_entities.append(
                    {"label": label, "start": start, "end": end, "text": text}
                )
            elif "start" in ent and "end" in ent:
                normalized_entities.append(ent)

        add_case(case["id"], case["text"], normalized_entities, REPO_ROOT)