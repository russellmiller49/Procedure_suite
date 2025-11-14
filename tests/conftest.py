import pytest

from proc_report import engine as report_engine


@pytest.fixture(autouse=True)
def stub_umls(monkeypatch):
    monkeypatch.setattr(report_engine, "umls_link", lambda text: [{"cui": "C000000", "text": "stub"}])
    yield
