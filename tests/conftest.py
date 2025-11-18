import pytest

from proc_report import engine as report_engine


def _fake_umls_link(_: str):
    return [{"cui": "C000000", "text": "stub"}]


@pytest.fixture(autouse=True)
def stub_umls(monkeypatch):
    monkeypatch.setattr(report_engine, "umls_link", _fake_umls_link)
    yield
