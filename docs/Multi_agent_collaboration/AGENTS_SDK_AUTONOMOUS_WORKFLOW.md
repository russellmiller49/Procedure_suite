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

## Local Setup (WSL-safe)

Use a dedicated project venv for this workflow to avoid dependency conflicts with
the `medparse-py311` runtime used by the main API app.

```bash
cd /home/rjm/projects/proc_suite

# one-time (if .venv does not exist yet)
python3.11 -m venv .venv

# install project + optional agents SDK
.venv/bin/pip install -e ".[agents]"

# required for Planner/Classifier/Reporter SDK calls
export OPENAI_API_KEY="..."

# force non-interactive Codex exec path for this workflow
export CODEX_EXECUTABLE="/home/rjm/projects/proc_suite/ops/tools/codex_exec_json_wrapper.sh"
```

Quick verification:

```bash
.venv/bin/python -c "import agents; print('agents ok')"
codex --version
.venv/bin/python ops/tools/run_engineering_workflow.py --help
```

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
- If your local Codex binary is under WSL npm globals (for example `~/.npm-global/bin/codex`),
  keep using `CODEX_EXECUTABLE=ops/tools/codex_exec_json_wrapper.sh` so subprocess execution
  always uses `codex exec` and emits only the final JSON message.

