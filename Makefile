SHELL := /bin/bash
.PHONY: setup lint typecheck test validate-schemas validate-kb autopatch autocommit codex-train codex-metrics run-coder distill-phi distill-phi-silver sanitize-phi-silver normalize-phi-silver build-phi-platinum eval-phi-client audit-phi-client patch-phi-client-hardneg finetune-phi-client-hardneg finetune-phi-client-hardneg-cpu export-phi-client-model export-phi-client-model-quant export-phi-client-model-quant-static dev-iu pull-model-pytorch prodigy-prepare prodigy-prepare-file prodigy-annotate prodigy-export prodigy-retrain prodigy-finetune prodigy-cycle prodigy-clear-unannotated check-corrections-fresh gold-export gold-split gold-train gold-finetune gold-audit gold-eval gold-cycle gold-incremental platinum-test platinum-build platinum-sanitize platinum-apply platinum-apply-dry platinum-cycle platinum-final

# Use conda environment medparse-py311 (Python 3.11)
CONDA_ACTIVATE := source ~/miniconda3/etc/profile.d/conda.sh && conda activate medparse-py311
SETUP_STAMP := .setup.stamp
PYTHON := python
KB_PATH := data/knowledge/ip_coding_billing_v2_9.json
SCHEMA_PATH := data/knowledge/IP_Registry.json
NOTES_PATH := data/knowledge/synthetic_notes_with_registry2.json
PORT ?= 8000
MODEL_BACKEND ?= pytorch
PROCSUITE_SKIP_WARMUP ?= 1
REGISTRY_RUNTIME_DIR ?= data/models/registry_runtime
DEVICE ?= cpu
PRODIGY_EPOCHS ?= 1

setup:
	@if [ -f $(SETUP_STAMP) ]; then echo "Setup already done"; exit 0; fi
	$(CONDA_ACTIVATE) && pip install -r requirements.txt
	touch $(SETUP_STAMP)

lint:
	$(CONDA_ACTIVATE) && ruff check --cache-dir .ruff_cache .

typecheck:
	$(CONDA_ACTIVATE) && mypy --cache-dir .mypy_cache .

test:
	$(CONDA_ACTIVATE) && pytest

# Validate JSON schemas and Pydantic models
validate-schemas:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/validate_jsonschema.py --schema $(SCHEMA_PATH) || true
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/check_pydantic_models.py

# Validate knowledge base
validate-kb:
	@echo "Validating knowledge base at $(KB_PATH)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import json; json.load(open('$(KB_PATH)'))" && echo "KB JSON valid"

# Run the smart-hybrid coder over notes
run-coder:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_coder_hybrid.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--keyword-dir data/keyword_mappings \
		--out-json outputs/coder_suggestions.jsonl

distill-phi:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/distill_phi_labels.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/distilled_phi_labels.jsonl \
		--teacher-model data/models/hf/piiranha-v1-detect-personal-information \
		--device cpu

distill-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/distill_phi_labels.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/distilled_phi_labels.jsonl \
		--teacher-model data/models/hf/piiranha-v1-detect-personal-information \
		--label-schema standard \
		--device $(DEVICE)

sanitize-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/sanitize_dataset.py \
		--in data/ml_training/distilled_phi_labels.jsonl \
		--out data/ml_training/distilled_phi_CLEANED.jsonl

normalize-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/normalize_phi_labels.py \
		--in data/ml_training/distilled_phi_CLEANED.jsonl \
		--out data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--password-policy id

eval-phi-client:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--data data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--output-dir artifacts/phi_distilbert_ner \
		--eval-only

audit-phi-client:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/audit_model_fp.py \
		--model-dir artifacts/phi_distilbert_ner \
		--data data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--limit 5000

patch-phi-client-hardneg:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_hard_negative_patch.py \
		--audit-report artifacts/phi_distilbert_ner/audit_report.json \
		--data-in data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--data-out data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl

# Default: MPS with memory-saving options (gradient accumulation, smaller batches)
# Removes MPS memory limits to use available system RAM
# If OOM on Apple Silicon, use: make finetune-phi-client-hardneg-cpu
finetune-phi-client-hardneg:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--resume-from artifacts/phi_distilbert_ner \
		--patched-data data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl \
		--epochs 1 \
		--lr 1e-5 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0 \
		--save-steps 500 \
		--eval-steps 500 \
		--logging-steps 50

