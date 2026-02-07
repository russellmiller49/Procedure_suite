# Registry Data Prep Skill

Use this skill when working on ML training data preparation for the registry prediction model. This includes extracting labels from golden JSONs, running the 3-tier hydration pipeline, deduplication, and generating train/val/test splits.

## Architecture Overview

The registry data prep uses a **3-tier extraction with hydration** approach:

```
Golden JSON Entry
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Structured Extraction (confidence: 0.95)            │
│ extract_v2_booleans(registry_entry)                         │
│ Source: app/registry/v2_booleans.py                     │
└─────────────────────────────────────────────────────────────┘
       │ (if all-zero)
       ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 2: CPT-Based Derivation (confidence: 0.80)             │
│ derive_booleans_from_json(entry)                            │
│ Uses: cpt_codes field from golden JSON                      │
└─────────────────────────────────────────────────────────────┘
       │ (if still all-zero)
       ▼
┌─────────────────────────────────────────────────────────────┐
│ TIER 3: Keyword Hydration (confidence: 0.60)                │
│ hydrate_labels_from_text(note_text)                         │
│ Uses: 40+ regex patterns with negation filtering            │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ DEDUPLICATION: Priority-based duplicate removal             │
│ structured > cpt > keyword                                  │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ STRATIFIED SPLIT: 70/15/15 with encounter grouping          │
│ Uses: skmultilearn IterativeStratification                  │
└─────────────────────────────────────────────────────────────┘
```

## Key Files

### Core Modules
| File | Purpose |
|------|---------|
| `ml/lib/ml_coder/registry_data_prep.py` | Main data prep logic (3-tier extraction, dedup, splits) |
| `ml/lib/ml_coder/label_hydrator.py` | 3-tier extraction + keyword hydration |
| `app/registry/v2_booleans.py` | Canonical 30 procedure boolean fields |
| `ml/scripts/golden_to_csv.py` | CLI interface for data prep |

### Test Files
| File | Purpose |
|------|---------|
| `tests/ml_coder/test_registry_first_data_prep.py` | Tests for data prep functions |
| `tests/ml_coder/test_label_hydrator.py` | Tests for hydration + deduplication |

### Data Locations
| Location | Purpose |
|----------|---------|
| `data/knowledge/golden_extractions_final/` | PHI-scrubbed golden JSONs (preferred) |
| `data/knowledge/golden_extractions/` | Original golden JSONs (fallback) |
| `data/ml_training/registry_train.csv` | Training set output |
| `data/ml_training/registry_val.csv` | Validation set output |
| `data/ml_training/registry_test.csv` | Test set output |
| `data/ml_training/registry_meta.json` | Extraction metadata |

## Procedure Label Schema

30 canonical procedure boolean fields:

### Bronchoscopy (23 fields)
| Field | Description |
|-------|-------------|
| `diagnostic_bronchoscopy` | Basic diagnostic bronchoscopy |
| `bal` | Bronchoalveolar lavage |
| `bronchial_wash` | Bronchial washing |
| `brushings` | Bronchial brushings |
| `endobronchial_biopsy` | Endobronchial biopsy |
| `tbna_conventional` | Conventional TBNA |
| `linear_ebus` | Linear EBUS (stations) |
| `radial_ebus` | Radial EBUS (peripheral) |
| `navigational_bronchoscopy` | Navigation bronchoscopy |
| `fiducial_placement` | Fiducial marker placement |
| `transbronchial_biopsy` | Transbronchial biopsy |
| `transbronchial_cryobiopsy` | Transbronchial cryobiopsy |
| `therapeutic_aspiration` | Therapeutic aspiration |
| `foreign_body_removal` | Foreign body removal |
| `airway_dilation` | Airway dilation |
| `airway_stent` | Airway stent placement |
| `thermal_ablation` | Thermal ablation |
| `cryotherapy` | Cryotherapy |
| `blvr` | Bronchoscopic lung volume reduction |
| `peripheral_ablation` | Peripheral ablation |
| `bronchial_thermoplasty` | Bronchial thermoplasty |
| `whole_lung_lavage` | Whole lung lavage |
| `rigid_bronchoscopy` | Rigid bronchoscopy |

