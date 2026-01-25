# Makefile Commands Reference

This document provides a comprehensive reference for all available `make` commands in the Procedure Suite project.

## Table of Contents

- [Setup & Development](#setup--development)
- [Code Quality](#code-quality)
- [Validation](#validation)
- [PHI (Protected Health Information)](#phi-protected-health-information)
  - [Data Preparation](#data-preparation)
  - [Model Training & Evaluation](#model-training--evaluation)
  - [Model Export](#model-export)
  - [Prodigy Workflow](#prodigy-workflow)
- [Registry & Coding](#registry--coding)
- [Development Server](#development-server)
- [Utilities](#utilities)

---

## Setup & Development

### `make setup`
**Description**: Install project dependencies in the conda environment.

**What it does**:
- Installs packages from `requirements.txt` into the `medparse-py311` conda environment
- Creates a `.setup.stamp` file to track completion
- Skips re-installation if already completed

**Usage**:
```bash
make setup
```

---

## Code Quality

### `make lint`
**Description**: Run the Ruff linter to check code style and quality.

**What it does**:
- Runs `ruff check` on the entire codebase
- Uses `.ruff_cache` for caching

**Usage**:
```bash
make lint
```

### `make typecheck`
**Description**: Run MyPy type checker to validate type annotations.

**What it does**:
- Runs `mypy` on the codebase
- Uses `.mypy_cache` for caching

**Usage**:
```bash
make typecheck
```

### `make test`
**Description**: Run the test suite using pytest.

**What it does**:
- Executes all tests in the project
- Uses pytest for test discovery and execution

**Usage**:
```bash
make test
```
- To create a text file with make test output run
```bash
make test 2>&1 | tee test_output_$(date +%Y%m%d_%H%M%S).txt

---
#mac make test
set -a; source .env; set +a; make test
set -a; source .env; set +a; make test 2>&1 | tee test_output_$(date +%Y%m%d_%H%M%S).txt


## Validation

### `make validate-schemas`
**Description**: Validate JSON schemas and Pydantic models.

**What it does**:
- Validates the knowledge base schema (`data/knowledge/IP_Registry.json`)
- Checks Pydantic models for correctness
- Continues even if schema validation fails (for development)

**Usage**:
```bash
make validate-schemas
```

### `make validate-kb`
**Description**: Validate the knowledge base JSON file.

**What it does**:
- Checks that `data/knowledge/ip_coding_billing_v3_0.json` is valid JSON
- Prints confirmation message on success

**Usage**:
```bash
make validate-kb
```

### `make validate-knowledge-release`
**Description**: Validate KB + schema integration (no external network calls).

**What it does**:
- Loads the KB via both the lightweight JSON loader and the main KB adapter
- Builds/validates the dynamic `RegistryRecord` model from `data/knowledge/IP_Registry.json`
- Runs a no-op extraction in the `parallel_ner` pathway to catch runtime/import regressions
- Runs deterministic Registry → CPT derivation (should not crash)

**Usage**:
```bash
make validate-knowledge-release
```

### `make knowledge-diff`
**Description**: Generate a diff report between two KB JSON files.

**What it does**:
- Reports codes added/removed in `master_code_index`
- Reports descriptor / RVU changes for overlapping codes
- Reports add-on code list changes

**Usage**:
```bash
make knowledge-diff OLD_KB=path/to/old_kb.json NEW_KB=data/knowledge/ip_coding_billing_v3_0.json
```

---

## PHI (Protected Health Information)

### Data Preparation

#### `make distill-phi`
**Description**: Distill PHI labels from golden extractions using a teacher model.

**What it does**:
- Uses Piiranha teacher model to generate PHI labels
- Processes notes from `data/knowledge/golden_extractions`
- Outputs to `data/ml_training/distilled_phi_labels.jsonl`
- Runs on CPU

**Usage**:
```bash
make distill-phi
```

#### `make distill-phi-silver`
**Description**: Distill PHI labels with standard label schema.

**What it does**:
- Similar to `distill-phi` but uses standard label schema
- Uses device specified by `DEVICE` variable (default: `cpu`)
- Can use GPU if available

**Usage**:
```bash
make distill-phi-silver
# Or with GPU:
DEVICE=cuda make distill-phi-silver
```

#### `make sanitize-phi-silver`
**Description**: Clean and sanitize distilled PHI labels.

**What it does**:
- Removes invalid or problematic labels from the dataset
- Input: `data/ml_training/distilled_phi_labels.jsonl`
- Output: `data/ml_training/distilled_phi_CLEANED.jsonl`

**Usage**:
```bash
make sanitize-phi-silver
```

#### `make normalize-phi-silver`
**Description**: Normalize PHI labels to a stable schema.

**What it does**:
- Standardizes label names and formats
- Applies password policy (maps passwords to ID labels)
- Input: `data/ml_training/distilled_phi_CLEANED.jsonl`
- Output: `data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl`

**Usage**:
```bash
make normalize-phi-silver
```

#### `make build-phi-platinum`
**Description**: Build hybrid redactor PHI spans from golden extractions.

**What it does**:
- Creates model-agnostic PHI span annotations
- Processes golden extraction files
- Outputs to `data/ml_training/phi_platinum_spans.jsonl`

**Usage**:
```bash
make build-phi-platinum
```

### Model Training & Evaluation

#### `make eval-phi-client`
**Description**: Evaluate the DistilBERT NER model without retraining.

**What it does**:
- Loads model from `artifacts/phi_distilbert_ner`
- Evaluates on `data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl`
- Generates evaluation metrics
- Does not modify the model

**Usage**:
```bash
make eval-phi-client
```

#### `make audit-phi-client`
**Description**: Run false-positive audit to find model mistakes.

**What it does**:
- Analyzes model predictions for false positives
- Checks for violations (dangling entities, numeric codes in CPT context, etc.)
- Processes up to 5000 records
- Generates audit report at `artifacts/phi_distilbert_ner/audit_report.json`

**Usage**:
```bash
make audit-phi-client
```

#### `make patch-phi-client-hardneg`
**Description**: Create hard negative training data from audit violations.

**What it does**:
- Reads audit report from `artifacts/phi_distilbert_ner/audit_report.json`
- Patches training data by converting false positives to "O" labels
- Input: `data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl`
- Output: `data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl`

**Usage**:
```bash
make patch-phi-client-hardneg
```

#### `make finetune-phi-client-hardneg`
**Description**: Fine-tune model on hard negative examples (recommended for Apple Silicon).

**What it does**:
- Resumes from `artifacts/phi_distilbert_ner`
- Trains on hard negative patched data
- Uses MPS (Metal) with memory optimizations:
  - Gradient accumulation (2 steps)
  - Small batch sizes (train: 4, eval: 16)
  - Removes MPS memory limits
- 1 epoch with low learning rate (1e-5)

**Usage**:
```bash
make finetune-phi-client-hardneg
```

#### `make finetune-phi-client-hardneg-cpu`
**Description**: Fine-tune on hard negatives using CPU (slower but reliable fallback).

**What it does**:
- Same as `finetune-phi-client-hardneg` but forces CPU mode
- Larger batch size (train: 8) since CPU doesn't have memory constraints
- Takes ~5-6 hours for 1 epoch
- Use if MPS runs out of memory

**Usage**:
```bash
make finetune-phi-client-hardneg-cpu
```

### Model Export

#### `make export-phi-client-model`
**Description**: Export PyTorch model to ONNX format for client-side use.

**What it does**:
- Converts model from `artifacts/phi_distilbert_ner` (PyTorch)
- Exports to `modules/api/static/phi_redactor/vendor/phi_distilbert_ner` (ONNX)
- Includes tokenizer, config, and label mappings
- Creates unquantized ONNX model

**Usage**:
```bash
make export-phi-client-model
```

**Note**: Run this after training to update the UI model at `/ui/phi_redactor/`

#### `make export-phi-client-model-quant`
**Description**: Export quantized ONNX model (smaller file size).

**What it does**:
- Same as `export-phi-client-model` but creates INT8 quantized model
- Smaller file size but may have accuracy trade-offs
- Useful for deployment with bandwidth constraints

**Usage**:
```bash
make export-phi-client-model-quant
```

### Prodigy Workflow

The Prodigy workflow is used for iterative PHI model improvement through manual annotation.

#### `make prodigy-prepare`
**Description**: Prepare a batch of notes for Prodigy annotation.

**What it does**:
- Samples notes that need annotation/correction
- Uses model predictions to identify uncertain cases
- Outputs to `data/ml_training/prodigy_batch.jsonl`
- Default count: 100 (override with `PRODIGY_COUNT=200`)

**Usage**:
```bash
make prodigy-prepare
# Or with custom count:
PRODIGY_COUNT=200 make prodigy-prepare
```

#### `make prodigy-prepare-file`
**Description**: Prepare batch from a specific input file.

**What it does**:
- Same as `prodigy-prepare` but uses a specific input file
- Default input: `synthetic_phi.jsonl`
- Override with `PRODIGY_INPUT_FILE=your_file.jsonl`

**Usage**:
```bash
make prodigy-prepare-file
# Or with custom file:
PRODIGY_INPUT_FILE=my_notes.jsonl make prodigy-prepare-file
```

#### `make prodigy-annotate`
**Description**: Launch Prodigy annotation UI.

**What it does**:
- Starts Prodigy web interface for manual annotation
- Uses dataset name from `PRODIGY_DATASET` (default: `phi_corrections`)
- Labels: PATIENT, DATE, ID, GEO, CONTACT
- Reads from `data/ml_training/prodigy_batch.jsonl`

**Usage**:
```bash
make prodigy-annotate
# Or with custom dataset:
PRODIGY_DATASET=my_corrections make prodigy-annotate
```

#### `make prodigy-export`
**Description**: Export Prodigy annotations to training format.

**What it does**:
- Exports corrections from Prodigy dataset
- Merges with base dataset (`distilled_phi_CLEANED_STANDARD.jsonl`)
- Outputs to `data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl`
- Converts annotations to token-level BIO tags

**Usage**:
```bash
make prodigy-export
```

#### `make prodigy-retrain`
**Description**: Train model from scratch on corrected data.

**What it does**:
- Trains new model (does not resume from existing)
- Uses `distilled_phi_WITH_CORRECTIONS.jsonl`
- 3 epochs
- Auto-detects Metal/CUDA
- Removes MPS memory limits

**Usage**:
```bash
make prodigy-retrain
```

#### `make prodigy-finetune`
**Description**: Fine-tune existing model on corrected data (recommended).

**What it does**:
- Resumes from `artifacts/phi_distilbert_ner` (preserves learned weights)
- Trains on `distilled_phi_WITH_CORRECTIONS.jsonl`
- 1 epoch by default (override with `PRODIGY_EPOCHS=3`)
- Low learning rate (1e-5) to avoid catastrophic forgetting
- Auto-detects Metal/CUDA
- Removes MPS memory limits

**Usage**:
```bash
make prodigy-finetune
# Or with more epochs:
PRODIGY_EPOCHS=3 make prodigy-finetune
```

#### `make prodigy-cycle`
**Description**: Full Prodigy iteration workflow (prepares batch only).

**What it does**:
- Runs `prodigy-prepare` to create annotation batch
- Prints instructions for next steps

**Usage**:
```bash
make prodigy-cycle
```

**Typical workflow**:
```bash
make prodigy-cycle              # Prepare batch
make prodigy-annotate           # Annotate in UI
make prodigy-export             # Export corrections
make prodigy-finetune           # Fine-tune model
make export-phi-client-model    # Update UI model
```

---

## Registry & Coding

### `make run-coder`
**Description**: Run the smart-hybrid coder over notes.

**What it does**:
- Processes notes using hybrid coding approach (ML + keyword matching)
- Input: `data/knowledge/synthetic_notes_with_registry2.json`
- Knowledge base: `data/knowledge/ip_coding_billing_v3_0.json`
- Output: `outputs/coder_suggestions.jsonl`

**Usage**:
```bash
make run-coder
```

### `make registry-prep`
**Description**: Build registry-first ML training splits from golden JSONs.

**What it does**:
- Converts `golden_*.json` files into multi-label CSV splits
- Uses 3-tier hydration for labels (structured → CPT → keyword)
- Writes:
  - `data/ml_training/registry_train.csv`
  - `data/ml_training/registry_val.csv`
  - `data/ml_training/registry_test.csv`

**Usage**:
```bash
make registry-prep
make registry-prep-final   # recommended (PHI-scrubbed)
make registry-prep-raw     # raw golden_extractions
make registry-prep-dry     # validate only (no writes)
```

### `make registry-prep-with-human`
**Description**: Registry prep + Tier-0 merge of human labels (Diamond Loop).

**What it does**:
- Loads a human-labeled CSV (from Prodigy export) and merges it as **Tier-0**
  (`human > structured > cpt > keyword`)
- Deduplicates before splitting to avoid leakage

**Usage**:
```bash
make registry-prep-with-human HUMAN_REGISTRY_CSV=data/ml_training/registry_human.csv
```

### `make registry-prodigy-prepare`
**Description**: Prepare a Prodigy `choice` batch for registry procedure flags (Diamond Loop).

**What it does**:
- Generates a Prodigy JSONL with checkbox options for all canonical labels
- Pre-checks boxes using model + deterministic/CPT signals
- Tracks a manifest to avoid re-sampling the same note

**Usage**:
```bash
make registry-prodigy-prepare REG_PRODIGY_COUNT=200 REG_PRODIGY_INPUT_FILE=data/ml_training/registry_unlabeled_notes.jsonl
```

### `make registry-prodigy-annotate`
**Description**: Launch Prodigy UI for registry multi-label annotation.

**Usage**:
```bash
make registry-prodigy-annotate REG_PRODIGY_DATASET=registry_v1
```

### `make registry-prodigy-export`
**Description**: Export Prodigy registry annotations to a training CSV.

**Usage**:
```bash
make registry-prodigy-export REG_PRODIGY_DATASET=registry_v1 REG_PRODIGY_EXPORT_CSV=data/ml_training/registry_human.csv
```

### Legacy Registry Prodigy targets
The Makefile also includes legacy targets that follow the same general flow:
- `make prodigy-prepare-registry`
- `make prodigy-annotate-registry`
- `make prodigy-export-registry`
- `make prodigy-merge-registry`
- `make prodigy-retrain-registry`

### `make codex-train`
**Description**: Run full training pipeline (CI-like flow).

**What it does**:
- Runs multiple targets in sequence:
  1. `setup` - Install dependencies
  2. `lint` - Code quality checks
  3. `typecheck` - Type validation
  4. `test` - Run tests
  5. `validate-schemas` - Schema validation
  6. `validate-kb` - Knowledge base validation
  7. `autopatch` - Generate patches

**Usage**:
```bash
make codex-train
```

### `make codex-metrics`
**Description**: Run metrics over a batch of notes.

**What it does**:
- Runs coding pipeline and generates metrics
- Outputs to `outputs/metrics_run.jsonl`
- Measures coding accuracy and performance

**Usage**:
```bash
make codex-metrics
```

### `make autopatch`
**Description**: Generate patches for registry cleaning.

**What it does**:
- Runs cleaning pipeline on notes
- Generates patches in `autopatches/patches.json`
- Creates error report in `reports/errors.csv`
- Applies minimal fixes automatically

**Usage**:
```bash
make autopatch
```

### `make autocommit`
**Description**: Automatically commit generated files.

**What it does**:
- Stages all changes with `git add .`
- Commits with message "Autocommit: generated patches/reports"
- Continues even if commit fails (for development)

**Usage**:
```bash
make autocommit
```

---

## Development Server

### `make dev-iu`
**Description**: Start the development server with hot-reload.

**What it does**:
- Starts FastAPI server with uvicorn
- Enables hot-reload (auto-restarts on code changes)
- Uses port from `PORT` variable (default: 8000)
- Sets `MODEL_BACKEND`, `REGISTRY_RUNTIME_DIR`, `PROCSUITE_SKIP_WARMUP`

**Usage**:
```bash
make dev-iu
# Or with custom port:
PORT=8080 make dev-iu
```

**Environment variables**:
- `PORT` - Server port (default: 8000)
- `MODEL_BACKEND` - Model backend: `pytorch`, `onnx`, or `auto` (default: `pytorch`)
- `REGISTRY_RUNTIME_DIR` - Registry model directory (default: `data/models/registry_runtime`)
- `PROCSUITE_SKIP_WARMUP` - Skip model warmup (default: `1`)

### `make pull-model-pytorch`
**Description**: Download PyTorch model bundle from S3.

**What it does**:
- Downloads registry model from S3
- Uses `MODEL_BUNDLE_S3_URI_PYTORCH` environment variable
- Saves to `REGISTRY_RUNTIME_DIR` (default: `data/models/registry_runtime`)

**Usage**:
```bash
MODEL_BUNDLE_S3_URI_PYTORCH="s3://..." make pull-model-pytorch
```

---

## Utilities

### `make clean`
**Description**: Remove generated files and caches.

**What it does**:
- Removes setup stamp file
- Cleans cache directories (`.ruff_cache`, `.mypy_cache`, `.pytest_cache`)
- Removes `outputs`, `autopatches`, and `reports` directories
- Removes all `__pycache__` directories

**Usage**:
```bash
make clean
```

### `make help`
**Description**: Display list of available make targets.

**What it does**:
- Prints all available targets with brief descriptions

**Usage**:
```bash
make help
```

---

## Common Workflows

### Initial Setup
```bash
make setup
make validate-kb
```

### PHI Model Training (Full Pipeline)
```bash
# 1. Prepare data
make distill-phi-silver
make sanitize-phi-silver
make normalize-phi-silver

# 2. Train initial model (if needed)
# (Use train_distilbert_ner.py directly or see USER_GUIDE.md)

# 3. Evaluate and audit
make eval-phi-client
make audit-phi-client

# 4. Fine-tune on hard negatives
make patch-phi-client-hardneg
make finetune-phi-client-hardneg

# 5. Export for UI
make export-phi-client-model
```

### Prodigy Iterative Improvement
```bash
# 1. Prepare annotation batch
make prodigy-prepare

# 2. Annotate in Prodigy UI
make prodigy-annotate

# 3. Export corrections
make prodigy-export

# 4. Fine-tune model
make prodigy-finetune

# 5. Update UI model
make export-phi-client-model
```

### Code Quality Check
```bash
make lint
make typecheck
make test
make validate-schemas
```

---

## Environment Variables

Many make targets can be customized using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port for `dev-iu` |
| `MODEL_BACKEND` | `pytorch` | Model backend (`pytorch`, `onnx`, `auto`) |
| `PROCSUITE_SKIP_WARMUP` | `1` | Skip model warmup on startup |
| `REGISTRY_RUNTIME_DIR` | `data/models/registry_runtime` | Registry model directory |
| `DEVICE` | `cpu` | Device for training (`cpu`, `cuda`, `mps`) |
| `PRODIGY_COUNT` | `100` | Number of examples for Prodigy batch |
| `PRODIGY_DATASET` | `phi_corrections` | Prodigy dataset name |
| `PRODIGY_INPUT_FILE` | `synthetic_phi.jsonl` | Input file for `prodigy-prepare-file` |
| `PRODIGY_EPOCHS` | `1` | Number of epochs for `prodigy-finetune` |
| `REGISTRY_INPUT_DIR` | `data/knowledge/golden_extractions_final` | Golden registry inputs for `registry-prep` |
| `REGISTRY_OUTPUT_DIR` | `data/ml_training` | Output dir for registry CSV splits |
| `REGISTRY_PREFIX` | `registry` | Output filename prefix |
| `REGISTRY_MIN_LABEL_COUNT` | `5` | Min positives to keep a label |
| `REGISTRY_SEED` | `42` | Registry split RNG seed |
| `HUMAN_REGISTRY_CSV` | *(none)* | Human labels CSV for `registry-prep-with-human` |
| `REG_PRODIGY_COUNT` | `200` | Registry Prodigy batch size |
| `REG_PRODIGY_DATASET` | `registry_v1` | Registry Prodigy dataset name |
| `REG_PRODIGY_INPUT_FILE` | `data/ml_training/registry_unlabeled_notes.jsonl` | Unlabeled notes JSONL for registry Prodigy |
| `REG_PRODIGY_BATCH_FILE` | `data/ml_training/registry_prodigy_batch.jsonl` | Output Prodigy batch JSONL |
| `REG_PRODIGY_MANIFEST` | `data/ml_training/registry_prodigy_manifest.json` | Registry Prodigy manifest (dedup) |
| `REG_PRODIGY_MODEL_DIR` | `data/models/registry_runtime` | Optional registry runtime dir for prefill |
| `REG_PRODIGY_EXPORT_CSV` | `data/ml_training/registry_human.csv` | Exported human labels CSV |

---

*Last updated: December 2025*
