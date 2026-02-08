from __future__ import annotations

import logging

import pytest

from config.startup_settings import StartupSettings


def test_startup_settings_accept_extraction_first_non_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.delenv("CODER_REQUIRE_PHI_REVIEW", raising=False)
    monkeypatch.setenv("PROCSUITE_ENV", "development")
    StartupSettings().validate_runtime_contract()


@pytest.mark.parametrize("mode", ["parallel_ner", "current", ""])
def test_startup_settings_rejects_non_extraction_first_modes(
    mode: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", mode)
    with pytest.raises(RuntimeError, match="PROCSUITE_PIPELINE_MODE"):
        StartupSettings().validate_runtime_contract()


def test_startup_settings_enforces_production_invariants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "engine")
    monkeypatch.setenv("REGISTRY_SCHEMA_VERSION", "v2")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "legacy")

    with pytest.raises(RuntimeError, match="REGISTRY_EXTRACTION_ENGINE"):
        StartupSettings().validate_runtime_contract()


def test_startup_settings_allows_production_engine_override_with_warning(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING)
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("CODER_REQUIRE_PHI_REVIEW", "true")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "engine")
    monkeypatch.setenv("PROCSUITE_ALLOW_REGISTRY_ENGINE_OVERRIDE", "true")
    monkeypatch.setenv("REGISTRY_SCHEMA_VERSION", "v3")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")

    StartupSettings().validate_runtime_contract()

    assert "Production override enabled" in caplog.text
