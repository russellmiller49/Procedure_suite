# Self-Improvement & Evaluation Scripts (User Guide)

This repo is moving to a **stateless, extraction-first** service model:
**Text In → Registry + Codes Out** (authoritative endpoint: `POST /api/v1/process`).

This guide is a practical “how to run it” reference for the **self-improvement** and
**evaluation** scripts used to debug extraction, measure regressions, and iterate safely.

---

## Safety & Operating Modes (read first)

### PHI / Zero-knowledge expectations

- Treat anything you run with **real LLM calls** as potentially sending text off-machine.
- Prefer using **scrubbed text** (from the UI PHI redactor) or **repo fixtures**
  (`tests/fixtures/...`) when evaluating.
- Many scripts are **offline by default** (stub LLMs), but some have explicit “go online”
  switches. Read each script’s section.

### Required runtime invariants (scripts should match production direction)

At runtime, the system expects:

- `PROCSUITE_PIPELINE_MODE=extraction_first`
- Production additionally requires `REGISTRY_EXTRACTION_ENGINE=parallel_ner`,
  `REGISTRY_SCHEMA_VERSION=v3`, `REGISTRY_AUDITOR_SOURCE=raw_ml`

CLI scripts usually set conservative defaults, but you can always hard-set:

```bash
export PROCSUITE_PIPELINE_MODE=extraction_first
export REGISTRY_EXTRACTION_ENGINE=parallel_ner
export REGISTRY_SCHEMA_VERSION=v3
```

### `.env` loading

`.env` is loaded automatically unless `PROCSUITE_SKIP_DOTENV=1`.
Scripts that must avoid accidental API-key usage often force `PROCSUITE_SKIP_DOTENV=1`.

---

## Quickstart (recommended loop)

1. **Start with fixtures (no PHI):**
   - `tests/fixtures/notes/*.txt` (smoke tests)
   - `data/ml_training/reporter_prompt/v1/*.jsonl` (reporter eval)
2. **Run a single-note smoke test** to see flags + warnings.
3. **Run the batch smoke test** to catch regressions across many notes.
4. If a regression is real, iterate via:
   - deterministic extractor/rules changes, then re-smoke
   - keyword guard updates if you see `SILENT_FAILURE:` misses
   - self-correction diagnostics only after the deterministic path is stable

---

## Registry extraction evaluation

### 1) Single-note smoke test: `ops/tools/registry_pipeline_smoke.py`

**What it does**

- Runs `RegistryService.extract_record()` and prints “performed” flags.
- Runs deterministic extractors on **masked** text and performs an “uplift” merge to show
  what deterministic backstops would add.
- Runs omission scanning (`scan_for_omissions`) to surface `SILENT_FAILURE:` warnings.
- Optional: runs `RegistryService.extract_fields()` with self-correction enabled to show
  why self-correction did/didn’t apply.

**Typical usage**

```bash
# Run on a fixture note
python ops/tools/registry_pipeline_smoke.py --note tests/fixtures/notes/note_274.txt

# Inline text
python ops/tools/registry_pipeline_smoke.py --text "PROCEDURE IN DETAIL: ..."
```

**Self-correction diagnostics (use with care)**

```bash
# Enables the self-correction path (still offline unless you also allow real LLM calls)
python ops/tools/registry_pipeline_smoke.py --note tests/fixtures/notes/note_274.txt --self-correct

# Allow real network LLM calls (disables stub/offline defaults used by the script)
python ops/tools/registry_pipeline_smoke.py --note tests/fixtures/notes/note_274.txt --self-correct --real-llm
```

**How to read output**

- **Performed flags (extract_record)**: what the primary extraction produced.
- **Performed flags added by deterministic uplift**: what deterministic backstops found.
- **Omission warnings**: high-value missed-procedure warnings from the keyword guard.
- **Self-correction diagnostics**: only appears with `--self-correct`; includes audit omissions
  + any `SELF_CORRECT_*` / `AUTO_CORRECTED_*` warnings.

---

### 2) Batch smoke test: `ops/tools/registry_pipeline_smoke_batch.py`

**What it does**

- Randomly samples notes from a directory and runs the same smoke-test logic per note.
- Writes a single output file with per-note blocks + a summary.

**Supported note formats in `--notes-dir`**

- `*.txt`: one note per file
- `*.json`: a dict of `note_key -> note_text` (the script picks the first key that does not
  contain `"_syn_"`)

**Example (fixtures)**

```bash
python ops/tools/registry_pipeline_smoke_batch.py \
  --count 10 \
  --notes-dir tests/fixtures/notes \
  --seed 42 \
  --output reports/registry_smoke_batch_fixture.txt
```

**With self-correction diagnostics**

