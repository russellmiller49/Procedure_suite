from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

from app.common.reporter_seed_eval import load_eval_rows


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_load_eval_rows_accepts_ideal_output(tmp_path: Path) -> None:
    input_path = tmp_path / "reporter_rows.json"
    input_path.write_text(
        json.dumps(
            [
                {
                    "id": "case_1",
                    "input_text": "Prompt text",
                    "ideal_output": "Canonical completion",
                }
            ]
        ),
        encoding="utf-8",
    )

    rows = load_eval_rows(input_path, prompt_field="input_text")

    assert len(rows) == 1
    assert rows[0].id == "case_1"
    assert rows[0].prompt_text == "Prompt text"
    assert rows[0].completion_canonical == "Canonical completion"


def test_run_quality_gates_pr_targets_cover_required_suites() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    mod = _load_module("run_quality_gates_module", repo_root / "ops" / "tools" / "run_quality_gates.py")

    assert "tests/registry/test_regression_pack.py" in mod.PR_PYTEST_TARGETS
    assert "tests/quality/test_unified_quality_matrix.py" in mod.PR_PYTEST_TARGETS
    assert "tests/quality/test_reporter_seed_dual_path_matrix.py" in mod.PR_PYTEST_TARGETS
    assert mod.PR_EXTRACTION_INPUT.name == "unified_quality_corpus.json"
    assert mod.PR_REPORTER_INPUT.name == "reporter_seed_eval_samples.json"


def test_run_quality_gates_nightly_uses_full_reporter_fixture_paths() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    mod = _load_module("run_quality_gates_nightly_module", repo_root / "ops" / "tools" / "run_quality_gates.py")

    assert mod.FULL_REPORTER_INPUT.name == "reporter_golden_dataset.json"
    assert mod.FULL_REPORTER_PROMPT_FIELD == "input_text"
    assert mod.FULL_REPORTER_LLM_FIXTURE.name == "reporter_seed_eval_llm_fixture_full.json"
    assert mod.FULL_REPORTER_COMPARE_BASELINE.name == "reporter_seed_dual_path_full_compare_baseline.json"
