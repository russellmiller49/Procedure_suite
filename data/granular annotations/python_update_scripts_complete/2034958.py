import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

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
# Note 1: 2034958_syn_1
# ==========================================
text_1 = """Indication: Central airway obstruction (R main) and R pleural effusion.
Procedure: Rigid bronchoscopy. Tumor cored/debrided. APC/Cautery for hemostasis. Balloon dilation. 14x60mm metallic stent placed. PleurX catheter placed right hemithorax.
Complication: None.
Result: Airway patent. Effusion drained."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Central airway obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "R main", 1)},
    {"label": "LATERALITY", **get_span(text_1, "R", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "cored", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "debrided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cautery", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Balloon dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_1, "14x60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "metallic stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "PleurX catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "right hemithorax", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "Airway patent", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "Effusion drained", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2034958_syn_2
# ==========================================
text_2 = """OPERATIVE NARRATIVE: The patient was brought to the operating suite for management of complex malignant central airway obstruction and malignant pleural effusion. Under general anesthesia with rigid bronchoscopic intubation, the right mainstem bronchus was visualized, demonstrating 90% occlusion by fungating tumor. Mechanical debulking was performed utilizing the rigid barrel, followed by electrocautery and argon plasma coagulation to the tumor base (CPT 31641). Following balloon dilation, a covered metallic stent was deployed, restoring luminal patency to the right mainstem bronchus (CPT 31636). Subsequently, a tunneled indwelling pleural catheter was inserted into the right hemithorax for palliation of the recurrent effusion (CPT 32550)."""

entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "malignant central airway obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignant pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rigid bronchoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "intubation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "right mainstem bronchus", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "90% occlusion", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "fungating tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "rigid barrel", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "electrocautery", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "argon plasma coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "balloon dilation", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "covered metallic stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "deployed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "restoring luminal patency", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "right mainstem bronchus", 2)},
    {"label": "DEV_CATHETER", **get_span(text_2, "tunneled indwelling pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "inserted", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "right hemithorax", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "recurrent effusion", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2034958_syn_3
# ==========================================
text_3 = """Procedures Performed:
1. 31641: Rigid bronchoscopy with destruction of tumor. Justification: APC and mechanical coring used to relieve right mainstem obstruction.
2. 31636: Bronchoscopy with stent placement. Justification: Covered metallic stent deployed in R mainstem after debulking.
3. 32550: Insertion of tunneled pleural catheter. Justification: Indwelling catheter placed for recurrent malignant effusion."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "mechanical coring", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "right mainstem", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "stent placement", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "Covered metallic stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "R mainstem", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Insertion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "tunneled pleural catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Indwelling catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "placed", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "recurrent malignant effusion", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2034958_syn_4
# ==========================================
text_4 = """Procedure Note
Patient: [REDACTED]
Attending: Dr. Kim
Steps:
1. Time out. GA induced. Rigid scope inserted.
2. Saw tumor in Right Main. Debulked with scope tip and APC.
3. Dilated with balloon.
4. Placed metal stent (14x60). Good position.
5. Did PleurX catheter on the right side. Got 850cc fluid.
6. Extubated/Stable."""

