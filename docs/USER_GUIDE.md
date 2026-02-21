# Procedure Suite - User Guide

This guide explains how to use the Procedure Suite tools for generating reports, coding procedures, and validating registry data.

---

## Important: Current Production Mode (2026-01)

- The server is a **stateless logic engine**: **(scrubbed) note text in → registry + CPT codes out**.
- **Primary endpoint:** `POST /api/v1/process`
- Startup enforces `PROCSUITE_PIPELINE_MODE=extraction_first` (service will not start otherwise).
- In production (`CODER_REQUIRE_PHI_REVIEW=true`), `/api/v1/process` stays enabled and returns:
  - `review_status="pending_phi_review"`
  - `needs_manual_review=true`
- Optional: `REGISTRY_SELF_CORRECT_ENABLED=1` allows an external LLM to act as a **judge** on **scrubbed text** to patch missing fields
  when high-confidence omissions are detected (slower but higher quality).
  - Self-correction is gated by a CPT keyword guard; skips will include `SELF_CORRECT_SKIPPED:` warnings when enabled.

## Dependency Reproducibility (2026-02)

- Runtime dependency inputs are tracked in `requirements.in`.
- The pinned lockfile is `requirements.txt` (generated with pip-tools).
- Use:
  - `make deps-compile` to regenerate `requirements.txt`
  - `make deps-check` to verify sync (CI enforces this check)
- The lock is compiled against CPython 3.11 + `manylinux2014_x86_64` for reproducible CI/prod resolution.
- `scikit-learn` is intentionally constrained for model compatibility (`1.5.x` line).

## Recent Updates (2026-01-24)

- **BLVR CPT derivation:** valve placement uses `31647` (initial lobe) + `31651` (each additional lobe); valve removal uses `31648` (initial lobe) + `31649` (each additional lobe).
- **Chartis bundling:** `31634` is derived only when Chartis is documented; suppressed when Chartis is in the same lobe as valve placement, and flagged for modifier documentation when distinct lobes are present.
- **Moderate sedation threshold:** `99152`/`99153` are derived only when `sedation.type="Moderate"`, `anesthesia_provider="Proceduralist"`, and intraservice minutes ≥10 (computed from start/end if needed).
- **Coding support + traceability:** extraction-first now populates `registry.coding_support` (rules applied + QA flags) and enriches `registry.billing.cpt_codes[]` with `description`, `derived_from`, and evidence spans.
- **Providers normalization:** added `providers_team[]` (auto-derived from legacy `providers` when missing).
- **Registry schema:** added `pathology_results.pdl1_tps_text` to preserve values like `"<1%"` or `">50%"`.
- **KB hygiene (Phase 0–2):** added `docs/KNOWLEDGE_INVENTORY.md`, `docs/KNOWLEDGE_RELEASE_CHECKLIST.md`, and `make validate-knowledge-release` for safer knowledge/schema updates.
- **KB version gating:** loaders now enforce KB filename semantic version ↔ internal `"version"` (override: `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`).
- **Single source of truth:** runtime code metadata/RVUs come from `master_code_index`, and synonym phrase lists are centralized in KB `synonyms`.

## How the System Works (Plain Language)

The Procedure Suite is an intelligent medical coding assistant that reads procedure notes and suggests appropriate CPT billing codes. Here's how it works in simple terms:

### The Three Brains

1. **Granular NER**: A trained model that finds procedure actions/devices (e.g., BAL, EBUS stations, cryotherapy) as text spans to drive structured extraction.

2. **Rules Engine**: A set of explicit business rules that encode medical billing knowledge, such as:
   - "You can't bill these two codes together" (bundling rules)
   - "This code requires specific documentation" (validation rules)
   - "If procedure X was done, code Y is required" (inference rules)

3. **ML Auditor + Guardrails**: A safety net that flags likely omissions/mismatches and forces review when extraction degrades. Optional LLM components are used for advisor/self-correction when enabled.

### Extraction-First Pipeline (Current)

Recommended runtime configuration uses the `parallel_ner` extraction engine:

```
(Scrubbed) Note Text
  → [Path A] Granular NER → Registry mapping → Deterministic Registry→CPT rules
  → [Path B] Optional ML classifier/auditor (may be unavailable)
  → Guardrails + omission scan (surface warnings, require review when needed)
```

Key behaviors:
- **Deterministic uplift** prevents “silent revenue loss” when NER misses common procedures (BAL/EBBx/radial EBUS/cryotherapy, plus backstops like navigational bronchoscopy and pleural IPC/tunneled catheter).
- `audit_warnings` surfaces `SILENT_FAILURE:` and other degraded-mode warnings to the UI.
- **Context guardrails (anti-hallucination)** reduce over-coding from “keyword only” matches:
  - **Stents**: inspection-only phrases like “stent … in good position” clear `airway_stent.performed` (prevents CPT `31636`).
  - **Chest tubes**: discontinue/removal phrases like “D/c chest tube” do not set `pleural_procedures.chest_tube.performed` (prevents CPT `32551`).
  - **TBNA**: EBUS-TBNA does not set `tbna_conventional` (prevents double-coding `31629` alongside `31652/31653`).
  - **Radial EBUS**: explicit “radial probe” language sets `radial_ebus.performed` even without “concentric/eccentric” markers.
- **Noise masking** strips CPT menu blocks (e.g., `IP ... CODE MOD DETAILS`) before extraction to prevent “menu reading” hallucinations (laser/APC/etc).
- **Self-correction (LLM judge)**: when `REGISTRY_SELF_CORRECT_ENABLED=1`, RAW-ML high-confidence omissions can trigger a small number of
  evidence-gated patches (verbatim quote required). This is designed to fix “empty/under-coded” cases without making the LLM the primary extractor.

### Legacy: ML-First Hybrid Pipeline

Older “hybrid-first” workflows may still exist behind feature flags, but production is moving to extraction-first stateless processing via `/api/v1/process`.

```
Note Text → ML Predicts → Classify Difficulty → Decision Gate → Final Codes
                              ↓
            HIGH_CONF: ML + Rules (fast path, no LLM)
            GRAY_ZONE: LLM as judge (ML provides hints)
            LOW_CONF:  LLM as primary coder
```

**Step-by-step:**

1. **ML Prediction**: The ML model reads the note and predicts CPT codes with confidence scores.

2. **Difficulty Classification**: Based on confidence scores, the case is classified:
   - **HIGH_CONF** (High Confidence): ML is very sure about the codes
   - **GRAY_ZONE**: ML sees multiple possibilities, needs help
   - **LOW_CONF** (Low Confidence): ML is unsure, note may be unusual

3. **Decision Gate**:
   - If HIGH_CONF and rules pass → Use ML codes directly (fast, cheap, no LLM call)
   - If GRAY_ZONE or rules fail → Ask LLM to make the final decision
   - If LOW_CONF → Let LLM be the primary coder

4. **Rules Validation**: Final codes always pass through rules engine for safety checks

