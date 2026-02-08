SHELL := /bin/bash
.PHONY: setup lint typecheck test deps-compile deps-check validate-schemas validate-kb validate-knowledge-release test-kb-strict autopatch autocommit codex-train codex-metrics run-coder distill-phi distill-phi-silver sanitize-phi-silver normalize-phi-silver build-phi-platinum eval-phi-client audit-phi-client patch-phi-client-hardneg finetune-phi-client-hardneg finetune-phi-client-hardneg-cpu export-phi-client-model export-phi-client-model-quant export-phi-client-model-quant-static dev-iu pull-model-pytorch prodigy-prepare prodigy-prepare-file prodigy-annotate prodigy-export prodigy-retrain prodigy-finetune prodigy-cycle prodigy-clear-unannotated prodigy-prepare-registry prodigy-annotate-registry prodigy-export-registry prodigy-merge-registry prodigy-retrain-registry prodigy-registry-cycle registry-prodigy-prepare registry-prodigy-annotate registry-prodigy-export check-corrections-fresh gold-export gold-split gold-train gold-finetune gold-audit gold-eval gold-cycle gold-incremental reporter-gold-generate-pilot reporter-gold-split reporter-gold-eval reporter-gold-pilot platinum-test platinum-build platinum-sanitize platinum-apply platinum-apply-dry platinum-cycle platinum-final registry-prep registry-prep-with-human registry-prep-dry registry-prep-final registry-prep-raw registry-prep-module test-registry-prep

# Use conda environment medparse-py311 (Python 3.11)
CONDA_ACTIVATE := source ~/miniconda3/etc/profile.d/conda.sh && conda activate medparse-py311
SETUP_STAMP := .setup.stamp
PYTHON := python
KB_PATH := data/knowledge/ip_coding_billing_v3_0.json
SCHEMA_PATH := data/knowledge/IP_Registry.json
NOTES_PATH := data/knowledge/synthetic_notes_with_registry2.json
PORT ?= 8000
MODEL_BACKEND ?= pytorch
PROCSUITE_SKIP_WARMUP ?= 1
REGISTRY_RUNTIME_DIR ?= data/models/registry_runtime
DEVICE ?= cpu
PRODIGY_EPOCHS ?= 1
DEPS_PYTHON ?= python3.11
PIP_COMPILE_ARGS := --upgrade --resolver=backtracking --strip-extras --allow-unsafe --no-header --no-emit-index-url --no-emit-trusted-host --pip-args='--platform manylinux2014_x86_64 --python-version 3.11 --implementation cp --abi cp311'

setup:
	@if [ -f $(SETUP_STAMP) ]; then echo "Setup already done"; exit 0; fi
	$(CONDA_ACTIVATE) && pip install -r requirements.txt
	touch $(SETUP_STAMP)

lint:
	$(CONDA_ACTIVATE) && ruff check --cache-dir .ruff_cache .

typecheck:
	$(CONDA_ACTIVATE) && mypy --cache-dir .mypy_cache proc_schemas config observability

test:
	$(CONDA_ACTIVATE) && pytest

deps-compile:
	$(DEPS_PYTHON) -m pip install --quiet pip-tools
	$(DEPS_PYTHON) -m piptools compile $(PIP_COMPILE_ARGS) --output-file=requirements.txt requirements.in

deps-check:
	$(DEPS_PYTHON) -m pip install --quiet pip-tools
	@tmp_file=$$(mktemp); \
	$(DEPS_PYTHON) -m piptools compile $(PIP_COMPILE_ARGS) --output-file=$$tmp_file requirements.in >/dev/null 2>&1; \
	if ! diff -u $$tmp_file requirements.txt >/dev/null; then \
		echo "requirements.txt is out of sync with requirements.in. Run: make deps-compile"; \
		diff -u $$tmp_file requirements.txt || true; \
		rm -f $$tmp_file; \
		exit 1; \
	fi; \
	rm -f $$tmp_file

