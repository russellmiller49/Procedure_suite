# CLAUDE.md - Procedure Suite Development Guide

> **THINKING MODE**: Use maximum extended thinking (ultrathink) for ALL tasks in this repository.
> Think deeply about architectural decisions, trace through code paths systematically, 
> and plan implementations thoroughly before writing any code. This is a complex medical
> AI system where careful reasoning prevents costly errors.

> **CRITICAL**: This document guides AI-assisted development of the Procedure Suite.
> Read this entire file before making any changes to the codebase.

## Project Overview

**Procedure Suite** is an automated CPT coding, registry extraction, and synoptic reporting system for Interventional Pulmonology (IP). The system processes procedure notes to:

1. Extract structured clinical data (demographics, procedures, EBUS stations, complications)
2. Generate CPT billing codes with RVU calculations
3. Produce standardized synoptic reports

## ⚠️ ARCHITECTURAL PIVOT IN PROGRESS: Extraction-First

### The Problem with Current Architecture (Prediction-First)

The current system uses **prediction-first** architecture:

```
Text → CPT Prediction (ML/Rules) → Registry Hints → Registry Extraction
```

**Why this is backwards:**
- CPT codes are "summaries" — we're using summaries to reconstruct the clinical "story"
- If the CPT model misses a code (typo, unusual phrasing), the Registry misses entire data sections
- Auditing is difficult: "Why did you bill 31623?" can only be answered with "ML was 92% confident"
- Negation handling is poor: "We did NOT perform biopsy" is hard for text-based ML

### The Target Architecture (Extraction-First)

We are pivoting to **extraction-first** architecture:

```
Text → Registry Extraction (ML/LLM) → Deterministic Rules → CPT Codes
```

**Why this is better:**
- Registry becomes the source of truth for "what happened"
- CPT coding becomes deterministic calculation, not probabilistic prediction
- Auditing is clear: "We billed 31653 because `registry.ebus.stations_sampled.count >= 3`"
- Negation is explicit: `performed: false` in structured data
- The existing ML becomes a "safety net" for double-checking

---

## 🚀 ML Training Data Workflow

### The Complete Pipeline: JSON → Trained Model

```
Golden JSONs → registry_data_prep.py (3-tier hydration + dedup) → train_roberta.py → ONNX Model
```

The production data preparation module uses **3-tier extraction with hydration** and **priority-based deduplication** for clean, high-quality training data.

---

### Quick Start (Make Commands)

```bash
make registry-prep        # Generate train/val/test CSV files
make registry-prep-dry    # Preview extraction stats (no file writes)
make registry-prep-module # Run via Python module interface
```

Or use the `/registry-data-prep` skill for guided execution.

---

### Step 1: Update Source Data

Add or modify your golden JSON files in:
```
data/knowledge/golden_extractions_final/   # PHI-scrubbed (preferred)
data/knowledge/golden_extractions/          # Fallback
```

---

### Step 2: Prepare Training Splits

**Using CLI script (recommended):**
```bash
python scripts/golden_to_csv.py \
  --input-dir data/knowledge/golden_extractions_final \
  --output-dir data/ml_training \
  --prefix registry
```

**Using Python API:**
```python
from modules.ml_coder.registry_data_prep import prepare_registry_training_splits

train_df, val_df, test_df = prepare_registry_training_splits()

train_df.to_csv("data/ml_training/registry_train.csv", index=False)
val_df.to_csv("data/ml_training/registry_val.csv", index=False)
test_df.to_csv("data/ml_training/registry_test.csv", index=False)
```

---

### 3-Tier Extraction with Hydration

The pipeline extracts labels from golden JSONs using a cascading approach:

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: Structured Extraction (confidence: 0.95)            │
│ extract_v2_booleans(registry_entry)                         │
│ Source: modules/registry/v2_booleans.py                     │
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
```

**Typical distribution:**
- Tier 1 (Structured): ~79%
- Tier 2 (CPT): ~18%
- Tier 3 (Keyword): ~3%

---

### Priority-Based Deduplication

When the same `note_text` appears multiple times with different labels, deduplication keeps the highest-priority source:

```
structured (priority=3) > cpt (priority=2) > keyword (priority=1)
```

**Benefits:**
- Eliminates conflicting ground truth signals
- Removes ~2-3% duplicate records
- Tracks conflict statistics for quality monitoring

---

### Output Schema

Each output CSV contains:

| Column | Description |
|--------|-------------|
| `note_text` | Procedure note text |
| `encounter_id` | Stable hash for encounter-level grouping |
| `source_file` | Origin golden JSON file |
| `label_source` | Extraction tier ("structured", "cpt", "keyword") |
| `label_confidence` | Confidence score (0.60-0.95) |
| `[29 procedure columns]` | Binary (0/1) procedure labels |

---

### Step 3: Train Model

```bash
python scripts/train_roberta.py --batch-size 16 --epochs 5
```

Or with explicit paths:
```bash
python scripts/train_roberta.py \
  --train-csv data/ml_training/registry_train.csv \
  --val-csv data/ml_training/registry_val.csv \
  --test-csv data/ml_training/registry_test.csv
