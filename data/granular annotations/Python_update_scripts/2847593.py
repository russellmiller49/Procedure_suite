import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure this script is run from a location where 'scripts.add_training_case' is accessible
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure your project structure is correct.")
    sys.exit(1)

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
# Case 1: 2847593_syn_1
# ==========================================
text_1 = """Procedure: EBUS-TBNA & Ion Robotic Bronchoscopy.
EBUS: Stations 4R, 7 sampled. Positive for Adeno.
Ion: Navigated to RLL mass. r-EBUS concentric. Biopsied x8.
ROSE: Adenocarcinoma in node and mass.
Dx: Stage IIIA (N2 positive)."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion Robotic Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 2)}, # "EBUS:"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Stations 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "sampled", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Positive for Adeno", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 2)}, # "Ion:"
    {"label": "PROC_ACTION", **get_span(text_1, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "r-EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsied", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x8", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adenocarcinoma", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 2)},
]
BATCH_DATA.append({"id": "2847593_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 2847593_syn_2
# ==========================================
text_2 = """OPERATIVE NARRATIVE: A combined staging and diagnostic procedure was performed. First, convex EBUS allowed for sampling of stations 4R and 7; rapid on-site evaluation demonstrated adenocarcinoma. Subsequently, the Ion robotic platform was docked. The catheter was navigated to the RLL posterior basal segment mass. Radial EBUS confirmed concentric alignment. Transbronchial biopsies were obtained. The pathologic findings confirm primary lung adenocarcinoma with mediastinal nodal involvement (N2 disease)."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "convex EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sampling", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "stations 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Ion robotic platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL posterior basal segment", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "concentric alignment", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lung adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "2847593_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 2847593_syn_3
# ==========================================
text_3 = """Codes:
- 31652 (EBUS-TBNA 1-2 stations): Sampled 4R, 7.
- 31628 (Transbronchial lung biopsy): RLL mass via Ion.
- 31627 (Navigational Bronchoscopy): Ion system used.
- 31654 (Radial EBUS): Peripheral lesion check.
Note: Nodal staging performed first."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS-TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Transbronchial lung biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Ion system", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Peripheral lesion", 1)},
]
BATCH_DATA.append({"id": "2847593_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 2847593_syn_4
# ==========================================
text_4 = """Resident Note
Pt: [REDACTED]roc: EBUS + Ion
Steps:
1. EBUS first. Biopsied 4R and 7. Both malignant.
2. Switched to Ion robot.
3. Navigated to RLL mass.
4. rEBUS showed we were in the lesion.
5. Took biopsies.
Impression: Stage 3 Lung Cancer."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "malignant", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Ion robot", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "biopsies", 1)},
]
BATCH_DATA.append({"id": "2847593_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 2847593_syn_5
# ==========================================
text_5 = """We did a combined case today EBUS and the robot. Started with EBUS sampled the 4R and 7 nodes both looked cancerous on the slide. Then used the Ion robot to go out to that mass in the right lower lobe. Navigation was smooth. Biopsied the mass too confirmed it was the same cancer. So she has stage 3A."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(text_5, "sampled", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancerous", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "Ion robot", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "right lower lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "Navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "Biopsied", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "mass", 2)},
]
BATCH_DATA.append({"id": "2847593_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 2847593_syn_6
# ==========================================
text_6 = """Combined endobronchial ultrasound and robotic navigational bronchoscopy. Mediastinal staging was performed first via EBUS-TBNA of stations 4R and 7, revealing metastatic adenocarcinoma. The Ion robotic system was then utilized to navigate to a right lower lobe mass. Radial EBUS confirmed target acquisition. Transbronchial biopsies of the mass also showed adenocarcinoma. The patient was extubated and transferred to recovery."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "robotic navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "stations 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "7", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Ion robotic system", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "navigate", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Transbronchial biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mass", 2)},
    {"label": "OBS_ROSE", **get_span(text_6, "adenocarcinoma", 2)},
]
BATCH_DATA.append({"id": "2847593_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 2847593_syn_7
# ==========================================
text_7 = """[Indication]
RLL mass, mediastinal adenopathy.
[Anesthesia]
General, ETT.
[Description]
1. EBUS-TBNA: 4R, 7 positive for malignancy.
2. Ion Robotics: Navigation to RLL mass. Biopsies positive for malignancy.
[Plan]
Oncology consult for Stage IIIA NSCLC."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mediastinal adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "positive for malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Ion Robotics", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 2)},
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsies", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "positive for malignancy", 2)},
]
BATCH_DATA.append({"id": "2847593_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 2847593_syn_8
# ==========================================
text_8 = """[REDACTED] a diagnostic bronchoscopy today. We started by checking the lymph nodes in the center of her chest using the EBUS scope. Unfortunately, the samples from nodes 4R and 7 showed cancer cells. We then used the robotic system to navigate to the main tumor in her lower right lung and took a biopsy of that as well, which matched the lymph nodes. This confirms the cancer has spread to the lymph nodes, placing her at Stage IIIA."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "diagnostic bronchoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "lymph nodes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "EBUS scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "nodes 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_8, "7", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "cancer cells", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "robotic system", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "navigate", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lower right lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
]
BATCH_DATA.append({"id": "2847593_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 2847593_syn_9
# ==========================================
text_9 = """Procedure: Endosonography and Robotic-assisted bronchoscopy.
Findings: Mediastinal nodes 4R and 7 were sampled and found malignant. The primary RLL lesion was accessed via the robotic platform and sampled.
Conclusion: Primary adenocarcinoma with nodal metastasis."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Endosonography", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic-assisted bronchoscopy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "Mediastinal nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampled", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "malignant", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "robotic platform", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampled", 2)},
]
BATCH_DATA.append({"id": "2847593_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 2847593
# ==========================================
text_10 = """**INTERVENTIONAL PULMONOLOGY PROCEDURE REPORT**

**PATIENT INFORMATION:**
Name: [REDACTED]nne
MRN: [REDACTED]
DOB: [REDACTED]
Sex: Female
Date of Service: [REDACTED]

**CLINICAL TEAM:**
Attending: Dr. Nicholas Foster, MD, FCCP
Fellow: Dr. Amy Chen, MD
Anesthesia: Dr. Robert Martinez, MD
Nursing: RN Jessica Thompson
Respiratory Therapy: RT Michael Davis

**PROCEDURES PERFORMED:**
1. Endobronchial ultrasound with transbronchial needle aspiration (EBUS-TBNA)
2. Ion robotic navigational bronchoscopy
3. Radial endobronchial ultrasound
4. Transbronchial biopsy

**CPT CODES:** 31652, 31653, 31627, 31654, 31628

**INDICATIONS:**
55-year-old female with 35 pack-year smoking history presents with:
- Right lower lobe mass, 3.4cm, PET SUV 9.2
- Mediastinal lymphadenopathy: Station 4R (2.1cm, SUV 5.8), Station 7 (1.8cm, SUV 4.3)
- Requires both nodal staging and peripheral mass biopsy for diagnosis and treatment planning

**CONSENT:**
Comprehensive informed consent obtained. Risks discussed including but not limited to: bleeding (1-5%), pneumothorax (1-3%), infection (<1%), mediastinal complications (pericardial/vascular injury <0.1%), need for additional procedures, anesthesia-related complications. Patient expressed understanding and agreed to proceed.

**ANESTHESIA:**
General endotracheal anesthesia administered.
- Induction: Propofol 200mg, Fentanyl 150mcg, Rocuronium 50mg
- Maintenance: Sevoflurane, intermittent propofol boluses
- ETT: 8.0mm at 22cm at teeth
- Ventilation: Pressure control, Pinsp 18, RR 12, PEEP 5, FiO2 50%

**PRE-PROCEDURE TIMEOUT:**
Performed confirming patient id[REDACTED] (verbal + 2 id[REDACTED]), procedure planned, site/laterality confirmed, team introductions, equipment availability checked.

**PROCEDURE NARRATIVE:**

**PHASE 1: EBUS-TBNA FOR MEDIASTINAL STAGING**

EBUS bronchoscope (Olympus BF-UC190F) introduced through ETT.

Systematic mediastinal lymph node survey performed:

**STATION 4R (Right paratracheal):**
- Size: 22mm x 14mm
- Ultrasound features: Hypoechoic, heterogeneous, discrete borders
- Vascular pattern: Central hilar vessels present
- Elastography: Predominantly hard (strain ratio 8.2, suggesting malignancy)
- TBNA: 22-gauge needle, 4 passes
- ROSE: "Abundant cellularity, malignant cells present, consistent with non-small cell carcinoma, favor adenocarcinoma"

**STATION 7 (Subcarinal):**
- Size: 19mm x 16mm
- Ultrasound features: Hypoechoic, round, sharp borders
- Elastography: Firm (strain ratio 6.8)
- TBNA: 22-gauge needle, 4 passes
- ROSE: "Similar malignant cells as 4R, adenocarcinoma"

**Additional Stations Surveyed but Not Sampled:**
- Station 10R: 8mm (below size threshold)
- Station 11R: 6mm (not sampled - diagnostic yield from 4R/7 adequate)
- Left-sided stations: No enlarged nodes id[REDACTED]

**PHASE 2: ION ROBOTIC BRONCHOSCOPY FOR RLL MASS**

After completing EBUS, EBUS scope removed. Ion robotic bronchoscope introduced.

**Navigation Setup:**
CT chest from [REDACTED] loaded to Ion platform. 3D reconstruction showed target in RLL posterior basal segment.

**Ion Registration:**
Automatic registration performed. Landmarks matched at carina, RLL carina, and segmental bifurcations. Mean fiducial error: 1.3mm (acceptable). No registration drift observed.

**Navigation to Target:**
Ion catheter advanced under navigational guidance to RLL posterior basal segment. Real-time tracking showed tool-to-target distance of 0.7cm at final position.

**Radial EBUS:**
20MHz probe inserted through Ion extended working channel.
- Pattern: Concentric (lesion centered around probe)
- Size: 32mm diameter
- Characteristics: Heterogeneous echogenicity, irregular margins, no visible vessels in immediate vicinity

**CBCT Confirmation:**
Cone-beam CT spin acquired. NaviLink 3D fusion overlay confirmed catheter tip within lesion borders, 4mm from lesion center.

**Sampling of RLL Mass:**
- Transbronchial biopsies: 8 specimens obtained via Ion catheter
- Cytology brushings: 3 specimens
- Bronchial washing: sent for cytology and microbiology

**ROSE (Peripheral Lesion):**
"Adequate samples. Malignant cells consistent with adenocarcinoma, morphologically similar to lymph node specimens. Recommend molecular testing."

**HEMOSTASIS:**
No significant bleeding from any biopsy sites. Airways clear.

**PROCEDURE COMPLETION:**
Total procedure time: 78 minutes
EBUS portion: 32 minutes
Ion bronchoscopy portion: 46 minutes

Patient [REDACTED] well. Extubated in OR without difficulty. Transferred to PACU in stable condition, SpO2 98% on 2L NC.

**ESTIMATED BLOOD LOSS:** <10mL

**SPECIMENS:**
1. Station 4R TBNA x 4 passes (cell block + cytology)
2. Station 7 TBNA x 4 passes (cell block + cytology)
3. RLL mass TBBx x 8 (formalin, histopathology - **ORDER MOLECULAR TESTING**)
4. RLL mass brushings x 3 (cytology)
5. RLL mass washing (cytology, bacterial/fungal/AFB cultures)

**COMPLICATIONS:** None

**PRELIMINARY FINDINGS:**
- N2 disease confirmed (stations 4R, 7 both positive for adenocarcinoma)
- Primary RLL adenocarcinoma confirmed
- Stage: At least IIIA (T2bN2M0) pending full staging workup

**POST-PROCEDURE PLAN:**
1. Recovery room monitoring per protocol
2. Chest X-ray in 2 hours to rule out pneumothorax
3. Discharge home same day if stable and CXR clear
4. Complete staging: Brain MRI, consider bone scan if not covered by PET
5. Molecular testing: EGFR, ALK, ROS1, BRAF, PD-L1, broader NGS panel
6. Multidisciplinary tumor board presentation next week
7. Medical oncology referral for neoadjuvant therapy discussion
8. Radiation oncology consultation
9. Follow-up in IP clinic in 1 week with full pathology results

**CLINICAL IMPRESSION:**
Stage IIIA adenocarcinoma of the lung (RLL primary with N2 mediastinal involvement). Not a surgical candidate initially. Will likely require neoadjuvant chemoimmunotherapy with consideration for surgery after response assessment vs definitive chemoradiation. Molecular profiling pending.

**ATTENDING STATEMENT:**
I was present throughout the entire procedure, personally performed the critical portions including EBUS-TBNA and supervised the Ion navigation and sampling. I reviewed all ROSE results in real-time and made all clinical decisions.

Electronically signed: Dr. Nicholas Foster, [REDACTED] 16:42"""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Endobronchial ultrasound with transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ion robotic navigational bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Right lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "3.4cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Mediastinal lymphadenopathy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.1cm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.8cm", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Fentanyl", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Rocuronium", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Sevoflurane", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS-TBNA", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "EBUS bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "STATION 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "22mm x 14mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Hypoechoic, heterogeneous", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignant cells present, consistent with non-small cell carcinoma, favor adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "STATION 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "19mm x 16mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Hypoechoic, round", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22-gauge needle", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "Similar malignant cells as 4R, adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 11R", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ION ROBOTIC BRONCHOSCOPY", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Ion robotic bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL posterior basal segment", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RLL carina", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Ion catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL posterior basal segment", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "20MHz probe", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Concentric", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "32mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Heterogeneous echogenicity, irregular margins", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "catheter", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "8 specimens", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Ion catheter", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "3 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchial washing", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Malignant cells consistent with adenocarcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 3)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 passes", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBNA", 4)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 passes", 4)},
    {"label": "OBS_LESION", **get_span(text_10, "RLL mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBBx", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x 8", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "RLL mass", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "RLL mass", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "washing", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "stations 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "7", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "positive for adenocarcinoma", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "RLL adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "EBUS-TBNA", 3)},
]
BATCH_DATA.append({"id": "2847593", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)