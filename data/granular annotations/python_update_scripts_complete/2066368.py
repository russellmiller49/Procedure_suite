import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add cases
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly without package context, though strictly expected within repo
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
            break
            
    if start == -1:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
        
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2066368_syn_1
# ==========================================
text_1 = """Indication: Bronchial stricture post-sleeve resection.
Procedure: Balloon dilation (31630).
- Deep sedation.
- RUL anastomosis stenosis 74%.
- Hurricane balloon: 6, 8, 9mm x 45s.
- Post: 28% residual.
- Mild bleeding.
Plan: Admit overnight. Decadron 10mg."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Bronchial stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_1, "post-sleeve resection", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    # "anastomosis" implies airway structure, strictly RUL is location
    {"label": "OBS_LESION", **get_span(text_1, "stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "74%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Hurricane balloon", 1)},
    # First '6' is in CPT 31630, second is the measurement
    {"label": "MEAS_SIZE", **get_span(text_1, "6", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "9mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "45s", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "28%", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Mild bleeding", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Decadron", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2066368_syn_2
# ==========================================
text_2 = """OPERATIVE NOTE: Management of post-surgical bronchial anastomotic stricture.
PATIENT: 52-year-old male status post RUL sleeve resection.
FINDINGS: Significant circumferential stenosis at the right upper lobe bronchial anastomosis, estimated at 74% narrowing.
PROCEDURE: Under deep sedation, a Hurricane balloon catheter was positioned across the stricture. Serial dilations were performed to a maximum of 9mm. Four inflation cycles were completed.
OUTCOME: Residual stenosis reduced to 28%. Mild mucosal oozing was noted and was self-limited."""

entities_2 = [
    {"label": "CTX_HISTORICAL", **get_span(text_2, "post-surgical", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "bronchial anastomotic stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_2, "post", 2)},  # status post
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_2, "sleeve resection", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "stenosis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right upper lobe", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchial anastomosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "74% narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Hurricane balloon", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "stricture", 2)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilations", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Four", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "28%", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Mild mucosal oozing", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2066368_syn_3
# ==========================================
text_3 = """CPT 31630: Bronchoscopy with dilation.
Indication: Anastomotic stricture (post-lung cancer surgery).
Technique: Flexible bronchoscopy. Id[REDACTED] of 74% stenosis at RUL anastomosis. Dilation with Hurricane balloon (6-9mm). Improvement to 72% patency verified."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "dilation", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Anastomotic stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_3, "post-lung cancer surgery", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Flexible bronchoscopy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "74%", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "stenosis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Hurricane balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "6-9mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "72% patency", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2066368_syn_4
# ==========================================
text_4 = """Fellow Note
Patient: [REDACTED]
Procedure: Airway dilation
Attending: Dr. D. Anderson
Steps:
1. Deep sedation.
2. Scope to RUL anastomosis.
3. Stricture id[REDACTED].
4. Hurricane balloon dilation up to 9mm.
5. Airway opened well.
Plan: Admit, f/u 6 weeks."""

entities_4 = [
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Airway", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "anastomosis", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Stricture", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "dilation", 2)},
    {"label": "MEAS_SIZE", **get_span(text_4, "9mm", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2066368_syn_5
# ==========================================
text_5 = """donald wilson had a sleeve resection now has a stricture at the rul. deep sedation used. saw the narrowing pretty tight 74 percent. used the hurricane balloon went 6 8 and 9 mm. held for 45 secs. opened up to about 28 percent left. bit of bleeding but fine. admit him give decadron."""

entities_5 = [
    {"label": "CTX_HISTORICAL", **get_span(text_5, "sleeve resection", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "stricture", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rul", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "narrowing", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "74 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "hurricane balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "6", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "9 mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "45 secs", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "28 percent", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "bleeding", 1)},
    {"label": "MEDICATION", **get_span(text_5, "decadron", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2066368_syn_6
# ==========================================
text_6 = """A 52-year-old male underwent bronchoscopy for a bronchial stricture following sleeve resection. Under deep sedation, the RUL anastomosis was found to be narrowed by 74%. A Hurricane balloon was used for serial dilation at 6mm, 8mm, and 9mm. The airway patency improved to 72%. Mild mucosal oozing occurred. The patient was admitted for overnight observation."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "bronchial stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_6, "following", 1)}, # Context for history
    {"label": "CTX_HISTORICAL", **get_span(text_6, "sleeve resection", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "anastomosis", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "narrowed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "74%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "9mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "72%", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Mild mucosal oozing", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2066368_syn_7
# ==========================================
text_7 = """[Indication]
Bronchial stricture post sleeve resection.
[Anesthesia]
Deep sedation.
[Description]
RUL anastomosis stenosis (74%) id[REDACTED]. Hurricane balloon dilation performed (6-9mm). Patency improved to 72%.
[Plan]
Admit overnight. Repeat in 6 weeks."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Bronchial stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_7, "post", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_7, "sleeve resection", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "anastomosis", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "74%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "6-9mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "72%", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2066368_syn_8
# ==========================================
text_8 = """We performed a bronchoscopy on [REDACTED] his anastomotic stricture. After sedation, we examined the RUL anastomosis and found it significantly narrowed. We used a Hurricane balloon to dilate the stricture, performing multiple inflations up to 9mm. The airway diameter improved noticeably. There was some minor bleeding which resolved on its own. He was admitted for observation."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "anastomotic stricture", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "anastomosis", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "narrowed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dilate", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "stricture", 2)},
    {"label": "MEAS_SIZE", **get_span(text_8, "9mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "bleeding", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2066368_syn_9
# ==========================================
text_9 = """DIAGNOSIS: Bronchial narrowing after surgery.
PROCEDURE: Scope with balloon expansion.
OBSERVATIONS: We saw a tight spot at the RUL connection. We used a Hurricane balloon to stretch it out. We went up to 9mm. The opening is much better now. Minor bleeding was observed. He will stay in the hospital tonight."""

entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "Bronchial narrowing", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_9, "after surgery", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "expansion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Hurricane balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "9mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "bleeding", 1)},
]
BATCH_DATA.append({"id": "2066368_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")