from pathlib import Path
import json
import os
import datetime
import re

# Configuration
NOTE_ID = "note_141"
SOURCE_FILENAME = "note_141.txt"

# Raw Text from the provided note
RAW_TEXT = """Preoperative Diagnosis:
Near-complete tracheal occlusion secondary to granulation tissue and severe tracheomalacia

Postoperative Diagnosis:
Near-complete tracheal occlusion secondary to granulation tissue and severe tracheomalacia

Procedure Performed:
Rigid bronchoscopy with silicone Y-stent placement

Indication:
Near-complete tracheal obstruction requiring urgent intervention

Anesthesia:
General anesthesia

Description of Procedure

Informed consent was obtained from the patient prior to the procedure after discussion, in lay terms, of the indications, procedural details, risks, benefits, and alternatives. The patient acknowledged understanding and agreed to proceed.

The procedure was performed in the main operating room. Initial airway inspection was performed using an ultra-slim Olympus P190 flexible bronchoscope inserted through the patient’s customized 5.5-mm tracheostomy tube. At the distal margin of the tracheostomy tube, approximately 2 cm proximal to the main carina, there was a ridge of granulation tissue occluding approximately 80% of the tracheostomy tube lumen. Distal to this obstruction, there was severe tracheobronchial malacia with near-complete collapse of the distal trachea and right mainstem bronchus, and approximately 75% obstruction of the left mainstem bronchus. The airway mucosa was diffusely erythematous and inflamed.

The flexible bronchoscope and tracheostomy tube were removed, and an attempt was made to insert a 14-mm ventilating rigid bronchoscope through the tracheostomy stoma; this was unsuccessful due to the small size of the stoma. The tracheostomy tube was reinserted, and rigid bronchoscopy was then attempted via the oral route. However, the patient had severely distorted upper airway anatomy and significant edema, making visualization of the posterior pharynx and vocal cords impossible. Attempts were made to insert progressively smaller rigid bronchoscopes, down to a 6-mm scope, but these were unsuccessful due to a fixed stricture within the tracheostomy tract. At this point, otolaryngology was consulted intraoperatively for assistance with surgical extension of the tracheostomy stoma. Otolaryngology also attempted visualization of the vocal cords using suspension laryngoscopy but was unsuccessful. The tracheostomy stoma was surgically extended; however, due to extensive scar tissue and concern for injury to the anterior trachea, the stoma could not be enlarged sufficiently to accommodate a large rigid bronchoscope. It was, however, extended enough to allow insertion of smaller rigid bronchoscopes. A 6-mm rigid bronchoscope was inserted through the tracheostomy stoma and advanced to the main carina. Due to the small diameter of the scope, it was not possible to introduce usable instruments or deploy a silicone stent through the rigid bronchoscope. The decision was therefore made to deploy the smallest available silicone Y-stent (14 × 10 × 10 mm) through the tracheostomy stoma. The bronchial limbs were compressed with rigid forceps, and the stent was advanced toward the main carina under direct visualization using a flexible bronchoscope inserted through the left bronchial limb of the stent. After measurement, the tracheal limb was trimmed to 30 mm, the left bronchial limb to 20 mm, and the right bronchial limb to 10 mm. Advancement and seating of the stent were extremely challenging due to the patient’s severely narrowed airways. Multiple techniques were employed, including manipulation with rigid optical forceps, advancement using Kelly clamps by otolaryngology under direct bronchoscopic visualization, gentle balloon dilation using a CRE balloon, and eventual insertion of a slightly larger 8-mm rigid bronchoscope through the tracheostomy stoma and into the stent to help seat the bronchial limbs. During this maneuver, a small airway tear was visualized along the lateral aspect of the right mainstem bronchus, approximately 0.5 cm proximal to the right upper lobe orifice. This was felt to be caused by the distal edge of the right bronchial limb of the stent. Consideration was given to placement of a metallic stent to cover the defect; however, given concerns regarding metallic stents in benign airway disease, this was deferred. The patient received 1 gram of cefazolin intraoperatively. Thoracic surgery was consulted by phone, and based on their experience, recommended conservative management provided there was no evidence of pneumothorax. A portable chest radiograph demonstrated no pneumothorax or pneumomediastinum.

The stent was slightly repositioned to optimize seating at the main carina. There was mild tenting of the distal right bronchial limb at the site of the airway tear that could not be corrected; otherwise, the stent was well seated, with resolution of distal tracheal and mainstem bronchial obstruction and patent distal airways. The patient’s tracheostomy tube was reinserted under direct visualization through the stoma and positioned within the tracheal limb of the stent, where it was secured. The procedure was then concluded, and the patient was transferred to the ICU. Postoperative Course

Upon arrival in the ICU, the patient was initially stable but subsequently developed an episode of acute hypoxia with transient PaO₂ <50%, associated with difficulty ventilating. This resolved rapidly with manual bag ventilation. Flexible bronchoscopy performed through the tracheostomy tube demonstrated no significant stent obstruction, though foamy, blood-tinged secretions were present, consistent with acute pulmonary edema. A chest radiograph obtained during this event showed no pneumothorax. The patient received 20 mg of furosemide intravenously, and the condom catheter was exchanged for a Foley catheter, resulting in brisk diuresis and significant improvement in tidal volumes. Persistently elevated ventilator pressures were felt to be related in part to the small tracheostomy tube. Under bronchoscopic visualization, the tracheostomy tube was exchanged for a 7.0 Bivona tracheostomy tube, which was positioned midway within the stent. This resulted in improved airway compliance and ventilation.

The patient was subsequently deemed stable. After discussion with the patient’s parents, care was transitioned to the ICU team. Complications:
Small lateral right mainstem bronchial tear

Recommendations

Continue positive-pressure ventilation overnight

Empiric vancomycin and piperacillin–tazobactam for 7 days to prevent infection related to airway injury

Obtain noncontrast CT chest once the patient is stable enough for transport

Plan for repeat bedside flexible bronchoscopy on or around 4/1/2019, or sooner if clinical concerns arise

Notify the Interventional Pulmonology team immediately for any airway issues

Note that the silicone stent is radiolucent and will not be visible on chest radiograph; CT or bronchoscopy should be used for evaluation of suspected stent-related complications

Administer 3% saline nebulizers three times daily starting tonight and continuing while the stent remains in place to reduce secretion burden and prevent stent obstruction

If tracheostomy tube removal or replacement is required, this must be performed under direct bronchoscopic visualization to ensure correct positioning within the stent and to avoid kinking or obstruction

Interventional Pulmonology will continue to follow"""

