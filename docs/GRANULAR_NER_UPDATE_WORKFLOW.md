# Granular NER: Updating Training Data from `Python_update_scripts/`

This repo uses generated Python scripts in `data/granular annotations/Python_update_scripts/` to append new annotated notes into the granular NER training artifacts under `data/ml_training/granular_ner/`.

Key facts:
- Update scripts typically call `from scripts.add_training_case import add_case` and then `add_case(id, text, entities, REPO_ROOT)`.
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
python scripts/run_python_update_scripts.py --pattern '*.py' --failure-report reports/python_update_scripts_failures.json
```

If it reports failures, open `reports/python_update_scripts_failures.json` and fix the corresponding update scripts (most failures are `get_span()` text mismatches or import path issues).

Tips for fixing update scripts:
- If you use `**get_span(...)`, make sure `get_span()` never returns `None` for a required entity. Prefer raising a clear `ValueError` when a term isn’t found.
- Ensure the searched term matches the note text exactly (case/spacing/punctuation) and that `occurrence=N` is correct.

### 2) Dedupe duplicates created by re-runs (safe; makes backups)

Because update scripts append, re-running scripts can create duplicate IDs. Deduping is the safest “cleanup” step:

```bash
python scripts/dedupe_granular_ner.py --base-dir data/ml_training/granular_ner --write
```

Notes:
- This creates a timestamped backup folder under `data/ml_training/granular_ner/_backup_*/` first.
- Default strategy keeps the record with the most entities for a given note id (ties broken by longer text, then latest).

### 3) Validate span alignment

```bash
python scripts/validate_ner_alignment.py data/ml_training/granular_ner/ner_dataset_all.jsonl
```

This checks that each span’s offsets are in-bounds and (when a span text field exists) that it matches the text slice.

### 4) Regenerate `stats.json`

```bash
python scripts/regenerate_granular_ner_stats.py --base-dir data/ml_training/granular_ner --write
```

This recomputes alignment counts + label counts from `ner_dataset_all.jsonl` (the real training file).

### 5) Rebuild BIO format

```bash
python scripts/convert_spans_to_bio.py \
  --input data/ml_training/granular_ner/ner_dataset_all.jsonl \
  --output data/ml_training/granular_ner/ner_bio_format.jsonl \
  --model microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext \
  --max-length 512
```
###6) Retrain:
python scripts/train_registry_ner.py \
  --data data/ml_training/granular_ner/ner_bio_format_refined.jsonl \
  --output-dir artifacts/registry_biomedbert_ner_v2 \
  --epochs 20 \
  --lr 2e-5 \
  --train-batch 16 \
  --eval-batch 16

## “Clean rebuild” workflow (you want to regenerate from scratch)

Use this when you suspect the dataset drifted due to many re-runs.

1) Move the current artifacts out of the way (or rely on the dedupe backup mechanism).
2) Re-run all update scripts:
   ```bash
   python scripts/run_python_update_scripts.py --pattern '*.py'
   ```
3) Run the same post-steps as incremental:
   - `python scripts/dedupe_granular_ner.py --write`
   - `python scripts/validate_ner_alignment.py ...`
   - `python scripts/regenerate_granular_ner_stats.py --write`
   - `python scripts/convert_spans_to_bio.py ...`

## Fixing alignment / schema issues (when validation fails)

If `validate_ner_alignment.py` reports issues, use the alignment fixer to produce a corrected JSONL:

```bash
python scripts/fix_alignment.py \
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
  - `python scripts/validate_ner_alignment.py ...`
  - `python scripts/regenerate_granular_ner_stats.py --write`
  - `python scripts/convert_spans_to_bio.py ...`

## Common problems and what to do

### Update script fails: `ModuleNotFoundError: No module named 'scripts'`
- Your new update script should still use `from scripts.add_training_case import add_case`.
- If it still fails, run it via the runner from repo root (the runner uses `cwd=repo_root`):
  - `python scripts/run_python_update_scripts.py --pattern '<your_script>.py'`

### Update script fails: `ValueError: Term '...' not found in text`
- Fix the term/occurrence in that script so `get_span()` finds the text.
- If the note text changed, update the note text in the script to match what you intend to train on.

### Stats show `alignment_errors > 0`
- First run: `python scripts/validate_ner_alignment.py data/ml_training/granular_ner/ner_dataset_all.jsonl`
- Then fix:
  - adjust the update script(s), or
  - run `scripts/fix_alignment.py` (see above) and regenerate stats.

### Stats show `duplicate_note_ids > 0`
- Run: `python scripts/dedupe_granular_ner.py --write`