```

---

### Key Module Functions

| Function | Purpose |
|----------|---------|
| `prepare_registry_training_splits()` | Main entry - returns (train_df, val_df, test_df) |
| `extract_records_from_golden_dir()` | Extract records with 3-tier hydration |
| `deduplicate_records()` | Remove duplicates by source priority |
| `extract_labels_with_hydration()` | Single-entry label extraction |
| `stratified_split()` | Multi-label stratification with grouping |

**Key Files:**
- `modules/ml_coder/registry_data_prep.py` - Core data prep logic
- `modules/ml_coder/label_hydrator.py` - 3-tier extraction + hydration
- `scripts/golden_to_csv.py` - CLI interface

**Tests:**
- `tests/ml_coder/test_registry_first_data_prep.py`
- `tests/ml_coder/test_label_hydrator.py`

---

## 🔒 PHI Label Distillation (Silver vs Platinum)

**Silver (Piiranha → token BIO):** fast offline distillation for client-sized models.

**Run:**
```bash
python scripts/distill_phi_labels.py --limit-notes 50 --device cpu
```
Or:
```bash
make distill-phi-silver
```

**Output:** `data/ml_training/distilled_phi_labels.jsonl`

**Sanitizer (post-hoc):** clean older distills or add belt-and-suspenders protection.
```bash
python scripts/sanitize_dataset.py
```
Or:
```bash
make sanitize-phi-silver
```
**Output:** `data/ml_training/distilled_phi_CLEANED.jsonl`
**Normalize (post-hoc):** collapse remaining granular Piiranha classes (e.g., `PASSWORD`) into a small stable schema for client training.
```bash
python scripts/normalize_phi_labels.py
```
Or:
```bash
make normalize-phi-silver
```
**Output:** `data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl`

**Workflow:** distill → sanitize → normalize → train on the STANDARD file for client models.

**Password policy:** default is `id` (recommended) which maps `PASSWORD → ID`; optional `--password-policy drop` maps `PASSWORD → O`.

---

## ✅ Client NER Evaluation (DistilBERT)

**Evaluate without retraining:**
```bash
make eval-phi-client
```

**Safety regression audit (must-not-redact guardrails):**
```bash
make audit-phi-client
```

> **SAFETY INVARIANT**: Post-veto must-not-redact audit violations **must be 0**.
> Raw model violations may be non-zero; the post-processing veto layer guarantees safety.
> The audit specifically checks: CPT codes, LN stations, anatomy terms, and device terms.

**Hard-negative finetuning workflow** (optional if post-veto is already 0):
```bash
make audit-phi-client           # Identify violations
make patch-phi-client-hardneg   # Patch training data with hard negatives
make finetune-phi-client-hardneg # Finetune model on patched data
```

**If seqeval missing:**
```bash
pip install evaluate seqeval
```

**Interpretation:** review `artifacts/phi_distilbert_ner/eval_metrics.json` for `overall_f1`.

---

## 🔄 Prodigy-Based Iterative Label Correction

Human-in-the-loop workflow for improving PHI detection using [Prodigy](https://prodi.gy/).

### Workflow Overview

```
┌─────────────────────────────────────────────────────────────┐
│  1. Sample Notes → Pre-annotate with DistilBERT             │
│     make prodigy-prepare (or prodigy-prepare-file)          │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Prodigy ner.manual - Review/correct annotations         │
│     make prodigy-annotate                                   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Export corrections → Merge with training data           │
│     make prodigy-export                                     │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Fine-tune model (preserves learned weights)             │
│     make prodigy-finetune                                   │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
                      Iterate → Back to Step 1
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `make prodigy-prepare` | Sample 100 golden notes, pre-annotate with DistilBERT |
| `make prodigy-prepare-file` | Prepare from specific file (default: `synthetic_phi.jsonl`) |
| `make prodigy-annotate` | Launch Prodigy annotation UI (ner.manual) |
| `make prodigy-export` | Export corrections, merge with training data |
| `make prodigy-finetune` | Fine-tune existing model (recommended) |
| `make prodigy-retrain` | Train from scratch (loses learned weights) |
| `make prodigy-cycle` | Run prepare + show next steps |

### Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PRODIGY_COUNT` | `100` | Number of notes to sample |
| `PRODIGY_DATASET` | `phi_corrections` | Prodigy dataset name |
| `PRODIGY_INPUT_FILE` | `synthetic_phi.jsonl` | Input file for `prodigy-prepare-file` |
| `PRODIGY_EPOCHS` | `1` | Fine-tuning epochs |

### Example: Full Iteration Cycle

```bash
# 1. Prepare batch (from synthetic PHI data)
make prodigy-prepare-file PRODIGY_COUNT=50

# 2. Launch Prodigy UI - review/correct annotations
make prodigy-annotate
# (Annotate in browser at http://localhost:8080)

# 3. Export corrections to training format
make prodigy-export

# 4. Fine-tune model on corrected data
make prodigy-finetune PRODIGY_EPOCHS=2

# 5. Evaluate model performance
make eval-phi-client

# 6. Export updated ONNX for browser
make export-phi-client-model
```

### Key Files

| File | Purpose |
|------|---------|
| `scripts/prodigy_prepare_phi_batch.py` | Sample notes, run DistilBERT inference, output Prodigy JSONL |
| `scripts/prodigy_export_corrections.py` | Convert Prodigy → BIO training format |
| `data/ml_training/prodigy_manifest.json` | Track annotated windows (avoids re-sampling) |
| `data/ml_training/prodigy_batch.jsonl` | Current batch for annotation |
| `data/ml_training/phi_gold_standard_v1.jsonl` | Gold standard export (pure Prodigy data) |
| `data/ml_training/phi_train_gold.jsonl` | Gold training set (80% of notes) |
| `data/ml_training/phi_test_gold.jsonl` | Gold test set (20% of notes) |
| `data/ml_training/ARCHIVE_distilled_phi_raw.jsonl` | Old mixed data (archived) |
| `synthetic_phi.jsonl` | Dense synthetic PHI data (300 records) |

### Tips

- **Use `prodigy-finetune` (not `prodigy-retrain`)** to preserve learned weights
- **Drop dataset to re-annotate**: `prodigy drop phi_corrections`
- **Check Prodigy stats**: `prodigy stats phi_corrections`
- **Synthetic data** (`synthetic_phi.jsonl`) has dense PHI for targeted training
- **Fine-tune with more epochs**: `make prodigy-finetune PRODIGY_EPOCHS=3`

### Prodigy Installation Note

Prodigy requires a separate Python environment (system Python 3.12):
```bash
# Prodigy is installed in system Python, not conda
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m prodigy --help
```

---

## ⭐ Gold Standard PHI Training (Recommended)

The gold workflow uses **only human-verified Prodigy annotations** for maximum quality training. Unlike the mixed "silver" data, gold standard data contains no unverified machine labels.

### Why Gold Standard?

- **Pure human verification**: Every annotation explicitly reviewed
- **No data leakage**: Notes split at encounter level (all windows from same note in same split)
- **Higher quality**: Smaller but cleaner dataset produces better model convergence
- **Audit-friendly**: Clear provenance for all training labels

### Gold Workflow Commands

| Command | Purpose |
|---------|---------|
| `make gold-export` | Export pure gold from Prodigy dataset (no merging) |
| `make gold-split` | 80/20 train/test split with note-level grouping |
| `make gold-train` | Train with 10 epochs on smaller high-quality data |
| `make gold-audit` | Safety audit on gold test set |
| `make gold-eval` | Evaluate metrics on gold test set |
| `make gold-cycle` | Full workflow: export → split → train → audit → eval |

### Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOLD_EPOCHS` | `10` | Training epochs (more for smaller dataset) |
| `GOLD_DATASET` | `phi_corrections` | Prodigy dataset to export |
| `GOLD_OUTPUT_DIR` | `data/ml_training` | Output directory |
| `GOLD_MODEL_DIR` | `artifacts/phi_distilbert_ner` | Model directory |

### Example: Complete Gold Workflow