# CPU fallback: reliable but slower (~5-6 hours for 1 epoch)
finetune-phi-client-hardneg-cpu:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--resume-from artifacts/phi_distilbert_ner \
		--patched-data data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl \
		--epochs 1 \
		--lr 1e-5 \
		--train-batch 8 \
		--eval-batch 16 \
		--save-steps 500 \
		--eval-steps 500 \
		--logging-steps 50 \
		--cpu

export-phi-client-model:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir modules/api/static/phi_redactor/vendor/phi_distilbert_ner

export-phi-client-model-quant:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir modules/api/static/phi_redactor/vendor/phi_distilbert_ner \
		--quantize

export-phi-client-model-quant-static:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir modules/api/static/phi_redactor/vendor/phi_distilbert_ner \
		--quantize --static-quantize

build-phi-platinum:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_model_agnostic_phi_spans.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/phi_platinum_spans.jsonl

# Prodigy-based PHI label correction workflow
PRODIGY_COUNT ?= 100
PRODIGY_DATASET ?= phi_corrections
# Prodigy is installed in system Python 3.12
PRODIGY_PYTHON ?= /Library/Frameworks/Python.framework/Versions/3.12/bin/python3

prodigy-prepare:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/prodigy_prepare_phi_batch.py \
		--count $(PRODIGY_COUNT) \
		--model-dir artifacts/phi_distilbert_ner \
		--output data/ml_training/prodigy_batch.jsonl

# Prepare from a specific input file (e.g., synthetic_phi.jsonl)
PRODIGY_INPUT_FILE ?= synthetic_phi.jsonl
prodigy-prepare-file:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/prodigy_prepare_phi_batch.py \
		--count $(PRODIGY_COUNT) \
		--input-file $(PRODIGY_INPUT_FILE) \
		--model-dir artifacts/phi_distilbert_ner \
		--output data/ml_training/prodigy_batch.jsonl

prodigy-annotate:
	$(PRODIGY_PYTHON) -m prodigy ner.manual $(PRODIGY_DATASET) blank:en \
		data/ml_training/prodigy_batch.jsonl \
		--label PATIENT,DATE,ID,GEO,CONTACT

prodigy-export:
	$(PRODIGY_PYTHON) scripts/prodigy_export_corrections.py \
		--dataset $(PRODIGY_DATASET) \
		--merge-with data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--output data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl

# Train from scratch on corrected data
prodigy-retrain:
	@echo "Training from scratch on corrected data..."
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--data data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl \
		--output-dir artifacts/phi_distilbert_ner \
		--epochs 3 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0

# Corrections file for Prodigy workflow
CORRECTIONS_FILE := data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl

# Guard: Ensure corrections file exists before fine-tuning
check-corrections-fresh:
	@if [ ! -f $(CORRECTIONS_FILE) ]; then \
		echo "ERROR: $(CORRECTIONS_FILE) not found."; \
		echo "Run 'make prodigy-export' first to export Prodigy corrections."; \
		exit 1; \
	fi
	@echo "Using corrections file: $(CORRECTIONS_FILE)"
	@echo "Last modified: $$(stat -f '%Sm' $(CORRECTIONS_FILE) 2>/dev/null || stat -c '%y' $(CORRECTIONS_FILE) 2>/dev/null || echo 'unknown')"

# Fine-tune existing model on corrected data (recommended for iterative improvement)
# Override epochs: make prodigy-finetune PRODIGY_EPOCHS=3
prodigy-finetune: check-corrections-fresh
	@echo "Fine-tuning existing model on corrected data..."
	@echo "Epochs: $(PRODIGY_EPOCHS)"
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--resume-from artifacts/phi_distilbert_ner \
		--patched-data data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl \
		--output-dir artifacts/phi_distilbert_ner \
		--epochs $(PRODIGY_EPOCHS) \
		--lr 1e-5 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0

prodigy-cycle: prodigy-prepare
	@echo "Batch prepared at data/ml_training/prodigy_batch.jsonl"
	@echo "Run 'make prodigy-annotate' to start Prodigy annotation UI"
	@echo "After annotation, run 'make prodigy-export' then either:"
	@echo "  make prodigy-finetune  (recommended - preserves learned weights)"
	@echo "  make prodigy-retrain   (train from scratch)"