This approach is **faster** (43% of cases skip LLM entirely) and **more accurate** (ML catches patterns, LLM handles edge cases).

---

## 🚀 Quick Start: The Dev Server

The easiest way to interact with the system is the development server, which provides a web UI and API documentation.

```bash
./ops/devserver.sh
```
*Starts the server on port 8000.*

- **Web UI**: [http://localhost:8000/ui/](http://localhost:8000/ui/)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

Notes:
- The devserver sources `.env`. If you change `.env`, restart the devserver.
- Keep secrets (e.g., `OPENAI_API_KEY`) out of version control; prefer shell env vars or an untracked local `.env`.
- To use the current granular NER model, set `GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner` (in `.env` or your shell).
  Example (shell): `export GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner`
  Example (`.env`): `GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner`
- For faster responses (disable self-correction LLM calls), run with `PROCSUITE_FAST_MODE=1`.
---

## 🛠 CLI Tools

The suite includes several command-line scripts for batch processing and validation.

### 1. Validate Registry Extraction
Run the extraction pipeline on synthetic notes and compare against ground truth.

```bash
make validate-registry
```
*Output*: `reports/registry_validation_output.txt` and `data/registry_errors.jsonl`

### 2. Evaluate CPT Coder
Test the CPT coding engine against the training dataset.

```bash
python ml/scripts/evaluate_cpt.py
```
*Output*: Accuracy metrics and error logs in `data/cpt_errors.jsonl`.

### 3. Self-Correction (LLM)
Ask the LLM to analyze specific registry fields or errors and suggest improvements.

```bash
# Analyze errors for a specific field
make self-correct-registry FIELD=sedation_type
```
*Output*: `reports/registry_self_correction_sedation_type.md`

### 3b. Smoke Test (Registry Extraction + Self-Correction Diagnostics)

Use these scripts to quickly sanity-check extraction behavior and see why self-correction did or did not apply.

#### Single Note Smoke Test

Test a single note file:

```bash
# Basic usage
python ops/tools/registry_pipeline_smoke.py --note <note.txt>

# With self-correction enabled
python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct

# With real LLM calls enabled (OpenAI)
python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct --real-llm

# With inline text (no file needed)
python ops/tools/registry_pipeline_smoke.py --text "Procedure: EBUS bronchoscopy..."
```

**Output shows:**
- Performed flags from `extract_record()`
- Flags added by deterministic uplift
- Extract warnings
- Omission warnings
- Self-correction diagnostics (if `--self-correct` flag is used)

#### Batch Smoke Test

Test multiple random notes from a directory:

```bash
# Basic usage (30 random notes, default output file)
python ops/tools/registry_pipeline_smoke_batch.py

# Custom number of notes
python ops/tools/registry_pipeline_smoke_batch.py --count 50

# Specify output file
python ops/tools/registry_pipeline_smoke_batch.py --output my_results.txt

# Use a random seed for reproducibility
python ops/tools/registry_pipeline_smoke_batch.py --seed 42

# Enable self-correction testing
python ops/tools/registry_pipeline_smoke_batch.py --self-correct

# Custom notes directory (default: data/knowledge/patient_note_texts)
python ops/tools/registry_pipeline_smoke_batch.py --notes-dir path/to/notes

python ops/tools/registry_pipeline_smoke_batch.py --output my_results.txt --self-correct --real-llm
python ops/tools/registry_pipeline_smoke_batch.py --output my_results_V2.txt --self-correct --real-llm

python ops/tools/registry_pipeline_smoke_batch.py \
  --notes-dir "data/granular annotations/Additional_notes" \
  --count 96 \
  --output my_results.txt \
  --self-correct \
  --real-llm
```

**Output file format:**
- Header with test metadata
- For each note:
  - Note ID
  - Performed flags (before/after uplift)
  - Extract warnings
  - Omission warnings
  - Self-correction diagnostics (if enabled)
- Summary with success/failure counts

**What to look for in the output:**
- `Audit high-conf omissions:` indicates RAW-ML thinks something high-value was missed (self-correct triggers are sourced from this list).
- `SELF_CORRECT_SKIPPED:` indicates self-correction was eligible but blocked (commonly keyword guard failures).
- `AUTO_CORRECTED:` indicates self-correction successfully applied a fix.
- Keyword gating is configured in `app/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.

**Note:** The batch script automatically sets `REGISTRY_USE_STUB_LLM=1` and `GEMINI_OFFLINE=1` for offline testing. To test with real LLM/self-correction, ensure `REGISTRY_SELF_CORRECT_ENABLED=1` is set in your environment and pass the `--self-correct` flag.
The single-note smoke test supports `--real-llm`, which disables stub/offline defaults for that run.

#### LLM usage + cost reporting (tokens / $)

If you want your batch runs to print **LLM token usage** and an **estimated USD cost**:

- **Enable per-call logging**: `OPENAI_LOG_USAGE_PER_CALL=1`
- **Enable end-of-run summary**: `OPENAI_LOG_USAGE_SUMMARY=1`
- **Configure pricing** (so `$` can be estimated): `OPENAI_PRICING_JSON=...`

Example (bash):

```bash
export OPENAI_PRICING_JSON='{"gpt-5-mini":{"input_per_1k":0.00025,"output_per_1k":0.00200},"gpt-5.2":{"input_per_1k":0.00175,"output_per_1k":0.01400}}'
OPENAI_LOG_USAGE_PER_CALL=1 OPENAI_LOG_USAGE_SUMMARY=1 \
python ops/tools/registry_pipeline_smoke_batch.py --output my_results.txt --self-correct --real-llm
or
export OPENAI_PRICING_JSON='{"gpt-5-mini":{"input_per_1k":0.00025,"output_per_1k":0.00200},"gpt-5.2":{"input_per_1k":0.00175,"output_per_1k":0.01400}}'
OPENAI_LOG_USAGE_PER_CALL=1 OPENAI_LOG_USAGE_SUMMARY=1 \
python ops/tools/unified_pipeline_batch.py --output my_results.txt --real-llm
```

Notes:
- `OPENAI_PRICING_JSON` must be set **once** (include multiple models in a single JSON object).
- Cost reporting currently applies to **OpenAI-compatible** calls (`LLM_PROVIDER=openai_compat`). If pricing is not configured, tokens/latency still print and cost will show as “pricing not configured”.

### 3c. Unified Pipeline Batch Test

Test the full unified pipeline (same as the UI at `/ui/`) on multiple random notes:

```bash
# Basic usage (10 random notes from notes_text directory, default output file)
python ops/tools/unified_pipeline_batch.py

# Custom number of notes
python ops/tools/unified_pipeline_batch.py --count 20

# Specify output file
python ops/tools/unified_pipeline_batch.py --output my_results.txt

# Use a random seed for reproducibility
python ops/tools/unified_pipeline_batch.py --seed 42

# Exclude financials or evidence
python ops/tools/unified_pipeline_batch.py --no-financials --no-explain

# Custom notes directory (default: data/granular annotations/notes_text)
python ops/tools/unified_pipeline_batch.py --notes-dir path/to/notes

# With real LLM calls enabled
python ops/tools/unified_pipeline_batch.py --output my_results.txt --real-llm

# Check which provider is configured
python -c "import os; print('LLM_PROVIDER:', os.getenv('LLM_PROVIDER', 'gemini (default)'))"

# Check if API keys are set (without showing values)
python -c "import os; print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'); print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"

python ops/tools/unified_pipeline_batch.py \
  --notes-dir "data/granular annotations/Additional_notes" \
  --count 20 \
  --output my_results.txt \
  --real-llm
```

**Output file format:**
- Header with test metadata
- For each note:
  - Note ID
  - Full note text
  - Complete JSON results (same format as `/api/v1/process` endpoint):
    - `registry`: Extracted registry fields
    - `evidence`: Evidence spans with confidence scores
    - `cpt_codes`: Derived CPT codes
    - `suggestions`: Code suggestions with confidence and rationale
    - `total_work_rvu`: Total work RVU
    - `estimated_payment`: Estimated payment
    - `per_code_billing`: Per-code RVU and payment breakdown
    - `audit_warnings`: Warnings and self-correction messages
    - `review_status`: Review status
    - `processing_time_ms`: Processing time
- Summary with success/failure counts

**This script:**
- Uses the same pipeline as the UI (`/api/v1/process` endpoint)
- Includes PHI redaction (same as UI)
- Processes notes from `.txt` files in the notes directory
- Automatically sets `REGISTRY_USE_STUB_LLM=1` and `GEMINI_OFFLINE=1` for offline testing
- Returns the complete unified response with registry, CPT codes, financials, and evidence

**Use cases:**
- Testing extraction quality on a random sample of notes
- Generating example outputs for documentation
- Validating pipeline behavior after code changes
- Comparing results across different configurations

### 4. Build UMLS Lite Map (IP Domain Terminology)

Extract IP-relevant UMLS terminology from a local UMLS 2025AA installation into a lightweight JSON map for runtime concept linking without the heavy scispaCy UMLS linker (~7 MB vs ~1 GB).

```bash
# Default: reads ~/UMLS/2025AA/META/, writes data/knowledge/ip_umls_map.json
python ops/tools/build_ip_umls_map.py

# Custom UMLS directory
python ops/tools/build_ip_umls_map.py --umls-dir /path/to/UMLS/META

# Include definitions and relationship expansion
python ops/tools/build_ip_umls_map.py --include-defs --expand-rels

# Verbose progress logging
python ops/tools/build_ip_umls_map.py --verbose
```

**Prerequisites:**
- UMLS 2025AA RRF files (`MRCONSO.RRF`, `MRSTY.RRF`) at `~/UMLS/2025AA/META/` (or specify `--umls-dir`)
- No additional Python dependencies required (uses stdlib only)

**Output:** `data/knowledge/ip_umls_map.json` containing ~19K concepts across anatomy, procedures, devices, diseases, and pharmacology — filtered to IP-relevant terminology via category-gated pattern matching.

**Runtime usage:** The map is consumed by `proc_nlp/umls_lite.py` which provides a drop-in lightweight alternative to `proc_nlp/umls_linker.py`:

```python
from proc_nlp.umls_lite import umls_link_lite, lookup_cui, search_terms

# Link clinical text to UMLS concepts
concepts = umls_link_lite("bronchoscopy with EBUS-TBNA")
for c in concepts:
    print(c.cui, c.preferred_name, c.score)

# Direct CUI lookup
info = lookup_cui("C0006290")  # Bronchoscopy

# Search the term index
matches = search_terms("cryobiopsy")
```

The map path is configurable via `IP_UMLS_MAP_PATH` env var (default: `data/knowledge/ip_umls_map.json`).

### 5. Clean & Normalize Registry
Run the full cleaning pipeline (Schema Norm -> CPT Logic -> Consistency -> Clinical QC) on a raw dataset.

The legacy clean-registry CLI was removed during migration.
Use the canonical cleaning modules under `app/registry_cleaning/` from your own batch job.

### 6. Generate LLM "repo context" docs (gitingest)
When you want to share repo context with an LLM, use the gitingest generator to produce:

- `gitingest.md`: a **lightweight**, curated repo snapshot (structure + a few key files)
- `gitingest_details.md`: an **optional** second document with more granular, **text-only** code/docs

```bash
# Base (light) doc only
python ops/tools/generate_gitingest.py

# Generate both base + details
python ops/tools/generate_gitingest.py --details

# Details only (no base)
python ops/tools/generate_gitingest.py --no-base --details
```

#### Details document controls
The details doc is designed to stay readable and safe for LLM ingestion:
- Skips common large/binary/unreadable files (best-effort)
- Enforces a per-file size cap
- Can avoid minified JS/TS bundles

```bash
# Include only specific folders (repeatable), cap size and inline count
python ops/tools/generate_gitingest.py --details \
  --details-include ml/scripts/ \
  --details-include ops/tools/ \
  --details-include app/registry/ \
  --details-max-bytes 200000 \
  --details-max-files 75 \
  --details-inline curated
```

---

## 🔌 API Usage

You can interact with the system programmatically via the REST API.

### Machine Extraction Endpoint (Stateless)
**POST** `/api/v1/process`

This is the production extraction engine. It expects **already scrubbed** text and
returns structured registry data plus derived CPT codes. When
`CODER_REQUIRE_PHI_REVIEW=true`, the response includes
`review_status="pending_phi_review"` and `needs_manual_review=true`.

If `REGISTRY_SELF_CORRECT_ENABLED=1`, the server may call an external LLM on **scrubbed text**
as a judge to propose and apply small JSON patches when high-confidence omissions are detected.

Evidence is returned in a UI-friendly V3 shape:
`{"source": "...", "text": "...", "span": [start, end], "confidence": 0.0-1.0}`.

Input:
```json
{
  "note": "Scrubbed procedure note text...",
  "already_scrubbed": true,
  "include_financials": true,
  "explain": true
}
```

Output (excerpt):
```json
{
  "registry": { "...": "..." },
  "cpt_codes": ["31654"],
  "audit_warnings": ["SILENT_FAILURE: ..."],
  "review_status": "pending_phi_review",
  "needs_manual_review": true
}
```

### CPT Coding Endpoint
**POST** `/v1/coder/run` (legacy; returns 410 unless `PROCSUITE_ALLOW_LEGACY_ENDPOINTS=1`)

Input:
```json
{
  "note": "Bronchoscopy with EBUS at station 7.",
  "locality": "00",
  "setting": "facility"
}
```

Output:
```json
{
  "codes": [
    {
      "cpt": "31652",
      "description": "Bronchoscopy w/ EBUS 1-2 stations",
      "confidence": 0.95
    }
  ],
  "financials": {
    "total_work_rvu": 4.46
  }
}
```

### Registry Extraction Endpoint
**POST** `/v1/registry/run` (legacy; returns 410 unless `PROCSUITE_ALLOW_LEGACY_ENDPOINTS=1`)

Input:
```json
{
  "note": "Patient is a 65yo male..."
}
```

Optional mode override:
```json
{
  "note": "Patient is a 65yo male...",
  "mode": "parallel_ner"
}
```

Output:
```json
{
  "record": {
    "patient_age": 65,
    "gender": "M",
    "cpt_codes": [...]
  }
}
```

---

## Parallel Pathway Configuration

Use the parallel NER+ML pathway globally by setting these environment flags:

- `PROCSUITE_PIPELINE_MODE=extraction_first`
- `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
- `REGISTRY_SCHEMA_VERSION=v3` (recommended; required in production)
- `MODEL_BACKEND=auto` (or `pytorch`)

Example:
```bash
PROCSUITE_PIPELINE_MODE=extraction_first \
REGISTRY_EXTRACTION_ENGINE=parallel_ner \
REGISTRY_SCHEMA_VERSION=v3 \
MODEL_BACKEND=auto \
./ops/devserver.sh
```

Note: `MODEL_BACKEND=onnx` (the devserver default) may skip the registry ML classifier if ONNX artifacts are missing.

---

## 📊 Key Files

- **`data/knowledge/ip_coding_billing_v3_0.json`**: The "Brain". Contains all CPT codes, RVUs, and bundling rules.
- **`data/knowledge/ip_umls_map.json`**: Lightweight UMLS concept map (~19K IP-relevant concepts). Built by `ops/tools/build_ip_umls_map.py`, consumed by `proc_nlp/umls_lite.py`.
- **`schemas/IP_Registry.json`**: The "Law". Defines the valid structure for registry data.
- **`reports/`**: Where output logs and validation summaries are saved.

---

## 🖥️ Using the Web UI (Unicorn Frontend)

The Web UI provides a simple interface for coding procedure notes.

### Basic Usage

1. **Start the server**: `./ops/devserver.sh`
2. **Open the UI**: Navigate to [http://localhost:8000/ui/](http://localhost:8000/ui/)
3. **Select "Unified" tab** (recommended; production-style flow)
4. **Paste your procedure note** into the text area
5. **Configure options**:
   - **Include financials**: Adds RVU/payment estimates
   - **Explain**: Returns evidence spans for UI display/debugging
6. **Click "Run Processing"**

### PDF Upload and OCR (Client-Side)

The dashboard PDF path is browser-local (no server-side PDF/OCR):

- Uploading a PDF runs extraction in Web Workers under `ui/static/phi_redactor/pdf_local/`.
- `workers/pdf.worker.js` performs native pdf.js text extraction plus layout analysis.
- The UI computes per-page `nativeTextDensity = charCount / pageArea`:
  - Dense digital pages short-circuit OCR and use native text directly (`NATIVE_DENSE_TEXT` path).
- Pages that still need OCR are sent to `workers/ocr.worker.js`, which applies:
  - Image masking (`auto`, `on`, `off`)
  - Left-column/body crop logic
  - Header zonal OCR: top 25% of page split into left/right columns, OCRed separately, recombined in order.
- OCR postprocessing includes figure-overlap filtering and clinical hardening corrections:
  - `Lidocaine 49%` -> `Lidocaine 4%`
  - `Atropine 9.5 mg` -> `Atropine 0.5 mg`
  - `lyrnphadenopathy` -> `lymphadenopathy`
  - `hytnph` -> `lymph`
  - Lightweight Levenshtein correction for long clinical terms.
- Native/OCR fusion is strict: native text is preferred unless OCR recovers clear missing content.

Security constraints:

- Raw PDF bytes and unredacted extraction text stay in-browser.
- OCR assets are same-origin vendored assets (`ui/static/phi_redactor/vendor/`).
- Debug logging is metrics-only (no raw clinical text).

### Understanding the Results

In **Unified** mode, the UI runs the PHI workflow and then calls `POST /api/v1/process` with `already_scrubbed=true`.
You’ll see:

- **Pipeline metadata**: `pipeline_mode`, `review_status`, `needs_manual_review`
- **Audit warnings**: includes degraded-mode warnings like `SILENT_FAILURE:` and `DETERMINISTIC_UPLIFT:`
- **Evidence**: V3 evidence objects with `source/text/span/confidence`

### Suggested Missing Fields (Completeness)

At the top of the extraction dashboard results, the UI also shows **Suggested Missing Fields (Completeness)**:

- Prompts are **required** vs **recommended**, and are **procedure-aware** (based on what was performed + what’s missing).
- The panel includes **inputs** so you can enter missing values quickly.
  - These entries are staged into **Edited JSON (Training)** as JSON Patch operations (useful for QA/training review).
- For **evidence-backed extraction**, add the missing documentation to the **note text** and re-run extraction.
  - Tip: click **Open Reporter Builder** to insert a short addendum into the note before transferring back to the dashboard.

- **Billing Codes**: The final CPT codes with descriptions

- **RVU & Payment**: Work RVUs and estimated Medicare payment

---

## 📝 Reporter Module (Builder + Seed Strategies)

Reporter Builder is available at:

- `http://localhost:8000/ui/reporter_builder.html`

### Reporter Builder PHI Workflow (Required Before Seed)

Reporter Builder now enforces client-side PHI workflow before `Seed Bundle`:

1. Click `Run Detection`
2. Click `Apply Redactions`
3. Then click `Seed Bundle`

When seeded from Reporter Builder, the request sends `already_scrubbed=true` and the backend treats text as pre-scrubbed input for the reporter seed path.

### Seed Strategy Modes (`/report/seed_from_text`)

Reporter seeding is environment-controlled:

- `REPORTER_SEED_STRATEGY=registry_extract_fields` (default)
  - Uses deterministic extraction-first record seeding.
- `REPORTER_SEED_STRATEGY=llm_findings`
  - Reporter-only path: masked prompt -> GPT findings with evidence -> synthetic NER -> `NERToRegistryMapper` -> `ClinicalGuardrails` -> deterministic CPT derivation -> bundle/templates.

Optional strict mode for eval/QA:

- `REPORTER_SEED_LLM_STRICT=1`
  - Return error if LLM findings seeding fails (no fallback).
- Default (`0`/unset): fallback to deterministic seed and attach warning `REPORTER_SEED_FALLBACK: llm_findings_failed`.

### LLM Config for Reporter Findings

Use existing OpenAI-compatible wiring:

- `LLM_PROVIDER=openai_compat`
- `OPENAI_MODEL_STRUCTURER=gpt-5-mini`
- `OPENAI_API_KEY=...`
- `OPENAI_OFFLINE=0` (or fallback/strict behavior applies when offline)

### Reporter Prompt Random Sampling Tool

Generate random prompt->report samples from reporter training JSONL files:

```bash
python ops/tools/run_reporter_random_seeds.py \
  --input-dir /home/rjm/projects/proc_suite_notes/reporter_training/reporter_training \
  --count 20 \
  --seed 42 \
  --output reporter_tests.txt \
  --include-metadata-json
```

Outputs:

- `reporter_tests.txt` (human-readable prompt + output pairs)
- `reporter_tests.json` (machine-readable metadata/case outputs; default path)

To customize metadata path:

```bash
python ops/tools/run_reporter_random_seeds.py \
  --output reporter_tests.txt \
  --include-metadata-json \
  --metadata-output reporter_tests_metadata.json
```

### LLM Findings Evaluation Tool

Evaluate reporter LLM findings strategy on reporter prompt datasets:

```bash
PROCSUITE_ALLOW_ONLINE=1 \
LLM_PROVIDER=openai_compat \
OPENAI_MODEL_STRUCTURER=gpt-5-mini \
python ops/tools/eval_reporter_prompt_llm_findings.py \
  --input data/ml_training/reporter_prompt/v1/reporter_prompt_test.jsonl \
  --output data/ml_training/reporter_prompt/v1/reporter_prompt_llm_findings_eval_report.json
```

This evaluator is offline-safe by default and only performs real GPT calls when `PROCSUITE_ALLOW_ONLINE=1`.

---

## 🧠 Model Improvement

This section covers supported workflows for improving the repo’s ML models.

### ✅ Registry Procedure Classifier (Prodigy “Diamond Loop”)

This repo supports a human-in-the-loop loop for the **registry multi-label procedure classifier** using Prodigy’s `textcat` UI (multi-label `cats`) and disagreement sampling.

References:
- `docs/REGISTRY_PRODIGY_WORKFLOW.md` (the detailed “Diamond Loop” spec)
- `docs/MAKEFILE_COMMANDS.md` (Makefile target reference)

#### 0) One-time sanity check (do this first)

```bash
make lint
make typecheck
make test
```

#### 1) Build (or rebuild) your registry CSV splits

Run the recommended “final” prep (PHI-scrubbed) to produce the standard train/val/test CSVs:

```bash
make registry-prep-final

# If you need the raw (non-scrubbed) corpus for debugging:
# make registry-prep-raw
```

You should now have:
- `data/ml_training/registry_train.csv`
- `data/ml_training/registry_val.csv`
- `data/ml_training/registry_test.csv`

#### 2) Train a baseline model (1 epoch smoke test)

This confirms your training pipeline + artifacts are good.

```bash
python ml/scripts/train_roberta.py \
  --train-csv data/ml_training/registry_train.csv \
  --val-csv data/ml_training/registry_val.csv \
  --test-csv data/ml_training/registry_test.csv \
  --output-dir data/models/roberta_registry \
  --epochs 1
```

After it finishes, verify these exist:
- `data/models/roberta_registry/thresholds.json`
- `data/models/roberta_registry/label_order.json`

If you’re deciding “local CUDA vs VM”, check now:

```bash
python -c "import torch; print('cuda:', torch.cuda.is_available()); print('mps:', hasattr(torch.backends,'mps') and torch.backends.mps.is_available())"
```

- If **cuda: True** → keep going locally (fast iteration).
- If **cuda: False** and you’re on CPU/MPS → fine for a 1-epoch smoke test, but for real runs (3–5 epochs + repeated loops) a GPU VM will feel much better.

#### 3) Create (or confirm) your unlabeled notes file for Prodigy

Prodigy prep expects a JSONL where each line includes `note_text` (or `text` / `note`).

Default path used by the make targets:
- `data/ml_training/registry_unlabeled_notes.jsonl`

If you already have it, skip this.

#### 4) Prepare a Prodigy batch (disagreement sampling + pre-checked labels)

This generates:
- `data/ml_training/registry_prodigy_batch.jsonl`
- `data/ml_training/registry_prodigy_manifest.json`

```bash
make registry-prodigy-prepare \
  REG_PRODIGY_INPUT_FILE=data/ml_training/registry_unlabeled_notes.jsonl \
  REG_PRODIGY_COUNT=200
```

##### Annotating a specific JSONL file (example)

If you want to annotate a targeted file, override `REG_PRODIGY_INPUT_FILE` and give the dataset a descriptive name:

```bash
make registry-prodigy-prepare \
  REG_PRODIGY_INPUT_FILE=data/ml_training/registry_trach_peg.jsonl \
  REG_PRODIGY_COUNT=150

make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_trach_peg_v1
```

#### 5) Annotate in Prodigy (checkbox UI)

```bash
make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_v1
```

Notes:
- The annotation UI is served at `http://localhost:8080` (Prodigy’s default).
- This workflow uses **`textcat.manual`** (multi-label checkboxes via `cats`), not NER. If you see “Using 32 label(s): …” you’re in the right place.

##### Working across machines (Google Drive sync — safe “export/import”)

Do **not** cloud-sync the raw Prodigy SQLite DB file (risk of corruption). Instead, sync by exporting/importing a JSONL snapshot to a shared Google Drive folder.

Pick a single “source of truth” folder in Google Drive, e.g. `proc_suite_sync/`, and keep these inside it:
- `prodigy/registry_v1.prodigy.jsonl` (the Prodigy dataset snapshot)
- `diamond_loop/registry_prodigy_manifest.json` (recommended: avoids re-sampling across machines)
- `diamond_loop/registry_unlabeled_notes.jsonl` (recommended: consistent sampling universe)

###### Recommended: one-command Diamond Loop sync

Use `ml/scripts/diamond_loop_cloud_sync.py` to sync the dataset snapshot + key Diamond Loop files.

**WSL + Google Drive on Windows `G:` (your setup):**

```bash
# Pull latest from Drive before annotating on this machine
python ml/scripts/diamond_loop_cloud_sync.py pull \
  --dataset registry_v1 \
  --gdrive-win-root "G:\\My Drive\\proc_suite_sync" \
  --reset

# Push back to Drive after finishing a session
python ml/scripts/diamond_loop_cloud_sync.py push \
  --dataset registry_v1 \
  --gdrive-win-root "G:\\My Drive\\proc_suite_sync"
```

**macOS (Drive path varies by install):**

```bash
python ml/scripts/diamond_loop_cloud_sync.py pull \
  --dataset registry_v1 \
  --sync-root "/path/to/GoogleDrive/proc_suite_sync" \
  --reset

python ml/scripts/diamond_loop_cloud_sync.py push \
  --dataset registry_v1 \
  --sync-root "/path/to/GoogleDrive/proc_suite_sync"
```

Optional flags:
- Add `--include-batch` to also sync `data/ml_training/registry_prodigy_batch.jsonl` (resume the exact same batch on another machine)
- Add `--include-human` to also sync `data/ml_training/registry_human.csv`

###### Manual fallback: dataset-only export/import

If you prefer to sync just the Prodigy dataset snapshot file, you can use `ml/scripts/prodigy_cloud_sync.py` directly.

**Before you start annotating on a machine** (pull latest from Drive):

```bash
python ml/scripts/prodigy_cloud_sync.py import \
  --dataset registry_v1 \
  --in "/path/to/GoogleDrive/proc_suite_sync/prodigy/registry_v1.prodigy.jsonl" \
  --reset
```

**After you finish a session** (push to Drive):

```bash
python ml/scripts/prodigy_cloud_sync.py export \
  --dataset registry_v1 \
  --out "/path/to/GoogleDrive/proc_suite_sync/prodigy/registry_v1.prodigy.jsonl"
```

Rules:
- Only annotate on **one machine at a time**.
- Always **export after** you finish a session, and **import before** you start on another machine.
- If you rely on avoiding re-sampling, also keep `data/ml_training/registry_prodigy_manifest.json` synced alongside the dataset snapshot.

Annotate as many as you can tolerate in one sitting (even 50 is enough for the first iteration).

If you need to restart cleanly (wrong batch, wrong dataset, switching strategies), reset the dataset + batch/manifest:

```bash
make registry-prodigy-reset REG_PRODIGY_DATASET=registry_v1
```

#### 6) Export Prodigy annotations → a human labels CSV

Important:
- Export reads **everything currently in the Prodigy dataset** and writes a fresh CSV.
- The export **overwrites** the output path you provide (it does not append to an existing CSV file).

```bash
make registry-prodigy-export \
  REG_PRODIGY_DATASET=registry_v1 \
  REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human.csv
```

#### 7) (Recommended) Keep a single “master” human CSV across iterations

If you want to retain prior human labels while adding new annotation sessions/batches, use an “updates” file and merge it into your master:

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
- This works even if the updates contain **no overlapping** `encounter_id`s (common when you annotate a new batch).
- Merge keys on `encounter_id` (computed from `note_text` when missing).

#### 8) Merge human labels as Tier-0 and rebuild splits (no leakage)

This is critical: merge **before splitting**.

```bash
make registry-prep-with-human HUMAN_REGISTRY_CSV=data/ml_training/registry_human.csv
```

#### 9) Retrain for real (3–5 epochs)

```bash
python ml/scripts/train_roberta.py \
  --train-csv data/ml_training/registry_train.csv \
  --val-csv data/ml_training/registry_val.csv \
  --test-csv data/ml_training/registry_test.csv \
  --output-dir data/models/roberta_registry \
  --epochs 5
```

#### 10) Repeat the Diamond Loop

Repeat steps **4 → 9** until disagreement rate drops and metrics plateau.

Notes:
- Canonical label schema/order is `ml/lib/ml_coder/registry_label_schema.py`.
- Training uses `label_confidence` as a per-row loss weight when present.

### ➕ CPT Coding Model: Adding Training Cases

To improve the CPT model’s accuracy, you can add new training cases. Here's how:

#### Step 1: Prepare Your Data

Create a JSONL file with your cases. Each line should be a JSON object with:

```json
{
  "note": "Your procedure note text here...",
  "cpt_codes": ["31622", "31628"],
  "dataset": "my_new_cases"
}
```

**Required fields:**
- `note`: The full procedure note text
- `cpt_codes`: List of correct CPT codes for this note

**Optional fields:**
- `dataset`: A label for grouping (e.g., "bronchoscopy", "pleural")
- `procedure_type`: The type of procedure (auto-detected if not provided)

#### Step 2: Add Cases to Training Data

Place your JSONL file in the training data directory:

```bash
# Copy your cases to the training data folder
cp my_new_cases.jsonl data/training/
```

#### Step 3: Validate Your Cases

Before training, validate that your cases are properly formatted:

```bash
python - <<'PY'
import json
from pathlib import Path

path = Path("data/training/my_new_cases.jsonl")
for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
    if not line.strip():
        continue
    row = json.loads(line)
    missing = [field for field in ("note", "cpt_codes") if field not in row]
    if missing:
        raise ValueError(f"Line {index}: missing required fields {missing}")
print(f"Validated {path}")
PY
```

#### Step 4: Retrain the Model (Optional)

If you have enough new cases (50+), use the current registry-first training flow
documented above (`ml/scripts/train_roberta.py` and related commands).

#### Tips for Good Training Data

1. **Diverse examples**: Include various procedure types and complexity levels
2. **Accurate labels**: Double-check the CPT codes are correct
3. **Representative notes**: Use real-world note formats and writing styles
4. **Edge cases**: Include tricky cases where coding is non-obvious
5. **Clean text**: Remove any PHI (patient identifying information)

---

## 🔍 Reviewing Errors

When the system makes mistakes, you can review them to improve future performance.

### Run the Error Review Script

```bash
# Review all errors
python ml/scripts/review_llm_fallback_errors.py --mode all

# Review only fast path errors (ML+Rules mistakes)
python ml/scripts/review_llm_fallback_errors.py --mode fastpath

# Review only LLM fallback errors
python ml/scripts/review_llm_fallback_errors.py --mode llm_fallback
```

This generates a markdown report in `data/eval_results/` with:
- Error patterns and common mistakes
- Per-case review with recommendations
- Codes that were incorrectly predicted or missed

### Using Error Analysis to Improve the System

1. **False Positives** (codes predicted but shouldn't be):
   - May need to add negative rules to the rules engine
   - May need more training examples without these codes

2. **False Negatives** (codes missed):
   - May need to add new keyword patterns
   - May need more training examples with these codes

3. **ML was correct but LLM overrode it**:
   - Consider adjusting confidence thresholds
   - May need to improve LLM prompt constraints

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading at startup | `false` |
| `CODER_REQUIRE_PHI_REVIEW` | Require PHI review before coding | `false` |
| `DEMO_MODE` | Enable demo mode (synthetic data only) | `false` |
| `ENABLE_UMLS_LINKER` | Enable heavy scispaCy UMLS linker (disable on Railway) | `true` |
| `IP_UMLS_MAP_PATH` | Path to lightweight UMLS concept map for `umls_lite` | `data/knowledge/ip_umls_map.json` |

### OpenAI Configuration

When using an OpenAI-compatible backend (`LLM_PROVIDER=openai_compat`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | API key for OpenAI | Required |
| `OPENAI_MODEL` | Model name (e.g., `gpt-4o`) | Required |
| `OPENAI_BASE_URL` | Base URL (no `/v1` suffix) | `https://api.openai.com` |
| `OPENAI_PRIMARY_API` | API path: `responses` or `chat` | `responses` |
| `OPENAI_RESPONSES_FALLBACK_TO_CHAT` | Fall back to Chat on 404 | `1` |
| `OPENAI_TIMEOUT_READ_REGISTRY_SECONDS` | Registry task timeout (seconds) | `180` |
| `OPENAI_TIMEOUT_READ_DEFAULT_SECONDS` | Default task timeout (seconds) | `60` |

**Note**: The system uses OpenAI's Responses API by default. For endpoints that don't support it, use `OPENAI_PRIMARY_API=chat`.

### Adjusting ML Thresholds

The ML model's confidence thresholds can be tuned in `ml/lib/ml_coder/thresholds.py`:

```python
# High confidence threshold (codes above this are HIGH_CONF)
HIGH_CONF_THRESHOLD = 0.80

# Gray zone lower bound (codes between this and HIGH_CONF are GRAY_ZONE)
GRAY_ZONE_THRESHOLD = 0.45

# Codes below GRAY_ZONE_THRESHOLD are LOW_CONF
```

Higher thresholds = more cases go to LLM (safer but slower)
Lower thresholds = more cases use fast path (faster but may miss edge cases)

---

## 🛡️ PHI Redaction & Training

The Procedure Suite includes tools for training and improving PHI (Protected Health Information) redaction models.

### PHI Audit

Audit a note for PHI detection:

```bash
python ml/scripts/phi_audit.py --note-path test_redact.txt
```

### Scrubbing Golden JSON Files

Scrub PHI from golden extraction files:

```bash
python ml/scripts/scrub_golden_jsons.py \
  --input-dir data/knowledge/golden_extractions \
  --pattern 'golden_*.json' \
  --report-path artifacts/redactions.jsonl
```

### Platinum Redaction Pipeline (Golden → Scrubbed/Final)

For registry ML training data, use the **Platinum** workflow (hybrid redactor → character spans → applied redactions).

**Key behavior:**
- Scrubs both `note_text` **and** `registry_entry.evidence` to prevent PHI leakage
- Standardizes all PHI placeholders to the single token: `[REDACTED]`
- Does **not** redact physician/provider names (e.g., `Dr. Stevens`)

**Run the pipeline (recommended):**
```bash
make platinum-final
```
This produces:
- `data/knowledge/golden_extractions_scrubbed/` (PHI-scrubbed)
- `data/knowledge/golden_extractions_final/` (scrubbed + institution cleanup)

**Or run step-by-step:**
```bash
make platinum-build      # data/ml_training/phi_platinum_spans.jsonl
make platinum-sanitize   # data/ml_training/phi_platinum_spans_CLEANED.jsonl
make platinum-apply      # data/knowledge/golden_extractions_scrubbed/
python ml/scripts/fix_registry_hallucinations.py \
  --input-dir data/knowledge/golden_extractions_scrubbed \
  --output-dir data/knowledge/golden_extractions_final
```

**Optional: align synthetic names before building spans**
```bash
python ml/scripts/align_synthetic_names.py \
  --input-dir data/knowledge/golden_extractions \
  --output-dir data/knowledge/golden_extractions_aligned
```
If you use the aligned directory, point the pipeline at it:
```bash
PLATINUM_INPUT_DIR=data/knowledge/golden_extractions_aligned make platinum-cycle
```

### PHI Model Training with Prodigy

Use Prodigy for iterative PHI model improvement:

**Workflow:**
```bash
make prodigy-prepare      # Sample new notes for annotation
make prodigy-annotate     # Annotate in Prodigy UI
make prodigy-export       # Export corrections to training format
make prodigy-finetune     # Fine-tune model (recommended)
```

**Training Options:**

| Command | Description |
|---------|-------------|
| `make prodigy-finetune` | Fine-tunes existing model (1 epoch, low LR), preserves learned weights |
| `make prodigy-retrain` | Trains from scratch (3 epochs), loses previous training |

**Fine-tuning details:**
- `--resume-from artifacts/phi_distilbert_ner` - Starts from your trained weights
- `--epochs 1` - Just one pass over the data (override with `PRODIGY_EPOCHS=3`)
- `--lr 1e-5` - Low learning rate to avoid catastrophic forgetting
- Automatically detects and uses Metal (MPS) or CUDA when available
- Removes MPS memory limits to use full system memory

**Manual fine-tuning (same as `make prodigy-finetune`):**
```bash
python ml/scripts/train_distilbert_ner.py \
    --resume-from artifacts/phi_distilbert_ner \
    --patched-data data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl \
    --output-dir artifacts/phi_distilbert_ner \
    --epochs 1 \
    --lr 1e-5 \
    --train-batch 4 \
    --eval-batch 16 \
    --gradient-accumulation-steps 2 \
    --mps-high-watermark-ratio 0.0
```

### Model Locations & Exporting for UI

The PHI model exists in two locations:

1. **Training location** (PyTorch format): `artifacts/phi_distilbert_ner/`
   - Updated by `make prodigy-finetune` or `make prodigy-retrain`
   - Contains PyTorch model weights, tokenizer, and label mappings

2. **Client-side location** (ONNX format): `ui/static/phi_redactor/vendor/phi_distilbert_ner/`
   - Used by the browser UI at `http://localhost:8000/ui/phi_redactor/`
   - Contains ONNX model files, tokenizer, and configuration

**Important**: After training, you must export the model to update the UI:

```bash
make export-phi-client-model
```

This converts the PyTorch model to ONNX format and copies it to the static directory. The UI will continue using the old model until you run this export step.

**Export options:**
- `make export-phi-client-model` - Exports unquantized ONNX model (default)
- `make export-phi-client-model-quant` - Exports quantized ONNX model (smaller, but may have accuracy trade-offs)

### Hard Negative Fine-tuning

Fine-tune on hard negatives (cases where the model made mistakes):

```bash
make finetune-phi-client-hardneg
```

This uses:
- `--resume-from artifacts/phi_distilbert_ner`
- `--patched-data data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl`
- Memory-optimized settings for MPS/CUDA

### Gold Standard PHI Training Workflow

Train on pure human-verified data from Prodigy annotations. This workflow uses only Prodigy-verified annotations for maximum quality training.

**Complete Workflow (Step-by-Step):**

```bash
# Step 1: Export pure gold from Prodigy
make gold-export

# Step 2: Split into train/test (80/20 with note grouping)
make gold-split

# Step 3: Train on gold data (10 epochs default)
make gold-train

# Step 4: Safety audit on gold test set
make gold-audit

# Step 5: Evaluate F1 metrics on gold test set
make gold-eval

# Step 6: Export updated ONNX for browser
make export-phi-client-model
```

**Or run the full cycle (Steps 1-5) with one command:**

```bash
make gold-cycle
```

**Training Configuration:**
- **Epochs**: 10 (default, override with `GOLD_EPOCHS=15`)
- **Learning rate**: 1e-5
- **Batch size**: 4 (with gradient accumulation = 2, effective batch = 8)
- **GPU acceleration**: Automatically detects and uses Metal (MPS) or CUDA
- **Memory optimization**: Removes MPS memory limits to use full system memory on Mac

**Output Files:**
- `data/ml_training/phi_gold_standard_v1.jsonl` - Exported gold data
- `data/ml_training/phi_train_gold.jsonl` - Training split (80%)
- `data/ml_training/phi_test_gold.jsonl` - Test split (20%)
- `artifacts/phi_distilbert_ner/audit_gold_report.json` - Safety audit report

**When to use:**
- When you have a sufficient amount of Prodigy-verified annotations
- For maximum quality training on human-verified data
- When you want to train for more epochs on smaller, high-quality datasets

### Testing PHI Redaction

Test the client-side PHI redactor:

```bash
cd ops/tools/phi_test_node
node test_phi_redaction.mjs --count 30
```

### Server Configuration for PHI

Start the dev server with different model backends:

```bash
# Use PyTorch backend (for PHI without registry ONNX)
MODEL_BACKEND=pytorch ./ops/devserver.sh

# Auto-detect best backend
MODEL_BACKEND=auto ./ops/devserver.sh
```
http://localhost:8000/ui/phi_redactor/
---

## Deploy Mirror (Slim Railway Repo)

The monorepo is large (training data, ML scripts, docs, etc.), so Railway deployments use a lightweight **deploy mirror** that contains only runtime files. The mirror lives at:

- **Deploy repo:** [github.com/russellmiller49/proc_suite_deploy](https://github.com/russellmiller49/proc_suite_deploy) (`main` branch)

### What is included

Runtime code and dependencies only: `app/`, `observability/`, `ml/`, `config/`, `configs/`, `ops/`, `proc_schemas/`, `proc_nlp/`, `proc_kb/`, `schemas/`, `ui/static` (minus PHI vendor), Alembic migrations, minimal runtime data, `pyproject.toml`, `requirements.txt`, `runtime.txt`.

### What is excluded

Training data (outside the allowlisted runtime subset), docs, tests, heavyweight PHI vendor model artifacts (`ui/static/phi_redactor/vendor/phi_distilbert_ner*`), and local caches.

### Automatic sync (GitHub Actions)

A workflow (`.github/workflows/deploy-mirror-sync.yml`) automatically syncs the mirror on every push to `main` in `Procedure_suite`. It can also be triggered manually from the Actions tab (`workflow_dispatch`).

**Required GitHub configuration** (set on the `Procedure_suite` repo under Settings > Secrets and variables > Actions):

| Type | Name | Value |
|------|------|-------|
| Variable | `DEPLOY_MIRROR_REPO` | `russellmiller49/proc_suite_deploy` |
| Variable | `DEPLOY_MIRROR_BRANCH` | `main` (optional, defaults to `main`) |
| Secret | `DEPLOY_MIRROR_PUSH_TOKEN` | A fine-grained PAT with `Contents: Read and write` on the deploy repo |

The workflow skips gracefully when `DEPLOY_MIRROR_REPO` or `DEPLOY_MIRROR_PUSH_TOKEN` is not set.

### Manual sync (local)

Build and push the mirror from your local machine:

```bash
# Build the payload
bash ops/tools/build_deploy_mirror.sh /tmp/proc-suite-deploy

# Push to the deploy repo
cd /tmp/proc-suite-deploy
git init && git checkout -b main
git add -A && git commit -m "chore(deploy-mirror): manual sync"
git remote add origin https://github.com/russellmiller49/proc_suite_deploy.git
git push -u origin main --force
```

### Including PHI vendor assets (one-off)

By default, heavyweight PHI model vendor folders are excluded while core OCR web assets (`vendor/tesseract`, `vendor/pdfjs`) are included. To include the heavyweight PHI model folders too:

```bash
DEPLOY_MIRROR_INCLUDE_VENDOR=1 bash ops/tools/build_deploy_mirror.sh /tmp/proc-suite-deploy
```

Or trigger the workflow manually from the Actions tab and check "Include heavyweight PHI model vendor folders in mirror payload".

### Key files

| File | Purpose |
|------|---------|
| `ops/deploy/mirror_paths.txt` | Allowlist of paths copied to the mirror |
| `ops/tools/build_deploy_mirror.sh` | Build script that assembles the payload |
| `.github/workflows/deploy-mirror-sync.yml` | GitHub Actions workflow for automatic sync |
| `docs/DEPLOY_MIRROR.md` | Detailed reference documentation |

---

## 📞 Getting Help

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Technical Issues**: Check the logs in `logs/` directory
- **Questions**: Open an issue on the repository

---

## 🏷️ Registry NER training (granular)

Use this workflow to retrain the **granular registry NER** model with the **BiomedBERT** tokenizer/model.

### Step 1) Regenerate BIO training data (crucial)
This rebuilds `ner_bio_format.jsonl` using the target tokenizer. Do this any time you change the base model/tokenizer.

```bash
python ml/scripts/convert_spans_to_bio.py \
  --input data/ml_training/granular_ner/ner_dataset_all.jsonl \
  --output data/ml_training/granular_ner/ner_bio_format.jsonl \
  --model microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext \
  --max-length 512
```

### Step 2) Train the model
Note: the training script uses **hyphenated** flags like `--output-dir`, `--train-batch`, and the learning rate flag is `--lr`.

```bash
python ml/scripts/train_registry_ner.py \
  --data data/ml_training/granular_ner/ner_bio_format.jsonl \
  --output-dir artifacts/registry_biomedbert_ner \
  --epochs 20 \
  --lr 2e-5 \
  --train-batch 16 \
  --eval-batch 16
```

---

## 🧪 Reporter Gold Pilot Dataset

Build a versioned pilot dataset of golden reporter notes from `_syn_*` short synthetic notes.
The generator reads `LLM_PROVIDER`, `OPENAI_API_KEY`, and `OPENAI_MODEL` from local `.env` by default (unless `PROCSUITE_SKIP_DOTENV=1`).

### Generate pilot candidates (200 notes)

```bash
make reporter-gold-generate-pilot \
  REPORTER_GOLD_INPUT_DIR=/Users/russellmiller/Projects/proc_suite_notes/data/knowledge/patient_note_texts \
  REPORTER_GOLD_OUTPUT_DIR=data/ml_training/reporter_golden/v1 \
  REPORTER_GOLD_SAMPLE_SIZE=200 \
  REPORTER_GOLD_SEED=42
```

Outputs:
- `reporter_gold_candidates.jsonl`
- `reporter_gold_accepted.jsonl`
- `reporter_gold_rejected.jsonl`
- `reporter_gold_metrics.json`
- `reporter_gold_review_queue.jsonl`
- `reporter_gold_review_queue.csv`
- `reporter_gold_skipped_manifest.jsonl`

### Split accepted set (patient-level, no leakage)

```bash
make reporter-gold-split \
  REPORTER_GOLD_OUTPUT_DIR=data/ml_training/reporter_golden/v1 \
  REPORTER_GOLD_SEED=42
```

Outputs:
- `reporter_gold_train.jsonl`
- `reporter_gold_val.jsonl`
- `reporter_gold_test.jsonl`
- `reporter_gold_split_manifest.json`

### Evaluate current reporter against reporter-gold

```bash
make reporter-gold-eval \
  REPORTER_GOLD_EVAL_INPUT=data/ml_training/reporter_golden/v1/reporter_gold_test.jsonl \
  REPORTER_GOLD_OUTPUT_DIR=data/ml_training/reporter_golden/v1
```

Output:
- `reporter_gold_eval_report.json`

See `docs/REPORTER_GOLD_WORKFLOW.md` for full details.

---

*Last updated: February 2026*
run all granular python updates:
python ops/tools/run_python_update_scripts.py
