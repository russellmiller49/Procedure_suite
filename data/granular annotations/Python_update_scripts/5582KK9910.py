import sys
from pathlib import Path

# Set up path to import utility functions
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

# Import the add_case utility
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure you are running this from the correct repository structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of a case-sensitive term.
    """
    def find_nth(haystack, needle, n):
        start = -1
        for _ in range(n):
            start = haystack.find(needle, start + 1)
            if start == -1:
                return -1
        return start

    start = find_nth(text, term, occurrence)
    if start == -1:
        start = find_nth(text.lower(), term.lower(), occurrence)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text: {text[:50]}...")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 5582-KK-9910_syn_1
# ==========================================
t1 = """Indication: Post-biopsy hemorrhage RUL.
Procedure: Bronchoscopy + RFA.
Findings: Blood in RUL. No active bronchial source.
Action: Navigated to tumor site. RFA probe inserted. Coagulation mode (40W) then Ablation mode (90C). 
Result: Hemostasis achieved. Tumor ablated. Chest tube output decreased.
Plan: ICU, wean chest tube."""

e1 = [
    # Indication / Finding
    {"label": "OBS_FINDING", **get_span(t1, "hemorrhage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    
    # Procedure
    {"label": "PROC_ACTION", **get_span(t1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "RFA", 1)},
    
    # Findings
    {"label": "OBS_FINDING", **get_span(t1, "Blood", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 2)},
    
    # Action
    {"label": "PROC_METHOD", **get_span(t1, "Navigated", 1)},
    {"label": "OBS_LESION", **get_span(t1, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "RFA probe", 1)},
    {"label": "MEAS_ENERGY", **get_span(t1, "40W", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Ablation", 1)},
    {"label": "MEAS_TEMP", **get_span(t1, "90C", 1)},
    
    # Result / Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Hemostasis achieved", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "ablated", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Chest tube", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "chest tube", 2)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 5582-KK-9910_syn_2
# ==========================================
t2 = """PROCEDURE: Emergent Bronchoscopy with Radiofrequency Ablation for Hemostasis and Tumor Control.
INDICATION: 72-year-old male status post complicated TTNA with active hemothorax and parenchymal bleeding.
DESCRIPTION: Under general anesthesia, the airway was inspected. Utilizing ENB, the RFA catheter was advanced to the site of the bleeding tumor in the RUL. A modified RFA protocol was employed: initially low-wattage energy was applied to effect hemostasis via tissue coagulation, followed by standard high-temperature ablation to treat the underlying malignancy. Immediate cessation of bleeding was observed."""

e2 = [
    # Header
    {"label": "PROC_ACTION", **get_span(t2, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Radiofrequency Ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "Hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(t2, "Tumor", 1)},
    
    # Indication
    {"label": "OBS_FINDING", **get_span(t2, "hemothorax", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "bleeding", 1)},
    
    # Description
    {"label": "ANAT_AIRWAY", **get_span(t2, "airway", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "ENB", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "RFA catheter", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "bleeding", 2)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "RFA", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "hemostasis", 2)},
    {"label": "PROC_ACTION", **get_span(t2, "ablation", 2)},
    {"label": "OBS_LESION", **get_span(t2, "malignancy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "cessation of bleeding", 1)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 5582-KK-9910_syn_3
# ==========================================
t3 = """Codes: 31641 (Bronchoscopy with destruction/relief of stenosis).
Justification: RFA probe used primarily to destroy tumor tissue and secondarily to coagulate bleeding vessels in the tumor bed.
Note: This was a salvage procedure combining hemostasis (normally 31634/31643) and ablation (31641). 31641 is the primary definitive therapy performed."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "RFA probe", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "bleeding", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t3, "hemostasis", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "ablation", 1)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 5582-KK-9910_syn_4
# ==========================================
t4 = """Procedure: Urgent RFA
Patient: [REDACTED]
Indication: Bleeding after IR biopsy.
Steps:
1. Intubated. Bronch to RUL.
2. Navigated to biopsy site.
3. Inserted RFA probe.
4. Cauterized bleeding (40W).
5. Ablated tumor (90C).
6. Bleeding stopped.
Plan: ICU, keep chest tube."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "RFA", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Navigated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "RFA probe", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Cauterized", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "bleeding", 2)},
    {"label": "MEAS_ENERGY", **get_span(t4, "40W", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Ablated", 1)},
    {"label": "OBS_LESION", **get_span(t4, "tumor", 1)},
    {"label": "MEAS_TEMP", **get_span(t4, "90C", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "Bleeding stopped", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "chest tube", 1)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 5582-KK-9910_syn_5
# ==========================================
t5 = """emergency bronch for [REDACTED] he was bleeding from that IR biopsy yesterday chest tube putting out blood. we went in intubated him. used the nav system to find the hole in the tumor. stuck the RFA probe in there. cooked it at low power to stop the bleed then high power to kill the cancer. worked great bleeding stopped chest tube looks clear now. sending back to ICU."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "bronch", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsy", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "blood", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "nav system", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "RFA probe", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "bleed", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "bleeding stopped", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 2)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 5582-KK-9910_syn_6
# ==========================================
t6 = """Urgent bronchoscopy with radiofrequency ablation. Patient with hemothorax following transthoracic biopsy. General anesthesia. Airway clear of active large airway bleeding. Navigation to RUL posterior segment. RFA probe deployed. Hemostasis protocol (low power) followed by ablation protocol (high power) utilizing Vivant system. Hemostasis achieved. Tumor treated. Chest tube output diminished."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "radiofrequency ablation", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "hemothorax", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "transthoracic biopsy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "large airway", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL posterior segment", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "RFA probe", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "Hemostasis", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "ablation", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Vivant system", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "Hemostasis achieved", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Tumor", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 5582-KK-9910_syn_7
# ==========================================
t7 = """[Indication]
Post-biopsy hemorrhage, RUL tumor.
[Anesthesia]
General.
[Description]
Emergent navigation to RUL tumor. RFA applied for hemostasis and tumor destruction. Bleeding resolved. Tumor ablated.
[Plan]
ICU, monitor Hgb/Chest tube."""

e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "hemorrhage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(t7, "RFA", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "Bleeding resolved", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "ablated", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 5582-KK-9910_syn_8
# ==========================================
t8 = """[REDACTED] a complication from his lung biopsy yesterday and was bleeding into his chest. We took him to the bronchoscopy suite urgently. Using a special navigation system, we guided a radiofrequency probe to the bleeding tumor. We used the heat from the probe first to seal the bleeding vessels and then to destroy the tumor itself. It worked perfectly, and the bleeding stopped immediately."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "lung biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "navigation system", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "radiofrequency probe", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "bleeding", 2)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "bleeding", 3)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "bleeding stopped", 1)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 5582-KK-9910_syn_9
# ==========================================
t9 = """Procedure: Bronchoscopic thermal therapy.
Indication: Iatrogenic hemorrhage and malignancy.
Action: The hemorrhagic site was accessed via navigation. Thermal energy was applied to coagulate vessels and destroy neoplastic tissue. 
Result: Hemostasis and tumor ablation achieved."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Bronchoscopic thermal therapy", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "hemorrhage", 1)},
    {"label": "OBS_LESION", **get_span(t9, "malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "navigation", 1)},
    {"label": "OBS_LESION", **get_span(t9, "neoplastic tissue", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "Hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "ablation", 1)},
]
BATCH_DATA.append({"id": "5582-KK-9910_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 5582-KK-9910 (Original)
# ==========================================
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]  
PROCEDURE DATE: [REDACTED]
LOCATION: [REDACTED]
PHYSICIAN: Dr. Anthony Russo, MD

**URGENT CASE - POST-BIOPSY HEMORRHAGE MANAGEMENT**

ORIGINAL PROCEDURE: Transthoracic needle biopsy RUL nodule by interventional radiology (performed [REDACTED], 1430hrs). Biopsy complicated by significant hemorrhage with hemothorax development requiring chest tube placement. Patient transferred to ICU overnight. Biopsy confirmed squamous cell carcinoma.

MODIFIED INDICATION: 
Given active bleeding from biopsy site and confirmed malignancy, multidisciplinary discussion between interventional radiology, thoracic surgery, and interventional pulmonology. Decision made for bronchoscopic approach to: (1) achieve hemostasis and (2) treat tumor definitively with ablation given high surgical risk and desire to avoid repeat intervention.

**EMERGENT BRONCHOSCOPY WITH RFA - MODIFIED PROTOCOL**

Patient [REDACTED] chest tube in place (right pigtail, 14Fr). Active output decreased but persistent blood-tinged drainage 50mL/hr. Hemoglobin stable at 9.2 after transfusion.

PROCEDURE (Performed [REDACTED], 0800hrs):
General anesthesia, intubation. Bronchoscopy showed blood in RUL but no active endobronchial source. ENB navigation to RUL posterior segment biopsy site/tumor location. Immediate goal: hemostasis. Secondary goal: tumor ablation.

RFA probe (VIVANT, 1.5cm tip) placed at hemorrhage site within tumor. Treatment modified from standard protocol:
- Initial lower power (40W x 3min) for cauterization/hemostasis
- Then standard ablation (90°C x 8min) for tumor treatment
- Careful monitoring for increased bleeding during treatment

OUTCOME: 
Successfully achieved hemostasis - no further bleeding noted post-ablation. Tumor ablation completed per protocol. Chest tube output decreased to <10mL/hr serosanguinous fluid immediately post-procedure.

COMPLICATIONS: None additional

MODIFIED PLAN:
- ICU monitoring continues
- Chest tube remains, anticipate removal tomorrow if output <50mL/24hr
- CT chest at 48hr  
- Standard post-ablation follow-up once acute issues resolved

**UNUSUAL CASE DISCUSSION:**
This represents off-label use of bronchoscopic RFA for both hemostasis and tumor treatment following complicated transthoracic biopsy. While not standard indication, multidisciplinary team felt this was best approach to manage both bleeding and provide definitive treatment in one procedure. Case to be presented at morbidity/mortality conference for systems review of management pathway.

Dr. Anthony Russo, MD
Interventional Pulmonology - Tampa General
Attending on call for emergent procedures

Case reviewed with: Dr. Sarah Kim (Thoracic Surgery), Dr. James Liu (Interventional Radiology), Dr. Patricia Mendez (Pulmonary Critical Care)"""

