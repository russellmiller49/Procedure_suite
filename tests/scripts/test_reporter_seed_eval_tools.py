from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_reporter_seed_eval_scripts_share_schema(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    input_path = repo_root / "tests" / "fixtures" / "reporter_seed_eval_samples.json"
    llm_seed_fixture = repo_root / "tests" / "fixtures" / "reporter_seed_eval_llm_fixture.json"
    baseline_script = repo_root / "ops" / "tools" / "eval_reporter_prompt_baseline.py"
    llm_script = repo_root / "ops" / "tools" / "eval_reporter_prompt_llm_findings.py"

    baseline_output = tmp_path / "baseline.json"
    llm_output = tmp_path / "llm.json"

    baseline_run = subprocess.run(
        [
            str(repo_root / ".venv" / "bin" / "python"),
            str(baseline_script),
            "--input",
            str(input_path),
            "--output",
            str(baseline_output),
            "--strict",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert baseline_run.returncode == 0, (baseline_run.stdout or "") + (baseline_run.stderr or "")

    llm_run = subprocess.run(
        [
            str(repo_root / ".venv" / "bin" / "python"),
            str(llm_script),
            "--input",
            str(input_path),
            "--output",
            str(llm_output),
            "--seed-fixture",
            str(llm_seed_fixture),
            "--strict",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert llm_run.returncode == 0, (llm_run.stdout or "") + (llm_run.stderr or "")

    baseline_payload = json.loads(baseline_output.read_text(encoding="utf-8"))
    llm_payload = json.loads(llm_output.read_text(encoding="utf-8"))

    shared_top_level = {
        "schema_version",
        "kind",
        "seed_path",
        "input_path",
        "output_path",
        "prompt_field",
        "row_count",
        "created_at",
        "environment_defaults_applied",
        "metadata",
        "summary",
        "per_case",
        "failures",
    }
    assert set(baseline_payload) == shared_top_level
    assert set(llm_payload) == shared_top_level

    assert baseline_payload["seed_path"] == "registry_extract_fields"
    assert llm_payload["seed_path"] == "llm_findings"
    assert baseline_payload["input_path"] == "tests/fixtures/reporter_seed_eval_samples.json"
    assert baseline_payload["output_path"] is None
    assert llm_payload["metadata"]["seed_fixture_path"] == "tests/fixtures/reporter_seed_eval_llm_fixture.json"
    assert baseline_payload["metadata"]["production_default"] is True
    assert llm_payload["metadata"]["challenger_only"] is True
    assert baseline_payload["summary"]["strict_render_fallback_rate"] < 1.0
    assert llm_payload["summary"]["strict_render_fallback_rate"] < 1.0
    assert isinstance(baseline_payload["summary"]["fallback_reason_counts"], dict)
    assert isinstance(llm_payload["summary"]["fallback_reason_counts"], dict)

    baseline_case_keys = set(baseline_payload["per_case"][0])
    llm_case_keys = set(llm_payload["per_case"][0])
    assert baseline_case_keys == llm_case_keys

    required_case_keys = {
        "id",
        "seed_path",
        "text_similarity",
        "missing_sections",
        "cpt_jaccard",
        "performed_flag_f1",
        "critical_extra_flags",
        "critical_predicted_flags",
        "predicted_cpt_codes",
        "render_fallback_used",
        "render_fallback_reason",
        "render_fallback_category",
        "render_fallback_details",
        "seed_warning_count",
        "quality_flag_codes",
        "needs_review",
        "accepted_findings",
        "dropped_findings",
        "drop_reason_counts",
        "error",
        "error_code",
    }
    assert required_case_keys <= baseline_case_keys


def test_compare_reporter_seed_paths_script(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    compare_script = repo_root / "ops" / "tools" / "compare_reporter_seed_paths.py"

    left_report = tmp_path / "left.json"
    right_report = tmp_path / "right.json"
    output = tmp_path / "compare.json"

    left_report.write_text(
        json.dumps(
            {
                "seed_path": "registry_extract_fields",
                "summary": {
                    "avg_cpt_jaccard": 0.5,
                    "avg_performed_flag_f1": 0.7,
                    "avg_text_similarity": 0.8,
                    "required_section_coverage": 1.0,
                    "critical_extra_flag_rate": 0.0,
                    "strict_render_fallback_rate": 0.0,
                    "forbidden_artifact_case_rate": 0.0,
                    "avg_seed_warning_count": 0.0,
                    "avg_accepted_findings": 0.0,
                    "avg_dropped_findings": 0.0,
                },
                "per_case": [
                    {
                        "id": "case_1",
                        "seed_path": "registry_extract_fields",
                        "cpt_jaccard": 0.5,
                        "performed_flag_f1": 0.7,
                        "critical_predicted_flags": ["procedures_performed.linear_ebus.performed"],
                        "render_fallback_used": False,
                        "forbidden_artifact_hits": [],
                        "seed_warning_count": 0,
                        "error": None,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    right_report.write_text(
        json.dumps(
            {
                "seed_path": "llm_findings",
                "summary": {
                    "avg_cpt_jaccard": 0.6,
                    "avg_performed_flag_f1": 0.7,
                    "avg_text_similarity": 0.8,
                    "required_section_coverage": 1.0,
                    "critical_extra_flag_rate": 0.0,
                    "strict_render_fallback_rate": 0.1,
                    "forbidden_artifact_case_rate": 0.0,
                    "avg_seed_warning_count": 1.0,
                    "avg_accepted_findings": 2.0,
                    "avg_dropped_findings": 1.0,
                },
                "per_case": [
                    {
                        "id": "case_1",
                        "seed_path": "llm_findings",
                        "cpt_jaccard": 0.6,
                        "performed_flag_f1": 0.7,
                        "critical_predicted_flags": ["procedures_performed.linear_ebus.performed"],
                        "render_fallback_used": True,
                        "forbidden_artifact_hits": [],
                        "seed_warning_count": 1,
                        "error": None,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            str(repo_root / ".venv" / "bin" / "python"),
            str(compare_script),
            "--left-report",
            str(left_report),
            "--right-report",
            str(right_report),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["left_seed_path"] == "registry_extract_fields"
    assert payload["right_seed_path"] == "llm_findings"
    assert payload["left_report_path"] is None
    assert payload["right_report_path"] is None
    assert payload["summary_diff"]["avg_cpt_jaccard"]["delta"] == 0.1
    assert payload["counts"]["right_worse_fallback_cases"] == 1
    assert payload["per_case_diff"][0]["right"]["render_fallback_reason"] is None


def test_summarize_reporter_seed_fallbacks_script(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    summarize_script = repo_root / "ops" / "tools" / "summarize_reporter_seed_fallbacks.py"

    left_report = tmp_path / "left.json"
    right_report = tmp_path / "right.json"
    output = tmp_path / "fallbacks.json"

    left_report.write_text(
        json.dumps(
            {
                "seed_path": "registry_extract_fields",
                "per_case": [
                    {"id": "case_1", "render_fallback_used": True, "render_fallback_reason": "missing_tbna_details"},
                    {"id": "case_2", "render_fallback_used": False, "render_fallback_reason": None},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    right_report.write_text(
        json.dumps(
            {
                "seed_path": "llm_findings",
                "per_case": [
                    {"id": "case_1", "render_fallback_used": True, "render_fallback_reason": "missing_tbna_details"},
                    {"id": "case_2", "render_fallback_used": True, "render_fallback_reason": "missing_bal_location"},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            str(repo_root / ".venv" / "bin" / "python"),
            str(summarize_script),
            "--left-report",
            str(left_report),
            "--right-report",
            str(right_report),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["left_report_path"] is None
    assert payload["right_report_path"] is None
    assert payload["counts"]["left_fallback_cases"] == 1
    assert payload["counts"]["right_fallback_cases"] == 2
    by_reason = {item["reason"]: item for item in payload["reasons"]}
    assert by_reason["missing_tbna_details"]["left_count"] == 1
    assert by_reason["missing_tbna_details"]["right_count"] == 1
    assert by_reason["missing_bal_location"]["right_cases"] == ["case_2"]
