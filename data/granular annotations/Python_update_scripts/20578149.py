import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
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

# ==========================================
# 3. Data Payload (Batch)
# ==========================================
BATCH_DATA = []

# -----------------------------------------------------------------------------
# Case 1: 20578149_syn_1
# -----------------------------------------------------------------------------
t1 = """Indication: Malignant airway obstruction (Esophageal CA).
Findings: Distal trachea 20% patent. LMS 100% occluded. RMS 30% patent.
Procedure: Rigid bronchoscopy.
- Tumor debulking (APC/Cryo).
- Silicone Y-Stent (15x12x12) placed.
Result: Airways 90% patent through stent."""

e1 = [
    {"label": "OBS_LESION",                 **get_span(t1, "Malignant airway obstruction", 1)},
    {"label": "OBS_LESION",                 **get_span(t1, "Esophageal CA", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t1, "Distal trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t1, "20% patent", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t1, "LMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t1, "100% occluded", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t1, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t1, "30% patent", 1)},
    {"label": "PROC_METHOD",                **get_span(t1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t1, "Tumor debulking", 1)},
    {"label": "PROC_METHOD",                **get_span(t1, "APC", 1)},
    {"label": "PROC_METHOD",                **get_span(t1, "Cryo", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t1, "Silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t1, "Y-Stent", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t1, "15x12x12", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t1, "Airways", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t1, "90% patent", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_1", "text": t1, "entities": e1})

# -----------------------------------------------------------------------------
# Case 2: 20578149_syn_2
# -----------------------------------------------------------------------------
t2 = """OPERATIVE NARRATIVE: The patient presented with critical malignant central airway obstruction. Rigid bronchoscopy was initiated. Extensive tumor infiltration was noted at the carina, completely occluding the Left Mainstem (LMS). Mechanical debulking and APC were utilized to re-establish a lumen. A customized 15x12x12mm silicone Y-stent was deployed to scaffold the airway. Post-deployment, the trachea and both mainstems demonstrated >90% patency."""

e2 = [
    {"label": "OBS_LESION",                 **get_span(t2, "malignant central airway obstruction", 1)},
    {"label": "PROC_METHOD",                **get_span(t2, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION",                 **get_span(t2, "tumor infiltration", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "carina", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t2, "completely occluding", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "Left Mainstem", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "LMS", 1)},
    {"label": "PROC_ACTION",                **get_span(t2, "Mechanical debulking", 1)},
    {"label": "PROC_METHOD",                **get_span(t2, "APC", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t2, "15x12x12mm", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t2, "silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t2, "Y-stent", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "airway", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "trachea", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "mainstems", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t2, ">90% patency", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_2", "text": t2, "entities": e2})

# -----------------------------------------------------------------------------
# Case 3: 20578149_syn_3
# -----------------------------------------------------------------------------
t3 = """Codes: 
- 31636 (Stent placement, bronchial)
- 31641 (Tumor destruction/debulking)
Rationale: Critical obstruction required mechanical debulking prior to stent placement. A silicone Y-stent was placed covering the trachea and both mainstems."""

e3 = [
    {"label": "PROC_ACTION",                **get_span(t3, "Stent placement", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t3, "bronchial", 1)},
    {"label": "PROC_ACTION",                **get_span(t3, "Tumor destruction/debulking", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t3, "Critical obstruction", 1)},
    {"label": "PROC_ACTION",                **get_span(t3, "mechanical debulking", 1)},
    {"label": "PROC_ACTION",                **get_span(t3, "stent placement", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t3, "silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t3, "Y-stent", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t3, "trachea", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t3, "mainstems", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_3", "text": t3, "entities": e3})

# -----------------------------------------------------------------------------
# Case 4: 20578149_syn_4
# -----------------------------------------------------------------------------
t4 = """Procedure: Rigid Bronch + Y-Stent
Pt: [REDACTED]
Steps:
1. 12mm Rigid scope inserted.
2. Tumor debulked with APC and suction.
3. Measured for Y-stent.
4. Inserted silicone Y-stent (blind pass technique).
5. Adjusted with forceps.
6. Airway open now.
Plan: ICU, humidified air."""

e4 = [
    {"label": "PROC_METHOD",                **get_span(t4, "Rigid Bronch", 1)},
    {"label": "DEV_STENT",                  **get_span(t4, "Y-Stent", 1)},
    {"label": "MEAS_SIZE",                  **get_span(t4, "12mm", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t4, "Rigid scope", 1)},
    {"label": "OBS_LESION",                 **get_span(t4, "Tumor", 1)},
    {"label": "PROC_ACTION",                **get_span(t4, "debulked", 1)},
    {"label": "PROC_METHOD",                **get_span(t4, "APC", 1)},
    {"label": "DEV_STENT",                  **get_span(t4, "Y-stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t4, "silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t4, "Y-stent", 2)},
    {"label": "DEV_INSTRUMENT",             **get_span(t4, "forceps", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t4, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t4, "open now", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_4", "text": t4, "entities": e4})

# -----------------------------------------------------------------------------
# Case 5: 20578149_syn_5
# -----------------------------------------------------------------------------
t5 = """Ethan Calder with the esophageal cancer compressing the airway. We took him to the OR for a stent. Rigid scope went in. Debulked a lot of tumor at the carina left side was totally shut. Put in a Y stent silicone type. Had to push it past cords blindly then grab it with forceps. It sat perfectly. Airways look great now. ICU for monitoring."""

e5 = [
    {"label": "OBS_LESION",                 **get_span(t5, "esophageal cancer", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t5, "airway", 1)},
    {"label": "DEV_STENT",                  **get_span(t5, "stent", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t5, "Rigid scope", 1)},
    {"label": "PROC_ACTION",                **get_span(t5, "Debulked", 1)},
    {"label": "OBS_LESION",                 **get_span(t5, "tumor", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t5, "carina", 1)},
    {"label": "LATERALITY",                 **get_span(t5, "left side", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t5, "totally shut", 1)},
    {"label": "DEV_STENT",                  **get_span(t5, "Y stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t5, "silicone", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t5, "cords", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t5, "forceps", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t5, "Airways", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t5, "look great now", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_5", "text": t5, "entities": e5})

# -----------------------------------------------------------------------------
# Case 6: 20578149_syn_6
# -----------------------------------------------------------------------------
t6 = """Rigid bronchoscopy with tumor debulking and silicone Y-stent placement. Significant malignant obstruction of the distal trachea and mainstem bronchi was id[REDACTED]. Tumor was debulked using APC and cryotherapy. A 15x12x12 silicone Y-stent was customized and deployed. Post-procedure inspection confirmed excellent stent position and patency of bilateral mainstems."""

e6 = [
    {"label": "PROC_METHOD",                **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t6, "tumor debulking", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t6, "silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t6, "Y-stent", 1)},
    {"label": "OBS_LESION",                 **get_span(t6, "malignant obstruction", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t6, "distal trachea", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t6, "mainstem bronchi", 1)},
    {"label": "OBS_LESION",                 **get_span(t6, "Tumor", 1)},
    {"label": "PROC_ACTION",                **get_span(t6, "debulked", 1)}, # Corrected from 2 to 1 (first occurrence of 'debulked', 'debulking' is different)
    {"label": "PROC_METHOD",                **get_span(t6, "APC", 1)},
    {"label": "PROC_METHOD",                **get_span(t6, "cryotherapy", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t6, "15x12x12", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t6, "silicone", 2)},
    {"label": "DEV_STENT",                  **get_span(t6, "Y-stent", 2)},
    {"label": "DEV_STENT",                  **get_span(t6, "stent", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t6, "patency", 1)},
    {"label": "LATERALITY",                 **get_span(t6, "bilateral", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t6, "mainstems", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_6", "text": t6, "entities": e6})

# -----------------------------------------------------------------------------
# Case 7: 20578149_syn_7
# -----------------------------------------------------------------------------
t7 = """[Indication]
Malignant Central Airway Obstruction.
[Anesthesia]
General, Jet Ventilation.
[Description]
Rigid bronchoscopy. Tumor debulked (APC/Cryo). Silicone Y-Stent placed. Patency restored to >90%.
[Plan]
ICU, Saline nebs."""

e7 = [
    {"label": "OBS_LESION",                 **get_span(t7, "Malignant Central Airway Obstruction", 1)},
    {"label": "PROC_METHOD",                **get_span(t7, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION",                 **get_span(t7, "Tumor", 1)},
    {"label": "PROC_ACTION",                **get_span(t7, "debulked", 1)},
    {"label": "PROC_METHOD",                **get_span(t7, "APC", 1)},
    {"label": "PROC_METHOD",                **get_span(t7, "Cryo", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t7, "Silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t7, "Y-Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t7, "Patency restored to >90%", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_7", "text": t7, "entities": e7})

# -----------------------------------------------------------------------------
# Case 8: 20578149_syn_8
# -----------------------------------------------------------------------------
t8 = """[REDACTED] from severe difficulty breathing due to a tumor blocking his main airways. We performed a rigid bronchoscopy to clear the blockage. After removing a significant amount of tumor tissue using heat and freezing probes, we placed a Y-shaped silicone stent. This stent props open his windpipe and branches to both lungs. We were very pleased to see his airways were 90% open after the stent was in place."""

e8 = [
    {"label": "OBS_LESION",                 **get_span(t8, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t8, "blocking", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t8, "main airways", 1)},
    {"label": "PROC_METHOD",                **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t8, "removing", 1)},
    {"label": "OBS_LESION",                 **get_span(t8, "tumor tissue", 1)},
    {"label": "PROC_METHOD",                **get_span(t8, "heat", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t8, "freezing probes", 1)},
    {"label": "DEV_STENT",                  **get_span(t8, "Y-shaped", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t8, "silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t8, "stent", 1)},
    {"label": "DEV_STENT",                  **get_span(t8, "stent", 2)},
    {"label": "ANAT_AIRWAY",                **get_span(t8, "windpipe", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t8, "airways", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t8, "90% open", 1)},
    {"label": "DEV_STENT",                  **get_span(t8, "stent", 3)},
]
BATCH_DATA.append({"id": "20578149_syn_8", "text": t8, "entities": e8})

# -----------------------------------------------------------------------------
# Case 9: 20578149_syn_9
# -----------------------------------------------------------------------------
t9 = """Procedure: Rigid endoscopy with tumor ablation and prosthetic scaffolding.
Problem: Carinal neoplastic infiltration.
Action: Tissue was excised. A bifurcated silicone prosthesis was inserted.
Result: Luminal integrity restored."""

e9 = [
    {"label": "PROC_METHOD",                **get_span(t9, "Rigid endoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t9, "tumor ablation", 1)},
    {"label": "DEV_STENT",                  **get_span(t9, "prosthetic scaffolding", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t9, "Carinal", 1)},
    {"label": "OBS_LESION",                 **get_span(t9, "neoplastic infiltration", 1)},
    {"label": "OBS_LESION",                 **get_span(t9, "Tissue", 1)},
    {"label": "PROC_ACTION",                **get_span(t9, "excised", 1)},
    {"label": "DEV_STENT",                  **get_span(t9, "bifurcated", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t9, "silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t9, "prosthesis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t9, "Luminal integrity restored", 1)},
]
BATCH_DATA.append({"id": "20578149_syn_9", "text": t9, "entities": e9})

# -----------------------------------------------------------------------------
# Case 10: 20578149
# -----------------------------------------------------------------------------
t10 = """DATE OF PROCEDURE: [REDACTED]
Patient name: [REDACTED]RN: [REDACTED]
PREOPERATIVE DIAGNOSIS: Malignant central airway obstruction.  
POSTOPERATIVE DIAGNOSIS: Resolved airway obstruction s/p silicone Y-stent
PROCEDURE PERFORMED: Rigid bronchoscopy with tumor debulking and silicone tracheobronchial Y- stent placement 
SURGEON: Russell Miller, MD
INDICATIONS: Airway obstruction
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives. The patient’s family acknowledged and gave consent.
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room. After administration of sedatives the a14mm ventilating rigid bronchoscope insertion was attempted. Due to poor mouth opening and glottic irregularities (related to previous head and neck radiation) we were unable to pass the large rigid bronchoscope through the cords and has to convert to a 12mm rigid ventilating bronchoscope which was advanced past the vocal cords into the mid trachea and connected to jet ventilator. Unfortunately due to a combination of extremely poor dentition and poor mouth opening two teeth were lost during the intubation procedure.  Airway inspection was performed using the T190 therapeutic flexible bronchoscope. The upper trachea was normal. The mid trachea had friable tumor mostly at the right lateral wall causing about 30% airway obstruction. The distal trachea had extensive tumor involving both mainstem with carinal tumor infiltration as well. The distal trachea was about 20% patient. The left mainstem was completely occluded and the right mainstem was 30% patent.  It appeared that intrinsic tumor ingrowth was the predominant issue will only mild extrinsic compression. Tumor debulking  was performed using APC to  “burn and shave” the tumor within the trachea and proximal bilateral mainstem along with cryotherapy to remove loose debris and blood clots.
Once we were able to bypass the central tumor the left mainstem tumor only extended about 1cm pass the main carina and the distal left mainstem and left sided bronchi were normal and fully patent. The right mainstem involvement also limited to the first cm pass the main carina. There was non-obstructive tumor infiltration in the posterior segment of the right upper lobe but the right sided airways were otherwise uninvolved. 
After measuring the airways we customized a 15x12x12 silicone Y-stent to a length of 65mm in the tracheal limb, 17.5 mm in the right mainstem limb and 40mm in the left mainstem limb. The rigid bronchoscope was then removed as the stent was too large to insert through the rigid and using Fritag forceps along with a bougie inserted into the left limb we were able to blindly pass the stent through the vocal cords into the trachea. The rigid bronchoscope was then re-inserted. Through the use of rigid forceps, and manipulation with the tip of the flexible bronchoscope we were eventually able to seed the stent into proper position. Post-insertion the trachea, right mainstem and left mainstem were all at least 90% patent. We then removed the rigid bronchoscope turned over the case to anesthesia for recovery. 

Recommendations:
-          Transfer back to ICU
-          Post-procedure x-ray
-          Start 3% saline nebs 4cc 3 times daily for stent maintenance.
-          Ensure supplemental oxygen is humidified
-          Please arrange for patient to have nebulizer at home for continued hypertonic saline nebs post-discharge.
-	If invasive ventilatory support is required blind intubation (direct laryngoscopy, glidescope) should be avoided as it can result in dislodgment of the tracheal stent and potential catastrophic airway obstruction.  Intubation should be performed with a 7.0 or smaller ETT with bronchoscopic insertion to visualize the distal tip of the endotracheal tube. The endotracheal tube should be advanced approximately 3 cm into the tracheal limb of the stent and secured.	

Maya Ellington MD
Interventional Pulmonology 
University Medical Center Los Angeles"""

e10 = [
    {"label": "OBS_LESION",                 **get_span(t10, "Malignant central airway obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t10, "Resolved airway obstruction", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t10, "silicone", 1)},
    {"label": "DEV_STENT",                  **get_span(t10, "Y-stent", 1)},
    {"label": "PROC_METHOD",                **get_span(t10, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t10, "tumor debulking", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t10, "silicone", 2)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "tracheobronchial", 1)},
    {"label": "DEV_STENT",                  **get_span(t10, "Y- stent", 1)},
    {"label": "OBS_LESION",                 **get_span(t10, "Airway obstruction", 1)},
    {"label": "MEAS_SIZE",                  **get_span(t10, "14mm", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "ventilating rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "cords", 1)},
    {"label": "MEAS_SIZE",                  **get_span(t10, "12mm", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "rigid ventilating bronchoscope", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "vocal cords", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "mid trachea", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "T190 therapeutic flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "upper trachea", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "mid trachea", 2)},
    {"label": "OBS_LESION",                 **get_span(t10, "tumor", 2)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "right lateral wall", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t10, "30% airway obstruction", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "distal trachea", 1)},
    {"label": "OBS_LESION",                 **get_span(t10, "tumor", 3)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "mainstem", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "carinal", 1)},
    {"label": "OBS_LESION",                 **get_span(t10, "tumor infiltration", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "distal trachea", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t10, "20% patient", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "left mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t10, "completely occluded", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "right mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t10, "30% patent", 1)},
    {"label": "OBS_LESION",                 **get_span(t10, "tumor ingrowth", 1)},
    {"label": "PROC_ACTION",                **get_span(t10, "Tumor debulking", 1)},
    {"label": "PROC_METHOD",                **get_span(t10, "APC", 1)},
    {"label": "PROC_ACTION",                **get_span(t10, "burn and shave", 1)},
    {"label": "OBS_LESION",                 **get_span(t10, "tumor", 4)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "trachea", 3)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "proximal bilateral mainstem", 1)},
    {"label": "PROC_METHOD",                **get_span(t10, "cryotherapy", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "left mainstem", 2)},
    {"label": "OBS_LESION",                 **get_span(t10, "tumor", 5)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "main carina", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "distal left mainstem", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "right mainstem", 2)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "main carina", 2)},
    {"label": "OBS_LESION",                 **get_span(t10, "tumor infiltration", 2)},
    {"label": "ANAT_LUNG_LOC",             **get_span(t10, "right upper lobe", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t10, "15x12x12", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t10, "silicone", 3)},
    {"label": "DEV_STENT",                  **get_span(t10, "Y-stent", 2)},
    {"label": "DEV_STENT_SIZE",             **get_span(t10, "65mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "tracheal limb", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t10, "17.5 mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "right mainstem limb", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t10, "40mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "left mainstem limb", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "rigid bronchoscope", 1)},
    {"label": "DEV_STENT",                  **get_span(t10, "stent", 3)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "Fritag forceps", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "bougie", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "left limb", 1)},
    {"label": "DEV_STENT",                  **get_span(t10, "stent", 4)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "vocal cords", 2)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "trachea", 4)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "rigid bronchoscope", 2)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "rigid forceps", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "flexible bronchoscope", 1)},
    {"label": "DEV_STENT",                  **get_span(t10, "stent", 5)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "trachea", 5)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "right mainstem", 3)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "left mainstem", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t10, "90% patent", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "rigid bronchoscope", 3)},
    {"label": "DEV_STENT",                  **get_span(t10, "tracheal stent", 1)},
    {"label": "MEAS_SIZE",                  **get_span(t10, "7.0", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t10, "ETT", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "tracheal limb", 2)},
    {"label": "DEV_STENT",                  **get_span(t10, "stent", 7)},
]
BATCH_DATA.append({"id": "20578149", "text": t10, "entities": e10})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)