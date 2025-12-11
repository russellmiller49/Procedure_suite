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

# FIXED: Inputs point to existing registry files for test/edge cases to allow in-place schema updates
CSV_BATCHES = [
    ("data/ml_training/train_flat.csv",           "data/ml_training/registry_train.csv"),
    ("data/ml_training/registry_test.csv",        "data/ml_training/registry_test.csv"),
    ("data/ml_training/registry_edge_cases.csv",  "data/ml_training/registry_edge_cases.csv"),
]

# UPDATED: Added missing schema fields identified in review
REGISTRY_COLUMNS = [
    "note_text", "verified_cpt_codes", 
    # Bronchoscopy
    "diagnostic_bronchoscopy", "bal", "bronchial_wash", "brushings", 
    "endobronchial_biopsy", "transbronchial_biopsy", "transbronchial_cryobiopsy", 
    "tbna_conventional", "linear_ebus", "radial_ebus", "navigational_bronchoscopy", 
    "therapeutic_aspiration", "foreign_body_removal", "airway_dilation", "airway_stent", 
    "thermal_ablation", "cryotherapy", "mechanical_debulking", "brachytherapy_catheter", # Added
    "blvr", "peripheral_ablation", "bronchial_thermoplasty", "whole_lung_lavage", 
    "rigid_bronchoscopy", "photodynamic_therapy", # Added
    # Pleural / Thoracic
    "thoracentesis", "chest_tube", "ipc", "medical_thoracoscopy", 
    "pleural_biopsy", "pleurodesis", "fibrinolytic_therapy" # Added pleural_biopsy
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
    """Returns a SET of codes from raw input."""
    if raw is None: return set()
    if isinstance(raw, (list, tuple, set)): raw = str(list(raw))
    try:
        if pd.isna(raw): return set()
    except: pass
    s = str(raw)
    codes = re.findall(r"\b\d{5}\b", s)
    return set(codes)

def clean_code_string(code_set):
    return ",".join(sorted(list(code_set)))

# =============================================================================
# PART A: Golden JSON -> ML Train-Style Dataset
# =============================================================================

def golden_dataset_generator(json_dir_pattern):
    files = glob.glob(json_dir_pattern)
    for filepath in files:
        with open(filepath, "r") as f:
            try: data = json.load(f)
            except: continue
        if isinstance(data, dict): data = [data]
        for entry in data:
            billed_codes = normalize_cpt_list(entry.get("cpt_codes", []))
            rationale_obj = entry.get("coding_support", {}).get("section_3_rationale", {})
            if not rationale_obj: rationale_obj = entry.get("coding_review", {})
            dropped = normalize_cpt_list(rationale_obj.get("dropped_codes", []))
            clinical_reality_codes = billed_codes.union(dropped)

            flat_row = {
                "source_file": Path(filepath).name,
                "note_text": entry.get("note_text", ""),
                "billed_codes_list": clean_code_string(billed_codes),
                "clinical_codes_list": clean_code_string(clinical_reality_codes),
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
        if isinstance(setting, dict): airway = str(setting.get("airway_type", "")).lower()
    if "rigid" in airway: return 1
    text_lower = str(entry.get("note_text", "")).lower()
    if "rigid" in text_lower and "bronch" in text_lower and "no rigid" not in text_lower: return 1
    return 0

def build_train_flat_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=TRAIN_FLAT_OUTPUT):
    rows = list(golden_dataset_generator(json_pattern))
    if rows:
        df_flat = pd.DataFrame(rows, columns=TRAIN_FLAT_COLUMNS)
        df_flat.to_csv(output_csv, index=False)
        print(f"Wrote {len(df_flat)} rows to {output_csv}")

# =============================================================================
# PART B: Registry Logic
# =============================================================================

def get_registry_flags_from_codes_and_text(clinical_codes_raw, note_text):
    cpt_codes = normalize_cpt_list(clinical_codes_raw)
    text_lower = str(note_text).lower()
    flags = {col: 0 for col in REGISTRY_COLUMNS if col not in ["note_text", "verified_cpt_codes"]}

    # --- 1. Basic CPT Mapping ---
    # Bronchoscopy
    if any(c in cpt_codes for c in ["31622", "31624", "31625", "31628", "31629", "31641", "31647", "31652", "31653"]):
        flags["diagnostic_bronchoscopy"] = 1
    if "31624" in cpt_codes: flags["bal"] = 1
    if "31623" in cpt_codes: flags["brushings"] = 1
    if "31625" in cpt_codes: flags["endobronchial_biopsy"] = 1
    
    # FIX: Review found 1.8% missing TBNA flags. Added 31633 check.
    if any(c in cpt_codes for c in ["31629", "31633"]): flags["tbna_conventional"] = 1

    if any(c in cpt_codes for c in ["31652", "31653"]): flags["linear_ebus"] = 1
    if "31654" in cpt_codes: flags["radial_ebus"] = 1
    if "31627" in cpt_codes: flags["navigational_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31645", "31646"]): flags["therapeutic_aspiration"] = 1
    if "31635" in cpt_codes: flags["foreign_body_removal"] = 1
    if "31630" in cpt_codes: flags["airway_dilation"] = 1
    if any(c in cpt_codes for c in ["31631", "31636", "31637", "31638"]): flags["airway_stent"] = 1
    if any(c in cpt_codes for c in ["31660", "31661"]): flags["bronchial_thermoplasty"] = 1
    if "32997" in cpt_codes: flags["whole_lung_lavage"] = 1
    
    # Advanced / Destructive
    if any(c in cpt_codes for c in ["31647", "31648", "31650", "31651"]): flags["blvr"] = 1
    if "31643" in cpt_codes: flags["brachytherapy_catheter"] = 1
    if "96570" in cpt_codes or "96571" in cpt_codes: flags["photodynamic_therapy"] = 1
    
    # Pleural
    if "32550" in cpt_codes: flags["ipc"] = 1
    if any(c in cpt_codes for c in ["32554", "32555"]): flags["thoracentesis"] = 1
    if "32551" in cpt_codes: flags["chest_tube"] = 1
    if any(c in cpt_codes for c in ["32601", "32604", "32606", "32607", "32608", "32609", "32650"]): 
        flags["medical_thoracoscopy"] = 1
    if any(c in cpt_codes for c in ["32650", "32560", "32561"]): flags["pleurodesis"] = 1
    if any(c in cpt_codes for c in ["32561", "32562"]): flags["fibrinolytic_therapy"] = 1
    
    # FIX: Map biopsy codes to pleural_biopsy flag
    if any(c in cpt_codes for c in ["32609", "32604", "32400", "32405"]): 
        flags["pleural_biopsy"] = 1

    # --- 2. Hybrid / Text-Based Logic ---
    
    # Cryobiopsy (Text detection or inferred from biopsy + text)
    if "cryobiopsy" in text_lower or ("cryo" in text_lower and "biopsy" in text_lower):
        flags["transbronchial_cryobiopsy"] = 1
    elif any(c in cpt_codes for c in ["31628", "31632"]):
        # If code is generic biopsy, check text for cryo specific
        if "cryo" in text_lower or "freeze" in text_lower:
            flags["transbronchial_cryobiopsy"] = 1
        else:
            flags["transbronchial_biopsy"] = 1 # Standard forceps
    
    # Rigid Bronch (Text or CPT)
    if "31603" in cpt_codes or ("rigid" in text_lower and "bronch" in text_lower and "no rigid" not in text_lower):
        flags["rigid_bronchoscopy"] = 1

    # Mechanical Debulking / Tissue Resection
    if "31640" in cpt_codes or "31641" in cpt_codes:
        if "snare" in text_lower or "forceps" in text_lower or "debulking" in text_lower or "resection" in text_lower:
            flags["mechanical_debulking"] = 1
            
    # Ablation logic (Thermal vs Cryo vs APC)
    if "31641" in cpt_codes:
        if ("31627" in cpt_codes or "31654" in cpt_codes or "peripheral" in text_lower):
            flags["peripheral_ablation"] = 1
        if "cryo" in text_lower:
            flags["cryotherapy"] = 1
        elif "apc" in text_lower or "argon" in text_lower or "laser" in text_lower or "electrocautery" in text_lower:
            flags["thermal_ablation"] = 1

    return flags

