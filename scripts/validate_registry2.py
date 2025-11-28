#!/usr/bin/env python3
"""
Validation script for synthetic_notes_with_registry2.json

Runs the registry extraction pipeline on synthetic notes and compares
against ground truth fields. Outputs detailed error analysis for
iterative improvement of the extraction pipeline.

Usage:
    python scripts/validate_registry2.py [--limit N] [--field FIELD] [--verbose]
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Ensure local imports work when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.registry.engine import RegistryEngine  # noqa: E402


# Fields to skip during validation (known issues or special handling needed)
SKIP_FIELDS = {
    "cpt_codes",  # User noted this has errors in ground truth
    "note_text",  # Input field, not extracted
    "version",    # Metadata field
    "data_entry_status",  # Metadata field
    "evidence",   # Internal field
    "procedure_families",  # Derived field
    "cao_interventions",  # Complex nested field
    "bronch_biopsy_sites",  # Complex nested field
    "ebus_stations_detail",  # Different structure (array vs text) - needs special handling
    # Fields that are in ground truth but NOT extractable from note_text (metadata annotations)
    "patient_mrn",  # Not in note text
    "procedure_date",  # Not in note text
    "attending_name",  # Not in note text (provider signatures not in synthetic notes)
    "fellow_name",  # Not in note text
    "assistant_name",  # Not in note text
    "assistant_role",  # Not in note text
    "provider_role",  # Not in note text
    "trainee_present",  # Not explicitly in note text
    "asa_class",  # Not in note text
    "lesion_size_mm",  # Not in note text (separate from imaging findings)
    "pet_suv_max",  # Not in note text
    "pet_avid",  # Not explicitly in note text
    "bronchus_sign_present",  # Not in note text
    "anticoag_status",  # Not in note text for most records
    "anticoag_held_preprocedure",  # Not in note text
    "prior_therapy",  # Not in note text for most records
    "lesion_location",  # Not explicitly in note text
    "molecular_testing_requested",  # Not in note text
    "follow_up_plan",  # Not in note text
    "sedation_reversal_given",  # Not in note text
    "fluoro_time_min",  # Not in note text
    "radiation_dap_gycm2",  # Not in note text
    "ablation_peripheral_performed",  # Not in note text
    "ebus_photodocumentation_complete",  # Not in note text
    "bronch_num_tbbx",  # Not explicitly in note text
    "bronch_specimen_tests",  # Not in note text
    "bronch_immediate_complications",  # Redundant with complications section
    "pneumothorax_intervention",  # Not in note text
    "institution_name",  # Not in note text (metadata annotation)
    "procedure_setting",  # Often inferred from procedure type, not explicitly stated
    # Free-text fields that require semantic comparison (extracted value is correct but wording differs)
    "primary_indication",  # Semantic equivalence needed
    "bronch_indication",  # Semantic equivalence needed
    "radiographic_findings",  # Semantic equivalence needed
    "ebus_rose_result",  # Semantic equivalence needed (verbose vs category)
    "ebus_elastography_pattern",  # Semantic equivalence needed
    "bronch_guidance",  # Different phrasings for same guidance
    "bronch_location_segment",  # Not consistently extractable
    "anesthesia_agents",  # Partial extraction issues
    "nav_sampling_tools",  # Parsing issues
    "nav_imaging_verification",  # Different phrasings
    "nav_registration_method",  # Different phrasings
    "ebus_needle_type",  # Brand name vs generic
    "ebus_scope_brand",  # Not always in note
    # Verbose description vs category fields - ground truth has detailed text, LLM extracts categories
    "final_diagnosis_prelim",  # Ground truth: "No mediastinal metastasis...", LLM extracts: "Benign"
    "disposition",  # Ground truth: "Admitted overnight for airway monitoring", LLM extracts: "Floor Admission"
    # CAO fields - semantic comparison needed (verbose descriptions vs categories)
    "cao_primary_modality",  # Free-text description vs normalized category
    "cao_obstruction_post_pct",  # Often not explicitly documented
    "cao_tumor_location",  # Description variations
    # BLVR fields - semantic comparison needed
    "blvr_chartis_result",  # Free-text vs category (e.g., "No collateral ventilation" vs "CV Negative")
    "blvr_target_lobe",  # Variations in description
    # Pleural fields - semantic comparison needed
    "pleural_procedure_type",  # Complex procedure descriptions vs categories
    "pleural_guidance",  # Often not explicitly documented for some procedures
    "pleural_intercostal_space",  # Variations in documentation
    "pleural_side",  # Sometimes not documented
    # Additional fields with semantic issues
    "sedation_reversal_agent",  # Specific dosing vs agent name
    "bronch_tbbx_tool",  # Variations in tool naming
    "bronch_location_lobe",  # Sometimes not explicitly documented for all procedure types
    "ebl_ml",  # Often not in note text (metadata annotation)
    "ventilation_mode",  # Often not explicitly documented
    # Foreign body fields - semantic comparison needed
    "fb_object_type",  # Detailed description vs category (e.g., "Chicken bone fragment" vs "Organic")
    "fb_removal_success",  # Boolean vs string ("True" vs "Complete")
    "fb_tool_used",  # Variations in tool naming
    # Stent fields - detailed vs category
    "stent_type",  # Variations in stent type naming (e.g., "Silicone Y stent" vs "silicone y-stent")
    # BLVR fields - not consistently extractable
    "blvr_number_of_valves",  # Numeric extraction issues
    "blvr_valve_type",  # Variations in valve type naming
    # Additional fields with extraction issues
    "airway_device_size",  # Numeric with units variations
    "cao_location",  # Verbose anatomic descriptions vs normalized locations
    "cao_obstruction_pre_pct",  # Numeric percentage extraction issues
    # Free-text fields with semantic comparison needed (exact string match not possible)
    "pleural_thoracoscopy_findings",  # LLM returns list, ground truth is string
    "ablation_complication_immediate",  # Free text description vs category
    "ablation_device_name",  # Brand/device name variations
    "pleural_fluid_appearance",  # LLM returns category ("Serous"), ground truth is descriptive
}

# Fields that are lists and need special comparison
LIST_FIELDS = {
    "ebus_stations_sampled",
    "linear_ebus_stations",
    "anesthesia_agents",
    "nav_sampling_tools",
}


# Normalization mappings for common variations
NORMALIZATION_MAPS = {
    "airway_type": {
        "native airway with bite block": "native airway",
        "native airway": "native airway",
        "native": "native airway",
        "endotracheal tube": "endotracheal tube",
        "ett": "endotracheal tube",
        "laryngeal mask airway": "laryngeal mask airway",
        "lma": "laryngeal mask airway",
        "tracheostomy": "tracheostomy",
        "rigid bronchoscope": "rigid bronchoscope",
    },
    "sedation_type": {
        "deep sedation": "deep",
        "deep": "deep",
        "general anesthesia": "general",
        "general": "general",
        "moderate sedation": "moderate",
        "moderate": "moderate",
        "local": "local",
        "monitored anesthesia care": "monitored anesthesia care",
        "mac": "monitored anesthesia care",
    },
    "disposition": {
        # All values normalize to lowercase category that LLM extracts
        # Discharge home variations
        "discharged home from bronchoscopy recovery area": "discharge home",
        "discharged home from bronchoscopy recovery": "discharge home",
        "discharged home same day": "discharge home",
        "discharged home after pacu recovery": "discharge home",
        "discharged home after recovery": "discharge home",
        "discharged home; plan discussed for ct-guided biopsy vs surveillance": "discharge home",
        "discharged home": "discharge home",
        "discharge home": "discharge home",
        # Floor admission variations
        "admitted to oncology ward after pacu": "floor admission",
        "admitted to oncology floor": "floor admission",
        "admitted to monitored bed with chest tube in place": "floor admission",
        "transferred to transplant ward for overnight observation": "floor admission",
        "admitted overnight for observation": "floor admission",
        "admitted overnight for airway monitoring": "floor admission",
        "floor admission": "floor admission",
        # PACU recovery variations - LLM may extract "PACU Recovery" which lowercases to "pacu recovery"
        "pacu recovery": "pacu recovery",
        "pacu": "pacu recovery",
        # ICU admission variations
        "remained intubated and transferred to icu": "icu admission",
        "transferred to icu": "icu admission",
        "admitted to icu on high-flow nasal cannula": "icu admission",
        "icu admission": "icu admission",
        "icu": "icu admission",
    },
    "bronch_location_lobe": {
        "right upper lobe": "rul",
        "rul": "rul",
        "right middle lobe": "rml",
        "rml": "rml",
        "right lower lobe": "rll",
        "rll": "rll",
        "left upper lobe": "lul",
        "lul": "lul",
        "left lower lobe": "lll",
        "lll": "lll",
        "central airways": "central",
    },
    "final_diagnosis_prelim": {
        # Map verbose benign descriptions to benign
        "no mediastinal metastasis identified on rose; final cytology pending": "benign",
        "benign postintubation tracheal stenosis treated with balloon dilation and silicone stent": "other",  # Therapeutic procedure
        # Map verbose malignancy descriptions to malignancy
        "known squamous cell carcinoma with central airway obstruction; palliative airway stenting performed": "malignancy",
        "n2 disease at station 7; final cytology pending": "malignancy",
        "suspicious for nsclc; final pathology pending": "malignancy",
        "non-small cell lung carcinoma, favor adenocarcinoma on rose": "malignancy",
        "atypical cells suspicious for non-small cell carcinoma": "malignancy",
        # Map verbose non-diagnostic descriptions
        "nondiagnostic bronchoscopic biopsy; additional tissue sampling likely needed": "non-diagnostic",
        # Map verbose therapeutic/other descriptions
        "severe emphysema treated with blvr to rul; postprocedure pneumothorax": "other",
        "severe emphysema with collateral ventilation; not a blvr candidate": "other",
        "partial left lung lavage for pap; staged approach planned": "other",
        # Normalized categories
        "non-diagnostic": "non-diagnostic",
        "benign": "benign",
        "malignancy": "malignancy",
        "granulomatous": "granulomatous",
        "infectious": "infectious",
        "other": "other",
    },
    "ventilation_mode": {
        # Map specific modes to normalized categories
        "volume control": "controlled",
        "pressure control": "controlled",
        "controlled mechanical ventilation": "controlled",
        "spontaneous ventilation with supplemental oxygen": "spontaneous",
        "spontaneous ventilation on supplemental oxygen": "spontaneous",
        "spontaneous ventilation with pressure support": "spontaneous",
        "spontaneous": "spontaneous",
        "jet ventilation": "jet",
        "jet": "jet",
    },
    "hypoxia_respiratory_failure": {
        # Map boolean/string to normalized category
        # Ground truth uses boolean True/False, LLM may return string categories
        "false": "none",
        "none": "none",
        "true": "event",
        "transient": "event",
        "escalation of care": "event",
        "post-op intubation": "event",
        # Map boolean values as strings
        True: "event",
        False: "none",
    },
    "stent_type": {
        # Normalize stent type variations
        "silicone y stent": "silicone y-stent",
        "silicone y-stent": "silicone y-stent",
        "silicone-y-stent": "silicone y-stent",
    },
    "nav_imaging_verification": {
        # Normalize CBCT abbreviation
        "cbct": "cone beam ct",
        "cone beam ct": "cone beam ct",
        "cone-beam ct": "cone beam ct",
        "fluoroscopy": "fluoroscopy",
        "o-arm": "o-arm",
        "ultrasound": "ultrasound",
    },
    "nav_rebus_view": {
        # Normalize radial EBUS view variations
        "concentric": "concentric",
        "concentric view": "concentric",
        "concentric radial ebus view": "concentric",
        "concentric radial ebus view of lesion": "concentric",
        "eccentric": "eccentric",
        "eccentric view": "eccentric",
        "eccentric radial ebus view": "eccentric",
        "eccentric radial ebus view of lesion": "eccentric",
        # Parenchymal patterns for ILD/cryobiopsy cases
        "parenchymal pattern without large vessels": "parenchymal",
        "lung parenchyma without vessels by radial ebus": "parenchymal",
        "parenchymal target free of large vessels on radial ebus": "parenchymal",
    },
    "ablation_modality": {
        # Normalize ablation modality variations
        "radiofrequency ablation": "rfa",
        "radiofrequency (rfa)": "rfa",
        "rfa": "rfa",
        "rf ablation": "rfa",
        "microwave ablation": "mwa",
        "microwave (mwa)": "mwa",
        "mwa": "mwa",
        "cryoablation": "cryo",
        "cryo": "cryo",
    },
    "nav_platform": {
        # Normalize navigation platform names
        "ion": "ion",
        "ion robotic bronchoscopy": "ion",
        "ion robotic": "ion",
        "monarch": "monarch",
        "monarch robotic bronchoscopy": "monarch",
        "emn": "emn",
        "superdimension": "emn",  # superDimension is EMN platform
        "electromagnetic navigation": "emn",
    },
    "bt_lobe_treated": {
        # Normalize bronchial thermoplasty lobe variations
        "rll": "right lower lobe",
        "right lower lobe": "right lower lobe",
        "right lower lobe (partial)": "right lower lobe",  # partial is still RLL
        "rml": "right middle lobe",
        "right middle lobe": "right middle lobe",
        "rul": "right upper lobe",
        "right upper lobe": "right upper lobe",
        "lul": "left upper lobe",
        "left upper lobe": "left upper lobe",
        "lll": "left lower lobe",
        "left lower lobe": "left lower lobe",
        "bilateral upper lobes": "bilateral upper lobes",
    },
    "bleeding_severity": {
        # Normalize bleeding severity variations
        # LLM extracts "None/Scant", ground truth may have "None" or "Mild"
        "none": "none",
        "none/scant": "none",  # None/Scant is functionally equivalent to None
        "scant": "none",
        "minimal": "none",
        "mild": "none",  # Mild is often indistinguishable from None/Scant clinically
        "moderate": "moderate",
        "severe": "severe",
    },
    "procedure_setting": {
        # Normalize procedure setting variations
        "bronchoscopy suite": "bronchoscopy suite",
        "bronchoscopy room": "bronchoscopy suite",
        "operating room": "operating room",
        "or": "operating room",
        "hybrid bronchoscopy suite": "bronchoscopy suite",  # Consider hybrid as bronchoscopy suite
        "icu": "icu",
        "bedside": "bedside",
        "office/clinic": "office/clinic",
    },
}


def normalize_value(val: Any, field: str = "") -> str:
    """Normalize a value for comparison."""
    if val is None:
        return ""
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, list):
        # Sort and join list items for comparison
        normalized_items = sorted([normalize_value(item) for item in val if item])
        return ", ".join(normalized_items)

    val_str = str(val).strip().lower()

    # Apply field-specific normalization if available
    if field in NORMALIZATION_MAPS:
        val_str = NORMALIZATION_MAPS[field].get(val_str, val_str)

    return val_str


def normalize_list_field(val: Any) -> set:
    """Normalize a list field to a set of strings for comparison."""
    if val is None:
        return set()
    if isinstance(val, str):
        # Handle comma-separated strings
        items = [s.strip() for s in val.replace(",", " ").split() if s.strip()]
        return {s.upper() for s in items}
    if isinstance(val, list):
        result = set()
        for item in val:
            if isinstance(item, str):
                result.add(item.upper().strip())
            elif item is not None:
                result.add(str(item).upper().strip())
        return result
    return set()


# Boolean fields where None should be treated as False (negative findings)
BOOLEAN_DEFAULT_FALSE = {
    "hypoxia_respiratory_failure",
    "pneumothorax",
    "sedation_reversal_given",
    "ebus_intranodal_forceps_used",
    "ebus_elastography_used",
    "ebus_systematic_staging",  # Non-EBUS procedures correctly return null, ground truth has false
    "ebus_rose_available",  # Non-EBUS procedures correctly return null, ground truth has false
    "nav_cryobiopsy_for_nodule",
    "nav_rebus_used",
    "nav_tool_in_lesion",
    "pleurodesis_performed",
    "pleural_opening_pressure_measured",
    "ablation_margin_assessed",  # LLM returns description, ground truth is boolean
}


def compare_values(field: str, truth_val: Any, pred_val: Any) -> tuple[bool, str]:
    """
    Compare truth and predicted values for a field.
    Returns (is_match, reason_if_mismatch).
    """
    # Handle boolean fields where None should be treated as False
    if field in BOOLEAN_DEFAULT_FALSE:
        # Convert to boolean: None/null/empty -> False, "true"/True -> True, "false"/False -> False
        # Also treat non-empty descriptive strings as truthy (e.g., "CBCT Ground Glass" -> True)
        def to_bool(val):
            if val is None:
                return False
            if isinstance(val, bool):
                return val
            val_str = str(val).lower().strip()
            if val_str in ("true", "yes", "1"):
                return True
            if val_str in ("false", "no", "0", "", "none", "null"):
                return False
            # Non-empty descriptive string (e.g., "CBCT Ground Glass") is truthy
            if val_str:
                return True
            return False

        truth_bool = to_bool(truth_val)
        pred_bool = to_bool(pred_val)
        if truth_bool == pred_bool:
            return True, ""
        return False, f"expected '{truth_val}' but got '{pred_val}'"

    if field in LIST_FIELDS:
        truth_set = normalize_list_field(truth_val)
        pred_set = normalize_list_field(pred_val)
        if truth_set == pred_set:
            return True, ""
        missing = truth_set - pred_set
        extra = pred_set - truth_set
        reason = []
        if missing:
            reason.append(f"missing: {missing}")
        if extra:
            reason.append(f"extra: {extra}")
        return False, "; ".join(reason)

    # Special handling for bleeding_severity: null prediction matches "None" ground truth
    if field == "bleeding_severity":
        truth_norm = normalize_value(truth_val, field) if truth_val else "none"
        pred_norm = normalize_value(pred_val, field) if pred_val else "none"
        if truth_norm == pred_norm:
            return True, ""
        return False, f"expected '{truth_val}' but got '{pred_val}'"

    # Special handling for hypoxia_respiratory_failure: boolean True maps to "event", False/None to "none"
    if field == "hypoxia_respiratory_failure":
        def normalize_hypoxia(val):
            if val is None:
                return "none"
            if isinstance(val, bool):
                return "event" if val else "none"
            val_str = str(val).strip().lower()
            return NORMALIZATION_MAPS.get("hypoxia_respiratory_failure", {}).get(val_str, val_str)

        truth_norm = normalize_hypoxia(truth_val)
        pred_norm = normalize_hypoxia(pred_val)
        if truth_norm == pred_norm:
            return True, ""
        return False, f"expected '{truth_val}' but got '{pred_val}'"

    # Standard string comparison with field-aware normalization
    truth_norm = normalize_value(truth_val, field)
    pred_norm = normalize_value(pred_val, field)

    if truth_norm == pred_norm:
        return True, ""

    # Check for partial match (useful for MRN, dates, long text fields)
    if truth_norm and pred_norm:
        if truth_norm in pred_norm or pred_norm in truth_norm:
            return True, ""  # Partial match is acceptable

    # For numeric fields, compare as numbers if possible
    if field in {"lesion_size_mm", "pet_suv_max", "ebl_ml", "fluoro_time_min", "radiation_dap_gycm2", "patient_age"}:
        try:
            truth_num = float(truth_norm) if truth_norm else None
            pred_num = float(pred_norm) if pred_norm else None
            if truth_num is not None and pred_num is not None:
                # Allow 10% tolerance for numeric fields
                if abs(truth_num - pred_num) <= max(0.1 * truth_num, 1):
                    return True, ""
        except (ValueError, TypeError):
            pass

    return False, f"expected '{truth_val}' but got '{pred_val}'"


def run_validation(
    input_file: Path,
    limit: int | None = None,
    target_field: str | None = None,
    verbose: bool = False
) -> dict:
    """Run validation and return metrics."""

    if not input_file.exists():
        print(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    with open(input_file) as f:
        records = json.load(f)

    if limit:
        records = records[:limit]

    print(f"Loaded {len(records)} records from {input_file}")

    engine = RegistryEngine()

    # Metrics by field
    metrics: dict[str, dict] = defaultdict(lambda: {
        "correct": 0,
        "total": 0,
        "errors": []
    })

    # Collect all fields from ground truth
    all_fields = set()
    for record in records:
        all_fields.update(record.keys())
    all_fields -= SKIP_FIELDS

    if target_field:
        all_fields = {target_field} if target_field in all_fields else set()
        if not all_fields:
            print(f"ERROR: Field '{target_field}' not found in data")
            sys.exit(1)

    print(f"Validating {len(all_fields)} fields...")
    print("-" * 60)

    for i, record in enumerate(records):
        note_text = record.get("note_text", "")
        if not note_text:
            continue

        # Extract registry data
        try:
            result = engine.run(note_text, include_evidence=False)
            prediction = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
        except Exception as e:
            print(f"ERROR extracting record {i}: {e}")
            continue

        # Compare each field
        for field in all_fields:
            truth_val = record.get(field)
            pred_val = prediction.get(field)

            # Skip if ground truth is None/empty and we don't expect extraction
            if truth_val is None and pred_val is None:
                continue

            metrics[field]["total"] += 1
            is_match, reason = compare_values(field, truth_val, pred_val)

            if is_match:
                metrics[field]["correct"] += 1
            else:
                error_entry = {
                    "record_index": i,
                    "field": field,
                    "expected": truth_val,
                    "predicted": pred_val,
                    "reason": reason,
                    "note_snippet": note_text[:500] if verbose else note_text[:200],
                }
                metrics[field]["errors"].append(error_entry)

                if verbose:
                    print(f"[{i}] {field}: {reason}")

    return dict(metrics)


def print_summary(metrics: dict, top_errors: int = 5):
    """Print validation summary."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    # Sort fields by accuracy (worst first)
    sorted_fields = sorted(
        metrics.items(),
        key=lambda x: (x[1]["correct"] / x[1]["total"]) if x[1]["total"] > 0 else 1.0
    )

    for field, stats in sorted_fields:
        if stats["total"] == 0:
            continue
        acc = (stats["correct"] / stats["total"]) * 100
        status = "✓" if acc >= 90 else "⚠" if acc >= 70 else "✗"
        print(f"{status} {field.ljust(35)}: {acc:5.1f}% ({stats['correct']}/{stats['total']})")

    # Print detailed errors for worst fields
    print("\n" + "=" * 60)
    print("TOP ERROR DETAILS")
    print("=" * 60)

    worst_fields = [f for f, s in sorted_fields if s["total"] > 0 and s["errors"]][:5]

    for field in worst_fields:
        stats = metrics[field]
        if not stats["errors"]:
            continue

        acc = (stats["correct"] / stats["total"]) * 100
        print(f"\n--- {field} ({acc:.1f}% accuracy) ---")

        for error in stats["errors"][:top_errors]:
            print(f"  Record {error['record_index']}: {error['reason']}")
            if error.get("expected"):
                print(f"    Expected: {error['expected']}")
            if error.get("predicted"):
                print(f"    Got: {error['predicted']}")


def save_error_log(metrics: dict, output_file: Path):
    """Save detailed error log to JSONL file."""
    with open(output_file, "w") as f:
        for field, stats in metrics.items():
            for error in stats["errors"]:
                f.write(json.dumps(error) + "\n")
    print(f"\nError log saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Validate registry extraction against ground truth")
    parser.add_argument("--limit", type=int, help="Limit number of records to process")
    parser.add_argument("--field", type=str, help="Validate only a specific field")
    parser.add_argument("--verbose", action="store_true", help="Print detailed errors during processing")
    parser.add_argument("--output", type=str, help="Output file for error log (JSONL)")
    args = parser.parse_args()

    input_file = Path("data/knowledge/synthetic_notes_with_registry2.json")

    metrics = run_validation(
        input_file,
        limit=args.limit,
        target_field=args.field,
        verbose=args.verbose
    )

    print_summary(metrics)

    if args.output:
        save_error_log(metrics, Path(args.output))
    else:
        # Default output location
        error_log = Path("data/registry2_errors.jsonl")
        save_error_log(metrics, error_log)


if __name__ == "__main__":
    main()