# Validate JSON schemas and Pydantic models
validate-schemas:
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/validate_jsonschema.py --schema $(SCHEMA_PATH) || true
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/check_pydantic_models.py

# Validate knowledge base
validate-kb:
	@echo "Validating knowledge base at $(KB_PATH)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import json; json.load(open('$(KB_PATH)'))" && echo "KB JSON valid"

# Validate KB + schema integration (no-op extraction)
validate-knowledge-release:
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/validate_knowledge_release.py --kb $(KB_PATH) --schema $(SCHEMA_PATH)

# Run regression tests with KB Strict Mode to catch orphan codes
test-kb-strict:
	@echo "Running smoke tests in KB STRICT mode..."
	$(CONDA_ACTIVATE) && PROCSUITE_PIPELINE_MODE=extraction_first PSUITE_KB_STRICT=1 pytest tests/coder/test_coding_rules_phase7.py -v
	$(CONDA_ACTIVATE) && PROCSUITE_PIPELINE_MODE=extraction_first PSUITE_KB_STRICT=1 $(PYTHON) ops/tools/registry_pipeline_smoke_batch.py --count 10 --notes-dir "tests/fixtures/notes"

# Knowledge diff report (set OLD_KB=...; NEW_KB defaults to KB_PATH)
OLD_KB ?=
NEW_KB ?= $(KB_PATH)

knowledge-diff:
	@if [ -z "$(OLD_KB)" ]; then echo "ERROR: Set OLD_KB=path/to/old_kb.json"; exit 2; fi
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/knowledge_diff_report.py --old $(OLD_KB) --new $(NEW_KB)

# Run the smart-hybrid coder over notes
run-coder:
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/run_coder_hybrid.py \
		--notes $(NOTES_PATH) \
		--kb $(KB_PATH) \
		--keyword-dir data/keyword_mappings \
		--out-json outputs/coder_suggestions.jsonl

distill-phi:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/distill_phi_labels.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/distilled_phi_labels.jsonl \
		--teacher-model artifacts/phi_distilbert_ner \
		--device cpu

distill-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/distill_phi_labels.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/distilled_phi_labels.jsonl \
		--teacher-model artifacts/phi_distilbert_ner \
		--label-schema standard \
		--device $(DEVICE)

sanitize-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/sanitize_dataset.py \
		--in data/ml_training/distilled_phi_labels.jsonl \
		--out data/ml_training/distilled_phi_CLEANED.jsonl

normalize-phi-silver:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/normalize_phi_labels.py \
		--in data/ml_training/distilled_phi_CLEANED.jsonl \
		--out data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--password-policy id

eval-phi-client:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
		--data data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--output-dir artifacts/phi_distilbert_ner \
		--eval-only

audit-phi-client:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/audit_model_fp.py \
		--model-dir artifacts/phi_distilbert_ner \
		--data data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--limit 5000

patch-phi-client-hardneg:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/build_hard_negative_patch.py \
		--audit-report artifacts/phi_distilbert_ner/audit_report.json \
		--data-in data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--data-out data/ml_training/distilled_phi_CLEANED_STANDARD.hardneg.jsonl

# Default: MPS with memory-saving options (gradient accumulation, smaller batches)
# Removes MPS memory limits to use available system RAM
# If OOM on Apple Silicon, use: make finetune-phi-client-hardneg-cpu
finetune-phi-client-hardneg:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir ui/static/phi_redactor/vendor/phi_distilbert_ner

export-phi-client-model-quant:
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir ui/static/phi_redactor/vendor/phi_distilbert_ner \
		--quantize

export-phi-client-model-quant-static:
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/export_phi_model_for_transformersjs.py \
		--model-dir artifacts/phi_distilbert_ner \
		--out-dir ui/static/phi_redactor/vendor/phi_distilbert_ner \
		--quantize --static-quantize

build-phi-platinum:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/build_model_agnostic_phi_spans.py \
		--in-dir data/knowledge/golden_extractions \
		--out data/ml_training/phi_platinum_spans.jsonl

