import json
import glob
from pathlib import Path
import re
import os
import pandas as pd

# =============================================================================
# CONFIG
# =============================================================================

GOLDEN_JSON_GLOB = "data/knowledge/golden_extractions/golden_*.json"
TRAIN_FLAT_OUTPUT = "data/ml_training/train_flat.csv"
REGISTRY_FROM_GOLDEN_OUTPUT = "data/ml_training/registry_from_golden.csv"

# BATCH CONFIG: Add all your input/output pairs here
# NOTE: Ensure your input CSVs (train.csv, etc.) have 'clinical_codes_list' 
# if you want accurate registry flags for bundled procedures.
CSV_BATCHES = [
    # (Input Filename, Output Filename)
    ("data/ml_training/train_flat.csv",           "data/ml_training/registry_train.csv"),
    ("data/ml_training/test.csv",                 "data/ml_training/registry_test.csv"),
    ("data/ml_training/edge_cases_holdout.csv",   "data/ml_training/registry_edge_cases.csv"),
]

REGISTRY_COLUMNS = [
    "note_text", "verified_cpt_codes", "diagnostic_bronchoscopy", "bal",
    "bronchial_wash", "brushings", "endobronchial_biopsy", "transbronchial_biopsy",
    "transbronchial_cryobiopsy", "tbna_conventional", "linear_ebus", "radial_ebus",
    "navigational_bronchoscopy", "therapeutic_aspiration", "foreign_body_removal",
    "airway_dilation", "airway_stent", "thermal_ablation", "cryotherapy", "blvr",
    "peripheral_ablation", "bronchial_thermoplasty", "whole_lung_lavage",
    "rigid_bronchoscopy", "thoracentesis", "chest_tube", "ipc",
    "medical_thoracoscopy", "pleurodesis", "fibrinolytic_therapy"
]

TRAIN_FLAT_COLUMNS = [
    "source_file", "note_text", "billed_codes_list", "clinical_codes_list",
    "bal", "linear_ebus", "transbronchial_biopsy", "navigational_bronchoscopy",
    "stent_placement", "dilation", "rigid_bronchoscopy", "radial_ebus",
]

# =============================================================================
# Shared Helpers
# =============================================================================

def normalize_cpt_list(raw):
    """
    Returns a SET of codes from raw input (list, string, or stringified list).
    """
    if raw is None:
        return set()

    if isinstance(raw, (list, tuple, set)):
        raw = str(list(raw))

    try:
        if pd.isna(raw):
            return set()
    except (ValueError, TypeError):
        pass

    s = str(raw)
    codes = re.findall(r"\b\d{5}\b", s)
    return set(codes)

def clean_code_string(code_set):
    """Returns a clean comma-separated string for CSV output: '31623,31624'"""
    return ",".join(sorted(list(code_set)))

# =============================================================================
# PART A: Golden JSON -> ML Train-Style Dataset
# =============================================================================

def golden_dataset_generator(json_dir_pattern):
    files = glob.glob(json_dir_pattern)
    for filepath in files:
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue

        if isinstance(data, dict):
            data = [data]

        for entry in data:
            billed_codes = normalize_cpt_list(entry.get("cpt_codes", []))
            
            # Robust rationale extraction for Dropped/Suppressed codes
            rationale_obj = entry.get("coding_support", {}).get("section_3_rationale", {})
            if not rationale_obj:
                rationale_obj = entry.get("coding_review", {})
            
            dropped = normalize_cpt_list(rationale_obj.get("dropped_codes", []))
            
            # Clinical Codes = Billed + Dropped (The full list of what actually happened)
            clinical_reality_codes = billed_codes.union(dropped)

            flat_row = {
                "source_file": Path(filepath).name,
                "note_text": entry.get("note_text", ""),
                
                # PRESERVE BOTH LISTS
                "billed_codes_list": clean_code_string(billed_codes),
                "clinical_codes_list": clean_code_string(clinical_reality_codes),
                
                # Simple boolean helpers for flat review (optional)
                "bal": 1 if "31624" in clinical_reality_codes else 0,
                "linear_ebus": 1 if any(c in clinical_reality_codes for c in ["31652", "31653"]) else 0,
                "transbronchial_biopsy": 1 if any(c in clinical_reality_codes for c in ["31628", "31632"]) else 0,
                "navigational_bronchoscopy": 1 if "31627" in clinical_reality_codes else 0,
                "stent_placement": 1 if any(c in clinical_reality_codes for c in ["31631","31636","31637","31638"]) else 0,
                "dilation": 1 if "31630" in clinical_reality_codes else 0,
                "rigid_bronchoscopy": infer_rigid_from_entry(entry),
                "radial_ebus": 1 if "31654" in clinical_reality_codes else 0,
            }
            yield flat_row

def infer_rigid_from_entry(entry):
    registry = entry.get("registry_entry") or {}
    airway = str(registry.get("airway_type", "")).lower()
    
    if not airway:
        setting = registry.get("procedure_setting")
        if isinstance(setting, dict):
            airway = str(setting.get("airway_type", "")).lower()

    if "rigid" in airway: return 1

    text_lower = str(entry.get("note_text", "")).lower()
    if "rigid" in text_lower and "bronch" in text_lower:
        if "no rigid" not in text_lower:
            return 1
    return 0

