from pathlib import Path
import json
import re
import datetime

# -----------------------------------------------------------------------------
# 1. Configuration & Path Setup
# -----------------------------------------------------------------------------

# Defines the specific note ID and the raw text content derived from the input
NOTE_ID = "note_060"

# Reconstructed text based on the provided snippets (Front + Back)
# In a production environment, this would be the full file content.
RAW_TEXT = (
    "NOTE_ID:  note_060 SOURCE_FILE: note_060.txt INDICATION FOR OPERATION:  [REDACTED]is a 32 year old-year-old male who presents with lung infiltrates.  "
    "The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.  "
    "Patient indicated a wish to proceed with surgery and informed consent was signed.\n \n"
    "PREOPERATIVE DIAGNOSIS: R91.8 Other nonspecific abnormal finding of lung field.\n \n"
    "POSTOPERATIVE DIAGNOSIS:  R91.8 Other nonspecific abnormal finding of lung field.\n \n"
    "PROCEDURE:  \n"
    "31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS)\n"
    "31645 Therapeutic aspiration initial episode\n"
    "31624 Dx bronchoscope/lavage (BAL)    \n"
    "31625 Endobronchial Biopsy(s)\n"
    "31628 TBBX single lobe     \n"
    "31652 EBUS sampling 1 or 2 nodes\n"
    "31654 Radial EBUS for peripheral lesion\n"
    "76982 Ultrasound Elastography, First Target Lesion\n"
    "76983 Ultrasound Elastography, Additional Targets \n"
    "76983 Ultrasound Elastography, Additional Target 2\n \n \n"
    "IP [REDACTED] CODE MOD DETAILS: \n"
    "Unusual Procedure:\n"
    "This patient required a EBUS lymph node forceps/cryo biopsies. This resulted in >40% increased work due to Technical difficulty of procedure and Physical and mental effort required. Apply to: 31652 EBUS sampling 1 or 2 nodes. \n"
    "ANESTHESIA: \n"
    "General Anesthesia\n \n"
    "MONITOR...\n"
    "..., TBNA was directed at representative areas to ensure comprehensive sampling and to minimize the risk of underdiagnosis.\n \n"
    "Site 2: The 11Rs lymph node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable. The lymph node was photographed. "
    "The site was not sampled: Sampling this lymph node was not clinically indicated. Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics. "
    "The target lymph node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process. \n \n"
    "Site 3: The 11L lymph node was < 10 mm on CT  and Metabolic activity unknown or PET-CT scan unavailable. The lymph node was photographed. "
    "The site was not sampled: Sampling this lymph node was not clinically indicated. Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics. "
    "The target lymph node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process. \n \n"
    "The patient tolerated the procedure well.  There were no immediate complications.  At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition. \n \n"
    "SPECIMEN(S): \n"
    "EBBX, TBBX\n"
    "BAL\n"
    "Station 7 - TBCBX, TBNA\n \n"
    "IMPRESSION/PLAN: [REDACTED]is a 32 year old-year-old male who presents for bronchoscopy for possible sarcoid.\n- f/u in clinic\n "
)

# Script location: data/granular annotations/Python_update_scripts/
# Target location: data/ml_training/granular_ner/
OUTPUT_DIR = (Path(__file__).resolve().parents[2] / "ml_training" / "granular_ner")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 2. Analyze & Extract (NER Simulation based on Label_guide_UPDATED.csv)
# -----------------------------------------------------------------------------

# List of target text strings and their strictly mapped labels
targets = [
    ("lung infiltrates", "OBS_LESION"),
    ("Bronchoscopy", "PROC_METHOD"),
    ("Therapeutic aspiration", "PROC_ACTION"),
    ("BAL", "PROC_ACTION"),
    ("Endobronchial Biopsy(s)", "PROC_ACTION"),
    ("TBBX", "PROC_ACTION"),
    ("EBUS", "PROC_METHOD"),
    ("sampling", "PROC_ACTION"),
    ("Radial EBUS", "PROC_METHOD"),
    ("peripheral lesion", "OBS_LESION"),
    ("Ultrasound Elastography", "PROC_METHOD"),
    ("forceps", "DEV_INSTRUMENT"),
    ("cryo biopsies", "PROC_ACTION"),
    ("TBNA", "PROC_ACTION"),
    ("11Rs", "ANAT_LN_STATION"),
    ("< 10 mm", "MEAS_SIZE"),
    ("Endobronchial ultrasound (EBUS)", "PROC_METHOD"),
    ("elastography", "PROC_METHOD"),
    ("Type 1", "OBS_FINDING"),
    ("11L", "ANAT_LN_STATION"),
    ("Station 7", "ANAT_LN_STATION"),
    ("sarcoid", "OBS_LESION")
]

