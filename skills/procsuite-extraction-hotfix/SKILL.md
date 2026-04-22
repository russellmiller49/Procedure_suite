---
name: procsuite-extraction-hotfix
description: Use when working on Procedure Suite extraction-first precision bugs or deterministic parse regressions in app/registry and app/coder, especially suppress-or-preserve hotfixes like EBUS station parsing, Chartis versus blocker logic, dose parsing, and bleeding complication inflation. Do not use when the main work is evidence anchoring, header leakage, reporter redesign, or schema changes.
---

# Procedure Suite Extraction Hotfix

Use this skill for small, high-confidence fixes in the extraction-first pipeline where the failure mode is a hallucinated procedure/code, a missed suppressor, or a clinically wrong deterministic parse.

## Use this when

- The user asks to fix an extraction regression, billing-grade CPT error, or deterministic guardrail bug.
- The likely change is in `app/registry/`, `app/coder/domain_rules/`, or a nearby postprocess module.
- The right fix is a targeted code change plus durable regression coverage.
- The desired behavior can stay within the current schema.

## Do not use this when

- The main problem is reporter phrasing or bundle/render fidelity.
- The fix requires adding a new bundle field or changing a shared schema contract.
- The task is primarily about CI/eval harness changes rather than extraction logic.

## Read first

- `AGENTS.md`
- `CLAUDE.md`
- `references/known-hotfixes.md`

## Default workflow

1. Reproduce the current behavior before editing code.
   - Run the PR gate:
     - `python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr`
   - If the bug is note-specific, use the smoke tool:
     - `python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct`

2. Add the narrowest failing regression test first.
   - Prefer an existing targeted test file if a close neighbor exists.
   - If there is no natural home, add a focused test under `tests/registry/`, `tests/coder/`, or `tests/quality/`.
   - Keep the assertion clinically concrete: stations, CPT codes, performed flags, complication grades, or preserved dose text.

3. Make the smallest safe code change.
   - Tighten context checks before adding broad heuristics.
   - Prefer evidence-aware suppressions over keyword-only logic.
   - Do not widen recall while doing a suppression fix unless you can justify the tradeoff.

4. Re-run validation in this order.
   - New failing test
   - Nearby impacted tests
   - PR gate:
     - `python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr`

5. Stop with a concise implementation note.
   - Files changed
   - Logic changed
   - Tests added
   - Remaining edge cases or risk

## Guardrails

- Narrative evidence outranks header, menu, and template content.
- Tool mention is not the same as therapeutic intent.
- Header/menu CPT numerals are never enough by themselves to prove a performed procedure.
- Preserve auditable evidence; do not replace a real narrative anchor with a header numeral.
- Stay within the current schema in this skill.

## Files to inspect first

- `app/registry/postprocess/__init__.py`
- `app/registry/deterministic_extractors.py`
- `app/registry/postprocess/complications_reconcile.py`
- `app/coder/domain_rules/registry_to_cpt/coding_rules.py`
- `app/registry/application/registry_service.py`
- Nearby tests under `tests/registry/`, `tests/coder/`, and `tests/quality/`

## Validation commands

- `pytest -q <path>::<test_name>`
- `python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct`
- `python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr`

## Definition of done

- A targeted failing test was added first and now passes.
- The behavior is fixed without introducing schema churn.
- Nearby regressions still pass.
- The PR gate passes or any remaining failures are clearly explained.

## Example prompts

- Fix the EBUS dimension-as-station hallucination and add the regression.
- Suppress 31634 for non-Chartis Uniblocker cases without breaking true Chartis workflows.
- Preserve decimal medication doses in therapeutic injection extraction.
- Stop prophylactic hemostasis wording from inflating Nashville bleeding complications.