def build_train_flat_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=TRAIN_FLAT_OUTPUT):
    rows = list(golden_dataset_generator(json_pattern))
    if rows:
        df_flat = pd.DataFrame(rows, columns=TRAIN_FLAT_COLUMNS)
        df_flat.to_csv(output_csv, index=False)
        print(f"Wrote {len(df_flat)} rows to {output_csv} (Contains Billed AND Clinical codes)")

# =============================================================================
# PART B: Registry Logic
# =============================================================================

def get_registry_flags_from_codes_and_text(clinical_codes_raw, note_text):
    """
    CRITICAL: This function expects CLINICAL codes (all procedures performed),
    not just the billed codes. This ensures suppressed codes (like 31622) 
    still trigger the correct registry flags.
    """
    cpt_codes = normalize_cpt_list(clinical_codes_raw)
    text_lower = str(note_text).lower()

    flags = {col: 0 for col in REGISTRY_COLUMNS if col not in ["note_text", "verified_cpt_codes"]}

    # --- CPT MAPPING (Using Clinical Codes) ---
    # 1. Force Diagnostic Bronch flag if ANY bronch code is present
    bronch_codes = ["31624", "31625", "31628", "31629", "31641", "31647", "31652", "31653"]
    if any(c in cpt_codes for c in bronch_codes) or "31622" in cpt_codes:
        flags["diagnostic_bronchoscopy"] = 1
    if "31624" in cpt_codes: flags["bal"] = 1
    if "31623" in cpt_codes: flags["brushings"] = 1
    if "31625" in cpt_codes: flags["endobronchial_biopsy"] = 1
    if "31629" in cpt_codes: flags["tbna_conventional"] = 1

    if any(c in cpt_codes for c in ["31652", "31653"]): flags["linear_ebus"] = 1
    if "31654" in cpt_codes: flags["radial_ebus"] = 1
    if "31627" in cpt_codes: flags["navigational_bronchoscopy"] = 1

    if any(c in cpt_codes for c in ["31645", "31646"]): flags["therapeutic_aspiration"] = 1
    if "31635" in cpt_codes: flags["foreign_body_removal"] = 1
    
    if "31630" in cpt_codes: flags["airway_dilation"] = 1
    if any(c in cpt_codes for c in ["31631", "31636", "31637", "31638"]): flags["airway_stent"] = 1
    
    if any(c in cpt_codes for c in ["31660", "31661"]): flags["bronchial_thermoplasty"] = 1
    if "32997" in cpt_codes: flags["whole_lung_lavage"] = 1

    if "32550" in cpt_codes: flags["ipc"] = 1
    if any(c in cpt_codes for c in ["32554", "32555"]): flags["thoracentesis"] = 1
    if "32551" in cpt_codes: flags["chest_tube"] = 1
    if any(c in cpt_codes for c in ["32601", "32650"]): flags["medical_thoracoscopy"] = 1
    if any(c in cpt_codes for c in ["32650", "32560"]): flags["pleurodesis"] = 1
    if any(c in cpt_codes for c in ["31647", "31648", "31650", "31651"]): flags["blvr"] = 1

    # --- HYBRID / TEXT FALLBACKS ---
    
    # 2. Force Cryobiopsy flag if text mentions it, even if code is just 31628
    if "cryobiopsy" in text_lower or ("cryo" in text_lower and "biopsy" in text_lower):
        flags["transbronchial_cryobiopsy"] = 1
    # Cryobiopsy (code-based)
    elif any(c in cpt_codes for c in ["31628", "31632", "31645"]):
        if "cryo" in text_lower or "freeze" in text_lower:
            flags["transbronchial_cryobiopsy"] = 1
        elif "31628" in cpt_codes or "31632" in cpt_codes:
            flags["transbronchial_biopsy"] = 1
    
    # Rigid Bronch
    if "31603" in cpt_codes or ("rigid" in text_lower and "bronch" in text_lower):
         if "no rigid" not in text_lower:
            flags["rigid_bronchoscopy"] = 1

    # Foreign Body Fallback
    if flags["foreign_body_removal"] == 0:
        if "foreign body" in text_lower and ("removed" in text_lower or "extraction" in text_lower):
            flags["foreign_body_removal"] = 1

    # Ablation
    if "31641" in cpt_codes:
        if ("31627" in cpt_codes or "31654" in cpt_codes or "peripheral" in text_lower):
            flags["peripheral_ablation"] = 1
        if "cryo" in text_lower:
            flags["cryotherapy"] = 1
        else:
            flags["thermal_ablation"] = 1

    return flags

