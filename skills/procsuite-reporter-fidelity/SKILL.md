---
name: procsuite-reporter-fidelity
description: Use when Procedure Suite reporter output drops clinically important source detail, produces blank procedure bodies, mis-parses indications, overuses Not documented, or loses prompt-described complications while staying inside the current ProcedureBundle contract. Do not use for shared schema refactors.
---

# Procedure Suite Reporter Fidelity

Use this skill when the rendered note is clinically thin because the bundle builder or reporter pipeline is dropping source detail that already exists in the prompt or extraction output.

## Use this when

- The output drops complications, conversions, doses, or important findings.
- The reporter renders `PROCEDURE: See procedure details below`, blank detail bodies, or too many `Not documented` placeholders.
- Indication parsing is brittle.
- Anesthesia inference is too strict for prompt-style inputs.
- The fix can stay within the current `ProcedureBundle` contract.

## Do not use this when

- The only issue is extraction precision or CPT derivation.
- The right fix requires adding a new bundle field.
- The task is primarily about eval/CI plumbing.

## Read first

- `AGENTS.md`
- `CLAUDE.md`
- `references/reporter-scope.md`

## Default workflow

1. Reproduce the fidelity problem.
   - Use the reporter evals:
     - `python ops/tools/eval_reporter_prompt_baseline.py --input tests/fixtures/reporter_seed_eval_samples.json --output /tmp/reporter_seed_registry.json --strict`
     - `python ops/tools/eval_reporter_prompt_llm_findings.py --input tests/fixtures/reporter_seed_eval_samples.json --output /tmp/reporter_seed_llm.json --strict`
   - If comparing fallback behavior:
     - `python ops/tools/summarize_reporter_seed_fallbacks.py --left-report <left.json> --right-report <right.json> --output <summary.json>`

2. Add or curate a focused regression case first.
   - Prefer a deterministic case from `reporter_tests_5.4.json` or existing reporter fixtures.
   - Keep the assertion slot-level: complication survives, indication is not truncated, procedure body is non-empty, anesthesia cue survives.

3. Fix the bundle builder or minimal reporter logic first.
   - Prefer `build_procedure_bundle_from_extraction` and narrow helpers over broad template-only edits.
   - Stay within the current contract:
     - `complications_text`
     - `addons`
     - existing bundle fields
   - Do not implement against a non-existent `bundle.complications` object.

4. Re-run strict reporter tests and summaries.
   - `pytest -q tests/quality/test_reporter_seed_dual_path_matrix.py`
   - `pytest -q tests/quality/test_reporter_precision_extra_flags.py`
   - `pytest -q tests/reporting/test_strict_render_validation.py`

5. Stop with a concise note.
   - source case
   - files changed
   - what detail now survives
   - remaining risks

## Guardrails

- Preserve seed-path comparability; do not fork reporter behavior by seed path.
- Prefer bundle-build fixes over template cosmetics when information is missing.
- Explicit complications in the source should not collapse to `COMPLICATIONS: None`.
- Do not default generic flexible bronchoscopy to moderate sedation when there is no cue.
- Avoid blank procedure bodies when the prompt explicitly names a high-confidence procedure.

## Files to inspect first

- `app/reporting/engine.py`
- `app/api/routes/reporting.py`
- `app/reporting/templates/addons/interventional_pulmonology_operative_report.jinja`
- `tests/reporting/`
- `tests/quality/test_reporter_seed_dual_path_matrix.py`
- `tests/quality/test_reporter_precision_extra_flags.py`

## Validation commands

- `pytest -q tests/quality/test_reporter_seed_dual_path_matrix.py`
- `pytest -q tests/quality/test_reporter_precision_extra_flags.py`
- `pytest -q tests/reporting/test_strict_render_validation.py`
- `python ops/tools/eval_reporter_prompt_baseline.py --input tests/fixtures/reporter_seed_eval_samples.json --output /tmp/reporter_seed_registry.json --strict`

## Definition of done

- The source detail survives into the rendered note.
- The fix stays within the current bundle contract.
- Reporter strict tests still pass.
- The change improves fidelity without adding obvious hallucinated defaults.

## Example prompts

- Improve reporter fidelity for prompt-described complications that currently render as `COMPLICATIONS: None`.
- Fix indication parsing so `a LLL lesion, taking` no longer becomes the indication.
- Prevent blank procedure bodies for obviously named procedures in the reporter prompts.