e10 = [
    # History
    {"label": "OBS_FINDING", **get_span(t10, "hemorrhage", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transthoracic needle biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "hemorrhage", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "hemothorax", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "OBS_LESION", **get_span(t10, "squamous cell carcinoma", 1)},
    
    # Indication
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 1)},
    {"label": "OBS_LESION", **get_span(t10, "malignancy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "bronchoscopic approach", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 1)},
    
    # Pre-Op
    {"label": "PROC_ACTION", **get_span(t10, "BRONCHOSCOPY", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "RFA", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 2)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "pigtail", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t10, "14Fr", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "50mL", 1)},
    
    # Procedure
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "blood", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "ENB navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL posterior segment", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "hemostasis", 2)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 2)},
    
    # Treatment
    {"label": "DEV_INSTRUMENT", **get_span(t10, "RFA probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "VIVANT", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "hemorrhage", 3)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 4)},
    {"label": "MEAS_ENERGY", **get_span(t10, "40W", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "3min", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "cauterization", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "hemostasis", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 3)},
    {"label": "MEAS_TEMP", **get_span(t10, "90°C", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "8min", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 5)},
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 2)},
    
    # Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "hemostasis", 4)},
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 4)},
    {"label": "OBS_LESION", **get_span(t10, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 5)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "10mL", 1)},
    
    # Plan
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "50mL", 2)},
    
    # Discussion
    {"label": "PROC_ACTION", **get_span(t10, "RFA", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "hemostasis", 5)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 6)},
    {"label": "PROC_ACTION", **get_span(t10, "transthoracic biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 4)},
]
BATCH_DATA.append({"id": "5582-KK-9910", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
