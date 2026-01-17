import sys
from pathlib import Path

# Set the repository root (assumed to be 3 levels up from this script, adaptable)
REPO_ROOT = Path(__file__).resolve().parents[2]
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
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return start, start + len(term)

# ==========================================
# Note 1: S31640-002_syn_1
# ==========================================
text_1 = """Dx: Tracheal stenosis (granulation).
Rx: Flex bronch w/ mechanical debulking.
- 2cm above carina.
- Forceps used to remove granulation.
- Snare excision of fibrotic band.
- Lumen opened.
- No thermal energy used.
- D/C home."""

entities_1 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_1, "Tracheal", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "stenosis", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "granulation", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "Flex", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "bronch", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_1, "mechanical", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "debulking", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_1, "2cm", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_1, "carina", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Forceps", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "granulation", 2)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Snare", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "excision", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "fibrotic band", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_1, "Lumen opened", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: S31640-002_syn_2
# ==========================================
text_2 = """PROCEDURE: Therapeutic flexible bronchoscopy.
CLINICAL CONTEXT: Post-intubation stenosis.
FINDINGS: Circumferential granulation tissue at the distal trachea.
TECHNIQUE: Mechanical excision was prioritized. Large alligator forceps were utilized to debride the friable tissue. Subsequently, an electrocautery-independent snare technique was employed to resect a central fibrotic band, effectively disrupting the stenotic ring and restoring luminal diameter."""

