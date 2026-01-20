import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}. Check your directory structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 5029384_syn_1
# ==========================================
t1 = """Indication: RLL nodule + Adenopathy.
Procedures: EBUS-TBNA + Ion Nav + Cryobiopsy.
EBUS: 10R positive (Adeno). 4L neg.
Ion: Navigated to RLL mass. REBUS/CBCT confirmed.
Sampling: Forceps x6, Cryo x2.
ROSE: Adenocarcinoma (Primary & N1).
Plan: Staging workup."""

e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion Nav", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Cryobiopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "10R", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "positive", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Adeno", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "neg", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "REBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CBCT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Cryo", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Adenocarcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "N1", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 5029384_syn_2
# ==========================================
t2 = """PROCEDURE: Combined endobronchial ultrasound and robotic-assisted bronchoscopy. EBUS-TBNA was performed at stations 4L and 10R; station 10R was positive for malignancy. The Ion robotic platform was then utilized to navigate to the RLL superior segment mass. Following radial EBUS and Cone-Beam CT confirmation, both conventional forceps biopsies and transbronchial cryobiopsies were obtained to ensure adequate tissue for molecular profiling."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "stations", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "station 10R", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "positive", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Ion robotic platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RLL superior segment", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Cone-Beam CT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "transbronchial", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "cryobiopsies", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 5029384_syn_3
# ==========================================
t3 = """Billing: 31653 (EBUS 3+ stations - note says 4L, 10R sampled, plus others surveyed/considered?), 31627 (Nav), 31654 (REBUS), 31628 (TBBx), 31623 (Brush).
Correction: Note lists sampling of 4L and 10R only (2 stations). Should be 31652. Cryobiopsy (31628 covers TBBx method broadly or 31645 if distinct)."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "10R", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBBx", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Brush", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "10R", 2)},
    {"label": "PROC_ACTION", **get_span(t3, "Cryobiopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBBx", 2)}
]
BATCH_DATA.append({"id": "5029384_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 5029384_syn_4
# ==========================================
t4 = """Combined EBUS/Robotic Bronch
Patient: [REDACTED]
Indication: RLL mass + nodes
Steps:
1. EBUS: Sampled 4L (neg) and 10R (pos).
2. Ion Robot: Navigated to RLL mass.
3. Confirmed with REBUS + CBCT.
4. Biopsies: Forceps and Cryo.
5. Bleeding controlled with blocker.
Result: Stage IIIA Adeno (T1cN1)."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Robotic Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodes", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "4L", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "neg", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "10R", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "pos", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Ion Robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(t4, "mass", 2)},
    {"label": "PROC_METHOD", **get_span(t4, "REBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Cryo", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "blocker", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Adeno", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "N1", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 5029384_syn_5
# ==========================================
t5 = """Michelle needs staging for her RLL mass. Did EBUS first sampled 4L and 10R. 10R was positive for adeno. Then switched to the Ion robot found the RLL mass with rebus and cone beam. Took forceps biopsies and then two cryo biopsies for molecular. Had some bleeding used a blocker and iced saline. Patient stable."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "10R", 2)},
    {"label": "OBS_ROSE", **get_span(t5, "positive", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "adeno", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "Ion robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 2)},
    {"label": "PROC_METHOD", **get_span(t5, "rebus", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "cone beam", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "two", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "cryo", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 2)},
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "blocker", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 5029384_syn_6
# ==========================================
t6 = """EBUS with TBNA, Ion robotic bronchoscopy, Radial EBUS, Cryobiopsy of RLL mass. Patient is a 71-year-old female. EBUS Phase: Sampled stations 4L and 10R. ROSE positive for malignancy at 10R. Ion Robotic Bronchoscopy Phase: Navigated to RLL superior segment mass. Radial EBUS and CBCT confirmed position. Forceps biopsies and cryobiopsies obtained. Mild bleeding managed with blocker. Final staging likely IIIA."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Ion robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Cryobiopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "stations", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "10R", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "positive", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "10R", 2)},
    {"label": "PROC_METHOD", **get_span(t6, "Ion Robotic Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL superior segment", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 2)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(t6, "CBCT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "cryobiopsies", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "blocker", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 5029384_syn_7
# ==========================================
t7 = """[Indication]
RLL mass, mediastinal adenopathy.
[Anesthesia]
General, ETT.
[Description]
EBUS-TBNA (4L, 10R). Ion Nav to RLL. REBUS/CBCT confirmation. Forceps and Cryobiopsy of mass. 10R and Mass positive for Adenocarcinoma.
[Plan]
Molecular testing. Oncology consult."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "mediastinal adenopathy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "10R", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Ion Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 2)},
    {"label": "PROC_METHOD", **get_span(t7, "REBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "CBCT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Cryobiopsy", 1)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "10R", 2)},
    {"label": "OBS_LESION", **get_span(t7, "Mass", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "positive", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 5029384_syn_8
# ==========================================
t8 = """We performed a comprehensive staging procedure for [REDACTED]. First, we used EBUS to sample lymph nodes; the right hilar node tested positive for cancer. Then, using the robotic bronchoscope, we biopsied the main tumor in the right lower lobe using both standard forceps and a freezing probe to get a large sample for genetic testing. She is diagnosed with Stage IIIA adenocarcinoma and will need further treatment planning."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "lymph nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "right hilar node", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "positive", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "robotic bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsied", 1)},
    {"label": "OBS_LESION", **get_span(t8, "main tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right lower lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "freezing probe", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 5029384_syn_9
# ==========================================
t9 = """Procedure: Multimodal staging bronchoscopy.
Components: EBUS-TBNA of hilar/mediastinal nodes. Robotic navigation with cryosampling of pulmonary parenchymal lesion.
Findings: N1 nodal involvement and primary adenocarcinoma confirmed.
Intervention: Hemostasis secured via bronchial blocker."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "staging bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "hilar", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "mediastinal nodes", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Robotic navigation", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "cryosampling", 1)},
    {"label": "OBS_LESION", **get_span(t9, "pulmonary parenchymal lesion", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "N1", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "Hemostasis secured", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "bronchial blocker", 1)}
]
BATCH_DATA.append({"id": "5029384_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 5029384
# ==========================================
t10 = """PROCEDURE NOTE:
68 y.o. male with 60 pack-year smoking history presents with LLL mass on staging CT. PET shows SUV 8.9. Mediastinal nodes negative. Patient consented for diagnostic bronch and fiducial placement for possible SBRT.

Intubated by anesthesia without difficulty. ETT 8.0 at 23 cm.

VENT: VC, TV 500, RR 14, PEEP 5, FiO2 45%, Flow 55, Pmean 11

CT from [REDACTED] loaded to Ion station. Navigation plan created to LLL superior segment mass. Automatic registration completed. Fiducial error 1.4mm - acceptable.

Ion catheter deployed. Initial navigation showed 8mm deviation at target - reregistration performed with improved accuracy (error 0.9mm).

Radial probe inserted through Ion working channel. Eccentric pattern visualized - lesion 36mm diameter. Probe withdrawn, biopsy tools inserted.

Obtained:
• 8 transbronchial biopsies (formalin)
• 3 brush specimens (cytopathology)
• Bronchial washings (cytology, AFB, fungal, bacterial cx)

ROSE: highly cellular, malignant cells consistent with squamous cell carcinoma

Fiducial marker (0.8x3mm gold CIVCO) placed in LLL anterior segmental bronchus under fluoroscopy - confirmed adequate position for radiation planning.

Post-procedure: hemostasis confirmed, no bleeding. Patient extubated, stable vitals, transferred to recovery.

PLAN: Multidisciplinary tumor board discussion. Likely SBRT candidate given node-negative disease. F/u 1 week.
**Bronchoscopy Report**

Thompson Memorial Hospital
Department of Interventional Pulmonology

Pt [REDACTED]: Lee, Catherine Y. | Age: 72 | Sex: F
Medical Record: [REDACTED] | Date: [REDACTED]
Attending: Dr. Rebecca Hoffman | Fellow: Dr. James Park

**Chief Complaint:** Incidental pulmonary nodule

**HPI:** Patient with history of breast cancer (2018, in remission) found to have 1.8cm RML nodule on surveillance CT. PET shows mild uptake SUV 2.8. Presents for tissue diagnosis.

**Procedure Performed:** Robotic bronchoscopy (Intuitive Ion platform), radial endobronchial ultrasound, transbronchial biopsy

**Informed Consent:** Reviewed risks of bleeding (1-5%), pneumothorax (1-2%), infection, need for chest tube, respiratory compromise. Patient consented.

**Anesthesia:** GETA by Dr. Steven Kim. MAC #7.5 ETT, depth 21cm at teeth.

**Ventilator Parameters:** SIMV, Rate 12, Vt 400mL, PEEP 5, FiO2 50%, I:E 1:2

**Technique:**
Preoperative CT dated [REDACTED] uploaded to Ion planning workstation. Virtual pathway generated to RML medial segment nodule.

Registration protocol: Automatic method employed. Carina, RUL/RML/RLL carinas, and segmental bifurcations matched. Global alignment quality: excellent. Mean fiducial registration error: 1.1mm.

Ion robotic catheter navigated along planned trajectory. Distance to target: 0.8cm at final position.

Radial EBUS probe (1.4mm) inserted - demonstrated concentric hypoechoic pattern, lesion diameter 17mm, well-circumscribed borders.

CBCT performed (NaviLink 3D fusion): Overlay confirmed catheter within lesion volume. Margin from lesion center: 2mm.

**Samples obtained:**
- TBBx x 5 (histopathology)
- Cytology brush x 2
- BAL from RML (cell count, micro)

**ROSE:** Adequate sample. Bronchioloalveolar cells, no malignancy id[REDACTED] in initial review. (Final cytology pending)

**Findings:**
- Upper airway: normal
- Trachea: patent, no masses
- Carina: sharp, mobile
- Right bronchial tree: patent, no endobronchial lesions
- Left bronchial tree: not fully examined given unilateral target

**Complications:** None
**EBL:** Minimal
**Condition:** Stable, extubated, to PACU

**Assessment/Plan:**
Successful robotic bronchoscopy with biopsy of RML nodule. ROSE shows no definitive malignancy but final pathology pending. If benign, plan for 3-month interval CT surveillance per Fleischner criteria. Patient to follow up in clinic 2 weeks for pathology review.

Electronically signed: R. Hoffman MD - [REDACTED] 16:45"""

e10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Mediastinal nodes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "diagnostic bronch", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "fiducial", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL superior segment", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.4mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Ion catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Radial probe", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "36mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "8", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "transbronchial biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchial washings", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "squamous cell carcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Fiducial marker", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "0.8x3mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL anterior segmental bronchus", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "fluoroscopy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "hemostasis confirmed", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no bleeding", 1)},
    
    # Second Note Context in t10
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.8cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Intuitive Ion platform", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "radial endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "transbronchial biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "ETT", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML medial segment", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Ion robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Radial EBUS probe", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.4mm", 2)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "17mm", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "TBBx", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Cytology brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 3)},
    {"label": "OBS_ROSE", **get_span(t10, "ROSE", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "no malignancy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Carina", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right bronchial tree", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left bronchial tree", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "None", 1)}
]
BATCH_DATA.append({"id": "5029384", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)