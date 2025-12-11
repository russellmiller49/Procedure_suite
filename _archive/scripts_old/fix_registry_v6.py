import re
import pandas as pd
import json
from pathlib import Path

# Define the list of flag field names in the correct order (from registry_label_fields schema)
FIELDS = [
    "diagnostic_bronchoscopy", "bal", "bronchial_wash", "brushings", "endobronchial_biopsy",
    "transbronchial_biopsy", "transbronchial_cryobiopsy", "tbna_conventional", "linear_ebus", "radial_ebus",
    "navigational_bronchoscopy", "therapeutic_aspiration", "foreign_body_removal", "airway_dilation",
    "airway_stent", "rigid_bronchoscopy", "thermal_ablation", "cryotherapy", "blvr", "ipc",
    "thoracentesis", "chest_tube", "medical_thoracoscopy", "pleurodesis", "peripheral_ablation",
    "bronchial_thermoplasty", "whole_lung_lavage", "fibrinolytic_therapy"
]

# Precompile regex patterns for performance and clarity
# For each flag, define a pattern to detect its presence, and a pattern (or method) to detect negation context.
patterns = {
    "diagnostic_bronchoscopy": re.compile(r"\bdiagnostic bronch(oscopy)?\b", re.IGNORECASE),
    "bal": re.compile(r"\bBAL\b|bronchoalveolar\s+lavage", re.IGNORECASE),
    "bronchial_wash": re.compile(r"bronchial\s+washing?s?", re.IGNORECASE),
    "brushings": re.compile(r"\bbrushings?\b|bronchial\s+brushing", re.IGNORECASE),
    "endobronchial_biopsy": re.compile(r"endobronchial\s+biopsies?\b", re.IGNORECASE),
    "transbronchial_biopsy": re.compile(r"transbronchial\s+biopsies?\b|\bTBBX\b|\bTBLB\b", re.IGNORECASE),
    "transbronchial_cryobiopsy": re.compile(r"cryo[-\s]?biopsies?\b|transbronchial\s+cryobiopsy", re.IGNORECASE),
    "tbna_conventional": re.compile(r"\bTBNA\b(?![^\.]*\bEBUS\b)", re.IGNORECASE),  # TBNA not immediately in "EBUS" phrase
    "linear_ebus": re.compile(r"\bEBUS\b|endobronchial\s+ultrasound", re.IGNORECASE),
    "radial_ebus": re.compile(r"radial[^\.]{0,5}\bEBUS\b|radial\s+ultrasound|R-?EBUS", re.IGNORECASE),
    "navigational_bronchoscopy": re.compile(r"navigation|navigational|electromagnetic|ENB|\(ENB\)|robotic|Monarch|Ion\b|superDimension|Veran", re.IGNORECASE),
    "therapeutic_aspiration": re.compile(r"therapeutic aspiration|mucus\s+plug\s*(removed|retriev|extract|suction)|secretions\s*(suction|aspirat)", re.IGNORECASE),
    "foreign_body_removal": re.compile(r"foreign\s+body|FB removal|foreign\s+object|retrieved\s+a\s+\w+", re.IGNORECASE),
    "airway_dilation": re.compile(r"dilatation|dilation|dilated|balloon dilation|ballooned", re.IGNORECASE),
    "airway_stent": re.compile(r"\bstent\b", re.IGNORECASE),
    "rigid_bronchoscopy": re.compile(r"rigid\s*bronch|rigid\s*scope|converted\s*to\s*rigid", re.IGNORECASE),
    "thermal_ablation": re.compile(r"\bAPC\b|argon plasma|laser|cautery|thermal ablation", re.IGNORECASE),
    "cryotherapy": re.compile(r"cryotherapy|cryoablation|cryo treatment|cryodebridement|cryospray", re.IGNORECASE),
    "blvr": re.compile(r"valve|coil|lung volume reduction", re.IGNORECASE),
    "ipc": re.compile(r"indwelling\s+pleural\s+catheter|tunneled\s+pleural\s+catheter|pleurx|IPC\b", re.IGNORECASE),
    "thoracentesis": re.compile(r"thoracentesis|pleural\s+tap", re.IGNORECASE),
    "chest_tube": re.compile(r"chest\s+tube|thoracostomy\s+tube|pigtail\s+catheter", re.IGNORECASE),
    "medical_thoracoscopy": re.compile(r"medical\s+thoracoscopy|pleuroscopy|\bthoracoscopy\b", re.IGNORECASE),
    "pleurodesis": re.compile(r"pleurodesis|talc insufflation|talc slurry|doxycycline pleurodesis", re.IGNORECASE),
    "peripheral_ablation": re.compile(r"radiofrequency ablation|RFA\b|microwave ablation|peripheral lesion ablation", re.IGNORECASE),
    "bronchial_thermoplasty": re.compile(r"thermoplasty", re.IGNORECASE),
    "whole_lung_lavage": re.compile(r"whole lung lavage|whole-lung lavage|WLL\b", re.IGNORECASE),
    "fibrinolytic_therapy": re.compile(r"\btPA\b|alteplase|urokinase|streptokinase|DNase|fibrinolytic", re.IGNORECASE)
}

