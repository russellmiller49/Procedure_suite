from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_run_quality_gates_pr_targets_cover_required_suites() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    mod = _load_module("run_quality_gates_module", repo_root / "ops" / "tools" / "run_quality_gates.py")

    assert "tests/registry/test_regression_pack.py" in mod.PR_PYTEST_TARGETS
    assert "tests/registry/test_header_evidence_integrity.py" in mod.PR_PYTEST_TARGETS
    assert "tests/scripts/test_eval_golden.py" in mod.PR_PYTEST_TARGETS
    assert mod.PR_EXTRACTION_INPUT.name == "unified_quality_corpus.json"
    assert mod.PR_EXTRACTION_BASELINE.name == "unified_quality_corpus_extraction_baseline.json"


def test_run_quality_gates_pr_writes_summary_on_gate_failure(tmp_path: Path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    mod = _load_module("run_quality_gates_gate_failure_module", repo_root / "ops" / "tools" / "run_quality_gates.py")

    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps({"summary": {"failed_cases": 0, "pass_rate": 1.0}}), encoding="utf-8")
    monkeypatch.setattr(mod, "PR_EXTRACTION_BASELINE", baseline_path)

    def fake_run_command(*, name: str, command: list[str], output_dir: Path, env=None):  # noqa: ANN001
        stdout_path = output_dir / f"{name}.stdout.txt"
        stderr_path = output_dir / f"{name}.stderr.txt"
        stdout_path.write_text(f"{name} ran\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")

        output_path = None
        if "--output" in command:
            output_path = Path(command[command.index("--output") + 1])
            payload = {"summary": {"failed_cases": 1, "pass_rate": 0.5}}
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
    assert "extraction_eval" in summary_md


def test_run_quality_gates_pr_writes_summary_on_command_failure(tmp_path: Path, monkeypatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    mod = _load_module("run_quality_gates_command_failure_module", repo_root / "ops" / "tools" / "run_quality_gates.py")

    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(json.dumps({"summary": {"failed_cases": 0, "pass_rate": 1.0}}), encoding="utf-8")
    monkeypatch.setattr(mod, "PR_EXTRACTION_BASELINE", baseline_path)

    def fake_run_command(*, name: str, command: list[str], output_dir: Path, env=None):  # noqa: ANN001
        stdout_path = output_dir / f"{name}.stdout.txt"
        stderr_path = output_dir / f"{name}.stderr.txt"
        stdout_path.write_text(f"{name} ran\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")

        if name == "focused_pytest":
            stderr_path.write_text("pytest boom\n", encoding="utf-8")
            return mod.StepResult(
                name=name,
                status="failed",
                command=command,
                stdout_path=str(stdout_path),
                stderr_path=str(stderr_path),
                returncode=2,
                error="command failed with exit code 2",
            )

        output_path = None
        if "--output" in command:
            output_path = Path(command[command.index("--output") + 1])
            payload = {"summary": {"failed_cases": 0, "pass_rate": 1.0}}
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
    focused_step = next(step for step in summary_json["steps"] if step["name"] == "focused_pytest")
    extraction_step = next(step for step in summary_json["steps"] if step["name"] == "extraction_eval")
    assert focused_step["status"] == "failed"
    assert focused_step["returncode"] == 2
    assert Path(focused_step["stdout_path"]).exists()
    assert Path(focused_step["stderr_path"]).read_text(encoding="utf-8") == "pytest boom\n"
    assert extraction_step["status"] == "passed"
