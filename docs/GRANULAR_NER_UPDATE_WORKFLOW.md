# Granular NER: Updating Training Data from `Python_update_scripts/`

This repo uses generated Python scripts in `data/granular annotations/Python_update_scripts/` to append new annotated notes into the granular NER training artifacts under `data/ml_training/granular_ner/`.

Key facts:
- Update scripts typically call `from ml.scripts.add_training_case import add_case` and then `add_case(id, text, entities, REPO_ROOT)`.
- `add_case()` **appends** to JSONL files; re-running scripts can create duplicates.
- The repo includes utilities to validate alignment, fix common span schema issues, regenerate stats, convert spans to BIO, and dedupe duplicate note IDs.

## Outputs (what gets populated)

Running update scripts (directly or via the runner) populates/updates:
- `data/ml_training/granular_ner/ner_dataset_all.jsonl` (primary training file)
- `data/ml_training/granular_ner/notes.jsonl` (debug notes)
- `data/ml_training/granular_ner/spans.jsonl` (debug spans)

Then you typically generate:
- `data/ml_training/granular_ner/stats.json` (summary stats for the above)
- `data/ml_training/granular_ner/ner_bio_format.jsonl` + `data/ml_training/granular_ner/ner_bio_format.stats.json` (token/BIO training format)

## Recommended workflow (incremental: you added a few new update scripts)

### 1) Run the update scripts and fix failures

Run everything (recommended when you’re not sure what’s new), and capture failures:

```bash
python ops/tools/run_python_update_scripts.py --pattern '*.py' --failure-report reports/python_update_scripts_failures.json
```

If it reports failures, open `reports/python_update_scripts_failures.json` and fix the corresponding update scripts (most failures are `get_span()` text mismatches or import path issues).

Tips for fixing update scripts:
- If you use `**get_span(...)`, make sure `get_span()` never returns `None` for a required entity. Prefer raising a clear `ValueError` when a term isn’t found.
- Ensure the searched term matches the note text exactly (case/spacing/punctuation) and that `occurrence=N` is correct.

### 2) Dedupe duplicates created by re-runs (safe; makes backups)

Because update scripts append, re-running scripts can create duplicate IDs. Deduping is the safest “cleanup” step:

```bash
python ml/scripts/dedupe_granular_ner.py --base-dir data/ml_training/granular_ner --write
```

Notes:
- This creates a timestamped backup folder under `data/ml_training/granular_ner/_backup_*/` first.
- Default strategy keeps the record with the most entities for a given note id (ties broken by longer text, then latest).

### 3) Validate span alignment

```bash
python ml/scripts/validate_ner_alignment.py data/ml_training/granular_ner/ner_dataset_all.jsonl
```

This checks that each span’s offsets are in-bounds and (when a span text field exists) that it matches the text slice.

### 4) Regenerate `stats.json`

```bash
python ml/scripts/regenerate_granular_ner_stats.py --base-dir data/ml_training/granular_ner --write
```

This recomputes alignment counts + label counts from `ner_dataset_all.jsonl` (the real training file).

### 4.5) Add `NEG_STENT` labels (optional; recommended for stent label quality)

If you want `DEV_STENT` to mean “stent deployed/placed” (and avoid training false positives from
phrases like “stent in place”, “stent removed”, or “no stent placed”), generate `NEG_STENT` labels
as a post-processing step:

```bash
python ml/scripts/label_neg_stent.py --write
```

This writes:
- `data/ml_training/granular_ner/ner_dataset_all.neg_stent.jsonl` (updated training spans)
- `reports/neg_stent_labeling_report.json` (what changed/was added; review this)

Notes:
- `NEG_STENT` is reserved for explicit absence (e.g., “no stent placed/needed/indicated”).
- “Stent in place / good position” mentions may be relabeled to `CTX_STENT_PRESENT` (disable with `--no-label-present`).
- Stent removal/exchange/migration is intentionally kept as `DEV_STENT`.
- `ml/scripts/label_neg_stent.py` is **dry-run by default**; add `--write` to write `--output`.

⚠️ Important: update scripts must call `add_case(note_id, raw_text, entities, repo_root)` (in that order).
If a script swaps `note_id` and `raw_text`, it can corrupt the dataset (e.g., `"text": "<script>.py"` with zero-length spans).
`ml/scripts/add_training_case.py` now raises a `ValueError` when it detects this common swap.

Optional: validate alignment on the new file:

```bash
python ml/scripts/validate_ner_alignment.py data/ml_training/granular_ner/ner_dataset_all.neg_stent.jsonl
```

### 4.6) Clean the dataset labels (recommended after `label_neg_stent.py --write`)

After you generate `ner_dataset_all.neg_stent.jsonl`, run the cleaner to:
- merge known “alias” labels (e.g., `MEAS_VOLUME` → `MEAS_VOL`)
- drop labels you don’t want the NER model to learn

```bash
python data/ml_training/clean_data.py \
  --input data/ml_training/granular_ner/ner_dataset_all.neg_stent.jsonl \
  --output data/ml_training/granular_ner/ner_dataset_all.cleaned.jsonl
```

Notes:
- The merge/drop rules live in `data/ml_training/clean_data.py` (`MERGE_MAP`, `DROP_LABELS`).
- The cleaner supports both `entities` (current) and legacy `spans` keys.
- `PROC_METHOD` is merged into `PROC_ACTION` for training (so the model learns a single “procedure” action label).

### 5) Rebuild BIO format

```bash
python ml/scripts/convert_spans_to_bio.py \
  --input data/ml_training/granular_ner/ner_dataset_all.jsonl \
  --output data/ml_training/granular_ner/ner_bio_format.jsonl \
  --model microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext \
  --max-length 512
```

