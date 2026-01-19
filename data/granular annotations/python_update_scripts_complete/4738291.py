import sys
from pathlib import Path

# Set up the repository root path
# Assumes this script is running within the structure: repo_root/scripts/your_script.py
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for different directory structures or if the path adjustment above wasn't sufficient
    # Attempting to assume standard structure if previous import failed, though strict adherence to the 
    # specific provided broken script suggests focusing on the content error.
    # However, correcting the path depth is often required in these debug tasks.
    # Given the file path data/granular annotations/Python_update_scripts/4738291.py
    # Depth is 4 levels deep relative to repo root if 'scripts' is at the top.
    pass 

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
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 4783621_syn_1
# ==========================================
text_1 = """Indication: Airway obstruction, squamous cell CA.
Proc: Rigid bronch, mechanical debridement, APC, stent.
Steps:
- Rigid scope inserted.
- 90% obstruction LMS visualized.
- Tumor cored/debrided (15cc).
- Base cauterized (APC/Bovie).
- 14x60mm Dumon stent placed.
- Final: Patent lumen, no bleeding.
Plan: ICU, surveillance bronch."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Airway obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "squamous cell CA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Rigid bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "mechanical debridement", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "APC", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Rigid scope", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "90% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "cored", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "debrided", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "15cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "cauterized", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "APC", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bovie", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_1, "14x60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "Dumon stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "Patent lumen", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no bleeding", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 4783621_syn_2
# ==========================================
text_2 = """HISTORY: The patient, a 72-year-old female with advanced squamous cell carcinoma, presented with critical central airway obstruction. 
PROCEDURE: Under general anesthesia with jet ventilation, the airway was accessed via a 14mm rigid bronchoscope. Significant endobronchial tumor burden was id[REDACTED] in the left mainstem bronchus. Multimodal recanalization was performed utilizing mechanical coring, electrocautery, and argon plasma coagulation, resulting in restoration of patency. To maintain airway caliber, a 14x60mm silicone stent was deployed. 
CONCLUSION: Successful rigid bronchoscopy with tumor destruction and stent placement."""

entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "squamous cell carcinoma", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "central airway obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "jet ventilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "rigid bronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "left mainstem bronchus", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "mechanical coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "electrocautery", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "argon plasma coagulation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_2, "14x60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "silicone stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "stent placement", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 4783621_syn_3
# ==========================================
text_3 = """Procedures Performed:
- 31640: Rigid bronchoscopy with excision of tumor (Mechanical debulking of LMS).
- 31641: Destruction of tumor (APC/Cautery).
- 31636: Stent placement (Revision/Placement of bronchial stent).
Medical Necessity: Critical airway obstruction (90% LMS stenosis).
Technique: Rigid barrel used for coring; stent deployed under direct vision. Hemostasis achieved."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "excision of tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Mechanical debulking", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Destruction of tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Cautery", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Stent placement", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "bronchial stent", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "airway obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "90% LMS stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Rigid barrel", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "coring", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "stent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3, "Hemostasis achieved", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 4783621_syn_4
# ==========================================
text_4 = """Procedure Note
Patient: [REDACTED]
Attending: Dr. Anderson
Diagnosis: Malignant Airway Obstruction
Steps:
1. Time out done. GA induced.
2. Rigid scope to trachea.
3. LMS 90% blocked by tumor.
4. Mechanical debulking and APC used to clear airway.
5. Silicone stent (14x60) placed in LMS.
6. Airway patent at end of case.
Plan: ICU for monitoring."""

