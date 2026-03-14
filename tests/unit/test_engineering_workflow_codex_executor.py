from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ops.engineering_workflow.codex_executor import CodexCliExecutor


class _CompletedProcess:
    def __init__(self, stdout: str, stderr: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_codex_executor_parses_valid_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: _CompletedProcess(
            '{"schema_version":"proc_suite.engineering_workflow.v1","status":"implemented","summary":"done"}'
        ),
    )

    executor = CodexCliExecutor(executable="codex")
    result = executor.run(prompt="{}", repo_root=tmp_path, artifact_dir=tmp_path, task_id="slice_1")

    assert result.payload.status == "implemented"
    assert result.payload.summary == "done"


def test_codex_executor_rejects_invalid_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: _CompletedProcess("not-json"))

    executor = CodexCliExecutor(executable="codex")
    with pytest.raises(RuntimeError, match="valid JSON"):
        executor.run(prompt="{}", repo_root=tmp_path, artifact_dir=tmp_path, task_id="slice_1")

