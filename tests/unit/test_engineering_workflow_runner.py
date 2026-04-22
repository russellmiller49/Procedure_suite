from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from ops.engineering_workflow.contracts import CodexReportPayload, CodexRunResult, CommandSpec, PlanPacket, TaskSlice
from ops.engineering_workflow.runner import EngineeringWorkflowRunner, WorkflowDependencies


MODULE_TEST = (
    "import sys\n"
    "from pathlib import Path\n\n"
    "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"
    "from app.module import meaning\n\n\n"
    "def test_meaning():\n"
    "    assert meaning() == 42\n"
)


def _artifact_root(tmp_path: Path) -> Path:
    return tmp_path.parent / f"{tmp_path.name}_artifacts"


def _pytest_command(test_path: str) -> list[str]:
    pytest_bin = shutil.which("pytest")
    if pytest_bin:
        return [pytest_bin, "-q", test_path]
    sibling = Path(sys.executable).with_name("pytest")
    return [str(sibling), "-q", test_path]


def _init_git_repo(repo_root: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_root, check=True)
    (repo_root / "app").mkdir()
    (repo_root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (repo_root / "tests").mkdir()
    (repo_root / "README.md").write_text("# Repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo_root, check=True, capture_output=True, text=True)


class _FakePlanner:
    def __init__(self, plan: PlanPacket) -> None:
        self.plan_packet = plan

    def plan(self, *, goal, preflight, repo_root):  # noqa: ANN001
        return self.plan_packet


class _FakeExecutor:
    def __init__(self, writer) -> None:  # noqa: ANN001
        self.writer = writer
        self.calls = 0

    def run(self, *, prompt, repo_root, artifact_dir, task_id):  # noqa: ANN001
        self.calls += 1
        self.writer(repo_root, task_id, self.calls)
        stdout_path = artifact_dir / f"{task_id}.stdout.json"
        stderr_path = artifact_dir / f"{task_id}.stderr.txt"
        stdout_path.write_text("{}", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        return CodexRunResult(
            payload=CodexReportPayload(
                summary=f"call {self.calls}",
                status="implemented",
                files_changed=[],
            ),
            executor_command=["codex"],
            returncode=0,
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            parsed_json_path=str(stdout_path),
        )


def test_runner_happy_path(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    (tmp_path / "app" / "module.py").write_text("def meaning():\n    return 42\n", encoding="utf-8")
    (tmp_path / "tests" / "test_module.py").write_text(MODULE_TEST, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True, text=True)

    plan = PlanPacket(
        goal="Update module",
        task_slices=[
            TaskSlice(
                id="slice_1",
                title="Update module",
                objective="Touch module only",
                allowed_paths=["app"],
                validation_commands=[CommandSpec(name="pytest", command=_pytest_command("tests/test_module.py"))],
            )
        ],
        final_gate_commands=[CommandSpec(name="pytest_final", command=_pytest_command("tests/test_module.py"))],
    )

    def writer(repo_root: Path, task_id: str, call_count: int) -> None:
        (repo_root / "app" / "module.py").write_text("def meaning():\n    return 42\n", encoding="utf-8")

    runner = EngineeringWorkflowRunner(
        repo_root=tmp_path,
        dependencies=WorkflowDependencies(planner=_FakePlanner(plan), codex_executor=_FakeExecutor(writer)),
    )

    result = runner.run(goal="Update module", artifact_root=_artifact_root(tmp_path))

    assert result.status == "completed"
    assert result.report_path.exists()
    assert (result.session_dir / "session_handoff.md").exists()


def test_runner_blocks_on_preexisting_red_baseline(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    (tmp_path / "tests" / "test_module.py").write_text("def test_fail():\n    assert False\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True, text=True)

    plan = PlanPacket(
        goal="Try update",
        task_slices=[
            TaskSlice(
                id="slice_1",
                title="Update module",
                objective="Touch module only",
                allowed_paths=["app"],
                validation_commands=[CommandSpec(name="pytest", command=_pytest_command("tests/test_module.py"))],
            )
        ],
    )

    executor = _FakeExecutor(lambda repo_root, task_id, call_count: None)
    runner = EngineeringWorkflowRunner(
        repo_root=tmp_path,
        dependencies=WorkflowDependencies(planner=_FakePlanner(plan), codex_executor=executor),
    )

    result = runner.run(goal="Try update", artifact_root=_artifact_root(tmp_path))

    assert result.status == "blocked"
    assert executor.calls == 0


def test_runner_repair_round_can_succeed(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    (tmp_path / "app" / "module.py").write_text("def meaning():\n    return 42\n", encoding="utf-8")
    (tmp_path / "tests" / "test_module.py").write_text(MODULE_TEST, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True, text=True)

    plan = PlanPacket(
        goal="Update module",
        task_slices=[
            TaskSlice(
                id="slice_1",
                title="Update module",
                objective="Touch module only",
                allowed_paths=["app"],
                validation_commands=[CommandSpec(name="pytest", command=_pytest_command("tests/test_module.py"))],
            )
        ],
    )

    def writer(repo_root: Path, task_id: str, call_count: int) -> None:
        if call_count == 1:
            (repo_root / "app" / "module.py").write_text("def meaning():\n    return 1\n", encoding="utf-8")
        else:
            (repo_root / "app" / "module.py").write_text("def meaning():\n    return 42\n", encoding="utf-8")

    executor = _FakeExecutor(writer)
    runner = EngineeringWorkflowRunner(
        repo_root=tmp_path,
        dependencies=WorkflowDependencies(planner=_FakePlanner(plan), codex_executor=executor),
    )

    result = runner.run(goal="Update module", artifact_root=_artifact_root(tmp_path))

    assert result.status == "completed"
    assert executor.calls == 2


def test_runner_blocks_out_of_scope_changes(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    (tmp_path / "tests" / "test_smoke.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "seed"], cwd=tmp_path, check=True, capture_output=True, text=True)

    plan = PlanPacket(
        goal="Only touch app",
        task_slices=[
            TaskSlice(
                id="slice_1",
                title="Out of scope",
                objective="Touch app only",
                allowed_paths=["app"],
                validation_commands=[CommandSpec(name="pytest", command=_pytest_command("tests/test_smoke.py"))],
            )
        ],
    )

    def writer(repo_root: Path, task_id: str, call_count: int) -> None:
        (repo_root / "README.md").write_text("# changed\n", encoding="utf-8")

    runner = EngineeringWorkflowRunner(
        repo_root=tmp_path,
        dependencies=WorkflowDependencies(planner=_FakePlanner(plan), codex_executor=_FakeExecutor(writer)),
    )

    result = runner.run(goal="Only touch app", artifact_root=_artifact_root(tmp_path))

    assert result.status == "blocked"
    handoff = (result.session_dir / "session_handoff.md").read_text(encoding="utf-8")
    assert "Blocked Slice" in handoff
