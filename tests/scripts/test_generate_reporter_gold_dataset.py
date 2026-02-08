from __future__ import annotations

import json
from pathlib import Path

from ml.scripts import generate_reporter_gold_dataset as gen


def _write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f)


def test_collect_source_records_filters_syn_and_requires_anchor(tmp_path: Path) -> None:
    input_dir = tmp_path / "notes"
    input_dir.mkdir()

    _write_json(
        input_dir / "A100.json",
        {
            "A100_syn_1": "short v1",
            "A100_syn_2": "short v2",
            "A100": "canonical anchor",
            "A100_style_1": "style variant should be ignored",
        },
    )
    _write_json(
        input_dir / "B200.json",
        {
            "B200_syn_1": "has no anchor",
            "B200_style_1": "ignored style",
        },
    )

    records, skipped = gen.collect_source_records(input_dir)

    ids = [r.input_note_id for r in records]
    assert ids == ["A100_syn_1", "A100_syn_2"]
    assert all(r.anchor_note_id == "A100" for r in records)
    assert all(r.anchor_text == "canonical anchor" for r in records)
    assert any(item.get("reason") == "missing_anchor" for item in skipped)


def test_stratified_sample_is_deterministic(tmp_path: Path) -> None:
    # Build deterministic synthetic source records with pre-assigned families.
    records = []
    for i in range(6):
        family = "pleural" if i < 3 else "navigation"
        records.append(
            gen.SourceRecord(
                source_file=f"F{i}.json",
                patient_base_id=f"P{i}",
                input_note_id=f"P{i}_syn_1",
                input_text=f"text {i}",
                anchor_note_id=f"P{i}",
                anchor_text=f"anchor {i}",
                procedure_family=family,
            )
        )

    sample_a = gen.stratified_sample_records(records, sample_size=4, seed=42)
    sample_b = gen.stratified_sample_records(records, sample_size=4, seed=42)

    assert [r.input_note_id for r in sample_a] == [r.input_note_id for r in sample_b]
    assert len(sample_a) == 4


def test_section_headers_artifacts_and_placeholder_policy() -> None:
    bad_report = "\n".join(
        [
            "INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT",
            "INDICATION FOR OPERATION",
            "CONSENT",
            "PROCEDURE",
            "ANESTHESIA",
            "IMPRESSION / PLAN",
            "This has TODO and literal None and {{bad}}.",
            "Unknown placeholder [NOT_ALLOWED] appears here.",
        ]
    )

    missing = gen.find_missing_sections(bad_report)
    artifacts = gen.find_forbidden_artifacts(bad_report)
    disallowed = gen.find_disallowed_placeholders(bad_report)

    assert "PREOPERATIVE DIAGNOSIS" in missing
    assert "literal_none" in artifacts
    assert "todo" in artifacts
    assert "jinja_open" in artifacts
    assert "NOT_ALLOWED" in disallowed


def test_build_review_queue_includes_all_rejects_plus_10_percent_pass_sample() -> None:
    accepted = [
        {
            "id": f"a{i}",
            "accepted": True,
            "judge_scores": {"factuality": 0.95, "completeness": 0.9, "style": 0.91},
            "judge_verdict": "accept",
            "reject_reasons": [],
        }
        for i in range(20)
    ]
    rejected = [
        {
            "id": f"r{i}",
            "accepted": False,
            "judge_scores": {"factuality": 0.4, "completeness": 0.5, "style": 0.6},
            "judge_verdict": "reject",
            "reject_reasons": ["judge_rejected"],
        }
        for i in range(3)
    ]

    queue = gen.build_review_queue(
        accepted_rows=accepted,
        rejected_rows=rejected,
        seed=42,
        pass_fraction=0.10,
    )

    reject_ids = {row["id"] for row in rejected}
    queue_ids = {row["id"] for row in queue}
    assert reject_ids.issubset(queue_ids)

    pass_samples = [row for row in queue if row.get("review_reason") == "pass_sample"]
    assert len(pass_samples) == 2  # 10% of 20
    assert len(queue) == 3 + 2

