.PHONY: install test unit contracts integration lint preflight

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