# Prodigy-based PHI label correction workflow
PRODIGY_COUNT ?= 100
PRODIGY_DATASET ?= phi_corrections
# Prodigy should run in the same environment as the rest of the tooling.
# (The previous default hardcoded a macOS system Python path and breaks on Linux/WSL.)
PRODIGY_PYTHON ?= $(PYTHON)

prodigy-prepare:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/prodigy_prepare_phi_batch.py \
		--count $(PRODIGY_COUNT) \
		--model-dir artifacts/phi_distilbert_ner \
		--output data/ml_training/prodigy_batch.jsonl

# Prepare from a specific input file (e.g., synthetic_phi.jsonl)
PRODIGY_INPUT_FILE ?= synthetic_phi.jsonl
prodigy-prepare-file:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/prodigy_prepare_phi_batch.py \
		--count $(PRODIGY_COUNT) \
		--input-file $(PRODIGY_INPUT_FILE) \
		--model-dir artifacts/phi_distilbert_ner \
		--output data/ml_training/prodigy_batch.jsonl

prodigy-annotate:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) -m prodigy ner.manual $(PRODIGY_DATASET) blank:en \
		data/ml_training/prodigy_batch.jsonl \
		--label PATIENT,DATE,ID,GEO,CONTACT

prodigy-export:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) ml/scripts/prodigy_export_corrections.py \
		--dataset $(PRODIGY_DATASET) \
		--merge-with data/ml_training/distilled_phi_CLEANED_STANDARD.jsonl \
		--output data/ml_training/distilled_phi_WITH_CORRECTIONS.jsonl

# Train from scratch on corrected data
prodigy-retrain:
	@echo "Training from scratch on corrected data..."
	@echo "Checking for GPU acceleration (Metal/CUDA)..."
	$(CONDA_ACTIVATE) && $(PYTHON) -c "import torch; mps=torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False; cuda=torch.cuda.is_available(); print(f'MPS: {mps}, CUDA: {cuda}')" && \
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/clear_unannotated_prodigy_batch.py \
		--batch-file data/ml_training/prodigy_batch.jsonl \
		--dataset $(PRODIGY_DATASET) \
		--backup

# ==============================================================================
# Registry Prodigy Workflow (Multi-Label Classification)
# ==============================================================================
# Requires:
#   make registry-prep-final (or otherwise produce registry_train/val/test.csv)
#   and a JSONL of unlabeled notes at $(PRODIGY_REGISTRY_INPUT_FILE)
#
# Workflow: prepare → annotate → export → merge → retrain

PRODIGY_REGISTRY_COUNT ?= 200
PRODIGY_REGISTRY_DATASET ?= registry_corrections_v1
PRODIGY_REGISTRY_INPUT_FILE ?= data/ml_training/registry_unlabeled_notes.jsonl
PRODIGY_REGISTRY_STRATEGY ?= hybrid
PRODIGY_REGISTRY_MODEL_DIR ?= data/models/registry_runtime

PRODIGY_REGISTRY_BATCH_FILE ?= data/ml_training/prodigy_registry_batch.jsonl
PRODIGY_REGISTRY_MANIFEST ?= data/ml_training/prodigy_registry_manifest.json
PRODIGY_REGISTRY_EXPORT_CSV ?= data/ml_training/registry_prodigy_labels.csv
PRODIGY_REGISTRY_TRAIN_AUGMENTED ?= data/ml_training/registry_train_augmented.csv

prodigy-prepare-registry:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/prodigy_prepare_registry.py \
		--input-file $(PRODIGY_REGISTRY_INPUT_FILE) \
		--output-file $(PRODIGY_REGISTRY_BATCH_FILE) \
		--count $(PRODIGY_REGISTRY_COUNT) \
		--strategy $(PRODIGY_REGISTRY_STRATEGY) \
		--model-dir $(PRODIGY_REGISTRY_MODEL_DIR) \
		--manifest $(PRODIGY_REGISTRY_MANIFEST) \
		--exclude-csv data/ml_training/registry_train.csv

