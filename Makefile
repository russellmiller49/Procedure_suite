.PHONY: install test unit contracts integration lint preflight api tests type

install:
	pip install -e .

preflight:
	python -c "import spacy, sklearn; print('spaCy OK:', spacy.__version__); print('sklearn OK:', __import__('sklearn').__version__)"
	python scripts/preflight.py

unit:
	pytest -q tests/unit

contracts:
	pytest -q tests/contracts

integration:
	pytest -q tests/integration

test: unit contracts integration

lint:
	ruff check .

api:
	scripts/devserver.sh

tests:
	pytest -q

type:
	mypy modules

validate-registry:
	python scripts/validate_registry.py

analyze-registry-errors:
	python scripts/analyze_registry_errors.py

self-correct-registry:
	python scripts/self_correct_registry.py --field $(FIELD)
