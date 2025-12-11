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
TRAIN_CSV_INPUT = "data/ml_training/train.csv"
TRAIN_CSV_OUTPUT = "data/ml_training/train_flat.csv"
REGISTRY_CSV_OUTPUT = "data/ml_training/registry_train.csv"
REGISTRY_FROM_GOLDEN_OUTPUT = "data/ml_training/registry_from_golden.csv"

# Columns for registry_train
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

# Columns for "train_flat" dataset
TRAIN_FLAT_COLUMNS = [
    "source_file", "note_text", "billed_codes_list", "clinical_codes_list",
    "bal", "linear_ebus", "transbronchial_biopsy", "navigational_bronchoscopy",
    "stent_placement", "dilation", "rigid_bronchoscopy", "radial_ebus",
]

# =============================================================================
# Shared helpers
# =============================================================================

def normalize_cpt_list(raw):
    """Convert raw CPT representation into a set of 5-digit string codes."""
    if raw is None: return set()
    if isinstance(raw, (list, tuple, set)):
        return {str(x).strip() for x in raw if str(x).strip()}
    s = str(raw)
    codes = re.findall(r"\b\d{5}\b", s)
    return set(codes)

def iter_golden_entries(payload, filepath):
    """
    Yield note entries from a golden JSON payload.
    Supports legacy list files and the newer category-keyed dict format.
    """
    if isinstance(payload, list):
        for entry in payload:
            yield entry
        return

    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "metadata":
                continue
            if isinstance(value, list):
                for entry in value:
                    yield entry
            elif isinstance(value, dict):
                yield value
            else:
                print(f"Skipping {filepath}: key '{key}' with unsupported type {type(value).__name__}")
        return

    print(f"Skipping {filepath}: unsupported root type {type(payload).__name__}")

# =============================================================================
# PART A: Golden JSON -> ML Train-Style Dataset
# =============================================================================

def golden_dataset_generator(json_dir_pattern):
    files = glob.glob(json_dir_pattern)
    for filepath in files:
        with open(filepath, "r") as f:
            data = json.load(f)

        for entry in iter_golden_entries(data, filepath):
            if not isinstance(entry, dict):
                print(f"Skipping non-dict entry in {filepath}: {type(entry).__name__}")
                continue

            billed_codes = normalize_cpt_list(entry.get("cpt_codes"))
            
            # --- FIX: Robust Rationale Extraction ---
            # Handle varying paths: some files have 'coding_review' at root, others nested
            rationale_obj = entry.get("coding_support", {}).get("section_3_rationale", {})
            if not rationale_obj:
                rationale_obj = entry.get("coding_review", {})
            
            dropped = rationale_obj.get("dropped_codes", [])
            dropped_codes = normalize_cpt_list(dropped)

            clinical_reality_codes = billed_codes.union(dropped_codes)

            flat_row = {
                "source_file": Path(filepath).name,
                "note_text": entry.get("note_text", ""),
                "billed_codes_list": sorted(list(billed_codes)),
                "clinical_codes_list": sorted(list(clinical_reality_codes)),
                "bal": 1 if "31624" in clinical_reality_codes else 0,
                "linear_ebus": 1 if any(c in clinical_reality_codes for c in ["31652", "31653"]) else 0,
                "transbronchial_biopsy": 1 if any(c in clinical_reality_codes for c in ["31628", "31629", "31632", "31633"]) else 0,
                "navigational_bronchoscopy": 1 if "31627" in clinical_reality_codes else 0,
                "stent_placement": 1 if any(c in clinical_reality_codes for c in ["31631","31636","31637","31638"]) else 0,
                "dilation": 1 if "31630" in clinical_reality_codes else 0,
                "rigid_bronchoscopy": infer_rigid_from_entry(entry),
                "radial_ebus": 1 if "31654" in clinical_reality_codes else 0,
            }
            yield flat_row