def enrich_flags_with_registry_entry(flags, registry_entry):
    if not registry_entry: return flags
    proc_nested = registry_entry.get("procedures_performed") or {}
    pleural_nested = registry_entry.get("pleural_procedures") or {}
    
    def is_performed(key):
        # Check proc_nested - handle both dict and boolean values
        proc_val = proc_nested.get(key)
        if proc_val is True:
            return True
        if isinstance(proc_val, dict) and proc_val.get("performed") is True:
            return True

        # Check pleural_nested - handle both dict and boolean values
        pleural_val = pleural_nested.get(key)
        if pleural_val is True:
            return True
        if isinstance(pleural_val, dict) and pleural_val.get("performed") is True:
            return True

        # Direct registry_entry checks
        if registry_entry.get(f"{key}_performed") is True: return True
        if registry_entry.get(key) is True: return True

        # Specific mappings
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
    for input_csv, output_csv in batch_list:
        if not os.path.exists(input_csv):
            print(f"Skipping {input_csv}: File not found.")
            continue

        print(f"Processing {input_csv} -> {output_csv}...")
        df = pd.read_csv(input_csv)
        rows = []
        
        has_clinical = 'clinical_codes_list' in df.columns
        has_billed = 'billed_codes_list' in df.columns
        has_verified = 'verified_cpt_codes' in df.columns

        for _, row in df.iterrows():
            note_text = str(row.get("note_text", ""))
            
            # Use Clinical codes for FLAGS (Truth A)
            if has_clinical: codes_for_flags = row['clinical_codes_list']
            elif has_verified: codes_for_flags = row['verified_cpt_codes']
            else: codes_for_flags = ""

            # Use Billed codes for TARGET LABEL (Truth B)
            if has_billed: codes_for_target = row['billed_codes_list']
            elif has_verified: codes_for_target = row['verified_cpt_codes']
            else: codes_for_target = ""

            flags = get_registry_flags_from_codes_and_text(codes_for_flags, note_text)
            target_cpts = clean_code_string(normalize_cpt_list(codes_for_target))

            row_dict = {
                "note_text": note_text,
                "verified_cpt_codes": target_cpts 
            }
            row_dict.update(flags)
            rows.append(row_dict)

        out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
        out_df.to_csv(output_csv, index=False)
        print(f"  - Wrote {len(out_df)} rows.")

def build_registry_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=REGISTRY_FROM_GOLDEN_OUTPUT):
    files = glob.glob(json_pattern)
    rows = []
    for filepath in files:
        with open(filepath, "r") as f:
            try: data = json.load(f)
            except: continue
        if isinstance(data, dict): data = [data]
        for entry in data:
            note_text = entry.get("note_text", "")
            billed_codes = normalize_cpt_list(entry.get("cpt_codes", []))
            rationale_obj = entry.get("coding_support", {}).get("section_3_rationale", {})
            if not rationale_obj: rationale_obj = entry.get("coding_review", {})
            dropped = normalize_cpt_list(rationale_obj.get("dropped_codes", []))
            clinical_codes = billed_codes.union(dropped)

            # Clinical codes -> Registry Flags
            flags = get_registry_flags_from_codes_and_text(list(clinical_codes), note_text)
            flags = enrich_flags_with_registry_entry(flags, entry.get("registry_entry"))

            # Billed codes -> Verified CPT Codes column
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

if __name__ == "__main__":
    build_train_flat_from_golden()
    build_registry_from_csv_batch(CSV_BATCHES)
    build_registry_from_golden()