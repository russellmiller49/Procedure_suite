import pytest

from app.api import dependencies


def test_get_registry_service_skips_hybrid_bootstrap_in_extraction_first(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_SCHEMA_VERSION", "v3")

    dependencies.reset_registry_service_cache()

    def _raise_if_called(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError(
            "build_hybrid_orchestrator should not be called in extraction_first mode"
        )

    monkeypatch.setattr(dependencies, "build_hybrid_orchestrator", _raise_if_called)

    service = dependencies.get_registry_service()
    assert service.hybrid_orchestrator is None

    dependencies.reset_registry_service_cache()