# Patterns or lists for negation cues
negation_cues = ["no", "not", "none", "without", "never", "was not", "were not", "did not"]
# Specific negative phrases for clarity (field-specific where needed)
negation_patterns = {
    "biopsy": re.compile(r"\bno biopsy\b|\bno biopsies\b|biopsies?\s+(were|was)\s+not\s+performed", re.IGNORECASE),
    "valve": re.compile(r"\bno valve\b|valve\s+(was|were)\s+not\s+placed", re.IGNORECASE),
    "stent": re.compile(r"\bno stent\b|stent\s+not\s+placed", re.IGNORECASE),
    "tbna": re.compile(r"\bno TBNA\b|TBNA\s+not\s+performed", re.IGNORECASE),
    "lavage": re.compile(r"\bno lavage\b|\bno BAL\b|lavage\s+not\s+done", re.IGNORECASE),
    "wash": re.compile(r"\bno washings?\b", re.IGNORECASE),
    "brush": re.compile(r"\bno brushings?\b", re.IGNORECASE),
    "aspiration": re.compile(r"\bno aspiration\b|\bno mucus plug\b", re.IGNORECASE),
    "foreign_body": re.compile(r"\bno foreign body\b|no evidence of foreign body", re.IGNORECASE),
    "dilation": re.compile(r"\bno dilation\b|\bnot dilated\b", re.IGNORECASE),
    "thermoplasty": re.compile(r"\bno thermoplasty\b", re.IGNORECASE),
    "pleurodesis": re.compile(r"\bno pleurodesis\b", re.IGNORECASE),
    "thoracoscopy": re.compile(r"\bno thoracoscopy\b", re.IGNORECASE),
    "thoracentesis": re.compile(r"\bno thoracentesis\b", re.IGNORECASE),
    "chest_tube": re.compile(r"\bno chest tube\b", re.IGNORECASE)
}
# Also handle "EBUS not performed" as negation for linear_ebus
negation_patterns["linear_ebus"] = re.compile(r"\bEBUS\b.*\bnot performed\b|\bEBUS\b.*\bnot done\b", re.IGNORECASE)
negation_patterns["radial_ebus"] = re.compile(r"\bradial EBUS\b.*\bnot performed\b", re.IGNORECASE)
negation_patterns["navigational_bronchoscopy"] = re.compile(r"\bno navigation\b|\bnot navigated\b|\bno robotic\b", re.IGNORECASE)
negation_patterns["ipc"] = re.compile(r"\bno catheter\b|\bno IPC\b", re.IGNORECASE)

# Helper function to detect negation near a match
def is_negated(field, text, match):
    """Check if the context around a regex match or in the sentence contains a negation cue for the given field."""
    start = match.start()
    end = match.end()
    # Consider a window around the match (e.g., current sentence or a few words before/after)
    window_span = text[max(0, start-30): min(len(text), end+30)]
    # Generic negation check in window
    for cue in negation_cues:
        if re.search(rf"\b{cue}\b", window_span, re.IGNORECASE):
            return True
    # Field-specific negation (if any pattern defined)
    if field in negation_patterns:
        if negation_patterns[field].search(text):
            return True
    return False

# Process each CSV file
# Get project root (parent of scripts directory)
project_root = Path(__file__).parent.parent
data_dir = project_root / "data" / "ml_training"
csv_files = ["registry_train.csv", "registry_test.csv", "registry_edge_cases.csv"]