# Label Guide Mappings
# Based on the provided CSV and analysis
ENTITIES_TO_EXTRACT = [
    {"label": "PROC_METHOD", "text": "Rigid bronchoscopy"},
    {"label": "DEV_STENT", "text": "silicone Y-stent"},
    {"label": "DEV_INSTRUMENT", "text": "Olympus P190 flexible bronchoscope"},
    {"label": "DEV_CATHETER_SIZE", "text": "5.5-mm"},
    {"label": "DEV_CATHETER", "text": "tracheostomy tube"},
    {"label": "ANAT_AIRWAY", "text": "main carina"},
    {"label": "OBS_LESION", "text": "granulation tissue"},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "occluding approximately 80%"},
    {"label": "OBS_LESION", "text": "severe tracheobronchial malacia"},
    {"label": "ANAT_AIRWAY", "text": "distal trachea"},
    {"label": "ANAT_AIRWAY", "text": "right mainstem bronchus"},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "approximately 75% obstruction"},
    {"label": "ANAT_AIRWAY", "text": "left mainstem bronchus"},
    {"label": "OBS_FINDING", "text": "erythematous"},
    {"label": "OBS_FINDING", "text": "inflamed"},
    {"label": "DEV_INSTRUMENT", "text": "flexible bronchoscope"},
    {"label": "DEV_INSTRUMENT", "text": "14-mm ventilating rigid bronchoscope"},
    {"label": "ANAT_AIRWAY", "text": "tracheostomy stoma"},
    {"label": "PROC_METHOD", "text": "rigid bronchoscopy"},
    {"label": "ANAT_AIRWAY", "text": "posterior pharynx"},
    {"label": "ANAT_AIRWAY", "text": "vocal cords"},
    {"label": "DEV_INSTRUMENT", "text": "6-mm scope"},
    {"label": "OBS_LESION", "text": "fixed stricture"},
    {"label": "PROC_ACTION", "text": "surgical extension"},
    {"label": "PROC_METHOD", "text": "suspension laryngoscopy"},
    {"label": "OBS_LESION", "text": "scar tissue"},
    {"label": "ANAT_AIRWAY", "text": "anterior trachea"},
    {"label": "DEV_INSTRUMENT", "text": "rigid bronchoscopes"},
    {"label": "DEV_INSTRUMENT", "text": "6-mm rigid bronchoscope"},
    {"label": "DEV_STENT_SIZE", "text": "14 × 10 × 10 mm"},
    {"label": "DEV_INSTRUMENT", "text": "rigid forceps"},
    {"label": "DEV_INSTRUMENT", "text": "rigid optical forceps"},
    {"label": "DEV_INSTRUMENT", "text": "Kelly clamps"},
    {"label": "PROC_METHOD", "text": "balloon dilation"},
    {"label": "DEV_INSTRUMENT", "text": "CRE balloon"},
    {"label": "DEV_INSTRUMENT", "text": "8-mm rigid bronchoscope"},
    {"label": "OUTCOME_COMPLICATION", "text": "airway tear"},
    {"label": "ANAT_AIRWAY", "text": "right upper lobe orifice"},
    {"label": "DEV_STENT", "text": "metallic stent"},
    {"label": "MEDICATION", "text": "cefazolin"},
    {"label": "OUTCOME_COMPLICATION", "text": "pneumothorax"},
    {"label": "OUTCOME_COMPLICATION", "text": "pneumomediastinum"},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "patent distal airways"},
    {"label": "OUTCOME_COMPLICATION", "text": "acute hypoxia"},
    {"label": "PROC_ACTION", "text": "manual bag ventilation"},
    {"label": "PROC_METHOD", "text": "Flexible bronchoscopy"},
    {"label": "OBS_FINDING", "text": "secretions"},
    {"label": "OBS_FINDING", "text": "acute pulmonary edema"},
    {"label": "MEDICATION", "text": "furosemide"},
    {"label": "DEV_CATHETER", "text": "condom catheter"},
    {"label": "DEV_CATHETER", "text": "Foley catheter"},
    {"label": "DEV_CATHETER_SIZE", "text": "7.0"},
    {"label": "DEV_CATHETER", "text": "Bivona tracheostomy tube"},
    {"label": "MEDICATION", "text": "vancomycin"},
    {"label": "MEDICATION", "text": "piperacillin"},
    {"label": "MEDICATION", "text": "tazobactam"},
    {"label": "PROC_METHOD", "text": "CT chest"},
    {"label": "MEDICATION", "text": "3% saline"},
    {"label": "DEV_STENT_MATERIAL", "text": "silicone"},
    {"label": "MEAS_SIZE", "span_text": "2 cm"},
    {"label": "MEAS_SIZE", "span_text": "0.5 cm"}
]

