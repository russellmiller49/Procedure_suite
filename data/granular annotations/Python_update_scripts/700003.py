import sys
from pathlib import Path

# Set the repository root (assuming script is run from a subdir)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports
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
# Case 1: 700003_syn_1
# ==========================================
t1 = """Dx: Tracheal SCC obstruction.
Proc: Rigid bronch, debulking, APC, stent.
Details:
- Rigid scope inserted.
- 80% mid-tracheal stenosis.
- Cored/debulked + APC.
- 16x50mm silicone stent deployed.
- Lumen patent.
Plan: Extubate, PACU, home."""

e1 = [
    {"label": "ANAT_AIRWAY", **get_span(t1, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t1, "SCC", 1)},
    {"label": "OBS_LESION", **get_span(t1, "obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Rigid bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "APC", 1)},
    {"label": "DEV_STENT", **get_span(t1, "stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Rigid scope", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "80%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "mid-tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t1, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Cored", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "debulked", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "APC", 2)},
    {"label": "DEV_STENT_SIZE", **get_span(t1, "16x50mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t1, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t1, "stent", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "Lumen patent", 1)},
]
BATCH_DATA.append({"id": "700003_syn_1", "text": t1, "entities": e1})

# ==========================================
# Case 2: 700003_syn_2
# ==========================================
t2 = """PROCEDURE: Rigid therapeutic bronchoscopy with tumor destruction and tracheal stenting.
INDICATION: 73-year-old male with severe airway obstruction due to squamous cell carcinoma.
DESCRIPTION: The rigid tracheobronchoscope was introduced. Significant fungating tumor was noted in the mid-trachea. Mechanical debulking was performed using the bevel of the scope and forceps, followed by APC for hemostasis and tumor ablation. A 16 x 50 mm Dumon silicone stent was deployed, covering the lesion and restoring airway patency."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Rigid therapeutic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "tumor destruction", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "tracheal stenting", 1)},
    {"label": "OBS_LESION", **get_span(t2, "airway obstruction", 1)},
    {"label": "OBS_LESION", **get_span(t2, "squamous cell carcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid tracheobronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(t2, "fungating tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "mid-trachea", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "tumor ablation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t2, "16 x 50 mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t2, "Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t2, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t2, "stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "restoring airway patency", 1)},
]
BATCH_DATA.append({"id": "700003_syn_2", "text": t2, "entities": e2})

# ==========================================
# Case 3: 700003_syn_3
# ==========================================
t3 = """Billable Services:
- 31641: Destruction of tumor (rigid coring + APC).
- 31636: Placement of tracheal stent (silicone).
Justification: Critical central airway obstruction (80%). General anesthesia/Jet ventilation required. Stent necessary to maintain patency after debulking."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Destruction of tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "rigid coring", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Placement of tracheal stent", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t3, "silicone", 1)},
    {"label": "OBS_LESION", **get_span(t3, "central airway obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t3, "80%", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Jet ventilation", 1)},
    {"label": "DEV_STENT", **get_span(t3, "Stent", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "debulking", 1)},
]
BATCH_DATA.append({"id": "700003_syn_3", "text": t3, "entities": e3})

# ==========================================
# Case 4: 700003_syn_4
# ==========================================
t4 = """Resident Note: Rigid Bronchoscopy
Patient: [REDACTED]
Attending: Dr. Bennett
Steps:
1. GA/Jet vent.
2. Rigid scope passed.
3. Tumor ID'd mid-trachea.
4. Debulked with scope/forceps/APC.
5. Stent placed (16x50mm).
6. Airway inspected: Patent.
Complications: None."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Jet vent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Rigid scope", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "mid-trachea", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Debulked", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "scope", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "APC", 1)},
    {"label": "DEV_STENT", **get_span(t4, "Stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t4, "16x50mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "Patent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "None", 1)},
]
BATCH_DATA.append({"id": "700003_syn_4", "text": t4, "entities": e4})

# ==========================================
# Case 5: 700003_syn_5
# ==========================================
t5 = """Mr [REDACTED] here for the tracheal obstruction we did the rigid bronch today. Saw the tumor blocking about 80 percent of the trachea. Used the rigid barrel to core it out and used some APC to clean it up. Put in a silicone stent 16 by 50 fits good. Airway looks wide open now. Extubated in OR doing well."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "tracheal obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rigid bronch", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "80 percent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "trachea", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid barrel", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "core it out", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "APC", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t5, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t5, "16 by 50", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "Airway looks wide open", 1)},
]
BATCH_DATA.append({"id": "700003_syn_5", "text": t5, "entities": e5})

# ==========================================
# Case 6: 700003_syn_6
# ==========================================
t6 = """Therapeutic rigid bronchoscopy performed for mid-tracheal squamous cell carcinoma obstruction. 80% stenosis reduced to <20% via mechanical coring and argon plasma coagulation. 16x50 mm silicone stent deployed across lesion. Airway patent. Patient extubated and stable."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "rigid bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "mid-tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t6, "squamous cell carcinoma", 1)},
    {"label": "OBS_LESION", **get_span(t6, "obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "80%", 1)},
    {"label": "OBS_LESION", **get_span(t6, "stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "<20%", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "mechanical coring", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "argon plasma coagulation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t6, "16x50 mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t6, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t6, "stent", 1)},
    {"label": "OBS_LESION", **get_span(t6, "lesion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "Airway patent", 1)},
]
BATCH_DATA.append({"id": "700003_syn_6", "text": t6, "entities": e6})

# ==========================================
# Case 7: 700003_syn_7
# ==========================================
t7 = """[Indication]
Severe malignant mid-tracheal obstruction (SCC).
[Anesthesia]
General, rigid bronchoscopy, jet ventilation.
[Description]
Mechanical debulking and APC of tracheal tumor. Deployment of 16x50mm silicone stent. Restoration of airway patency.
[Plan]
PACU, discharge, follow-up 4-6 weeks."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "malignant", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "mid-tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t7, "obstruction", 1)},
    {"label": "OBS_LESION", **get_span(t7, "SCC", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "jet ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Mechanical debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "APC", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "tracheal", 2)},
    {"label": "OBS_LESION", **get_span(t7, "tumor", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t7, "16x50mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t7, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t7, "stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "Restoration of airway patency", 1)},
]
BATCH_DATA.append({"id": "700003_syn_7", "text": t7, "entities": e7})

# ==========================================
# Case 8: 700003_syn_8
# ==========================================
t8 = """[REDACTED] bronchoscopy to relieve his tracheal obstruction. We id[REDACTED] the squamous cell carcinoma narrowing the mid-trachea. We mechanically removed the bulk of the tumor and used APC to control bleeding and destroy residual tissue. To prevent re-obstruction, we placed a straight silicone stent. The airway is now widely patent, and he was extubated immediately following the procedure."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tracheal obstruction", 1)},
    {"label": "OBS_LESION", **get_span(t8, "squamous cell carcinoma", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "mid-trachea", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "mechanically removed", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "APC", 1)},
    {"label": "OBS_LESION", **get_span(t8, "re-obstruction", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t8, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t8, "stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "airway is now widely patent", 1)},
]
BATCH_DATA.append({"id": "700003_syn_8", "text": t8, "entities": e8})

# ==========================================
# Case 9: 700003_syn_9
# ==========================================
t9 = """Procedure: Rigid endoscopy with tumor ablation and airway stenting.
Subject: [REDACTED].
Findings: Severe tracheal stenosis.
Intervention: The mass was resected and cauterized. A silicone prosthesis was positioned to scaffold the airway.
Outcome: Obstruction resolved."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Rigid endoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "tumor ablation", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "airway stenting", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t9, "stenosis", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "resected", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "cauterized", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t9, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t9, "prosthesis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "Obstruction resolved", 1)},
]
BATCH_DATA.append({"id": "700003_syn_9", "text": t9, "entities": e9})

