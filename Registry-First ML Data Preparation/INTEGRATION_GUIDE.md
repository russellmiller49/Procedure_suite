# Registry-First ML Data Preparation — Integration Guide

## Overview

This solution provides a reliable way to convert golden JSON files into properly stratified CSV files for multi-label ML classification. It implements the "registry-first" approach described in CLAUDE.md:

```
Text → Registry Extraction (ML/LLM) → Deterministic Rules → CPT Codes
```

## Files Provided

| File | Purpose | Destination |
|------|---------|-------------|
| `golden_to_csv.py` | Standalone CLI tool | `ml/scripts/golden_to_csv.py` |
| `registry_data_prep.py` | Module integration | `ml/lib/ml_coder/registry_data_prep.py` |
| `test_registry_data_prep.py` | Test suite | `tests/ml_coder/test_registry_data_prep.py` |
| `makefile_snippet.mk` | Makefile targets | Append to `Makefile` |

## Quick Start

### Option 1: Standalone Script

```bash
python ml/scripts/golden_to_csv.py \
    --input-dir data/knowledge/golden_extractions_final \
    --output-dir data/ml_training \
    --prefix registry
```

### Option 2: Module Integration

```python
from ml.lib.ml_coder.registry_data_prep import prepare_registry_training_splits

# Generate train/val/test splits
train_df, val_df, test_df = prepare_registry_training_splits()

# Save to CSV
train_df.to_csv("data/ml_training/registry_train.csv", index=False)
val_df.to_csv("data/ml_training/registry_val.csv", index=False)
test_df.to_csv("data/ml_training/registry_test.csv", index=False)
```

### Option 3: Makefile

```bash
make registry-prep-final
```

## Installation Steps

1. **Copy files to your repo:**
   ```bash
   cp golden_to_csv.py /path/to/proc_suite/ml/scripts/
   cp registry_data_prep.py /path/to/proc_suite/ml/lib/ml_coder/
   cp test_registry_data_prep.py /path/to/proc_suite/tests/ml_coder/
   ```

2. **Add Makefile targets:**
   ```bash
   cat makefile_snippet.mk >> /path/to/proc_suite/Makefile
   ```

3. **Update data_prep.py (optional):**
   ```python
   # In ml/lib/ml_coder/data_prep.py, add:
   from .registry_data_prep import prepare_registry_training_splits
   ```

4. **Install dependencies:**
   ```bash
   pip install pandas numpy skmultilearn
   ```

## Output Format

The generated CSV files have this structure:

| Column | Type | Description |
|--------|------|-------------|
| `note_text` | str | Procedure note text |
| `encounter_id` | str | Stable ID for grouping (prevents data leakage) |
| `source_file` | str | Origin golden_*.json filename |
| `diagnostic_bronchoscopy` | int | 0/1 binary label |
| `bal` | int | 0/1 binary label |
| ... | ... | (30 total procedure labels) |

## Key Features

### 1. Schema Version Compatibility
Handles both V2 (flat) and V3 (granular) registry structures:
```python
# V2 flat
{"procedures_performed": {"bal": True}}

# V2 nested
{"procedures_performed": {"bronchoscopy": {"bal": True}}}

# V3 granular
{"granular_data": {"bronchoscopy": {"bal": {"performed": True}}}}
```

### 2. Field Alias Mapping
Automatically maps alternate field names:
```python
LABEL_ALIASES = {
    "ebus_linear": "linear_ebus",
    "tap": "thoracentesis",
    "ipc_placement": "ipc",
    # ... 15 more
}
```

### 3. Multi-Label Stratification
Uses `skmultilearn.IterativeStratification` for proper stratified splits:
- Maintains label distribution across splits
- Respects encounter-level grouping (no data leakage)
- Falls back to random split if skmultilearn unavailable

### 4. Rare Label Filtering
Automatically removes labels with fewer than N positive examples:
```bash
python golden_to_csv.py --min-label-count 5  # Default
```

## Canonical 30 Procedure Labels

### Bronchoscopy (22)
- diagnostic_bronchoscopy, bal, bronchial_wash, brushings
- endobronchial_biopsy, tbna_conventional, linear_ebus, radial_ebus
- navigational_bronchoscopy, transbronchial_biopsy, transbronchial_cryobiopsy
- therapeutic_aspiration, foreign_body_removal, airway_dilation, airway_stent
- thermal_ablation, cryotherapy, blvr, peripheral_ablation
- bronchial_thermoplasty, whole_lung_lavage, rigid_bronchoscopy

### Pleural (7)
- thoracentesis, chest_tube, ipc, medical_thoracoscopy
- pleurodesis, pleural_biopsy, fibrinolytic_therapy

## Workflow Integration

### Complete Registry-First Training Pipeline

```bash
# 1. PHI-scrub golden JSONs (if not already done)
make platinum-final

# 2. Convert to ML training CSVs
make registry-prep-final

# 3. Train the model
python ml/scripts/train_roberta.py \
    --train-csv data/ml_training/registry_train.csv \
    --val-csv data/ml_training/registry_val.csv \
    --test-csv data/ml_training/registry_test.csv

# 4. Export to ONNX for production
make export-registry-model
```

## Troubleshooting

### Common Issues

1. **"No golden_*.json files found"**
   - Check the input directory path
   - Ensure files follow the `golden_*.json` naming pattern

2. **"No valid records extracted"**
   - Golden JSONs may have empty `registry_entry`
   - Check for missing `note_text` fields
   - Run with `--dry-run` to see statistics

3. **"skmultilearn not available"**
   - Install with: `pip install skmultilearn`
   - Falls back to random split with encounter grouping

4. **"Dropped X rare labels"**
   - Normal behavior when labels have < min_label_count examples
   - Adjust with `--min-label-count 3` for smaller datasets

### Validation

```bash
# Run tests
pytest tests/ml_coder/test_registry_data_prep.py -v

# Dry run to check extraction
python ml/scripts/golden_to_csv.py --dry-run

# Verify CSV structure
head data/ml_training/registry_train.csv
```

## Maintenance

When updating the registry schema:

1. Update `ALL_PROCEDURE_LABELS` in `registry_data_prep.py`
2. Add any new aliases to `LABEL_ALIASES`
3. Update `app/registry/v2_booleans.py` for consistency
4. Run tests: `pytest tests/ml_coder/test_registry_data_prep.py`
