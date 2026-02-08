# Reporter Gold Workflow

This workflow builds a pilot reporter-gold dataset from synthetic short notes (`*_syn_*`) and evaluates reporter regressions against that dataset.

## Scope

- Input unit: one `_syn_*` note variant
- Pilot size: 200 notes (default)
- Source-of-truth anchor: canonical base note in the same patient JSON file
- Output format: versioned JSONL artifacts in `data/ml_training/reporter_golden/v1/`

## Prerequisites

Set OpenAI-compatible provider env before running generation:

```bash
export LLM_PROVIDER=openai_compat
export OPENAI_API_KEY=...
export OPENAI_MODEL=...
# Optional:
export OPENAI_MODEL_STRUCTURER=...
export OPENAI_MODEL_JUDGE=...
```

## Commands

### 1) Generate pilot dataset

```bash
make reporter-gold-generate-pilot \
  REPORTER_GOLD_INPUT_DIR=/Users/russellmiller/Projects/proc_suite_notes/data/knowledge/patient_note_texts \
  REPORTER_GOLD_OUTPUT_DIR=data/ml_training/reporter_golden/v1 \
  REPORTER_GOLD_SAMPLE_SIZE=200 \
  REPORTER_GOLD_SEED=42
```

Generation writes:

- `reporter_gold_candidates.jsonl`
- `reporter_gold_accepted.jsonl`
- `reporter_gold_rejected.jsonl`
- `reporter_gold_metrics.json`
- `reporter_gold_review_queue.jsonl`
- `reporter_gold_review_queue.csv`
- `reporter_gold_skipped_manifest.jsonl`

### 2) Split accepted data (patient-level no leakage)

```bash
make reporter-gold-split \
  REPORTER_GOLD_OUTPUT_DIR=data/ml_training/reporter_golden/v1 \
  REPORTER_GOLD_SEED=42
```

Split outputs:

- `reporter_gold_train.jsonl`
- `reporter_gold_val.jsonl`
- `reporter_gold_test.jsonl`
- `reporter_gold_split_manifest.json`

### 3) Evaluate current reporter against reporter-gold

```bash
make reporter-gold-eval \
  REPORTER_GOLD_EVAL_INPUT=data/ml_training/reporter_golden/v1/reporter_gold_test.jsonl \
  REPORTER_GOLD_OUTPUT_DIR=data/ml_training/reporter_golden/v1
```

Evaluator output:

- `reporter_gold_eval_report.json`

### 4) Full pilot flow

```bash
make reporter-gold-pilot \
  REPORTER_GOLD_INPUT_DIR=/Users/russellmiller/Projects/proc_suite_notes/data/knowledge/patient_note_texts \
  REPORTER_GOLD_OUTPUT_DIR=data/ml_training/reporter_golden/v1
```

## Quality Gates Applied in Generation

- Required section headers present in generated report.
- No forbidden artifacts (`{{`, `}}`, `None`, `TODO`).
- Placeholder policy restricted to canonical bracket placeholders.
- Extraction-first comparison across input, anchor, generated:
  - performed flags
  - CPT overlap metrics
  - hard fail on critical introduced performed flags not present in input-anchor union.
- Judge thresholds:
  - factuality >= 0.85
  - style >= 0.85
  - completeness >= 0.80
  - no critical hallucination

## Notes

- Existing seed fixture `tests/fixtures/reporter_golden_dataset.json` remains unchanged.
- Manual review queue includes:
  - all rejected cases
  - plus 10% sampled accepted cases.
