import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# Assuming saved in: data/granular_annotations/Python_update_scripts/
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
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 8472-9315_syn_1
# ==========================================
id_1 = "8472-9315_syn_1"
text_1 = """Indication: RUL posterior nodule (2.3cm). High risk surgical candidate.
Procedure: EMN Bronchoscopy + Microwave Ablation.
Equipment: SuperDimension, Emprint 2.0 probe.
Action: Navigated to RB1. Confirmed w/ R-EBUS & Cone Beam. Ablated 65W x 5 min (Max temp 85C).
Result: Hyperechoic zone on R-EBUS (necrosis).
Plan: [REDACTED] 6h."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL posterior", 1)},
    {"label": "OBS_LESION",    **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_1, "2.3cm", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "EMN Bronchoscopy", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "Microwave Ablation", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "SuperDimension", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_1, "Emprint 2.0 probe", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RB1", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "R-EBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_1, "Cone Beam", 1)},
    {"label": "PROC_ACTION",   **get_span(text_1, "Ablated", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_1, "65W", 1)},
    {"label": "MEAS_TIME",     **get_span(text_1, "5 min", 1)},
    {"label": "MEAS_TEMP",     **get_span(text_1, "85C", 1)},
    {"label": "OBS_FINDING",   **get_span(text_1, "Hyperechoic zone", 1)},
    {"label": "OBS_FINDING",   **get_span(text_1, "necrosis", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 8472-9315_syn_2
# ==========================================
id_2 = "8472-9315_syn_2"
text_2 = """OPERATIVE REPORT: Electromagnetic Navigation Bronchoscopy with Microwave Ablation.
INDICATION: Primary lung adenocarcinoma, RUL posterior segment, in a patient with severe COPD.
TECHNIQUE: General anesthesia was induced. Using the SuperDimension system, the RUL posterior target was cannulated. Radial EBUS and Cone-Beam CT verified probe placement within 5mm of the lesion center. A microwave ablation catheter was advanced. Energy was delivered (65W, 5 min) achieving a peak tip temperature of 85C. Post-ablation imaging confirmed coagulative necrosis encompassing the tumor."""

entities_2 = [
    {"label": "PROC_METHOD",   **get_span(text_2, "Electromagnetic Navigation Bronchoscopy", 1)},
    {"label": "PROC_ACTION",   **get_span(text_2, "Microwave Ablation", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "lung adenocarcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL posterior segment", 1)},
    {"label": "PROC_METHOD",   **get_span(text_2, "SuperDimension system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL posterior", 1)},
    {"label": "PROC_METHOD",   **get_span(text_2, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_2, "Cone-Beam CT", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_2, "5mm", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_2, "microwave ablation catheter", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_2, "65W", 1)},
    {"label": "MEAS_TIME",     **get_span(text_2, "5 min", 1)},
    {"label": "MEAS_TEMP",     **get_span(text_2, "85C", 1)},
    {"label": "OBS_FINDING",   **get_span(text_2, "coagulative necrosis", 1)},
    {"label": "OBS_LESION",    **get_span(text_2, "tumor", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 8472-9315_syn_3
# ==========================================
id_3 = "8472-9315_syn_3"
text_3 = """Billing Codes:
- 31641: Destruction of tumor (Microwave Ablation).
- 31627: Navigation (SuperDimension).
- 31654: Radial EBUS.
Note: No biopsy performed today (diagnostic confirmed prior). 31641 is the primary service."""

entities_3 = [
    {"label": "OBS_LESION",    **get_span(text_3, "tumor", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3, "Microwave Ablation", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "Navigation", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "SuperDimension", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3, "Radial EBUS", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 8472-9315_syn_4
# ==========================================
id_4 = "8472-9315_syn_4"
text_4 = """Procedure Note
Patient: [REDACTED]
Attending: Dr. Chen
Steps:
1. GA/Intubation.
2. Navigated to RUL posterior nodule.
3. Confirmed with REBUS and Cone Beam CT.
4. Microwave ablation: 65W for 5 mins.
5. Re-imaged: Good ablation zone.
6. Extubated.
Plan: Admit."""

entities_4 = [
    {"label": "PROC_ACTION",   **get_span(text_4, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL posterior", 1)},
    {"label": "OBS_LESION",    **get_span(text_4, "nodule", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "REBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_4, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION",   **get_span(text_4, "Microwave ablation", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_4, "65W", 1)},
    {"label": "MEAS_TIME",     **get_span(text_4, "5 mins", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 8472-9315_syn_5
# ==========================================
id_5 = "8472-9315_syn_5"
text_5 = """ablation for [REDACTED] today. he has that RUL nodule and cant have surgery. used the superD nav system and the emprint microwave probe. got right to the middle of it checked with the spinny CT. cooked it at 65 watts for 5 mins. temp got up to 85. looks fried on the ultrasound. no bleeding."""

entities_5 = [
    {"label": "PROC_ACTION",   **get_span(text_5, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_5, "nodule", 1)},
    {"label": "PROC_METHOD",   **get_span(text_5, "superD nav system", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_5, "emprint microwave probe", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_5, "65 watts", 1)},
    {"label": "MEAS_TIME",     **get_span(text_5, "5 mins", 1)},
    {"label": "MEAS_TEMP",     **get_span(text_5, "85", 1)},
    {"label": "PROC_METHOD",   **get_span(text_5, "ultrasound", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 8472-9315_syn_6
# ==========================================
id_6 = "8472-9315_syn_6"
text_6 = """Bronchoscopic electromagnetic navigation with microwave ablation of right upper lobe peripheral nodule. 67-year-old gentleman. General anesthesia. Navigation to RUL posterior segment. Radial EBUS and cone-beam CT confirmation. Microwave ablation probe advanced. Ablation 65 watts for 5 minutes. Hyperechoic changes on EBUS. No complications."""

entities_6 = [
    {"label": "PROC_METHOD",   **get_span(text_6, "electromagnetic navigation", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "microwave ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "right upper lobe", 1)},
    {"label": "OBS_LESION",    **get_span(text_6, "nodule", 1)},
    {"label": "PROC_METHOD",   **get_span(text_6, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL posterior segment", 1)},
    {"label": "PROC_METHOD",   **get_span(text_6, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_6, "cone-beam CT", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_6, "Microwave ablation probe", 1)},
    {"label": "PROC_ACTION",   **get_span(text_6, "Ablation", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_6, "65 watts", 1)},
    {"label": "MEAS_TIME",     **get_span(text_6, "5 minutes", 1)},
    {"label": "OBS_FINDING",   **get_span(text_6, "Hyperechoic changes", 1)},
    {"label": "PROC_METHOD",   **get_span(text_6, "EBUS", 2)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 8472-9315_syn_7
# ==========================================
id_7 = "8472-9315_syn_7"
text_7 = """[Indication]
RUL Adenocarcinoma, inoperable.
[Anesthesia]
General.
[Description]
EMN to RUL posterior. Confirmed w/ REBUS/CBCT. Microwave ablation (65W, 5min). Tumor necrosed.
[Plan]
Admit, f/u CT."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_7, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD",   **get_span(text_7, "EMN", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL posterior", 1)},
    {"label": "PROC_METHOD",   **get_span(text_7, "REBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(text_7, "CBCT", 1)},
    {"label": "PROC_ACTION",   **get_span(text_7, "Microwave ablation", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_7, "65W", 1)},
    {"label": "MEAS_TIME",     **get_span(text_7, "5min", 1)},
    {"label": "OBS_LESION",    **get_span(text_7, "Tumor", 1)},
    {"label": "OBS_FINDING",   **get_span(text_7, "necrosed", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 8472-9315_syn_8
# ==========================================
id_8 = "8472-9315_syn_8"
text_8 = """We treated [REDACTED]'s lung cancer today using a microwave ablation catheter. Because of his COPD, surgery wasn't an option. We navigated a small catheter to the tumor in his right upper lobe and confirmed its position with a 3D X-ray spin. We then heated the tumor to 85 degrees Celsius for 5 minutes to kill the cancer cells. The procedure was successful."""

entities_8 = [
    {"label": "DEV_INSTRUMENT",**get_span(text_8, "microwave ablation catheter", 1)},
    {"label": "PROC_ACTION",   **get_span(text_8, "navigated", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_8, "catheter", 2)},
    {"label": "OBS_LESION",    **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right upper lobe", 1)},
    {"label": "MEAS_TEMP",     **get_span(text_8, "85 degrees Celsius", 1)},
    {"label": "MEAS_TIME",     **get_span(text_8, "5 minutes", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 8472-9315_syn_9
# ==========================================
id_9 = "8472-9315_syn_9"
text_9 = """Procedure: Image-guided tumor destruction.
Device: Microwave antenna.
Action: The RUL lesion was accessed via electromagnetic guidance. The probe was inserted and activated (65W). Thermal ablation was performed. 
Result: Coagulative necrosis of the target."""

entities_9 = [
    {"label": "OBS_LESION",    **get_span(text_9, "tumor", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_9, "Microwave antenna", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "OBS_LESION",    **get_span(text_9, "lesion", 1)},
    {"label": "PROC_METHOD",   **get_span(text_9, "electromagnetic guidance", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_9, "probe", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_9, "65W", 1)},
    {"label": "PROC_ACTION",   **get_span(text_9, "Thermal ablation", 1)},
    {"label": "OBS_FINDING",   **get_span(text_9, "Coagulative necrosis", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})


# ==========================================
# Note 10: 8472-9315
# ==========================================
id_10 = "8472-9315"
text_10 = """Patient Name: [REDACTED] Anderson
MRN: [REDACTED]
DOB: [REDACTED] (Age: 67)
Date of Procedure: [REDACTED]
Institution: [REDACTED]
Attending Physician: Dr. Sarah Chen, MD, FCCP
Fellow: Dr. Michael Rodriguez, MD
Anesthesia: Dr. Patricia Williams, MD

PREOPERATIVE DIAGNOSIS:
Right upper lobe pulmonary nodule, 2.3 cm, highly suspicious for primary lung adenocarcinoma. Patient deemed high surgical risk due to severe COPD (FEV1 38% predicted) and coronary artery disease with prior CABG.

POSTOPERATIVE DIAGNOSIS: Same

PROCEDURE PERFORMED:
Bronchoscopic electromagnetic navigation with microwave ablation of right upper lobe peripheral nodule

INDICATION:
67-year-old gentleman with 45 pack-year smoking history presents with incidentally discovered 2.3 cm spiculated nodule in right upper lobe posterior segment. PET-CT demonstrates SUV max 8.4. Transthoracic needle biopsy confirmed adenocarcinoma. Patient evaluated by thoracic surgery but deemed prohibitive surgical risk. Multidisciplinary tumor board recommended bronchoscopic ablation vs SBRT. Patient elected for bronchoscopic microwave ablation after extensive discussion of risks and benefits.

PROCEDURE DETAILS:
After informed consent, patient brought to interventional pulmonology suite. Time-out performed. General anesthesia induced with propofol and rocuronium, patient intubated with 8.5 ETT. Bronchoscope advanced through ETT after securing airway. Initial survey bronchoscopy revealed patent airways without endobronchial lesions. 

Electromagnetic navigation bronchoscopy performed using superDimension system with prior thin-slice CT protocol. Planning software id[REDACTED] target nodule in RUL posterior segment (RB1). Navigation successful with 8 steerable guide sheath advanced to peripheral location. Radial EBUS performed demonstrating target lesion in contact position with characteristic hypoechoic appearance. Target confirmed with cone-beam CT showing guide sheath within 5mm of lesion center.

Extended working channel passed through guide sheath. Microwave ablation probe (Emprint 2.0, 15mm active tip) advanced through EWC to target site. Ablation parameters: 65 watts, 5 minute duration. Temperature monitoring showed gradual rise to 85°C at probe tip. Patient remained hemodynamically stable throughout ablation. Post-ablation radial EBUS demonstrated hyperechoic changes consistent with coagulative necrosis. 

Guide sheath slowly withdrawn under direct visualization. Inspection revealed mild mucosal edema but no active bleeding. Airways suctioned clear. Patient emerged from anesthesia without complications. Extubated in suite and transferred to PACU in stable condition.

ESTIMATED BLOOD LOSS: Minimal
FLUIDS: 800 mL crystalloid
COMPLICATIONS: None
SPECIMENS: None sent

FINDINGS:
1. Successful electromagnetic navigation to RUL posterior segment target
2. Microwave ablation completed per protocol with good real-time monitoring
3. Post-ablation imaging confirms appropriate zone of coagulation

PLAN:
1. Admit for overnight observation
2. Chest CT with contrast in 6 hours to assess for complications
3. Pain control with scheduled acetaminophen and PRN oxycodone
4. Incentive spirometry q2h while awake
5. Follow-up CT chest in 6 weeks to assess treatment response
6. Close PET-CT surveillance at 3, 6, and 12 months

DISPOSITION: Admitted to 7 West pulmonary intermediate care

_________________________________
Sarah Chen, MD, FCCP
Director, Interventional Pulmonology"""

entities_10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Right upper lobe", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "pulmonary nodule", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_10, "2.3 cm", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "lung adenocarcinoma", 1)},
    {"label": "CTX_HISTORICAL",**get_span(text_10, "prior CABG", 1)},
    
    {"label": "PROC_METHOD",   **get_span(text_10, "Bronchoscopic electromagnetic navigation", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "microwave ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right upper lobe", 2)},
    {"label": "OBS_LESION",    **get_span(text_10, "nodule", 2)},
    
    {"label": "MEAS_SIZE",     **get_span(text_10, "2.3 cm", 2)},
    {"label": "OBS_LESION",    **get_span(text_10, "nodule", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "right upper lobe posterior segment", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "PET-CT", 1)},
    {"label": "CTX_HISTORICAL",**get_span(text_10, "Transthoracic needle biopsy", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "adenocarcinoma", 2)},
    {"label": "PROC_ACTION",   **get_span(text_10, "bronchoscopic ablation", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "bronchoscopic microwave ablation", 1)},
    
    {"label": "MEDICATION",    **get_span(text_10, "propofol", 1)},
    {"label": "MEDICATION",    **get_span(text_10, "rocuronium", 1)},
    
    {"label": "PROC_METHOD",   **get_span(text_10, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "superDimension system", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "nodule", 4)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL posterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB1", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "Navigation", 2)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "steerable guide sheath", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "Radial EBUS", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "lesion", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "cone-beam CT", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "guide sheath", 2)},
    {"label": "MEAS_SIZE",     **get_span(text_10, "5mm", 1)},
    {"label": "OBS_LESION",    **get_span(text_10, "lesion", 2)},
    
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "Extended working channel", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "Microwave ablation probe", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "Emprint 2.0", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_10, "15mm", 1)},
    {"label": "PROC_ACTION",   **get_span(text_10, "Ablation", 1)},
    {"label": "MEAS_ENERGY",   **get_span(text_10, "65 watts", 1)},
    {"label": "MEAS_TIME",     **get_span(text_10, "5 minute", 1)},
    {"label": "MEAS_TEMP",     **get_span(text_10, "85°C", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "radial EBUS", 1)},
    {"label": "OBS_FINDING",   **get_span(text_10, "hyperechoic changes", 1)},
    {"label": "OBS_FINDING",   **get_span(text_10, "coagulative necrosis", 1)},
    
    {"label": "DEV_INSTRUMENT",**get_span(text_10, "Guide sheath", 1)},
    {"label": "OBS_FINDING",   **get_span(text_10, "mucosal edema", 1)},
    
    {"label": "PROC_METHOD",   **get_span(text_10, "electromagnetic navigation", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RUL posterior segment", 2)},
    {"label": "PROC_ACTION",   **get_span(text_10, "Microwave ablation", 2)},
    
    {"label": "MEDICATION",    **get_span(text_10, "acetaminophen", 1)},
    {"label": "MEDICATION",    **get_span(text_10, "oxycodone", 1)},
    {"label": "PROC_METHOD",   **get_span(text_10, "PET-CT", 2)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