If you ran the `NEG_STENT` + clean steps above, use the cleaned file as input instead:

```bash
python ml/scripts/convert_spans_to_bio.py \
  --input data/ml_training/granular_ner/ner_dataset_all.cleaned.jsonl \
  --output data/ml_training/granular_ner/ner_bio_format.jsonl \
  --model microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext \
  --max-length 512
```

If you ran `NEG_STENT` but skipped cleaning, use:
- `--input data/ml_training/granular_ner/ner_dataset_all.neg_stent.jsonl`

### 6) Retrain

```bash
python ml/scripts/train_registry_ner.py \
  --data data/ml_training/granular_ner/ner_bio_format.jsonl \
  --output-dir artifacts/registry_biomedbert_ner \
  --epochs 20 \
  --lr 2e-5 \
  --train-batch 16 \
  --eval-batch 16
```

## Diamond Loop: Span-Level Attribute Workflow

Use this when you want a focused annotation pass for granular attribute spans
(stent type/size, lesion size, obstruction pre/post values).

### 1) Bootstrap high-precision silver spans

```bash
python ml/scripts/bootstrap_granular_attributes.py \
  --in data/ml_training/granular_ner/ner_dataset_all.jsonl \
  --out data/ml_training/granular_ner/silver_attributes.jsonl
```

Output records are Prodigy-friendly:
- `text`
- `spans` (`start`, `end`, `label`, `text`)
- `meta` (`note_id`, `source` when present)

### 2) Annotate in Prodigy

```bash
prodigy ner.manual granular_attrs_v1 blank:en \
  data/ml_training/granular_ner/silver_attributes.jsonl \
  --label DEV_STENT_TYPE,DEV_STENT_DIM,NODULE_SIZE,OBS_VAL_PRE,OBS_VAL_POST
```

### 3) Export reviewed annotations

```bash
python -m prodigy db-out granular_attrs_v1 > data/ml_training/granular_ner/gold_attributes.jsonl
```

### 4) Merge reviewed spans into training dataset

```bash
python ml/scripts/merge_granular_attribute_spans.py \
  --prodigy-input data/ml_training/granular_ner/gold_attributes.jsonl \
  --base-input data/ml_training/granular_ner/ner_dataset_all.jsonl \
  --output data/ml_training/granular_ner/ner_dataset_all.plus_attrs.jsonl
```

This converts Prodigy span format to training `entities` and deduplicates
merged output by `id` then `note_id`.

### 5) Validate alignment on merged dataset

```bash
python ml/scripts/validate_ner_alignment.py data/ml_training/granular_ner/ner_dataset_all.plus_attrs.jsonl
```

### 6) Convert to BIO and train

```bash
python ml/scripts/convert_spans_to_bio.py \
  --input data/ml_training/granular_ner/ner_dataset_all.plus_attrs.jsonl \
  --output data/ml_training/granular_ner/ner_bio_format.plus_attrs.jsonl
```

```bash
python ml/scripts/train_registry_ner.py \
  --data data/ml_training/granular_ner/ner_bio_format.plus_attrs.jsonl \
  --output-dir artifacts/registry_biomedbert_ner_vX
```

## “Clean rebuild” workflow (you want to regenerate from scratch)

Use this when you suspect the dataset drifted due to many re-runs.

1) Move the current artifacts out of the way (or rely on the dedupe backup mechanism).
2) Re-run all update scripts:
   ```bash
   python ops/tools/run_python_update_scripts.py --pattern '*.py'
   ```
3) Run the same post-steps as incremental:
   - `python ml/scripts/dedupe_granular_ner.py --write`
   - `python ml/scripts/validate_ner_alignment.py ...`
   - `python ml/scripts/regenerate_granular_ner_stats.py --write`
   - `python ml/scripts/convert_spans_to_bio.py ...`

## Fixing alignment / schema issues (when validation fails)

If `validate_ner_alignment.py` reports issues, use the alignment fixer to produce a corrected JSONL:

```bash
python ml/scripts/fix_alignment.py \
  --input-jsonl data/ml_training/granular_ner/ner_dataset_all.jsonl \
  --use-update-scripts-text \
  --update-scripts-dir 'data/granular annotations/Python_update_scripts' \
  --fix-whitespace-mismatch \
  --threshold 200 \
  --report reports/fix_alignment_report.json
```

This writes `data/ml_training/granular_ner/ner_dataset_all.fixed.jsonl` by default.

If the fixed file looks good, replace the primary file and regenerate:
- Move `ner_dataset_all.fixed.jsonl` into place as `ner_dataset_all.jsonl`
- Re-run:
  - `python ml/scripts/validate_ner_alignment.py ...`
  - `python ml/scripts/regenerate_granular_ner_stats.py --write`
  - `python ml/scripts/convert_spans_to_bio.py ...`

## Common problems and what to do

### Update script fails: `ModuleNotFoundError: No module named 'scripts'`
- Your new update script should use `from ml.scripts.add_training_case import add_case`.
- If it still fails, run it via the runner from repo root (the runner uses `cwd=repo_root`):
  - `python ops/tools/run_python_update_scripts.py --pattern '<your_script>.py'`

### Update script fails: `ValueError: Term '...' not found in text`
- Fix the term/occurrence in that script so `get_span()` finds the text.
- If the note text changed, update the note text in the script to match what you intend to train on.

### Stats show `alignment_errors > 0`
- First run: `python ml/scripts/validate_ner_alignment.py data/ml_training/granular_ner/ner_dataset_all.jsonl`
- Then fix:
  - adjust the update script(s), or
  - run `ml/scripts/fix_alignment.py` (see above) and regenerate stats.

### Stats show `duplicate_note_ids > 0`
- Run: `python ml/scripts/dedupe_granular_ner.py --write`
