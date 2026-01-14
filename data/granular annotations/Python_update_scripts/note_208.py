import json
import re
from pathlib import Path
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
NOTE_ID = "note_208"

# Reconstructed raw text from the provided source snippets (cleaning source tags)
RAW_TEXT = """Indications: Diagnosis and staging of presumed lung cancer
Medications: General Anesthesia,
Consent was obtained from the patient prior to procedure after explanation in lay terms the indications,
details of procedure, and potential risks and alternatives.
All questions were answered and informed consent was documented as per institutional protocol.
A history and physical were performed and updated in the pre-procedure assessment record. Laboratory studies and radiographs were reviewed.
A time-out was performed prior to the intervention.
Following intravenous medications as per the record and topical anesthesia to the upper airway and
tracheobronchial tree, the T190 video bronchoscope was introduced through the mouth, via laryngeal
mask airway and advanced to the tracheobronchial tree.
The laryngeal mask airway was in good position. The vocal cords appeared normal. The subglottic space was normal.
The trachea was of normal caliber. The carina was sharp. The tracheobronchial tree was examined to at least the first subsegmental level.
Left sided bronchial mucosa and anatomy were normal; without endobronchial lesions, or secretions.
Within the right mainstem mucosal irregularities and mild compression of the right upper
lobe segmental bronchi was seen.
Gross submucosal infiltration of tumor was seen in the mid to distal
bronchus intermedius extending into the right middle lobe and right lower lobe causing >
80% obstruction of the right middle lobe orifice, and right lower lobe basilar segments and complete
obstruction of the superior segment of the right lower lobe.
The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal
mask airway and advanced to the tracheobronchial tree.
A systematic hilar and mediastinal lymph node survey was carried out.
Sampling criteria (5mm short axis diameter) were met in station 4L, 7 and 4R lymph nodes.
The N1 lymph nodes were not measured due to tumor invasion.
The EBUS scope was inserted into the right lower lobe orifice and positioned laterally allowing visualization of the completely
obstructed right intralobar pulmonary artery.
Tumor infiltration could be seen within the vessel with progressive tapering of the patent artery.
Surrounding tumor could also be seen with the linear EBUS outside of the vessel wall.
Sampling by transbronchial needle aspiration was performed with the
Olympus EBUS Visioshot 2 19G and 25G needles beginning with the 4L Lymph node, followed by the 7
and then 4R.
A total of 5 biopsies was performed at each station.
ROSE reported as benign lymphocytes in the 4L and 4R and non-diagnostic in the station 7. All samples were sent for routine cytology.
The EBUS bronchoscope was then repositioned at the level of the right hilar lobe/PA mass.
EBUS guided TBNA was performed in the mass distal to the cessation of blood flow from the PA.
ROSE was reported as benign lymphocytes. A total of 5 biopsies of the mass was performed.
Following completion of EBUS bronchoscopy, the T190 video bronchoscope was then re-inserted into the airway.
A large clot completely obstructed the right sided airways. After suctioning the clot active bleeding was encountered
originating from the superior segment of the right lower lobe.
Blood was suctioned and we were able to perform two endobronchial forceps biopsies of the right middle lobe carina as well as one
endobronchial brushing of the submucosal tumor within the BI.
Bleeding however continued from the superior segment despite attempts to control the bleeding with wedging of the bronchoscope into the
bleeding segment, endobronchial epinephrine (5cc 2% lidocaine with epi) and endobronchial TXA (100mg).
The LMA was then removed, and the patient was intubated bronchoscopically with an 8.5 ETT.
An Arndt endobronchial blocker was then inserted into the distal right mainstem and inflated to prevent
blood soiling of the left sided airways.
After clearing residual blood from the left sided airways the patient was transferred to the ICU with the endobronchial blocker in place.
Complications: Hemoptysis requiring endobronchial blocker and ICU admission.
Estimated Blood Loss: 50cc

Post Procedure Recommendations:
- Admit to ICU
- CXR upon arrival in ICU and in AM
- Keep endobronchial blocker inflated overnight
- In issues with ventilation occur, confirm blocker has not migrated into the trachea (vis bronchoscopy with pediatric scope)
- Technical aspects of repositioning were discussed with the ICU team.
- In AM if no overnight issues would deflate the balloon and if bleeding has stopped remove blocker and extubate.
- Await final path
Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.
- The patient has remained stable and has been transferred in good condition to the post-surgical monitoring unit.
- Please call if any questions or concerns
- Will await final pathology results"""

