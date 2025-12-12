"""
data_generators.py (updated)

Key fixes:
- Robust CPT extraction: prefer coding_review summary primary codes, then registry_entry.billing.cpt_codes, then registry_entry.cpt_codes, then top-level cpt_codes.
- Correctly read dropped_codes from registry_entry.coding_support.section_3_rationale (old code looked at entry["coding_support"] which is often missing).
- Expanded CPT->label mappings for codes that were producing 0-label rows: 32556/32557/32552/32602/32662/31634/31640.
- Added text-based label inference for labels that were always 0 (bronchial_wash, photodynamic_therapy) and for cases with missing/incorrect codes (e.g., robotic navigation notes).
- Added group_id/style_type/original_index metadata to enable *case-level* stratified splitting (prevents split drift while avoiding leakage).

Outputs:
- train_flat.csv: optional "flat" schema (kept for backwards compat)
- registry_from_golden.csv: full registry schema used for ML (note_text + labels + verified_cpt_codes + metadata)
"""

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

# If you also convert existing CSVs (train/test/edge) -> updated registry schema:
CSV_BATCHES = [
    ("data/ml_training/train_flat.csv",           "data/ml_training/registry_train.csv"),
    ("data/ml_training/registry_test.csv",        "data/ml_training/registry_test.csv"),
    ("data/ml_training/registry_edge_cases.csv",  "data/ml_training/registry_edge_cases.csv"),
]

# =============================================================================
# Schema
# =============================================================================

LABEL_COLS = [
    # Bronchoscopy
    "diagnostic_bronchoscopy", "bal", "bronchial_wash", "brushings",
    "endobronchial_biopsy", "transbronchial_biopsy", "transbronchial_cryobiopsy",
    "tbna_conventional", "linear_ebus", "radial_ebus", "navigational_bronchoscopy",
    "therapeutic_aspiration", "foreign_body_removal", "airway_dilation", "airway_stent",
    "thermal_ablation", "cryotherapy", "mechanical_debulking", "brachytherapy_catheter",
    "blvr", "peripheral_ablation", "bronchial_thermoplasty", "whole_lung_lavage",
    "rigid_bronchoscopy", "photodynamic_therapy",
    # Pleural / Thoracic
    "thoracentesis", "chest_tube", "ipc", "medical_thoracoscopy",
    "pleural_biopsy", "pleurodesis", "fibrinolytic_therapy",
]

META_COLS = ["verified_cpt_codes", "group_id", "source_file", "style_type", "original_index"]

REGISTRY_COLUMNS = ["note_text"] + LABEL_COLS + META_COLS

TRAIN_FLAT_COLUMNS = [
    "source_file", "group_id", "style_type", "original_index",
    "note_text", "billed_codes_list", "clinical_codes_list",
    "bal", "linear_ebus", "transbronchial_biopsy", "navigational_bronchoscopy",
    "stent_placement", "dilation", "rigid_bronchoscopy", "radial_ebus",
]

# =============================================================================
# Helpers
# =============================================================================

_CPT_RE = re.compile(r"\b\d{5}\b")

def normalize_cpt_list(raw):
    """Return a set[str] of 5-digit codes from many possible raw inputs."""
    if raw is None:
        return set()
    # If already a list/tuple/set, stringify for regex
    if isinstance(raw, (list, tuple, set)):
        raw = str(list(raw))
    # If dict, stringify too
    if isinstance(raw, dict):
        raw = json.dumps(raw, ensure_ascii=False)
    try:
        if pd.isna(raw):
            return set()
    except Exception:
        pass
    s = str(raw)
    return set(_CPT_RE.findall(s))

def clean_code_string(code_set):
    """Stable, comma-delimited codes."""
    if not code_set:
        return ""
    if isinstance(code_set, str):
        # already clean-ish
        return ",".join(sorted(normalize_cpt_list(code_set)))
    return ",".join(sorted(list(set(code_set))))