prodigy-annotate-registry:
	$(CONDA_ACTIVATE) && LABELS="$$( $(PYTHON) -c 'from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS; print(",".join(REGISTRY_LABELS))' )" && \
		$(PRODIGY_PYTHON) -m prodigy textcat.manual $(PRODIGY_REGISTRY_DATASET) \
		$(PRODIGY_REGISTRY_BATCH_FILE) \
		--label $$LABELS

prodigy-export-registry:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) ml/scripts/prodigy_export_registry.py \
		--dataset $(PRODIGY_REGISTRY_DATASET) \
		--output-csv $(PRODIGY_REGISTRY_EXPORT_CSV)

prodigy-merge-registry:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/merge_registry_prodigy.py \
		--base-train-csv data/ml_training/registry_train.csv \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--prodigy-csv $(PRODIGY_REGISTRY_EXPORT_CSV) \
		--out-csv $(PRODIGY_REGISTRY_TRAIN_AUGMENTED)

prodigy-retrain-registry:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_roberta.py \
		--train-csv $(PRODIGY_REGISTRY_TRAIN_AUGMENTED) \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--output-dir data/models/roberta_registry

prodigy-registry-cycle: prodigy-prepare-registry
	@echo "Batch prepared at $(PRODIGY_REGISTRY_BATCH_FILE)"
	@echo "Run 'make prodigy-annotate-registry' to start Prodigy UI (textcat)"
	@echo "After annotation:"
	@echo "  make prodigy-export-registry"
	@echo "  make prodigy-merge-registry"
	@echo "  make prodigy-retrain-registry"

# ==============================================================================
# Registry Distillation (Teacher → Student)
# ==============================================================================
TEACHER_MODEL_NAME ?= data/models/RoBERTa-base-PM-M3-Voc-distill/RoBERTa-base-PM-M3-Voc-distill-hf
TEACHER_OUTPUT_DIR ?= data/models/registry_teacher
TEACHER_EPOCHS ?= 3

TEACHER_LOGITS_IN ?= data/ml_training/registry_unlabeled_notes.jsonl
TEACHER_LOGITS_OUT ?= data/ml_training/teacher_logits.npz

DISTILL_ALPHA ?= 0.5
DISTILL_TEMP ?= 2.0
DISTILL_LOSS ?= mse
STUDENT_DISTILL_OUTPUT_DIR ?= data/models/roberta_registry_distilled

teacher-train:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_roberta_pm3.py \
		--model-name $(TEACHER_MODEL_NAME) \
		--output-dir $(TEACHER_OUTPUT_DIR) \
		--train-csv data/ml_training/registry_train.csv \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--epochs $(TEACHER_EPOCHS)

teacher-eval:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_roberta_pm3.py \
		--evaluate-only \
		--model-dir $(TEACHER_OUTPUT_DIR) \
		--test-csv data/ml_training/registry_test.csv

teacher-logits:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/generate_teacher_logits.py \
		--model-dir $(TEACHER_OUTPUT_DIR) \
		--input-jsonl $(TEACHER_LOGITS_IN) \
		--out $(TEACHER_LOGITS_OUT)

student-distill:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_roberta.py \
		--train-csv data/ml_training/registry_train.csv \
		--val-csv data/ml_training/registry_val.csv \
		--test-csv data/ml_training/registry_test.csv \
		--teacher-logits $(TEACHER_LOGITS_OUT) \
		--distill-alpha $(DISTILL_ALPHA) \
		--distill-temp $(DISTILL_TEMP) \
		--distill-loss $(DISTILL_LOSS) \
		--output-dir $(STUDENT_DISTILL_OUTPUT_DIR)

registry-overlap-report:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/registry_label_overlap_report.py \
		--csv data/ml_training/registry_train.csv \
		--csv data/ml_training/registry_val.csv \
		--csv data/ml_training/registry_test.csv \
		--out reports/registry_label_overlap.json

