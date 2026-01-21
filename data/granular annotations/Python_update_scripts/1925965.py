import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 1925965_syn_1
# ==========================================
text_1 = """Indication: RCC met to RMS (89% block).
Procedure: Rigid Bronchoscopy (Jet Vent).
Actions:
- Balloon dilation of RMS.
- Ultraflex Covered SEMS (18x30mm) placed.
Result: 25% residual. Minimal EBL.
Plan: Floor admit."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "RCC met", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "89% block", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Jet Vent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "RMS", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_1, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_1, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_1, "18x30mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "25% residual", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1925965_syn_2
# ==========================================
text_2 = """PROCEDURE: [REDACTED], with a known history of renal cell carcinoma, presented with an 89% metastatic obstruction of the Right Main Stem (RMS) bronchus. Under general anesthesia utilizing jet ventilation, rigid bronchoscopy was performed. The stenotic segment underwent sequential balloon dilation. Subsequently, an 18x30mm Ultraflex Self-Expanding Metallic Stent (SEMS, covered) was deployed across the lesion. Confirmation of stent position demonstrated good radial expansion and patency, reducing the obstruction to approximately 25%."""

entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "renal cell carcinoma", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "89% metastatic obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "Right Main Stem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchus", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "stenotic segment", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_2, "18x30mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_2, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "Self-Expanding Metallic Stent", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "SEMS", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_2, "covered", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "reducing the obstruction to approximately 25%", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1925965_syn_3
# ==========================================
text_3 = """CPT: 31641 (Tumor Debulking? No, Stent placement = 31636).
Correct Coding: 31636 (Bronchial Stent) + 31630 (Balloon Dilation).
Device: Ultraflex SEMS Covered (18x30mm).
Location: Right Main Stem.
Justification: 89% critical obstruction requiring structural support."""

entities_3 = [
    {"label": "DEV_STENT", **get_span(text_3, "Stent", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "Bronchial Stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Dilation", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_3, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "SEMS", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_3, "Covered", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_3, "18x30mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Right Main Stem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "89% critical obstruction", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1925965_syn_4
# ==========================================
text_4 = """Resident Note
Pt: [REDACTED], 78F
Dx: RCC met to RMS.
Steps:
1. Rigid bronch with jet vent.
2. Balloon dilation of RMS.
3. Placed Ultraflex Covered SEMS 18x30mm.
4. Checked position, looks good.
5. RMS much more open now (25% obs).
Plan: Floor."""

entities_4 = [
    {"label": "OBS_LESION", **get_span(text_4, "RCC met", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "jet vent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "RMS", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_4, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_4, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(text_4, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_4, "18x30mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "RMS", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "25% obs", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1925965_syn_5
# ==========================================
text_5 = """Margaret Green here for the RMS obstruction its a met from renal cell. 89 percent blocked. We did the rigid bronch with jet ventilation. Dilated it with the balloon first. Then put in the Ultraflex covered stent 18 by 30. It opened up nice residual is 25 percent. No complications she is going to the floor."""

entities_5 = [
    {"label": "ANAT_AIRWAY", **get_span(text_5, "RMS", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "met", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "89 percent blocked", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "jet ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "Dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "balloon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_5, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_5, "covered", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_5, "18 by 30", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "residual is 25 percent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "No complications", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1925965_syn_6
# ==========================================
text_6 = """Under general anesthesia with jet ventilation, rigid bronchoscopy performed. Sequential balloon dilation of RMS stenosis performed. Airway measured and Ultraflex SEMS - Covered stent (18x30mm) deployed in Right mainstem. Stent position confirmed with good expansion and patency. Post-procedure obstruction: ~25% No complications. EBL minimal."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "RMS", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "stenosis", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_6, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "SEMS", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_6, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_6, "18x30mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Right mainstem", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "Post-procedure obstruction: ~25%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1925965_syn_7
# ==========================================
text_7 = """[Indication]
Renal cell carcinoma met to RMS, 89% obstruction.
[Anesthesia]
General with Jet Ventilation.
[Description]
Rigid bronchoscopy. Balloon dilation of RMS. Deployment of Ultraflex Covered SEMS (18x30mm). Stent expanded well. Residual obstruction 25%.
[Plan]
Floor admission. Repeat bronchoscopy 4-6 weeks."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Renal cell carcinoma met", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "89% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Jet Ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "RMS", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_7, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_7, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_7, "18x30mm", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "Residual obstruction 25%", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "bronchoscopy", 2)},
]
BATCH_DATA.append({"id": "1925965_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1925965_syn_8
# ==========================================
text_8 = """Due to [REDACTED] 89% blockage in the right mainstem bronchus from metastatic cancer, we proceeded with stent placement. Under general anesthesia, we first dilated the narrowing with a balloon. We then deployed an 18x30mm covered Ultraflex SEMS. The stent expanded well, improving the airway patency significantly to a residual obstruction of 25%."""

entities_8 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "89% blockage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "right mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "metastatic cancer", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "balloon", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_8, "18x30mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_8, "covered", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_8, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "SEMS", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "stent", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "residual obstruction of 25%", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1925965_syn_9
# ==========================================
text_9 = """Procedure: Rigid bronchoscopy with implantation of self-expanding metallic stent.
Focus: Right Main Stem.
Action: The stenosis was dilated via balloon. An Ultraflex Covered SEMS (18x30mm) was deployed. Visualization confirmed adequacy.
Outcome: Occlusion reduced to 25%."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "self-expanding metallic stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "Right Main Stem", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "balloon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_9, "Ultraflex", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_9, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "SEMS", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_9, "18x30mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "Occlusion reduced to 25%", 1)},
]
BATCH_DATA.append({"id": "1925965_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1925965
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams
Fellow: Dr. James Liu (PGY-5)

Indication: Renal cell carcinoma metastasis to bronchus
Pre-procedure obstruction: ~89% Right mainstem

PROCEDURE:
Under general anesthesia with jet ventilation, rigid bronchoscopy performed.
Sequential balloon dilation of RMS stenosis performed.
Airway measured and Ultraflex SEMS - Covered stent (18x30mm) deployed in Right mainstem.
Stent position confirmed with good expansion and patency.
Post-procedure obstruction: ~25%
No complications. EBL minimal.

DISPOSITION: Recovery then floor admission for overnight observation.
F/U: Clinic in 4-6 weeks with repeat bronchoscopy.

Williams, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Renal cell carcinoma metastasis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "bronchus", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "obstruction: ~89%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Right mainstem", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "stenosis", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "SEMS", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "Covered", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_10, "18x30mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Right mainstem", 2)},
    {"label": "DEV_STENT", **get_span(text_10, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "Post-procedure obstruction: ~25%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchoscopy", 2)},
]
BATCH_DATA.append({"id": "1925965", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)