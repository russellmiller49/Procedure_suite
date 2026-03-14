# Agents SDK Autonomous Workflow

This workflow lives under `ops/engineering_workflow/` and is intentionally split between:

- deterministic Python orchestration
- a typed `PlannerAgent`
- optional `FailureClassifierAgent`
- optional `ReporterAgent`

## Entry Point

```bash
python ops/tools/run_engineering_workflow.py --goal "Implement X"
```

Useful flags:

- `--session-id <id>`
- `--resume`
- `--allow-dirty`
- `--enable-tracing`
- `--artifact-root /custom/path`

## Artifact Layout

By default artifacts are written outside the repo worktree:

- `$CODEX_HOME/agent_runs/proc_suite/<session_id>/`
- fallback: `~/.codex/agent_runs/proc_suite/<session_id>/`

Each session writes:

- `session_manifest.json`
- `events.jsonl`
- `preflight.json`
- `plan.json`
- `slice_*_prompt.md`
- `slice_*_codex_result.json`
- `slice_*_scope_check.json`
- `slice_*_validation.json`
- `session_report.json`
- `session_handoff.md`

## Behavior

- Preflight records git state, tool discovery, and dirty-tree status.
- Clean repos are moved to a session branch named `codex/<session_id>`.
- Planner output must be typed and versioned.
- Codex output must be strict JSON.
- Scope checks run after every Codex execution.
- Validation runs before execution to detect pre-existing red baselines, then after each slice, and once more for final gates.
- Only localized and syntax/import failures are repair-eligible.

## Notes

- Agents SDK tracing is disabled by default via `OPENAI_AGENTS_DISABLE_TRACING=1`.
- The workflow does not use SDK sessions in v1; `session_manifest.json` is the source of truth.
- Manual smoke-testing still depends on a working local Codex CLI and installed `openai-agents`.