def enrich_flags_with_registry_entry(flags, registry_entry):
    if not registry_entry:
        return flags

    proc_nested = registry_entry.get("procedures_performed") or {}
    pleural_nested = registry_entry.get("pleural_procedures") or {}
    
    def is_performed(key):
        if proc_nested.get(key, {}).get("performed") is True: return True
        if pleural_nested.get(key, {}).get("performed") is True: return True
        if registry_entry.get(f"{key}_performed") is True: return True
        if registry_entry.get(key) is True: return True
        if key == "whole_lung_lavage" and (registry_entry.get("wll_volume_instilled_l") or 0) > 0: return True
        if key == "transbronchial_cryobiopsy" and registry_entry.get("nav_cryobiopsy_for_nodule"): return True
        if key == "peripheral_ablation" and registry_entry.get("ablation_peripheral_performed"): return True
        if key == "blvr" and registry_entry.get("blvr_valve_type"): return True
        if key == "navigational_bronchoscopy" and registry_entry.get("nav_platform"): return True
        if key == "radial_ebus" and registry_entry.get("nav_rebus_used"): return True
        return False

    for col in flags.keys():
        if is_performed(col):
            flags[col] = 1
            
    intervention = str(registry_entry.get("pneumothorax_intervention", "")).lower()
    if "chest tube" in intervention or "pigtail" in intervention:
        flags["chest_tube"] = 1

    return flags

# =============================================================================
# BATCH PROCESSING
# =============================================================================

def build_registry_from_csv_batch(batch_list):
    """
    Generates registry training data from input CSVs.
    Logic: 
      - Use 'clinical_codes_list' (if available) to generate FLAGS (Registry Truth).
      - Use 'billed_codes_list' (or 'verified_cpt_codes') for the VERIFIED_CPT_CODES column (Billing Truth).
    """
    for input_csv, output_csv in batch_list:
        if not os.path.exists(input_csv):
            print(f"Skipping {input_csv}: File not found.")
            continue

        print(f"Processing {input_csv} -> {output_csv}...")
        df = pd.read_csv(input_csv)
        rows = []

        # Check which columns we have available
        has_clinical = 'clinical_codes_list' in df.columns
        has_billed = 'billed_codes_list' in df.columns
        has_verified = 'verified_cpt_codes' in df.columns

        for _, row in df.iterrows():
            note_text = str(row.get("note_text", ""))
            
            # 1. Determine codes for FLAGS (Should be Clinical/All codes)
            if has_clinical:
                codes_for_flags = row['clinical_codes_list']
            elif has_verified:
                codes_for_flags = row['verified_cpt_codes'] # Fallback
            else:
                codes_for_flags = ""

            # 2. Determine codes for TARGET LABEL (Should be Billed codes)
            if has_billed:
                codes_for_target = row['billed_codes_list']
            elif has_verified:
                codes_for_target = row['verified_cpt_codes']
            else:
                codes_for_target = ""

            # Generate flags based on clinical reality
            flags = get_registry_flags_from_codes_and_text(codes_for_flags, note_text)
            
            # Clean up the target codes
            target_cpts = clean_code_string(normalize_cpt_list(codes_for_target))

            row_dict = {
                "note_text": note_text,
                "verified_cpt_codes": target_cpts # This is the BILLING target
            }
            row_dict.update(flags)
            rows.append(row_dict)

        out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
        out_df.to_csv(output_csv, index=False)
        print(f"  - Wrote {len(out_df)} rows. (Flags based on {'Clinical' if has_clinical else 'Billed'} codes)")

def build_registry_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=REGISTRY_FROM_GOLDEN_OUTPUT):
    files = glob.glob(json_pattern)
    rows = []

    for filepath in files:
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except: continue
        
        if isinstance(data, dict): data = [data]

        for entry in data:
            note_text = entry.get("note_text", "")
            billed_codes = normalize_cpt_list(entry.get("cpt_codes", []))
            
            rationale_obj = entry.get("coding_support", {}).get("section_3_rationale", {})
            if not rationale_obj:
                rationale_obj = entry.get("coding_review", {})
            
            dropped = normalize_cpt_list(rationale_obj.get("dropped_codes", []))
            clinical_codes = billed_codes.union(dropped)

            # 1. Use CLINICAL codes for Registry Flags (e.g. 31622 -> Diagnostic Bronch Flag = 1)
            flags = get_registry_flags_from_codes_and_text(list(clinical_codes), note_text)
            flags = enrich_flags_with_registry_entry(flags, entry.get("registry_entry"))

            # 2. Use BILLED codes for the verified_cpt_codes column (Training Target)
            row_dict = {
                "note_text": note_text,
                "verified_cpt_codes": clean_code_string(billed_codes) 
            }
            row_dict.update(flags)
            rows.append(row_dict)

    if rows:
        out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
        out_df.to_csv(output_csv, index=False)
        print(f"Wrote {len(out_df)} rows to {output_csv}")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # 1. Golden JSON -> ML Train Flat (Contains both Billed and Clinical columns)
    build_train_flat_from_golden()

    # 2. Process all CSV Batches (Train, Test, Edge Cases)
    # The script will now look for 'clinical_codes_list' in these inputs to generate accurate flags
    build_registry_from_csv_batch(CSV_BATCHES)

    # 3. Golden JSON -> Registry Ground Truth (Direct path)
    build_registry_from_golden()