import sys
from pathlib import Path

# Add the repository root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
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
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 582736_syn_1
# ==========================================
t1 = """Procedure: Rigid Bronchoscopy.
Indication: Tracheal mass, stridor.
Findings: Post. trachea mass 2cm above carina, 70% occlusion.
Action: 4 biopsies w/ rigid forceps.
Plan: Await path, potential debulking."""

e1 = [
    {"label": "PROC_METHOD", **get_span(t1, "Rigid Bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "trachea", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 2)},
    {"label": "MEAS_SIZE", **get_span(t1, "2cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "carina", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "70% occlusion", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "rigid forceps", 1)}
]
BATCH_DATA.append({"id": "582736_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 582736_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: The patient was placed under general anesthesia with jet ventilation. A 12mm Karl Storz rigid bronchoscope was introduced. A large, well-vascularized, pedunculated mass was visualized on the posterior tracheal wall, significantly obstructing the airway. Four biopsies were obtained using rigid cup forceps. Hemostasis was achieved via direct pressure and suction."""

e2 = [
    {"label": "MEAS_SIZE", **get_span(t2, "12mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid bronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "tracheal", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "airway", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "Four", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid cup forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "Hemostasis was achieved", 1)}
]
BATCH_DATA.append({"id": "582736_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 582736_syn_3
# ==========================================
t3 = """Billing Code: 31625 (Biopsy). Note: Technique used was RIGID bronchoscopy (compatible with 31625). No debulking or excision (31640/31641) performed at this session; procedure limited to diagnostic biopsy of tracheal mass."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "RIGID bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t3, "mass", 1)}
]
BATCH_DATA.append({"id": "582736_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 582736_syn_4
# ==========================================
t4 = """Fellow Note
Pt: R. Davis
Proc: Rigid Bronch
1. Rigid scope inserted.
2. Mass seen in trachea (70% blockage).
3. Biopsied x4 with cup forceps.
4. Bleeding controlled with pressure.
5. Intubated for transport to PACU."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Rigid Bronch", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Rigid scope", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Mass", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t4, "70% blockage", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsied", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x4", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "cup forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "Bleeding controlled", 1)}
]
BATCH_DATA.append({"id": "582736_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 582736_syn_5
# ==========================================
t5 = """[REDACTED] rigid bronch for tracheal mass stridor mass is huge 70 percent block above carina took 4 biopsies with the big forceps bled a moderate amount used pressure to stop it kept him intubated for now pending path results."""

e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "rigid bronch", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "70 percent block", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "carina", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "used pressure to stop it", 1)}
]
BATCH_DATA.append({"id": "582736_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 582736_syn_6
# ==========================================
t6 = """General anesthesia and jet ventilation were utilized. A 12mm rigid bronchoscope was inserted. A large pedunculated mass on the posterior trachea was id[REDACTED], causing 70% obstruction. Four biopsies were taken. Moderate bleeding was controlled with pressure. The patient was intubated and transferred to the PACU."""

e6 = [
    {"label": "MEAS_SIZE", **get_span(t6, "12mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "rigid bronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "70% obstruction", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Four", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "bleeding was controlled", 1)}
]
BATCH_DATA.append({"id": "582736_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 582736_syn_7
# ==========================================
t7 = """[Indication]
Tracheal mass, stridor.
[Anesthesia]
General, Jet Ventilation.
[Description]
Rigid scope used. 70% tracheal obstruction. 4 biopsies taken. Bleeding controlled.
[Plan]
Admit to stepdown. Potential debulking later."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Rigid scope", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "70% tracheal obstruction", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "Bleeding controlled", 1)}
]
BATCH_DATA.append({"id": "582736_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 582736_syn_8
# ==========================================
t8 = """[REDACTED] a rigid bronchoscopy for a large mass in his trachea causing breathing difficulty. Using a rigid scope under general anesthesia, we found the mass blocking about 70% of the airway. We took four biopsy samples. We controlled the bleeding with pressure and decided to wait for results before removing the mass. He remains intubated for safety."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "trachea", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "rigid scope", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "70%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "four", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "controlled the bleeding", 1)}
]
BATCH_DATA.append({"id": "582736_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 582736_syn_9
# ==========================================
t9 = """Intervention for tracheal obstruction. Performed rigid endoscopy. Id[REDACTED] pedunculated tumor. Sampled 4 areas with rigid forceps. Managed hemorrhage with compression. Patient remains intubated."""

e9 = [
    {"label": "ANAT_AIRWAY", **get_span(t9, "tracheal", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rigid endoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "4", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "rigid forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "Managed hemorrhage", 1)}
]
BATCH_DATA.append({"id": "582736_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 582736
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Sarah Mitchell, Fellow: Dr. Kevin Lee (PGY-6)

Dx: Tracheal mass, stridor
Procedure: Rigid bronchoscopy with endobronchial biopsy

General anesthesia, jet ventilation. Rigid bronchoscope (Karl Storz 12mm) inserted. Large pedunculated mass arising from posterior trachea, 2cm above carina, causing 70% obstruction. Mobile, well-vascularized. 4 biopsies with rigid cup forceps. Moderate bleeding - controlled with suction and pressure. Decision to await pathology before debulking. Scope exchanged for ETT, patient ventilated and transferred to PACU intubated for airway monitoring.

Admit to stepdown. Repeat bronch for potential debulking pending path.

S. Mitchell, MD / K. Lee, MD"""

e10 = [
    {"label": "ANAT_AIRWAY", **get_span(t10, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "endobronchial biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Rigid bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "12mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "posterior trachea", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "70% obstruction", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "rigid cup forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "bleeding - controlled", 1)}
]
BATCH_DATA.append({"id": "582736", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)