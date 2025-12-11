import pandas as pd
import re
import json
import os
import numpy as np

# Define paths
DATA_DIR = "data/ml_training"
FILES_TO_FIX = [
    "registry_train.csv",
    "registry_test.csv",
    "registry_edge_cases.csv"
]
SCHEMA_FILE = os.path.join(DATA_DIR, "registry_label_fields.json")

# 1. Correct Schema (Order matters for some ML loaders, but Pandas handles by name)
REGISTRY_FIELDS = [
    "diagnostic_bronchoscopy", "brushings", "tbna_conventional", "linear_ebus",
    "radial_ebus", "navigational_bronchoscopy", "transbronchial_biopsy",
    "transbronchial_cryobiopsy", "foreign_body_removal", "airway_stent",
    "thermal_ablation", "blvr", "peripheral_ablation", "bronchial_thermoplasty",
    "whole_lung_lavage", "rigid_bronchoscopy", "thoracentesis", "chest_tube",
    "ipc", "medical_thoracoscopy", "pleurodesis", "bal", "therapeutic_aspiration"
]

# 2. Strict Regex Patterns (Compiled for speed and accuracy)
# We use \b to ensure whole word matches (e.g. avoid matching "ball" for "bal")
PATTERNS = {
    "linear_ebus": [r"ebus", r"endobronchial ultrasound", r"station \d", r"convex probe"],
    "radial_ebus": [r"radial ebus", r"radial probe", r"r-ebus", r"rebus", r"concentric", r"eccentric"],
    "navigational_bronchoscopy": [r"navigation", r"electromagnetic", r"veran", r"monarch", r"ion\b", r"robotic", r"superdimension", r"illumisite"],
    "rigid_bronchoscopy": [r"rigid bronch", r"rigid barrel", r"jet ventilation", r"rigid scope"],
    "foreign_body_removal": [r"foreign body", r"peanut", r"aspiration of object", r"removal of object", r"extracted object"],
    "airway_stent": [r"stent", r"dumon", r"silicone", r"metallic stent", r"covered stent", r"stent placement"],
    "transbronchial_biopsy": [r"transbronchial biopsy", r"forceps biopsy", r"tbbx", r"parenchymal biopsy"],
    "transbronchial_cryobiopsy": [r"transbronchial cryobiopsy", r"cryoprobe", r"freezing time"],
    "whole_lung_lavage": [r"whole lung lavage", r"large volume lavage", r"pap\b", r"proteinosis"],
    "blvr": [r"endobronchial valve", r"zephyr", r"spiration", r"lung volume reduction", r"valve placement", r"valve deployment"],
    "medical_thoracoscopy": [r"thoracoscopy", r"pleuroscopy", r"semirigid scope", r"rigid thoracoscope"],
    "pleurodesis": [r"pleurodesis", r"talc", r"sclerosing", r"doxycycline", r"slurry", r"poudrage"],
    "ipc": [r"tunneled pleural catheter", r"pleurx", r"aspira", r"indwelling pleural catheter", r"ipc"],
    "thoracentesis": [r"thoracentesis", r"pleural drainage", r"catheter over needle"],
    "chest_tube": [r"chest tube", r"tube thoracostomy", r"pigtail catheter"],
    "bal": [r"\bbal\b", r"bronchoalveolar lavage", r"bronchial lavage"],
    "thermal_ablation": [r"argon plasma", r"\bapc\b", r"electrocautery", r"laser", r"coagulation", r"debulking"],
    "peripheral_ablation": [r"microwave ablation", r"radiofrequency ablation", r"\bmwa\b", r"\brfa\b"],
    "bronchial_thermoplasty": [r"thermoplasty", r"alair"],
    "therapeutic_aspiration": [r"therapeutic aspiration", r"mucus plug", r"toilet", r"suctioning of secretions"]
}

# 3. Negation/Exclusion Phrases (If these appear near the keyword, ignore it)
NEGATIONS = [
    r"no \w+ was performed",
    r"not performed",
    r"aborted",
    r"ruled out",
    r"without \w+",
    r"history of"
]

def check_flag(text, patterns):
    """Returns 1 if pattern found AND not negated, else 0."""
    for p in patterns:
        if re.search(p, text):
            # Basic negation check (window of 50 chars before match)
            match = re.search(p, text)
            start = max(0, match.start() - 50)
            preceding_text = text[start:match.start()]
            
            is_negated = False
            for neg in NEGATIONS:
                if re.search(neg, preceding_text):
                    is_negated = True
                    break
            
            if not is_negated:
                return 1
    return 0

def process_row(row):
    text = str(row['note_text']).lower()
    
    # Reset all relevant flags to 0 first
    for field in REGISTRY_FIELDS:
        row[field] = 0
        
    # Apply regex logic
    for field, patterns in PATTERNS.items():
        if field in REGISTRY_FIELDS:
            row[field] = check_flag(text, patterns)

    # --- LOGIC OVERRIDES (The "Strict" Rules) ---
    
    # 1. Foreign Body Priority: If foreign body, "forceps" implies extraction, not biopsy.
    if row['foreign_body_removal'] == 1:
        row['transbronchial_biopsy'] = 0
        
    # 2. BLVR Specificity: Do not confuse "therapeutic aspiration" or "volume" with BLVR.
    # (Regex handled this by requiring "valve" or "reduction", but safety check:)
    if 'valve' not in text and 'zephyr' not in text and 'spiration' not in text:
        row['blvr'] = 0
        
    # 3. Stent Specificity: Rigid bronch often checks stents, but doesn't always place them.
    # Only flag stent if "placement", "deployment", or specific brand names found.
    if 'stent' in text and not any(x in text for x in ['plac', 'deploy', 'dumon', 'aero', 'silicone']):
        row['airway_stent'] = 0

    return row

def fix_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename} (not found)")
        return

    print(f"Processing {filename}...")
    df = pd.read_csv(filepath)
    
    # Ensure all columns exist
    for col in REGISTRY_FIELDS:
        if col not in df.columns:
            df[col] = 0
            
    # Apply logic row by row
    df = df.apply(process_row, axis=1)
    
    # Save back
    df.to_csv(filepath, index=False)
    print(f"✓ Fixed {len(df)} rows in {filename}")
    
    # Validation stats
    print("  Positives per class:")
    for col in REGISTRY_FIELDS:
        count = df[col].sum()
        if count > 0:
            print(f"    {col}: {count}")

if __name__ == "__main__":
    # 1. Populate Schema
    with open(SCHEMA_FILE, 'w') as f:
        json.dump(REGISTRY_FIELDS, f, indent=2)
    print(f"✓ Written schema to {SCHEMA_FILE}")

    # 2. Process Files
    for f in FILES_TO_FIX:
        fix_file(f)