```bash
python ops/tools/registry_pipeline_smoke_batch.py \
  --count 10 \
  --notes-dir tests/fixtures/notes \
  --self-correct \
  --real-llm \
  --output reports/registry_smoke_batch_self_correct.txt
```

**Exit codes**

- `0` if all selected notes succeed
- `1` if any note fails

---

### 3) End-to-end unified pipeline batch: `ops/tools/unified_pipeline_batch.py`

**What it does**

- Runs the same logical steps as the unified UI/API pipeline:
  - PHI redaction (via `apply_phi_redaction`)
  - `RegistryService.extract_fields(...)`
  - deterministic registry→CPT derivation (`derive_all_codes_with_meta`)
  - V3 evidence payload building (`build_v3_evidence_payload`)
  - wraps output as a `UnifiedProcessResponse`

**When to use**

- You want a “close to `/api/v1/process`” batch sanity-check without running the server.

**Example**

```bash
python ops/tools/unified_pipeline_batch.py \
  --count 5 \
  --notes-dir tests/fixtures/notes \
  --seed 7 \
  --output reports/unified_pipeline_batch_fixture.txt
```

Notes:
- The script expects `--notes-dir` to contain `*.txt` notes.
- The output file includes **the full note text** for each case; do not run on unredacted PHI
  unless your output location is handled appropriately.
- Use `--no-financials` / `--no-explain` to speed up large runs.
- Use `--real-llm` only when your input text is scrubbed and you intend to allow network calls.

---

## Self-improvement utilities (registry)

### 4) Field prompt improvement helper: `ops/tools/self_correct_registry.py`

**What it does**

- Looks up **allowed enum values** for a registry field from the JSON schema (via
  `KnowledgeSettings().registry_schema_path`).
- Loads recent extraction errors for that field from `data/registry_errors.jsonl`.
- Sends a compact “current instruction + errors” prompt to an LLM to propose:
  - updated instruction text
  - Python post-processing mapping rules
  - comments
- Writes a report: `reports/registry_self_correction_<field>.md`

**Prerequisite**

You must first create `data/registry_errors.jsonl` with rows like:

```json
{"field_name":"sedation_type","gold_value":"Moderate","predicted_value":"General","note_text":"..."}
```

**Example**

```bash
python ops/tools/self_correct_registry.py --field sedation_type --max-examples 20
```

**Model selection**

```bash
python ops/tools/self_correct_registry.py --field sedation_type --model gpt-5-mini
```

This sets `REGISTRY_SELF_CORRECTION_MODEL` for the run.

---

### 5) “Immediate logic fix” helper: `ops/tools/apply_immediate_logic_fixes.py`

**What it does**

- Applies the production checkbox-negation hardening
  (`app.registry.postprocess.template_checkbox_negation.apply_template_checkbox_negation`)
  to an existing record JSON, given the source note text.

**When to use**

- You have a record JSON where template checkbox artifacts caused false positives and you
  want a quick postprocess patch for debugging.

**Example**

```bash
python ops/tools/apply_immediate_logic_fixes.py \
  --note tests/fixtures/notes/note_274.txt \
  --record /path/to/record.json > /tmp/record_patched.json
```

---

### 6) Blank per-patient update scripts: `ops/tools/create_blank_update_scripts_from_patient_note_texts.py`

**What it does**

- For each `*.json` file in an input directory, writes a matching blank `*.py` “update script”
  into an output directory (one-per-patient/work-item).

**Example**

```bash
python ops/tools/create_blank_update_scripts_from_patient_note_texts.py \
  --input-dir /path/to/patient_note_texts \
  --output-dir "data/granular annotations/Python_update_scripts"
```

Use `--dry-run` to preview and `--overwrite` to regenerate.

---

### 7) Run update scripts: `ops/tools/run_python_update_scripts.py`

**What it does**

- Executes `note_*.py` (configurable) scripts from:
  `data/granular annotations/Python_update_scripts`
- Captures stdout/stderr per script and writes a structured failure report when any fail:
  `reports/python_update_scripts_failures.json`

**Example**

```bash
python ops/tools/run_python_update_scripts.py --pattern "note_*.py"
```

Use `--fail-fast` when debugging a single broken update script.

---

## Reporter evaluation & improvement

### 8) Random-seed reporter runs: `ops/tools/run_reporter_random_seeds.py`

**What it does**

- Reservoir-samples prompt rows from `*.jsonl` files in a directory.
- Runs extraction-first registry seeding + reporter rendering.
- Writes a human-readable transcript (`.txt`) and optional JSON metadata (`.json`).
  Both include the sampled prompt text; keep outputs PHI-safe.

**Example (repo dataset)**

