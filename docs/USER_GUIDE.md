# Procedure Suite - User Guide

This guide explains how to use the Procedure Suite tools for generating reports, coding procedures, and validating registry data.

---

## How the System Works (Plain Language)

The Procedure Suite is an intelligent medical coding assistant that reads procedure notes and suggests appropriate CPT billing codes. Here's how it works in simple terms:

### The Three Brains

1. **Machine Learning (ML) Model**: A trained neural network that has learned from thousands of procedure notes. It quickly predicts which CPT codes are likely correct and assigns a confidence score to each prediction.

2. **Rules Engine**: A set of explicit business rules that encode medical billing knowledge, such as:
   - "You can't bill these two codes together" (bundling rules)
   - "This code requires specific documentation" (validation rules)
   - "If procedure X was done, code Y is required" (inference rules)

3. **LLM Advisor**: A large language model (like GPT/Gemini) that can read and understand procedure notes in natural language. It acts as a "second opinion" when the ML model is uncertain.

### The ML-First Hybrid Pipeline (NEW)

The system uses a smart decision-making process called the **SmartHybridOrchestrator**:

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
./scripts/devserver.sh
```
*Starts the server on port 8000.*

- **Web UI**: [http://localhost:8000/ui/](http://localhost:8000/ui/)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

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
python scripts/evaluate_cpt.py
```
*Output*: Accuracy metrics and error logs in `data/cpt_errors.jsonl`.

### 3. Self-Correction (LLM)
Ask the LLM to analyze specific registry fields or errors and suggest improvements.

```bash
# Analyze errors for a specific field
make self-correct-registry FIELD=sedation_type
```
*Output*: `reports/registry_self_correction_sedation_type.md`

### 4. Clean & Normalize Registry
Run the full cleaning pipeline (Schema Norm -> CPT Logic -> Consistency -> Clinical QC) on a raw dataset.

```bash
python scripts/clean_ip_registry.py \
  --registry-data data/samples/my_registry_dump.jsonl \
  --output-json reports/cleaned_registry_data.json \
  --issues-log reports/issues_log.csv
```

---

## 🔌 API Usage

You can interact with the system programmatically via the REST API.

### CPT Coding Endpoint
**POST** `/v1/coder/run`

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
**POST** `/v1/registry/run`

Input:
```json
{
  "note": "Patient is a 65yo male..."
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

## 📊 Key Files

- **`data/knowledge/ip_coding_billing_v2_9.json`**: The "Brain". Contains all CPT codes, RVUs, and bundling rules.
- **`schemas/IP_Registry.json`**: The "Law". Defines the valid structure for registry data.
- **`reports/`**: Where output logs and validation summaries are saved.

---

## 🖥️ Using the Web UI (Unicorn Frontend)

The Web UI provides a simple interface for coding procedure notes.

### Basic Usage

1. **Start the server**: `./scripts/devserver.sh`
2. **Open the UI**: Navigate to [http://localhost:8000/ui/](http://localhost:8000/ui/)
3. **Select "Coder" tab** (default)
4. **Paste your procedure note** into the text area
5. **Configure options**:
   - **Use ML-First Pipeline** (recommended): Enables the smart hybrid pipeline
   - **Locality**: Geographic code for RVU calculations (default: 00 = National)
   - **Setting**: Facility or Non-Facility pricing
6. **Click "Run Processing"**

### Understanding the Results

When using the ML-First Pipeline, you'll see:

- **Pipeline Metadata** (colored badges):
  - **Difficulty**: green (high_confidence), yellow (gray_zone), red (low_confidence)
  - **Source**: green (ml_rules_fastpath) means no LLM was used, blue (hybrid_llm_fallback) means LLM was consulted
  - **LLM Used**: green (No) or yellow (Yes)

- **Billing Codes**: The final CPT codes with descriptions

- **RVU & Payment**: Work RVUs and estimated Medicare payment

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
python scripts/train_roberta.py \
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

#### 5) Annotate in Prodigy (checkbox UI)

```bash
make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_v1
```

Notes:
- The annotation UI is served at `http://localhost:8080` (Prodigy’s default).
- This workflow uses **`textcat.manual`** (multi-label checkboxes via `cats`), not NER. If you see “Using 30 label(s): …” you’re in the right place.

##### Working across machines (Google Drive sync — safe “export/import”)

Do **not** cloud-sync the raw Prodigy SQLite DB file (risk of corruption). Instead, sync by exporting/importing a JSONL snapshot to a shared Google Drive folder.

Pick a single “source of truth” folder in Google Drive, e.g. `proc_suite_sync/`, and keep these inside it:
- `prodigy/registry_v1.prodigy.jsonl` (the Prodigy dataset snapshot)
- `diamond_loop/registry_prodigy_manifest.json` (recommended: avoids re-sampling across machines)
- `diamond_loop/registry_unlabeled_notes.jsonl` (recommended: consistent sampling universe)

