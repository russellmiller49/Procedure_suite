import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from a subdirectory)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for local testing or if path needs adjustment
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 4592817_syn_1
# ==========================================
text_1 = """Procedure: Rigid Bronchoscopy, Tumor Ablation.
Indication: Tracheal obstruction (tumor).
Findings: 90% obstruction subglottic.
Action: Rigid scope. Snare resection of polypoid lesions. APC for base/hemostasis.
Result: 90% patent airway.
Plan: Oncology f/u. No stent placed (patient refusal)."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Ablation", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "90% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "subglottic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Rigid scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Snare", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "resection", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "polypoid lesions", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "APC", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "90% patent airway", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4592817_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: Rigid bronchoscopy with mechanical and thermal tumor debulking.
INDICATION: Critical endotracheal obstruction.
FINDINGS: Multiple polypoid lesions in the subglottic trachea causing 90% expiratory obstruction. 
TECHNIQUE: A 10mm rigid tracheoscope was utilized. The flexible scope was introduced through the rigid barrel. Electrocautery snare was used to resect the dominant polypoid masses. Argon Plasma Coagulation (APC) was applied to the tumor base for destruction and hemostasis. Luminal patency was restored to approximately 90%."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "debulking", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "endotracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "polypoid lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "subglottic trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "90% expiratory obstruction", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "10mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "rigid tracheoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "flexible scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "rigid barrel", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Electrocautery snare", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "resect", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "polypoid masses", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Argon Plasma Coagulation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "APC", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_2, "destruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "Luminal patency was restored to approximately 90%", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4592817_syn_3
# ==========================================
text_3 = """CPT 31641: Bronchoscopy with destruction of tumor.
Techniques: Rigid bronchoscopy, Snare electrocautery, Argon Plasma Coagulation (APC).
Site: Trachea (Endotracheal tumor).
Complexity: Debulking of >50 lesions to restore airway."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Snare electrocautery", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Argon Plasma Coagulation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "APC", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Endotracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "Debulking", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "lesions", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4592817_syn_4
# ==========================================
text_4 = """Procedure: Rigid Bronch / Debulking
Patient: [REDACTED]
Attending: Dr. Lee

1. GA / Paralytics.
2. LMA -> Flex scope check: 90% blocked.
3. Rigid scope inserted.
4. Snare used to cut tumors.
5. APC used to burn the rest.
6. Airway open now.
7. Extubated."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "LMA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Flex scope", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_4, "90% blocked", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Snare", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "tumors", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "APC", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "Airway open", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4592817_syn_5
# ==========================================
text_5 = """[REDACTED] rigid bronch. dr lee attending. guy had a huge tumor in his trachea blocking 90 percent. we went in with the rigid scope. used the snare to chop off the big pieces. then apc to burn the rest. got it open pretty good. he didn't want a stent so we didn't put one in. hopefully chemo works."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "rigid bronch", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "blocking 90 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "rigid scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "snare", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "apc", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "stent", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4592817_syn_6
# ==========================================
text_6 = """Rigid bronchoscopy performed for symptomatic tracheal tumor. Visualization showed 90% obstruction by polypoid masses. Mechanical debulking performed via snare cautery followed by APC for residual tissue and hemostasis. Airway patency restored to near normal. No stent placed per patient preference. Complications: None."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Rigid bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "90% obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "polypoid masses", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "snare cautery", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "APC", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "Airway patency restored to near normal", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "stent", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4592817_syn_7
# ==========================================
text_7 = """[Indication]
Tracheal tumor, obstruction.
[Anesthesia]
General (Rigid).
[Description]
Rigid bronchoscopy. Snare resection of polyps. APC ablation.
[Result]
Airway recanalized (90% open).
[Plan]
Oncology for chemo/radiation."""

entities_7 = [
    {"label": "ANAT_AIRWAY", **get_span(text_7, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Snare", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "resection", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "polyps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "ablation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "Airway recanalized (90% open)", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4592817_syn_8
# ==========================================
text_8 = """[REDACTED] to the OR for management of his tracheal tumor. We found the airway was 90% blocked by growths. We used a rigid bronchoscope to control the airway and then used a snare to cut away the large tumors. We cleaned up the base of the tumors with argon plasma coagulation. By the end, his airway was wide open. He had refused a stent, so we rely on his chemotherapy to prevent regrowth."""

entities_8 = [
    {"label": "ANAT_AIRWAY", **get_span(text_8, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "90% blocked", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "growths", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "rigid bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "snare", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumors", 2)},
    {"label": "PROC_METHOD", **get_span(text_8, "argon plasma coagulation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "airway was wide open", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "stent", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4592817_syn_9
# ==========================================
text_9 = """Procedure: Rigid endoscopy with tumor destruction (31641).
Target: Endotracheal neoplasm.
Action: Mechanical resection (snare) and thermal ablation (APC).
Outcome: Recanalization of airway."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Rigid endoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "destruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "Endotracheal", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "neoplasm", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "resection", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "snare", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "APC", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "Recanalization of airway", 1)},
]

