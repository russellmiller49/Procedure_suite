import json
import os
import re
import datetime
from pathlib import Path

# -------------------------------------------------------------------------
# 1. Configuration & Path Setup
# -------------------------------------------------------------------------
NOTE_ID = "note_204"

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------
# 2. Raw Text Data
# -------------------------------------------------------------------------
# Cleaned of source tags and header metadata for the content
RAW_TEXT = """PREOPERATIVE DIAGNOSIS: 
1.	Left mainstem obstruction
POSTOPERATIVE DIAGNOSIS: 
1.	Left mainstem obstruction secondary to stricture and granulation tissue
PROCEDURE PERFORMED: 
CPT 31641: Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with destruction of tumor or relief of stenosis by any method other than excision (eg, laser therapy, cryotherapy)
Bronchoscopy, rigid or flexible, including fluoroscopic guidance, when performed;
with tracheal/bronchial dilation or closed reduction of fracture
CPT 31645 bronchoscopy with therapeutic aspiration
CPT 31502 Tracheotomy tube change
INDICATIONS:  Left mainstem obstruction
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications, details of procedure, and potential risks and alternatives.
The patient acknowledged and gave consent. 
Sedation: General Anesthesia
DESCRIPTION OF PROCEDURE: DESCRIPTION OF PROCEDURE: The procedure was performed in the main operating room.
Following intravenous medications as per the record a laryngeal mask airway was inserted and the tracheoscomy tube removed and the stoma covered.
Topical anesthesia was then applied to the upper airway and the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal.
The tracheostomy stoma was mature without granulation tissue. There was no evidence of TE fistula. The tracheal carina was sharp.
All right sided airways were inspected to at least the first subsegmental bronchi with findings notable for purulent secretions in the superior segment and basilar segments of the right lower lobe with mild extrinsic compression of the superior segment.
The left-sided airways were than inspected. The proximal and mid left mainstem was normal.
In the distal aspect of the left mainstem there was an asymmetrical complex-appearing stricture with area of attached granulation tissue, on a stalk, moving in a ball valve motion with breathing resulting in approximately 90% obstruction.
At this point the only was removed and a 12 mm ventilating rigid bronchoscope was inserted through the mouth into the distal trachea and advanced into the distal trachea before attaching the monsoon JET ventilator.
There is difficulty ventilating the patient with jet ventilation and oxygen saturation dropped requiring rigid bronchoscope to be removed and LMA replaced until saturation increase.
We then reinserted the rigid bronchoscope and had similar problems causing us to convert to closed ventilation with packing of the mouth and nose.
Once we are able to ensure adequate oxygenation and ventilation the FiO2 was decreased until exhaled FiO2 is less than 40% at which time the T190 therapeutic bronchoscope was inserted through the rigid bronchoscope and an electrocautery snare was used to remove the area of granulation tissue without difficulty and there is only minimal bleeding.
Subsequently the electrocautery knife was used to make 2 incisions (2 and 6 o’clock) in the complex-appearing stricture (which is felt to likely be from unrecognized airway trauma at time of injury) after which a phase 8/9/10 Merritt dilatation balloon was used to gently dilate the airway to a maximum diameter of 10 mm.
At this point, the rigid bronchoscope was advanced to the distal left mainstem and inserted through the area of the stricture for further mechanical dilatation.
The rigid bronchoscope was then pulled back to the trachea and on repeat inspection with the flexible bronchoscope the post dilatational orifice was approximately 8 mm with orifice compromised by associated malacia.
There remains significant stricturing of the medial wall however decision was made not to further dilate or inserts sent at this time given plan for him to transfer to long-term neuro rehabilitation facility in Northern California in the next few days.
The rigid bronchoscope was then removed after which a fresh 6.0 cuffed fenestrated Shiley tracheostomy tube was reinserted through his stoma and attached to the ventilator.
Complications: None
Recommendations:
- Return to ICU for recovery 
- Will discuss case with interventional pulmonology at Stamford prior to the patient’s transfer to Palo Alto neuro rehabilitation facility, as repeat dilatation and possibly temporary stent placement will likely be required."""