entities_4 = [
    {"label": "OBS_LESION", **get_span(text_4, "Malignant Airway Obstruction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "LMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_4, "90% blocked", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Mechanical debulking", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "APC", 1)},
    {"label": "DEV_STENT", **get_span(text_4, "Silicone stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_4, "14x60", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "LMS", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "Airway patent", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 4783621_syn_5
# ==========================================
text_5 = """procedure note for ms [REDACTED] she has the squamous cell ca with stridor we did the rigid bronch today anesthesia gave the propofol. went down with the 14mm scope left main was tight like 90 percent blocked. used the coring technique and some apc to burn the base got it open pretty good. put a dumon stent in there 14 by 60 fits nice. no bleeding stopped with epi. woke up fine sent to recovery."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "squamous cell ca", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_5, "stridor", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "rigid bronch", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "left main", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "90 percent blocked", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "apc", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "dumon stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_5, "14 by 60", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no bleeding", 1)},
    {"label": "MEDICATION", **get_span(text_5, "epi", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 4783621_syn_6
# ==========================================
text_6 = """[REDACTED] a 72-year-old female with known squamous cell lung cancer presenting with worsening dyspnea and stridor. CT chest shows near-complete obstruction of the left mainstem bronchus by endobronchial tumor. A rigid bronchoscope (14mm) was introduced via the mouth under direct visualization. High-frequency jet ventilation (HFJV) was utilized. Left mainstem was 90% obstructed by friable, hemorrhagic endobronchial tumor. The tumor was cored using the rigid bronchoscope with mechanical debridement. Residual tumor base was treated with electrocautery and Argon Plasma Coagulation. A 14mm x 60mm Dumon silicone stent was deployed in the left mainstem bronchus. Prior to treatment, left mainstem bronchus was 10% patent. After treatment, the airway was 70% patent."""

entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "squamous cell lung cancer", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_6, "dyspnea", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_6, "stridor", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "left mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "endobronchial tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "rigid bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "14mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "High-frequency jet ventilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Left mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "90% obstructed", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "endobronchial tumor", 2)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "cored", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "rigid bronchoscope", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "mechanical debridement", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "electrocautery", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Argon Plasma Coagulation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_6, "14mm x 60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "Dumon silicone stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "left mainstem bronchus", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "left mainstem bronchus", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "10% patent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "70% patent", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 4783621_syn_7
# ==========================================
text_7 = """[Indication]
Symptomatic malignant airway obstruction, LMS.
[Anesthesia]
General, TIVA, Jet Ventilation.
[Description]
Rigid bronchoscopy performed. 90% obstruction of LMS id[REDACTED]. Mechanical debridement and APC destruction performed. 14x60mm silicone stent placed. Airway patency restored to 70%.
[Plan]
ICU admission. Follow-up bronchoscopy 4 weeks."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "malignant airway obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "LMS", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Jet Ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Rigid bronchoscopy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "90% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "LMS", 2)},
    {"label": "PROC_ACTION", **get_span(text_7, "Mechanical debridement", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "APC destruction", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_7, "14x60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "silicone stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "70%", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 4783621_syn_8
# ==========================================
text_8 = """The patient was brought to the operating room for management of her malignant airway obstruction. After induction of general anesthesia, we inserted the rigid bronchoscope. The left mainstem bronchus was found to be critically narrowed by tumor. We proceeded to core out the tumor mechanically and applied thermal energy to the base to prevent regrowth and bleeding. Once the airway was opened, we sized and placed a silicone stent to ensure it remained patent. The patient tolerated the procedure well and was transferred to the ICU."""

entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "malignant airway obstruction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "left mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "core out", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_8, "applied thermal energy", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "silicone stent", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 4783621_syn_9
# ==========================================
text_9 = """Operation: Rigid endoscopy with tumor eradication and stent insertion.
Context: Critical blockage of the left bronchial tube.
Action: The rigid barrel was navigated to the obstruction. The malignancy was excised mechanically and ablated with argon plasma. A silicone prosthesis was positioned to scaffold the airway.
Result: The bronchial lumen was re-established. Hemostasis was secured."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Rigid endoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "tumor eradication", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "stent insertion", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "blockage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "left bronchial tube", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "rigid barrel", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "malignancy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "excised", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "ablated", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "argon plasma", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "silicone prosthesis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "bronchial lumen was re-established", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "Hemostasis was secured", 1)},
]
BATCH_DATA.append({"id": "4783621_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# Note 10: 4783621
# ==========================================
text_10 = """PATIENT: [REDACTED], 72-year-old Female
MRN: [REDACTED]
INDICATION FOR OPERATION: Ms. [REDACTED] is a 72-year-old female with known squamous cell lung cancer presenting with worsening dyspnea and stridor. CT chest shows near-complete obstruction of the left mainstem bronchus by endobronchial tumor. The nature, purpose, risks, benefits and alternatives to therapeutic bronchoscopy were discussed with the patient in detail. Patient indicated a wish to proceed and informed consent was signed.
PREOPERATIVE DIAGNOSIS: Left mainstem bronchus obstruction secondary to endobronchial tumor
POSTOPERATIVE DIAGNOSIS: Same
PROCEDURE: Rigid Bronchoscopy, Endobronchial Tumor Destruction (CPT 31641), Mechanical Tumor Debridement (CPT 31640), Airway Stent Placement (CPT 31631)
ATTENDING: Dr. Michael Anderson
ASSISTANT: Dr. Sarah Kim, Fellow
Support Staff:

RN: Robert Martinez
RT: Lisa Johnson
Anesthesia: Dr. Thomas Wright

ANESTHESIA: General anesthesia with TIVA
MONITORING: Standard ASA monitoring with arterial line
INSTRUMENT: Storz rigid bronchoscope (14mm), Olympus flexible bronchoscope, Electrocautery (Bovie), APC probe, mechanical debrider, 14mm x 60mm silicone stent (Dumon)
ESTIMATED BLOOD LOSS: 150 mL
COMPLICATIONS: None
PROCEDURE IN DETAIL:
After induction of general anesthesia, a timeout was performed. All procedure related images were saved and archived.
PATIENT [REDACTED]: Supine with shoulder roll
A rigid bronchoscope (14mm) was introduced via the mouth under direct visualization. High-frequency jet ventilation (HFJV) was utilized. A complete airway survey was performed.
Initial Findings:

Trachea: Patent, no lesions
Right mainstem: Patent, mucosa normal
Left mainstem: 90% obstructed by friable, hemorrhagic endobronchial tumor starting 1cm distal to the carina and extending 3cm distally

Therapeutic Interventions:
1. Mechanical Debridement: The tumor was cored using the rigid bronchoscope with mechanical debridement. Multiple passes were required to remove bulk tumor. Estimated tumor volume removed: 15cc.
2. Electrocautery: Residual tumor base was treated with electrocautery at 40 watts in coagulation mode. Total treatment time: 3 minutes. FiO2 maintained at 40% during cautery.
3. Argon Plasma Coagulation: APC was applied to residual tumor at 40 watts, argon flow 1.5 L/min. Treatment applied circumferentially to tumor base. Duration: 2 minutes.
Results: Prior to treatment, left mainstem bronchus was 10% patent. After treatment, the airway was 70% patent.
4. Stent Placement: Due to significant malacia and risk of re-obstruction, a 14mm x 60mm Dumon silicone stent was deployed in the left mainstem bronchus under direct visualization and fluoroscopic guidance. Stent [REDACTED] confirmed endoscopically with good apposition to airway wall.
Hemostasis was confirmed with minimal oozing controlled with topical epinephrine (1:10,000 dilution, 10mL instilled). A flexible bronchoscope was passed through the rigid barrel for final inspection showing:

Patent stent lumen
Visible LUL and LLL orifices through stent
No significant bleeding

The bronchoscope and adjunct instruments were withdrawn. The patient tolerated the procedure well without immediate complications.
SPECIMEN(S):

Endobronchial tumor debridement (histology)

IMPRESSION/PLAN: Ms. [REDACTED] is a 72-year-old female with squamous cell lung cancer and critical left mainstem obstruction. Successful therapeutic bronchoscopy with tumor debridement, cautery, APC, and stent placement. Airway patency improved from 10% to 70%. Patient will require surveillance bronchoscopy in 4-6 weeks. Oncology to follow for systemic therapy planning."""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "squamous cell lung cancer", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "dyspnea", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "stridor", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Left mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "obstruction", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Endobronchial Tumor Destruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Mechanical Tumor Debridement", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Airway Stent Placement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Storz rigid bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Olympus flexible bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Electrocautery", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Bovie", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "APC probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "mechanical debrider", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_10, "14mm x 60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "silicone stent", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "Dumon", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "High-frequency jet ventilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Right mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Left mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "90% obstructed", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial tumor", 3)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Mechanical Debridement", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "cored", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid bronchoscope", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "mechanical debridement", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 4)},
    {"label": "MEAS_VOL", **get_span(text_10, "15cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Electrocautery", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 5)},
    {"label": "PROC_ACTION", **get_span(text_10, "electrocautery", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_10, "40 watts", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "3 minutes", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Argon Plasma Coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "APC", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 6)},
    {"label": "MEAS_ENERGY", **get_span(text_10, "40 watts", 2)},
    {"label": "MEAS_TIME", **get_span(text_10, "2 minutes", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem bronchus", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "10% patent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "70% patent", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Stent Placement", 2)},
    {"label": "DEV_STENT_SIZE", **get_span(text_10, "14mm x 60mm", 2)},
    {"label": "DEV_STENT", **get_span(text_10, "Dumon silicone stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem bronchus", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "minimal oozing", 1)},
    {"label": "MEDICATION", **get_span(text_10, "epinephrine", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "flexible bronchoscope", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid barrel", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "Patent stent lumen", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Endobronchial tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "squamous cell lung cancer", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "obstruction", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "therapeutic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "tumor debridement", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "cautery", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "APC", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "stent placement", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "10%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "70%", 2)},
]
BATCH_DATA.append({"id": "4783621", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)
    print("Batch processing complete.")