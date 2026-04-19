# Procedure Suite Codex Skills

This folder is the source tree for Procedure Suite repo-scoped skills.
If your Codex setup expects repo skills under `.agents/skills/`, copy or symlink the individual skill folders there.

## Skills included

- `procsuite-extraction-hotfix` — billing-grade extraction and deterministic CPT hotfixes
- `procsuite-coding-evidence` — evidence anchoring, header/menu leakage, coding traceability
- `procsuite-reporter-fidelity` — reporter output fidelity within the current bundle contract
- `procsuite-narrative-annotations` — new preservation channel for narrative details that lack a schema home
- `procsuite-quality-gates` — unified quality corpus, reporter evals, PR gate wiring, and durable regression coverage

## Which skill to reach for

- `procsuite-extraction-hotfix` for focused extraction or deterministic parsing bugs that stay inside the current schema and evidence model.
- `procsuite-coding-evidence` for auditability problems such as header/menu leakage, `coding_support`, `derived_from`, or hint-versus-proof separation.
- `procsuite-reporter-fidelity` for reporter output that drops detail which already has a home in the current `ProcedureBundle`.
- `procsuite-narrative-annotations` when the missing detail needs a new preservation channel threaded through extraction, bundle, and reporter code.
- `procsuite-quality-gates` when the main task is fixtures, eval wiring, or making sure a regression actually runs in the PR gate.

## Suggested usage

Explicitly trigger a skill when you want predictable behavior:

- `$procsuite-extraction-hotfix fix the EBUS station 9 hallucination and add the regression`
- `$procsuite-coding-evidence stop CPT evidence from anchoring to header numerals`
- `$procsuite-reporter-fidelity improve complication carry-through for prompt-only reporter cases`
- `$procsuite-narrative-annotations add a durable narrative preservation channel to ProcedureBundle`
- `$procsuite-quality-gates add durable fixture coverage for blocker-vs-Chartis and decimal-dose regressions`

## Shared repo rules these skills assume

- Read `AGENTS.md` and `CLAUDE.md` before large changes.
- Keep the service in extraction-first mode.
- Add a failing test before a bug fix.
- Prefer minimal, scoped changes over broad refactors.
- Re-run focused tests plus the PR quality gate before stopping.
