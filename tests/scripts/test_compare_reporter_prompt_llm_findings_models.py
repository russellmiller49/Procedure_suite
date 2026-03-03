from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_compare_reporter_prompt_llm_findings_models_diff_only(tmp_path: Path) -> None:
    report_a = tmp_path / "report_a.json"
    report_b = tmp_path / "report_b.json"
    diff_path = tmp_path / "diff.json"

    report_a.write_text(
        json.dumps(
            {
                "summary": {
                    "required_section_coverage": 1.0,
                    "avg_cpt_jaccard": 0.2,
                    "avg_performed_flag_f1": 0.4,
                    "critical_extra_flag_rate": 0.01,
                    "avg_accepted_findings": 1.0,
                    "avg_dropped_findings": 0.5,
                },
                "per_case": [
                    {
                        "id": "case_1",
                        "cpt_jaccard": 0.0,
                        "performed_flag_f1": 0.2,
                        "accepted_findings": 1,
                        "dropped_findings": 0,
                        "critical_extra_flags": [],
                        "error": None,
                    },
                    {
                        "id": "case_2",
                        "cpt_jaccard": 0.4,
                        "performed_flag_f1": 0.8,
                        "accepted_findings": 2,
                        "dropped_findings": 1,
                        "critical_extra_flags": ["procedures_performed.therapeutic_aspiration.performed"],
                        "error": None,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    report_b.write_text(
        json.dumps(
            {
                "summary": {
                    "required_section_coverage": 1.0,
                    "avg_cpt_jaccard": 0.35,
                    "avg_performed_flag_f1": 0.45,
                    "critical_extra_flag_rate": 0.0,
                    "avg_accepted_findings": 1.5,
                    "avg_dropped_findings": 0.0,
                },
                "per_case": [
                    {
                        "id": "case_1",
                        "cpt_jaccard": 0.5,
                        "performed_flag_f1": 0.3,
                        "accepted_findings": 2,
                        "dropped_findings": 0,
                        "critical_extra_flags": [],
                        "error": None,
                    },
                    {
                        "id": "case_2",
                        "cpt_jaccard": 0.3,
                        "performed_flag_f1": 0.7,
                        "accepted_findings": 1,
                        "dropped_findings": 0,
                        "critical_extra_flags": [],
                        "error": None,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "ops" / "tools" / "compare_reporter_prompt_llm_findings_models.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--diff-only",
            "--report-a",
            str(report_a),
            "--report-b",
            str(report_b),
            "--diff-path",
            str(diff_path),
            "--output-dir",
            str(tmp_path),
            "--model-a",
            "gpt-5-mini",
            "--model-b",
            "gpt-5.2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (result.stdout or "") + (result.stderr or "")

    payload = json.loads(diff_path.read_text(encoding="utf-8"))
    assert payload["model_a"] == "gpt-5-mini"
    assert payload["model_b"] == "gpt-5.2"
    assert payload["summary_diff"]["avg_cpt_jaccard"]["delta"] == 0.15

    counts = payload["per_case_diff"]["counts"]
    assert counts["total_cases"] == 2
    assert counts["cpt_improved_cases"] == 1
    assert counts["cpt_worsened_cases"] == 1

    # Assertion mode should fail the run when delta is too small.
    result_fail = subprocess.run(
        [
            sys.executable,
            str(script),
            "--diff-only",
            "--report-a",
            str(report_a),
            "--report-b",
            str(report_b),
            "--diff-path",
            str(diff_path),
            "--output-dir",
            str(tmp_path),
            "--min-delta-avg-cpt-jaccard",
            "0.2",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result_fail.returncode == 3, (result_fail.stdout or "") + (result_fail.stderr or "")

