---
name: procsuite-quality-gates
description: Use when adding or maintaining Procedure Suite quality fixtures, eval scripts, reporter seed checks, unified quality corpus cases, or PR and nightly gate wiring in ops/tools/run_quality_gates.py. Focus on durable regression coverage and making sure new tests actually run in CI. Do not use for core extraction implementation except for minimal test-target wiring.
---

# Procedure Suite Quality Gates

Use this skill when the main task is turning a regression into durable automated coverage.

## Use this when

- The user asks to add fixture coverage, update the unified quality corpus, tighten reporter evals, or change the PR gate.
- A bug fix is done but not yet protected by deterministic tests.
- You need to ensure a new test file is actually included in the fast gate.
- You are deciding whether to extend the current harness or add a new one.

## Do not use this when

- The main task is implementing extraction or reporter logic.
- The work is mostly a schema or bundle redesign.
- The bug is still not reproducible.

## Read first

- `AGENTS.md`
- `CLAUDE.md`
- `references/gate-playbook.md`

## Default workflow

1. Inspect the current gate before adding anything.
   - `ops/tools/run_quality_gates.py`
   - current `PR_PYTEST_TARGETS`
   - current fixture inputs and baselines

2. Choose the smallest durable coverage mechanism.
   - Add a focused pytest for the exact bug.
   - Extend `tests/fixtures/unified_quality_corpus.json` when the existing shared schema can express the assertion.
   - Only add a new corpus or harness if the current evaluator genuinely cannot represent the needed check.

3. Make the assertion clinically explicit.
   - good:
     - forbidden CPT code
     - forbidden station value
     - required performed flag
     - required phrase group in reporter output
   - bad:
     - vague similarity checks
     - model-random outputs

4. Ensure the new coverage actually runs.
   - Update `PR_PYTEST_TARGETS` or the appropriate eval entrypoint if needed.
   - Do not assume a new test file or fixture will automatically run in the PR gate.

5. Re-run the gate and inspect the summary artifacts.
   - `python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr`

## Guardrails

- Every critical bug should get at least one narrow regression test.
- Prefer extending the existing unified quality corpus and evaluator before introducing a parallel harness.
- Keep reporter evals deterministic and slot-level first.
- Avoid gates that depend on nondeterministic phrasing or LLM variance.
- Name fixture cases for the clinical failure mode, not the implementation detail.

## Files to inspect first

- `ops/tools/run_quality_gates.py`
- `tests/fixtures/unified_quality_corpus.json`
- `tests/fixtures/reporter_seed_eval_samples.json`
- `app/common/quality_eval.py`
- `tests/scripts/test_run_quality_gates.py`
- `tests/scripts/test_eval_golden.py`
- `tests/quality/`
- `tests/reporting/`

## Validation commands

- `pytest -q tests/scripts/test_run_quality_gates.py`
- `pytest -q tests/scripts/test_eval_golden.py`
- `python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr`

## Definition of done

- The new regression is expressed in a deterministic test or fixture.
- The PR gate actually executes that coverage.
- The summary artifact makes pass/fail status easy to inspect.
- The change is small enough that future regressions will be obvious.

## Example prompts

- Extend the unified quality corpus with the blocker-versus-Chartis regression and wire it into the PR gate.
- Add a structural invariant test for header/menu evidence anchoring.
- Tighten reporter seed checks so explicit complications cannot disappear silently.