# ==============================================================================
# Registry “Diamond Loop” targets (brief-compatible aliases)
# ==============================================================================
REG_PRODIGY_COUNT ?= 200
REG_PRODIGY_DATASET ?= registry_v1
REG_PRODIGY_INPUT_FILE ?= data/ml_training/registry_unlabeled_notes.jsonl
REG_PRODIGY_BATCH_FILE ?= data/ml_training/registry_prodigy_batch.jsonl
REG_PRODIGY_MANIFEST ?= data/ml_training/registry_prodigy_manifest.json
REG_PRODIGY_MODEL_DIR ?= data/models/registry_runtime
REG_PRODIGY_STRATEGY ?= disagreement
REG_PRODIGY_SEED ?= 42
REG_PRODIGY_EXPORT_CSV ?= data/ml_training/registry_human.csv
REG_PRODIGY_RESET_ARCHIVE_DIR ?= data/ml_training/_archive/registry_prodigy

# Relabel workflow (build a review batch from an existing human CSV)
REG_RELABEL_INPUT_CSV ?= data/ml_training/registry_human_v1_backup.csv
REG_RELABEL_OUTPUT_FILE ?= data/ml_training/registry_rigid_review.jsonl
REG_RELABEL_FILTER_LABEL ?= rigid_bronchoscopy
REG_RELABEL_LIMIT ?= 0
REG_RELABEL_PREFILL_NON_THERMAL ?= 1

REG_HUMAN_BASE_CSV ?= data/ml_training/registry_human_v1_backup.csv
REG_HUMAN_UPDATES_CSV ?= data/ml_training/registry_human_rigid_review.csv
REG_HUMAN_OUT_CSV ?= data/ml_training/registry_human_v2.csv

# Reset registry Prodigy state (batch + manifest + Prodigy dataset).
# This is safe to run even if some files/datasets don't exist.
registry-prodigy-reset:
	@mkdir -p $(REG_PRODIGY_RESET_ARCHIVE_DIR)
	@ts="$$(date +%Y%m%d_%H%M%S)"; \
	for f in "$(REG_PRODIGY_BATCH_FILE)" "$(REG_PRODIGY_MANIFEST)"; do \
		if [ -f "$$f" ]; then \
			mv "$$f" "$(REG_PRODIGY_RESET_ARCHIVE_DIR)/$$(basename "$$f").$$ts"; \
			echo "Archived $$f → $(REG_PRODIGY_RESET_ARCHIVE_DIR)/$$(basename "$$f").$$ts"; \
		fi; \
	done
	@$(CONDA_ACTIVATE) && REG_PRODIGY_DATASET="$(REG_PRODIGY_DATASET)" $(PRODIGY_PYTHON) - <<'PY'\nfrom prodigy.components.db import connect\nimport os\n\nds = os.environ.get(\"REG_PRODIGY_DATASET\", \"\").strip()\nif not ds:\n    raise SystemExit(\"REG_PRODIGY_DATASET is empty\")\n\ndb = connect()\nif ds in db.datasets:\n    db.drop_dataset(ds)\n    print(f\"Dropped Prodigy dataset: {ds}\")\nelse:\n    print(f\"Prodigy dataset not found (nothing to drop): {ds}\")\nPY

registry-prodigy-prepare:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/prodigy_prepare_registry_batch.py \
		--input-file $(REG_PRODIGY_INPUT_FILE) \
		--output-file $(REG_PRODIGY_BATCH_FILE) \
		--limit $(REG_PRODIGY_COUNT) \
		--strategy $(REG_PRODIGY_STRATEGY) \
		--manifest $(REG_PRODIGY_MANIFEST) \
		--seed $(REG_PRODIGY_SEED) \
		--model-dir $(REG_PRODIGY_MODEL_DIR)

registry-prodigy-prepare-relabel:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/prodigy_prepare_registry_relabel_batch.py \
		--input-csv $(REG_RELABEL_INPUT_CSV) \
		--output-file $(REG_RELABEL_OUTPUT_FILE) \
		--filter-label $(REG_RELABEL_FILTER_LABEL) \
		--limit $(REG_RELABEL_LIMIT) \
		$(if $(filter 1,$(REG_RELABEL_PREFILL_NON_THERMAL)),--prefill-non-thermal-from-rigid,)

registry-human-merge-updates:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/merge_registry_human_labels.py \
		--base-csv $(REG_HUMAN_BASE_CSV) \
		--updates-csv $(REG_HUMAN_UPDATES_CSV) \
		--out-csv $(REG_HUMAN_OUT_CSV) \
		--prefer-updates-meta

registry-prodigy-annotate:
	$(CONDA_ACTIVATE) && LABELS="$$( $(PYTHON) -c 'from ml.lib.ml_coder.registry_label_schema import REGISTRY_LABELS; print(",".join(REGISTRY_LABELS))' )" && \
		$(PRODIGY_PYTHON) -m prodigy textcat.manual $(REG_PRODIGY_DATASET) $(REG_PRODIGY_BATCH_FILE) \
		--loader jsonl \
		--label $$LABELS

registry-prodigy-export:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) ml/scripts/prodigy_export_registry.py \
		--dataset $(REG_PRODIGY_DATASET) \
		--output-csv $(REG_PRODIGY_EXPORT_CSV)

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
# Run in the same conda env as the rest of the pipeline (WSL/Linux friendly).
gold-export:
	$(CONDA_ACTIVATE) && $(PRODIGY_PYTHON) ml/scripts/export_phi_gold_standard.py \
		--dataset $(GOLD_DATASET) \
		--output $(GOLD_OUTPUT_DIR)/phi_gold_standard_v1.jsonl \
		--model-dir $(GOLD_MODEL_DIR)

