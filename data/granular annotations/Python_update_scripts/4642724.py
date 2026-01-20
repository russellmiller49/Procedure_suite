import sys
from pathlib import Path

# Set the repository root (assuming script is running in a subdirectory of the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
    
    if start == -1:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4642724_syn_1
# ==========================================
t1 = """Indication: Esophageal CA invasion RMS (89%).
Procedure: Rigid Bronch (Jet Vent).
Actions:
- Balloon dilation.
- Ultraflex Covered SEMS (16x50mm) placed.
Result: 11% residual.
Plan: Floor admit."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Esophageal CA", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "89%", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Rigid Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Jet Vent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "dilation", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t1, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t1, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t1, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t1, "16x50mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "11% residual", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 4642724_syn_2
# ==========================================
t2 = """PROCEDURE: [REDACTED] high-grade obstruction (89%) of the Right Main Stem (RMS) bronchus secondary to esophageal malignancy. Rigid bronchoscopy with jet ventilation was initiated. The stenosis was dilated using a balloon catheter. Following dilation, a 16x50mm Ultraflex Covered SEMS was deployed. Inspection confirmed optimal stent expansion and patency, reducing the obstruction to 11%."""

e2 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "obstruction (89%)", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "Right Main Stem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "bronchus", 1)},
    {"label": "OBS_LESION", **get_span(t2, "esophageal malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "jet ventilation", 1)},
    {"label": "OBS_LESION", **get_span(t2, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "balloon catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t2, "16x50mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t2, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t2, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t2, "SEMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "11%", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 4642724_syn_3
# ==========================================
t3 = """CPT: 31636 (Bronchial Stent).
Ancillary: 31630 (Balloon Dilation).
Device: Ultraflex Covered SEMS (16x50mm).
Site: Right Main Stem.
Improvement: 89% to 11% obstruction."""

e3 = [
    {"label": "DEV_STENT", **get_span(t3, "Stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Dilation", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t3, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t3, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t3, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t3, "16x50mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Right Main Stem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t3, "89%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "11% obstruction", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 4642724_syn_4
# ==========================================
t4 = """Resident Note
Pt: [REDACTED], 66F
Dx: Esophageal CA -> RMS.
Steps:
1. Rigid bronch/Jet.
2. Balloon dilated RMS.
3. Placed Ultraflex Covered SEMS 16x50.
4. Good position.
5. Residual obs 11%.
Plan: Floor."""

e4 = [
    {"label": "OBS_LESION", **get_span(t4, "Esophageal CA", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Rigid bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Jet", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "dilated", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "RMS", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t4, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t4, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t4, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t4, "16x50", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "11%", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 4642724_syn_5
# ==========================================
t5 = """Ashley Adams 66 female esophageal cancer into the RMS 89 percent blocked. We did the rigid bronch with jet vent. Ballooned the stenosis. Then put in a Ultraflex covered stent 16 by 50 mm. Looks great 11 percent obstruction left. No bleeding. Floor."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "esophageal cancer", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "89 percent blocked", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rigid bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "jet vent", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "Ballooned", 1)},
    {"label": "OBS_LESION", **get_span(t5, "stenosis", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t5, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t5, "covered", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t5, "16 by 50 mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "11 percent obstruction", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "No bleeding", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 4642724_syn_6
# ==========================================
t6 = """Under general anesthesia with jet ventilation, rigid bronchoscopy performed. Sequential balloon dilation of RMS stenosis performed. Airway measured and Ultraflex SEMS - Covered stent (16x50mm) deployed in Right mainstem. Stent position confirmed with good expansion and patency. Post-procedure obstruction: ~11% No complications. EBL minimal."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "RMS", 1)},
    {"label": "OBS_LESION", **get_span(t6, "stenosis", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t6, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(t6, "SEMS", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t6, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t6, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t6, "16x50mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "Right mainstem", 1)},
    {"label": "DEV_STENT", **get_span(t6, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "~11%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 4642724_syn_7
# ==========================================
t7 = """[Indication]
Esophageal cancer, 89% RMS obstruction.
[Anesthesia]
General with Jet Ventilation.
[Description]
Rigid bronchoscopy. Balloon dilation of RMS. Deployment of Ultraflex Covered SEMS (16x50mm). Stent patent. Residual obstruction 11%.
[Plan]
Floor admission. Repeat bronchoscopy 4-6 weeks."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Esophageal cancer", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "89%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Jet Ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "RMS", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t7, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t7, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t7, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t7, "16x50mm", 1)},
    {"label": "DEV_STENT", **get_span(t7, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "11%", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 4642724_syn_8
# ==========================================
t8 = """[REDACTED] bronchoscopy to treat a severe 89% blockage in her right mainstem bronchus. We utilized a balloon to dilate the area before placing a 16x50mm covered Ultraflex SEMS. The stent deployed perfectly, restoring the airway to just 11% obstruction. She is stable and moving to the floor."""

e8 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "89% blockage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "right mainstem bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "dilate", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t8, "16x50mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t8, "covered", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t8, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(t8, "SEMS", 1)},
    {"label": "DEV_STENT", **get_span(t8, "stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "11% obstruction", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 4642724_syn_9
# ==========================================
t9 = """Procedure: Rigid bronchoscopy with endobronchial stenting.
Target: Right Main Stem.
Action: Balloon angioplasty was performed. An Ultraflex Covered SEMS (16x50mm) was implanted.
Result: Patency improved; obstruction reduced to 11%."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "stenting", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "Right Main Stem", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "angioplasty", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t9, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t9, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t9, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t9, "16x50mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "11%", 1)},
]
BATCH_DATA.append({"id": "4642724_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 4642724
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. James Rodriguez
Fellow: LT Michelle Torres, MD (PGY-5)

Indication: Esophageal cancer with tracheal invasion
Pre-procedure obstruction: ~89% Right mainstem

PROCEDURE:
Under general anesthesia with jet ventilation, rigid bronchoscopy performed.
Sequential balloon dilation of RMS stenosis performed.
Airway measured and Ultraflex SEMS - Covered stent (16x50mm) deployed in Right mainstem.
Stent position confirmed with good expansion and patency.
Post-procedure obstruction: ~11%
No complications. EBL minimal.

DISPOSITION: Recovery then floor admission for overnight observation.
F/U: Clinic in 4-6 weeks with repeat bronchoscopy.

Rodriguez, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Esophageal cancer", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tracheal invasion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "~89%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right mainstem", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RMS", 1)},
    {"label": "OBS_LESION", **get_span(t10, "stenosis", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(t10, "SEMS", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t10, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t10, "16x50mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right mainstem", 2)},
    {"label": "DEV_STENT", **get_span(t10, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "~11%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No complications", 1)},
]
BATCH_DATA.append({"id": "4642724", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)