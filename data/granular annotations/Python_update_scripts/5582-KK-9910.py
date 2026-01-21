import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parents[3]

# Import the utility function to add the case
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    def find_nth(haystack, needle, n):
        start = -1
        for _ in range(n):
            start = haystack.find(needle, start + 1)
            if start == -1:
                return -1
        return start

    start_index = find_nth(text, term, occurrence)
    if start_index == -1:
        start_index = find_nth(text.lower(), term.lower(), occurrence)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")

    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 5582KK9910_syn_1
# ==========================================
t1 = """Indication: Post-biopsy hemorrhage RUL + Tumor Rx.
Proc: Nav Bronch + RFA.
Target: RUL posterior.
Action: RFA 40W (hemostasis) -> 90C (ablation).
Outcome: Bleeding stopped. Tumor ablated.
Plan: ICU, keep chest tube."""

e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "hemorrhage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Nav Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "RFA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL posterior", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "RFA", 2)},
    {"label": "MEAS_ENERGY", **get_span(t1, "40W", 1)},
    {"label": "MEAS_TEMP", **get_span(t1, "90C", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Bleeding stopped", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Tumor", 2)},
    {"label": "DEV_CATHETER", **get_span(t1, "chest tube", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 5582KK9910_syn_2
# ==========================================
t2 = """EMERGENT PROCEDURE: [REDACTED] bronchoscopic intervention for hemorrhage following transthoracic biopsy. Navigation was used to localize the bleeding site within the RUL tumor. Radiofrequency ablation was applied first for hemostasis, followed by a full ablation protocol to treat the underlying malignancy. Hemostasis was achieved."""

e2 = [
    {"label": "OBS_FINDING", **get_span(t2, "hemorrhage", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Radiofrequency ablation", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "ablation", 2)},
    {"label": "OBS_LESION", **get_span(t2, "malignancy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "Hemostasis was achieved", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 5582KK9910_syn_3
# ==========================================
t3 = """Codes: 31641 (Destruction/Hemostasis via RFA), 31627 (Navigation). RFA used for both control of hemorrhage and tumor destruction in the same session."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "RFA", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "RFA", 2)},
    {"label": "OBS_FINDING", **get_span(t3, "hemorrhage", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 5582KK9910_syn_4
# ==========================================
t4 = """Urgent Bronch: Timothy Brooks
Indication: Bleeding after IR biopsy.
1. Intubated.
2. Navigated to RUL bleeding site.
3. RFA probe in.
4. Cauterized bleeding (stopped).
5. Burned the tumor while we were there.
6. Chest tube output dropped."""

e4 = [
    {"label": "OBS_FINDING", **get_span(t4, "Bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "RFA probe", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "bleeding", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "stopped", 1)},
    {"label": "OBS_LESION", **get_span(t4, "tumor", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 5582KK9910_syn_5
# ==========================================
t5 = """timothy brooks bleeding from that biopsy yesterday chest tube putting out blood. went in with the scope navigated to the spot in the right upper lobe. used the rfa probe to stop the bleeding worked great. then just decided to ablate the tumor too since we were there. bleeding stopped chest tube looks good."""

e5 = [
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsy", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "blood", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "scope", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "right upper lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rfa probe", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 2)},
    {"label": "PROC_ACTION", **get_span(t5, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 3)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 2)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 5582KK9910_syn_6
# ==========================================
t6 = """Emergency bronchoscopy performed for hemothorax post-biopsy. Electromagnetic navigation utilized to reach RUL posterior segment target. Radiofrequency ablation catheter deployed. Initial energy applied for hemostasis successful. Subsequent energy cycles delivered for tumor ablation. Chest tube output diminished significantly."""

e6 = [
    {"label": "OBS_FINDING", **get_span(t6, "hemothorax", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL posterior segment", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Radiofrequency ablation catheter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "hemostasis successful", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "ablation", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 5582KK9910_syn_7
# ==========================================
t7 = """[Indication]
RUL hemorrhage post-biopsy.
[Anesthesia]
General.
[Description]
Navigation to RUL. RFA applied for hemostasis and tumor ablation. Bleeding resolved.
[Plan]
ICU. Monitor output."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "hemorrhage", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 2)},
    {"label": "PROC_METHOD", **get_span(t7, "RFA", 1)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "ablation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "Bleeding resolved", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 5582KK9910_syn_8
# ==========================================
t8 = """[REDACTED] after his biopsy yesterday. We performed a bronchoscopy to stop the bleeding. We navigated to the spot in his right lung and used heat (radiofrequency) to seal the bleeding vessels. Once the bleeding stopped, we continued the heat treatment to destroy the tumor itself."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right lung", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radiofrequency", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "bleeding", 2)},
    {"label": "OBS_FINDING", **get_span(t8, "bleeding", 3)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 5582KK9910_syn_9
# ==========================================
t9 = """Procedure: Hemostasis and tumor destruction via radiofrequency energy.
Method: Navigational bronchoscopy.
Outcome: Cessation of hemorrhage and thermal ablation of the neoplasm."""

e9 = [
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "radiofrequency energy", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Navigational bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "hemorrhage", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(t9, "neoplasm", 1)},
]
BATCH_DATA.append({"id": "5582KK9910_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 5582KK9910
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
    {"label": "PROC_ACTION", **get_span(t10, "Transthoracic needle biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "hemorrhage", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "hemothorax", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Biopsy", 2)},
    {"label": "OBS_LESION", **get_span(t10, "squamous cell carcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 1)},
    {"label": "OBS_LESION", **get_span(t10, "malignancy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "RFA", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 2)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "pigtail", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t10, "14Fr", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "50mL", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "blood", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "ENB navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL posterior segment", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "RFA probe", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.5cm", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "hemorrhage", 3)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 4)},
    {"label": "MEAS_ENERGY", **get_span(t10, "40W", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "3min", 1)},
    {"label": "MEAS_TEMP", **get_span(t10, "90°C", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "8min", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 5)},
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Successfully achieved hemostasis", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 3)},
    {"label": "OBS_LESION", **get_span(t10, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 4)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "10mL", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "50mL", 2)},
    {"label": "MEAS_TIME", **get_span(t10, "24hr", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "RFA", 2)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 6)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsy", 3)},
    {"label": "OBS_FINDING", **get_span(t10, "bleeding", 4)},
]
BATCH_DATA.append({"id": "5582KK9910", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
