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
	$(CONDA_ACTIVATE) && pytest tests/ml_coder/test_registry_data_prep.py -v

# ==============================================================================
# Complete Registry-First Training Workflow
# ==============================================================================
# Run these in order for a complete training cycle:
#
#   1. make platinum-final        # PHI-scrub golden JSONs
#   2. make registry-prep-final   # Convert to ML CSVs  
#   3. make registry-train        # Train the model
#   4. make registry-eval         # Evaluate model
#
# The registry-train target should be defined in your training script section.