# Split into train/test (80/20) with grouping by note ID
gold-split:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/split_phi_gold.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/audit_model_fp.py \
		--model-dir $(GOLD_MODEL_DIR) \
		--data $(GOLD_OUTPUT_DIR)/phi_test_gold.jsonl \
		--report-out $(GOLD_MODEL_DIR)/audit_gold_report.json

# Evaluate metrics on gold test set
gold-eval:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/train_distilbert_ner.py \
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
# Reporter Gold Workflow (Pilot Dataset Generation + Regression Evaluation)
# ==============================================================================
REPORTER_GOLD_INPUT_DIR ?= data/knowledge/patient_note_texts
REPORTER_GOLD_OUTPUT_DIR ?= data/ml_training/reporter_golden/v1
REPORTER_GOLD_SAMPLE_SIZE ?= 200
REPORTER_GOLD_SEED ?= 42
REPORTER_GOLD_EVAL_INPUT ?= $(REPORTER_GOLD_OUTPUT_DIR)/reporter_gold_accepted.jsonl

reporter-gold-generate-pilot:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/generate_reporter_gold_dataset.py \
		--input-dir $(REPORTER_GOLD_INPUT_DIR) \
		--output-dir $(REPORTER_GOLD_OUTPUT_DIR) \
		--sample-size $(REPORTER_GOLD_SAMPLE_SIZE) \
		--seed $(REPORTER_GOLD_SEED)

reporter-gold-split:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/split_reporter_gold_dataset.py \
		--input $(REPORTER_GOLD_OUTPUT_DIR)/reporter_gold_accepted.jsonl \
		--output-dir $(REPORTER_GOLD_OUTPUT_DIR) \
		--seed $(REPORTER_GOLD_SEED)

reporter-gold-eval:
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/eval_reporter_gold_dataset.py \
		--input $(REPORTER_GOLD_EVAL_INPUT) \
		--output $(REPORTER_GOLD_OUTPUT_DIR)/reporter_gold_eval_report.json \
		--seed $(REPORTER_GOLD_SEED)

reporter-gold-pilot: reporter-gold-generate-pilot reporter-gold-split reporter-gold-eval
	@echo "Reporter gold pilot workflow complete."

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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/build_model_agnostic_phi_spans.py \
		--in-dir $(PLATINUM_INPUT_DIR) \
		--out $(PLATINUM_SPANS_FILE) \
		--limit-notes 100
	@echo "Test run complete. Check $(PLATINUM_SPANS_FILE) for span output."