def safe_get(d, *path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

def extract_billed_cpt_codes(entry):
    """
    Choose the best available 'final billed' CPT set for the entry.
    Priority:
      1) coding_review.summary.primary_codes
      2) registry_entry.billing.cpt_codes[*].code
      3) registry_entry.cpt_codes
      4) top-level cpt_codes
    """
    # 1) coding_review.summary.primary_codes
    primary = safe_get(entry, "coding_review", "summary", "primary_codes", default=None)
    primary_set = normalize_cpt_list(primary)
    if primary_set:
        return primary_set

    # 2) registry_entry.billing.cpt_codes
    billing_cpts = safe_get(entry, "registry_entry", "billing", "cpt_codes", default=None)
    if isinstance(billing_cpts, list):
        codes = set()
        for obj in billing_cpts:
            if isinstance(obj, dict) and obj.get("code"):
                codes |= normalize_cpt_list(obj.get("code"))
            else:
                codes |= normalize_cpt_list(obj)
        if codes:
            return codes

    # 3) registry_entry.cpt_codes
    reg_cpts = safe_get(entry, "registry_entry", "cpt_codes", default=None)
    reg_set = normalize_cpt_list(reg_cpts)
    if reg_set:
        return reg_set

    # 4) top-level
    return normalize_cpt_list(entry.get("cpt_codes", []))

def extract_dropped_cpt_codes(entry):
    """
    Extract 'dropped' codes (codes considered but not billed) so FLAGS reflect clinical reality.
    Common locations:
      - registry_entry.coding_support.section_3_rationale.dropped_codes
      - entry.coding_support.section_3_rationale.dropped_codes (older)
      - coding_review.summary.dropped_codes (if present)
    """
    dropped = set()

    dropped |= normalize_cpt_list(safe_get(entry, "registry_entry", "coding_support", "section_3_rationale", "dropped_codes", default=None))
    dropped |= normalize_cpt_list(safe_get(entry, "coding_support", "section_3_rationale", "dropped_codes", default=None))
    dropped |= normalize_cpt_list(safe_get(entry, "coding_review", "summary", "dropped_codes", default=None))

    return dropped

def make_group_id(entry, filepath, fallback_index):
    """
    Case-level grouping to prevent leakage *and* avoid split drift:
    Prefer synthetic_metadata.source_file + original_index.
    Fall back to registry_entry.patient_mrn (or its base), else filepath+index.
    """
    syn_src = safe_get(entry, "synthetic_metadata", "source_file", default=None)
    orig_idx = safe_get(entry, "synthetic_metadata", "original_index", default=None)
    if syn_src is not None and orig_idx is not None:
        return f"{syn_src}::idx{orig_idx}"

    mrn = safe_get(entry, "registry_entry", "patient_mrn", default=None)
    if mrn:
        mrn = str(mrn)
        # If you suffix synthetic MRNs like 12345_syn_7, keep the base to group all variants
        mrn_base = mrn.split("_syn_")[0]
        return f"MRN::{mrn_base}"

    return f"{Path(filepath).name}::idx{fallback_index}"

# =============================================================================
# Label logic
# =============================================================================

# CPT groups (expand as needed)
BRONCH_ANY = {
    "31622", "31623", "31624", "31625", "31628", "31629", "31632", "31633", "31634",
    "31635", "31627", "31630", "31631", "31636", "31637", "31638",
    "31640", "31641", "31645", "31646",
    "31647", "31648", "31650", "31651",
    "31652", "31653", "31654",
    "31660", "31661",
    "32997",
}

PLEURAL_IPC = {"32550", "32552"}  # insertion + removal
PLEURAL_THORACENTESIS = {"32554", "32555"}
PLEURAL_CHEST_TUBE = {"32551", "32556", "32557"}  # pigtail/chest tube/pleural drain
THORACOSCOPY_ANY = {"32601", "32602", "32604", "32606", "32607", "32608", "32609", "32650", "32662"}
PLEURAL_BIOPSY_ANY = {"32602", "32604", "32609", "32400", "32405"}

def get_registry_flags_from_codes_and_text(clinical_codes_raw, note_text):
    cpt_codes = normalize_cpt_list(clinical_codes_raw)
    text_lower = str(note_text or "").lower()

    flags = {col: 0 for col in LABEL_COLS}

    # --- CPT-driven flags ---
    if cpt_codes.intersection(BRONCH_ANY):
        flags["diagnostic_bronchoscopy"] = 1

    if "31624" in cpt_codes:
        flags["bal"] = 1
    if "31623" in cpt_codes:
        flags["brushings"] = 1
    if "31625" in cpt_codes:
        flags["endobronchial_biopsy"] = 1

    # TBNA / EBUS
    if any(c in cpt_codes for c in ["31629", "31633"]):
        flags["tbna_conventional"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31652", "31653"]):
        flags["linear_ebus"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if "31654" in cpt_codes:
        flags["radial_ebus"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Navigation
    if "31627" in cpt_codes:
        flags["navigational_bronchoscopy"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Biopsy
    if any(c in cpt_codes for c in ["31628", "31632"]):
        flags["transbronchial_biopsy"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Airway interventions
    if any(c in cpt_codes for c in ["31645", "31646"]):
        flags["therapeutic_aspiration"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if "31635" in cpt_codes:
        flags["foreign_body_removal"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if "31630" in cpt_codes:
        flags["airway_dilation"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31631", "31636", "31637", "31638"]):
        flags["airway_stent"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Bronchial thermoplasty / WLL
    if any(c in cpt_codes for c in ["31660", "31661"]):
        flags["bronchial_thermoplasty"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if "32997" in cpt_codes:
        flags["whole_lung_lavage"] = 1

    # Destructive / debulking
    if "31643" in cpt_codes:
        flags["brachytherapy_catheter"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if "31640" in cpt_codes or "31641" in cpt_codes:
        flags["mechanical_debulking"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Photodynamic therapy (codes are often missing in synthetic notes, so add text below too)
    if "96570" in cpt_codes or "96571" in cpt_codes:
        flags["photodynamic_therapy"] = 1

    # BLVR
    if any(c in cpt_codes for c in ["31647", "31648", "31650", "31651"]):
        flags["blvr"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Pleural / thoracic
    if cpt_codes.intersection(PLEURAL_IPC):
        flags["ipc"] = 1
    if cpt_codes.intersection(PLEURAL_THORACENTESIS):
        flags["thoracentesis"] = 1
    if cpt_codes.intersection(PLEURAL_CHEST_TUBE):
        flags["chest_tube"] = 1
    if cpt_codes.intersection(THORACOSCOPY_ANY):
        flags["medical_thoracoscopy"] = 1
    if cpt_codes.intersection(PLEURAL_BIOPSY_ANY):
        flags["pleural_biopsy"] = 1

    if any(c in cpt_codes for c in ["32650", "32560", "32561"]):
        flags["pleurodesis"] = 1
    if any(c in cpt_codes for c in ["32561", "32562"]):
        flags["fibrinolytic_therapy"] = 1

    # --- Text-driven inference (fills holes + fixes always-0 labels) ---
    # Navigation / robotic platforms
    if any(k in text_lower for k in ["robotic", "ion ", "ion-", "monarch", "shape-sensing", "navigational", "navigation bronc", "electromagnetic navigation"]):
        flags["navigational_bronchoscopy"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Radial EBUS
    if any(k in text_lower for k in ["radial ebus", "rebus", "radial endobronchial ultrasound"]):
        flags["radial_ebus"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Linear EBUS / EBUS-TBNA
    if any(k in text_lower for k in ["linear ebus", "ebus-tbna", "convex probe"]):
        flags["linear_ebus"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # TBNA keyword
    if "tbna" in text_lower:
        flags["tbna_conventional"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Cryobiopsy vs standard biopsy
    if "cryobiopsy" in text_lower or ("cryo" in text_lower and "biopsy" in text_lower):
        flags["transbronchial_cryobiopsy"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if "transbronchial biopsy" in text_lower or "tbbx" in text_lower:
        flags["transbronchial_biopsy"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if "endobronchial biopsy" in text_lower or "ebb" in text_lower:
        flags["endobronchial_biopsy"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Wash vs BAL
    if any(k in text_lower for k in ["bronchial wash", "bronchial washing", "washings"]):
        flags["bronchial_wash"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Photodynamic therapy often shows up as text only
    if "photodynamic" in text_lower or re.search(r"\bpdt\b", text_lower):
        flags["photodynamic_therapy"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # BLVR balloon occlusion / Chartis (31634 often)
    if "31634" in cpt_codes:
        if any(k in text_lower for k in ["chartis", "collateral ventilation", "zephyr", "valve", "lung volume reduction", "emphysema"]):
            flags["blvr"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    # Pleural text cues
    if any(k in text_lower for k in ["pleurx", "indwelling pleural catheter"]):
        flags["ipc"] = 1
    if "thoracentesis" in text_lower:
        flags["thoracentesis"] = 1
    if any(k in text_lower for k in ["chest tube", "pigtail"]):
        flags["chest_tube"] = 1
    if any(k in text_lower for k in ["thoracoscopy", "vats"]):
        flags["medical_thoracoscopy"] = 1
    if "pleural biopsy" in text_lower:
        flags["pleural_biopsy"] = 1
    if "pleurodesis" in text_lower or "talc" in text_lower:
        flags["pleurodesis"] = 1

    # Rigid bronch
    if "rigid" in text_lower and "bronch" in text_lower and "no rigid" not in text_lower:
        flags["rigid_bronchoscopy"] = 1
        flags["diagnostic_bronchoscopy"] = 1

    return flags

def enrich_flags_with_registry_entry(flags, registry_entry):
    """Use structured fields (when present) to set/confirm labels."""
    if not registry_entry:
        return flags

    proc_nested = registry_entry.get("procedures_performed") or {}
    pleural_nested = registry_entry.get("pleural_procedures") or {}

    def performed(key):
        # nested dict patterns like {performed: True}
        for container in (proc_nested, pleural_nested):
            val = container.get(key)
            if val is True:
                return True
            if isinstance(val, dict) and val.get("performed") is True:
                return True

        # direct registry_entry checks
        if registry_entry.get(f"{key}_performed") is True:
            return True
        if registry_entry.get(key) is True:
            return True

        # special mappings
        if key == "whole_lung_lavage" and (registry_entry.get("wll_volume_instilled_l") or 0) > 0:
            return True
        if key == "transbronchial_cryobiopsy" and registry_entry.get("nav_cryobiopsy_for_nodule"):
            return True
        if key == "peripheral_ablation" and registry_entry.get("ablation_peripheral_performed"):
            return True
        if key == "blvr" and registry_entry.get("blvr_valve_type"):
            return True
        if key == "navigational_bronchoscopy" and registry_entry.get("nav_platform"):
            return True
        if key == "radial_ebus" and registry_entry.get("nav_rebus_used"):
            return True

        return False

    for key in LABEL_COLS:
        if performed(key):
            flags[key] = 1

    # pneumothorax intervention => chest_tube
    intervention = str(registry_entry.get("pneumothorax_intervention", "")).lower()
    if "chest tube" in intervention or "pigtail" in intervention:
        flags["chest_tube"] = 1

    return flags

# =============================================================================
# PART A: Golden JSON -> Train-flat schema (optional)
# =============================================================================

def golden_dataset_generator(json_dir_pattern):
    files = glob.glob(json_dir_pattern)
    for filepath in files:
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                continue
        if isinstance(data, dict):
            data = [data]

        for i, entry in enumerate(data):
            billed_codes = extract_billed_cpt_codes(entry)
            dropped = extract_dropped_cpt_codes(entry)
            clinical_reality_codes = billed_codes.union(dropped)

            group_id = make_group_id(entry, filepath, i)
            style_type = safe_get(entry, "synthetic_metadata", "style_type", default=None)
            original_index = safe_get(entry, "synthetic_metadata", "original_index", default=None)

            flat_row = {
                "source_file": Path(filepath).name,
                "group_id": group_id,
                "style_type": style_type,
                "original_index": original_index,
                "note_text": (entry.get("note_text") or ""),
                "billed_codes_list": clean_code_string(billed_codes),
                "clinical_codes_list": clean_code_string(clinical_reality_codes),
                "bal": 1 if "31624" in clinical_reality_codes else 0,
                "linear_ebus": 1 if any(c in clinical_reality_codes for c in ["31652", "31653"]) else 0,
                "transbronchial_biopsy": 1 if any(c in clinical_reality_codes for c in ["31628", "31632"]) else 0,
                "navigational_bronchoscopy": 1 if "31627" in clinical_reality_codes else 0,
                "stent_placement": 1 if any(c in clinical_reality_codes for c in ["31631", "31636", "31637", "31638"]) else 0,
                "dilation": 1 if "31630" in clinical_reality_codes else 0,
                "rigid_bronchoscopy": 1 if ("rigid" in str(entry.get("note_text", "")).lower()) else 0,
                "radial_ebus": 1 if "31654" in clinical_reality_codes else 0,
            }
            yield flat_row

def build_train_flat_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=TRAIN_FLAT_OUTPUT):
    rows = list(golden_dataset_generator(json_pattern))
    if rows:
        df_flat = pd.DataFrame(rows, columns=TRAIN_FLAT_COLUMNS)
        df_flat.to_csv(output_csv, index=False)
        print(f"Wrote {len(df_flat)} rows to {output_csv}")

# =============================================================================
# PART B: Registry schema builder
# =============================================================================

def build_registry_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=REGISTRY_FROM_GOLDEN_OUTPUT):
    files = glob.glob(json_pattern)
    rows = []

    for filepath in files:
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                continue
        if isinstance(data, dict):
            data = [data]

        for i, entry in enumerate(data):
            note_text = entry.get("note_text") or ""
            if not str(note_text).strip():
                continue
            billed_codes = extract_billed_cpt_codes(entry)
            dropped = extract_dropped_cpt_codes(entry)
            clinical_codes = billed_codes.union(dropped)

            flags = get_registry_flags_from_codes_and_text(list(clinical_codes), note_text)
            flags = enrich_flags_with_registry_entry(flags, entry.get("registry_entry"))

            group_id = make_group_id(entry, filepath, i)
            style_type = safe_get(entry, "synthetic_metadata", "style_type", default=None)
            original_index = safe_get(entry, "synthetic_metadata", "original_index", default=None)

            row_dict = {"note_text": note_text}
            row_dict.update(flags)
            row_dict.update({
                "verified_cpt_codes": clean_code_string(billed_codes),
                "group_id": group_id,
                "source_file": Path(filepath).name,
                "style_type": style_type,
                "original_index": original_index,
            })
            rows.append(row_dict)

    if rows:
        out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
        out_df.to_csv(output_csv, index=False)
        print(f"Wrote {len(out_df)} rows to {output_csv}")

# =============================================================================
# CSV batch processing (optional)
# =============================================================================

def build_registry_from_csv_batch(batch_list):
    """
    Convert existing CSV batches to updated registry schema.
    - If the input already has verified_cpt_codes, we keep it.
    - If it has billed_codes_list / clinical_codes_list, we use those.
    """
    for input_csv, output_csv in batch_list:
        if not os.path.exists(input_csv):
            print(f"Skipping {input_csv}: File not found.")
            continue

        print(f"Processing {input_csv} -> {output_csv}...")
        df = pd.read_csv(input_csv)
        rows = []

        has_clinical = "clinical_codes_list" in df.columns
        has_billed = "billed_codes_list" in df.columns
        has_verified = "verified_cpt_codes" in df.columns

        for idx, row in df.iterrows():
            note_text = str(row.get("note_text", "") or "")
            if not note_text.strip():
                continue

            # Truth A (flags): clinical codes if available
            if has_clinical:
                codes_for_flags = row["clinical_codes_list"]
            elif has_verified:
                codes_for_flags = row["verified_cpt_codes"]
            else:
                codes_for_flags = ""

            # Truth B (target codes): billed codes if available
            if has_billed:
                codes_for_target = row["billed_codes_list"]
            elif has_verified:
                codes_for_target = row["verified_cpt_codes"]
            else:
                codes_for_target = ""

            flags = get_registry_flags_from_codes_and_text(codes_for_flags, note_text)

            group_id = row.get("group_id")
            if not group_id:
                group_id = f"{Path(input_csv).name}::idx{idx}"

            row_dict = {"note_text": note_text}
            row_dict.update(flags)
            row_dict.update({
                "verified_cpt_codes": clean_code_string(normalize_cpt_list(codes_for_target)),
                "group_id": group_id,
                "source_file": row.get("source_file", Path(input_csv).name),
                "style_type": row.get("style_type"),
                "original_index": row.get("original_index"),
            })
            rows.append(row_dict)

        out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
        out_df.to_csv(output_csv, index=False)
        print(f"  - Wrote {len(out_df)} rows.")

if __name__ == "__main__":
    # Optional: regenerate from golden JSON
    build_train_flat_from_golden()
    build_registry_from_csv_batch(CSV_BATCHES)
    build_registry_from_golden()