entities_2 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "flexible", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "bronchoscopy", 1)))},
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(text_2, "Post-intubation", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "stenosis", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "granulation tissue", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_2, "trachea", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_2, "Mechanical", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "excision", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "alligator forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "debride", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "snare", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "resect", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "fibrotic band", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "stenotic ring", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_2, "restoring luminal diameter", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: S31640-002_syn_3
# ==========================================
text_3 = """CPT 31640 Justification:
Service: Bronchoscopy with excision of tumor/tissue.
Method: Mechanical removal using alligator forceps and snare.
Site: Distal Trachea.
Note: No balloon dilation or thermal ablation codes are applicable as the primary method of opening the airway was physical excision of the obstructing granulation tissue."""

entities_3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "excision", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_3, "Mechanical", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "removal", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "alligator forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "snare", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_3, "Trachea", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_3, "opening the airway", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "excision", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_3, "granulation tissue", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: S31640-002_syn_4
# ==========================================
text_4 = """Procedure: Bronchoscopy (Flexible)
Indication: Tracheal stenosis.
Steps:
1. Moderate sedation.
2. Scope introduced.
3. Granulation tissue found distally.
4. Forceps used to remove tissue pieces.
5. Snare used to cut band.
6. Airway opened up.
Plan: Inhaled steroids, f/u 6 weeks."""

entities_4 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Bronchoscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_4, "Flexible", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_4, "Tracheal", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_4, "stenosis", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Scope", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_4, "Granulation tissue", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "remove", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Snare", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_4, "Airway", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_4, "opened up", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_4, "steroids", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: S31640-002_syn_5
# ==========================================
text_5 = """Procedure note for maria lopez... she has that tracheal stenosis from the tube before... we did a flex bronch with sedation... saw the granulation tissue above the carina... used the alligator forceps to pull it out piece by piece... also used a snare to cut a band of tissue... opened it up nice... no bleeding really... patient tolerated it well going home on steroids."""

entities_5 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_5, "tracheal", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "stenosis", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_5, "flex", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_5, "bronch", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "granulation tissue", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_5, "carina", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "alligator forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "snare", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_5, "opened it up nice", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_5, "steroids", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: S31640-002_syn_6
# ==========================================
text_6 = """Under moderate sedation the flexible bronchoscope was inserted. The distal trachea showed 70% obstruction from granulation tissue. Mechanical debulking was executed using large alligator forceps to remove tissue. A snare was then used to resect a fibrotic band. No thermal ablation was required. The airway lumen was significantly improved. The patient was stable and discharged to home."""

entities_6 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "flexible", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "bronchoscope", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_6, "trachea", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_6, "70% obstruction", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "granulation tissue", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_6, "Mechanical", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "debulking", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "alligator forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "snare", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "resect", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "fibrotic band", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_6, "airway lumen", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_6, "significantly improved", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: S31640-002_syn_7
# ==========================================
text_7 = """[Indication]
Symptomatic benign distal tracheal stenosis.
[Anesthesia]
Moderate Sedation.
[Description]
Mechanical debulking of granulation tissue using forceps and snare resection. Tracheal lumen restored. No thermal ablation.
[Plan]
Discharge on inhaled steroids."""

entities_7 = [
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_7, "tracheal", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "stenosis", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_7, "Mechanical", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "debulking", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "granulation tissue", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "snare", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "resection", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_7, "Tracheal lumen", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_7, "restored", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_7, "steroids", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: S31640-002_syn_8
# ==========================================
text_8 = """The patient underwent flexible bronchoscopy for tracheal stenosis. We id[REDACTED] a ring of granulation tissue causing obstruction. Using alligator forceps, we mechanically removed the tissue in a piecemeal fashion. We also utilized a snare to resect a fibrous band within the trachea. These mechanical interventions successfully opened the airway without the need for laser or balloon dilation."""

entities_8 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "flexible", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "bronchoscopy", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_8, "tracheal", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "stenosis", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "granulation tissue", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "alligator forceps", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "mechanically", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "removed", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "snare", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "resect", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "fibrous band", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_8, "trachea", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_8, "mechanical", 2)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_8, "opened the airway", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: S31640-002_syn_9
# ==========================================
text_9 = """Flexible endoscopy performed to clear the airway. The tracheal obstruction was dismantled using grasping forceps. The constricting tissue was avulsed and extracted. A loop snare was used to slice through the fibrotic stricture. The tracheal passage was widened via physical removal of the offending tissue."""

entities_9 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_9, "Flexible", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "endoscopy", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_9, "airway", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_9, "tracheal", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "obstruction", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "grasping forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "snare", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "fibrotic stricture", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_9, "tracheal passage", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_9, "widened", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "removal", 1)))},
]
BATCH_DATA.append({"id": "S31640-002_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: S31640-002
# ==========================================
text_10 = """BRONCHOSCOPY PROCEDURE NOTE

Patient: [REDACTED], 58-year-old female
MRN: [REDACTED]
Date: [REDACTED]
Location: [REDACTED]
Attending: Dr. James Porter

Indication:
Progressive dyspnea and stridor due to benign post-intubation granulation tissue causing distal tracheal stenosis.

Pre-/Post-procedure Diagnosis:
Benign distal tracheal obstruction from post-intubation granulation tissue.

Procedure:
Flexible bronchoscopy with mechanical debulking of obstructing granulation tissue (CPT 31640).

Anesthesia / Sedation:
Moderate sedation with IV midazolam and fentanyl; topical lidocaine. Native airway with oral bite block. ASA class III.

Findings:
At 2 cm above the carina there was circumferential granulation tissue and nodular scar narrowing the distal trachea to approximately 70% obstruction. No discrete mass elsewhere. Distal mainstem bronchi patent.

Interventions:
Using large alligator forceps through the flexible bronchoscope, multiple passes of mechanical debulking were performed, removing friable granulation tissue in piecemeal fashion. Snare resection was then used to excise a central fibrotic band. The stenotic ring was mechanically disrupted, and the tracheal lumen opened significantly. No balloon dilation or thermal ablation was used. The note explicitly reflects mechanical debulking and snare resection of the obstructing lesion consistent with CPT 31640.

Hemostasis / Complications:
Minor oozing controlled with cold saline; no significant bleeding. No desaturations or arrhythmias.

EBL:
Approximately 10 mL.

Disposition:
Observed for 2 hours in recovery and discharged home on inhaled corticosteroid and PPI. Follow-up bronchoscopy planned in 6–8 weeks to assess for recurrent stenosis."""

entities_10 = [
    {"label": "OUTCOME_SYMPTOMS", **dict(zip(["start", "end"], get_span(text_10, "Progressive dyspnea", 1)))},
    {"label": "OUTCOME_SYMPTOMS", **dict(zip(["start", "end"], get_span(text_10, "stridor", 1)))},
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(text_10, "post-intubation", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "granulation tissue", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "tracheal", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "stenosis", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "tracheal", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "obstruction", 1)))},
    {"label": "CTX_HISTORICAL", **dict(zip(["start", "end"], get_span(text_10, "post-intubation", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "granulation tissue", 2)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "Flexible", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "bronchoscopy", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "mechanical", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "debulking", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "granulation tissue", 3)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_10, "midazolam", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_10, "fentanyl", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_10, "lidocaine", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(text_10, "2 cm", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "carina", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "granulation tissue", 4)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "nodular scar", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "trachea", 3)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_10, "70% obstruction", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "mainstem bronchi", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "alligator forceps", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "flexible", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "bronchoscope", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "mechanical", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "debulking", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "granulation tissue", 5)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "Snare", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "resection", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "fibrotic band", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "stenotic ring", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "mechanically", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "tracheal", 3)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_10, "lumen opened significantly", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(text_10, "mechanical", 3)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "debulking", 3)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "snare", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "resection", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "lesion", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_10, "10 mL", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_10, "corticosteroid", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "bronchoscopy", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "stenosis", 2)))},
]
BATCH_DATA.append({"id": "S31640-002", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)