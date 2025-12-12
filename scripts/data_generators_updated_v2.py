"""
data_generators.py (updated)

Key fixes:
- Robust CPT extraction: supports multiple observed coding_review schemas (cpt_summary / coding_summary / per_code / lines),
  then falls back to registry_entry.billing.cpt_codes, registry_entry.cpt_codes, and top-level cpt_codes.
- Correctly read dropped_codes from registry_entry.coding_support.section_3_rationale (old code looked at entry["coding_support"] which is often missing).
- Expanded CPT->label mappings for codes that were producing 0-label rows.
- Added text-based label inference for labels that were always 0.
- Added group_id/style_type/original_index metadata.
- **NEW v3:** Applied hard-coded patch for known labeling errors (Christopher Hayes/golden_034).
- **NEW v3:** Enforced CSV quoting to prevent integer/string type confusion in CPT columns.
"""

import json
import glob
from pathlib import Path
import re
import os
import pandas as pd
import csv  # <--- Added for QUOTE_NONNUMERIC

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

META_COLS = ["verified_cpt_codes", "patient_id", "group_id", "source_file", "style_type", "original_index"]

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
    if isinstance(raw, (list, tuple, set)):
        raw = str(list(raw))
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
        return ",".join(sorted(normalize_cpt_list(code_set)))
    return ",".join(sorted(list(set(code_set))))

