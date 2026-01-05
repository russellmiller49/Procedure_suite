import json
import re
import glob
from pathlib import Path

# --- Configuration ---
# Where the "bad" (scrubbed) files are
SCRUBBED_DIR = "data/knowledge/golden_extractions_scrubbed"
# Where the "original" (raw) files are (to get the text for Prodigy)
ORIGINAL_DIR = "data/knowledge/golden_extractions"
OUTPUT_FILE = "failures.jsonl"

# Regex patterns for common leaks
LEAK_PATTERNS = [
    (r"\b(19|20)\d{2}\b", "Unredacted Year"),  # 1990-2029
    (r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "Unredacted Date"), # 1/1/2025
    (r"(?i)\b(mr\.|mrs\.|ms\.|dr\.)\s+[A-Z][a-z]+", "Titled Name"), # Mr. Smith
    (r"(?i)\b(patient|pt)\s*:\s*[A-Z][a-z]+", "Header Name"), # Patient: Smith
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN Pattern"),
]

def load_json_robust(path):
    """Helper to load JSON whether it's a dict or a list-wrapped dict."""
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Unwrap list if necessary
    if isinstance(data, list):
        if len(data) > 0:
            return data[0]
        else:
            return {} # Empty list
    return data

def scan_for_failures():
    failures = []
    seen_ids = set()
    
    print(f"Scanning {SCRUBBED_DIR} for leaks...")
    files = glob.glob(f"{SCRUBBED_DIR}/*.json")
    
    if not files:
        print(f"WARNING: No JSON files found in {SCRUBBED_DIR}")
        return

    for file_path in files:
        try:
            # 1. Check the scrubbed file for leaks
            data = load_json_robust(file_path)
            scrubbed_text = data.get('note_text', '')

            if not scrubbed_text:
                continue

            reasons = []
            for pattern, name in LEAK_PATTERNS:
                if re.search(pattern, scrubbed_text):
                    reasons.append(name)

            # 2. If leak found, get ORIGINAL text for Prodigy
            if reasons:
                filename = Path(file_path).name
                original_path = Path(ORIGINAL_DIR) / filename
                
                if original_path.exists():
                    orig_data = load_json_robust(original_path)
                    raw_text = orig_data.get('note_text', '')
                    
                    if raw_text:
                        # Avoid duplicates
                        if filename not in seen_ids:
                            failures.append({
                                "text": raw_text,
                                "meta": {
                                    "file": filename,
                                    "suspected_leaks": ", ".join(reasons)
                                }
                            })
                            seen_ids.add(filename)
                            print(f"Found leak in {filename}: {reasons}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # 3. Write to JSONL
    if failures:
        with open(OUTPUT_FILE, 'w') as out:
            for entry in failures:
                out.write(json.dumps(entry) + "\n")
        print(f"Done. Found {len(failures)} failures. Saved to {OUTPUT_FILE}")
    else:
        print("Done. No leaks found matching patterns.")

if __name__ == "__main__":
    scan_for_failures()