import os

# Prevent local `.env` files from influencing tests (and avoid accidental real network calls).
os.environ.setdefault("PROCSUITE_SKIP_DOTENV", "1")

import pytest

from modules.reporting import engine as report_engine

# Keep tests offline-friendly by default.
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
os.environ.setdefault("DISABLE_STATIC_FILES", "0")


def _fake_umls_link(_: str):
    return [{"cui": "C000000", "text": "stub"}]


@pytest.fixture(autouse=True)
def stub_umls(monkeypatch):
    # The reporting engine may expose different UMLS integration points over time.
    # Patch whichever is present to keep tests offline-friendly.
    if hasattr(report_engine, "umls_link"):
        monkeypatch.setattr(report_engine, "umls_link", _fake_umls_link)
    elif hasattr(report_engine, "_safe_umls_link"):
        monkeypatch.setattr(report_engine, "_safe_umls_link", _fake_umls_link)
    yield
