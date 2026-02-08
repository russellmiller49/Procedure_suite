from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_eval_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "ops" / "tools" / "eval_reporter_gold_dataset.py"
    spec = importlib.util.spec_from_file_location("eval_reporter_gold_dataset", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_eval_metrics_and_section_checks() -> None:
    mod = _load_eval_module()

    full_shell = "\n".join(
        [
            "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT",
            "INDICATION FOR OPERATION",
            "CONSENT",
            "PREOPERATIVE DIAGNOSIS",
            "POSTOPERATIVE DIAGNOSIS",
            "PROCEDURE",
            "ANESTHESIA",
            "MONITORING",
            "COMPLICATIONS",
            "PROCEDURE IN DETAIL",
            "IMPRESSION / PLAN",
        ]
    )

    rows = [
        mod.EvaluationRow(id="case1", input_text="short1", ideal_output=full_shell),
        mod.EvaluationRow(id="case2", input_text="short2", ideal_output=full_shell),
    ]

    outputs = {
        "short1": full_shell,  # perfect
        "short2": "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT\nPROCEDURE",  # missing sections
    }

    report = mod.evaluate_rows(rows, render_report=lambda text: outputs[text])
    summary = report["summary"]
    per_case = {row["id"]: row for row in report["per_case"]}

    assert summary["total_cases"] == 2
    assert summary["failed_cases"] == 0
    assert 0.0 <= summary["avg_similarity"] <= 1.0
    assert 0.0 <= summary["min_similarity"] <= 1.0
    assert per_case["case1"]["missing_sections_generated"] == []
    assert "CONSENT" in per_case["case2"]["missing_sections_generated"]


def test_to_eval_rows_uses_ideal_output_candidate_fallback() -> None:
    mod = _load_eval_module()

    raw = [
        {"id": "a", "input_text": "x", "ideal_output_candidate": "y"},
        {"id": "b", "input_text": "", "ideal_output_candidate": "z"},  # ignored: empty input
    ]
    rows = mod.to_eval_rows(raw)
    assert len(rows) == 1
    assert rows[0].id == "a"
    assert rows[0].ideal_output == "y"