###### Recommended: one-command Diamond Loop sync

Use `scripts/diamond_loop_cloud_sync.py` to sync the dataset snapshot + key Diamond Loop files.

**WSL + Google Drive on Windows `G:` (your setup):**

```bash
# Pull latest from Drive before annotating on this machine
python scripts/diamond_loop_cloud_sync.py pull \
  --dataset registry_v1 \
  --gdrive-win-root "G:\\My Drive\\proc_suite_sync" \
  --reset

# Push back to Drive after finishing a session
python scripts/diamond_loop_cloud_sync.py push \
  --dataset registry_v1 \
  --gdrive-win-root "G:\\My Drive\\proc_suite_sync"
```

**macOS (Drive path varies by install):**

```bash
python scripts/diamond_loop_cloud_sync.py pull \
  --dataset registry_v1 \
  --sync-root "/path/to/GoogleDrive/proc_suite_sync" \
  --reset

python scripts/diamond_loop_cloud_sync.py push \
  --dataset registry_v1 \
  --sync-root "/path/to/GoogleDrive/proc_suite_sync"
```

Optional flags:
- Add `--include-batch` to also sync `data/ml_training/registry_prodigy_batch.jsonl` (resume the exact same batch on another machine)
- Add `--include-human` to also sync `data/ml_training/registry_human.csv`

###### Manual fallback: dataset-only export/import

If you prefer to sync just the Prodigy dataset snapshot file, you can use `scripts/prodigy_cloud_sync.py` directly.

**Before you start annotating on a machine** (pull latest from Drive):

```bash
python scripts/prodigy_cloud_sync.py import \
  --dataset registry_v1 \
  --in "/path/to/GoogleDrive/proc_suite_sync/prodigy/registry_v1.prodigy.jsonl" \
  --reset
```

**After you finish a session** (push to Drive):

```bash
python scripts/prodigy_cloud_sync.py export \
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

```bash
make registry-prodigy-export \
  REG_PRODIGY_DATASET=registry_v1 \
  REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human.csv
```

#### 7) Merge human labels as Tier-0 and rebuild splits (no leakage)

This is critical: merge **before splitting**.

```bash
make registry-prep-with-human HUMAN_REGISTRY_CSV=data/ml_training/registry_human.csv
```

#### 8) Retrain for real (3–5 epochs)

```bash
python scripts/train_roberta.py \
  --train-csv data/ml_training/registry_train.csv \
  --val-csv data/ml_training/registry_val.csv \
  --test-csv data/ml_training/registry_test.csv \
  --output-dir data/models/roberta_registry \
  --epochs 5
```

#### 9) Repeat the Diamond Loop

Repeat steps **4 → 8** until disagreement rate drops and metrics plateau.

Notes:
- Canonical label schema/order is `modules/ml_coder/registry_label_schema.py`.
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
python scripts/validate_training_data.py data/training/my_new_cases.jsonl
```

#### Step 4: Retrain the Model (Optional)

If you have enough new cases (50+), you can retrain the ML model:

```bash
# Run the training pipeline
python scripts/train_ml_coder.py --include data/training/my_new_cases.jsonl
```

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
python scripts/review_llm_fallback_errors.py --mode all

# Review only fast path errors (ML+Rules mistakes)
python scripts/review_llm_fallback_errors.py --mode fastpath

# Review only LLM fallback errors
python scripts/review_llm_fallback_errors.py --mode llm_fallback
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

The ML model's confidence thresholds can be tuned in `modules/ml_coder/thresholds.py`:

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
python scripts/phi_audit.py --note-path test_redact.txt
```

### Scrubbing Golden JSON Files

Scrub PHI from golden extraction files:

```bash
python scripts/scrub_golden_jsons.py \
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
python scripts/fix_registry_hallucinations.py \
  --input-dir data/knowledge/golden_extractions_scrubbed \
  --output-dir data/knowledge/golden_extractions_final
```

**Optional: align synthetic names before building spans**
```bash
python scripts/align_synthetic_names.py \
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
python scripts/train_distilbert_ner.py \
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

2. **Client-side location** (ONNX format): `modules/api/static/phi_redactor/vendor/phi_distilbert_ner/`
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
cd scripts/phi_test_node
node test_phi_redaction.mjs --count 30
```

### Server Configuration for PHI

Start the dev server with different model backends:

```bash
# Use PyTorch backend (for PHI without registry ONNX)
MODEL_BACKEND=pytorch ./scripts/devserver.sh

# Auto-detect best backend
MODEL_BACKEND=auto ./scripts/devserver.sh
```
http://localhost:8000/ui/phi_redactor/
---

## 📞 Getting Help

- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Technical Issues**: Check the logs in `logs/` directory
- **Questions**: Open an issue on the repository

---

*Last updated: December 2025*
