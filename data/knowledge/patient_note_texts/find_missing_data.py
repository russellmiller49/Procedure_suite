import json
import os
import glob
import re
import argparse
from pathlib import Path

# ================= CONFIGURATION =================
# Default to the "complete" note text folder in this repo
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_DIR = REPO_ROOT / "data" / "knowledge" / "patient_note_texts_complete"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "reports" / "prioritized_annotation_list.txt"

INPUT_DIR = str(DEFAULT_INPUT_DIR)  # Directory containing your raw .json files
TEXT_KEY = "text"           # Key where the note content is stored (e.g., "text" or "content")

# Define the "High Value" keywords targeting your missing data
# Format: "Category": ["term1", "term2", ...]
TARGETS = {
    "VALVES (Priority 1)": [
        r"valve", r"Zephyr", r"Spiration", r"BLVR", r"atelectasis", 
        r"one-way", r"deployment", r"implant"
    ],
    "PLEURAL (Priority 2)": [
        r"pleural", r"chest tube", r"thoracostomy", r"PleurX", 
        r"Heimlich", r"drainage", r"effusion", r"empyema", r"pleurx"
    ],
    "MEASUREMENTS (Priority 3)": [
        r"cmH2O", r"mm Hg", r"pressure", r"inflation time", 
        r"freeze time", r"Watts", r"Joules", r"\bW\b", # \bW\b matches "W" as a whole word (Watts)
        r"force"
    ],
    "STENTS (Priority 4)": [
        r"stent", r"silicone", r"metallic", r"hybrid", 
        r"migration", r"granulation", r"obstruction"
    ],
    "CATHETERS (Priority 5)": [
        r"\bFr\b", r"French", r"gauge", r"Fogarty", r"dilator", r"cryoprobe"
    ]
}

# specific weights to prioritize certain categories more than others
WEIGHTS = {
    "VALVES (Priority 1)": 5,
    "PLEURAL (Priority 2)": 4,
    "MEASUREMENTS (Priority 3)": 3,
    "STENTS (Priority 4)": 2,
    "CATHETERS (Priority 5)": 1
}

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Scan note JSON files and rank by presence of high-value keywords.")
    ap.add_argument(
        "--input-dir",
        default=INPUT_DIR,
        help=f"Directory containing note JSONs (default: {DEFAULT_INPUT_DIR})",
    )
    ap.add_argument(
        "--glob",
        default="*.json",
        help="Glob pattern for note files (default: *.json).",
    )
    ap.add_argument(
        "--text-key",
        default=TEXT_KEY,
        help="JSON key where note text is stored (default: text).",
    )
    ap.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help=f"Where to write full prioritized list (default: {DEFAULT_OUTPUT_PATH})",
    )
    ap.add_argument(
        "--top",
        type=int,
        default=20,
        help="How many top results to print (default: 20).",
    )
    return ap.parse_args()


def scan_and_rank(input_dir: Path, *, file_glob: str, text_key: str, output_path: Path, top_n: int) -> int:
    files = glob.glob(os.path.join(str(input_dir), file_glob))
    print(f"Scanning {len(files)} files in {input_dir} for high-value keywords...")

    if not files:
        print(
            "\nNo JSON files found.\n"
            f"- Tried: {input_dir}/{file_glob}\n"
            f"- Tip: run with `--input-dir {DEFAULT_INPUT_DIR}` if you intended the repo dataset.\n"
        )
        return 0

    results = []

    for file_path in files:
        filename = os.path.basename(file_path)
        
        # Skip stats or config files
        if "stats" in filename or filename.startswith("fix"):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle cases where data might be a list or dict
                if isinstance(data, list):
                    # If it's a list, join all text parts or pick the first valid one
                    text_content = " ".join([d.get(text_key, "") for d in data if isinstance(d, dict)])
                elif isinstance(data, dict):
                    text_content = data.get(text_key, "")
                else:
                    continue
                
                if not text_content:
                    continue

                # Score the file
                file_score = 0
                found_hits = []

                for category, patterns in TARGETS.items():
                    for pattern in patterns:
                        # Case-insensitive search
                        if re.search(pattern, text_content, re.IGNORECASE):
                            weight = WEIGHTS.get(category, 1)
                            file_score += weight
                            found_hits.append(f"{category}: {pattern}")

                if file_score > 0:
                    results.append({
                        "filename": filename,
                        "score": file_score,
                        "hits": list(set(found_hits)) # unique hits only
                    })

        except Exception as e:
            # print(f"Error reading {filename}: {e}")
            continue

    # Sort results by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)

    # Output Report
    print(f"\nFound {len(results)} relevant files.\n")
    print(f"{'SCORE':<8} | {'FILENAME':<30} | {'TOP KEYWORDS FOUND'}")
    print("-" * 80)

    for r in results[: max(0, top_n)]:  # Show top N
        # Format hits for display (truncate if too long)
        hits_str = ", ".join([h.split(": ")[1] for h in r['hits']])
        if len(hits_str) > 40:
            hits_str = hits_str[:37] + "..."
        
        print(f"{r['score']:<8} | {r['filename']:<30} | {hits_str}")

    # Save full list to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"{r['filename']} (Score: {r['score']})\n")
            f.write(f"  Hits: {', '.join(r['hits'])}\n\n")

    print(f"\nFull prioritized list saved to '{output_path}'")
    return 0

if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(
        scan_and_rank(
            Path(args.input_dir),
            file_glob=args.glob,
            text_key=args.text_key,
            output_path=Path(args.output),
            top_n=args.top,
        )
    )