def infer_rigid_from_entry(entry):
    """
    Checks for 'Rigid' in airway_type across flattened or nested structures.
    """
    registry = entry.get("registry_entry") or {}
    
    # --- FIX: Handle String vs Dict in procedure_setting ---
    # 1. Check root level first (Common in your flattened files)
    airway = str(registry.get("airway_type", "")).lower()
    
    # 2. If empty, try nested if it exists and is a dict
    if not airway:
        setting = registry.get("procedure_setting")
        if isinstance(setting, dict):
            airway = str(setting.get("airway_type", "")).lower()

    if "rigid" in airway:
        return 1

    # 3. Fallback on CPT or note text
    # Note: Removed 31603 (Emergency Tracheostomy) as it is not strictly rigid bronchoscopy
    cpt_codes = set(str(c) for c in entry.get("cpt_codes", []))
    text_lower = str(entry.get("note_text", "")).lower()
    
    if "rigid" in text_lower and "bronch" in text_lower:
        if "no rigid" not in text_lower:
            return 1
    return 0

def build_train_flat_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=TRAIN_CSV_OUTPUT):
    rows = list(golden_dataset_generator(json_pattern))
    if not rows:
        print(f"No rows generated from pattern {json_pattern}")
        return
    df_flat = pd.DataFrame(rows, columns=TRAIN_FLAT_COLUMNS)
    df_flat.to_csv(output_csv, index=False)
    print(f"Wrote {len(df_flat)} rows to {output_csv}")

# =============================================================================
# PART B: CPT + Note -> Registry-Style Flags
# =============================================================================

def get_registry_flags_from_codes_and_text(cpt_raw, note_text):
    cpt_codes = normalize_cpt_list(cpt_raw)
    text_lower = str(note_text).lower()

    flags = {col: 0 for col in REGISTRY_COLUMNS if col not in ["note_text", "verified_cpt_codes"]}

    # --- DIRECT CPT MAPPING ---
    if "31622" in cpt_codes: flags["diagnostic_bronchoscopy"] = 1
    if "31624" in cpt_codes: flags["bal"] = 1
    if "31623" in cpt_codes: flags["brushings"] = 1
    if "31625" in cpt_codes: flags["endobronchial_biopsy"] = 1
    if "31629" in cpt_codes: flags["tbna_conventional"] = 1

    if any(c in cpt_codes for c in ["31652", "31653"]): flags["linear_ebus"] = 1
    if "31654" in cpt_codes: flags["radial_ebus"] = 1
    if "31627" in cpt_codes: flags["navigational_bronchoscopy"] = 1

    if any(c in cpt_codes for c in ["31645", "31646"]): flags["therapeutic_aspiration"] = 1
    if "31635" in cpt_codes: flags["foreign_body_removal"] = 1
    
    # --- FIX: CPT Correction ---
    if "31630" in cpt_codes: flags["airway_dilation"] = 1 # 31631 removed from here
    if any(c in cpt_codes for c in ["31631", "31636", "31637", "31638"]): flags["airway_stent"] = 1 # 31631 added here
    
    if any(c in cpt_codes for c in ["31660", "31661"]): flags["bronchial_thermoplasty"] = 1
    if "32997" in cpt_codes: flags["whole_lung_lavage"] = 1

    # Pleural
    if "32550" in cpt_codes: flags["ipc"] = 1
    if any(c in cpt_codes for c in ["32554", "32555"]): flags["thoracentesis"] = 1
    if "32551" in cpt_codes: flags["chest_tube"] = 1
    if any(c in cpt_codes for c in ["32601", "32650"]): flags["medical_thoracoscopy"] = 1
    if any(c in cpt_codes for c in ["32650", "32560"]): flags["pleurodesis"] = 1

    if any(c in cpt_codes for c in ["31647", "31648", "31650", "31651"]): flags["blvr"] = 1

    # --- HYBRID: codes + text context ---

    # --- FIX: Cryobiopsy Logic ---
    # Added 31645 (Therapeutic Asp) to the list, as per robotic sample data
    if any(c in cpt_codes for c in ["31628", "31632", "31645"]):
        if "cryo" in text_lower or "freeze" in text_lower:
            flags["transbronchial_cryobiopsy"] = 1
        elif "31628" in cpt_codes or "31632" in cpt_codes:
            flags["transbronchial_biopsy"] = 1

    # Rigid bronchoscopy
    if "rigid" in text_lower and "bronch" in text_lower:
        flags["rigid_bronchoscopy"] = 1

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
    """
    FIX: Handles FLATTENED registry structure (matching golden_*.json).
    Falls back to nested checks if flat keys aren't found.
    """
    if not registry_entry:
        return flags

    # 1. Try Nested (Strict Schema)
    proc_nested = registry_entry.get("procedures_performed") or {}
    pleural_nested = registry_entry.get("pleural_procedures") or {}
    
    # 2. Helper to check both Nested and Flat keys
    def is_performed(key):
        # Check nested schema
        if proc_nested.get(key, {}).get("performed") is True: return True
        if pleural_nested.get(key, {}).get("performed") is True: return True
        
        # Check Flat keys (found in your sample data)
        # e.g. "ablation_peripheral_performed": true
        if registry_entry.get(f"{key}_performed") is True: return True
        if registry_entry.get(key) is True: return True
        
        # Specific flat key mappings based on your samples
        if key == "whole_lung_lavage" and (registry_entry.get("wll_volume_instilled_l") or 0) > 0: return True
        if key == "transbronchial_cryobiopsy" and registry_entry.get("nav_cryobiopsy_for_nodule"): return True
        if key == "peripheral_ablation" and registry_entry.get("ablation_peripheral_performed"): return True
        if key == "blvr" and registry_entry.get("blvr_valve_type"): return True
        if key == "navigational_bronchoscopy" and registry_entry.get("nav_platform"): return True
        if key == "radial_ebus" and registry_entry.get("nav_rebus_used"): return True
        
        return False

    # Apply to all flags
    for col in flags.keys():
        if is_performed(col):
            flags[col] = 1
            
    # Extra check for Chest Tube via intervention text (common in your samples)
    intervention = str(registry_entry.get("pneumothorax_intervention", "")).lower()
    if "chest tube" in intervention or "pigtail" in intervention:
        flags["chest_tube"] = 1

    return flags