```bash
python ops/tools/run_reporter_random_seeds.py \
  --input-dir data/ml_training/reporter_prompt/v1 \
  --count 20 \
  --output reports/reporter_random_seed_run.txt \
  --include-metadata-json
```

Tip: use `--prompt-field prompt_text` if your dataset uses `prompt_text` instead of `prompt`.

---

### 9) Reporter baseline eval: `ops/tools/eval_reporter_prompt_baseline.py`

**What it does**

- Evaluates two baselines on `data/ml_training/reporter_prompt/v1/reporter_prompt_test.jsonl`:
  - `compose_report_from_text` (dictation-ish baseline)
  - structured baseline using `ReportingStrategy` seeded by extraction-first registry fields
- Scores:
  - text similarity vs `completion_canonical`
  - required section coverage
  - CPT Jaccard similarity (gold vs generated, via running the registry pipeline)
  - performed-flag F1 (gold vs generated)
  - “critical extra flag” rate (high-risk false positives)

**Example**

```bash
python ops/tools/eval_reporter_prompt_baseline.py --max-cases 200 --output reports/reporter_baseline_eval.json
```

Offline behavior:
- Unless `PROCSUITE_ALLOW_ONLINE=1`, the script forces stub/offline settings and disables
  any reporter LLM usage.

---

### 10) Findings-seeded reporter eval (online only): `ops/tools/eval_reporter_prompt_llm_findings.py`

**What it does**

- Runs the “structured-first” reporter POC:
  masked prompt → LLM findings (with evidence) → synthetic NER → registry flags → CPT → report
- Produces a JSON report with promotion gates.

**Online guard**

This script refuses to run unless `PROCSUITE_ALLOW_ONLINE=1` is set.

**Example**

```bash
export PROCSUITE_ALLOW_ONLINE=1
export LLM_PROVIDER=openai_compat
export OPENAI_API_KEY=...
export OPENAI_MODEL_STRUCTURER=gpt-5-mini

python ops/tools/eval_reporter_prompt_llm_findings.py --max-cases 50
```

---

### 11) Prompt→bundle model eval: `ops/tools/eval_reporter_prompt_model.py`

**What it does**

- Loads a local HuggingFace model directory (or PEFT adapter) that generates a `ProcedureBundle`
  JSON from a prompt.
- Parses/validates the bundle, renders a report, then scores it similarly to other reporter evals.

**Example**

```bash
python ops/tools/eval_reporter_prompt_model.py \
  --model-dir artifacts/reporter_prompt_bundle_v1 \
  --max-cases 100 \
  --output reports/reporter_prompt_model_eval.json
```

Notes:
- Requires `torch` + `transformers` (and optionally `peft` + bitsandbytes for adapters).
- This script forces offline/stub settings unless `PROCSUITE_ALLOW_ONLINE=1`.

---

### 12) Reporter gold dataset eval: `ops/tools/eval_reporter_gold_dataset.py`

**What it does**

- Evaluates reporter rendering quality against a gold JSONL file
  (default: `data/ml_training/reporter_golden/v1/reporter_gold_accepted.jsonl`).
- Outputs a JSON report (default: `data/ml_training/reporter_golden/v1/reporter_gold_eval_report.json`).

**Example**

```bash
python ops/tools/eval_reporter_gold_dataset.py --max-cases 50 --output reports/reporter_gold_eval.json
```

---

## Schema-compatibility notes (what “current” means)

The repo recently refactored schema modules. When touching scripts:

- Prefer `from app.registry.schema import RegistryRecord` for the dynamic registry model.
- Prefer `from app.registry.schema.ip_v3_extraction import ...` for V3 extraction/event-log types.
- Avoid legacy import shims unless you explicitly need backwards-compat behavior.

The UI evidence contract is V3-shaped:
`{"source": "...", "text": "...", "span": [start, end], "confidence": 0.0-1.0}`
(see `app/api/adapters/response_adapter.py:build_v3_evidence_payload()`).

---

## Troubleshooting

- **Script tries to use a real API key unexpectedly**
  - Set `PROCSUITE_SKIP_DOTENV=1` and `OPENAI_OFFLINE=1` / `GEMINI_OFFLINE=1`
  - Ensure `REGISTRY_USE_STUB_LLM=1` and `REPORTER_DISABLE_LLM=1`
- **Self-correction does nothing**
  - Check `--self-correct` output for `SELF_CORRECT_SKIPPED` warnings and omission-scan output.
  - Self-correction is gated by RAW-ML audit findings + keyword guard.
- **Missing datasets**
  - Many scripts default to paths that are often untracked locally. Use `--notes-dir` / `--input`
    to point at your local datasets, or use `tests/fixtures/...` to sanity-check behavior.