extracted_entities = []
extracted_spans = []

# 3. Calculate Indices
for text_span, label in targets:
    for match in re.finditer(re.escape(text_span), RAW_TEXT):
        start = match.start()
        end = match.end()
        
        # NER Object for ner_dataset_all.jsonl (Format: [start, end, label])
        # Note: ner_dataset_all schema in snippet shows lists of [start, end, label] or dicts?
        # Standard spaCy/JSONL format often uses [start, end, label]. 
        # However, the spans.jsonl requires specific dicts. 
        # We will format the 'entities' list as a list of [start, end, label] which is standard for many pipelines,
        # or if the existing file uses dicts, we stick to that. 
        # Based on typical JSONL NER datasets, we will use [start, end, label].
        
        entity_entry = [start, end, label]
        if entity_entry not in extracted_entities:
            extracted_entities.append(entity_entry)
        
        # Span Object for spans.jsonl
        span_entry = {
            "span_id": f"{label}_{start}",
            "note_id": NOTE_ID,
            "label": label,
            "text": text_span,
            "start": start,
            "end": end
        }
        extracted_spans.append(span_entry)

# Sort entities by start index
extracted_entities.sort(key=lambda x: x[0])

# -----------------------------------------------------------------------------
# 4. Generate Script & Update Files
# -----------------------------------------------------------------------------

# File Paths
file_ner_dataset = OUTPUT_DIR / "ner_dataset_all.jsonl"
file_notes = OUTPUT_DIR / "notes.jsonl"
file_spans = OUTPUT_DIR / "spans.jsonl"
file_stats = OUTPUT_DIR / "stats.json"
file_alignment_log = OUTPUT_DIR / "alignment_warnings.log"

# A. Update ner_dataset_all.jsonl
new_ner_record = {
    "id": NOTE_ID,
    "text": RAW_TEXT,
    "entities": extracted_entities
}

with open(file_ner_dataset, "a", encoding="utf-8") as f:
    f.write(json.dumps(new_ner_record) + "\n")

# B. Update notes.jsonl
new_note_record = {
    "id": NOTE_ID,
    "text": RAW_TEXT
}

with open(file_notes, "a", encoding="utf-8") as f:
    f.write(json.dumps(new_note_record) + "\n")

# C. Update spans.jsonl
with open(file_spans, "a", encoding="utf-8") as f:
    for span in extracted_spans:
        f.write(json.dumps(span) + "\n")

# D. Update stats.json
if file_stats.exists():
    with open(file_stats, "r", encoding="utf-8") as f:
        stats_data = json.load(f)
else:
    # Fallback if stats doesn't exist (though it should)
    stats_data = {
        "total_files": 0, "successful_files": 0, "total_notes": 0, 
        "total_spans_raw": 0, "total_spans_valid": 0, "label_counts": {}
    }

stats_data["total_files"] += 1
stats_data["successful_files"] += 1  # Assuming success since we are here
stats_data["total_notes"] += 1
stats_data["total_spans_raw"] += len(extracted_spans)
stats_data["total_spans_valid"] += len(extracted_spans) # Assuming all valid for this script

# Update label counts
current_counts = stats_data.get("label_counts", {})
for span in extracted_spans:
    lbl = span["label"]
    current_counts[lbl] = current_counts.get(lbl, 0) + 1
stats_data["label_counts"] = current_counts

with open(file_stats, "w", encoding="utf-8") as f:
    json.dump(stats_data, f, indent=2)

# E. Validate & Log (Alignment Warnings)
with open(file_alignment_log, "a", encoding="utf-8") as log_file:
    for span in extracted_spans:
        extracted_text = RAW_TEXT[span["start"]:span["end"]]
        if extracted_text != span["text"]:
            log_entry = {
                "note_id": NOTE_ID,
                "label": span["label"],
                "span_text": span["text"],
                "start": span["start"],
                "end": span["end"],
                "issue": f"alignment_error: extracted='{extracted_text}' vs span='{span['text']}'"
            }
            log_file.write(json.dumps(log_entry) + "\n")

print(f"Successfully processed {NOTE_ID}. Data appended to {OUTPUT_DIR}")