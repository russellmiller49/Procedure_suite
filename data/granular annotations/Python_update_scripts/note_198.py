import json
import os
import datetime
from pathlib import Path

# -------------------------------------------------------------------------
# 1. Configuration & Path Setup
# -------------------------------------------------------------------------
NOTE_ID = "note_198"
RAW_TEXT = """NOTE_ID:  note_198 SOURCE_FILE: note_198.txt PREOPERATIVE DIAGNOSIS: near-complete tracheal occlusion secondary to granulation tissue and severe tracheomalacia.
POSTOPERATIVE DIAGNOSIS: near-complete tracheal occlusion secondary to granulation tissue and severe tracheomalacia.
PROCEDURE PERFORMED: Rigid bronchoscopy with silicone wire stent placement
INDICATIONS: tracheal obstruction requiring intervention
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Initial airway inspection was performed with the ultra-slim Olympus P190 flexible bronchoscope was inserted through the patient’s customized 5.5 mm tracheostomy tube.
At the distal margin of the tracheostomy tube approximately 2 cm proximal to the main carina was a ridge of granulation tissue occluding approximately 80% of the tracheostomy tube the lumen.
Beyond the obstruction there was severe tracheobronchial malacia with near complete obstruction of the distal trachea and right mainstem with approximately 75% obstruction of the left mainstem.
The airways were erythematous and inflamed throughout. The flexible bronchoscope and the tracheostomy tube were then removed and we attempted to insert a 14 mm ventilating rigid bronchoscope through the small tracheostomy stoma which was unsuccessful.
We then reinserted the tracheostomy tube and attempted to insert the rigid bronchoscope through the oral route however the patient had severely distorted upper airway anatomy and edema which made it impossible to visualize the posterior pharynx and vocal cords.
We then attempted insertion of progressively smaller rigid bronchoscope down to the smallest diameter of 6 mm without success due to a stricture is within the stoma tract.
At this point we called for otolaryngology’s assistance in extending the stoma to allow insertion of the rigid bronchoscope.
Once they arrived, they attempted to visualize the vocal cords as well using suspension laryngoscopy but were unsuccessful.
They then surgically extended the tracheostomy stoma.  They were unable to extend the stoma to the point where the large rigid bronchoscope could be inserted due to significant scar tissue and concern for injury to the anterior trachea however they were able to extend it to the point we could insert the smaller rigid bronchoscopes.
At this point the 6 mm rigid bronchoscope was inserted through the tracheostomy stoma and advanced to the main carina.
We however unable to insert any usable instruments or have the ability to deploy the silicone stent through this rigid bronchoscope (due to size) and the decision was made to insert the smallest Y stent available (14 x 10 x 10) through the stoma with rigid forceps compressing the bronchial limbs and advance the stent to the main carina with visualization through a flexible bronchoscope inserted behind  through the left bronchial limb of the stent.
After taking measurements the tracheal limb of the stent was cut to 30mm the left lime cut to 20mm and the right limb cut to 10mm.
We were eventually able to successfully advance the stent however the patient’s airways were extremely narrowed and we had significant difficulty seating the bronchial limbs in place properly.
We used a variety of techniques including use of the rigid  optical forceps, advancement with Kelly clamps by ENT while we provided direct visualization with the flexible bronchoscope, insertion of CRE balloon to gently push the stent in the place and eventually insertion of the slightly larger  size 8 rigid bronchoscope through the tracheostomy stoma, into the stent and manipulate the rigid scope to push the limbs into place.
Unfortunately during this maneuver a small airway tear (likely caused by the distal edge of the stents right bronchial  limb) of the stoma was visualized at the lateral aspect of the right main stem approximately  half a centimeter above the right upper lobe.
We consider placing a metallic stent to cover this however were reluctant given the concerns of metallic stents and benign airway disease.
The patient was given 1 g of Ancef and we consulted thoracic surgery by phone to discuss options and based on their experience they felt that if there is no evidence of pneumothorax on chest x-ray this type of airway tears often resolves without intervention.
A portable chest x-ray was then performed which showed no evidence of pneumothorax or pneumomediastinum.
We are able to slightly advance the stent to see well at the main carina.
There was a slight tenting of the distal limb on the right at the distal margin of the airway tear which could not be corrected however otherwise the stent was well seated resulting in resolution of the distal tracheal and mainstem bronchi obstruction and the distal airways were patent.
We then reinserted the patient’s tracheostomy tube through the stoma with direct visualization and into the tracheal limb of the stent where it was secured.
At this point the procedure was completed and the patient was transferred back to the ICU.
Once the patient arrived in the ICU at first he was doing relatively well however he had an episode of inability to ventilate and severe hypoxia with PO2 dropping below 50% transiently while we were still at the bedside.
This improved rapidly with manual bag ventilation. The flexible bronchoscope was inserted through the tracheostomy tube and there did not appear to be any significant obstruction of the stent however there was some foamy bloody airway secretions which were consistent with what would be seen in acute pulmonary edema.
A chest x-ray was performed during this event (radiology technician was already at the bedside for preplanned chest x-ray) and no pneumothorax was seen.
20 mg of Lasix were given and the patient’s condom catheter was exchanged for a Foley catheter and there was a rapid diuresis after which his tidal volumes significantly improved.
Pressures required on the ventilator to maintain adequate tidal volumes were relatively high even after this maneuver and was felt  that the patient’s extremely small tracheostomy tube might be contributing to high airway pressures.
Because of this we decided to remove the tracheostomy tube and over bronchoscopic visualization insert a 7.0 Boniva tracheostomy tube and secured this in place midway into the stent.
This seemed to improve his airway compliance and ventilation.  At this point the patient was deemed stable and after discussing case with parents care was turned over to the ICU team.
Complications:  small lateral right mainstem airway tear
Recommendations:
-	Patient to remain on positive pressure ventilation tonight
-	Combination vancomycin and Zosyn for 1 week to empirically prevent infection related to airway tear.
-	Please obtain CT chest without contrast once patient has gained stable enough to transport.
-	Plan for repeat flexible bronchoscopy at bedside likely on 4/1/2019 or earlier if any concerns arise
-	Please contact the interventional pulmonary team if any airway issues occur in this patient.
-	The patient’s stent is radiolucent and will not be seen on chest x-ray, only CT.
If concern for stent related complication occurs flex bronchoscopy should be the first intervention followed by CT of the chest if clinically appropriate to evaluate for complications.
-	Patient will require 3 times a day 3% saline nebulizers starting tonight and as long as the patient’s airway stent is in place for mucolytic effect and hydration to prevent stent plugging.
-	If tracheostomy tube needs to be removed and reinserted this must be performed  with direct visualization of the distal tip as it is inserted into the lumen of the tracheostomy tube to prevent kinking or obstruction of the stent by  the tracheostomy tube.
-	We will continue to follow."""

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# 2. Define Entities (Manual Extraction mapped to Label Guide)
# -------------------------------------------------------------------------
# Note: Offsets are calculated relative to RAW_TEXT.
entities = [
    # "tracheal occlusion" -> OUTCOME/FINDING? Guide prefers explicit lumen outcome. "near-complete tracheal occlusion" is Pre-op dx.
    # Text body extraction:
    {"label": "PROC_ACTION", "text": "Rigid bronchoscopy"},
    {"label": "DEV_STENT", "text": "silicone wire stent"},
    {"label": "DEV_INSTRUMENT", "text": "Olympus P190 flexible bronchoscope"},
    {"label": "MEAS_SIZE", "text": "5.5 mm"},
    {"label": "DEV_INSTRUMENT", "text": "tracheostomy tube"},
    {"label": "ANAT_AIRWAY", "text": "main carina"},
    {"label": "OBS_LESION", "text": "granulation tissue"},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "occluding approximately 80%"},
    {"label": "ANAT_AIRWAY", "text": "lumen"},
    {"label": "OBS_FINDING", "text": "severe tracheobronchial malacia"},
    {"label": "ANAT_AIRWAY", "text": "distal trachea"},
    {"label": "ANAT_AIRWAY", "text": "right mainstem"},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "approximately 75% obstruction"},
    {"label": "ANAT_AIRWAY", "text": "left mainstem"},
    {"label": "OBS_FINDING", "text": "erythematous"},
    {"label": "OBS_FINDING", "text": "inflamed"},
    {"label": "DEV_INSTRUMENT", "text": "flexible bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "tracheostomy tube"},
    {"label": "MEAS_SIZE", "text": "14 mm"},
    {"label": "DEV_INSTRUMENT", "text": "ventilating rigid bronchoscope"},
    {"label": "ANAT_AIRWAY", "text": "tracheostomy stoma"},
    {"label": "DEV_INSTRUMENT", "text": "tracheostomy tube"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "ANAT_AIRWAY", "text": "oral route"},
    {"label": "ANAT_AIRWAY", "text": "posterior pharynx"},
    {"label": "ANAT_AIRWAY", "text": "vocal cords"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "MEAS_SIZE", "text": "6 mm"},
    {"label": "OBS_LESION", "text": "stricture"},
    {"label": "ANAT_AIRWAY", "text": "stoma tract"},
    {"label": "ANAT_AIRWAY", "text": "stoma"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "ANAT_AIRWAY", "text": "vocal cords"},
    {"label": "PROC_METHOD", "text": "suspension laryngoscopy"},
    {"label": "ANAT_AIRWAY", "text": "tracheostomy stoma"},
    {"label": "ANAT_AIRWAY", "text": "stoma"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "OBS_LESION", "text": "scar tissue"},
    {"label": "ANAT_AIRWAY", "text": "anterior trachea"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscopes"},
    {"label": "MEAS_SIZE", "text": "6 mm"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "ANAT_AIRWAY", "text": "tracheostomy stoma"},
    {"label": "ANAT_AIRWAY", "text": "main carina"},
    {"label": "DEV_STENT", "text": "silicone stent"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "DEV_STENT", "text": "Y stent"},
    {"label": "DEV_STENT_SIZE", "text": "14 x 10 x 10"},
    {"label": "ANAT_AIRWAY", "text": "stoma"},
    {"label": "DEV_INSTRUMENT", "text": "rigid forceps"},
    {"label": "ANAT_AIRWAY", "text": "main carina"},
    {"label": "DEV_INSTRUMENT", "text": "flexible bronchoscope"},
    {"label": "MEAS_SIZE", "text": "30mm"},
    {"label": "MEAS_SIZE", "text": "20mm"},
    {"label": "MEAS_SIZE", "text": "10mm"},
    {"label": "DEV_INSTRUMENT", "text": "rigid  optical forceps"},
    {"label": "DEV_INSTRUMENT", "text": "Kelly clamps"},
    {"label": "DEV_INSTRUMENT", "text": "flexible bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "CRE balloon"},
    {"label": "MEAS_SIZE", "text": "size 8"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscope"},
    {"label": "ANAT_AIRWAY", "text": "tracheostomy stoma"},
    {"label": "OBS_LESION", "text": "airway tear"},
    {"label": "ANAT_AIRWAY", "text": "stoma"},
    {"label": "ANAT_AIRWAY", "text": "right main stem"},
    {"label": "ANAT_LUNG_LOC", "text": "right upper lobe"},
    {"label": "DEV_STENT", "text": "metallic stent"},
    {"label": "MEDICATION", "text": "Ancef"},
    {"label": "OBS_LESION", "text": "pneumothorax"},
    {"label": "PROC_METHOD", "text": "chest x-ray"},
    {"label": "OBS_LESION", "text": "airway tears"},
    {"label": "PROC_METHOD", "text": "chest x-ray"},
    {"label": "OBS_LESION", "text": "pneumothorax"},
    {"label": "OBS_FINDING", "text": "pneumomediastinum"},
    {"label": "ANAT_AIRWAY", "text": "main carina"},
    {"label": "OBS_FINDING", "text": "tenting"},
    {"label": "OBS_LESION", "text": "airway tear"},
    {"label": "ANAT_AIRWAY", "text": "distal tracheal"},
    {"label": "ANAT_AIRWAY", "text": "mainstem bronchi"},
    {"label": "ANAT_AIRWAY", "text": "distal airways"},
    {"label": "DEV_INSTRUMENT", "text": "tracheostomy tube"},
    {"label": "ANAT_AIRWAY", "text": "stoma"},
    {"label": "OBS_FINDING", "text": "hypoxia"},
    {"label": "DEV_INSTRUMENT", "text": "flexible bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "tracheostomy tube"},
    {"label": "OBS_FINDING", "text": "secretions"},
    {"label": "OBS_FINDING", "text": "pulmonary edema"},
    {"label": "PROC_METHOD", "text": "chest x-ray"},
    {"label": "OBS_LESION", "text": "pneumothorax"},
    {"label": "MEDICATION", "text": "Lasix"},
    {"label": "DEV_CATHETER", "text": "condom catheter"},
    {"label": "DEV_CATHETER", "text": "Foley catheter"},
    {"label": "DEV_INSTRUMENT", "text": "tracheostomy tube"},
    {"label": "MEAS_SIZE", "text": "7.0"},
    {"label": "DEV_INSTRUMENT", "text": "Boniva tracheostomy tube"},
    {"label": "OBS_LESION", "text": "airway tear"},
    {"label": "MEDICATION", "text": "vancomycin"},
    {"label": "MEDICATION", "text": "Zosyn"},
    {"label": "PROC_METHOD", "text": "CT chest"},
    {"label": "PROC_ACTION", "text": "flexible bronchoscopy"},
    {"label": "PROC_METHOD", "text": "chest x-ray"},
    {"label": "PROC_METHOD", "text": "CT"},
    {"label": "PROC_METHOD", "text": "flex bronchoscopy"},
    {"label": "PROC_METHOD", "text": "CT"},
    {"label": "MEDICATION", "text": "3% saline"},
    {"label": "DEV_INSTRUMENT", "text": "nebulizers"},
    {"label": "DEV_INSTRUMENT", "text": "tracheostomy tube"},
]

# -------------------------------------------------------------------------
# 3. Helper Functions for Offset Calculation
# -------------------------------------------------------------------------
def find_offsets(text, entity_text, start_search_from=0):
    start = text.find(entity_text, start_search_from)
    if start == -1:
        return None, None
    end = start + len(entity_text)
    return start, end

# -------------------------------------------------------------------------
# 4. Process and Generate JSONL
# -------------------------------------------------------------------------
processed_entities = []
search_cursor = 0

# Sort entities by occurrence in text to ensure correct mapping of repeated terms
# Note: The entities list above is roughly chronological. We need to be careful with repeats.
# We will use a sliding cursor.

found_spans = []
for ent in entities:
    s, e = find_offsets(RAW_TEXT, ent["text"], search_cursor)
    
    # If not found, try searching from 0 (in case of out-of-order manual list error), 
    # but strictly prefer forward progression for correct duplicate handling.
    if s is None:
        # Fallback: search from 0, but warn (logic implies list should be ordered)
        s, e = find_offsets(RAW_TEXT, ent["text"], 0)
    
    if s is not None:
        span = {
            "span_id": f"{ent['label']}_{s}",
            "note_id": NOTE_ID,
            "label": ent["label"],
            "text": ent["text"],
            "start": s,
            "end": e
        }
        found_spans.append(span)
        # Advance cursor to avoid re-matching the same specific instance immediately
        # But be careful: if we have overlapping nested entities (rare here), this might skip.
        # For this dataset, usually flat. We update cursor to 's + 1' to find next.
        # Ideally, we update cursor to 's' so next entity can be anywhere after.
        # But if the list is truly sequential, 's' is safe. 
        # Actually, let's keep search_cursor moving forward only if we trust the order.
        # To be safe against list disorder, we only update cursor if the finding was > cursor.
        if s >= search_cursor:
            search_cursor = s 
            
    else:
        print(f"WARNING: Entity not found: {ent['text']}")

# -------------------------------------------------------------------------
# 5. Write to Output Files
# -------------------------------------------------------------------------
# A. ner_dataset_all.jsonl
ner_record = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": found_spans
}

with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_record) + "\n")

# B. notes.jsonl
note_record = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}
with open(OUTPUT_DIR / "notes.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(note_record) + "\n")

# C. spans.jsonl
with open(OUTPUT_DIR / "spans.jsonl", "a", encoding="utf-8") as f:
    for span in found_spans:
        f.write(json.dumps(span) + "\n")

# -------------------------------------------------------------------------
# 6. Update Stats
# -------------------------------------------------------------------------
STATS_FILE = OUTPUT_DIR / "stats.json"
if STATS_FILE.exists():
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    stats = {
        "total_files": 0,
        "successful_files": 0,
        "total_notes": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "label_counts": {}
    }

stats["total_files"] += 1
stats["successful_files"] += 1
stats["total_notes"] += 1
stats["total_spans_raw"] += len(found_spans)
stats["total_spans_valid"] += len(found_spans)

for span in found_spans:
    lbl = span["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(STATS_FILE, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# -------------------------------------------------------------------------
# 7. Validation Logging
# -------------------------------------------------------------------------
log_file = OUTPUT_DIR / "alignment_warnings.log"
with open(log_file, "a", encoding="utf-8") as f:
    for span in found_spans:
        extracted = RAW_TEXT[span["start"]:span["end"]]
        if extracted != span["text"]:
            f.write(f"MISMATCH: {NOTE_ID} - Expected '{span['text']}' but got '{extracted}' at {span['start']}:{span['end']}\n")

print(f"Successfully processed {NOTE_ID}. Added {len(found_spans)} entities.")