# ==========================================
# Case 10: 700003
# ==========================================
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (73 years)
DATE: [REDACTED]
LOCATION: [REDACTED]

PREOPERATIVE DIAGNOSIS: Severe mid-tracheal obstruction from squamous cell carcinoma.
POSTOPERATIVE DIAGNOSIS: Same.

PROCEDURE:
1. Rigid therapeutic bronchoscopy with destruction of endobronchial tumor.
2. Flexible bronchoscopy.
3. Tracheal silicone stent placement.

SURGEON: Laura Bennett, MD (Interventional Pulmonology)
ASSISTANT: Andrew Park, MD (Thoracic Surgery Fellow)
ANESTHESIA: General anesthesia with rigid bronchoscopy and jet ventilation.

INDICATION:
73-year-old male with known squamous cell carcinoma of the mid-trachea, presenting with stridor and 80% luminal obstruction on CT and bronchoscopy. Planned rigid therapeutic bronchoscopy with debulking and airway stent placement for palliation and airway stabilization.

PROCEDURE DETAILS:
After induction of general anesthesia, a rigid tracheobronchoscope was introduced under direct visualization. Tumor causing near circumferential narrowing of the mid-trachea over ~3 cm was id[REDACTED].

Tumor Debulking:
Mechanical debulking was performed using the bevel of the rigid scope and large forceps to core out the intraluminal mass. Argon plasma coagulation (APC) at 35 W and 1.5 L/min flow was then applied circumferentially to residual tumor and bleeding points until a widely patent lumen was obtained. Approximate residual obstruction was < 20% with smooth mucosal surface.

