from __future__ import annotations

import json
from pathlib import Path

from ops.engineering_workflow.artifacts import (
    append_event,
    ensure_session_dir,
    load_manifest,
    resolve_artifact_root,
    save_manifest,
)
from ops.engineering_workflow.state import initialize_manifest


def test_resolve_artifact_root_prefers_codex_home(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex_home"))

    root = resolve_artifact_root()

    assert root == (tmp_path / "codex_home" / "agent_runs" / "proc_suite").resolve()


def test_manifest_roundtrip_and_append_only_events(tmp_path: Path) -> None:
    session_dir = ensure_session_dir(tmp_path, "session_123")
    manifest = initialize_manifest(
        session_id="session_123",
        goal="Test the workflow",
        artifact_dir=session_dir,
        allow_dirty=False,
        enable_tracing=False,
    )

    save_manifest(session_dir, manifest)
    append_event(session_dir, "created", {"goal": "Test the workflow"})
    append_event(session_dir, "planned", {"slice_count": 1})

    loaded = load_manifest(session_dir)
    event_lines = (session_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()

    assert loaded.session_id == "session_123"
    assert len(event_lines) == 2
    assert json.loads(event_lines[0])["event_type"] == "created"
    assert json.loads(event_lines[1])["event_type"] == "planned"

