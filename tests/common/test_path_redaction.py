from __future__ import annotations

from app.common.path_redaction import repo_relative_path, sanitize_path_fields


def test_repo_relative_path_strips_machine_local_repo_prefix() -> None:
    value = "/Users/russellmiller/Projects/Procedure_suite/tests/fixtures/example.json"

    assert repo_relative_path(value) == "tests/fixtures/example.json"


def test_repo_relative_path_drops_external_absolute_paths() -> None:
    assert repo_relative_path("/tmp/outside.json") is None


def test_sanitize_path_fields_recurses_nested_metadata() -> None:
    payload = {
        "input_path": "/Users/russellmiller/Projects/Procedure_suite/tests/fixtures/example.json",
        "metadata": {
            "seed_fixture_path": "/Users/russellmiller/Projects/Procedure_suite/tests/fixtures/seed.json",
            "other": "kept",
        },
        "items": [
            {"left_report_path": "/Users/russellmiller/Projects/Procedure_suite/reports/a.json"},
            {"right_report_path": "/tmp/report.json"},
        ],
    }

    sanitized = sanitize_path_fields(payload)

    assert sanitized["input_path"] == "tests/fixtures/example.json"
    assert sanitized["metadata"]["seed_fixture_path"] == "tests/fixtures/seed.json"
    assert sanitized["items"][0]["left_report_path"] == "reports/a.json"
    assert sanitized["items"][1]["right_report_path"] is None
