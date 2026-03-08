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
    assert mod.FULL_REPORTER_FALLBACK_BASELINE.name == "reporter_seed_dual_path_full_fallback_summary_baseline.json"


def test_run_quality_gates_pr_writes_summary_on_gate_failure(tmp_path: Path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    mod = _load_module("run_quality_gates_gate_failure_module", repo_root / "ops" / "tools" / "run_quality_gates.py")

    for name in (
        "PR_EXTRACTION_BASELINE",
        "PR_REPORTER_BASELINE",
        "PR_REPORTER_LLM_BASELINE",
        "PR_REPORTER_COMPARE_BASELINE",
        "PR_REPORTER_FALLBACK_BASELINE",
    ):
        baseline_path = tmp_path / f"{name.lower()}.json"
        baseline_path.write_text(json.dumps({"summary": {"failed_cases": 0, "pass_rate": 1.0}, "counts": {}}), encoding="utf-8")
        monkeypatch.setattr(mod, name, baseline_path)

    def fake_run_command(*, name: str, command: list[str], output_dir: Path, env=None):  # noqa: ANN001
        stdout_path = output_dir / f"{name}.stdout.txt"
        stderr_path = output_dir / f"{name}.stderr.txt"
        stdout_path.write_text(f"{name} ran\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")

        output_path = None
        if "--output" in command:
            output_path = Path(command[command.index("--output") + 1])
            if name == "extraction_eval":
                payload = {"summary": {"failed_cases": 1, "pass_rate": 0.5}}
            elif name in {"reporter_seed_registry_eval", "reporter_seed_llm_eval"}:
                payload = {"summary": {"failed_cases": 0, "forbidden_artifact_case_rate": 0.0}}
            elif name == "reporter_seed_fallback_summary":
                payload = {"counts": {"left_fallback_cases": 1, "right_fallback_cases": 1}}
            else:
                payload = {"counts": {"critical_presence_mismatch_cases": 0, "right_worse_fallback_cases": 0}}
            output_path.write_text(json.dumps(payload), encoding="utf-8")

        return mod.StepResult(
            name=name,
            status="passed",
            command=command,
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            output_path=str(output_path) if output_path else None,
            returncode=0,
        )

    monkeypatch.setattr(mod, "_run_command", fake_run_command)

    exit_code = mod.run_pr(tmp_path)

    assert exit_code == 1
    summary_json = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    summary_md = (tmp_path / "summary.md").read_text(encoding="utf-8")
    extraction_step = next(step for step in summary_json["steps"] if step["name"] == "extraction_eval")
    assert extraction_step["status"] == "failed"
    assert "Extraction fixture gate failed" in str(extraction_step["error"])
    assert Path(extraction_step["stdout_path"]).exists()
    assert "Extraction fixture gate failed" in Path(extraction_step["stderr_path"]).read_text(encoding="utf-8")
    fallback_step = next(step for step in summary_json["steps"] if step["name"] == "reporter_seed_fallback_summary")
    assert fallback_step["status"] == "passed"
    assert "extraction_eval" in summary_md


def test_run_quality_gates_pr_writes_summary_on_command_failure(tmp_path: Path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    mod = _load_module("run_quality_gates_command_failure_module", repo_root / "ops" / "tools" / "run_quality_gates.py")

    for name in (
        "PR_EXTRACTION_BASELINE",
        "PR_REPORTER_BASELINE",
        "PR_REPORTER_LLM_BASELINE",
        "PR_REPORTER_COMPARE_BASELINE",
        "PR_REPORTER_FALLBACK_BASELINE",
    ):
        baseline_path = tmp_path / f"{name.lower()}.json"
        baseline_path.write_text(json.dumps({"summary": {"failed_cases": 0, "pass_rate": 1.0}, "counts": {}}), encoding="utf-8")
        monkeypatch.setattr(mod, name, baseline_path)

    def fake_run_command(*, name: str, command: list[str], output_dir: Path, env=None):  # noqa: ANN001
        stdout_path = output_dir / f"{name}.stdout.txt"
        stderr_path = output_dir / f"{name}.stderr.txt"
        stdout_path.write_text(f"{name} ran\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        output_path = None

        if name == "reporter_seed_registry_eval":
            stderr_path.write_text("boom\n", encoding="utf-8")
            return mod.StepResult(
                name=name,
                status="failed",
                command=command,
                stdout_path=str(stdout_path),
                stderr_path=str(stderr_path),
                returncode=2,
                error="command failed with exit code 2",
            )

        if "--output" in command:
            output_path = Path(command[command.index("--output") + 1])
            if name == "extraction_eval":
                payload = {"summary": {"failed_cases": 0, "pass_rate": 1.0}}
            elif name == "reporter_seed_llm_eval":
                payload = {"summary": {"failed_cases": 0, "forbidden_artifact_case_rate": 0.0}}
            elif name == "reporter_seed_fallback_summary":
                payload = {"counts": {"left_fallback_cases": 0, "right_fallback_cases": 0}}
            else:
                payload = {"counts": {"critical_presence_mismatch_cases": 0, "right_worse_fallback_cases": 0}}
            output_path.write_text(json.dumps(payload), encoding="utf-8")

        return mod.StepResult(
            name=name,
            status="passed",
            command=command,
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            output_path=str(output_path) if output_path else None,
            returncode=0,
        )

    monkeypatch.setattr(mod, "_run_command", fake_run_command)

    exit_code = mod.run_pr(tmp_path)

    assert exit_code == 1
    summary_json = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    registry_step = next(step for step in summary_json["steps"] if step["name"] == "reporter_seed_registry_eval")
    fallback_step = next(step for step in summary_json["steps"] if step["name"] == "reporter_seed_fallback_summary")
    assert registry_step["status"] == "failed"
    assert registry_step["returncode"] == 2
    assert Path(registry_step["stdout_path"]).exists()
    assert Path(registry_step["stderr_path"]).read_text(encoding="utf-8") == "boom\n"
    assert fallback_step["status"] == "failed"
