from __future__ import annotations

import subprocess
from pathlib import Path

from ops.engineering_workflow.contracts import DiffBudget, TaskSlice
from ops.engineering_workflow.preflight import run_preflight
from ops.engineering_workflow.scope_guard import capture_workspace_snapshot, evaluate_scope


def _init_git_repo(repo_root: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
    (repo_root / "README.md").write_text("# Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_root, check=True, capture_output=True, text=True)


def test_preflight_blocks_dirty_repo_without_override(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    result = run_preflight(repo_root=tmp_path, session_id="abc123", allow_dirty=False)

    assert result.dirty is True
    assert result.execution_allowed is False
    assert any("dirty" in reason.lower() for reason in result.reasons)


def test_scope_guard_flags_out_of_scope_and_protected_paths(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    before = capture_workspace_snapshot(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "note.md").write_text("changed\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# changed\n", encoding="utf-8")
    after = capture_workspace_snapshot(tmp_path)

    task = TaskSlice(
        id="slice_1",
        title="Test scope",
        objective="Modify app code only",
        allowed_paths=["app"],
        protected_paths=["README.md"],
        diff_budget=DiffBudget(max_changed_files=1, max_added_lines=1, max_deleted_lines=1),
    )

    result = evaluate_scope(repo_root=tmp_path, task=task, before=before, after=after)

    assert result.allowed is False
    assert "docs/note.md" in result.out_of_scope_changes
    assert "README.md" in result.protected_path_changes