# Clear unannotated examples from Prodigy batch file
prodigy-clear-unannotated:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/clear_unannotated_prodigy_batch.py \
		--batch-file data/ml_training/prodigy_batch.jsonl \
		--dataset $(PRODIGY_DATASET) \
		--backup

# ==============================================================================
# Gold Standard PHI Workflow (Pure Human-Verified Data)
# ==============================================================================
# Uses only Prodigy-verified annotations for maximum quality training.
# Run: make gold-cycle (or individual targets)

GOLD_EPOCHS ?= 10
GOLD_DATASET ?= phi_corrections
GOLD_OUTPUT_DIR ?= data/ml_training
GOLD_MODEL_DIR ?= artifacts/phi_distilbert_ner

# Export pure gold from Prodigy (no merging with old data)
# Uses PRODIGY_PYTHON because Prodigy is installed in system Python 3.12
gold-export:
	$(PRODIGY_PYTHON) scripts/export_phi_gold_standard.py \
		--dataset $(GOLD_DATASET) \
		--output $(GOLD_OUTPUT_DIR)/phi_gold_standard_v1.jsonl \
		--model-dir $(GOLD_MODEL_DIR)

# Split into train/test (80/20) with grouping by note ID
gold-split:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/split_phi_gold.py \
		--input $(GOLD_OUTPUT_DIR)/phi_gold_standard_v1.jsonl \
		--train-out $(GOLD_OUTPUT_DIR)/phi_train_gold.jsonl \
		--test-out $(GOLD_OUTPUT_DIR)/phi_test_gold.jsonl \
		--seed 42

# Train on pure gold data (Higher epochs for smaller high-quality data)
gold-train:
	@echo "Training on pure Gold Standard data..."
	@echo "Epochs: $(GOLD_EPOCHS)"
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--patched-data $(GOLD_OUTPUT_DIR)/phi_train_gold.jsonl \
		--resume-from $(GOLD_MODEL_DIR) \
		--output-dir $(GOLD_MODEL_DIR) \
		--epochs $(GOLD_EPOCHS) \
		--lr 1e-5 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0 \
		--eval-steps 100 \
		--save-steps 200 \
		--logging-steps 50

# Audit on gold test set (Critical for safety verification)
gold-audit:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/audit_model_fp.py \
		--model-dir $(GOLD_MODEL_DIR) \
		--data $(GOLD_OUTPUT_DIR)/phi_test_gold.jsonl \
		--report-out $(GOLD_MODEL_DIR)/audit_gold_report.json

# Evaluate metrics on gold test set
gold-eval:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--patched-data $(GOLD_OUTPUT_DIR)/phi_test_gold.jsonl \
		--output-dir $(GOLD_MODEL_DIR) \
		--eval-only

# Full cycle: export → split → train → audit → eval
gold-cycle: gold-export gold-split gold-train gold-audit gold-eval
	@echo "Gold standard workflow complete."
	@echo "Audit report: $(GOLD_MODEL_DIR)/audit_gold_report.json"

# Light fine-tune on expanded gold data (fewer epochs, for incremental updates)
GOLD_FINETUNE_EPOCHS ?= 3
gold-finetune:
	@echo "Fine-tuning on expanded Gold Standard data..."
	@echo "Epochs: $(GOLD_FINETUNE_EPOCHS) (use GOLD_FINETUNE_EPOCHS=N to override)"
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/train_distilbert_ner.py \
		--patched-data $(GOLD_OUTPUT_DIR)/phi_train_gold.jsonl \
		--resume-from $(GOLD_MODEL_DIR) \
		--output-dir $(GOLD_MODEL_DIR) \
		--epochs $(GOLD_FINETUNE_EPOCHS) \
		--lr 5e-6 \
		--train-batch 4 \
		--eval-batch 16 \
		--gradient-accumulation-steps 2 \
		--mps-high-watermark-ratio 0.0 \
		--eval-steps 50 \
		--save-steps 100 \
		--logging-steps 25

# Incremental cycle: export → split → finetune → audit (lighter than full train)
gold-incremental: gold-export gold-split gold-finetune gold-audit
	@echo "Incremental gold update complete."

# ==============================================================================
# Platinum PHI Workflow (Registry ML Preprocessing)
# ==============================================================================
# Generates high-quality PHI-scrubbed training data for Registry Model.
# Platinum = Hybrid Redactor (ML+Regex) → char spans → apply [REDACTED] to golden JSONs

