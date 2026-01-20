import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add cases
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
# Note 1: 3225609_syn_1
# ==========================================
t1 = """Indication: Lung tx anastomotic stricture.
Procedure: Balloon dilation (31630).
- 8.0 ETT.
- Anastomotic stenosis, 77% narrowing.
- Hurricane balloon: 6, 8, 10mm.
- 4 inflations total.
- Post: 79% patency.
Plan: Home today. F/u 4 weeks."""

e1 = [
    {"label": "CTX_HISTORICAL", **get_span(t1, "Lung tx", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(t1, "stricture", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "ETT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(t1, "stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "77% narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Hurricane balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "6", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "8", 2)}, # "8" appears in "8.0" and "6, 8, 10mm". The latter is 2nd occurrence.
    {"label": "MEAS_SIZE", **get_span(t1, "10mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "inflations", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "79% patency", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 3225609_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Bronchoscopic dilation of anastomotic stricture.
INDICATIONS: A 54-year-old male status post bilateral lung transplant presenting with dyspnea and secretions. Imaging confirmed anastomotic narrowing.
PROCEDURE: General anesthesia was induced. The bronchoscope was introduced via an 8.0mm ETT. A circumferential fibrous stricture was visualized at the bronchial anastomosis with 77% luminal compromise. A Hurricane balloon was utilized for graduated dilation up to 10mm. Post-procedural assessment demonstrated marked improvement in luminal caliber to 79% of expected diameter. No significant hemorrhage occurred."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(t2, "stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t2, "status post", 1)},
    {"label": "LATERALITY", **get_span(t2, "bilateral", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t2, "lung transplant", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "secretions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "anastomotic", 2)},
    {"label": "OBS_LESION", **get_span(t2, "narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "ETT", 1)},
    {"label": "OBS_LESION", **get_span(t2, "stricture", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "bronchial", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "anastomosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "77% luminal compromise", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "dilation", 2)},
    {"label": "MEAS_SIZE", **get_span(t2, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "79% of expected diameter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "No significant hemorrhage occurred", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 3225609_syn_3
# ==========================================
t3 = """Service: Bronchoscopy with Dilation (31630).
Target: Bronchial Anastomosis.
Method: Balloon Dilation (Hurricane).
Details: Stricture id[REDACTED]. Balloon catheter inserted. Serial inflations performed (6mm, 8mm, 10mm). Airway patency restored. Procedure required due to symptomatic stricture post-transplant."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Bronchial Anastomosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Dilation", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Hurricane", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Stricture", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Balloon catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "inflations", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "Airway patency restored", 1)},
    {"label": "OBS_LESION", **get_span(t3, "stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t3, "post-transplant", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 3225609_syn_4
# ==========================================
t4 = """Fellow Procedure Note
Patient: [REDACTED]
Attending: Dr. S. Kim
Procedure: Balloon dilation of airway
Steps:
1. ETT 8.0 placed.
2. Scope passed.
3. Anastomotic stricture found.
4. Hurricane balloon dilation x 4.
5. Airway looked much better.
Plan: Dexamethasone given. Follow up in 4 weeks."""

e4 = [
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "airway", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "ETT", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(t4, "stricture", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "dilation", 2)},
    {"label": "MEAS_COUNT", **get_span(t4, "4", 2)}, # "4" in x 4, second occurrence (first is in Step 4 label)
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "Airway looked much better", 1)},
    {"label": "MEDICATION", **get_span(t4, "Dexamethasone", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 3225609_syn_5
# ==========================================
t5 = """timothy brown lung transplant patient has a stricture at the anastomosis. having trouble breathing. we put him under general with a tube. saw the scar tissue blocking about 77 percent. used the hurricane balloon 6 8 and 10 mm. opened it up good to about 79 percent open. little bit of bleeding but stopped on its own. going home today."""

e5 = [
    {"label": "CTX_HISTORICAL", **get_span(t5, "lung transplant", 1)},
    {"label": "OBS_LESION", **get_span(t5, "stricture", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "anastomosis", 1)},
    {"label": "OBS_LESION", **get_span(t5, "scar tissue", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "77 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "hurricane balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "6", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "10 mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "79 percent open", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "little bit of bleeding but stopped on its own", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 3225609_syn_6
# ==========================================
t6 = """This 54-year-old male with a history of lung transplant underwent bronchoscopy for anastomotic stricture. Under general anesthesia, the stricture was id[REDACTED] with 77% narrowing. We used a Hurricane balloon to dilate the airway, performing inflations at 6mm, 8mm, and 10mm. The airway lumen improved significantly to 79%. There were no complications. The patient was discharged the same day."""

e6 = [
    {"label": "CTX_HISTORICAL", **get_span(t6, "history of", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t6, "lung transplant", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(t6, "stricture", 1)},
    {"label": "OBS_LESION", **get_span(t6, "stricture", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "77% narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "dilate", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "airway", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "inflations", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "10mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "airway", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "79%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "no complications", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 3225609_syn_7
# ==========================================
t7 = """[Indication]
Anastomotic bronchial stricture post lung transplant.
[Anesthesia]
General, 8.0 ETT.
[Description]
Stricture (77%) id[REDACTED]. Hurricane balloon dilation performed (6-10mm). Patency improved to 79%.
[Plan]
Home today. Repeat in 4 weeks."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "Anastomotic bronchial", 1)},
    {"label": "OBS_LESION", **get_span(t7, "stricture", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t7, "post", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t7, "lung transplant", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "ETT", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Stricture", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "77%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "6", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "79%", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 3225609_syn_8
# ==========================================
t8 = """[REDACTED] to the OR for dilation of his bronchial anastomotic stricture. After securing the airway, we id[REDACTED] the stenosis which was causing significant obstruction. Using a Hurricane balloon, we performed graduated dilations starting at 6mm and going up to 10mm. The response was excellent, with the airway opening up to near normal caliber. He recovered well and was discharged home."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "bronchial anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(t8, "stricture", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "OBS_LESION", **get_span(t8, "stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "dilations", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "10mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "airway opening up to near normal caliber", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 3225609_syn_9
# ==========================================
t9 = """PROBLEM: Anastomotic bronchial narrowing.
INTERVENTION: Bronchoscopy with balloon expansion.
OBSERVATIONS: We found a circumferential scar narrowing the bronchus. We utilized a Hurricane balloon to stretch the airway. We cycled through 6mm, 8mm, and 10mm sizes. The passage widened considerably. There was minor mucosal disruption but no bleeding. Recommendations include voice rest and follow-up."""

e9 = [
    {"label": "ANAT_AIRWAY", **get_span(t9, "Anastomotic bronchial", 1)},
    {"label": "OBS_LESION", **get_span(t9, "narrowing", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "expansion", 1)},
    {"label": "OBS_LESION", **get_span(t9, "scar", 1)},
    {"label": "OBS_LESION", **get_span(t9, "narrowing", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "Hurricane balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "stretch", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "airway", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "passage widened considerably", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "no bleeding", 1)},
]
BATCH_DATA.append({"id": "3225609_syn_9", "text": t9, "entities": e9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)