Run Guide

Registry validation

make validate-registry
Reads data/synthetic_notes_with_registry.jsonl, skips evidence, logs mismatches to data/registry_errors.jsonl, prints per-field accuracy.
Registry error summary

make analyze-registry-errors
Summarizes data/registry_errors.jsonl and writes reports/registry_error_summary.json.
Registry self-correction proposals

Default (uses REGISTRY_SELF_CORRECTION_MODEL, falls back to gpt-5.1):
make self-correct-registry FIELD=sedation_type
Override model for a run:
python scripts/self_correct_registry.py --field sedation_type --model gpt-5.1
Outputs console summary + reports/registry_self_correction_<field>.md with suggested prompt/rules (human applies).
CPT data prep

python scripts/prepare_data.py
Cleans raw CSV into data/cpt_training_data_cleaned.csv.
CPT training

python scripts/train_cpt.py
Trains and saves data/models/cpt_classifier.pkl + mlb.pkl.
CPT evaluation + error log

python scripts/evaluate_cpt.py
Evaluates on synthetic CSV; exact-match accuracy printed; mismatches to data/cpt_errors.jsonl.
CPT self-correction ideas

(After evaluate_cpt.py) use modules/ml_coder/self_correction.py functions to group data/cpt_errors.jsonl and call LLM for rule/keyword suggestions (no auto-edit).
Env to set

Gemini extraction: GEMINI_API_KEY, optional GEMINI_MODEL.
Self-correction preferred model: REGISTRY_SELF_CORRECTION_MODEL=gpt-5.1 (and OPENAI_API_KEY).
Per-run override via --model flag.


REGISTRY_SELF_CORRECTION_MODEL=gpt-5.1 python scripts/self_correct_registry.py --field sedation_type

## Testing

### Targeted EBUS Testing
Run tests specifically for EBUS extraction logic and new fields:
```bash
pytest -m ebus
```
This runs the suite defined in `tests/registry/test_registry_extraction_ebus.py` against the synthetic dataset.

## Registry Schema Updates (v0.5.0)

New fields added to `IP_Registry.json`:
- `sedation_reversal_given` (boolean)
- `sedation_reversal_agent` (string)
- `ebus_photodocumentation_complete` (boolean)

These are extracted via heuristics in `modules/registry/engine.py`.

uvicorn modules.api.fastapi_app:app --reload
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest -q
if you want to avoid API tests for now, you can run everything else with:
REGISTRY_USE_STUB_LLM=1 GEMINI_OFFLINE=1 DISABLE_STATIC_FILES=1 pytest tests/unit tests/registry tests/e2e -q


Railway deploy: conda activate medparse-py311
./scripts/railway_start.sh