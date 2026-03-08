from __future__ import annotations

from pathlib import Path

from app.common.quality_gate_reports import build_report_delta, render_delta_markdown, write_json


def test_build_report_delta_uses_summary_and_counts(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    write_json(
        baseline,
        {
            "summary": {"pass_rate": 1.0, "avg_cpt_jaccard": 0.8},
            "counts": {"critical_presence_mismatch_cases": 0},
        },
    )
    write_json(
        current,
        {
            "summary": {"pass_rate": 0.9, "avg_cpt_jaccard": 0.85},
            "counts": {"critical_presence_mismatch_cases": 1},
        },
    )

    delta = build_report_delta(current_path=current, baseline_path=baseline)

    assert delta["comparable_metric_count"] == 3
    assert delta["current_path"] is None
    assert delta["baseline_path"] is None
    metrics = {item["metric"]: item for item in delta["metrics"]}
    assert metrics["summary.pass_rate"]["delta"] == -0.1
    assert metrics["summary.avg_cpt_jaccard"]["delta"] == 0.05
    assert metrics["counts.critical_presence_mismatch_cases"]["delta"] == 1.0


def test_render_delta_markdown_highlights_changed_metrics(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    current = tmp_path / "current.json"
    write_json(baseline, {"summary": {"failed_cases": 0}})
    write_json(current, {"summary": {"failed_cases": 2}})

    delta = build_report_delta(current_path=current, baseline_path=baseline)
    markdown = render_delta_markdown(delta, title="Nightly Delta")

    assert "Nightly Delta" in markdown
    assert "summary.failed_cases" in markdown
    assert "delta `2.0`" in markdown
    assert "Baseline: `None`" in markdown
