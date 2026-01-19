import sys
from pathlib import Path

# 1. Dynamic Repo Root (Assumes script is 2 levels deep: repo/scripts/your_script.py)
# Adjust this calculation if your directory structure differs.
REPO_ROOT = Path(__file__).resolve().parent.parent

# 2. Add repo root to sys.path so we can import the utility
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# 3. Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the nth occurrence of a substring.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: SYNIP0012_syn_1
# ==========================================
t1 = """Indication: BI obstruction (NSCLC).
Procedure: Rigid bronchoscopy, mechanical debulking.
Findings: Exophytic tumor BI, 75% occlusion.
Action: Cored with rigid barrel. Microdebrider used for cleanup.
Result: 30% residual narrowing. No stent.
Complications: Mild bleeding.
Disp: Floor."""

e1 = [
    {"label": "ANAT_AIRWAY", **get_span(t1, "BI", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "obstruction", 1)},
    # NSCLC is diagnosis, skipping per guide strictness on lesions (Mass/Nodule)
    {"label": "PROC_ACTION", **get_span(t1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "mechanical debulking", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Exophytic tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "BI", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "75% occlusion", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Cored", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "rigid barrel", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Microdebrider", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "30% residual narrowing", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Mild bleeding", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: SYNIP0012_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: The patient underwent rigid bronchoscopy for the management of a symptomatic obstruction in the bronchus intermedius secondary to non-small cell lung cancer. Upon airway inspection, an exophytic neoplasm was visualized distal to the right upper lobe takeoff, occluding approximately 75% of the lumen. Mechanical debulking was undertaken utilizing the bevel of the rigid bronchoscope for coring, followed by microdebridement to ensure a smooth endoluminal surface. The procedure successfully re-established airway patency, leaving approximately 30% residual stenosis."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "rigid bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "bronchus intermedius", 1)},
    {"label": "OBS_LESION", **get_span(t2, "exophytic neoplasm", 1)},
    # "distal to" implies relationship, "right upper lobe" is the landmark (LUNG_LOC)
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "right upper lobe", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "occluding approximately 75% of the lumen", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "coring", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "microdebridement", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "approximately 30% residual stenosis", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: SYNIP0012_syn_3
# ==========================================
t3 = """Service: Bronchoscopy with tumor excision (31640).
Location: Bronchus Intermedius (Right Lung).
Method: Mechanical debulking via Rigid Bronchoscopy.
Tools: Rigid barrel, suction, forceps, microdebrider.
Outcome: Reduction of obstruction from 75% to 30%.
Medical Necessity: Recurrent post-obstructive pneumonia."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "tumor excision", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Bronchus Intermedius", 1)},
    {"label": "LATERALITY", **get_span(t3, "Right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Lung", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Mechanical debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Rigid Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Rigid barrel", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "microdebrider", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t3, "75%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "30%", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "post-obstructive pneumonia", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: SYNIP0012_syn_4
# ==========================================
t4 = """Procedure Note
Patient: [REDACTED], 74F
Procedure: Rigid Bronchoscopy/Debulking
Steps:
1. Anesthesia induction.
2. Rigid scope placed.
3. Id[REDACTED] tumor in Bronchus Intermedius.
4. Mechanically debulked with forceps/suction/microdebrider.
5. Hemostasis achieved.
6. Patient extubated.
Comments: Good result, airway open."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Rigid scope", 1)},
    {"label": "OBS_LESION", **get_span(t4, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Bronchus Intermedius", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Mechanically debulked", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "microdebrider", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "Hemostasis achieved", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: SYNIP0012_syn_5
# ==========================================
t5 = """Doris Hill 74 female with NSCLC obstructing the bronchus intermedius rigid bronch was done today under general anesthesia... saw the tumor blocking about 75 percent or so used the rigid tube to core it out and suctioned the pieces microdebrider used too final result looked good maybe 30 percent narrowing left no stent needed mild bleeding only stopped with saline admitted to floor."""

e5 = [
    {"label": "OBS_FINDING", **get_span(t5, "obstructing", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "bronchus intermedius", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "rigid bronch", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "blocking about 75 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid tube", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "core it out", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "suctioned", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "microdebrider", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "30 percent narrowing left", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "mild bleeding", 1)},
    {"label": "MEDICATION", **get_span(t5, "saline", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: SYNIP0012_syn_6
# ==========================================
t6 = """Right bronchus intermedius obstruction from non-small cell lung cancer with recurrent post-obstructive pneumonia. Rigid bronchoscopy with mechanical debulking of tumor in bronchus intermedius. General anesthesia with rigid bronchoscopy. Exophytic tumor in bronchus intermedius just distal to right upper lobe takeoff causing ~75% obstruction with distal mucous plugging. Mechanical debulking was performed using the rigid barrel, suction, and forceps to core out tumor and remove large fragments. A microdebrider was then used to excise residual tumor and smooth the airway wall. Final airway lumen had ~30% residual narrowing; no stent was placed. Mild bleeding controlled with cold saline and dilute epinephrine. Extubated in OR and admitted to medical floor for pneumonia management."""

e6 = [
    {"label": "LATERALITY", **get_span(t6, "Right", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "obstruction", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "post-obstructive pneumonia", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "mechanical debulking", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "bronchus intermedius", 2)},
    # Fixed: "rigid bronchoscopy" (lowercase) appears only once in text.
    {"label": "PROC_ACTION", **get_span(t6, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Exophytic tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "bronchus intermedius", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "right upper lobe", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "~75% obstruction", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "mucous plugging", 1)},
    # Fixed: "Mechanical debulking" (Capitalized) appears only once in text.
    {"label": "PROC_ACTION", **get_span(t6, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "rigid barrel", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "core out", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "excise", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "~30% residual narrowing", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "Mild bleeding controlled", 1)},
    {"label": "MEDICATION", **get_span(t6, "saline", 1)},
    {"label": "MEDICATION", **get_span(t6, "epinephrine", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: SYNIP0012_syn_7
# ==========================================
t7 = """[Indication]
NSCLC obstruction of Bronchus Intermedius.
[Anesthesia]
General, Rigid.
[Description]
75% occlusion of BI found. Mechanical debulking performed using rigid coring and microdebrider. Airway caliber improved to 30% residual stenosis. Distal mucous cleared.
[Plan]
Admit to floor. Pneumonia management."""

e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "Bronchus Intermedius", 1)},
    # "Rigid" here is under Anesthesia/technique, implies the scope method
    {"label": "PROC_METHOD", **get_span(t7, "Rigid", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "75% occlusion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "BI", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Mechanical debulking", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "rigid coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "microdebrider", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "30% residual stenosis", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Pneumonia", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: SYNIP0012_syn_8
# ==========================================
t8 = """We performed a rigid bronchoscopy on Ms. [REDACTED] to treat a tumor obstructing her bronchus intermedius. After inducing anesthesia, we located the tumor which was blocking about 75% of the airway. We used the rigid scope to mechanically remove the bulk of the tumor and then used a microdebrider to clean up the edges. The airway was significantly opened up, with only about 30% narrowing remaining. She tolerated the procedure well with minimal bleeding."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "obstructing", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "bronchus intermedius", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "blocking about 75%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "mechanically remove", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "microdebrider", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "30% narrowing remaining", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "minimal bleeding", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: SYNIP0012_syn_9
# ==========================================
t9 = """Procedure: Rigid bronchoscopy with physical resection of tumor in bronchus intermedius.
Findings: Growth in the airway causing 75% blockage.
Intervention: The mass was cored out using the rigid scope. Remaining tissue was shaved with a microdebrider. The airway was cleared.
Result: Airway flow restored."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "physical resection", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "bronchus intermedius", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Growth", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t9, "75% blockage", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "cored out", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "shaved", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "microdebrider", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: SYNIP0012 (Original)
# ==========================================
t10 = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
Patient: [REDACTED]  MRN: [REDACTED]  Age/Sex: 74/F
Date: [REDACTED]
Indication: Right bronchus intermedius obstruction from non-small cell lung cancer with recurrent post-obstructive pneumonia.
Procedure: Rigid bronchoscopy with mechanical debulking of tumor in bronchus intermedius.
Anesthesia: General anesthesia with rigid bronchoscopy.
Findings: Exophytic tumor in bronchus intermedius just distal to right upper lobe takeoff causing ~75% obstruction with distal mucous plugging.
Intervention: Mechanical debulking was performed using the rigid barrel, suction, and forceps to core out tumor and remove large fragments. A microdebrider was then used to excise residual tumor and smooth the airway wall. Final airway lumen had ~30% residual narrowing; no stent was placed.
Complications: Mild bleeding controlled with cold saline and dilute epinephrine.
Disposition: Extubated in OR and admitted to medical floor for pneumonia management."""

e10 = [
    {"label": "LATERALITY", **get_span(t10, "Right", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "obstruction", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "post-obstructive pneumonia", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "mechanical debulking", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "bronchus intermedius", 2)},
    # Fixed: "rigid bronchoscopy" (lowercase) appears only once in text.
    {"label": "PROC_ACTION", **get_span(t10, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Exophytic tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "bronchus intermedius", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "right upper lobe", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "~75% obstruction", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "mucous plugging", 1)},
    # Fixed: "Mechanical debulking" (Capitalized) appears only once in text.
    {"label": "PROC_ACTION", **get_span(t10, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid barrel", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "core out", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "excise", 1)},
    {"label": "OBS_LESION", **get_span(t10, "residual tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "~30% residual narrowing", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Mild bleeding controlled", 1)},
    {"label": "MEDICATION", **get_span(t10, "saline", 1)},
    {"label": "MEDICATION", **get_span(t10, "epinephrine", 1)}
]
BATCH_DATA.append({"id": "SYNIP0012", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)