```bash
# 1. Export pure gold from Prodigy (no merging with old data)
make gold-export

# 2. Split into train/test with note-level grouping
make gold-split

# 3. Train on pure gold (10 epochs default)
make gold-train

# 4. Safety audit (post-veto violations must be 0)
make gold-audit

# 5. Evaluate F1 metrics
make gold-eval

# Or run full cycle:
make gold-cycle
```

### Key Files

| File | Purpose |
|------|---------|
| `scripts/export_phi_gold_standard.py` | Export Prodigy → BIO format (no merging) |
| `scripts/split_phi_gold.py` | Train/test split with note grouping |
| `phi_gold_standard_v1.jsonl` | Full gold export from Prodigy |
| `phi_train_gold.jsonl` | Training set (80% of notes) |
| `phi_test_gold.jsonl` | Test set (20% of notes) |
| `ARCHIVE_distilled_phi_raw.jsonl` | Old mixed data (preserved for reference) |

### Transition from Mixed Data

The old `distilled_phi_WITH_CORRECTIONS.jsonl` (mixed Piiranha + Prodigy) has been archived. The gold workflow replaces it with pure human-verified data for higher quality training.

---

## 🌐 Client-side PHI Redactor (Transformers.js)

**Export local ONNX bundle:**
```bash
make export-phi-client-model
```

**Export quantized (opt-in):**
```bash
make export-phi-client-model-quant
```

### Bundle Layout

The ONNX model **must** live in an `onnx/` subfolder:
```
ui/phi_redactor/vendor/phi_distilbert_ner/
├── config.json
├── tokenizer.json
├── tokenizer_config.json
├── vocab.txt
├── protected_terms.json
└── onnx/
    ├── model.onnx
    └── model_quantized.onnx (optional)
```

The worker reads these files at runtime:
- `/ui/phi_redactor/vendor/phi_distilbert_ner/protected_terms.json`
- `/ui/phi_redactor/vendor/phi_distilbert_ner/onnx/model*.onnx`

### Quantization Warning

> **Known issue**: Quantized ONNX models may produce "all-O / empty output" in WASM runtime.
> **Recommendation**: Start with unquantized model (`forceUnquantized: true`). Only enable quantized after verification.

### Configuration Defaults

| Setting | Default | Description |
|---------|---------|-------------|
| `aiThreshold` | `0.45` | Confidence threshold for PHI detection |
| `forceUnquantized` | `true` | Use unquantized model (safe default) |

### Hybrid Detection Architecture (ML + Regex)

The client-side PHI redactor uses a **hybrid detection pipeline** to guarantee detection of structured header PHI even during ML "cold start" when the model may return 0 entities.

**Pipeline flow:**
```
┌─────────────────────────────────────────────────────────────┐
│  FOR EACH CHUNK (2500 chars, 250 overlap):                  │
│                                                             │
│    1. ML NER (DistilBERT via Transformers.js)               │
│       └── Returns spans with label/score/source="ner"       │
│                                                             │
│    2. Regex Detectors (deterministic)                       │
│       ├── PATIENT_HEADER_RE → PATIENT span (score=1.0)      │
│       └── MRN_RE → ID span (score=1.0, source="regex_*")    │
│                                                             │
│    3. Dedupe exact duplicates within chunk                  │
│    4. Convert to absolute offsets                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  POST-PROCESSING (after all chunks):                        │
│                                                             │
│    5. mergeOverlapsBestOf — prefer regex on overlap         │
│    6. expandToWordBoundaries — fix partial-word redactions  │
│    7. mergeOverlapsBestOf — re-merge after expansion        │
│    8. applyVeto (protectedVeto.js) — filter false positives │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    Final Detections
```

**Key files:**
- `modules/api/static/phi_redactor/redactor.worker.js` — Hybrid detection worker
- `modules/api/static/phi_redactor/protectedVeto.js` — Veto/allow-list layer

**Regex patterns (guaranteed detection):**
```javascript
// Patient header names: "Patient: Smith, John" or "Pt Name: John Smith"
const PATIENT_HEADER_RE = /(?:Patient(?:\s+Name)?|Pt|Name|Subject)\s*[:\-]?\s*([A-Z][a-z]+,...)/gim;

// MRN / IDs: "MRN: 12345" or "ID: 55-22-11"
const MRN_RE = /\b(?:MRN|MR|Medical\s*Record|Patient\s*ID|ID|EDIPI|DOD\s*ID)\s*[:\#]?\s*([A-Z0-9\-]{4,15})\b/gi;
```

**Why hybrid is needed:**
- ML models can return 0 entities on first inference ("cold start")
- Header PHI (patient name, MRN) is critical and must never be missed
- Regex provides deterministic guarantees while ML catches free-text PHI
- Regex spans have `score: 1.0` to survive thresholding

**Key merge behaviors (`mergeOverlapsBestOf`):**
- On overlap: prefer regex spans over ML spans (avoids double-highlights)
- Same label + adjacent/overlapping: union into single span
- Different labels + ≥80% overlap: keep higher-scoring span
- Different labels + <80% overlap: keep both spans

**Word boundary expansion (`expandToWordBoundaries`):**
- Fixes partial-word redactions like `"id[REDACTED]"` → `"[REDACTED]"`
- Expands span start/end to include adjacent alphanumeric chars
- Treats apostrophe/hyphen as word-chars when adjacent to alnum (e.g., "O'Brien")

**Veto layer (protectedVeto.js):**
The veto layer runs AFTER detection to filter false positives:
- LN stations (4R, 7, 11Rs) — anatomy, not PHI
- Segments (RB1, LB1+2) — anatomy, not PHI
- Measurements (5ml, 24 French) — clinical, not PHI
- Provider names (Dr. Smith, Attending: Jones) — staff, not patient PHI
- CPT codes in billing context (31653) — codes, not PHI
- Clinical terms (EBUS, TBNA, BAL) — procedures, not PHI

**Smoke test:**
1. Start dev server and open `/ui/phi_redactor/`.
2. Paste text containing:
   - Codes: `31653`, `77012`
   - LN stations: `4R`, `7` (with "station" nearby), `10R`, `11Ri`
   - Anatomy: `Left Upper Lobe`
   - Devices: `Dumon`, `Chartis`, `Zephyr`, `PleurX`
   - Real PHI: patient name, DOB, phone, address
3. Expected:
   - PHI highlights for patient/DOB/phone/address
   - Must-not-redact items are NOT highlighted

### Manual Redaction Feature

Users can add redactions for PHI missed by auto-detection:

1. Select text in the Monaco editor
2. Choose entity type from dropdown (Patient Name, MRN/ID, Date, Phone, Location, Other)
3. Click "Add" button

