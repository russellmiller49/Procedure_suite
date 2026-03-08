from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


def _load_eval_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "ml" / "scripts" / "eval_golden.py"
    spec = importlib.util.spec_from_file_location("eval_golden", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_eval_golden_main_writes_shared_report_shape(tmp_path) -> None:
    mod = _load_eval_module()

    input_path = tmp_path / "unified_quality_corpus.json"
    input_path.write_text(json.dumps({"cases": [{"id": "case1", "note_text": "note"}]}), encoding="utf-8")
    output_path = tmp_path / "report.json"

    fake_report = {
        "schema_version": "procedure_suite.quality_eval.v1",
        "kind": "extraction",
        "input_path": str(input_path),
        "output_path": None,
        "source_format": "unified_quality_corpus",
        "corpus_name": "unified_quality_corpus",
        "created_at": "2026-03-08T00:00:00+00:00",
        "runtime": {"extraction_engine": "parallel_ner"},
        "summary": {
            "total_cases": 1,
            "passed_cases": 1,
            "failed_cases": 0,
            "pass_rate": 1.0,
            "metrics": {"exact_code_match_cases": 1, "exact_code_match_rate": 1.0},
            "exact_code_match_cases": 1,
            "exact_code_match_rate": 1.0,
        },
        "per_case": [{"id": "case1", "status": "passed", "tags": [], "metrics": {}, "actual": {}, "failures": []}],
        "failures": [],
    }

    mod._evaluate_unified_quality_corpus = lambda **_: {"exit_code": 0, "report": dict(fake_report)}  # type: ignore[attr-defined]

    exit_code = mod.main(["--input", str(input_path), "--output", str(output_path)])
    assert exit_code == 0

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["schema_version"] == "procedure_suite.quality_eval.v1"
    assert written["kind"] == "extraction"
    assert set(written) == {
        "schema_version",
        "kind",
        "input_path",
        "output_path",
        "source_format",
        "corpus_name",
        "created_at",
        "runtime",
        "summary",
        "per_case",
        "failures",
    }
