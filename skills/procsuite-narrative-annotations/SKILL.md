---
name: procsuite-narrative-annotations
description: Use when Procedure Suite needs a new preservation channel for clinically important narrative details that do not fit the current extraction or ProcedureBundle schema, such as conversions, failed attempts, migrated devices, dose detail, or quantitative outcomes. This skill covers adding and threading narrative_annotations end to end. Do not use for small hotfixes that fit inside the current contract.
---

# Procedure Suite Narrative Annotations

Use this skill when repeated fidelity bugs all trace back to the same root cause: the information exists in the source note, but there is no durable schema home for it, so it gets dropped between extraction and rendering.

## Use this when

- The right fix needs a new preservation channel rather than another one-off hotfix.
- The missing detail includes conversions, failed attempts, migrated/removed/replaced devices, quantitative outcomes, or complication detail that lacks a field.
- The change touches shared bundle/schema code and must be threaded through serialization and render paths.

## Do not use this when

- A small reporter or extraction fix inside the current contract would solve the problem.
- The task is only about eval or fixture wiring.
- The needed information already has a clean structured home.

## Read first

- `AGENTS.md`
- `CLAUDE.md`
- `references/narrative-annotations-design.md`

## Default workflow

1. Confirm the loss point.
   - Reproduce the failure through the real extraction → bundle → reporter path.
   - Verify that the data is present in source text but has no structured destination.

2. Design the new field conservatively.
   - Add a `NarrativeAnnotation` model with minimal fields such as:
     - `section`
     - `text`
     - `confidence`
     - `source_span`
   - Keep it append-only and preservation-focused.

3. Thread the new field end to end.
   - schema/model definition
   - bundle construction
   - patch/apply logic
   - validation/serialization
   - real reporter render path

4. Populate annotations after structured extraction.
   - Focus on details that are repeatedly dropped:
     - conversions like `LMA` to `ETT`
     - failed attempts
     - migrated or replaced devices
     - dose detail
     - quantitative outcomes
     - complication details with no existing field

5. Render annotations conservatively.
   - Prefer near-verbatim or lightly normalized text.
   - Do not turn the annotation channel into a second inference engine.

6. Add curated regression fixtures and re-run reporter validation.

## Guardrails

- Structured fields remain authoritative when they exist.
- Narrative annotations are a preservation channel, not a license for aggressive summarization.
- Do not hide the new field inside a single addon template if the main reporter path should render it.
- Keep the field small, explicit, and serializable.

## Files to inspect first

- `proc_schemas/clinical/common.py`
- `app/reporting/engine.py`
- any bundle patch/apply or serialization paths touched by `ProcedureBundle`
- new helper module for extraction/postprocess narrative capture
- `tests/reporting/` and reporter quality fixtures

## Validation commands

- `pytest -q tests/reporting`
- `pytest -q tests/quality/test_reporter_seed_dual_path_matrix.py`
- `python ops/tools/eval_reporter_prompt_baseline.py --input tests/fixtures/reporter_seed_eval_samples.json --output /tmp/reporter_seed_registry.json --strict`

## Definition of done

- Missing narrative detail survives a curated regression set.
- The new field is threaded cleanly through schema, serialization, and reporter code.
- Structured fields still behave the same where they already existed.
- Reporter regressions remain deterministic.

## Example prompts

- Add `narrative_annotations` to ProcedureBundle and thread it through the reporter.
- Preserve stent migration, removal, and replacement detail that the current bundle drops.
- Add a durable channel for conversions like LMA to ETT due to bleeding.