def generate_spans(text, entities):
    spans = []
    # Use a case-insensitive search to be robust, though text provided is exact.
    # We iterate through the text to find matches.
    
    # We maintain a list of occupied indices to avoid overlapping spans if necessary,
    # though the requirement is to extract all valid ones.
    
    # Sort entities by length (descending) to prioritize specific matches if needed
    # but here we just need to find all occurrences.
    
    for item in entities:
        label = item["label"]
        span_text = item.get("text") or item.get("span_text")
        
        if not span_text:
            continue

        # Find all occurrences
        for match in re.finditer(re.escape(span_text), text):
            start = match.start()
            end = match.end()
            
            # Create the span object
            span = {
                "span_id": f"{label}_{start}",
                "note_id": NOTE_ID,
                "label": label,
                "text": span_text,
                "start": start,
                "end": end
            }
            spans.append(span)
            
    # Sort spans by start index
    spans = sorted(spans, key=lambda x: x["start"])
    return spans

def main():
    # 1. Path Setup
    # Script location: data/granular annotations/Python_update_scripts/
    # Target location: data/ml_training/granular_ner/
    OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    ner_dataset_file = OUTPUT_DIR / "ner_dataset_all.jsonl"
    notes_file = OUTPUT_DIR / "notes.jsonl"
    spans_file = OUTPUT_DIR / "spans.jsonl"
    stats_file = OUTPUT_DIR / "stats.json"
    log_file = OUTPUT_DIR / "alignment_warnings.log"

    # 2. Generate Spans
    extracted_spans = generate_spans(RAW_TEXT, ENTITIES_TO_EXTRACT)
    
    # Deduplicate spans (exact duplicates of start/end/label)
    unique_spans = []
    seen = set()
    for span in extracted_spans:
        ident = (span['start'], span['end'], span['label'])
        if ident not in seen:
            seen.add(ident)
            unique_spans.append(span)
    
    # 3. Update ner_dataset_all.jsonl
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": unique_spans
    }
    
    with open(ner_dataset_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")

    # 4. Update notes.jsonl
    note_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    with open(notes_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_entry) + "\n")

    # 5. Update spans.jsonl
    with open(spans_file, "a", encoding="utf-8") as f:
        for span in unique_spans:
            f.write(json.dumps(span) + "\n")

    # 6. Update stats.json
    if stats_file.exists():
        with open(stats_file, "r", encoding="utf-8") as f:
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
    # Assuming 1 file per note in this context, or incrementing processed files
    stats["total_files"] += 1 
    stats["total_spans_raw"] += len(unique_spans)
    stats["total_spans_valid"] += len(unique_spans)

    for span in unique_spans:
        lbl = span["label"]
        stats["label_counts"][lbl] = stats["label_counts"].get(lbl, 0) + 1

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    # 7. Validate & Log
    with open(log_file, "a", encoding="utf-8") as log:
        for span in unique_spans:
            text_slice = RAW_TEXT[span["start"]:span["end"]]
            if text_slice != span["text"]:
                log.write(f"[{datetime.datetime.now().isoformat()}] MISMATCH {NOTE_ID}: "
                          f"Label '{span['label']}' indices [{span['start']}:{span['end']}] "
                          f"extract '{text_slice}' != expected '{span['text']}'\n")

if __name__ == "__main__":
    main()