# -------------------------------------------------------------------------
# 3. Entity Definitions
# -------------------------------------------------------------------------
# Define targets to be found in the text.
# Using a list of (Label, String) or (Label, Regex)
entity_targets = [
    ("ANAT_AIRWAY", "Left mainstem"),
    ("OBS_FINDING", "obstruction"),  # General finding
    ("OBS_LESION", "stricture"),
    ("OBS_LESION", "granulation tissue"),
    ("DEV_INSTRUMENT", "laryngeal mask airway"),
    ("DEV_CATHETER", "tracheoscomy tube"), # Typo in note preserved
    ("ANAT_AIRWAY", "tracheostomy stoma"),
    ("DEV_INSTRUMENT", "Q190 video bronchoscope"),
    ("ANAT_AIRWAY", "tracheobronchial tree"),
    ("ANAT_AIRWAY", "vocal cords"),
    ("ANAT_AIRWAY", "tracheal carina"),
    ("ANAT_AIRWAY", "right sided airways"),
    ("OBS_FINDING", "purulent secretions"),
    ("ANAT_LUNG_LOC", "superior segment"),
    ("ANAT_LUNG_LOC", "basilar segments"),
    ("ANAT_LUNG_LOC", "right lower lobe"),
    ("ANAT_AIRWAY", "left-sided airways"),
    ("ANAT_AIRWAY", "proximal and mid left mainstem"),
    ("ANAT_AIRWAY", "distal aspect of the left mainstem"),
    ("OUTCOME_AIRWAY_LUMEN_PRE", "90% obstruction"),
    ("MEAS_SIZE", "12 mm"),
    ("DEV_INSTRUMENT", "rigid bronchoscope"),
    ("ANAT_AIRWAY", "distal trachea"),
    ("DEV_INSTRUMENT", "monsoon JET ventilator"),
    ("PROC_METHOD", "jet ventilation"),
    ("DEV_INSTRUMENT", "LMA"),
    ("DEV_INSTRUMENT", "T190 therapeutic bronchoscope"),
    ("DEV_INSTRUMENT", "electrocautery snare"),
    ("DEV_INSTRUMENT", "electrocautery knife"),
    ("PROC_ACTION", "incisions"),
    ("DEV_INSTRUMENT", "phase 8/9/10 Merritt dilatation balloon"),
    ("PROC_ACTION", "dilate"),
    ("MEAS_SIZE", "10 mm"),
    ("PROC_ACTION", "dilatation"),
    ("MEAS_AIRWAY_DIAM", "8 mm"),
    ("OBS_FINDING", "malacia"),
    ("MEAS_SIZE", "6.0"),
    ("DEV_CATHETER", "Shiley tracheostomy tube"),
    ("DEV_STENT", "stent"), # Mentioned in recommendations
]

# -------------------------------------------------------------------------
# 4. Entity Extraction Logic
# -------------------------------------------------------------------------
entities = []
_seen_spans = set()

def add_entity(label, start, end, text_str):
    span_key = f"{start}:{end}"
    if span_key not in _seen_spans:
        entities.append({
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text_str,
            "start": start,
            "end": end
        })
        _seen_spans.add(span_key)

# Iterate patterns and find matches
for label, pattern_str in entity_targets:
    # Escape special regex chars if it's a plain string
    pattern = re.compile(re.escape(pattern_str), re.IGNORECASE)
    for match in pattern.finditer(RAW_TEXT):
        add_entity(label, match.start(), match.end(), match.group())

# Sort entities by start index
entities.sort(key=lambda x: x["start"])

# -------------------------------------------------------------------------
# 5. Output Generation
# -------------------------------------------------------------------------

# A. ner_dataset_all.jsonl
ner_entry = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": [
        {"id": e["span_id"], "label": e["label"], "start_offset": e["start"], "end_offset": e["end"]}
        for e in entities
    ]
}

with open(OUTPUT_DIR / "ner_dataset_all.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(ner_entry) + "\n")

# B. notes.jsonl
note_entry = {"id": NOTE_ID, "text": RAW_TEXT}
with open(OUTPUT_DIR / "notes.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(note_entry) + "\n")

# C. spans.jsonl
with open(OUTPUT_DIR / "spans.jsonl", "a", encoding="utf-8") as f:
    for e in entities:
        f.write(json.dumps(e) + "\n")

# D. stats.json
stats_path = OUTPUT_DIR / "stats.json"
if stats_path.exists():
    with open(stats_path, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    stats = {
        "total_notes": 0,
        "total_files": 0,
        "total_spans_raw": 0,
        "total_spans_valid": 0,
        "label_counts": {}
    }

stats["total_notes"] += 1
stats["total_files"] += 1 # Assuming 1 note per file context
stats["total_spans_raw"] += len(entities)
stats["total_spans_valid"] += len(entities)

for e in entities:
    lbl = e["label"]
    stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

with open(stats_path, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

# -------------------------------------------------------------------------
# 6. Validation
# -------------------------------------------------------------------------
log_path = OUTPUT_DIR / "alignment_warnings.log"
with open(log_path, "a", encoding="utf-8") as log_file:
    for e in entities:
        extracted = RAW_TEXT[e["start"]:e["end"]]
        if extracted != e["text"]:
            log_file.write(f"{datetime.datetime.now()} - MISMATCH: ID {NOTE_ID}, Label {e['label']}, Exp '{e['text']}', Got '{extracted}'\n")

print(f"Successfully processed {NOTE_ID}. Output saved to {OUTPUT_DIR}")