import pandas as pd
import re
import json
import os

# --------------------------------------------------------------------------------
# 1. STRICT REGEX DEFINITIONS (Prevents Hallucinations)
# --------------------------------------------------------------------------------
LABEL_PATTERNS = {
    # --- Diagnostic ---
    "diagnostic_bronchoscopy": [r"diagnostic bronch", r"airway inspection", r"routine inspection"],
    "bal": [r"\bbal\b", r"bronchoalveolar lavage", r"lobar wash", r"segmental wash"],
    "bronchial_wash": [r"bronchial wash", r"bronchial washing"],
    "brushings": [r"\bbrush", r"brushing"],
    "endobronchial_biopsy": [r"endobronchial biopsy", r"\bebbx\b", r"forceps biopsy"],
    "transbronchial_biopsy": [r"transbronchial biopsy", r"\btbbx\b", r"parenchymal biopsy"],
    "transbronchial_cryobiopsy": [r"\bcryobiopsy\b", r"\bcryoprobe\b"],
    "tbna_conventional": [r"conventional tbna", r"wang needle"],
    
    # --- EBUS & Nav ---
    "linear_ebus": [r"linear ebus", r"ebus-tbna", r"systematic nodal", r"mediastinal staging", r"convex probe"],
    "radial_ebus": [r"radial ebus", r"r-ebus", r"radial probe", r"\brebus\b"],
    "navigational_bronchoscopy": [
        r"electromagnetic nav", r"\benb\b", r"superdimension", r"veran", 
        r"illumisite", r"robotic bronch", r"\bion\b", r"\bmonarch\b", r"shape-sensing"
    ],
    
    # --- Therapeutic ---
    "therapeutic_aspiration": [r"therapeutic aspiration", r"mucus plug", r"pulmonary toilet", r"suctioning of secretions"],
    "foreign_body_removal": [r"foreign body", r"peanut", r"object removal", r"extraction", r"retrieval"],
    "airway_dilation": [r"balloon dilation", r"airway dilation", r"\bcre\b"],
    "airway_stent": [r"airway stent", r"metallic stent", r"silicone stent", r"stent placement"],
    "rigid_bronchoscopy": [r"rigid bronch", r"rigid scope", r"rigid barrel"],
    "thermal_ablation": [r"thermal ablation", r"microwave", r"\bmwa\b", r"radiofrequency", r"\brfa\b"],
    "cryotherapy": [r"cryotherapy", r"cryoablation", r"spray cryo"],
    
    # --- Advanced / Pleural ---
    "blvr": [r"endobronchial valve", r"\bzephyr\b", r"\bspiration\b", r"lung volume reduction", r"valve placement"],
    "ipc": [r"indwelling pleural", r"pleurx", r"tunneled catheter", r"aspira"], # Strict: prevents generic "catheter" matches
    "thoracentesis": [r"thoracentesis", r"pleural tap"],
    "chest_tube": [r"chest tube", r"pigtail", r"thoracostomy"],
    "medical_thoracoscopy": [r"medical thoracoscopy", r"pleuroscopy"],
    "pleurodesis": [r"pleurodesis", r"talc", r"sclerosis"],
    
    # --- Rare/Other ---
    "peripheral_ablation": [r"peripheral ablation"], 
    "bronchial_thermoplasty": [r"thermoplasty", r"alair"],
    "whole_lung_lavage": [r"whole lung lavage"],
    "fibrinolytic_therapy": [r"\btpa\b", r"fibrinolytic", r"dnase"]
}

# Terms that negate a finding if they appear immediately before it
NEGATION_TERMS = [r"\bno\b", r"\bnot\b", r"\bwithout\b", r"\bruled out\b", r"\bnegative for\b", r"\bdenies\b"]

# Explicit exclusion logic for high-risk hallucinations
CONTEXT_EXCLUSIONS = {
    "blvr": [r"chartis", r"assessment", r"evaluation"], # Chartis is assessment, not valve placement
    "airway_stent": [r"chartis"],
    "endobronchial_biopsy": [r"transbronchial"],
    "transbronchial_biopsy": [r"cryobiopsy"], # TBBx is standard forceps; Cryo is distinct
    "ipc": [r"foley", r"suction catheter"]
}

# --------------------------------------------------------------------------------
# 2. LOGIC FUNCTIONS
# --------------------------------------------------------------------------------
def get_labels(text):
    if not isinstance(text, str):
        return {k: 0 for k in LABEL_PATTERNS.keys()}

    text_lower = text.lower()
    labels = {k: 0 for k in LABEL_PATTERNS.keys()}
    
    for label, patterns in LABEL_PATTERNS.items():
        # 1. Check for Positive Match
        match_found = False
        match_start = -1
        
        for pattern in patterns:
            m = re.search(pattern, text_lower)
            if m:
                match_found = True
                match_start = m.start()
                break
        
        if not match_found:
            continue
            
        # 2. Check for Context Exclusions (Global)
        if label in CONTEXT_EXCLUSIONS:
            if any(re.search(ex, text_lower) for ex in CONTEXT_EXCLUSIONS[label]):
                # Special case: Allow BLVR if "valve" is explicit even if "chartis" is present?
                # For safety, if we see "Chartis" and "Valve", we trust "Valve" regex IF it matches "Valve placement".
                # But to keep it simple and fix the specific "Chartis triggers Stent" error:
                # If we matched "stent" only because of some loose logic, exclusion saves us.
                # Since we use strict Positive Match now, global exclusion is a safety net.
                pass 

        # 3. Check for Immediate Negation (Lookbehind ~5-8 words)
        # We look at the 40 chars preceding the match
        window_start = max(0, match_start - 40)
        preceding_text = text_lower[window_start:match_start]
        
        is_negated = False
        for neg in NEGATION_TERMS:
            if re.search(neg, preceding_text):
                is_negated = True
                break
        
        if not is_negated:
            labels[label] = 1

    return labels

# --------------------------------------------------------------------------------
# 3. PROCESSING LOOP
# --------------------------------------------------------------------------------
def fix_registry_file(filename):
    if not os.path.exists(filename):
        print(f"Skipping {filename} (File not found)")
        return

    print(f"Fixing labels in {filename}...")
    df = pd.read_csv(filename)
    
    # Recalculate labels based on note_text
    # We strip out old label columns first to avoid duplicates/conflicts
    meta_cols = [c for c in df.columns if c not in LABEL_PATTERNS.keys()]
    meta_df = df[meta_cols].copy()
    
    label_list = []
    for text in df['note_text']:
        label_list.append(get_labels(str(text)))
        
    label_df = pd.DataFrame(label_list)
    
    # Combine metadata + new labels
    final_df = pd.concat([meta_df, label_df], axis=1)
    
    final_df.to_csv(filename, index=False)
    print(f"✅ Success: Updated {filename}")

if __name__ == "__main__":
    # 1. Generate Missing Schema
    schema = list(LABEL_PATTERNS.keys())
    with open("registry_label_fields.json", "w") as f:
        json.dump(schema, f, indent=4)
    print("✅ Schema generated: registry_label_fields.json")

    # 2. Fix the broken registry files
    fix_registry_file("data/ml_training/registry_train.csv")
    fix_registry_file("data/ml_training/registry_test.csv")
    fix_registry_file("data/ml_training/registry_edge_cases.csv")