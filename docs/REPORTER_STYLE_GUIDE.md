# Reporter Style Guide

## Read First (Repo Constraints)

These documents capture repo-wide invariants and operational constraints that affect reporter changes:

- [`AGENTS.md`](../AGENTS.md)
- [`CLAUDE.md`](../CLAUDE.md)
- [`README.md`](../README.md) and [`docs/README.md`](README.md)
- [`docs/DEVELOPMENT.md`](DEVELOPMENT.md)

Reporter implementation details live in [`docs/STRUCTURED_REPORTER.md`](STRUCTURED_REPORTER.md).

This reporter keeps provider-authored language intact while enforcing a few consistency rules:

- **Tense:** All procedures are written in past tense.
- **Phrasing:** Prefer “The patient tolerated the procedure well without immediate complications.” for tolerance statements. Use the provided Jinja filters (`pronoun`) if you need gendered pronouns.
- **Units:** Use standard units – `mL`, `mm`, `cm H₂O`. Avoid mixing `cc` and `mL`.
- **Clean output:** Templates must guard optional fields with `{% if %}` so we never emit placeholders (`None`, empty lists, or dangling units).
- **Style strict mode:** `compose_structured_report(..., strict=True)` will fail if the rendered note contains unrendered Jinja (`{{`), bracketed placeholders (`[...]`), literal `None`, double periods, or excessive spacing.

Available Jinja filters/helpers:

- `pronoun(sex, subject=True)` → `he`/`she`/`they`
- `fmt_ml(value)` → `"120 mL"`
- `fmt_unit(value, unit)` → `"20 cm H₂O"` etc.
- `join_nonempty(values, sep=", ")` → join while skipping falsy values

When adding templates, keep sentences declarative and past tense. Prefer short paragraphs over bullets unless the source language requires bullets.