PLATINUM_SPANS_FILE ?= data/ml_training/phi_platinum_spans.jsonl
PLATINUM_SPANS_CLEANED ?= data/ml_training/phi_platinum_spans_CLEANED.jsonl
PLATINUM_INPUT_DIR ?= data/knowledge/golden_extractions
PLATINUM_OUTPUT_DIR ?= data/knowledge/golden_extractions_scrubbed
PLATINUM_FINAL_DIR ?= data/knowledge/golden_extractions_final

# Test run (small batch to validate pipeline)
platinum-test:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_model_agnostic_phi_spans.py \
		--in-dir $(PLATINUM_INPUT_DIR) \
		--out $(PLATINUM_SPANS_FILE) \
		--limit-notes 100
	@echo "Test run complete. Check $(PLATINUM_SPANS_FILE) for span output."

# Build full platinum spans (all notes)
platinum-build:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/build_model_agnostic_phi_spans.py \
		--in-dir $(PLATINUM_INPUT_DIR) \
		--out $(PLATINUM_SPANS_FILE) \
		--limit-notes 0
	@echo "Platinum spans built: $(PLATINUM_SPANS_FILE)"

# Sanitize platinum spans (post-hoc cleanup)
platinum-sanitize:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/sanitize_platinum_spans.py \
		--in $(PLATINUM_SPANS_FILE) \
		--out $(PLATINUM_SPANS_CLEANED)
	@echo "Sanitized spans: $(PLATINUM_SPANS_CLEANED)"

# Apply redactions to create scrubbed golden JSONs
platinum-apply:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/apply_platinum_redactions.py \
		--spans $(PLATINUM_SPANS_CLEANED) \
		--input-dir $(PLATINUM_INPUT_DIR) \
		--output-dir $(PLATINUM_OUTPUT_DIR)
	@echo "Scrubbed golden JSONs: $(PLATINUM_OUTPUT_DIR)"

# Dry run (show what would be done without writing files)
platinum-apply-dry:
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/apply_platinum_redactions.py \
		--spans $(PLATINUM_SPANS_CLEANED) \
		--input-dir $(PLATINUM_INPUT_DIR) \
		--output-dir $(PLATINUM_OUTPUT_DIR) \
		--dry-run

# Full platinum cycle: build → sanitize → apply
platinum-cycle: platinum-build platinum-sanitize platinum-apply
	@echo "----------------------------------------------------------------"
	@echo "SUCCESS: Scrubbed Golden JSONs are ready."
	@echo "Location: $(PLATINUM_OUTPUT_DIR)"
	@echo "Next: Use scrubbed data for registry ML training"
	@echo "----------------------------------------------------------------"

# Post-processing: clean hallucinated institution fields and write final output set
platinum-final: platinum-cycle
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/fix_registry_hallucinations.py \
		--input-dir $(PLATINUM_OUTPUT_DIR) \
		--output-dir $(PLATINUM_FINAL_DIR)
	@echo "Final cleaned Golden JSONs: $(PLATINUM_FINAL_DIR)"

pull-model-pytorch:
	MODEL_BUNDLE_S3_URI_PYTORCH="$(MODEL_BUNDLE_S3_URI_PYTORCH)" REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" ./scripts/dev_pull_model.sh

dev-iu:
	$(CONDA_ACTIVATE) && \
		MODEL_BACKEND="$(MODEL_BACKEND)" \
		REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" \
		PROCSUITE_SKIP_WARMUP="$(PROCSUITE_SKIP_WARMUP)" \
		RAILWAY_ENVIRONMENT="local" \
		$(PYTHON) -m uvicorn modules.api.fastapi_app:app --reload --host 0.0.0.0 --port "$(PORT)"

# Run cleaning pipeline with patches
autopatch:
	@mkdir -p autopatches reports
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_cleaning_pipeline.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--schema $(SCHEMA_PATH) \
		--out-json autopatches/patches.json \
		--out-csv reports/errors.csv \
		--apply-minimal-fixes || true

# Autocommit generated patches/reports
autocommit:
	@git add .
	@git commit -m "Autocommit: generated patches/reports" || true

# Run codex training pipeline (full CI-like flow)
codex-train: setup lint typecheck test validate-schemas validate-kb autopatch
	@echo "Codex training pipeline complete"