def safe_get(d, *path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur

def compute_patient_id(entry):
    """
    Patient grouping identifier used for splitting.

    - Synthetic notes: keep full MRN including the '_syn_' suffix so each synthetic patient is distinct.
    - Real data: use base MRN (split on '_') to keep related records grouped and protect privacy.
    """
    raw_mrn = safe_get(entry, "registry_entry", "patient_mrn", default=None)
    if raw_mrn is None:
        raw_mrn = entry.get("patient_mrn", "")
    raw_mrn = "" if raw_mrn is None else str(raw_mrn).strip()

    if not raw_mrn or raw_mrn.lower() in {"unknown", "none", "nan"}:
        return ""
    if "_syn_" in raw_mrn:
        return raw_mrn
    return raw_mrn.split("_")[0]

def _extract_cpts_from_coding_review(cr):
    """
    Extract CPTs from multiple coding_review schema variants observed in golden JSONs.
    Returns set[str] of 5-digit CPT codes.
    """
    if not isinstance(cr, dict):
        return set()

    found = set()

    # Legacy-style: coding_review.summary.*
    summary = cr.get("summary")
    if isinstance(summary, dict):
        for field in ["primary_codes", "primary_code", "primary_cpt", "final_codes", "all_cpts"]:
            found |= normalize_cpt_list(summary.get(field))

    # Style A: coding_review.cpt_summary.*
    cpt_summary = cr.get("cpt_summary")
    if isinstance(cpt_summary, dict):
        for field in ["primary_code", "primary_cpt", "final_codes", "all_cpts", "primary_codes"]:
            found |= normalize_cpt_list(cpt_summary.get(field))
        lines = cpt_summary.get("lines")
        if isinstance(lines, list):
            for line in lines:
                if isinstance(line, dict):
                    found |= normalize_cpt_list(line.get("code"))

    # Style B/D: coding_review.coding_summary.*
    coding_summary = cr.get("coding_summary")
    if isinstance(coding_summary, dict):
        for field in ["primary_code", "primary_cpt", "final_codes", "all_cpts", "secondary_cpts"]:
            found |= normalize_cpt_list(coding_summary.get(field))
        lines = coding_summary.get("lines")
        if isinstance(lines, list):
            for line in lines:
                if isinstance(line, dict):
                    found |= normalize_cpt_list(line.get("code"))

    # Style C: coding_review.per_code (list of dicts)
    per_code = cr.get("per_code")
    if isinstance(per_code, list):
        for item in per_code:
            if isinstance(item, dict):
                found |= normalize_cpt_list(item.get("code"))
            else:
                found |= normalize_cpt_list(item)

    # Fallback: sometimes lines can appear directly under coding_review
    lines = cr.get("lines")
    if isinstance(lines, list):
        for line in lines:
            if isinstance(line, dict):
                found |= normalize_cpt_list(line.get("code"))

    return found

def extract_billed_cpt_codes(entry):
    # 1) coding_review (support multiple schema variants; check both top-level and nested)
    cr_set = set()
    cr_set |= _extract_cpts_from_coding_review(entry.get("coding_review"))
    cr_set |= _extract_cpts_from_coding_review(safe_get(entry, "registry_entry", "coding_review", default=None))
    if cr_set:
        return cr_set

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
    dropped = set()
    dropped |= normalize_cpt_list(safe_get(entry, "registry_entry", "coding_support", "section_3_rationale", "dropped_codes", default=None))
    dropped |= normalize_cpt_list(safe_get(entry, "coding_support", "section_3_rationale", "dropped_codes", default=None))
    dropped |= normalize_cpt_list(safe_get(entry, "coding_review", "summary", "dropped_codes", default=None))
    return dropped

def make_group_id(entry, filepath, fallback_index):
    patient_id = compute_patient_id(entry)
    if patient_id:
        return f"MRN::{patient_id}"

    syn_src = safe_get(entry, "synthetic_metadata", "source_file", default=None)
    orig_idx = safe_get(entry, "synthetic_metadata", "original_index", default=None)
    if syn_src is not None and orig_idx is not None:
        return f"{syn_src}::idx{orig_idx}"

    return f"{Path(filepath).name}::idx{fallback_index}"

# =============================================================================
# Label logic
# =============================================================================

BRONCH_ANY = {
    "31622", "31623", "31624", "31625", "31628", "31629", "31632", "31633", "31634",
    "31635", "31627", "31630", "31631", "31636", "31637", "31638",
    "31640", "31641", "31645", "31646", "31647", "31648", "31650", "31651",
    "31652", "31653", "31654", "31660", "31661", "32997",
}
PLEURAL_IPC = {"32550", "32552"}
PLEURAL_THORACENTESIS = {"32554", "32555"}
PLEURAL_CHEST_TUBE = {"32551", "32556", "32557"}
THORACOSCOPY_ANY = {"32601", "32602", "32604", "32606", "32607", "32608", "32609", "32650", "32662"}
PLEURAL_BIOPSY_ANY = {"32602", "32604", "32609", "32400", "32405"}

def get_registry_flags_from_codes_and_text(clinical_codes_raw, note_text):
    cpt_codes = normalize_cpt_list(clinical_codes_raw)
    text_lower = str(note_text or "").lower()

    flags = {col: 0 for col in LABEL_COLS}

    # --- CPT-driven flags ---
    if cpt_codes.intersection(BRONCH_ANY): flags["diagnostic_bronchoscopy"] = 1
    if "31624" in cpt_codes: flags["bal"] = 1
    if "31623" in cpt_codes: flags["brushings"] = 1
    if "31625" in cpt_codes: flags["endobronchial_biopsy"] = 1
    if any(c in cpt_codes for c in ["31629", "31633"]):
        flags["tbna_conventional"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31652", "31653"]):
        flags["linear_ebus"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "31654" in cpt_codes:
        flags["radial_ebus"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "31627" in cpt_codes:
        flags["navigational_bronchoscopy"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31628", "31632"]):
        flags["transbronchial_biopsy"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31645", "31646"]):
        flags["therapeutic_aspiration"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "31635" in cpt_codes:
        flags["foreign_body_removal"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "31630" in cpt_codes:
        flags["airway_dilation"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31631", "31636", "31637", "31638"]):
        flags["airway_stent"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(c in cpt_codes for c in ["31660", "31661"]):
        flags["bronchial_thermoplasty"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "32997" in cpt_codes: flags["whole_lung_lavage"] = 1
    if "31643" in cpt_codes:
        flags["brachytherapy_catheter"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "31640" in cpt_codes or "31641" in cpt_codes:
        flags["mechanical_debulking"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "96570" in cpt_codes or "96571" in cpt_codes: flags["photodynamic_therapy"] = 1
    if any(c in cpt_codes for c in ["31647", "31648", "31650", "31651"]):
        flags["blvr"] = 1; flags["diagnostic_bronchoscopy"] = 1

    if cpt_codes.intersection(PLEURAL_IPC): flags["ipc"] = 1
    if cpt_codes.intersection(PLEURAL_THORACENTESIS): flags["thoracentesis"] = 1
    if cpt_codes.intersection(PLEURAL_CHEST_TUBE): flags["chest_tube"] = 1
    if cpt_codes.intersection(THORACOSCOPY_ANY): flags["medical_thoracoscopy"] = 1
    if cpt_codes.intersection(PLEURAL_BIOPSY_ANY): flags["pleural_biopsy"] = 1
    if any(c in cpt_codes for c in ["32650", "32560", "32561"]): flags["pleurodesis"] = 1
    if any(c in cpt_codes for c in ["32561", "32562"]): flags["fibrinolytic_therapy"] = 1

    # --- Text-driven inference ---
    if any(k in text_lower for k in ["robotic", "ion ", "ion-", "monarch", "shape-sensing", "navigational", "navigation bronc", "electromagnetic navigation"]):
        flags["navigational_bronchoscopy"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(k in text_lower for k in ["radial ebus", "rebus", "radial endobronchial ultrasound"]):
        flags["radial_ebus"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(k in text_lower for k in ["linear ebus", "ebus-tbna", "convex probe"]):
        flags["linear_ebus"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "tbna" in text_lower:
        flags["tbna_conventional"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "cryobiopsy" in text_lower or ("cryo" in text_lower and "biopsy" in text_lower):
        flags["transbronchial_cryobiopsy"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "transbronchial biopsy" in text_lower or "tbbx" in text_lower:
        flags["transbronchial_biopsy"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "endobronchial biopsy" in text_lower or "ebb" in text_lower:
        flags["endobronchial_biopsy"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if any(k in text_lower for k in ["bronchial wash", "bronchial washing", "washings"]):
        flags["bronchial_wash"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "photodynamic" in text_lower or re.search(r"\bpdt\b", text_lower):
        flags["photodynamic_therapy"] = 1; flags["diagnostic_bronchoscopy"] = 1
    if "31634" in cpt_codes:
        if any(k in text_lower for k in ["chartis", "collateral ventilation", "zephyr", "valve", "lung volume reduction", "emphysema"]):
            flags["blvr"] = 1
        flags["diagnostic_bronchoscopy"] = 1
    if any(k in text_lower for k in ["pleurx", "indwelling pleural catheter"]): flags["ipc"] = 1
    if "thoracentesis" in text_lower: flags["thoracentesis"] = 1
    if any(k in text_lower for k in ["chest tube", "pigtail"]): flags["chest_tube"] = 1
    if any(k in text_lower for k in ["thoracoscopy", "vats"]): flags["medical_thoracoscopy"] = 1
    if "pleural biopsy" in text_lower: flags["pleural_biopsy"] = 1
    if "pleurodesis" in text_lower or "talc" in text_lower: flags["pleurodesis"] = 1
    if "rigid" in text_lower and "bronch" in text_lower and "no rigid" not in text_lower:
        flags["rigid_bronchoscopy"] = 1; flags["diagnostic_bronchoscopy"] = 1

    return flags

def enrich_flags_with_registry_entry(flags, registry_entry):
    if not registry_entry: return flags
    proc_nested = registry_entry.get("procedures_performed") or {}
    pleural_nested = registry_entry.get("pleural_procedures") or {}
    cao_modality = str(registry_entry.get("cao_primary_modality") or "").lower().strip()

    def performed(key):
        for container in (proc_nested, pleural_nested):
            val = container.get(key)
            if val is True: return True
            if isinstance(val, dict) and val.get("performed") is True: return True

        # CAO modality-driven mapping (matches canonical v2_booleans behavior)
        if cao_modality:
            if key == "thermal_ablation" and any(t in cao_modality for t in ["thermal", "electrocautery", "argon", "laser", "apc"]):
                return True
            if key == "cryotherapy" and "cryo" in cao_modality:
                return True
            if key == "airway_dilation" and ("dilation" in cao_modality or "balloon" in cao_modality):
                return True

        if registry_entry.get(f"{key}_performed") is True: return True
        if registry_entry.get(key) is True: return True
        if key == "whole_lung_lavage" and (registry_entry.get("wll_volume_instilled_l") or 0) > 0: return True
        if key == "transbronchial_cryobiopsy" and registry_entry.get("nav_cryobiopsy_for_nodule"): return True
        if key == "peripheral_ablation" and registry_entry.get("ablation_peripheral_performed"): return True
        if key == "blvr" and registry_entry.get("blvr_valve_type"): return True
        if key == "navigational_bronchoscopy" and registry_entry.get("nav_platform"): return True
        if key == "radial_ebus" and registry_entry.get("nav_rebus_used"): return True
        return False

    for key in LABEL_COLS:
        if performed(key): flags[key] = 1

    if cao_modality and (flags.get("thermal_ablation") or flags.get("cryotherapy") or flags.get("airway_dilation")):
        flags["diagnostic_bronchoscopy"] = 1

    intervention = str(registry_entry.get("pneumothorax_intervention", "")).lower()
    if "chest tube" in intervention or "pigtail" in intervention: flags["chest_tube"] = 1
    return flags

# =============================================================================
# MAIN LOGIC
# =============================================================================

def build_train_flat_from_golden(json_pattern=GOLDEN_JSON_GLOB, output_csv=TRAIN_FLAT_OUTPUT):
    # Optional flat file generation, can use default csv.writer behavior or pandas
    rows = list(golden_dataset_generator(json_pattern))
    if rows:
        df_flat = pd.DataFrame(rows, columns=TRAIN_FLAT_COLUMNS)
        # Enforce quoting for safety
        df_flat.to_csv(output_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"Wrote {len(df_flat)} rows to {output_csv}")

def golden_dataset_generator(json_dir_pattern):
    # Helper for the flat generator above
    files = glob.glob(json_dir_pattern)
    for filepath in files:
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                continue
        if isinstance(data, dict): data = [data]
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

            # --- PATCH: Fix Known Label Errors Upstream ---
            source_file = Path(filepath).name
            original_index = safe_get(entry, "synthetic_metadata", "original_index", default=None)
            
            # Correction for Christopher Hayes (Row 4.0 in golden_034)
            if source_file == "golden_034.json" and original_index == 4.0:
                print(f"  - Patching {source_file} idx {original_index}: Force navigational_bronchoscopy=0")
                flags["navigational_bronchoscopy"] = 0
            # -----------------------------------------------

            group_id = make_group_id(entry, filepath, i)
            style_type = safe_get(entry, "synthetic_metadata", "style_type", default=None)
            patient_id = compute_patient_id(entry)

            row_dict = {"note_text": note_text}
            row_dict.update(flags)
            row_dict.update({
                "verified_cpt_codes": clean_code_string(billed_codes),
                "patient_id": patient_id,
                "group_id": group_id,
                "source_file": source_file,
                "style_type": style_type,
                "original_index": original_index,
            })
            rows.append(row_dict)

    if rows:
        out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
        # Use quoting=csv.QUOTE_NONNUMERIC to ensure string fields (like "31647") are quoted
        out_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"Wrote {len(out_df)} rows to {output_csv} (quoted).")

def build_registry_from_csv_batch(batch_list):
    for input_csv, output_csv in batch_list:
        if not os.path.exists(input_csv):
            print(f"Skipping {input_csv}: File not found.")
            continue

        print(f"Processing {input_csv} -> {output_csv}...")
        # Force string type for CPT codes on load
        df = pd.read_csv(input_csv, dtype={'verified_cpt_codes': str, 'billed_codes_list': str, 'clinical_codes_list': str})
        rows = []

        has_clinical = "clinical_codes_list" in df.columns
        has_billed = "billed_codes_list" in df.columns
        has_verified = "verified_cpt_codes" in df.columns

        for idx, row in df.iterrows():
            note_text = str(row.get("note_text", "") or "")
            if not note_text.strip():
                continue

            if has_clinical: codes_for_flags = row["clinical_codes_list"]
            elif has_verified: codes_for_flags = row["verified_cpt_codes"]
            else: codes_for_flags = ""

            if has_billed: codes_for_target = row["billed_codes_list"]
            elif has_verified: codes_for_target = row["verified_cpt_codes"]
            else: codes_for_target = ""

            flags = get_registry_flags_from_codes_and_text(codes_for_flags, note_text)

            group_id = row.get("group_id")
            if not group_id:
                group_id = f"{Path(input_csv).name}::idx{idx}"

            patient_id = row.get("patient_id")
            try:
                if pd.isna(patient_id):
                    patient_id = None
            except Exception:
                pass
            if not patient_id and isinstance(group_id, str) and group_id.startswith("MRN::"):
                patient_id = group_id.split("MRN::", 1)[1]

            row_dict = {"note_text": note_text}
            row_dict.update(flags)
            row_dict.update({
                "verified_cpt_codes": clean_code_string(normalize_cpt_list(codes_for_target)),
                "patient_id": patient_id,
                "group_id": group_id,
                "source_file": row.get("source_file", Path(input_csv).name),
                "style_type": row.get("style_type"),
                "original_index": row.get("original_index"),
            })
            rows.append(row_dict)

        out_df = pd.DataFrame(rows, columns=REGISTRY_COLUMNS)
        # Force quoting here too
        out_df.to_csv(output_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(f"  - Wrote {len(out_df)} rows (quoted).")

if __name__ == "__main__":
    build_train_flat_from_golden()
    build_registry_from_csv_batch(CSV_BATCHES)
    build_registry_from_golden()