for csv_file in csv_files:
    csv_path = data_dir / csv_file
    if not csv_path.exists():
        print(f"Skipping {csv_file} (File not found at {csv_path})")
        continue
    
    print(f"Processing {csv_file}...")
    df = pd.read_csv(csv_path)
    # Ensure the output columns exist (if CSV might be empty initially, create columns)
    for field in FIELDS:
        if field not in df.columns:
            df[field] = 0  # initialize if not present
    # Iterate through notes and apply pattern matching
    updated_flags = {field: [] for field in FIELDS}  # store new flag values
    for note in df['note_text'].astype(str):
        text = note if note is not None else ""
        # Normalize text minimally for easier matching (e.g., collapse multiple spaces)
        text = re.sub(r"\s+", " ", text)
        # Initialize all flags as 0
        flags = {field: 0 for field in FIELDS}
        # Check each pattern
        for field, pattern in patterns.items():
            if field == "tbna_conventional":
                # We'll handle TBNA after EBUS logic to avoid misclassification
                continue
            match = pattern.search(text)
            if match:
                # If a match is found, verify it is not negated
                if not is_negated(field, text, match):
                    flags[field] = 1
        # Special handling for EBUS vs radial context:
        if flags["radial_ebus"] == 1 and flags["linear_ebus"] == 1:
            # If both flags set, ensure linear EBUS is true only if linear-specific context exists
            if not re.search(r"TBNA|station|mediastinal|linear EBUS|lymph node", text, re.IGNORECASE):
                # No clear linear EBUS context (only radial usage likely)
                flags["linear_ebus"] = 0
        # Now handle TBNA (conventional) after EBUS:
        tbna_match = patterns["tbna_conventional"].search(text)
        if tbna_match:
            if not is_negated("tbna", text, tbna_match):
                # Only mark conventional TBNA if linear EBUS flag is NOT set (no EBUS performed)
                if flags["linear_ebus"] == 0:
                    flags["tbna_conventional"] = 1
                else:
                    flags["tbna_conventional"] = 0
        # Handle diagnostic_bronchoscopy:
        # If explicitly mentioned in text, it's already flagged above. Otherwise, determine if should be 1.
        # Optionally, if no other procedure flags are true but a bronchoscopy was done, mark diagnostic.
        if flags["diagnostic_bronchoscopy"] == 0:
            # Heuristic: if none of the advanced flags (EBUS, navigational, foreign body, stent, etc.) are set 
            # but at least a basic diagnostic sample (BAL/wash/brush/biopsy) was done, or the note implies a bronchoscopy occurred,
            # we can consider it a diagnostic bronchoscopy.
            basic_diagnostic = (flags["bal"] or flags["bronchial_wash"] or flags["brushings"] or 
                                 flags["endobronchial_biopsy"] or flags["transbronchial_biopsy"] or 
                                 flags["transbronchial_cryobiopsy"] or flags["tbna_conventional"])
            advanced_procedure = (flags["linear_ebus"] or flags["radial_ebus"] or flags["navigational_bronchoscopy"] or 
                                   flags["foreign_body_removal"] or flags["airway_stent"] or flags["airway_dilation"] or 
                                   flags["rigid_bronchoscopy"] or flags["thermal_ablation"] or flags["cryotherapy"] or 
                                   flags["blvr"] or flags["ipc"] or flags["medical_thoracoscopy"] or 
                                   flags["peripheral_ablation"] or flags["bronchial_thermoplasty"])
            if basic_diagnostic and not advanced_procedure:
                flags["diagnostic_bronchoscopy"] = 1
        # Apply override rules for mutually exclusive fields:
        if flags["foreign_body_removal"] == 1:
            # Foreign body removal overrides any transbronchial biopsy flag
            flags["transbronchial_biopsy"] = 0
        if flags["transbronchial_cryobiopsy"] == 1:
            # Cryobiopsy overrides conventional transbronchial biopsy
            flags["transbronchial_biopsy"] = 0
        if flags["linear_ebus"] == 1:
            # EBUS present, ensure conventional TBNA is off
            flags["tbna_conventional"] = 0
        if flags["whole_lung_lavage"] == 1:
            # Whole lung lavage (WLL) is a special case of lavage; do not also count it as BAL
            flags["bal"] = 0

        # Append flags to updated list
        for field in FIELDS:
            updated_flags[field].append(flags[field])
    # Update the dataframe with new flag values
    for field in FIELDS:
        df[field] = updated_flags[field]
    # Overwrite the CSV with updated flags
    df.to_csv(csv_path, index=False)
    print(f"✅ Success: Updated {csv_file} ({len(df)} rows processed)")

# Save the registry_label_fields.json with the field order
schema_path = project_root / "registry_label_fields.json"
with open(schema_path, 'w') as schema_file:
    json.dump(FIELDS, schema_file, indent=2)
print(f"✅ Schema generated: {schema_path}")