### Pleural (7 fields)
| Field | Description |
|-------|-------------|
| `thoracentesis` | Thoracentesis |
| `chest_tube` | Chest tube placement |
| `ipc` | Indwelling pleural catheter |
| `medical_thoracoscopy` | Medical thoracoscopy |
| `pleurodesis` | Pleurodesis |
| `pleural_biopsy` | Pleural biopsy |
| `fibrinolytic_therapy` | Fibrinolytic therapy |

## Common Tasks

### 1. Generate Training Data (Full Pipeline)

**Using Make:**
```bash
make registry-prep        # Generate train/val/test CSVs
make registry-prep-dry    # Dry run (preview stats only)
```

**Using CLI:**
```bash
python ml/scripts/golden_to_csv.py \
  --input-dir data/knowledge/golden_extractions_final \
  --output-dir data/ml_training \
  --prefix registry
```

**Using Python API:**
```python
from ml.lib.ml_coder.registry_data_prep import prepare_registry_training_splits

train_df, val_df, test_df = prepare_registry_training_splits()
train_df.to_csv("data/ml_training/registry_train.csv", index=False)
```

### 2. Debug Label Extraction for Single Entry

```python
from ml.lib.ml_coder.label_hydrator import extract_labels_with_hydration

entry = {
    "note_text": "EBUS bronchoscopy with TBNA of stations 4R and 7.",
    "registry_entry": {"linear_ebus_stations": ["4R", "7"]},
    "cpt_codes": [31653],
}

result = extract_labels_with_hydration(entry)
print(f"Source: {result.source}")  # "structured", "cpt", or "keyword"
print(f"Confidence: {result.confidence}")
print(f"Labels: {result.labels}")
```

### 3. Check for Duplicates in Dataset

```python
from ml.lib.ml_coder.registry_data_prep import deduplicate_records

records = [...]  # Your records list
deduped, stats = deduplicate_records(records)

print(f"Removed: {stats['duplicates_removed']}")
print(f"Conflicts: {stats['conflicts_by_source']}")
```

### 4. Add New Keyword Pattern (Tier 3)

Edit `ml/lib/ml_coder/label_hydrator.py`:

```python
KEYWORD_TO_PROCEDURE_MAP = {
    # Add new pattern:
    r"\bnew_procedure\b": [
        ("procedure_field", 0.8),  # (field_name, confidence)
    ],
    ...
}
```

### 5. Add New Alias Mapping

Edit `ml/lib/ml_coder/registry_data_prep.py`:

```python
LABEL_ALIASES = {
    # Add alias → canonical mapping:
    "new_alias": "canonical_field_name",
    ...
}
```

### 6. Run Tests

```bash
# All data prep tests
pytest tests/ml_coder/test_registry_first_data_prep.py -v
pytest tests/ml_coder/test_label_hydrator.py -v

# Deduplication tests only
pytest tests/ml_coder/test_label_hydrator.py::TestDeduplication -v
```

## Output Schema

Each output CSV contains:

| Column | Type | Description |
|--------|------|-------------|
| `note_text` | str | Procedure note text |
| `encounter_id` | str | Stable hash for encounter-level grouping |
| `source_file` | str | Origin golden JSON file |
| `label_source` | str | Extraction tier ("structured", "cpt", "keyword") |
| `label_confidence` | float | Confidence score (0.60-0.95) |
| `[30 procedure columns]` | int | Binary (0/1) procedure labels |

## Expected Statistics

Typical extraction results:
- **Tier 1 (Structured):** ~79%
- **Tier 2 (CPT):** ~18%
- **Tier 3 (Keyword):** ~3%
- **Deduplication:** ~2-3% removed
- **Final dataset:** ~9,400 unique records

## Troubleshooting

### Too Many All-Zero Rows
Check if Tier 1 extraction is working:
1. Verify `registry_entry` structure in golden JSONs
2. Check alias mappings in `LABEL_ALIASES`
3. Ensure `extract_v2_booleans()` handles your schema version

### High Duplicate Count
This is expected when same note appears in multiple golden files:
1. Verify deduplication is enabled (`use_hydration=True`)
2. Check `label_source` distribution in output
3. Review conflict stats in extraction summary

### Stratification Failures
When using `skmultilearn`:
1. Ensure enough samples per label (`min_label_count >= 5`)
2. Check for rare labels that should be filtered
3. Verify encounter grouping isn't creating too few groups

## Related Documentation

- See `CLAUDE.md` section "ML Training Data Workflow" for full pipeline details
- See `docs/optimization_12_16_25.md` for roadmap context