BATCH_DATA.append({"id": "4592817_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4592817
# ==========================================
text_10 = """**PATIENT INFORMATION:**
- Name: James Rodriguez
- MRN: [REDACTED]
- DOB: [REDACTED]
- Date of Procedure: [REDACTED]
- Procedure Time: 09:15-09:40

**INSTITUTION:[REDACTED]

**ATTENDING PHYSICIAN:** Dr. Patricia Nguyen, MD (Interventional Pulmonology)

**INDICATION:**
54-year-old male with history of cirrhosis (MELD 18) presenting with recurrent hepatic hydrothorax. Right-sided pleural effusion causing moderate dyspnea.

**PRE-PROCEDURE:**
- Informed consent obtained with discussion of increased bleeding risk due to thrombocytopenia (platelets 68K) and coagulopathy (INR 1.7)
- Timeout performed
- Point-of-care ultrasound revealed right pleural effusion, maximum depth 6.5 cm
- Labs reviewed: Platelets 68K, INR 1.7, Creatinine 1.2
- Vital signs: BP 118/72, HR 76, SpO2 91% on 2L NC

**PROCEDURE DETAILS:**
- Patient positioned sitting, leaning forward
- Right lateral chest, 7th intercosal space, posterior axillary line
- Chlorhexidine skin prep
- Local anesthesia: 12 mL of 1% lidocaine
- Ultrasound-guided insertion of 8-French catheter system
- Initial fluid: transudative appearance, clear yellow
- Volume removed: 800 mL (stopped due to concern for re-expansion pulmonary edema)
- Drainage rate kept slow (less than 1000 mL/hour)
- Post-procedure ultrasound: no pneumothorax

**SPECIMENS SENT:**
- Pleural fluid analysis (cell count, protein, LDH, albumin)
- Pleural fluid culture

**IMMEDIATE RESULTS:**
- Appearance: Clear, yellow, transudative
- Estimated protein <2.5 g/dL based on appearance

**POST-PROCEDURE:**
- Procedure well tolerated
- No immediate complications
- Vital signs: BP 122/74, HR 78, SpO2 94% on 2L NC
- Patient reports significant improvement in breathing

**COMPLICATIONS:** None

**ASSESSMENT:** Successful therapeutic thoracentesis of recurrent hepatic hydrothorax. Limited drainage to 800 mL to minimize risk of complications given underlying coagulopathy and hepatic disease.

**PLAN:**
- Continue diuretic optimization
- Discuss with hepatology regarding TIPS evaluation
- Consider repeat thoracentesis vs IPC if rapid reaccumulation
- Sodium restriction and fluid management"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "hepatic hydrothorax", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right-sided", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ultrasound", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 2)},
    {"label": "MEAS_SIZE", **get_span(text_10, "6.5 cm", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "lateral chest", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "7th intercosal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "posterior axillary line", 1)},
    {"label": "MEDICATION", **get_span(text_10, "1% lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound-guided", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "8-French", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "catheter system", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "transudative", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "clear yellow", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "800 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Pleural fluid", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Pleural fluid", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "Clear, yellow", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "transudative", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "thoracentesis", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "hepatic hydrothorax", 2)},
    {"label": "MEDICATION", **get_span(text_10, "diuretic", 1)},
]

BATCH_DATA.append({"id": "4592817", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)