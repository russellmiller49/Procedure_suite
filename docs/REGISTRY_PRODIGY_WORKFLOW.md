# Registry Prodigy Workflow (Diamond Loop)

This repo supports a human-in-the-loop loop for improving the **registry multi-label procedure classifier** using Prodigy’s `textcat.manual` (multi-label checkbox UI) plus disagreement sampling.

## Label Schema (Single Source of Truth)

- Canonical label IDs + order: `ml/lib/ml_coder/registry_label_schema.py`
- Model training CSVs should contain:
  - `note_text`
  - `encounter_id`
  - `label_source`
  - `label_confidence`
  - 32 procedure label columns (see `REGISTRY_LABELS`)

## 1) Prepare a Prodigy Batch (pre-checked labels)

Inputs:
- A JSONL of unlabeled notes (each line with any of: `note_text`, `text`, or `note`)
- Optional `cpt_codes` array/string per record (used for CPT-based prefill + disagreement)

Commands:
```bash
make registry-prodigy-prepare \
  REG_PRODIGY_INPUT_FILE=data/ml_training/registry_unlabeled_notes.jsonl \
  REG_PRODIGY_COUNT=200
```

### Annotating a specific JSONL file (example)

If you have a targeted file you want to annotate (e.g. `registry_trach_peg.jsonl`), just point `REG_PRODIGY_INPUT_FILE` at it:

```bash
make registry-prodigy-prepare \
  REG_PRODIGY_INPUT_FILE=data/ml_training/registry_trach_peg.jsonl \
  REG_PRODIGY_COUNT=150

# Use a dataset name that reflects the batch/topic
make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_trach_peg_v1
```

Outputs:
- Batch tasks: `data/ml_training/registry_prodigy_batch.jsonl`
- Manifest (dedup): `data/ml_training/registry_prodigy_manifest.json`

## 2) Annotate in Prodigy

```bash
make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_v1
```

## Reset / Start Over (clean restart)

If you need to restart annotation cleanly (e.g., you prepared the wrong batch or switched tasks/labels), reset both:
- the generated batch/manifest files, and
- the Prodigy DB dataset.

```bash
make registry-prodigy-reset REG_PRODIGY_DATASET=registry_v1
```

## 3) Export Prodigy Annotations → Training CSV

Important:
- Export reads **everything currently in the Prodigy dataset** and writes a fresh CSV.
- The export **overwrites** the output path you provide (it does not append to an existing CSV file).

```bash
make registry-prodigy-export \
  REG_PRODIGY_DATASET=registry_v1 \
  REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human.csv
```

## 4) (Recommended) Keep a single “master” human CSV across iterations

If you want to retain prior human labels while also adding new Prodigy sessions/batches, use:

```bash
# Export current dataset snapshot to an "updates" file
make registry-prodigy-export \
  REG_PRODIGY_DATASET=registry_v1 \
  REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human_updates.csv

# Merge updates into your master file (append new encounter_ids, override overlaps)
make registry-human-merge-updates \
  REG_HUMAN_BASE_CSV=data/ml_training/registry_human.csv \
  REG_HUMAN_UPDATES_CSV=data/ml_training/registry_human_updates.csv \
  REG_HUMAN_OUT_CSV=data/ml_training/registry_human.csv
```

Notes:
- This works whether updates overlap or are entirely new (no overlap is common when you annotate a new batch).
- The merge keys on `encounter_id` (computed from `note_text` when missing).

## 5) Merge Human Labels as Tier-0 and Rebuild Splits

Human labels should be merged **before splitting** to avoid leakage.

```bash
make registry-prep-with-human HUMAN_REGISTRY_CSV=data/ml_training/registry_human.csv
```

This writes new:
- `data/ml_training/registry_train.csv`
- `data/ml_training/registry_val.csv`
- `data/ml_training/registry_test.csv`

## 6) Retrain (BiomedBERT / RoBERTa script)

```bash
python scripts/train_roberta.py \
  --train-csv data/ml_training/registry_train.csv \
  --val-csv data/ml_training/registry_val.csv \
  --test-csv data/ml_training/registry_test.csv \
  --output-dir data/models/roberta_registry \
  --epochs 1
```

Artifacts:
- Model dir: `data/models/roberta_registry/`
- Thresholds (bundle-friendly): `data/models/roberta_registry/thresholds.json`
- Legacy flat thresholds: `data/models/roberta_registry_thresholds.json`
- Label order: `data/models/roberta_registry/label_order.json`

## 7) Iterate

Repeat batches until disagreement rate drops and validation metrics plateau.

