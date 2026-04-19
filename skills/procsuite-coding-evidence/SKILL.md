---
name: procsuite-coding-evidence
description: Use when changing Procedure Suite billing evidence anchoring, coding_support, derived_from, header or menu leakage, or traceability rules in registry billing output. Focus on audit-ready evidence and hint-versus-proof separation, not generic extraction suppressors or standalone CPT hotfixes.
---

# Procedure Suite Coding Evidence

Use this skill when the issue is not just whether a CPT is emitted, but whether the evidence trail is clinically and auditorially defensible.

## Use this when

- The task mentions evidence spans, `coding_support`, `billing.cpt_codes`, `derived_from`, or traceability.
- Header/menu CPT numerals are leaking into performed-procedure evidence.
- The change touches `app/registry/application/registry_service.py` or CPT derivation paths.
- You need to preserve limited header hints while preventing header-only evidence anchors.

## Do not use this when

- The change is a straightforward extraction suppressor with no evidence-trace impact.
- The task is mainly reporter narrative preservation.
- The work is mostly fixture or gate plumbing.

## Read first

- `AGENTS.md`
- `CLAUDE.md`
- `references/evidence-invariants.md`

## Default workflow

1. Reproduce the current evidence behavior.
   - Inspect emitted CPT evidence spans, `derived_from`, and `coding_support`.
   - Confirm whether the primary evidence span falls inside a header or menu block.

2. Add a structural invariant test before changing logic.
   - Good examples:
     - no primary evidence span inside `PROCEDURE:` header code blocks
     - no anchoring inside masked menu sections like `IP ... CODE MOD DETAILS`
     - header-only support must be marked as hint or implied support, not as narrative evidence

3. Make the evidence model cleaner, not looser.
   - Split header-derived code signal from auditable narrative evidence.
   - Preserve guarded header-hint behavior only where the deterministic rule still has narrative or structured support.
   - Never delete working guarded rules blindly.

4. Update the deterministic coding rules that depend on the evidence channel.
   - Read from the new header-hint channel where appropriate.
   - Keep narrative or structured support requirements intact.

5. Re-run focused tests plus the PR gate.
   - `pytest -q <path>::<test_name>`
   - `python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr`

## Guardrails

- Narrative evidence outranks header/menu content.
- Header numerals may be hints, but not primary proof of a performed service.
- If the code is defensible only indirectly, mark it as implied support rather than fabricating a narrative span.
- Do not break legitimate guarded uses of header-derived hints while fixing leakage.

## Files to inspect first

- `app/registry/application/registry_service.py`
- `app/registry/application/coding_support_builder.py`
- `app/coder/domain_rules/registry_to_cpt/coding_rules.py`
- `app/common/quality_eval.py`
- `tests/quality/`
- `tests/scripts/test_run_quality_gates.py`
- `ops/tools/run_quality_gates.py`

## Validation commands

- `pytest -q tests/quality`
- `pytest -q tests/scripts/test_run_quality_gates.py`
- `python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr`

## Definition of done

- Header/menu spans no longer appear as primary CPT evidence anchors.
- Guarded header-hint behavior is preserved when still clinically justified.
- A structural invariant test exists for the leakage pattern.
- The PR gate still passes or any remaining failures are explained.

## Example prompts

- Split header CPT hints from auditable narrative evidence and update the coding rules.
- Add an invariant test that blocks primary evidence spans inside menu/header blocks.
- Stop 31646 from anchoring to the header numeral when the narrative should be the evidence source.
