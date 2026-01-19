import sys
from pathlib import Path

# Add the repository root to sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
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
# Note 1: 2595477_syn_1
# ==========================================
t1 = """Ind: Met lung CA, 62% LMS.
Proc: Rigid bronch, Microdebrider, APC.
Action: Excision + Ablation.
Result: 62% -> 39%.
EBL: 50mL.
Plan: ICU."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Met lung CA", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "62%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Rigid bronch", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Microdebrider", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Excision", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Ablation", 1)},
    # The second 62% is referencing the pre-state in the result line, but context implies pre-state data.
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "39%", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "50mL", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_1", "text": t1, "entities": e1})


# ==========================================
# Note 2: 2595477_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: [REDACTED] bronchoscopy for metastatic obstruction of the Left Mainstem (62%). The microdebrider was used for bulk excision of the tumor. Following mechanical removal, APC/Laser was utilized to ablate the tumor base and ensure hemostasis (CPT 31641). The airway was successfully recanalized to 39% residual obstruction."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t2, "metastatic obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "Left Mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "62%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Laser", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 2)},
    # "ensure hemostasis" describes the intent/result of the tool use
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "hemostasis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "39%", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_2", "text": t2, "entities": e2})


# ==========================================
# Note 3: 2595477_syn_3
# ==========================================
t3 = """Code: 31641 (Destruction/Ablation).
Support: Combination of Microdebrider for debulking and APC/Laser for thermal ablation of base.
Site: Left Mainstem.
Outcome: Partial restoration of patency."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Destruction", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Laser", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "ablation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Left Mainstem", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_3", "text": t3, "entities": e3})


# ==========================================
# Note 4: 2595477_syn_4
# ==========================================
t4 = """Procedure: Debulking (Microdebrider + APC)
Pt: [REDACTED]
Steps:
1. GA induced.
2. LMS obstruction 62%.
3. Microdebrider used to remove bulk.
4. APC used on base.
5. Residual 39%.
Plan: ICU."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Microdebrider", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "APC", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(t4, "obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t4, "62%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Microdebrider", 2)},
    {"label": "PROC_ACTION", **get_span(t4, "remove bulk", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "APC", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "39%", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_4", "text": t4, "entities": e4})


# ==========================================
# Note 5: 2595477_syn_5
# ==========================================
t5 = """[REDACTED]. she has mets to the LMS blocking it about 62 percent. we used the microdebrider to take out the bulk of it. then used the laser and apc to burn the rest and stop bleeding. residual is 39 percent. blood loss 50ml. icu for observation."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "mets", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "LMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "62 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "microdebrider", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "laser", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "apc", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "burn", 1)},
    # "stop bleeding" implies hemostasis
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "stop bleeding", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "39 percent", 1)},
    {"label": "MEAS_VOL", **get_span(t5, "50ml", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_5", "text": t5, "entities": e5})


# ==========================================
# Note 6: 2595477_syn_6
# ==========================================
t6 = """Metastatic lung cancer with bronchial obstruction. Pre-procedure 62% obstruction at LMS. Under general anesthesia, rigid bronchoscopy performed. Endobronchial tumor id[REDACTED] at LMS. Microdebrider assisted tumor removal performed with sequential tumor removal. Additional APC/laser used for hemostasis and tumor base ablation. Post-procedure 39% residual obstruction. EBL 50mL."""

e6 = [
    {"label": "OBS_LESION", **get_span(t6, "Metastatic lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(t6, "bronchial obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "62%", 1)},
    {"label": "OBS_LESION", **get_span(t6, "obstruction", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "LMS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "tumor removal", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "tumor removal", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "laser", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 4)},
    {"label": "PROC_ACTION", **get_span(t6, "ablation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "39%", 1)},
    {"label": "OBS_LESION", **get_span(t6, "obstruction", 3)},
    {"label": "MEAS_VOL", **get_span(t6, "50mL", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_6", "text": t6, "entities": e6})


# ==========================================
# Note 7: 2595477_syn_7
# ==========================================
t7 = """[Indication]
Metastatic lung CA, 62% LMS obstruction.
[Anesthesia]
General.
[Description]
Rigid bronchoscopy. Microdebrider excision. APC/Laser ablation. Residual obstruction 39%.
[Plan]
ICU admission."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Metastatic lung CA", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "62%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(t7, "obstruction", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "excision", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Laser", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "ablation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "39%", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_7", "text": t7, "entities": e7})


# ==========================================
# Note 8: 2595477_syn_8
# ==========================================
t8 = """We performed a rigid bronchoscopy on [REDACTED] a 62% obstruction in the Left Mainstem. We used a microdebrider to mechanically remove the tumor bulk. Following this, we used APC and laser to ablate the tumor base and control bleeding. The obstruction was reduced to 39%."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "62%", 1)},
    {"label": "OBS_LESION", **get_span(t8, "obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "Left Mainstem", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "remove the tumor bulk", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "ablate", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "control bleeding", 1)},
    {"label": "OBS_LESION", **get_span(t8, "obstruction", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "39%", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_8", "text": t8, "entities": e8})


# ==========================================
# Note 9: 2595477_syn_9
# ==========================================
t9 = """Under general anesthesia, rigid bronchoscopy was executed. An endobronchial tumor was found at the LMS. Microdebrider assisted tumor extraction was performed with sequential tumor removal. Supplemental APC/laser was used for hemostasis and tumor base destruction. Post-procedure ~39% residual blockage."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "LMS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "Microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "tumor extraction", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "tumor removal", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "laser", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 4)},
    {"label": "PROC_ACTION", **get_span(t9, "destruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "~39%", 1)}
]
BATCH_DATA.append({"id": "2595477_syn_9", "text": t9, "entities": e9})


# ==========================================
# Note 10: 2595477 (Original)
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Mark Taylor
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Metastatic lung cancer with bronchial obstruction
Pre-procedure: ~62% obstruction at LMS

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at LMS.
Microdebrider assisted tumor removal performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Additional APC/laser used for hemostasis and tumor base ablation.
Post-procedure: ~39% residual obstruction.
EBL: ~50mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Taylor, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Metastatic lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(t10, "bronchial obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "~62%", 1)},
    {"label": "OBS_LESION", **get_span(t10, "obstruction", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LMS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Microdebrider", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "tumor removal", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "tumor removal", 2)},
    {"label": "MEAS_COUNT", **get_span(t10, "Multiple passes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "laser", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 4)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "~39%", 1)},
    {"label": "OBS_LESION", **get_span(t10, "obstruction", 3)},
    {"label": "MEAS_VOL", **get_span(t10, "~50mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Hemostasis achieved", 1)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 1)}
]
BATCH_DATA.append({"id": "2595477", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)