def build_registry_from_train_csv(input_csv=TRAIN_CSV_INPUT, output_csv=REGISTRY_CSV_OUTPUT):
    if not os.path.exists(input_csv):
        print(f"Input CSV {input_csv} not found.")
        return

    df = pd.read_csv(input_csv)
    rows = []

    for _, row in df.iterrows():
        note_text = str(row.get("note_text", ""))
        cpt_raw = row.get("verified_cpt_codes", "")
        flags = get_registry_flags_from_codes_and_text(cpt_raw, note_text)

        row_dict = {
            "note_text": note_text,
            "verified_cpt_codes": str(row.get("verified_cpt_codes", ""))
        }
        row_dict.update(flags)
        rows.append(row_dict)

    out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
    out_df.to_csv(output_csv, index=False)
    print(f"Wrote {len(out_df)} rows to {output_csv}")

def build_registry_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=REGISTRY_FROM_GOLDEN_OUTPUT):
    files = glob.glob(json_pattern)
    rows = []

    for filepath in files:
        with open(filepath, "r") as f:
            data = json.load(f)

        for entry in iter_golden_entries(data, filepath):
            if not isinstance(entry, dict):
                print(f"Skipping non-dict entry in {filepath}: {type(entry).__name__}")
                continue

            note_text = entry.get("note_text", "")
            billed_codes = normalize_cpt_list(entry.get("cpt_codes"))
            
            # Use same robust rationale logic as above
            rationale_obj = entry.get("coding_support", {}).get("section_3_rationale", {})
            if not rationale_obj:
                rationale_obj = entry.get("coding_review", {})
            
            dropped = normalize_cpt_list(rationale_obj.get("dropped_codes", []))
            clinical_codes = billed_codes.union(dropped)

            flags = get_registry_flags_from_codes_and_text(list(clinical_codes), note_text)
            flags = enrich_flags_with_registry_entry(flags, entry.get("registry_entry"))

            row_dict = {
                "note_text": note_text,
                "verified_cpt_codes": ",".join(sorted(clinical_codes))
            }
            row_dict.update(flags)
            rows.append(row_dict)

    if not rows:
        print(f"No rows generated from golden JSON pattern {json_pattern}")
        return

    out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
    out_df.to_csv(output_csv, index=False)
    print(f"Wrote {len(out_df)} rows to {output_csv}")

if __name__ == "__main__":
    build_train_flat_from_golden()
    build_registry_from_train_csv()
    build_registry_from_golden()
