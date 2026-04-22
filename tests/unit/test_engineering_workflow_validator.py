from __future__ import annotations

from pathlib import Path

from ops.engineering_workflow.contracts import CommandResult, ValidationFailureCategory
from ops.engineering_workflow.validator import classify_failure, is_allowed_command


def _write_result_files(tmp_path: Path, name: str, stdout: str, stderr: str) -> tuple[str, str]:
    stdout_path = tmp_path / f"{name}.stdout.txt"
    stderr_path = tmp_path / f"{name}.stderr.txt"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    return str(stdout_path), str(stderr_path)


def test_allowed_commands_accept_repo_safe_prefixes() -> None:
    assert is_allowed_command(["pytest", "-q"]) is True
    assert is_allowed_command(["make", "test"]) is True
    assert is_allowed_command(["/usr/bin/python3", "ops/tools/run_quality_gates.py", "--tier", "pr"]) is True
    assert is_allowed_command(["bash", "-lc", "rm -rf /"]) is False


def test_classify_failure_detects_preexisting_environment_and_syntax(tmp_path: Path) -> None:
    baseline_stdout, baseline_stderr = _write_result_files(tmp_path, "baseline", "", "already failing\n")
    current_stdout, current_stderr = _write_result_files(tmp_path, "current", "", "already failing\n")
    syntax_stdout, syntax_stderr = _write_result_files(tmp_path, "syntax", "", "SyntaxError in module.py\n")
    env_stdout, env_stderr = _write_result_files(tmp_path, "env", "", "command not found\n")

    baseline_result = CommandResult(
        name="pytest",
        command=["pytest", "-q"],
        returncode=1,
        stdout_path=baseline_stdout,
        stderr_path=baseline_stderr,
        phase="baseline",
    )
    current_result = CommandResult(
        name="pytest",
        command=["pytest", "-q"],
        returncode=1,
        stdout_path=current_stdout,
        stderr_path=current_stderr,
        phase="slice",
    )
    syntax_result = CommandResult(
        name="pytest",
        command=["pytest", "-q"],
        returncode=1,
        stdout_path=syntax_stdout,
        stderr_path=syntax_stderr,
        phase="slice",
    )
    env_result = CommandResult(
        name="pytest",
        command=["pytest", "-q"],
        returncode=1,
        stdout_path=env_stdout,
        stderr_path=env_stderr,
        phase="slice",
    )

    preexisting = classify_failure(
        baseline_results=[baseline_result],
        current_results=[current_result],
        changed_files=[],
    )
    syntax = classify_failure(
        baseline_results=[],
        current_results=[syntax_result],
        changed_files=["app/module.py"],
    )
    env = classify_failure(
        baseline_results=[],
        current_results=[env_result],
        changed_files=[],
    )

    assert preexisting.category == ValidationFailureCategory.PREEXISTING_UNRELATED_FAILURE
    assert syntax.category == ValidationFailureCategory.TOUCHED_FILE_SYNTAX_IMPORT_FAILURE
    assert syntax.repair_eligible is True
    assert env.category == ValidationFailureCategory.ENVIRONMENTAL_FAILURE
    assert env.repair_eligible is False