Stent Placement:
A 16 x 50 mm straight silicone Dumon stent was selected. Under direct bronchoscopic visualization, the stent was mounted on the rigid stent loader and deployed across the involved segment. Final position covered the entire tumor bed with adequate proximal and distal margins. The stent was well seated with no migration and good distal ventilation.

The airway was reinspected distally with a flexible bronchoscope through the rigid barrel. No additional endobronchial disease was id[REDACTED]. Secretions were suctioned.

COMPLICATIONS:
Total estimated blood loss ~20 mL. No significant hypoxia, arrhythmia, or airway perforation. No intraoperative complications.

DISPOSITION:
The rigid scope was removed and the patient was transitioned back to a standard ETT and subsequently extubated in the OR. He was transported to PACU on 4 L/min nasal cannula in stable condition. Follow-up CT and bronchoscopy are planned in 4–6 weeks.

IMPRESSION:
Successful rigid therapeutic bronchoscopy with tumor destruction and silicone tracheal stent placement for malignant tracheal obstruction, with marked improvement in airway patency."""

e10 = [
    {"label": "ANAT_AIRWAY", **get_span(t10, "mid-tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t10, "obstruction", 1)},
    {"label": "OBS_LESION", **get_span(t10, "squamous cell carcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Rigid therapeutic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(t10, "endobronchial tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Tracheal", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placement", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "jet ventilation", 1)},
    {"label": "OBS_LESION", **get_span(t10, "squamous cell carcinoma", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "mid-trachea", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "stridor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "80%", 1)},
    {"label": "OBS_LESION", **get_span(t10, "luminal obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rigid therapeutic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "debulking", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid tracheobronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "mid-trachea", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "3 cm", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "OBS_LESION", **get_span(t10, "intraluminal mass", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Argon plasma coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "APC", 1)},
    {"label": "MEAS_ENERGY", **get_span(t10, "35 W", 1)},
    {"label": "OBS_LESION", **get_span(t10, "residual tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "widely patent lumen", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "< 20%", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t10, "16 x 50 mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "silicone", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "Dumon", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "flexible bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid barrel", 1)},
    {"label": "OBS_LESION", **get_span(t10, "endobronchial disease", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Secretions", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "20 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No significant hypoxia", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "arrhythmia", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "airway perforation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid scope", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "rigid therapeutic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "tumor destruction", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "silicone", 3)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "tracheal", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 5)},
    {"label": "OBS_LESION", **get_span(t10, "malignant tracheal obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "marked improvement in airway patency", 1)},
]
BATCH_DATA.append({"id": "700003", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)