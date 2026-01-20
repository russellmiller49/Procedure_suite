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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Case 1: 4821956_syn_1
# ==========================================
text_1 = """Indication: Bilateral nodules (RUL/LUL).
Procedure: Ion robotic bronchoscopy.
Actions:
- Registered Ion system.
- Sampled RUL anterior nodule (forceps x6, brush x2).
- Sampled LUL apical-posterior nodule (forceps x5, brush x2).
ROSE: Adenocarcinoma both sites.
Result: No complications."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion system", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Sampled", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "brush", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Sampled", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL apical-posterior", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "brush", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x2", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 4821956_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: The patient presented for evaluation of synchronous bilateral pulmonary nodules. The Ion robotic platform was deployed. Following successful registration (fiducial error 0.9 mm), navigation was sequentially performed to the right upper lobe anterior segment and the left upper lobe apical-posterior segment. Radial EBUS confirmation and fluoroscopic verification preceded tissue acquisition. Transbronchial forceps biopsies and cytology brushings were obtained from both sites. Rapid on-site evaluation was suggestive of adenocarcinoma in both locations, raising suspicion for synchronous primaries versus metastatic disease."""

entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "nodules", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Ion robotic platform", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right upper lobe anterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left upper lobe apical-posterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "fluoroscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "brushings", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 4821956_syn_3
# ==========================================
text_3 = """CPT Codes: 31627 (Navigational bronchoscopy), 31654 (Radial EBUS), 31628 (Transbronchial lung biopsy - first lobe), 31632 (Transbronchial lung biopsy - additional lobe), 31623 (Brushings).
Rationale: Robotic navigation and radial EBUS were used to localize peripheral lesions. Biopsies were taken from the RUL (initial lobe) and the LUL (additional lobe). Brushings were also performed."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Transbronchial lung biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Transbronchial lung biopsy", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "Brushings", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Robotic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "lesions", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Brushings", 2)},
]
BATCH_DATA.append({"id": "4821956_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 4821956_syn_4
# ==========================================
text_4 = """Procedure: Robotic Bronchoscopy (Bilateral)
Patient: [REDACTED]
Steps:
1. General anesthesia, ETT.
2. Ion registration complete.
3. Navigated to RUL nodule -> REBUS confirmed -> Biopsied.
4. Navigated to LUL nodule -> REBUS confirmed -> Biopsied.
5. ROSE: Adeno in both.
Plan: Staging workup."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Robotic Bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Ion", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Navigated", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodule", 2)},
    {"label": "PROC_METHOD", **get_span(text_4, "REBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 2)},
    {"label": "OBS_ROSE", **get_span(text_4, "Adeno", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 4821956_syn_5
# ==========================================
text_5 = """Anjali has nodules on both sides so we used the robot. Registered the ion system error was good under 1mm. Went to the right upper lobe first radial probe showed the lesion took biopsies and brushings. Then went to the left upper lobe and did the same thing. Rose said adenocarcinoma for both of them. She woke up fine no pneumothorax on the xray."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ion system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "right upper lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "radial probe", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brushings", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "left upper lobe", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no pneumothorax", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 4821956_syn_6
# ==========================================
text_6 = """Ion Robotic Bronchoscopy, Bilateral Nodule Sampling. Patient is a 45-year-old female with incidental bilateral lung nodules. RUL nodule 2.1cm, LUL nodule 1.6cm. Registration using automatic method was completed. Ion catheter navigated to RUL anterior segment and LUL apical-posterior segment. Tool-at-target confirmed by Radial EBUS. Forceps biopsies and brushings obtained from both sites. ROSE showed atypical pneumocytes, favor adenocarcinoma. No pneumothorax."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Ion Robotic Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "2.1cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 2)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.6cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Ion", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL anterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL apical-posterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "brushings", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "atypical pneumocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No pneumothorax", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 4821956_syn_7
# ==========================================
text_7 = """[Indication]
Bilateral lung nodules (RUL/LUL), suspicion of malignancy.
[Anesthesia]
General, ETT.
[Description]
Ion robotic navigation performed. Targets localized with REBUS. RUL and LUL nodules biopsied (forceps/brush). ROSE positive for adenocarcinoma bilaterally.
[Plan]
Final path pending. Staging MRI/PET."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "ETT", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Ion robotic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "REBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 2)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsied", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 4821956_syn_8
# ==========================================
text_8 = """[REDACTED] a robotic bronchoscopy to biopsy nodules in both her right and left lungs. We used the Ion robot to precisely navigate to each spot, confirming our location with ultrasound. We took tissue samples from both the right upper lobe and left upper lobe. The preliminary results suggests cancer in both spots, likely adenocarcinoma. She tolerated the procedure well and had no complications like a collapsed lung."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left lungs", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Ion robot", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "navigate", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "tissue samples", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right upper lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left upper lobe", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "cancer", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "no complications", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 4821956_syn_9
# ==========================================
text_9 = """Procedure: Robotic navigational sampling of bilateral pulmonary lesions.
Technique: Ion system utilized for localization. Radial EBUS verification performed.
Intervention: Transbronchial forceps and brush sampling of RUL and LUL targets.
Findings: Cytopathology consistent with adenocarcinoma.
Outcome: Patient extubated and stable."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic navigational", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesions", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Ion system", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LUL", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "4821956_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 4821956
# ==========================================
text_10 = """**PULMONARY PROCEDURE NOTE**

NAME: [REDACTED]
DOB: [REDACTED]
MRN: [REDACTED]
DOS: [REDACTED]
PROVIDER: Christopher Hayes, MD (Attending)
TRAINEE: Emily Watson, MD (IP Fellow)

**PROCEDURE:** Ion Robotic Bronchoscopy, Bilateral Nodule Sampling

**CLINICAL HISTORY:**
45F never-smoker with incidental bilateral lung nodules discovered on CT for evaluation of chronic cough. RUL nodule 2.1cm, LUL nodule 1.6cm. Both PET avid (SUV 3.4 and 2.9 respectively). No lymphadenopathy. Patient referred for tissue diagnosis.

**MEDICATIONS:**
Home meds held per protocol. No anticoagulation.

**PROCEDURE SUMMARY:**

Pre-procedure CT ([REDACTED]) loaded to Ion system. Dual-target navigation plan created for sequential sampling of RUL and LUL nodules.

Patient [REDACTED] anesthesia. ETT size 7.5 at 21cm at lips.

Vent Settings: VC mode, TV 420mL, RR 12, PEEP 5, FiO2 60%, Flow rate 50L/min, Pmean 12cmH2O

**ION REGISTRATION - COMPLETE:**
Registration using automatic method. Landmarks matched: carina, bilateral lobar carinas, segmental bifurcations RUL/LUL. Mean fiducial error 0.9mm. Excellent global alignment. No registration drift observed.

**TARGET 1 - RUL ANTERIOR SEGMENT NODULE:**

Ion catheter navigated to RUL anterior segment. Tool-at-target confirmed by:
- Navigation software showing 0.5cm distance
- Radial EBUS concentric pattern, 19mm lesion
- Fluoroscopy AP/lateral projections

Samples:
- Forceps biopsy x6
- Brushings x2
- Washing sent for cytology

ROSE: Atypical pneumocytes, favor adenocarcinoma. Final pending.

**TARGET 2 - LUL APICAL-POSTERIOR SEGMENT NODULE:**

Catheter repositioned to LUL. Navigation time from RUL target to LUL target: 8 minutes.

Radial EBUS: eccentric pattern initially, adjusted catheter position, achieved concentric pattern. Lesion 14mm.

Samples:
- Forceps biopsy x5
- Brushings x2

ROSE: Similar to RUL - atypical cells concerning for malignancy.

**PROCEDURE COMPLETION:**

Total procedure time: 62 minutes
Total navigation time: 47 minutes
Combined registration + navigation time to first nodule: 18 minutes

Hemostasis verified. Airways cleared. Patient extubated successfully, to recovery in stable condition.

Post-op CXR: No pneumothorax

**ASSESSMENT:**
Successful bilateral lung nodule sampling via robotic bronchoscopy. ROSE suggests possible synchronous primary lung cancers vs metastatic disease. Await final pathology. If malignant, will need PET/CT, brain MRI staging. Discussion at thoracic tumor board.

**FOLLOW-UP:** IP clinic 2 weeks

Dr. Christopher Hayes, Attending - electronically signed [REDACTED] 17:20
**BRONCHOSCOPY PROCEDURE NOTE**

Patient [REDACTED]: Williams, Robert D. | 71M | MRN [REDACTED]
Date of Service: [REDACTED]
Physician: Dr. Laura Martinez, Interventional Pulmonology
Fellow Physician: Dr. Ahmed Hassan

**Indication:** LLL nodule 2.8cm, hypermetabolic on PET scan

**Procedure:** Electromagnetic Navigation Bronchoscopy with transbronchial biopsy and radial EBUS

**Consent:** Obtained after discussion of risks including pneumothorax (~2%), bleeding (~1%), infection, need for additional procedures

**Sedation:** Moderate conscious sedation - Midazolam 3mg IV, Fentanyl 100mcg IV. Monitoring by RN Sarah Cooper. Vitals stable throughout.

**Procedure Details:**

Flexible bronchoscope (Olympus BF-1TH190) introduced via oral route. Initial survey:
- Oropharynx: unremarkable
- Larynx: no masses, cords mobile
- Trachea: midline, patent
- Carina: sharp
- Bilateral bronchial trees surveyed - no endobronchial lesions id[REDACTED]

Pre-procedure CT from [REDACTED] used for planning. SuperDimension electromagnetic navigation system employed.

**EMN Planning and Navigation:**
Virtual pathway created to LLL superior segment nodule. Registration performed automatically with good correlation (8 registration points matched, error <5mm acceptable).

Extended working channel (EWC) placed. EMN locatable guide advanced along planned pathway. Position verified at multiple checkpoints. Distance to target upon final positioning: 0.8cm.

**Radial EBUS:**
1.4mm radial probe advanced through EWC. Ultrasound demonstrated:
- Concentric hypoechoic lesion
- Irregular borders
- Size approximately 26mm
- No visible vessels within sampling trajectory

**Tissue Acquisition:**
Through guide sheath (after probe removal):
- Transbronchial forceps biopsies x 6 (sent to pathology in formalin)
- Cytology brush specimens x 3 (sent to cytology)
- Bronchial washing (sent for culture and cytology)

No immediate bleeding. Gentle suctioning applied.

**Rapid On-Site Evaluation (ROSE):**
Cytotechnologist present. Preliminary read: "Adequate cellularity. Malignant cells present consistent with adenocarcinoma. Recommend full cell block for molecular testing."

**Post-Procedure:**
Patient [REDACTED] well. No desaturation. Maintained SpO2 >95% on 2L NC throughout. No complications.

Portable CXR ordered - will check prior to discharge.

**Specimens Sent:**
1. TBBx x6 (histopathology)
2. Cytology brushings x3
3. Bronchial washing (microbiology and cytopathology)

**Impression:** Successful EMN bronchoscopy with biopsy of LLL nodule. ROSE positive for malignancy. Await final pathology and molecular testing for treatment planning.

**Plan:**
- Discharge home today if CXR negative
- Full staging workup (brain MRI, PET/CT if not recent)
- Return to clinic in 1 week for pathology review
- Referral to medical oncology and thoracic surgery for multidisciplinary evaluation

Laura Martinez, MD - [REDACTED]"""

entities_10 = [
    # Note 1 (Hayes)
    {"label": "PROC_METHOD", **get_span(text_10, "Ion Robotic Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.1cm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.6cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "ETT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Ion catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "19mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x2", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Atypical pneumocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL APICAL-POSTERIOR SEGMENT", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "NODULE", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "Lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Forceps", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsy", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Brushings", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x2", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "atypical cells", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "62 minutes", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "47 minutes", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "18 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No pneumothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "robotic bronchoscopy", 1)},

    # Note 2 (Martinez)
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 5)}, # 2 in Hayes, 2 header/summary, 1 here
    {"label": "MEAS_SIZE", **get_span(text_10, "2.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Electromagnetic Navigation Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "transbronchial biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "radial EBUS", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Fentanyl", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Carina", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "SuperDimension electromagnetic navigation system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL superior segment", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 6)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Extended working channel", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "EWC", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EMN", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "locatable guide", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "radial probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "26mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "guide sheath", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x 6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Cytology brush", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x 3", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "adenocarcinoma", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "TBBx", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "brushings", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EMN bronchoscopy", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignancy", 2)},
]
BATCH_DATA.append({"id": "4821956", "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)