import sys
from pathlib import Path

# Set up the repository root (assuming script is run from inside the repo)
# Adjust as needed if the script location changes.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure you are running this script from the correct repository context.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 772194_syn_1
# ==========================================
t1 = """Indication: Stridor, stent migration. 
Proc: Rigid Bronch, Stent Exchange, Laser.
- 14mm Rigid inserted.
- Migrated stent in RMB removed with forceps.
- 70% mid-tracheal obstruction (tumor ingrowth).
- Tx: Nd:YAG laser (40W), mechanical coring, 12mm CRE balloon dilation.
- New 16x50mm Dumon stent deployed.
- Final: Airway patent. EBL 50cc."""

e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "Stridor", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "stent migration", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Stent Exchange", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Laser", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Rigid", 2)}, # "Rigid inserted"
    {"label": "DEV_STENT", **get_span(t1, "stent", 2)}, # "Migrated stent"
    {"label": "ANAT_AIRWAY", **get_span(t1, "RMB", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "70%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "mid-tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t1, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Nd:YAG laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(t1, "40W", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "mechanical coring", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "12mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t1, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t1, "Dumon stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "Airway patent", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "50cc", 1)},
]
BATCH_DATA.append({"id": "772194_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 772194_syn_2
# ==========================================
t2 = """OPERATIVE NARRATIVE: The patient, a 65-year-old female with adenoid cystic carcinoma, presented with acute dyspnea secondary to prosthesis migration. Under general anesthesia with jet ventilation, the airway was cannulated with a 14mm rigid bronchoscope. The existing silicone stent was id[REDACTED] within the right mainstem bronchus and extracted. Significant tumor recurrence was noted at the proximal stent bed, narrowing the lumen by 70%. We utilized the Nd:YAG laser at 40 Watts for coagulative necrosis, followed by mechanical debridement with the rigid barrel. Balloon tracheoplasty was performed to 14mm. To maintain patency, a fresh 16x50mm Dumon silicone stent was deployed, covering the affected segment. Hemostasis was achieved."""

e2 = [
    {"label": "OBS_LESION", **get_span(t2, "adenoid cystic carcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "dyspnea", 1)},
    {"label": "DEV_STENT", **get_span(t2, "prosthesis", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "jet ventilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid bronchoscope", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t2, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t2, "stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "right mainstem bronchus", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "extracted", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "stent bed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "70%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Nd:YAG laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(t2, "40 Watts", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "coagulative necrosis", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "mechanical debridement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid barrel", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Balloon tracheoplasty", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "14mm", 2)},
    {"label": "DEV_STENT_SIZE", **get_span(t2, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t2, "Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t2, "silicone", 2)},
    {"label": "DEV_STENT", **get_span(t2, "stent", 2)},
    {"label": "PROC_ACTION", **get_span(t2, "deployed", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "Hemostasis was achieved", 1)},
]
BATCH_DATA.append({"id": "772194_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 772194_syn_3
# ==========================================
t3 = """Procedures Performed:
1. Bronchoscopy, Rigid, with removal of foreign body (stent) [31638].
2. Bronchoscopy, Rigid, with destruction of tumor (Laser/Coring) [31641].

Technique:
Access obtained via rigid bronchoscope. Existing stent found migrated distally; removed using optical forceps. Tumor ingrowth at mid-trachea treated with Nd:YAG laser ablation and coring. Stenosis dilated with CRE balloon. A new 16x50mm Dumon stent was sized and placed. 
Medical Necessity: Critical central airway obstruction/stent failure."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy, Rigid", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "removal", 1)},
    {"label": "DEV_STENT", **get_span(t3, "stent", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy, Rigid", 2)},
    {"label": "PROC_ACTION", **get_span(t3, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Laser", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "rigid bronchoscope", 1)},
    {"label": "DEV_STENT", **get_span(t3, "stent", 2)},
    {"label": "OBS_FINDING", **get_span(t3, "migrated", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "removed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "optical forceps", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "mid-trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Nd:YAG laser", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "ablation", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "coring", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "CRE balloon", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t3, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t3, "Dumon stent", 1)},
    {"label": "OBS_LESION", **get_span(t3, "central airway obstruction", 1)},
]
BATCH_DATA.append({"id": "772194_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 772194_syn_4
# ==========================================
t4 = """Procedure: Rigid Bronchoscopy / Stent Revision
Attending: Dr. Frankenstein
Steps:
1. GA/Jet ventilation started.
2. 14mm Rigid scope introduced.
3. Old stent found in RMB -> Removed.
4. Tumor regrowth (70%) seen mid-trachea.
5. Laser (Nd:YAG) and coring used to open airway.
6. Balloon dilation to 14mm.
7. New Dumon stent (16x50mm) placed.
8. EBL 50ml. Stable."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Stent Revision", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Jet ventilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Rigid scope", 1)},
    {"label": "DEV_STENT", **get_span(t4, "stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "RMB", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Removed", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t4, "70%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "mid-trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Laser", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Nd:YAG", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "14mm", 2)},
    {"label": "DEV_STENT", **get_span(t4, "Dumon stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t4, "16x50mm", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "placed", 1)},
    {"label": "MEAS_VOL", **get_span(t4, "50ml", 1)},
]
BATCH_DATA.append({"id": "772194_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 772194_syn_5
# ==========================================
t5 = """patient [REDACTED] here for airway issue she has the adenoid cystic ca. stent slipped down to the right side so we went in with the rigid scope general anesthesia jet vent. pulled the old stent out no problem. saw tumor growing back about 70 percent blocked used the yag laser and the barrel to core it out then dilated with the balloon. put a new dumon silicone stent in 16 by 50 size looks good now airway open. little bit of bleeding stopped with saline."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "adenoid cystic ca", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid scope", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "jet vent", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 2)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "70 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "yag laser", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "barrel", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "core", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "balloon", 1)},
    {"label": "DEV_STENT", **get_span(t5, "dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t5, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 3)},
    {"label": "DEV_STENT_SIZE", **get_span(t5, "16 by 50", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "airway open", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 1)},
]
BATCH_DATA.append({"id": "772194_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 772194_syn_6
# ==========================================
t6 = """Rigid bronchoscopy was performed for stent migration and tumor ingrowth. The patient was placed under general anesthesia. A 14mm rigid scope was used. The migrated silicone stent was retrieved from the right mainstem. Inspection showed 70% obstruction from tumor regrowth in the mid-trachea. This was treated with 40W Nd:YAG laser, mechanical coring, and 12mm balloon dilation. A new 16x50mm Dumon silicone stent was deployed. The airway was patent at the end of the case. EBL was 50cc."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "stent migration", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor ingrowth", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "rigid scope", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t6, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t6, "stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "right mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "70% obstruction", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "mid-trachea", 1)},
    {"label": "MEAS_ENERGY", **get_span(t6, "40W", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Nd:YAG laser", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "mechanical coring", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "12mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t6, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t6, "Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t6, "silicone", 2)},
    {"label": "DEV_STENT", **get_span(t6, "stent", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "airway was patent", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "50cc", 1)},
]
BATCH_DATA.append({"id": "772194_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 772194_syn_7
# ==========================================
t7 = """[Indication]
Tracheal Adenoid Cystic Carcinoma, stent migration, stridor.
[Anesthesia]
General TIVA, Jet Ventilation.
[Description]
Rigid bronchoscopy (14mm). Migrated stent removed from RMB. Mid-tracheal tumor (70% stenosis) treated with Nd:YAG laser and mechanical coring. Balloon dilation performed. New 16x50mm Dumon stent placed.
[Plan]
ICU monitoring."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Adenoid Cystic Carcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "stent migration", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "stridor", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Jet Ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Rigid bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "14mm", 1)},
    {"label": "DEV_STENT", **get_span(t7, "stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "RMB", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "Mid-tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "70% stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Nd:YAG laser", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "mechanical coring", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Balloon dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t7, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t7, "Dumon stent", 1)},
]
BATCH_DATA.append({"id": "772194_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 772194_syn_8
# ==========================================
t8 = """The patient was brought to the operating room for management of a migrated tracheal stent. After induction of general anesthesia and initiation of jet ventilation, a 14mm rigid bronchoscope was introduced. We located the previous stent migrated into the right mainstem bronchus and removed it using forceps. Further inspection revealed tumor ingrowth causing 70% obstruction at the mid-trachea. We applied Nd:YAG laser and performed mechanical coring to clear the obstruction, followed by balloon dilation. Finally, a new 16x50mm Dumon silicone stent was deployed, securing the airway."""

e8 = [
    {"label": "ANAT_AIRWAY", **get_span(t8, "tracheal", 1)},
    {"label": "DEV_STENT", **get_span(t8, "stent", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "jet ventilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "14mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "rigid bronchoscope", 1)},
    {"label": "DEV_STENT", **get_span(t8, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "right mainstem bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "70% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "mid-trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "Nd:YAG laser", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "mechanical coring", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "balloon dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t8, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t8, "Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t8, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t8, "stent", 3)},
]
BATCH_DATA.append({"id": "772194_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 772194_syn_9
# ==========================================
t9 = """Operation: Rigid endoscopy, prosthesis extraction, photo-ablation, and stent deployment.
Subject: 65F with tracheal malignancy.
Action: The rigid instrument was introduced. The displaced prosthesis was retrieved from the right lung. Exophytic tissue causing 70% occlusion was vaporized with the Nd:YAG laser and cored. The stricture was expanded via balloon. A replacement 16x50mm Dumon stent was implanted.
Outcome: Patency restored."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Rigid endoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "prosthesis extraction", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "photo-ablation", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "stent deployment", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t9, "malignancy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "rigid instrument", 1)},
    {"label": "DEV_STENT", **get_span(t9, "prosthesis", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "right lung", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Exophytic tissue", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t9, "70% occlusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "Nd:YAG laser", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "cored", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "balloon", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t9, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t9, "Dumon stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "Patency restored", 1)},
]
BATCH_DATA.append({"id": "772194_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 772194
# ==========================================
t10 = """OPERATIVE REPORT: COMPLEX AIRWAY INTERVENTION

Patient: [REDACTED] (MRN: [REDACTED])
Date: [REDACTED]
Attending: Dr. V. Frankenstein

**Indication:** 65F with adenoid cystic carcinoma of the trachea. Status post silicone stent placement 6 months ago. Presents with worsening stridor. CT shows stent migration distally and tumor ingrowth at the proximal stent edge.

**Procedure:** Rigid Bronchoscopy, Stent Removal, Laser Resection, New Stent Placement.
**Anesthesia:** General (TIVA). Jet Ventilation.

**Details:**
Rigid bronchoscope (14mm) inserted. The existing silicone stent was found migrated into the right mainstem, partially obstructing the RUL. Using rigid forceps, the stent was grasped, folded, and removed en bloc.

Inspection revealed exophytic tumor regrowth at the mid-trachea (proximal to old stent site) causing 70% obstruction. 
Nd:YAG Laser was applied (40W) to coagulate and vaporize the tumor. Mechanical coring with the rigid barrel was performed. 
Balloon dilation (CRE balloon, 12mm) was performed at the stenotic segment to 14mm.

Once patency improved to >90%, a new 16x50mm Dumon silicone stent was loaded and deployed covering the mid-to-distal trachea. Position confirmed with flexible scope. RUL patent. Stent stable.

**EBL:** 50cc.
**Complications:** Minor hemorrhage controlled with cold saline and laser."""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "adenoid cystic carcinoma", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "stridor", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "stent migration", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor ingrowth", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Stent Removal", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Laser Resection", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "New Stent Placement", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Jet Ventilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Rigid bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "silicone", 2)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 3)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "right mainstem", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid forceps", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 4)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "mid-trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "70% obstruction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Nd:YAG Laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(t10, "40W", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "coagulate", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "vaporize", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Mechanical coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid barrel", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Balloon dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "12mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "patency improved to >90%", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t10, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t10, "Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "silicone", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 5)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "flexible scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
    {"label": "DEV_STENT", **get_span(t10, "Stent", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "50cc", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Minor hemorrhage controlled", 1)},
]
BATCH_DATA.append({"id": "772194", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)