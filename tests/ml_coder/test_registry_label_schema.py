from modules.ml_coder.registry_label_schema import REGISTRY_LABELS, validate_schema
from modules.registry.v2_booleans import PROCEDURE_BOOLEAN_FIELDS


def test_registry_label_schema_valid() -> None:
    validate_schema()


def test_registry_label_schema_count() -> None:
    assert len(REGISTRY_LABELS) == len(PROCEDURE_BOOLEAN_FIELDS)