# Run metrics over a batch of notes
codex-metrics: setup
	@mkdir -p outputs
	@echo "Running metrics pipeline..."
	$(CONDA_ACTIVATE) && $(PYTHON) scripts/run_coder_hybrid.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--keyword-dir data/keyword_mappings \
		--out-json outputs/metrics_run.jsonl
	@echo "Metrics written to outputs/metrics_run.jsonl"

# Clean generated files
clean:
	rm -rf $(SETUP_STAMP)
	rm -rf .ruff_cache .mypy_cache .pytest_cache
	rm -rf outputs autopatches reports
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Help target
help:
	@echo "Available targets:"
	@echo "  setup          - Install dependencies in conda env medparse-py311"
	@echo "  lint           - Run ruff linter"
	@echo "  typecheck      - Run mypy type checker"
	@echo "  test           - Run pytest"
	@echo "  validate-schemas - Validate JSON schemas and Pydantic models"
	@echo "  validate-kb    - Validate knowledge base"
	@echo "  run-coder      - Run smart-hybrid coder over notes"
	@echo "  distill-phi    - Distill PHI labels for student NER training"
	@echo "  distill-phi-silver - Distill Piiranha silver PHI labels"
	@echo "  sanitize-phi-silver - Post-hoc sanitizer for silver PHI labels"
	@echo "  normalize-phi-silver - Normalize silver labels to stable schema"
	@echo "  build-phi-platinum - Build hybrid redactor PHI spans"
	@echo "  eval-phi-client - Evaluate DistilBERT NER model (no retraining)"
	@echo "  audit-phi-client - Run false-positive audit guardrails"
	@echo "  patch-phi-client-hardneg - Patch training data with audit violations"
	@echo "  finetune-phi-client-hardneg - Finetune model on hard negatives (MPS w/ gradient accumulation)"
	@echo "  finetune-phi-client-hardneg-cpu - Finetune on CPU (slower but reliable fallback)"
	@echo "  export-phi-client-model - Export client-side ONNX bundle (unquantized) for transformers.js"
	@echo "  export-phi-client-model-quant - Export client-side ONNX bundle + INT8 quantized model (dynamic)"
	@echo "  export-phi-client-model-quant-static - Export client-side ONNX bundle + INT8 quantized model (static, smaller)"
	@echo "  prodigy-prepare - Prepare batch for Prodigy annotation (PRODIGY_COUNT=100)"
	@echo "  prodigy-annotate - Launch Prodigy annotation UI (PRODIGY_DATASET=phi_corrections)"
	@echo "  prodigy-export  - Export Prodigy corrections to training format"
	@echo "  prodigy-retrain - Retrain model from scratch with corrections"
	@echo "  prodigy-finetune - Fine-tune existing model with corrections (recommended)"
	@echo "                    Override epochs: make prodigy-finetune PRODIGY_EPOCHS=3"
	@echo "  prodigy-cycle   - Full Prodigy iteration workflow"
	@echo "  prodigy-clear-unannotated - Remove unannotated examples from batch file"
	@echo ""
	@echo "Gold Standard PHI Workflow (pure human-verified data):"
	@echo "  gold-export    - Export pure gold from Prodigy dataset"
	@echo "  gold-split     - 80/20 train/test split with note grouping"
	@echo "  gold-train     - Train on gold data (10 epochs default)"
	@echo "  gold-finetune  - Light fine-tune (3 epochs, lower LR) for incremental updates"
	@echo "  gold-audit     - Safety audit on gold test set"
	@echo "  gold-eval      - Evaluate metrics on gold test set"
	@echo "  gold-cycle     - Full workflow: export → split → train → audit → eval"
	@echo "  gold-incremental - Incremental: export → split → finetune → audit"
	@echo ""
	@echo "Platinum PHI Workflow (Registry ML Preprocessing):"
	@echo "  platinum-test  - Test run on 100 notes to validate pipeline"
	@echo "  platinum-build - Build full platinum spans from all golden JSONs"
	@echo "  platinum-sanitize - Post-hoc cleanup of platinum spans"
	@echo "  platinum-apply - Apply [REDACTED] to golden JSONs"
	@echo "  platinum-apply-dry - Dry run (show what would be done)"
	@echo "  platinum-cycle - Full workflow: build → sanitize → apply"
	@echo ""
	@echo "  autopatch      - Generate patches for registry cleaning"
	@echo "  autocommit     - Git commit generated files"
	@echo "  codex-train    - Full training pipeline"
	@echo "  codex-metrics  - Run metrics over notes batch"
	@echo "  clean          - Remove generated files"
