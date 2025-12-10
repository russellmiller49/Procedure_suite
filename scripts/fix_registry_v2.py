import pandas as pd
import re
import json
import os

# --- Configuration ---
FILES = [
    "data/ml_training/registry_train.csv",
    "data/ml_training/registry_test.csv",
    "data/ml_training/registry_edge_cases.csv"
]
LABEL_FILE = "data/ml_training/registry_label_fields.json"

# --- Schema Definition ---
# The 28 keys identified in the previous step
ALL_LABELS = [
    "airway_dilation", "airway_stent", "bal", "blvr", "bronchial_thermoplasty", 
    "bronchial_wash", "brushings", "chest_tube", "cryotherapy", "diagnostic_bronchoscopy", 
    "endobronchial_biopsy", "fibrinolytic_therapy", "foreign_body_removal", "ipc", 
    "linear_ebus", "medical_thoracoscopy", "navigational_bronchoscopy", "peripheral_ablation", 
    "pleurodesis", "radial_ebus", "rigid_bronchoscopy", "tbna_conventional", 
    "therapeutic_aspiration", "thermal_ablation", "thoracentesis", "transbronchial_biopsy", 
    "transbronchial_cryobiopsy", "whole_lung_lavage"
]

class SmartKeywordMatcher:
    def __init__(self):
        # Define keywords for each label
        # Order matters? Not for independent flags.
        self.rules = {
            "linear_ebus": ["linear ebus", "station", "endobronchial ultrasound", "ebus"],
            "radial_ebus": ["radial ebus", "radial probe", "r-ebus", "rebus"],
            "rigid_bronchoscopy": ["rigid bronch", "rigid scope", "jet ventilation"],
            "foreign_body_removal": ["foreign body", "peanut", "object removal", "extraction"],
            "bal": ["bal", "lavage", "wash", "bronchoalveolar"],
            "bronchial_wash": ["bronchial wash", "washing"],
            "brushings": ["brush"],
            "endobronchial_biopsy": ["endobronchial biopsy", "ebb"],
            "tbna_conventional": ["tbna", "transbronchial needle aspiration"],
            "navigational_bronchoscopy": ["navigation", "ion", "monarch", "veran", "superdimension", "enb", "electromagnetic"],
            "transbronchial_biopsy": ["transbronchial biopsy", "tbbx", "tbb", "biopsy", "bx", "forceps", "sampling"],
            "transbronchial_cryobiopsy": ["cryobiopsy", "cryo biopsy"],
            "therapeutic_aspiration": ["therapeutic aspiration", "mucus plug", "suctioning"],
            "airway_dilation": ["dilation", "balloon", "dilator", "cre"],
            "airway_stent": ["stent", "prosthesis", "dumon", "silicone", "metallic"],
            "thermal_ablation": ["apc", "argon plasma", "laser", "electrocautery", "cautery"],
            "cryotherapy": ["cryotherapy", "cryo ablation", "cryo recanalization"], # Removed generic "cryo" to avoid overlap with cryobiopsy
            "blvr": ["valve", "zephyr", "spiration", "endobronchial valve"],
            "peripheral_ablation": ["microwave", "mwa", "rf ablation", "radiofrequency"],
            "bronchial_thermoplasty": ["thermoplasty"],
            "whole_lung_lavage": ["whole lung lavage"],
            "thoracentesis": ["thoracentesis"],
            "chest_tube": ["chest tube", "thoracostomy"],
            "ipc": ["indwelling pleural catheter", "ipc", "pleurx", "tunneled catheter"],
            "medical_thoracoscopy": ["thoracoscopy", "pleuroscopy"],
            "pleurodesis": ["pleurodesis", "talc", "doxycycline"],
            "fibrinolytic_therapy": ["tpa", "dnase", "fibrinolytic"],
            "diagnostic_bronchoscopy": ["diagnostic bronchoscopy", "inspection", "airway survey"]
        }
        
        # Negation triggers (lookbehind window)
        self.negation_patterns = [
            r"\bno\b",
            r"\bnot\b",
            r"\bwithout\b",
            r"\bdenies\b",
            r"\bru led\s+out\b",
            r"\bnegative\s+for\b",
            r"\bhistory\s+of\b"
        ]
        self.negation_regex = re.compile("|".join(self.negation_patterns), re.IGNORECASE)

    def is_negated(self, text, start_index, window=35):
        """Check if a negation term exists in the window characters before match."""
        snippet = text[max(0, start_index - window):start_index]
        return bool(self.negation_regex.search(snippet))

    def predict(self, text):
        if not isinstance(text, str):
            text = ""
        text = text.lower() # Normalization
        
        results = {label: 0 for label in ALL_LABELS}
        
        for label, keywords in self.rules.items():
            # Check for label existence
            label_found = False
            for kw in keywords:
                # Use regex word boundary where appropriate or simple find?
                # Using find for simplicity but checking boundaries for short words would be better.
                # Given instructions, substring match is implied for things like "ion" (might be in 'location'?).
                # "ion" is dangerous as substring. "station" is dangerous. 
                # Let's use word boundaries for short keywords.
                
                if len(kw) <= 4:
                    pattern = r"\b" + re.escape(kw) + r"\b"
                else:
                    pattern = re.escape(kw)
                
                matches = list(re.finditer(pattern, text))
                for match in matches:
                    if not self.is_negated(text, match.start()):
                        label_found = True
                        break
                if label_found:
                    break
            
            if label_found:
                results[label] = 1
                
        return results

def main():
    matcher = SmartKeywordMatcher()
    
    # 1. Update Schema
    print(f"Updating Schema: {LABEL_FILE}")
    with open(LABEL_FILE, "w") as f:
        json.dump(ALL_LABELS, f, indent=2)
    
    # 2. Process Files
    for file_path in FILES:
        if not os.path.exists(file_path):
            print(f"Skipping {file_path} (Not Found)")
            continue
            
        print(f"Processing {file_path}...")
        df = pd.read_csv(file_path)
        
        if "note_text" not in df.columns:
            print(f"  Error: 'note_text' column missing in {file_path}")
            continue
            
        # Initialize/Overwrite label columns
        for label in ALL_LABELS:
            df[label] = 0
            
        # Apply Logic
        # We process row by row to allow debug/logic flexibility
        new_rows = []
        for idx, row in df.iterrows():
            text = row.get("note_text", "")
            flags = matcher.predict(text)
            for k, v in flags.items():
                df.at[idx, k] = v
        
        # Save
        df.to_csv(file_path, index=False)
        print(f"  Saved {len(df)} rows.")

    print("\nRegistry Data Repair Complete (v2).")

if __name__ == "__main__":
    main()
