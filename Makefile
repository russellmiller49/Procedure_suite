SHELL := /bin/bash
.PHONY: setup lint typecheck test validate-schemas validate-kb autopatch autocommit codex-train codex-metrics run-coder dev-iu pull-model-pytorch

# Use conda environment medparse-py311 (Python 3.11)
CONDA_ACTIVATE := source ~/miniconda3/etc/profile.d/conda.sh && conda activate medparse-py311
SETUP_STAMP := .setup.stamp
PYTHON := python
KB_PATH := data/knowledge/ip_coding_billing_v2_8.json
SCHEMA_PATH := data/knowledge/IP_Registry.json
NOTES_PATH := data/knowledge/synthetic_notes_with_registry2.json
PORT ?= 8000
MODEL_BACKEND ?= pytorch
PROCSUITE_SKIP_WARMUP ?= 1
REGISTRY_RUNTIME_DIR ?= data/models/registry_runtime

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
	@echo "  autopatch      - Generate patches for registry cleaning"
	@echo "  autocommit     - Git commit generated files"
	@echo "  codex-train    - Full training pipeline"
	@echo "  codex-metrics  - Run metrics over notes batch"
	@echo "  clean          - Remove generated files"
