import csv
import json
import os

FILES = [
    "data/ml_training/registry_train.csv",
    "data/ml_training/registry_test.csv",
    "data/ml_training/registry_edge_cases.csv"
]

# The 28 binary flags identified from the CSV header
LABELS = [
    "diagnostic_bronchoscopy",
    "bal",
    "bronchial_wash",
    "brushings",
    "endobronchial_biopsy",
    "tbna_conventional",
    "linear_ebus",
    "radial_ebus",
    "navigational_bronchoscopy",
    "transbronchial_biopsy",
    "transbronchial_cryobiopsy",
    "therapeutic_aspiration",
    "foreign_body_removal",
    "airway_dilation",
    "airway_stent",
    "thermal_ablation",
    "cryotherapy",
    "blvr",
    "peripheral_ablation",
    "bronchial_thermoplasty",
    "whole_lung_lavage",
    "rigid_bronchoscopy",
    "thoracentesis",
    "chest_tube",
    "ipc",
    "medical_thoracoscopy",
    "pleurodesis",
    "fibrinolytic_therapy"
]

def process_text(text):
    text_lower = text.lower()
    
    # 1. Default to 0
    flags = {label: 0 for label in LABELS}

    # 2. Strict Keyword Matching (Positive Triggers)
    
    # linear_ebus
    if (("ebus" in text_lower and "station" in text_lower) or 
        "lymph node sampling" in text_lower):
        flags["linear_ebus"] = 1
        
    # rigid_bronchoscopy
    if ("rigid bronch" in text_lower or "jet ventilation" in text_lower):
        flags["rigid_bronchoscopy"] = 1
        
    # airway_stent
    # Note: "dumon" and "silicone stent" are specific types
    if ("stent placed" in text_lower or 
        "stent deployment" in text_lower or 
        "dumon" in text_lower or 
        "silicone stent" in text_lower):
        flags["airway_stent"] = 1
        
    # blvr
    if ("valve placement" in text_lower or 
        "zephyr" in text_lower or 
        "spiration" in text_lower or 
        "lung volume reduction" in text_lower):
        flags["blvr"] = 1
        
    # transbronchial_biopsy
    if ("transbronchial biopsy" in text_lower or 
        "bx" in text_lower or 
        "forceps" in text_lower):
        flags["transbronchial_biopsy"] = 1
        
    # foreign_body_removal
    if ("foreign body" in text_lower or 
        "peanut" in text_lower or 
        "removed object" in text_lower):
        flags["foreign_body_removal"] = 1
        
    # 3. "Draconian" Exclusion (Negative Overrides)
    
    # blvr overrides
    if ("no valve placed" in text_lower or 
        "valve placement was not performed" in text_lower or 
        "aborted" in text_lower):
        flags["blvr"] = 0
        
    if ("pneumonia" in text_lower or "atelectasis" in text_lower):
        flags["blvr"] = 0
        
    # airway_stent overrides
    # If text contains "foreign body" OR "removed", THEN FORCE airway_stent = 0 
    # (unless "stent placed" is explicitly found).
    if ("foreign body" in text_lower or "removed" in text_lower):
        if "stent placed" not in text_lower:
            flags["airway_stent"] = 0
            
    # transbronchial_biopsy overrides
    if ("not biopsied" in text_lower or "no biopsy" in text_lower):
        flags["transbronchial_biopsy"] = 0
        
    return flags

def process_file(file_path):
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} (not found)")
        return

    print(f"Processing {file_path}...")
    rows = []
    fieldnames = []
    
    # Read
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print(f"Empty header in {file_path}")
            return
            
        for row in reader:
            # Assumes 'note_text' is the column containing the procedure text
            text = row.get("note_text", "")
            
            # Calculate new flags
            new_flags = process_text(text)
            
            # Update row
            for label in LABELS:
                if label in fieldnames:
                    row[label] = new_flags[label]
                # If label not in fieldnames, we ignore it (don't add columns)
            
            rows.append(row)
            
    # Write
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Finished updating {file_path}")

def main():
    # Process the CSVs
    for f in FILES:
        process_file(f)
        
    # 4. Schema Repair
    # Write the list of 28 flag names into data/ml_training/registry_label_fields.json
    json_path = "data/ml_training/registry_label_fields.json"
    try:
        with open(json_path, 'w') as f:
            json.dump(LABELS, f, indent=2)
        print(f"Created {json_path}")
    except Exception as e:
        print(f"Error creating JSON schema: {e}")

if __name__ == "__main__":
    main()
