# Registry Prodigy Workflow (Diamond Loop)

This repo supports a human-in-the-loop loop for improving the **registry multi-label procedure classifier** using Prodigy’s `textcat.manual` (multi-label checkbox UI) plus disagreement sampling.

## Label Schema (Single Source of Truth)

- Canonical label IDs + order: `modules/ml_coder/registry_label_schema.py`
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

```bash
make registry-prodigy-export \
  REG_PRODIGY_DATASET=registry_v1 \
  REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human.csv
```

## 4) Merge Human Labels as Tier-0 and Rebuild Splits

Human labels should be merged **before splitting** to avoid leakage.

```bash
make registry-prep-with-human HUMAN_REGISTRY_CSV=data/ml_training/registry_human.csv
```

This writes new:
- `data/ml_training/registry_train.csv`
- `data/ml_training/registry_val.csv`
- `data/ml_training/registry_test.csv`

## 5) Retrain (BiomedBERT / RoBERTa script)

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

## 6) Iterate

Repeat batches until disagreement rate drops and validation metrics plateau.

