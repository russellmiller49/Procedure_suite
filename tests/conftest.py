import os

# Keep a safe baseline even for module-import time behavior.
# Per-test enforcement happens in `baseline_env` to avoid cross-test contamination.
os.environ.setdefault("PROCSUITE_SKIP_DOTENV", "1")
os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")
os.environ.setdefault("ENABLE_UMLS_LINKER", "false")
os.environ.setdefault("PROCSUITE_PIPELINE_MODE", "extraction_first")
os.environ.setdefault("REGISTRY_EXTRACTION_ENGINE", "engine")
os.environ.setdefault("REGISTRY_SCHEMA_VERSION", "v3")
os.environ.setdefault("REGISTRY_AUDITOR_SOURCE", "raw_ml")

import pytest

from app.reporting import engine as report_engine

_BASELINE_TEST_ENV: dict[str, str] = {
    # Prevent local `.env` files from influencing tests (and avoid accidental real network calls).
    "PROCSUITE_SKIP_DOTENV": "1",
    # Avoid warmup threads importing optional heavyweight deps (e.g. scispacy/nmslib) in tests.
    "PROCSUITE_SKIP_WARMUP": "1",
    "ENABLE_UMLS_LINKER": "false",
    # Force the new canonical pipeline.
    "PROCSUITE_PIPELINE_MODE": "extraction_first",
    "REGISTRY_EXTRACTION_ENGINE": "engine",
    # Default API schema & audit behaviors for tests.
    "REGISTRY_SCHEMA_VERSION": "v3",
    "REGISTRY_AUDITOR_SOURCE": "raw_ml",
    # Keep legacy endpoints enabled in most tests (production can disable).
    "PROCSUITE_ALLOW_LEGACY_ENDPOINTS": "1",
    # PHI workflow defaults.
    "CODER_REQUIRE_PHI_REVIEW": "false",
    # Keep tests offline-friendly by default.
    "REGISTRY_USE_STUB_LLM": "1",
    "GEMINI_OFFLINE": "1",
    # Many UI tests expect static assets to be served.
    "DISABLE_STATIC_FILES": "0",
}


@pytest.fixture(autouse=True)
def baseline_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in _BASELINE_TEST_ENV.items():
        monkeypatch.setenv(key, value)


def _fake_umls_link(_: str):
    return [{"cui": "C000000", "text": "stub"}]


def _fake_umls_link_terms(_: object):
    return [{"cui": "C000000", "text": "stub"}]


@pytest.fixture(autouse=True)
def stub_umls(monkeypatch):
    # The reporting engine may expose different UMLS integration points over time.
    # Patch whichever is present to keep tests offline-friendly.
    if hasattr(report_engine, "umls_link"):
        monkeypatch.setattr(report_engine, "umls_link", _fake_umls_link)
    elif hasattr(report_engine, "_safe_umls_link"):
        monkeypatch.setattr(report_engine, "_safe_umls_link", _fake_umls_link)
    elif hasattr(report_engine, "_safe_umls_link_terms"):
        monkeypatch.setattr(report_engine, "_safe_umls_link_terms", _fake_umls_link_terms)
    yield
