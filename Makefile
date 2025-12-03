.PHONY: setup lint typecheck test validate-schemas validate-kb autopatch autocommit codex-train

SETUP_STAMP := .setup.stamp
VENV := .venv

setup:
	@if [ -f $(SETUP_STAMP) ]; then echo "Setup already done"; exit 0; fi
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt
	touch $(SETUP_STAMP)

lint:
	$(VENV)/bin/ruff --cache-dir .ruff_cache .

typecheck:
	$(VENV)/bin/mypy --cache-dir .mypy_cache .

test:
	$(VENV)/bin/pytest

validate-schemas:
	$(VENV)/bin/python scripts/validate_jsonschema.py
	$(VENV)/bin/python scripts/check_pydantic_models.py

validate-kb:
	$(VENV)/bin/python scripts/run_cleaning_pipeline.py --validate-kb

autopatch:
	$(VENV)/bin/python scripts/run_cleaning_pipeline.py --autopatch

autocommit:
	@git add .
	@git commit -m "Autocommit: generated patches/reports" || true

codex-train: setup lint typecheck test validate-schemas validate-kb autopatch
	@echo "Codex training pipeline complete"
