# Knowledge Release Checklist

Goal: ship knowledge/schema changes safely without breaking extraction, coding logic, or schema validation.

## Required Checks

1) **Schema validation**
- `make validate-schemas`

2) **Knowledge base validation**
- `make validate-kb`
- `make validate-knowledge-release`

3) **Regression tests**
- `make test` (full suite)
- If time‑boxed: at minimum run the deterministic CPT derivation + registry unit tests you changed.

3b) **Diff report (recommended for KB bumps)**
- `make knowledge-diff OLD_KB=path/to/old_kb.json NEW_KB=data/knowledge/ip_coding_billing_v3_0.json`

4) **Versioning + deprecations**
- Ensure KB internal `"version"` matches the semantic version in the filename (e.g., `ip_coding_billing_v3_0.json` ↔ `version: "3.0"`).
- If a path/name changes, add `metadata.deprecations[]` entries.
- Default behavior is **strict** (mismatch fails fast). Dev override: `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`.

5) **Changelog**
- Add an entry to the KB `metadata.changelog` describing:
  - RVU updates (year + source)
  - codes added/removed
  - rule behavior changes (bundling, add‑ons, guardrails)

## Acceptance Smoke (Optional but Recommended)

- Run a single-note smoke:
  - `python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct`