# Define target entities based on Label_guide_UPDATED.csv
# Order matters for simple find: specific first, then general.
TARGETS = [
    ("tracheobronchial tree", "ANAT_AIRWAY"),
    ("T190 video bronchoscope", "PROC_METHOD"),
    ("trachea", "ANAT_AIRWAY"),
    ("carina", "ANAT_AIRWAY"),
    ("Left sided bronchial", "ANAT_AIRWAY"),
    ("right mainstem", "ANAT_AIRWAY"),
    ("right upper lobe", "ANAT_LUNG_LOC"),
    ("tumor", "OBS_LESION"),
    ("bronchus intermedius", "ANAT_AIRWAY"),
    ("right middle lobe", "ANAT_LUNG_LOC"),
    ("right lower lobe", "ANAT_LUNG_LOC"),
    ("> 80% obstruction", "OUTCOME_AIRWAY_LUMEN_PRE"), # Normalized form
    ("UC180F convex probe EBUS bronchoscope", "PROC_METHOD"),
    ("station 4L", "ANAT_LN_STATION"),
    ("station 4R", "ANAT_LN_STATION"), # Matches "station 4L, 7 and 4R" context logic
    ("5mm", "MEAS_SIZE"),
    ("N1 lymph nodes", "ANAT_LN_STATION"),
    ("transbronchial needle aspiration", "PROC_ACTION"),
    ("19G", "DEV_NEEDLE"),
    ("25G", "DEV_NEEDLE"),
    ("5 biopsies", "MEAS_COUNT"),
    ("benign lymphocytes", "OBS_ROSE"),
    ("EBUS guided TBNA", "PROC_ACTION"),
    ("clot", "OBS_FINDING"), # Matches general clinical findings
    ("forceps", "DEV_INSTRUMENT"),
    ("biopsies", "PROC_ACTION"),
    ("brushing", "PROC_ACTION"),
    ("epinephrine", "MEDICATION"),
    ("lidocaine", "MEDICATION"),
    ("TXA", "MEDICATION"),
    ("Arndt endobronchial blocker", "DEV_INSTRUMENT"),
    ("Hemoptysis", "OUTCOME_COMPLICATION"),
    ("50cc", "MEAS_VOL")
]

# Special handling for "7" in "station 4L, 7 and 4R"
# We will manually add this to avoid matching every "7" in text
MANUAL_SPANS = [
    # (Label, Text, Context_Window_Start, Context_Window_End)
    # Finding "7" between "station 4L, " and " and 4R"
    ("ANAT_LN_STATION", "7", "station 4L, ", " and 4R")
]

# Path Setup
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NOTES_FILE = OUTPUT_DIR / "notes.jsonl"
NER_DATASET_FILE = OUTPUT_DIR / "ner_dataset_all.jsonl"
SPANS_FILE = OUTPUT_DIR / "spans.jsonl"
STATS_FILE = OUTPUT_DIR / "stats.json"
LOG_FILE = OUTPUT_DIR / "alignment_warnings.log"

# ==========================================
# 2. PROCESSING LOGIC
# ==========================================

def find_offsets(text, targets, manual_spans):
    entities = []
    # Search for simple targets
    for target_text, label in targets:
        # Normalize target for search (handle newlines in raw text if needed)
        # We will search literally first
        search_text = target_text.replace("\n", " ").replace(">", "&gt;") if ">" in target_text else target_text
        
        # If strict literal match fails, try regex for whitespace variations
        pattern = re.escape(target_text).replace(r'\ ', r'\s+')
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entities.append({
                "label": label,
                "text": match.group(),
                "start": match.start(),
                "end": match.end()
            })
            
    # Handle manual context-aware spans
    for label, target_text, prefix, suffix in manual_spans:
        pattern = re.escape(prefix) + r"(" + re.escape(target_text) + r")" + re.escape(suffix)
        for match in re.finditer(pattern, text):
            # match.group(1) is the target
            start = match.start(1)
            end = match.end(1)
            entities.append({
                "label": label,
                "text": match.group(1),
                "start": start,
                "end": end
            })
            
    # Sort by start index
    entities = sorted(entities, key=lambda x: x['start'])
    
    # Deduplicate (keep first valid if exact overlap, though logic above allows overlaps)
    # Simple logic: allow overlaps for now as they might be distinct concepts
    return entities

def update_files():
    # 1. Generate Entity List
    entities_found = find_offsets(RAW_TEXT, TARGETS, MANUAL_SPANS)
    
    # 2. Prepare Data Objects
    note_obj = {
        "id": NOTE_ID,
        "text": RAW_TEXT
    }
    
    ner_entry = {
        "id": NOTE_ID,
        "text": RAW_TEXT,
        "entities": [
            {
                "label": e["label"],
                "start": e["start"],
                "end": e["end"]
            }
            for e in entities_found
        ]
    }
    
    span_lines = []
    for e in entities_found:
        span_id = f"{e['label']}_{e['start']}"
        span_obj = {
            "span_id": span_id,
            "note_id": NOTE_ID,
            "label": e["label"],
            "text": e["text"],
            "start": e["start"],
            "end": e["end"]
        }
        span_lines.append(span_obj)
        
    # 3. Write to JSONL Files
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(note_obj) + "\n")
        
    with open(NER_DATASET_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ner_entry) + "\n")
        
    with open(SPANS_FILE, "a", encoding="utf-8") as f:
        for span in span_lines:
            f.write(json.dumps(span) + "\n")
            
    # 4. Update Stats
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
        
    stats["total_files"] += 1
    stats["total_notes"] += 1
    stats["total_spans_raw"] += len(entities_found)
    stats["total_spans_valid"] += len(entities_found)
    
    for e in entities_found:
        lbl = e["label"]
        if lbl in stats["label_counts"]:
            stats["label_counts"][lbl] += 1
        else:
            stats["label_counts"][lbl] = 1
            
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    # 5. Validation & Logging
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        for e in entities_found:
            extracted = RAW_TEXT[e["start"]:e["end"]]
            if extracted != e["text"]:
                log.write(f"[{datetime.now()}] ALIGNMENT WARNING: Note {NOTE_ID}, Label {e['label']}. "
                          f"Expected '{e['text']}', found '{extracted}' at {e['start']}:{e['end']}\n")

if __name__ == "__main__":
    update_files()
    print(f"Successfully processed {NOTE_ID} and updated datasets.")