**Visual distinction:**
- **Auto-detected PHI**: Red highlighting
- **Manual additions**: Amber/yellow highlighting

**UI Components:**
- `entityTypeSelect` - Dropdown for entity type selection
- `addRedactionBtn` - "Add" button (enabled only when text is selected)
- Manual detections appear in sidebar with "manual" source tag

**Key files:**
- `modules/api/static/phi_redactor/app.js` - Selection tracking + Add button logic
- `modules/api/static/phi_redactor/styles.css` - `.phi-detection-manual` styling

### Formatted Results Display

After submitting a scrubbed note, the UI displays formatted results instead of raw JSON:

**Status Banner:**
- **Green**: High confidence extraction, no review needed
- **Yellow**: Audit warnings present, review recommended
- **Red**: Manual review required

**CPT Codes Table:**
| Column | Description |
|--------|-------------|
| Code | CPT code (e.g., 31653) |
| Description | Procedure description |
| Confidence | Model confidence % |
| RVU | Work relative value units |
| Payment | Estimated facility payment |

**Registry Summary:**
- Shows ALL non-null fields from `registry` response
- Nested objects displayed with " → " path notation (e.g., "Linear Ebus → Stations Sampled")
- Skips `null`, `false` booleans, and empty arrays
- `snake_case` converted to Title Case

**Raw JSON:**
- Collapsible `<details>` section for full response inspection

**Key functions in app.js:**
- `renderResults(data)` - Main entry point
- `renderCPTTable(data)` - CPT codes table rendering
- `renderRegistrySummary(registry)` - Recursive registry field extraction

### Troubleshooting (0 detections / empty output)

If the UI returns **0 detections** on obvious PHI:

1. Re-export **unquantized** bundle:
   ```bash
   make export-phi-client-model
   ```
2. Confirm ONNX signature includes `attention_mask`:
   ```bash
   python scripts/check_onnx_inputs.py modules/api/static/phi_redactor/vendor/phi_distilbert_ner/onnx/model.onnx
   ```
   - If missing: the export is invalid for token-classification; re-export until `attention_mask` is present.
3. Run `/ui/phi_redactor/` with `forceUnquantized: true` and `debug: true`, then paste:
   ```
   Patient: John Doe. DOB: 01/01/1970. Phone: 555-123-4567.
   ```
4. Check browser console:
   - `[PHI] token preds label counts` proves whether the model is predicting **all `O`**.
   - If token list is empty, the worker logs a one-time `logits` sample to distinguish formatting vs inference failure.
5. Only after unquantized works, export quantized and test with `forceUnquantized: false`:
   ```bash
   make export-phi-client-model-quant
   ```
   If quantized collapses to all-`O`, keep unquantized.

> **DEPLOYMENT REQUIREMENT**: Post-veto must-not-redact audit violations **must be 0**.
> Raw model violations may be non-zero; the veto layer guarantees safety.

**Refinery:** drops common false positives (e.g., temps like `105C`, CPT codes in ZIPCODE).
**Label schema:** `--label-schema standard` maps Piiranha labels into `PATIENT/GEO/PROVIDER/...`.

**Platinum (Hybrid Redactor → char spans):** highest-precision, model-agnostic spans for both server and client training.

**Run:**
```bash
python scripts/build_model_agnostic_phi_spans.py --limit-notes 50
```
Or:
```bash
make build-phi-platinum
```

**Output:** `data/ml_training/phi_platinum_spans.jsonl`
**Note:** Platinum is the long-term source of truth; fix edge cases in the hybrid redactor, regenerate, and retrain both models.

**Optional sanitizer:** retroactive cleanup for platinum spans.
```bash
python scripts/sanitize_platinum_spans.py
```
**Output:** `data/ml_training/phi_platinum_spans_CLEANED.jsonl`
**Workflow:** build → optional sanitize → train (align char spans to tokenizer outputs).

### Platinum Apply (Golden JSONs → Training-Ready Scrubbed/Final)

Apply platinum spans back onto the Golden JSONs to produce PHI-safe registry training data:

```bash
make platinum-final      # platinum-cycle + institution cleanup

# (Equivalent step-by-step)
make platinum-build       # data/ml_training/phi_platinum_spans.jsonl
make platinum-sanitize    # data/ml_training/phi_platinum_spans_CLEANED.jsonl
make platinum-apply       # data/knowledge/golden_extractions_scrubbed/
python scripts/fix_registry_hallucinations.py \
  --input-dir data/knowledge/golden_extractions_scrubbed \
  --output-dir data/knowledge/golden_extractions_final
```

**Notes:**
- `scripts/apply_platinum_redactions.py` scrubs both `note_text` and `registry_entry.evidence`, standardizes all placeholders to `[REDACTED]`, and never redacts physician/provider names (e.g., `Dr. Green`).
- `scripts/fix_registry_hallucinations.py` cleans hallucinated/contaminated `registry_entry.institution_name` values (anatomy/date leakage) and writes a final cleaned dataset.
- `scripts/align_synthetic_names.py` is optional, but if you run it (it edits `note_text`), you must rebuild spans afterward (char offsets will change).

**Provider policy:** default is `drop` (name-like spans in provider contexts are removed).

**Shared safeguards (Silver + Platinum):**
- CPT false-positive suppression (token-level wipes vs span-level drops in CPT context).
- Temperature false-positive suppression (token-level wipes vs span-level drops).
- Provider suppression (doctors are not redacted by default).
- Protected clinical term veto (anatomy/device/allow-list, LN stations, segments).
- Address plausibility gate for GEO-like spans.
- Standard schema mapping for downstream alignment.

**Differences:** Silver applies tokenizer-aware subword wipes (CPT/LN stations) plus an optional post-hoc sanitizer, while Platinum applies equivalent span-level filters using line context with an optional span sanitizer for retroactive cleanup.

---

## 🚀 Implementation Roadmap

### Phase 1: Data Preparation (Local)

**Goal**: Build clean, leak-free, class-balanced training data from Golden JSON notes.

**Tasks:**

1. **Add/Update Golden JSONs** in `data/knowledge/golden_extractions/`
2. **Run `prepare_registry_training_splits()`** from `modules/ml_coder/data_prep.py`

**Output:**
- `data/ml_training/registry_train.csv`
- `data/ml_training/registry_val.csv`
- `data/ml_training/registry_test.csv`

---

### Phase 2: BiomedBERT Training (Local - Fast Track)

**Goal**: Train a high-performance deep learning model. This will likely be sufficient.