# Build full platinum spans (all notes)
platinum-build:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/build_model_agnostic_phi_spans.py \
		--in-dir $(PLATINUM_INPUT_DIR) \
		--out $(PLATINUM_SPANS_FILE) \
		--limit-notes 0
	@echo "Platinum spans built: $(PLATINUM_SPANS_FILE)"

# Sanitize platinum spans (post-hoc cleanup)
platinum-sanitize:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/sanitize_platinum_spans.py \
		--in $(PLATINUM_SPANS_FILE) \
		--out $(PLATINUM_SPANS_CLEANED)
	@echo "Sanitized spans: $(PLATINUM_SPANS_CLEANED)"

# Apply redactions to create scrubbed golden JSONs
platinum-apply:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/apply_platinum_redactions.py \
		--spans $(PLATINUM_SPANS_CLEANED) \
		--input-dir $(PLATINUM_INPUT_DIR) \
		--output-dir $(PLATINUM_OUTPUT_DIR)
	@echo "Scrubbed golden JSONs: $(PLATINUM_OUTPUT_DIR)"

# Dry run (show what would be done without writing files)
platinum-apply-dry:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/apply_platinum_redactions.py \
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
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/fix_registry_hallucinations.py \
		--input-dir $(PLATINUM_OUTPUT_DIR) \
		--output-dir $(PLATINUM_FINAL_DIR)
	@echo "Final cleaned Golden JSONs: $(PLATINUM_FINAL_DIR)"

pull-model-pytorch:
	MODEL_BUNDLE_S3_URI_PYTORCH="$(MODEL_BUNDLE_S3_URI_PYTORCH)" REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" ./ops/tools/dev_pull_model.sh

dev-iu:
	$(CONDA_ACTIVATE) && \
		MODEL_BACKEND="$(MODEL_BACKEND)" \
		REGISTRY_RUNTIME_DIR="$(REGISTRY_RUNTIME_DIR)" \
		PROCSUITE_SKIP_WARMUP="$(PROCSUITE_SKIP_WARMUP)" \
		RAILWAY_ENVIRONMENT="local" \
		$(PYTHON) -m uvicorn app.api.fastapi_app:app --reload --host 0.0.0.0 --port "$(PORT)"

# Run patch validation (legacy cleaning pipeline CLI was retired)
autopatch:
	@mkdir -p autopatches reports
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/patch.py || true

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
	$(CONDA_ACTIVATE) && $(PYTHON) ops/tools/run_coder_hybrid.py \
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
	@echo "Registry Prodigy Workflow (multi-label classification):"
	@echo "  prodigy-prepare-registry - Prepare batch for Prodigy choice (PRODIGY_REGISTRY_COUNT=200)"
	@echo "  prodigy-annotate-registry - Launch Prodigy UI (PRODIGY_REGISTRY_DATASET=registry_corrections_v1)"
	@echo "  prodigy-export-registry  - Export accepted labels to CSV"
	@echo "  prodigy-merge-registry   - Merge Prodigy labels into train split (leakage-guarded)"
	@echo "  prodigy-retrain-registry - Retrain registry classifier on augmented train split"
	@echo "  prodigy-registry-cycle   - Convenience: prepare + instructions"
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
	@echo "Reporter Gold Workflow (synthetic short notes -> golden reporter dataset):"
	@echo "  reporter-gold-generate-pilot - Generate/judge/gate 200 _syn_* notes"
	@echo "  reporter-gold-split          - Patient-level train/val/test split"
	@echo "  reporter-gold-eval           - Evaluate current reporter against reporter-gold set"
	@echo "  reporter-gold-pilot          - Full workflow: generate -> split -> eval"
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
	@echo ""
	@echo "Registry-First ML Data Preparation:"
	@echo "  registry-prep       - Full pipeline: extract, split, save CSVs"
	@echo "  registry-prep-dry   - Validate without saving files"
	@echo "  registry-prep-final - Use PHI-scrubbed final data (recommended)"
	@echo "  registry-prep-module - Use module integration (prepare_registry_training_splits)"
	@echo "  test-registry-prep  - Run registry data prep tests"

