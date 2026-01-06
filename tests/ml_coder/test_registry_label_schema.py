from modules.ml_coder.registry_label_schema import REGISTRY_LABELS, validate_schema


def test_registry_label_schema_valid() -> None:
    validate_schema()


def test_registry_label_schema_count() -> None:
    assert len(REGISTRY_LABELS) == 29

