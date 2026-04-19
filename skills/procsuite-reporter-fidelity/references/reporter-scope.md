# Reporter fidelity scope

This skill is for low-risk reporter fixes that do not require a new schema field.

## Preferred targets

- Explicit `Indication:` or `Primary indication:` labels
- Prompt-described complications that are otherwise lost
- Non-empty procedure bodies for clearly named procedures
- Narrow anesthesia inference from explicit cues
- Preserving clinically important detail via existing text fields and addons

## Stay inside the current contract

Use existing fields such as:
- `complications_text`
- existing procedure detail fields
- `addons`
- other current `ProcedureBundle` fields

Do not assume a new `bundle.complications` field exists in this phase.

## Anti-patterns

- Large template rewrites to compensate for missing upstream information
- Generic defaults that create new hallucinations
- Mixing schema redesign into a small reporter hotfix