**Hardware/Environment:**
- **GPU**: RTX 4070 Ti (local)
- **Framework**: PyTorch with CUDA 11.8/12.1
- **Mixed Precision**: `fp16=True`

**Model Selection:**
- **Primary**: `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext` (#1 on BLURB benchmark)
- **Alternative**: `RoBERTa-large-PM-M3-Voc` for teacher-student distillation

**Key Training Features:**
- **Head + Tail Truncation**: Keeps first 382 + last 128 tokens (preserves complications at end)
- **pos_weight**: Upweights rare classes (capped at 100x)
- **Per-Class Threshold Optimization**: F1-optimal thresholds per label (not uniform 0.5)

**Training Script** (`scripts/train_roberta.py`):

```bash
python scripts/train_roberta.py --batch-size 16 --epochs 5
```

**Success Criteria:**
- Macro F1 Score > 0.90 on test set
- F1 > 0.85 on rare classes (BLVR, thermal ablation, cryotherapy)
- **If criteria met → SKIP Phase 3, proceed to Phase 4**

**Checklist:**
- [x] Configure PyTorch with CUDA
- [x] Implement `scripts/train_roberta.py` with Head+Tail truncation
- [x] Calculate `pos_weight` for class imbalance
- [x] Per-class threshold optimization
- [ ] Train model with fp16 mixed precision
- [ ] Evaluate Macro F1 on test set
- [ ] Evaluate F1 on rare classes specifically

---

### Phase 3: Teacher-Student Distillation (Cloud - CONDITIONAL)

> **Only execute if Phase 2 fails success criteria (Macro F1 ≤ 0.90 OR rare-class F1 ≤ 0.85)**

**Goal**: Use a larger model to "teach" the smaller model through knowledge distillation.

**Steps:**

1. **Rent Cloud GPU** (~1 hour)
   - Options: Lambda Labs, AWS (A10G), RunPod
   - Target: NVIDIA A10G or A100

2. **Train Teacher Model**
   - Model: `RoBERTa-large-PM-M3-Voc` (larger variant)
   - Fine-tune on augmented training data

3. **Generate Soft Labels**
   - Run trained Teacher on Training Data
   - Save output logits: `teacher_logits.pt`

4. **Retrain Student (Local)**
   - Return to RTX 4070 Ti
   - Loss function: `0.5 * GroundTruthLoss + 0.5 * TeacherDistillationLoss`

**Checklist:**
- [ ] Spin up cloud GPU (if needed)
- [ ] Train teacher model
- [ ] Export soft labels to `teacher_logits.pt`
- [ ] Retrain student with distillation loss

---

### Phase 4: Rules Engine (Deterministic Logic)

**Goal**: Derive CPT codes from Registry flags deterministically—no ML guessing for the final coding step.

**Location**: `data/rules/coding_rules.py`

**Implementation Pattern:**

```python
# data/rules/coding_rules.py

def rule_31652(registry: dict) -> bool:
    """EBUS-TBNA, 1-2 stations."""
    return (
        registry.get("linear_ebus", False) and 
        1 <= registry.get("stations_sampled", 0) <= 2
    )

def rule_31653(registry: dict) -> bool:
    """EBUS-TBNA, 3+ stations."""
    return (
        registry.get("linear_ebus", False) and 
        registry.get("stations_sampled", 0) >= 3
    )

def rule_31625(registry: dict) -> bool:
    """Bronchoscopy with transbronchial biopsy."""
    return registry.get("transbronchial_biopsy", False)

def rule_31627(registry: dict) -> bool:
    """Navigation add-on (requires primary procedure)."""
    return registry.get("navigation_used", False)

def derive_all_codes(registry: dict) -> list[str]:
    """Master function to derive all applicable CPT codes."""
    codes = []
    
    # EBUS (mutually exclusive)
    if rule_31653(registry):
        codes.append("31653")
    elif rule_31652(registry):
        codes.append("31652")
    
    # Biopsies
    if rule_31625(registry):
        codes.append("31625")
    
    # Add-ons (only if primary exists)
    if codes and rule_31627(registry):
        codes.append("31627")
    
    return codes
```

**Validation Process:**
1. Run all 5,000+ Golden Notes through the rules engine
2. Compare `Engine_CPT` vs. `Verified_CPT`
3. **Fix rules until 100% match on verified cases**

**Checklist:**
- [ ] Create `data/rules/coding_rules.py`
- [ ] Implement all CPT rule functions
- [ ] Create unit tests for each rule
- [ ] Validate against Golden Notes (target: 100% match)
- [ ] Document edge cases and exceptions

---

### Phase 5: Optimization & Deployment (Railway)

**Goal**: Deploy an optimized, cost-effective inference system on Railway Pro plan.

#### 5.1 Model Quantization (Local)

**Process:**
1. Convert trained PyTorch model (`.pt`) to **ONNX format**
2. Apply **INT8 quantization**

**Results:**
- Model size: ~350MB → ~80MB
- Inference speed: ~3x faster
- RAM usage: <500MB

**Script** (`scripts/quantize_to_onnx.py`):

```python
import torch
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType

# Export to ONNX
torch.onnx.export(model, dummy_input, "registry_model.onnx")

# INT8 Quantization
quantize_dynamic(
    "registry_model.onnx",
    "registry_model_int8.onnx",
    weight_type=QuantType.QUInt8
)
```

#### 5.2 ONNX Inference Service

**Location**: `modules/registry/inference_onnx.py`

```python
# modules/registry/inference_onnx.py
import onnxruntime as ort
import numpy as np

class ONNXRegistryPredictor:
    """Lightweight ONNX-based registry prediction."""
    
    def __init__(self, model_path: str = "models/registry_model_int8.onnx"):
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
    
    def predict(self, text: str) -> dict:
        """Run inference on procedure note text."""
        # Tokenize and run inference
        inputs = self._preprocess(text)
        outputs = self.session.run(None, inputs)
        return self._postprocess(outputs)
```

#### 5.3 Railway Deployment

**Benefits of INT8 Model:**
- RAM usage: <500MB (leaves room for app + overhead)
- No GPU required (CPU inference sufficient)
- Avoids Railway overage charges
- Response time: <100ms typical

**Checklist:**
- [ ] Export model to ONNX format
- [ ] Apply INT8 quantization
- [ ] Verify quantized model accuracy (should be ~same as original)
- [ ] Create `modules/registry/inference_onnx.py`
- [ ] Test locally with ONNX runtime
- [ ] Deploy to Railway
- [ ] Monitor RAM usage and response times

---

## Summary Checklist

| Phase | Task | Status |
|-------|------|--------|
| 1 | Add/update Golden JSONs → generate training CSVs | [ ] |
| 1 | Create leak-free, balanced train/val/test splits | [ ] |
| 2 | Train `microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext` on RTX 4070 Ti | [ ] |
| 2 | Achieve Macro F1 > 0.90 | [ ] |
| 3 | (Conditional) Teacher-student distillation | [ ] |
| 4 | Write deterministic CPT rule functions | [ ] |
| 4 | Validate rules against Golden Notes (100%) | [ ] |
| 5 | Convert model to ONNX INT8 | [ ] |
| 5 | Deploy to Railway | [ ] |

---

## Directory Structure

```
procedure-suite/
├── CLAUDE.md                          # THIS FILE - read first!
├── modules/
│   ├── api/
│   │   ├── fastapi_app.py             # Main FastAPI backend (NOT api/app.py!)
│   │   ├── readiness.py               # require_ready dependency for endpoints
│   │   ├── routes_registry.py         # Registry API routes
│   │   ├── static/phi_redactor/       # Client-side PHI redactor UI
│   │   │   ├── redactor.worker.js     # Hybrid ML+Regex detection worker
│   │   │   ├── protectedVeto.js       # Veto/allow-list layer
│   │   │   └── vendor/phi_distilbert_ner/  # ONNX model bundle
│   │   └── services/
│   │       └── qa_pipeline.py         # Parallelized QA pipeline
│   ├── infra/                         # Infrastructure & optimization
│   │   ├── settings.py                # Centralized env var configuration
│   │   ├── perf.py                    # timed() context manager for metrics
│   │   ├── cache.py                   # LRU cache with TTL (memory/Redis)
│   │   ├── executors.py               # run_cpu() async wrapper for threads
│   │   ├── llm_control.py             # LLM semaphore, backoff, retry logic
│   │   ├── safe_logging.py            # PHI-safe text hashing for logs
│   │   └── nlp_warmup.py              # NLP model warmup utilities
│   ├── llm/
│   │   └── client.py                  # Async HTTP client for LLM providers
│   ├── common/
│   │   ├── llm.py                     # Centralized LLM caching & retry
│   │   └── openai_responses.py        # OpenAI Responses API wrapper
│   ├── coder/
│   │   ├── application/
│   │   │   ├── coding_service.py      # CodingService - main entry point
│   │   │   └── smart_hybrid_policy.py # SmartHybridOrchestrator (with fallback)
│   │   ├── adapters/
│   │   │   ├── registry_coder.py      # Registry-based coder
│   │   │   └── llm/
│   │   │       ├── gemini_advisor.py  # Gemini LLM with cache/retry
│   │   │       └── openai_compat_advisor.py # OpenAI with cache/retry
│   │   └── domain/
│   ├── registry/
│   │   ├── application/
│   │   │   └── registry_service.py    # RegistryService - main entry point
│   │   ├── engine/
│   │   │   └── registry_engine.py     # LLM extraction logic
│   │   ├── inference_onnx.py          # ONNX inference service
│   │   └── ml/                        # Registry ML predictors
│   ├── agents/
│   │   ├── contracts.py               # Pydantic I/O schemas
│   │   ├── run_pipeline.py            # Pipeline orchestration (with timing)
│   │   ├── parser/                    # ParserAgent
│   │   ├── summarizer/                # SummarizerAgent
│   │   └── structurer/                # StructurerAgent
│   ├── ml_coder/
│   │   ├── data_prep.py               # Training data preparation (stratified splits)
│   │   ├── predictor.py               # ML predictor (with caching)
│   │   └── registry_predictor.py      # Registry boolean predictor
│   └── reporter/                      # Synoptic report generator
├── scripts/
│   ├── railway_start.sh               # Railway startup (uvicorn, no pre-warmup)
│   ├── railway_start_gunicorn.sh      # Alternative: Gunicorn prefork+preload
│   ├── warm_models.py                 # Pre-load NLP models (optional)
│   ├── smoke_run.sh                   # Local smoke test (/health, /ready)
│   ├── train_roberta.py               # RoBERTa training script
│   └── quantize_to_onnx.py            # ONNX conversion & quantization
├── data/
│   ├── knowledge/
│   │   ├── ip_coding_billing_v2_9.json  # CPT codes, RVUs, bundling rules
│   │   ├── IP_Registry.json             # Registry schema definition
│   │   └── golden_extractions/          # Training data
│   └── rules/
│       └── coding_rules.py            # Deterministic CPT derivation rules
├── docs/
│   └── optimization_12_16_25.md       # 8-phase optimization roadmap
├── models/
│   ├── registry_model.pt              # Trained PyTorch model
│   └── registry_model_int8.onnx       # Quantized ONNX model
├── schemas/
│   └── IP_Registry.json               # JSON Schema for validation
└── tests/
    ├── coder/
    ├── registry/
    ├── ml_coder/
    └── rules/                         # Rules engine tests
```

## Critical Development Rules

### 1. File Locations
- **ALWAYS** edit `modules/api/fastapi_app.py` — NOT `api/app.py` (deprecated)
- **ALWAYS** use `CodingService` from `modules/coder/application/coding_service.py`
- **ALWAYS** use `RegistryService` from `modules/registry/application/registry_service.py`
- Knowledge base is at `data/knowledge/ip_coding_billing_v2_9.json`
- Deterministic rules are at `data/rules/coding_rules.py`

### 2. Testing Requirements
- **ALWAYS** run `make test` before committing
- **ALWAYS** run `make preflight` for full validation
- Test commands:
  ```bash
  pytest tests/coder/ -v          # Coder tests
  pytest tests/registry/ -v       # Registry tests
  pytest tests/ml_coder/ -v       # ML coder tests
  pytest tests/rules/ -v          # Rules engine tests
  make validate-registry          # Registry extraction validation
  ```

### 3. Environment Variables

#### LLM Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | API key for Gemini LLM | Required for LLM |
| `GEMINI_OFFLINE` | Disable LLM calls (use stubs) | `1` |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry tests | `1` |
| `PROCSUITE_SKIP_DOTENV` | Skip loading `.env` in Python (tests/offline) | `1` |
| `OPENAI_API_KEY` | API key for OpenAI LLM | Required for OpenAI |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4.1` |
| `OPENAI_PRIMARY_API` | Primary API: `responses` or `chat` | `responses` |
| `OPENAI_RESPONSES_FALLBACK_TO_CHAT` | Fall back to Chat on 404 | `1` |
| `OPENAI_TIMEOUT_READ_REGISTRY_SECONDS` | Read timeout for registry tasks | `180` |
| `OPENAI_TIMEOUT_READ_DEFAULT_SECONDS` | Read timeout for default tasks | `60` |
| `OPENAI_OFFLINE` | Disable OpenAI calls (use stubs) | `0` |

#### Warmup & Startup (see `modules/infra/settings.py`)
| Variable | Description | Default |
|----------|-------------|---------|
| `SKIP_WARMUP` | Skip all model warmup at startup | `false` |
| `PROCSUITE_SKIP_WARMUP` | Alias for `SKIP_WARMUP` | `false` |
| `ENABLE_UMLS_LINKER` | Load UMLS linker (~1GB memory) | `true` |
| `WAIT_FOR_READY_S` | Seconds to wait for readiness before 503 | `0` |

#### Performance Tuning
| Variable | Description | Default |
|----------|-------------|---------|
| `CPU_WORKERS` | Thread pool size for CPU-bound work | `1` |
| `LLM_CONCURRENCY` | Max concurrent LLM requests (semaphore) | `2` |
| `LLM_TIMEOUT_S` | Max time for LLM calls before fallback | `60` |
| `LIMIT_CONCURRENCY` | Uvicorn connection limit | `50` |

#### Caching
| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_LLM_CACHE` | Cache LLM responses (memory) | `true` |
| `ENABLE_REDIS_CACHE` | Use Redis backend for caching | `false` |

#### Thread Limiting (Railway)
| Variable | Description | Default |
|----------|-------------|---------|
| `OMP_NUM_THREADS` | OpenMP threads (sklearn/ONNX) | `1` |
| `MKL_NUM_THREADS` | Intel MKL threads | `1` |
| `OPENBLAS_NUM_THREADS` | OpenBLAS threads | `1` |
| `NUMEXPR_NUM_THREADS` | NumExpr threads | `1` |

### 4. Contract-First Development
All agents use Pydantic contracts defined in `modules/agents/contracts.py`:
- **ALWAYS** define input/output contracts before implementing
- **ALWAYS** include `status: Literal["ok", "degraded", "failed"]`
- **ALWAYS** include `warnings: List[AgentWarning]` and `errors: List[AgentError]`
- **ALWAYS** include `trace: Trace` for debugging

### 5. Status Tracking Pattern
```python
class MyAgentOut(BaseModel):
    status: Literal["ok", "degraded", "failed"]
    warnings: List[AgentWarning]
    errors: List[AgentError]
    trace: Trace
    # ... other fields
```

Pipeline behavior:
- `ok` → Continue to next stage
- `degraded` → Continue with warning
- `failed` → Stop pipeline, return partial results

---

## CPT Coding Rules Reference

### EBUS Codes
| Code | Description | Registry Condition |
|------|-------------|-------------------|
| 31652 | EBUS-TBNA, 1-2 stations | `ebus.performed AND len(ebus.stations) in [1,2]` |
| 31653 | EBUS-TBNA, 3+ stations | `ebus.performed AND len(ebus.stations) >= 3` |

### Bronchoscopy Codes
| Code | Description | Registry Condition |
|------|-------------|-------------------|
| 31622 | Diagnostic bronchoscopy | `bronchoscopy.diagnostic AND NOT any_interventional` |
| 31623 | Bronchoscopy with brushing | `brushings.performed` |
| 31624 | Bronchoscopy with BAL | `bal.performed` |
| 31625 | Bronchoscopy with biopsy | `transbronchial_biopsy.performed` |
| 31627 | Navigation add-on | `navigation.performed` (add-on only) |

### Bundling Rules
- 31622 is bundled into any interventional procedure
- 31627 can only be billed with a primary procedure
- Multiple biopsies from same lobe = single code
- Check `data/knowledge/ip_coding_billing_v2_9.json` for NCCI/MER rules

---

## Agent Pipeline Reference

The 3-agent pipeline (`modules/agents/`) provides structured note processing:

```
Raw Text → Parser → Summarizer → Structurer → Registry + Codes
```

### ParserAgent
- **Input**: Raw procedure note text
- **Output**: Segmented sections (History, Procedure, Findings, etc.)
- **Location**: `modules/agents/parser/parser_agent.py`

### SummarizerAgent
- **Input**: Parsed segments
- **Output**: Section summaries and caveats
- **Location**: `modules/agents/summarizer/summarizer_agent.py`

### StructurerAgent
- **Input**: Summaries
- **Output**: Registry fields and CPT codes
- **Location**: `modules/agents/structurer/structurer_agent.py`

### Usage
```python
from modules.agents.run_pipeline import run_pipeline

result = run_pipeline({
    "note_id": "test_001",
    "raw_text": "History: 65yo male with lung nodule..."
})

print(result["registry"])  # Structured data
print(result["codes"])     # CPT codes
```

---

## Runtime Architecture (Railway Deployment)

The system uses a robust startup and concurrency pattern optimized for Railway's containerized environment.

### Liveness vs Readiness Pattern

```
/health (liveness)  → Always 200, fast response
/ready  (readiness) → 200 only after models loaded, else 503 + Retry-After
```

- Railway should probe `/health` for container health (liveness)
- Load balancers should use `/ready` before routing traffic
- Heavy endpoints use `require_ready` dependency to fail fast during warmup

### Application State (`app.state`)

| Field | Type | Description |
|-------|------|-------------|
| `model_ready` | `bool` | True when all models loaded |
| `model_error` | `Optional[str]` | Error message if warmup failed |
| `ready_event` | `asyncio.Event` | Signaled when ready |
| `cpu_executor` | `ThreadPoolExecutor` | For CPU-bound work |
| `llm_sem` | `asyncio.Semaphore` | Limits concurrent LLM calls |
| `llm_http` | `httpx.AsyncClient` | Shared HTTP client for LLM |

### CPU Offload Pattern

CPU-bound operations (sklearn, spaCy, ONNX) run in a thread pool to avoid blocking the async event loop:

```python
from modules.infra.executors import run_cpu

# In an async endpoint:
result = await run_cpu(app, model.predict, [note])
```

### LLM Concurrency Control

All LLM calls go through a semaphore to prevent rate limit spikes:

```python
from modules.infra.llm_control import llm_slot

async with llm_slot(app):
    response = await call_llm(prompt)
```

Features:
- Exponential backoff with jitter on 429/5xx
- Retry-After header parsing
- Cache key generation (PHI-safe, uses SHA256)

### Graceful Degradation

When LLM times out or fails:
1. ML + rules output is returned as fallback
2. Response includes `"degraded": true` flag
3. Logged with timing info (no PHI)

### Startup Scripts

| Script | Use Case |
|--------|----------|
| `scripts/railway_start.sh` | **Default**: Uvicorn, 1 worker, background warmup |
| `scripts/railway_start_gunicorn.sh` | Alternative: Gunicorn prefork+preload (higher RAM) |
| `scripts/smoke_run.sh` | Local testing: start server, hit /health, /ready |

---

## Testing Patterns

### Unit Test Pattern
```python
def test_ebus_three_stations_produces_31653():
    """Deterministic test: 3+ stations = 31653."""
    record = RegistryRecord(
        procedures=Procedures(
            ebus=EBUSRecord(
                performed=True,
                stations=["4R", "7", "11L"]
            )
        )
    )
    
    coder = RegistryBasedCoder()
    codes = coder.derive_codes(record)
    
    assert "31653" in [c["code"] for c in codes]
```

### Rules Engine Test Pattern
```python
def test_rule_31653():
    """Test EBUS 3+ stations rule."""
    registry = {
        "linear_ebus": True,
        "stations_sampled": 4
    }
    assert rule_31653(registry) is True
    
    registry["stations_sampled"] = 2
    assert rule_31653(registry) is False

def test_rule_31652():
    """Test EBUS 1-2 stations rule."""
    registry = {
        "linear_ebus": True,
        "stations_sampled": 2
    }
    assert rule_31652(registry) is True
```

### Integration Test Pattern
```python
def test_extraction_first_pipeline():
    """Full pipeline test: text → registry → codes."""
    note = """
    Procedure: EBUS bronchoscopy with TBNA of stations 4R, 7, and 11L.
    Findings: All stations showed benign lymphoid tissue.
    """
    
    service = RegistryService()
    result = service.extract_and_code(note)
    
    assert result.registry.procedures.ebus.performed is True
    assert len(result.registry.procedures.ebus.stations) == 3
    assert "31653" in [c["code"] for c in result.codes]
    assert result.confidence == "high"
```

---

## Development Workflow

### Before Starting Any Task
1. Read this CLAUDE.md file completely
2. Review the specific module documentation in `docs/`
3. Understand the extraction-first goal
4. Identify which phase the task belongs to

### Making Changes
1. Create a feature branch
2. Write tests first (TDD)
3. Implement the feature
4. Run `make test` — all tests must pass
5. Run `make preflight` — all checks must pass
6. Update relevant documentation

### Code Review Checklist
- [ ] Follows extraction-first architecture
- [ ] Uses Pydantic contracts
- [ ] Includes status tracking (ok/degraded/failed)
- [ ] Has comprehensive tests
- [ ] Updates CLAUDE.md if architecture changes

---

## Troubleshooting

### Common Issues

**LLM calls failing in tests:**
```bash
export GEMINI_OFFLINE=1
export REGISTRY_USE_STUB_LLM=1
```

**NLP models not loading:**
```bash
export SKIP_WARMUP=true
make install  # Reinstall spaCy models
```

**Import errors:**
```bash
micromamba activate medparse-py311
pip install -e .
```

**ONNX inference issues:**
```bash
pip install onnxruntime  # CPU-only runtime
# or
pip install onnxruntime-gpu  # If GPU available
```

**Railway OOM (Out of Memory):**
```bash
# Disable UMLS linker to save ~1GB
ENABLE_UMLS_LINKER=false

# Ensure thread limiting is set
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
```

**503 errors on first request:**
This is expected during warmup. The server returns `503 + Retry-After` while models load.
Wait for `/ready` to return 200 before sending traffic.

**LLM rate limiting (429 errors):**
The system handles this automatically with exponential backoff. To reduce 429s:
```bash
# Lower concurrent LLM requests
LLM_CONCURRENCY=1
```

**Run without any LLM calls (local workbench / debugging):**
- Registry endpoint: send `mode: "engine_only"` to `POST /v1/registry/run` to disable the registry LLM extractor (deterministic-only).
- Coder endpoint: send `mode: "rules_only"` to `POST /v1/coder/run` (ML-first) to disable LLM fallback (ML + rules only).
- PHI-gated unified extraction: send `mode: "engine_only"` to `POST /api/v1/procedures/{id}/extract` to disable registry LLM extraction.

The workbench UI exposes these as checkboxes in Unified/Coder/Registry mode (look for “Disable LLM…”).

**Registry V3 (granular) endpoints and tooling:**
- Offline pipeline harness:
  - `python scripts/ingest_phase0_data.py` → writes `data/knowledge/golden_registry_v3/*.json`
  - `python scripts/eval_registry_granular.py` → runs V3 pipeline evaluation (set `REGISTRY_USE_STUB_LLM=1` for offline)
- API: `POST /v1/registry/v3/run` runs V3 extraction and projects back to the legacy `RegistryRecord` response shape.

**Slow cold starts:**
Check that background warmup is working:
1. `/health` should return immediately with `"ready": false`
2. `/ready` should return 503 during warmup
3. After warmup, `/ready` returns 200

**Dev server fails with MODEL_BACKEND=onnx missing registry model:**
```
missing registry model at data/models/registry_runtime/registry_model_int8.onnx
```
Solutions:
- Set `MODEL_BACKEND` to a non-onnx mode for local UI work, or
- Copy `data/models/registry_runtime/` from your GPU machine

**PHI UI shows "Failed to fetch" for tokenizer/config/model files:**
- Ensure FastAPI serves `/ui/phi_redactor/vendor/...` as static files
- Ensure CORS allows worker fetches (Origin `null` can happen in Web Workers)
- Check browser DevTools Network tab for 404s or CORS errors

---

## Contact & Resources

- **Knowledge Base**: `data/knowledge/ip_coding_billing_v2_9.json`
- **Registry Schema**: `schemas/IP_Registry.json`
- **API Docs**: `docs/Registry_API.md`
- **CPT Reference**: `docs/REFERENCES.md`
- **Rules Engine**: `data/rules/coding_rules.py`
- **Optimization Roadmap**: `docs/optimization_12_16_25.md`
- **Settings Reference**: `modules/infra/settings.py`
- **PHI Redactor Worker**: `modules/api/static/phi_redactor/redactor.worker.js`
- **PHI Veto Layer**: `modules/api/static/phi_redactor/protectedVeto.js`

---

*Last updated: January 2026*
*Architecture: Extraction-First with RoBERTa ML + Deterministic Rules Engine*
*Runtime: Async FastAPI + ThreadPool CPU offload + LLM concurrency control*
*Deployment Target: Railway (ONNX INT8, Uvicorn single-worker)*
*PHI Redactor: Hybrid ML+Regex detection with veto layer + Prodigy iterative correction*
