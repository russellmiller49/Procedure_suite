import os

import pytest

from modules.reporting import engine as report_engine

# Keep tests offline-friendly by default.
os.environ.setdefault("REGISTRY_USE_STUB_LLM", "1")
os.environ.setdefault("GEMINI_OFFLINE", "1")
os.environ.setdefault("DISABLE_STATIC_FILES", "1")


def _fake_umls_link(_: str):
    return [{"cui": "C000000", "text": "stub"}]


@pytest.fixture(autouse=True)
def stub_umls(monkeypatch):
    monkeypatch.setattr(report_engine, "umls_link", _fake_umls_link)
    yield