entities_4 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "inserted", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Right Main", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Debulked", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "scope tip", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Placed", 1)},
    {"label": "DEV_STENT", **get_span(text_4, "metal stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_4, "14x60", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "PleurX catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "right side", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "850cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "fluid", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2034958_syn_5
# ==========================================
text_5 = """we did a rigid bronch today on Clara Oswin for that airway tumor right side. used the storz scope cored out the tumor and burned the rest with APC. put a stent in there looks wide open now. also put in a pleurx catheter for the fluid on the right side. no issues really patient stable to recovery."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "rigid bronch", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "airway", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "storz scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "cored out", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_5, "burned", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "put", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "wide open", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "put in", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "pleurx catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "fluid", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "right side", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2034958_syn_6
# ==========================================
text_6 = """The patient presented with right lung collapse and effusion. General anesthesia. Rigid bronchoscopy performed. Right mainstem tumor debrided mechanically and with APC. Airway caliber restored. Metallic stent deployed in right mainstem bronchus. Attention turned to right chest. Tunneled pleural catheter placed using standard technique. Fluid drained. Catheter capped. Patient tolerated well."""

entities_6 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "right lung", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "collapse", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Rigid bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Right mainstem", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "debrided", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "APC", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "Airway caliber restored", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "Metallic stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "right mainstem bronchus", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "right chest", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Tunneled pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "placed", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_6, "Fluid drained", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2034958_syn_7
# ==========================================
text_7 = """[Indication]
Malignant airway obstruction (R Main) and Recurrent Pleural Effusion.
[Anesthesia]
General, Rigid Bronchoscopy.
[Description]
Rigid scope introduced. Tumor debulked via mechanical coring and APC (31641). Stent (14x60mm) placed in Right Mainstem (31636). Tunneled PleurX catheter inserted right chest (32550).
[Plan]
ICU monitoring. CXR."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Malignant airway obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "R Main", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Recurrent Pleural Effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "introduced", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "debulked", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "mechanical coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "APC", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "Stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_7, "14x60mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "placed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "Right Mainstem", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Tunneled PleurX catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "inserted", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "right chest", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2034958_syn_8
# ==========================================
text_8 = """[REDACTED] taken to the OR for airway management. We utilized a rigid bronchoscope to access the airway. A large tumor in the right mainstem was effectively removed using mechanical coring and heat therapy. To prevent re-obstruction, we deployed a metallic stent. While she was under, we also addressed her fluid buildup by placing a tunneled PleurX catheter in the right chest. She tolerated all distinct procedures well."""

entities_8 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 2)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "right mainstem", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "removed", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "mechanical coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "heat therapy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "re-obstruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "deployed", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "metallic stent", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "fluid buildup", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "placing", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "tunneled PleurX catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "right chest", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2034958_syn_9
# ==========================================
text_9 = """Procedure: Rigid bronchoscopy with tumor ablation and stent deployment; indwelling pleural catheter insertion.
Action: The right mainstem neoplasm was resected using the rigid barrel and argon plasma coagulation. Patency was re-established. An airway prosthesis was anchored in the right mainstem. A tunneled pleural drainage system was implanted in the right hemithorax.
Outcome: Successful recanalization and fluid drainage."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "ablation", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "deployment", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "indwelling pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "insertion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "right mainstem", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "neoplasm", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "resected", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "rigid barrel", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "argon plasma coagulation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "Patency was re-established", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "airway prosthesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "anchored", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "right mainstem", 2)},
    {"label": "DEV_CATHETER", **get_span(text_9, "tunneled pleural drainage system", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "implanted", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "right hemithorax", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "Successful recanalization", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_9, "fluid drainage", 1)}
]

BATCH_DATA.append({"id": "2034958_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 2034958
# ==========================================
text_10 = """Name: [REDACTED]
Medical Record [REDACTED]: 2034958
Date of Birth: [REDACTED] (65 years old)
Sex: Female
Date of Service: [REDACTED]
Time In: 07:30 | Time Out: 11:45 | Total Procedure Time: 4 hours 15 minutes

CARE TEAM

Primary Operator: David Kim, MD - Interventional Pulmonology (Attending)
Assistant Operator: Rachel Foster, MD - Interventional Pulmonology Fellow (PGY-6)
Anesthesiologist: Margaret Sullivan, MD
CRNA: James Torres, CRNA
Circulating RN: Patricia Martinez, RN
Scrub Tech: Anthony Garcia, CST
Respiratory Therapist: Michelle Chen, RRT


CLINICAL HISTORY & INDICATION
Mrs. [REDACTED] is a 65-year-old Nigerian-American female with a complex medical history including stage IIIB adenocarcinoma of the right lung (diagnosed 04/2023), status post chemoradiation therapy (completed 10/2023). She has been experiencing progressive dyspnea over the past 3 months and was found to have:

Right mainstem bronchus obstruction - Interval CT imaging from [REDACTED] shows tumor recurrence causing 85% obstruction of the right mainstem bronchus with post-obstructive pneumonitis of the entire right lung
Malignant pericardial effusion - Echo from [REDACTED] showed moderate-large pericardial effusion with early tamponade physiology (RA collapse)
Right malignant pleural effusion - Thoracentesis [REDACTED] confirmed malignant cells

The patient presented to our interventional pulmonology clinic [REDACTED] with severe dyspnea (MMRC grade 4), inability to lie flat, oxygen requirement of 4L NC at rest. Given the multiple sites requiring intervention and the patient's overall debilitated status, the decision was made to address all issues in a single procedure session to minimize anesthetic exposures.
MULTIDISCIPLINARY PLANNING
Pre-procedure conference held [REDACTED] with IP, cardiothoracic surgery, oncology, and anesthesia. Plan formulated:

Address airway obstruction first (most critical)
Follow with pericardial window creation
Complete with PleurX catheter placement if patient tolerates

INFORMED CONSENT
Extensive discussion held with patient [REDACTED] (healthcare proxy) on [REDACTED] at 16:00. Risks discussed in detail:

Bleeding (estimated 5-10% risk given tumor vascularity)
Perforation or pneumothorax (5% risk)
Arrhythmia during pericardial procedure (10-15%)
Hypoxemia or respiratory failure (moderate risk given baseline status)
Need for ICU care postoperatively (expected)
Mortality risk (~2-5% given complexity and comorbidities)

Benefits reviewed: Improved breathing, reduced cardiac compromise, palliation of symptoms.
Alternatives discussed: No intervention (continued clinical decline), staged procedures (multiple anesthetic exposures).
Patient [REDACTED] understood risks and expressed wish to proceed. Written consent obtained and witnessed.

PREOPERATIVE DIAGNOSES

Recurrent adenocarcinoma of right lung with endobronchial obstruction (C34.11)
Malignant pericardial effusion with tamponade physiology (I31.3, C38.0)
Malignant pleural effusion, right (J91.0)
Respiratory failure, acute on chronic (J96.20)

POSTOPERATIVE DIAGNOSES
Same as preoperative
PROCEDURES PERFORMED

Rigid bronchoscopy with endobronchial tumor debridement
Electrocautery and argon plasma coagulation of endobronchial tumor
Balloon dilation of right mainstem bronchus stenosis
Metallic airway stent placement, right mainstem bronchus
Flexible bronchoscopy with inspection and therapeutic aspiration
Subxiphoid pericardial window creation (performed by CT surgery)
Pericardial biopsy
Tunneled pleural catheter placement, right hemithorax

CPT CODES

31640 (Bronchoscopy with tumor excision)
31641 (Bronchoscopy with destruction of tumor)
31630 (Bronchoscopy with dilation)
31631 (Bronchoscopy with stent placement)
31645 (Bronchoscopy with therapeutic aspiration)
33015 (Pericardial window, subxiphoid)
32550 (Insertion of indwelling pleural catheter)


ANESTHESIA DETAILS
Type: General anesthesia with endotracheal intubation
Induction: Fentanyl 150mcg IV, Propofol 180mg IV, Rocuronium 50mg IV
Maintenance: Sevoflurane 1.5-2.5% with intermittent propofol boluses, Fentanyl infusion
Airway: Initial 8.0mm oral endotracheal tube, exchanged to rigid bronchoscope
Monitoring:

Standard ASA monitors (ECG, NIBP, pulse oximetry, capnography, temperature)
Arterial line - left radial artery
Central venous catheter - right internal jugular (placed by anesthesia for access/monitoring)
Transesophageal echocardiography probe (for pericardial window portion)
Neuromuscular blockade monitoring

Hemodynamics: Patient remained hemodynamically stable throughout with MAP 65-85mmHg, HR 75-95 bpm. Vasopressor support with phenylephrine intermittent boluses (total 400mcg). Post-pericardial drainage, improvement in cardiac output noted on TEE."""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lung", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_10, "status post chemoradiation therapy", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "dyspnea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Right mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor recurrence", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "85% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right mainstem bronchus", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "post-obstructive pneumonitis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lung", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "Malignant pericardial effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pericardial effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "tamponade physiology", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "RA collapse", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "malignant pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Thoracentesis", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "dyspnea", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "airway obstruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "pericardial window creation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "PleurX catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placement", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Recurrent adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right lung", 3)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Malignant pericardial effusion", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "tamponade physiology", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "Malignant pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 7)},
    {"label": "PROC_METHOD", **get_span(text_10, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "debridement", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Electrocautery", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "argon plasma coagulation", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Balloon dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right mainstem bronchus", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "stenosis", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "Metallic airway stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placement", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right mainstem bronchus", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "therapeutic aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Subxiphoid pericardial window creation", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Pericardial biopsy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Tunneled pleural catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placement", 3)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "right hemithorax", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "endotracheal intubation", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Fentanyl", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Rocuronium", 1)},
    {"label": "MEDICATION", **get_span(text_10, "Sevoflurane", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "oral endotracheal tube", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Arterial line", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Central venous catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Transesophageal echocardiography probe", 1)},
    {"label": "MEDICATION", **get_span(text_10, "phenylephrine", 1)}
]

BATCH_DATA.append({"id": "2034958", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)