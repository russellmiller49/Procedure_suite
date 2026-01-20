import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 3184705_syn_1
# ==========================================
id_1 = "3184705_syn_1"
text_1 = """Indication: Post-trach subglottic stenosis.
Procedure: Balloon dilation (31630).
- LMA airway.
- Eccentric weblike stenosis 1-2cm below cords.
- CRE balloon: 12, 14, 16mm x 30s.
- 25% -> 85% patency.
- No complications.
Plan: Admit overnight. Decadron 10mg."""
entities_1 = [
    {"label": "CTX_HISTORICAL", **get_span(text_1, "Post-trach", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Balloon dilation", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Eccentric", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "weblike", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "stenosis", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "cords", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "30s", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "25%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "85% patency", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No complications", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Decadron", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 3184705_syn_2
# ==========================================
id_2 = "3184705_syn_2"
text_2 = """PROCEDURE: Therapeutic bronchoscopy with balloon dilation.
CLINICAL SUMMARY: [REDACTED], a 36-year-old female with a history of tracheostomy, presented with biphasic stridor. Endoscopic examination revealed an eccentric weblike stenosis in the subglottic region, approximately 1-2 cm distal to the vocal cords. The luminal compromise was estimated at 75%. Mechanical dilation was effected using a controlled radial expansion balloon. Sequential dilations to 16mm resulted in restoration of airway patency to approximately 85% of normal caliber. Hemostasis was maintained."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "Therapeutic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "balloon dilation", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_2, "history of tracheostomy", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "stridor", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "eccentric", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "weblike", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "subglottic region", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "vocal cords", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "75%", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilation", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "controlled radial expansion balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilations", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "16mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "85%", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 3184705_syn_3
# ==========================================
id_3 = "3184705_syn_3"
text_3 = """Code: 31630 (Bronchial dilation).
Indication: Subglottic stenosis (post-tracheostomy).
Device: CRE Balloon.
Technique: Scope advanced to lesion. Balloon positioned across stenosis. Inflated to 12mm, 14mm, and 16mm. Visual confirmation of expansion. 
Result: Obstruction reduced from 75% to 15%. Symptom relief expected."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchial dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "stenosis", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_3, "post-tracheostomy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "CRE Balloon", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Balloon", 2)},
    {"label": "OBS_FINDING", **get_span(text_3, "stenosis", 2)},
    {"label": "MEAS_SIZE", **get_span(text_3, "12mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "14mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "16mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "75%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "15%", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 3184705_syn_4
# ==========================================
id_4 = "3184705_syn_4"
text_4 = """Resident Note
Patient: [REDACTED]
Procedure: Balloon Dilation
Attending: Dr. L. Garcia
Steps:
1. MAC anesthesia, LMA.
2. Airway inspected.
3. Stenosis found subglottic.
4. CRE balloon dilation x 2 cycles.
5. Patency improved.
6. No bleeding.
Plan: Admit for observation."""
entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Balloon Dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Airway", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "subglottic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "CRE balloon", 1)},
    # Fixed: "dilation" occurs once in lowercase (line 8). "Dilation" (line 3) is uppercase.
    {"label": "PROC_ACTION", **get_span(text_4, "dilation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No bleeding", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 3184705_syn_5
# ==========================================
id_5 = "3184705_syn_5"
text_5 = """dorothy white 36 f here for subglottic stenosis dilation. she had a trach before. stridor at rest. we used mac and an lma. saw the web like narrowing right below cords. used the balloon to open it up did 12 14 16 mm. opened up real nice went from 75 blocked to only 15. minimal bleeding. gave epi anyway. admit her overnight give decadron thanks."""
entities_5 = [
    {"label": "ANAT_AIRWAY", **get_span(text_5, "subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "dilation", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_5, "had a trach before", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "stridor", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "web like", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "narrowing", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "cords", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "12", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "14", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "16 mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "75", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "15", 1)},
    {"label": "MEDICATION", **get_span(text_5, "epi", 1)},
    {"label": "MEDICATION", **get_span(text_5, "decadron", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 3184705_syn_6
# ==========================================
id_6 = "3184705_syn_6"
text_6 = """A 36-year-old female underwent flexible bronchoscopy for post-tracheostomy subglottic stenosis. Under MAC anesthesia, the stenosis was id[REDACTED] 1-2 cm below the vocal cords with 75% narrowing. A controlled radial expansion balloon was used for dilation at 12mm, 14mm, and 16mm. Patency improved to 85%. There were no complications. The patient was admitted for overnight observation."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "flexible bronchoscopy", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_6, "post-tracheostomy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "stenosis", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "stenosis", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "vocal cords", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "75%", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "controlled radial expansion balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "12mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "14mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "16mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "85%", 1)},
    # Fixed: text contains "no complications" (lowercase), not "No complications"
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 3184705_syn_7
# ==========================================
id_7 = "3184705_syn_7"
text_7 = """[Indication]
Post-tracheostomy subglottic stenosis.
[Anesthesia]
MAC, LMA.
[Description]
Subglottic stenosis (75%) id[REDACTED]. Balloon dilation performed (12-16mm). Patency improved to 85%.
[Plan]
Admit overnight. Repeat in 6 weeks."""
entities_7 = [
    {"label": "CTX_HISTORICAL", **get_span(text_7, "Post-tracheostomy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "Subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "75%", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Balloon dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "12-16mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "85%", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 3184705_syn_8
# ==========================================
id_8 = "3184705_syn_8"
text_8 = """The patient presented for treatment of subglottic stenosis. We induced anesthesia and inserted the bronchoscope. The examination revealed an eccentric web-like stenosis narrowing the airway by 75%. We advanced a balloon catheter and performed serial dilations up to 16mm. The airway opened significantly, leaving only about 15% residual narrowing. The patient was stable throughout and was admitted for monitoring."""
entities_8 = [
    {"label": "ANAT_AIRWAY", **get_span(text_8, "subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "bronchoscope", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "eccentric", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "web-like", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "stenosis", 2)},
    {"label": "OBS_FINDING", **get_span(text_8, "narrowing", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "75%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "balloon catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dilations", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "16mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "15%", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "narrowing", 2)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 3184705_syn_9
# ==========================================
id_9 = "3184705_syn_9"
text_9 = """DIAGNOSIS: Post-tracheostomy subglottic constriction.
PROCEDURE: Bronchoscopy with balloon widening.
FINDINGS: We located the constriction 1-2 cm below the cords. It was an eccentric web. We used a radial expansion balloon to widen the passage. Cycles were run at 12, 14, and 16mm. The airway diameter increased substantially. No tissue damage occurred. The patient was moved to the floor for observation."""
entities_9 = [
    {"label": "CTX_HISTORICAL", **get_span(text_9, "Post-tracheostomy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "subglottic", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "constriction", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "balloon widening", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "constriction", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "cords", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "eccentric", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "web", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "radial expansion balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "12", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "14", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "16mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "airway", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "No tissue damage", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)