# ==============================================================================
# Registry-First ML Training Data Preparation
# ==============================================================================
# Add these targets to your existing Makefile to enable the registry-first
# training data workflow.
#
# Usage:
#   make registry-prep          # Full pipeline: extract, split, save CSVs
#   make registry-prep-dry      # Validate without saving files
#   make registry-prep-final    # Use PHI-scrubbed final data
#
# Output files:
#   data/ml_training/registry_train.csv
#   data/ml_training/registry_val.csv
#   data/ml_training/registry_test.csv
#   data/ml_training/registry_meta.json

# Configuration
REGISTRY_INPUT_DIR ?= data/knowledge/golden_extractions_final
REGISTRY_OUTPUT_DIR ?= data/ml_training
REGISTRY_PREFIX ?= registry
REGISTRY_MIN_LABEL_COUNT ?= 5
REGISTRY_SEED ?= 42

# Full pipeline
registry-prep:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/golden_to_csv.py \
		--input-dir $(REGISTRY_INPUT_DIR) \
		--output-dir $(REGISTRY_OUTPUT_DIR) \
		--prefix $(REGISTRY_PREFIX) \
		--min-label-count $(REGISTRY_MIN_LABEL_COUNT) \
		--random-seed $(REGISTRY_SEED)

# Full pipeline + Tier-0 merge of human labels (Diamond Loop)
HUMAN_REGISTRY_CSV ?=
registry-prep-with-human:
	@if [ -z "$(HUMAN_REGISTRY_CSV)" ]; then \
		echo "ERROR: HUMAN_REGISTRY_CSV is required (e.g. make registry-prep-with-human HUMAN_REGISTRY_CSV=/tmp/registry_human.csv)"; \
		exit 1; \
	fi
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/golden_to_csv.py \
		--input-dir $(REGISTRY_INPUT_DIR) \
		--output-dir $(REGISTRY_OUTPUT_DIR) \
		--prefix $(REGISTRY_PREFIX) \
		--min-label-count $(REGISTRY_MIN_LABEL_COUNT) \
		--random-seed $(REGISTRY_SEED) \
		--human-labels-csv $(HUMAN_REGISTRY_CSV)

# Dry run (validate only)
registry-prep-dry:
	$(CONDA_ACTIVATE) && $(PYTHON) ml/scripts/golden_to_csv.py \
		--input-dir $(REGISTRY_INPUT_DIR) \
		--output-dir $(REGISTRY_OUTPUT_DIR) \
		--prefix $(REGISTRY_PREFIX) \
		--dry-run

# Use PHI-scrubbed final data (recommended for production)
registry-prep-final:
	$(MAKE) registry-prep REGISTRY_INPUT_DIR=data/knowledge/golden_extractions_final

# Use raw golden extractions (for development/testing)
registry-prep-raw:
	$(MAKE) registry-prep REGISTRY_INPUT_DIR=data/knowledge/golden_extractions

# Alternative: Use the module integration
registry-prep-module:
	$(CONDA_ACTIVATE) && $(PYTHON) -c " \
from ml.lib.ml_coder.registry_data_prep import prepare_registry_training_splits; \
train, val, test = prepare_registry_training_splits(); \
train.to_csv('$(REGISTRY_OUTPUT_DIR)/$(REGISTRY_PREFIX)_train.csv', index=False); \
val.to_csv('$(REGISTRY_OUTPUT_DIR)/$(REGISTRY_PREFIX)_val.csv', index=False); \
test.to_csv('$(REGISTRY_OUTPUT_DIR)/$(REGISTRY_PREFIX)_test.csv', index=False); \
print(f'Train: {len(train)}, Val: {len(val)}, Test: {len(test)}')"

# Test the data prep module
test-registry-prep:
	$(CONDA_ACTIVATE) && pytest tests/ml_coder/test_registry_first_data_prep.py -v
