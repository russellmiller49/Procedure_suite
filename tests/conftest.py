import atexit
import os
import shutil
import tempfile

# Isolate test-time storage from tracked repo files (phi_demo.db, data/coding_traces.jsonl).
# These paths are read at module import time, so they must be set before any app import.
# Assigned unconditionally so a developer shell exporting them cannot redirect test writes;
# individual tests may still override them with monkeypatch.
_TEST_STATE_DIR = tempfile.mkdtemp(prefix="procsuite-tests-")
atexit.register(shutil.rmtree, _TEST_STATE_DIR, ignore_errors=True)
os.environ["PROCSUITE_TEST_STATE_DIR"] = _TEST_STATE_DIR
_TEST_DB_URL = f"sqlite:///{os.path.join(_TEST_STATE_DIR, 'phi_test.db')}"
os.environ["PHI_DATABASE_URL"] = _TEST_DB_URL
os.environ["REGISTRY_STORE_DATABASE_URL"] = _TEST_DB_URL
os.environ["DATABASE_URL"] = _TEST_DB_URL
os.environ["TRACE_FILE_PATH"] = os.path.join(_TEST_STATE_DIR, "coding_traces.jsonl")

# Keep a safe baseline even for module-import time behavior.
# Per-test enforcement happens in `baseline_env` to avoid cross-test contamination.
os.environ.setdefault("PROCSUITE_SKIP_DOTENV", "1")
os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")
os.environ.setdefault("ENABLE_UMLS_LINKER", "false")
os.environ.setdefault("PROCSUITE_PIPELINE_MODE", "extraction_first")
os.environ.setdefault("REGISTRY_EXTRACTION_ENGINE", "engine")
os.environ.setdefault("REGISTRY_SCHEMA_VERSION", "v3")
os.environ.setdefault("REGISTRY_AUDITOR_SOURCE", "raw_ml")

import pytest  # noqa: E402  (env above must be set before app imports)

from app.reporting import engine as report_engine  # noqa: E402

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


# Fail the run if tests modify tracked storage files instead of the temp dir above.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GUARDED_TRACKED_FILES = ("phi_demo.db", os.path.join("data", "coding_traces.jsonl"))


def _file_digest(path: str) -> str | None:
    import hashlib

    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except FileNotFoundError:
        return None


_GUARDED_DIGESTS = {
    rel: _file_digest(os.path.join(_REPO_ROOT, rel)) for rel in _GUARDED_TRACKED_FILES
}


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    changed = [
        rel
        for rel, digest in _GUARDED_DIGESTS.items()
        if _file_digest(os.path.join(_REPO_ROOT, rel)) != digest
    ]
    if changed:
        session.config.get_terminal_writer().line(
            f"ERROR: tests modified tracked files: {', '.join(changed)}", red=True
        )
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
